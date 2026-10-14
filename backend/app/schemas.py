from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class Registration(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=7, max_length=32)
    university: str = Field(min_length=2, max_length=160)
    department: str = Field(min_length=2, max_length=160)
    student_email: EmailStr


class OTPVerification(BaseModel):
    student_email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class CircleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    university: str | None = Field(default=None, max_length=160)
    is_private: bool = False


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CopilotQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class CircleResponse(BaseModel):
    id: UUID
    name: str
    description: str
    is_private: bool
    created_at: datetime
    model_config = {"from_attributes": True}
