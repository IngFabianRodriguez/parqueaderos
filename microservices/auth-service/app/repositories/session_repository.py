"""Session repository for database operations."""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session
from app.db.session import AsyncSessionLocal


class SessionRepository:
    """Repository for Session database operations."""

    @staticmethod
    async def create(
        session: AsyncSession,
        id: str,
        user_id: str,
        tenant_id: str,
        refresh_token: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Session:
        """Create a new session."""
        session_record = Session(
            id=id,
            user_id=user_id,
            tenant_id=tenant_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            is_revoked=False,
            created_at=datetime.utcnow(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        session.add(session_record)
        return session_record

    @staticmethod
    async def get_by_refresh_token(refresh_token: str) -> Optional[Session]:
        """Get session by refresh token."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.refresh_token == refresh_token,
                        Session.is_revoked == False,
                    )
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_active_sessions(user_id: str) -> List[Session]:
        """Get all active sessions for a user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.user_id == user_id,
                        Session.is_revoked == False,
                    )
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def revoke_session(session_id: str) -> bool:
        """Revoke a session by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(is_revoked=True)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def revoke_all_user_sessions(user_id: str) -> int:
        """Revoke all sessions for a user. Returns count of revoked sessions."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Session)
                .where(
                    and_(
                        Session.user_id == user_id,
                        Session.is_revoked == False,
                    )
                )
                .values(is_revoked=True)
            )
            await session.commit()
            return result.rowcount

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """Delete expired sessions. Returns count of deleted sessions."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                update(Session)
                .where(Session.expires_at < datetime.utcnow())
                .values(is_revoked=True)
            )
            await session.commit()
            return result.rowcount

    @staticmethod
    async def get_session_by_id(session_id: str) -> Optional[Session]:
        """Get session by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Session).where(Session.id == session_id)
            )
            return result.scalar_one_or_none()


session_repository = SessionRepository()