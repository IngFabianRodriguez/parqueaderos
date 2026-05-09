"""Authentication service business logic."""

from typing import Optional
from datetime import datetime, timedelta
import uuid

from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import User, Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire, "iss": settings.jwt_issuer})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token() -> str:
        """Create a refresh token."""
        return str(uuid.uuid4())

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await AuthService.get_user_by_email(email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user


auth_service = AuthService()