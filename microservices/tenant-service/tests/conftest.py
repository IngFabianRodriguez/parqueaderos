"""Pytest fixtures for tenant-service tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
from app.services.tenant_service import TenantService


@pytest.fixture
def sample_tenant_id():
    return uuid4()


@pytest.fixture
def sample_tenant(sample_tenant_id):
    tenant = MagicMock()
    tenant.id = sample_tenant_id
    tenant.name = "Test Tenant"
    tenant.plan = "starter"
    tenant.status = "active"
    tenant.config = {"timezone": "America/Bogota"}
    tenant.created_at = datetime.now(timezone.utc)
    tenant.updated_at = datetime.now(timezone.utc)
    return tenant


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def tenant_service(mock_db_session):
    return TenantService(mock_db_session)


@pytest.fixture
def make_mock_tenant():
    def _make():
        tenant = MagicMock()
        tenant.id = uuid4()
        tenant.name = "Mock Tenant"
        tenant.plan = "starter"
        tenant.status = "active"
        tenant.config = {}
        tenant.created_at = datetime.now(timezone.utc)
        tenant.updated_at = datetime.now(timezone.utc)
        return tenant
    return _make


@pytest.fixture
async def async_client():
    """Async HTTP client for API tests — avoids triggering asyncpg at import."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client