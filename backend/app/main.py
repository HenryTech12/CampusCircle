from datetime import timedelta
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import get_settings
from .db import Base, engine, get_db
from .models import Circle, CircleMember, EmailOTP, User, now
from .providers import EmailService, GroqService, ProviderUnavailable
from .schemas import CircleCreate, CircleResponse, CopilotQuestion, MessageCreate, OTPVerification, Registration
from .security import create_otp, create_session_token, otp_expiry, read_session_token, verify_otp

settings = get_settings()
app = FastAPI(title="CampusCircle API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


async def current_user(authorization: str | None = Header(default=None), db: AsyncSession = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authenticated session required")
    user_id = read_session_token(authorization.removeprefix("Bearer "), settings.session_secret)
    user = await db.get(User, user_id) if user_id else None
    if not user or not user.email_verified:
        raise HTTPException(status_code=401, detail="Authenticated session required")
    return user


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "environment": settings.app_env, "financial_provider": "configured" if settings.bmoni_api_key else "unavailable"}


@app.post("/api/auth/register", status_code=status.HTTP_202_ACCEPTED)
async def register(payload: Registration, db: AsyncSession = Depends(get_db)) -> dict:
    existing = await db.scalar(select(User).where(User.student_email == payload.student_email))
    if existing and existing.email_verified:
        raise HTTPException(status_code=409, detail="An account already exists for this email")
    user = existing or User(**payload.model_dump())
    if not existing:
        db.add(user)
    await db.flush()
    code, digest = create_otp()
    db.add(EmailOTP(user_id=user.id, code_hash=digest, expires_at=otp_expiry(settings.otp_expiry_seconds)))
    await db.commit()
    try:
        await EmailService(settings).send(
            recipient=payload.student_email,
            subject="Your CampusCircle verification code",
            html=f"<p>Your verification code is <strong>{code}</strong>.</p><p>It expires in 10 minutes. Never share it.</p>",
        )
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail="Verification email is temporarily unavailable. Please try again.") from exc
    return {"status": "verification_required", "expires_in_seconds": settings.otp_expiry_seconds}


@app.post("/api/auth/resend", status_code=status.HTTP_202_ACCEPTED)
async def resend(payload: Registration, db: AsyncSession = Depends(get_db)) -> dict:
    user = await db.scalar(select(User).where(User.student_email == payload.student_email))
    if not user or user.email_verified:
        raise HTTPException(status_code=400, detail="Unable to resend verification code")
    latest = await db.scalar(select(EmailOTP).where(EmailOTP.user_id == user.id).order_by(EmailOTP.created_at.desc()))
    if latest and latest.created_at > now() - timedelta(seconds=60):
        raise HTTPException(status_code=429, detail="Please wait before requesting another code")
    code, digest = create_otp()
    db.add(EmailOTP(user_id=user.id, code_hash=digest, expires_at=otp_expiry(settings.otp_expiry_seconds)))
    await db.commit()
    try:
        await EmailService(settings).send(
            recipient=user.student_email,
            subject="Your new CampusCircle verification code",
            html=f"<p>Your new verification code is <strong>{code}</strong>.</p><p>It expires in 10 minutes. Never share it.</p>",
        )
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail="Verification email is temporarily unavailable. Please try again.") from exc
    return {"status": "verification_required", "expires_in_seconds": settings.otp_expiry_seconds}


@app.post("/api/auth/verify")
async def verify(payload: OTPVerification, db: AsyncSession = Depends(get_db)) -> dict:
    user = await db.scalar(select(User).where(User.student_email == payload.student_email))
    otp = await db.scalar(select(EmailOTP).where(EmailOTP.user_id == user.id if user else False).order_by(EmailOTP.created_at.desc()))
    if not user or not otp or otp.consumed_at or otp.expires_at <= now() or otp.attempts >= settings.otp_max_attempts:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    otp.attempts += 1
    if not verify_otp(payload.code, otp.code_hash):
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    otp.consumed_at = now()
    user.email_verified = True
    await db.commit()
    return {"status": "verified", "user_id": str(user.id), "access_token": create_session_token(str(user.id), settings.session_secret)}


@app.get("/api/circles", response_model=list[CircleResponse])
async def circles(db: AsyncSession = Depends(get_db)):
    return list((await db.scalars(select(Circle).order_by(Circle.created_at.desc()))).all())


@app.post("/api/circles", response_model=CircleResponse, status_code=201)
async def create_circle(payload: CircleCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    circle = Circle(**payload.model_dump(), created_by=user.id)
    db.add(circle)
    await db.flush()
    db.add(CircleMember(circle_id=circle.id, user_id=user.id, role="admin"))
    await db.commit()
    await db.refresh(circle)
    return circle


@app.post("/api/circles/{circle_id}/messages", status_code=201)
async def send_message(circle_id: str, payload: MessageCreate, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    member = await db.scalar(select(CircleMember).where(CircleMember.circle_id == circle_id, CircleMember.user_id == user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Circle membership required")
    from .models import ChatMessage
    message = ChatMessage(circle_id=circle_id, sender_id=user.id, body=payload.body)
    db.add(message)
    await db.commit()
    return {"id": str(message.id), "status": "sent"}


@app.post("/api/copilot")
async def copilot(payload: CopilotQuestion):
    try:
        answer = await GroqService(settings).answer(payload.question, {"note": "Authoritative account facts require an authenticated session"})
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail="Copilot is temporarily unavailable") from exc
    return {"answer": answer, "source": "groq" if settings.groq_api_key else "unavailable"}
