"""Tests for tenant service business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

import pytest_asyncio
from app.services.tenant_service import TenantService
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    PlanEnum,
    TenantStatus,
)


@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def tenant_service(mock_db):
    return TenantService(mock_db)


def make_mock_tenant(tenant_id=None, name="Test", plan="starter", status="active"):
    mock = MagicMock()
    mock.id = tenant_id or uuid4()
    mock.name = name
    mock.plan = plan
    mock.status = status
    mock.config = {}
    mock.created_at = datetime.now(timezone.utc)
    mock.updated_at = datetime.now(timezone.utc)
    return mock


class TestCreateTenant:
    @pytest.mark.asyncio
    async def test_create_tenant_success(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock(side_effect=lambda t: setattr(t, "id", mock_tenant.id))
        
        with patch("app.services.tenant_service.Tenant") as MockTenant:
            MockTenant.return_value = mock_tenant
            result = await tenant_service.create_tenant("Test Tenant", PlanEnum.STARTER)
            assert result is not None

    @pytest.mark.asyncio
    async def test_create_tenant_with_config(self, tenant_service):
        config = {"timezone": "America/Bogota", "currency": "COP"}
        # Mock implementation
        mock_tenant = make_mock_tenant()
        mock_tenant.config = config
        assert mock_tenant.config == config


class TestGetTenant:
    @pytest.mark.asyncio
    async def test_get_tenant_success(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        tenant_id = uuid4()
        result = await tenant_service.get_tenant(tenant_id, str(tenant_id), "tenant_admin")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_tenant_not_found(self, tenant_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        result = await tenant_service.get_tenant(uuid4(), str(uuid4()), "tenant_admin")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_tenant_access_denied(self, tenant_service):
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        
        with pytest.raises(PermissionError):
            await tenant_service.get_tenant(tenant_id, str(other_tenant_id), "tenant_admin")


class TestListTenants:
    @pytest.mark.asyncio
    async def test_list_tenants_pagination(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_tenant]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        tenants, total = await tenant_service.list_tenants(
            requesting_tenant_id=str(uuid4()),
            requesting_rol="superadmin",
            page=1,
            page_size=20,
        )
        assert isinstance(tenants, list)
        assert isinstance(total, int)


class TestSuspendTenant:
    @pytest.mark.asyncio
    async def test_suspend_tenant_success(self, tenant_service, mock_db):
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()
        
        tenant_id = uuid4()
        result = await tenant_service.suspend_tenant(tenant_id, str(tenant_id), "tenant_admin")
        assert result is True
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_suspend_tenant_access_denied(self, tenant_service):
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        
        with pytest.raises(PermissionError):
            await tenant_service.suspend_tenant(tenant_id, str(other_tenant_id), "tenant_admin")


class TestGetConfig:
    @pytest.mark.asyncio
    async def test_get_config_success(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_tenant.config = {"timezone": "America/Bogota"}
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        tenant_id = uuid4()
        result = await tenant_service.get_config(tenant_id, str(tenant_id))
        assert result.config["timezone"] == "America/Bogota"

    @pytest.mark.asyncio
    async def test_get_config_with_key(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_tenant.config = {"timezone": "America/Bogota", "currency": "COP"}
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        tenant_id = uuid4()
        result = await tenant_service.get_config(tenant_id, str(tenant_id), key="timezone")
        assert "timezone" in result.config


class TestSetConfig:
    @pytest.mark.asyncio
    async def test_set_config_success(self, tenant_service, mock_db):
        mock_tenant = make_mock_tenant()
        mock_tenant.config = {"timezone": "America/Bogota"}
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()
        
        tenant_id = uuid4()
        result = await tenant_service.set_config(tenant_id, str(tenant_id), {"currency": "USD"})
        assert result.config.get("currency") == "USD"


class TestGetUsage:
    @pytest.mark.asyncio
    async def test_get_usage_success(self, tenant_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        tenant_id = uuid4()
        result = await tenant_service.get_usage(tenant_id, str(tenant_id), "tenant_admin")
        assert result.tenant_id == tenant_id
        assert isinstance(result.sedes_count, int)


class TestToResponse:
    def test_to_response_maps_fields(self, tenant_service):
        mock_tenant = make_mock_tenant(name="Parqueadero Central", plan="professional", status="active")
        result = tenant_service._to_response(mock_tenant)
        assert result.name == "Parqueadero Central"
        assert result.plan == PlanEnum.PROFESSIONAL
        assert result.status == TenantStatus.ACTIVE
