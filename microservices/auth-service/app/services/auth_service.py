"""Authentication service business logic."""

import uuid
from typing import Optional
from datetime import datetime, timedelta

import pyotp
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import User, Session
from app.repositories import UserRepository, SessionRepository, PasswordResetTokenRepository


pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.session_repo = SessionRepository()
        self.password_reset_repo = PasswordResetTokenRepository()

    # ==================== Password Operations ====================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    # ==================== Token Operations ====================

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iss": settings.jwt_issuer,
            "iat": datetime.utcnow(),
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def create_refresh_token() -> str:
        """Create a refresh token (UUID format)."""
        return str(uuid.uuid4())

    @staticmethod
    def create_password_reset_token() -> str:
        """Create a password reset token (UUID format)."""
        return str(uuid.uuid4())

    # ==================== User Operations ====================

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self.user_repo.get_by_email(email)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(
        self,
        session: AsyncSessionLocal,
        email: str,
        password: str,
        tenant_id: str,
        full_name: Optional[str] = None,
        rol: str = "cliente",
    ) -> User:
        """Create a new user with hashed password."""
        hashed_password = self.hash_password(password)
        user_id = str(uuid.uuid4())
        return await self.user_repo.create(
            session=session,
            id=user_id,
            tenant_id=tenant_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            rol=rol,
        )

    async def update_user_password(self, user_id: str, new_password: str) -> bool:
        """Update user's password."""
        hashed = self.hash_password(new_password)
        return await self.user_repo.update_password(user_id, hashed)

    # ==================== Session Operations ====================

    async def create_session(
        self,
        session: AsyncSessionLocal,
        user_id: str,
        tenant_id: str,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Session:
        """Create a new session for user."""
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        session_id = str(uuid.uuid4())
        return await self.session_repo.create(
            session=session,
            id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    async def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Session]:
        """Get session by refresh token."""
        return await self.session_repo.get_by_refresh_token(refresh_token)

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user. Returns count."""
        return await self.session_repo.revoke_all_user_sessions(user_id)

    # ==================== MFA Operations ====================

    async def setup_mfa(self, user_id: str) -> tuple[str, str]:
        """Setup MFA for user. Returns (secret, qr_code_url)."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.mfa_enabled:
            raise ValueError("MFA already enabled")

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr_code_url = totp.provisioning_uri(name=user.email, issuer_name="Parqueaderos")

        await self.user_repo.set_mfa_secret(user_id, secret)
        return secret, qr_code_url

    async def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify MFA code for user."""
        user = await self.get_user_by_id(user_id)
        if not user or not user.mfa_secret:
            return False

        totp = pyotp.TOTP(user.mfa_secret)
        verified = totp.verify(code)

        if verified and not user.mfa_enabled:
            await self.user_repo.enable_mfa(user_id)

        return verified

    # ==================== Password Reset Operations ====================

    async def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset. Returns reset token or None."""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        token = self.create_password_reset_token()
        await self.password_reset_repo.create_token(
            user_id=user.id,
            email=email,
            token=token,
        )
        return token

    async def confirm_password_reset(
        self,
        token: str,
        new_password: str
    ) -> tuple[bool, str]:
        """Confirm password reset with token.

        Returns (success, message).
        """
        token_data = await self.password_reset_repo.get_valid_token(token)
        if not token_data:
            return False, "Invalid or expired reset token"

        hashed = self.hash_password(new_password)
        success = await self.user_repo.update_password(token_data["user_id"], hashed)

        if success:
            await self.password_reset_repo.mark_token_used(token)
            await self.password_reset_repo.delete_user_tokens(token_data["user_id"])

        return success, "Password updated successfully" if success else "Failed to update password"

    # ==================== Token Validation ====================

    async def validate_refresh_token(self, refresh_token: str) -> Optional[dict]:
        """Validate refresh token and return session data."""
        session = await self.get_session_by_refresh_token(refresh_token)
        if not session:
            return None
        if session.expires_at < datetime.utcnow():
            return None

        user = await self.get_user_by_id(session.user_id)
        if not user or not user.is_active:
            return None

        return {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "rol": user.rol,
        }


auth_service = AuthService()