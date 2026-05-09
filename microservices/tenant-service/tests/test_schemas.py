"""Tests for tenant schemas validation."""
import pytest
from pydantic import ValidationError
from uuid import uuid4
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantConfigGet,
    TenantUsageResponse,
    PlanEnum,
    TenantStatus,
)


def test_tenant_create_valid():
    data = TenantCreate(name="Parqueadero Central", plan=PlanEnum.PROFESSIONAL)
    assert data.name == "Parqueadero Central"
    assert data.plan == PlanEnum.PROFESSIONAL
    assert data.config is None


def test_tenant_create_with_config():
    data = TenantCreate(
        name="Test",
        plan=PlanEnum.ENTERPRISE,
        config={"timezone": "America/Bogota", "currency": "COP"},
    )
    assert data.config["timezone"] == "America/Bogota"


def test_tenant_create_empty_name_fails():
    with pytest.raises(ValidationError):
        TenantCreate(name="", plan=PlanEnum.STARTER)


def test_tenant_create_long_name_fails():
    with pytest.raises(ValidationError):
        TenantCreate(name="x" * 256, plan=PlanEnum.STARTER)


def test_tenant_update_partial():
    data = TenantUpdate(name="Nuevo Nombre")
    assert data.name == "Nuevo Nombre"
    assert data.plan is None
    assert data.config is None


def test_tenant_update_plan():
    data = TenantUpdate(plan=PlanEnum.ENTERPRISE)
    assert data.plan == PlanEnum.ENTERPRISE


def test_tenant_update_empty_update():
    data = TenantUpdate()
    assert data.model_dump(exclude_unset=True) == {}


def test_tenant_response_from_attributes():
    from datetime import datetime, timezone
    tenant_id = uuid4()
    now = datetime.now(timezone.utc)
    resp = TenantResponse(
        id=tenant_id,
        name="Test",
        plan=PlanEnum.STARTER,
        status=TenantStatus.ACTIVE,
        config={},
        created_at=now,
        updated_at=now,
    )
    assert resp.id == tenant_id
    assert resp.plan == PlanEnum.STARTER
    assert resp.status == TenantStatus.ACTIVE


def test_tenant_config_get():
    config = TenantConfigGet(config={"key": "value"})
    assert config.config["key"] == "value"


def test_tenant_config_get_empty():
    config = TenantConfigGet(config={})
    assert config.config == {}


def test_tenant_usage_response():
    tenant_id = uuid4()
    usage = TenantUsageResponse(
        tenant_id=tenant_id,
        sedes_count=5,
        users_count=20,
        api_calls_today=1000,
        active_sessions=3,
    )
    assert usage.sedes_count == 5
    assert usage.users_count == 20
    assert usage.api_calls_today == 1000


def test_plan_enum_values():
    assert PlanEnum.STARTER.value == "starter"
    assert PlanEnum.PROFESSIONAL.value == "professional"
    assert PlanEnum.ENTERPRISE.value == "enterprise"


def test_tenant_status_values():
    assert TenantStatus.TRIAL.value == "trial"
    assert TenantStatus.ACTIVE.value == "active"
    assert TenantStatus.SUSPENDED.value == "suspended"
    assert TenantStatus.CHURNED.value == "churned"
