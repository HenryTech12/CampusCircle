from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


class LoanState(StrEnum):
    pending_vote = "pending_vote"
    rejected = "rejected"
    approved_awaiting_acceptance = "approved_awaiting_acceptance"
    approved_insufficient_funds = "approved_insufficient_funds"
    accepted_pending_checks = "accepted_pending_checks"
    expired = "expired"
    disbursement_pending = "disbursement_pending"
    disbursed = "disbursed"
    disbursement_failed = "disbursement_failed"


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(120))
    phone_number: Mapped[str] = mapped_column(String(32))
    university: Mapped[str] = mapped_column(String(160))
    department: Mapped[str] = mapped_column(String(160))
    student_email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class EmailOTP(Base):
    __tablename__ = "email_otps"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    code_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Circle(Base):
    __tablename__ = "circles"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    university: Mapped[str | None] = mapped_column(String(160))
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class CircleMember(Base):
    __tablename__ = "circle_members"
    __table_args__ = (UniqueConstraint("circle_id", "user_id"),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    circle_id: Mapped[UUID] = mapped_column(ForeignKey("circles.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    circle_id: Mapped[UUID] = mapped_column(ForeignKey("circles.id", ondelete="CASCADE"))
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class LoanProposal(Base):
    __tablename__ = "loan_proposals"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    circle_id: Mapped[UUID] = mapped_column(ForeignKey("circles.id"))
    borrower_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    principal_minor: Mapped[int] = mapped_column(Integer)
    total_repayment_minor: Mapped[int] = mapped_column(Integer)
    interest_bps: Mapped[int] = mapped_column(Integer)
    fee_minor: Mapped[int] = mapped_column(Integer, default=0)
    repayment_frequency: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(40), default=LoanState.pending_vote)
    voting_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    terms: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("proposal_id", "voter_id"),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey("loan_proposals.id", ondelete="CASCADE"))
    voter_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    choice: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
