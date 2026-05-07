from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    lastname: str
    phone1: str
    company_name: str = ""
    company_edrpou: str = "00000000"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── SMS OTP ──────────────────────────────────────────────────────────────────

class SMSSendCodeRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: str) -> str:
        from src.utils.phone import validate_phone
        if not validate_phone(v):
            raise ValueError("Invalid Ukrainian phone number")
        return v


class SMSVerifyRequest(BaseModel):
    phone: str
    code: str
    # Required only for new-user registration
    name: Optional[str] = None
    lastname: Optional[str] = None


class SMSVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool


# ── Google OAuth ──────────────────────────────────────────────────────────────

class GoogleAuthUrlResponse(BaseModel):
    auth_url: str


class GoogleCallbackResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool
