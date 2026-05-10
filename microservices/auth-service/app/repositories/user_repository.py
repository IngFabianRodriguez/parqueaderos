"""User repository for database operations."""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import AsyncSessionLocal


class UserRepository:
    """Repository for User database operations."""

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        id: str,
        tenant_id: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        rol: str = "cliente",
        is_verified: bool = False,
        mfa_enabled: bool = False,
    ) -> User:
        """Create a new user."""
        user = User(
            id=id,
            tenant_id=tenant_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            rol=rol,
            is_verified=is_verified,
            mfa_enabled=mfa_enabled,
            created_at=datetime.utcnow(),
        )
        session.add(user)
        return user

    @staticmethod
    async def update_last_login(user_id: str) -> bool:
        """Update user's last login timestamp."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login_at=datetime.utcnow())
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def set_mfa_secret(user_id: str, secret: str) -> bool:
        """Set MFA secret for user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(mfa_secret=secret)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def enable_mfa(user_id: str) -> bool:
        """Enable MFA for user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(mfa_enabled=True)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def update_password(user_id: str, hashed_password: str) -> bool:
        """Update user's password."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    hashed_password=hashed_password,
                    updated_at=datetime.utcnow(),
                )
            )
            await session.commit()
            return result.rowcount > 0


user_repository = UserRepository()