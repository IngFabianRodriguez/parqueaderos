"""Pytest fixtures for tenant-service tests."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import validate_gateway_headers
from app.services.tenant_service import TenantService


@pytest.fixture
def sample_tenant_id():
    return uuid4()


@pytest.fixture
def sample_tenant(sample_tenant_id):
    from app.db.models import Tenant
    tenant = MagicMock(spec=Tenant)
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
def auth_headers():
    return {
        "X-User-Id": "user-123",
        "X-Rol": "tenant_admin",
        "X-Tenant-Id": "550e8400-e29b-41d4-a716-446655440000",
    }


@pytest.fixture
def superadmin_headers():
    return {
        "X-User-Id": "admin-123",
        "X-Rol": "superadmin",
        "X-Tenant-Id": "00000000-0000-0000-0000-000000000000",
    }


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
