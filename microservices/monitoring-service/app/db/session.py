"""Async SQLAlchemy session factory for monitoring-service.

Engine is created lazily to avoid ImportError when asyncpg isn't available
(e.g., in test environments where DB is mocked via conftest).
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TYPE_CHECKING

if TYPE_CHECKING:
    pass


# Module-level lazy engine
_engine = None
_session_maker = None


def _get_engine():
    """Lazily create the async engine."""
    global _engine
    if _engine is None:
        from app.config import get_settings
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            poolclass=NullPool,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_maker():
    """Lazily create the session maker."""
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_maker


# Re-export
AsyncSession = AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async session per request."""
    maker = _get_session_maker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for use outside the FastAPI request cycle."""
    maker = _get_session_maker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()