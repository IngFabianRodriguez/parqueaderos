"""conftest.py — shared pytest configuration and fixtures for monitoring-service.

All DB/HTTP/external calls are mocked so tests run without any real infrastructure.
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure the app module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# Mock async session — fully mocked, no real DB needed
# ─────────────────────────────────────────────────────────────────────────────

def _make_mock_session():
    """Create a fully async-mocked AsyncSession with no real engine."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=None), scalars=AsyncMock(return_value=MagicMock(all=AsyncMock(return_value=[]))), one=AsyncMock(return_value=MagicMock()), all=AsyncMock(return_value=[])))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.begin = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.get_bind = MagicMock(return_value=None)
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Pytest configuration — patch BEFORE app is imported
# ─────────────────────────────────────────────────────────────────────────────

# Patch _get_engine and _get_session_maker at module load time so no asyncpg import happens
with patch("app.db.session._get_engine", MagicMock()), \
     patch("app.db.session._get_session_maker", MagicMock()):

    # Now import the app — lazy engine is mocked, no asyncpg needed
    from app.main import app
    from app.db.session import get_db


# ─────────────────────────────────────────────────────────────────────────────
# Pytest override — replace FastAPI dependency injection
# ─────────────────────────────────────────────────────────────────────────────

def _mock_get_db():
    """Yields the mock session — used as FastAPI dependency override."""
    session = _make_mock_session()
    async def _gen():
        yield session
    return _gen()


# Override get_db in the app's dependency injection system
app.dependency_overrides[get_db] = lambda: _mock_get_db()


# ─────────────────────────────────────────────────────────────────────────────
# UUID fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tenant_id() -> uuid4:
    return uuid4()


@pytest.fixture
def user_id() -> uuid4:
    return uuid4()


@pytest.fixture
def service_id() -> str:
    return "test-service-001"


@pytest.fixture
def another_service_id() -> str:
    return "test-service-002"


@pytest.fixture
def auth_headers(tenant_id, user_id) -> dict[str, str]:
    return {
        "X-Tenant-Id": str(tenant_id),
        "X-User-Id": str(user_id),
        "X-Trace-ID": "test-trace-id",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Mock database session fixture (for unit tests)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db_session():
    """Async mock for sqlalchemy.ext.asyncio.AsyncSession."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(
        scalar_one_or_none=AsyncMock(return_value=None),
        scalars=AsyncMock(return_value=MagicMock(all=AsyncMock(return_value=[]))),
        one=AsyncMock(return_value=MagicMock()),
        all=AsyncMock(return_value=[]),
        rowcount=AsyncMock(return_value=0),
    ))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.begin = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.get_bind = MagicMock(return_value=None)
    return session


# ─────────────────────────────────────────────────────────────────────────────
# Mock repository classes
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_service_registry_repo():
    repo = MagicMock()
    repo.get_by_service_id = AsyncMock(return_value=None)
    repo.list_active = AsyncMock(return_value=[])
    repo.update_health = AsyncMock(return_value=(MagicMock(), MagicMock()))
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_alert_repo():
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=([], 0))
    repo.acknowledge = AsyncMock()
    repo.silence = AsyncMock()
    repo.resolve = AsyncMock()
    repo.has_recent_firing = AsyncMock(return_value=False)
    return repo


@pytest.fixture
def mock_maintenance_window_repo():
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list = AsyncMock(return_value=[])
    repo.list_active = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_metric_record_repo():
    repo = MagicMock()
    repo.record = AsyncMock()
    repo.query = AsyncMock(return_value=[])
    return repo


# ─────────────────────────────────────────────────────────────────────────────
# Sample domain objects
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_service_registry(tenant_id, service_id):
    """Minimal ServiceRegistry mock."""
    from app.db.models import ServiceRegistry
    svc = MagicMock(spec=ServiceRegistry)
    svc.id = uuid4()
    svc.tenant_id = tenant_id
    svc.service_id = service_id
    svc.service_name = "Test Service"
    svc.health_url = "http://localhost:8001/health"
    svc.is_active = True
    svc.metadata_ = {}
    return svc


@pytest.fixture
def sample_alert(tenant_id, service_id):
    """Minimal Alert mock."""
    from app.db.models import Alert
    alert = MagicMock(spec=Alert)
    alert.id = uuid4()
    alert.tenant_id = tenant_id
    alert.service_id = service_id
    alert.service_name = "Test Service"
    alert.type_ = "SERVICE_DOWN"
    alert.severity = "CRITICAL"
    alert.status = "FIRING"
    alert.message = "Service is down"
    alert.payload = {}
    alert.acknowledged = False
    alert.acknowledged_at = None
    alert.acknowledged_by = None
    alert.silenced_until = None
    alert.resolved_at = None
    alert.created_at = datetime.now(timezone.utc)
    alert.updated_at = datetime.now(timezone.utc)
    return alert


@pytest.fixture
def sample_health_check_record(tenant_id, service_id):
    """Minimal ServiceHealthRecord mock."""
    from app.db.models import ServiceHealthRecord
    record = MagicMock(spec=ServiceHealthRecord)
    record.id = uuid4()
    record.tenant_id = tenant_id
    record.service_id = service_id
    record.status = "UP"
    record.latency_ms = 15
    record.checked_at = datetime.now(timezone.utc)
    return record


# ─────────────────────────────────────────────────────────────────────────────
# HTTP client fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client — uses app.dependency_overrides for mock DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─────────────────────────────────────────────────────────────────────────────
# Pytest configuration
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "unit: unit test")
    config.addinivalue_line("markers", "api: api integration test")