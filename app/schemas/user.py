from uuid import UUID
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, field_validator


# 유효한 MBTI 타입 목록
VALID_MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP",
]


class UserCreate(BaseModel):
    google_id: str | None = None
    email: EmailStr
    name: str
    mbti: str | None = None
    is_premium: bool = False


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    mbti: str | None = None
    is_premium: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class MBTIUpdate(BaseModel):
    mbti: str

    @field_validator("mbti")
    @classmethod
    def validate_mbti(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_MBTI_TYPES:
            raise ValueError(f"Invalid MBTI type. Must be one of: {VALID_MBTI_TYPES}")
        return v_upper


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleAuthRequest(BaseModel):
    id_token: str
