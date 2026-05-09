"""Pydantic schemas for authentication."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str


class MFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class MFAVerifyResponse(BaseModel):
    verified: bool
    mfa_enabled: bool


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    full_name: Optional[str]
    rol: str
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    rol: Optional[str] = None