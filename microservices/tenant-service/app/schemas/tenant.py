"""Pydantic schemas for tenant-service."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class PlanEnum(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CHURNED = "churned"


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    plan: PlanEnum = PlanEnum.STARTER
    config: Optional[dict] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Parqueadero Central",
            "plan": "starter",
            "config": {"timezone": "America/Bogota", "currency": "COP"}
        }
    })


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    plan: Optional[PlanEnum] = None
    config: Optional[dict] = None

    model_config = ConfigDict(extra="ignore")


class TenantResponse(BaseModel):
    id: UUID
    name: str
    plan: PlanEnum
    status: TenantStatus
    config: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantListResponse(BaseModel):
    tenants: list[TenantResponse]
    total: int
    page: int
    page_size: int


class TenantConfigGet(BaseModel):
    config: dict


class TenantUsageResponse(BaseModel):
    tenant_id: UUID
    sedes_count: int
    users_count: int
    api_calls_today: int
    active_sessions: int
