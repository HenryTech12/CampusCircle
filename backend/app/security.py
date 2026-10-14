import hashlib
import hmac
import secrets
import base64
import json
from datetime import datetime, timedelta, timezone


def now() -> datetime:
    return datetime.now(timezone.utc)


def create_otp() -> tuple[str, str]:
    code = f"{secrets.randbelow(1_000_000):06d}"
    return code, hashlib.sha256(code.encode()).hexdigest()


def verify_otp(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hashlib.sha256(code.encode()).hexdigest(), code_hash)


def otp_expiry(seconds: int):
    return now() + timedelta(seconds=seconds)


def create_session_token(user_id: str, secret: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"sub": user_id}).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def read_session_token(token: str, secret: str) -> str | None:
    try:
        payload, signature = token.split(".", 1)
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        return json.loads(decoded)["sub"]
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
