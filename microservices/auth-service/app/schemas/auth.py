"""Auth schemas using pure Python dataclasses (no pydantic)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LoginRequest:
    """Login request schema."""
    email: str
    password: str

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email format")
        if not self.password or len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")


@dataclass
class RegisterRequest:
    """Schema for user registration."""
    email: str
    password: str
    tenant_id: str
    full_name: Optional[str] = None
    rol: str = "cliente"

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email format")
        if not self.password or len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not self.tenant_id:
            raise ValueError("tenant_id is required")


@dataclass
class LoginResponse:
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@dataclass
class RefreshRequest:
    """Refresh token request."""
    refresh_token: str


@dataclass
class RefreshResponse:
    """Refresh response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@dataclass
class MFASetupResponse:
    """MFA setup response."""
    secret: str
    qr_code_url: str


@dataclass
class MFAVerifyRequest:
    """MFA verify request."""
    code: str

    def __post_init__(self):
        if not self.code or len(self.code) != 6:
            raise ValueError("Code must be exactly 6 digits")


@dataclass
class MFAVerifyResponse:
    """MFA verify response."""
    verified: bool
    mfa_enabled: bool


@dataclass
class PasswordResetRequest:
    """Password reset request."""
    email: str

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email format")


@dataclass
class PasswordResetConfirmRequest:
    """Password reset confirm request."""
    token: str
    new_password: str

    def __post_init__(self):
        if not self.new_password or len(self.new_password) < 8:
            raise ValueError("Password must be at least 8 characters")


@dataclass
class UserResponse:
    """User response schema."""
    id: str
    tenant_id: str
    email: str
    full_name: Optional[str]
    rol: str
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime


@dataclass
class TokenPayload:
    """JWT token payload schema."""
    sub: str
    tenant_id: str
    rol: str
    exp: datetime
    iat: Optional[datetime] = None
    iss: Optional[str] = None


@dataclass
class ErrorResponse:
    """Standard error response schema."""
    detail: str
    code: Optional[str] = None


@dataclass
class ValidateTokenResponse:
    """Token validation response schema."""
    valid: bool
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    rol: Optional[str] = None


@dataclass
class PasswordResetToken:
    """Password reset token schema."""
    id: str
    user_id: str
    token: str
    expires_at: datetime
    is_used: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)