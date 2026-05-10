"""Pytest configuration and fixtures for auth-service tests."""

import os
import sys
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Set testing environment before imports
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ==================== Event Loop ====================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Database Fixtures ====================

@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine with SQLite in-memory."""
    from app.db.base import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_db(test_engine):
    """Provide a test database with committed data."""
    from app.db.base import Base

    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # Create tables
        await session.run_sync(Base.metadata.create_all)

    yield async_session

    # Cleanup
    await test_engine.dispose()


# ==================== User Fixtures ====================

@pytest.fixture
def test_user_id() -> str:
    """Generate a test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def test_tenant_id() -> str:
    """Generate a test tenant ID."""
    return str(uuid.uuid4())


@pytest.fixture
def test_user_data(test_user_id, test_tenant_id) -> dict:
    """Generate test user data."""
    return {
        "id": test_user_id,
        "tenant_id": test_tenant_id,
        "email": "test@example.com",
        "password": "testpassword123",
        "hashed_password": None,  # Will be set by service
        "full_name": "Test User",
        "rol": "cliente",
        "is_verified": False,
        "mfa_enabled": False,
        "created_at": datetime.utcnow(),
    }


# ==================== Session Fixtures ====================

@pytest.fixture
def test_session_id() -> str:
    """Generate a test session ID."""
    return str(uuid.uuid4())


@pytest.fixture
def test_refresh_token() -> str:
    """Generate a test refresh token."""
    return str(uuid.uuid4())


# ==================== Token Fixtures ====================

@pytest.fixture
def access_token(test_user_id, test_tenant_id) -> str:
    """Generate a test access token."""
    from app.services.auth_service import AuthService

    return AuthService.create_access_token(
        data={"sub": test_user_id, "tenant_id": test_tenant_id, "rol": "cliente"},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def refresh_token() -> str:
    """Generate a test refresh token."""
    from app.services.auth_service import AuthService
    return AuthService.create_refresh_token()


# ==================== Service Fixtures ====================

@pytest.fixture
def mock_user_repo():
    """Create a mock UserRepository."""
    mock = MagicMock()
    mock.get_by_email = AsyncMock(return_value=None)
    mock.get_by_id = AsyncMock(return_value=None)
    mock.create = AsyncMock()
    mock.update_last_login = AsyncMock(return_value=True)
    mock.set_mfa_secret = AsyncMock(return_value=True)
    mock.enable_mfa = AsyncMock(return_value=True)
    mock.update_password = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_session_repo():
    """Create a mock SessionRepository."""
    mock = MagicMock()
    mock.create = AsyncMock()
    mock.get_by_refresh_token = AsyncMock(return_value=None)
    mock.get_active_sessions = AsyncMock(return_value=[])
    mock.revoke_session = AsyncMock(return_value=True)
    mock.revoke_all_user_sessions = AsyncMock(return_value=0)
    return mock


@pytest.fixture
def mock_password_reset_repo():
    """Create a mock PasswordResetTokenRepository."""
    mock = MagicMock()
    mock.create_token = AsyncMock()
    mock.get_valid_token = AsyncMock(return_value=None)
    mock.mark_token_used = AsyncMock(return_value=True)
    mock.get_token_by_user = AsyncMock(return_value=None)
    mock.delete_token = AsyncMock(return_value=True)
    mock.delete_user_tokens = AsyncMock(return_value=0)
    return mock


# ==================== Auth Service Fixtures ====================

@pytest.fixture
def auth_service_instance(mock_user_repo, mock_session_repo, mock_password_reset_repo):
    """Create an AuthService with mocked repositories."""
    from app.services.auth_service import AuthService

    service = AuthService()
    service.user_repo = mock_user_repo
    service.session_repo = mock_session_repo
    service.password_reset_repo = mock_password_reset_repo
    return service


# ==================== Password Fixtures ====================

@pytest.fixture
def hashed_password():
    """Generate a bcrypt hashed password."""
    from app.services.auth_service import AuthService
    return AuthService.hash_password("testpassword123")


# ==================== Mock User Object ====================

@pytest.fixture
def mock_user(test_user_id, test_tenant_id, hashed_password):
    """Create a mock User object."""
    from app.db.models import User

    user = MagicMock(spec=User)
    user.id = test_user_id
    user.tenant_id = test_tenant_id
    user.email = "test@example.com"
    user.hashed_password = hashed_password
    user.full_name = "Test User"
    user.rol = "cliente"
    user.is_active = True
    user.is_verified = False
    user.mfa_enabled = False
    user.mfa_secret = None
    user.created_at = datetime.utcnow()
    user.last_login_at = None
    return user


# ==================== Mock Session Object ====================

@pytest.fixture
def mock_session_record(test_session_id, test_user_id, test_tenant_id, refresh_token):
    """Create a mock Session object."""
    from app.db.models import Session

    session = MagicMock(spec=Session)
    session.id = test_session_id
    session.user_id = test_user_id
    session.tenant_id = test_tenant_id
    session.refresh_token = refresh_token
    session.expires_at = datetime.utcnow() + timedelta(days=7)
    session.is_revoked = False
    session.created_at = datetime.utcnow()
    return session


# ==================== FastAPI Test Client Fixtures ====================

@pytest_asyncio.fixture
async def async_client(test_db):
    """Create an async test client using httpx AsyncClient."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    # Override database dependency
    from app.db.session import get_db

    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ==================== HTTPX AsyncClient ====================

@pytest_asyncio.fixture
async def httpx_client():
    """Create an httpx AsyncClient for API testing."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ==================== Validation Fixtures ====================

@pytest.fixture
def valid_email() -> str:
    """A valid email address."""
    return "user@example.com"


@pytest.fixture
def invalid_email() -> str:
    """An invalid email address."""
    return "not-an-email"


@pytest.fixture
def valid_password() -> str:
    """A valid password (8+ characters)."""
    return "securepassword123"


@pytest.fixture
def short_password() -> str:
    """A password that's too short."""
    return "short"


# ==================== Cleanup ====================

@pytest.fixture(autouse=True)
def cleanup_password_reset_tokens():
    """Clear password reset tokens after each test."""
    yield
    try:
        from app.repositories.password_reset_repository import PasswordResetTokenRepository
        PasswordResetTokenRepository.clear_all()
    except Exception:
        # Ignore errors during teardown (e.g., DB engine not available in unit tests)
        pass


# ==================== Coverage Helpers ====================

@pytest.fixture
def sample_register_data(test_tenant_id) -> dict:
    """Sample registration data."""
    return {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User",
        "tenant_id": test_tenant_id,
        "rol": "cliente",
    }


@pytest.fixture
def sample_login_data() -> dict:
    """Sample login data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
    }