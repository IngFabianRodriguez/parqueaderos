"""Async database session management — lazy engine init."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings

_engine = None
_AsyncSessionLocal = None


def _get_db_url():
    """Get DB URL safely."""
    url = getattr(settings, 'database_url', None)
    if url is None:
        url = getattr(settings, 'DATABASE_URL', None)
    if url is None:
        url = "sqlite+aiosqlite:///:memory:"
    return url


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _get_db_url(),
            pool_size=getattr(settings, 'db_pool_size', 20),
            max_overflow=getattr(settings, 'db_max_overflow', 10),
            pool_timeout=getattr(settings, 'db_pool_timeout', 30),
            echo=getattr(settings, 'debug', False),
            pool_pre_ping=True,
        )
    return _engine


def _get_session_maker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with _get_session_maker()() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database connection."""
    async with _get_engine().begin() as conn:
        pass


async def close_db():
    """Close database connections."""
    global _engine, _AsyncSessionLocal
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _AsyncSessionLocal = None


# Module-level aliases for app.db compatibility (lazy, no engine creation at import)
def __getattr__(name):
    if name == "engine":
        return _get_engine()
    if name == "AsyncSessionLocal":
        return _get_session_maker()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")