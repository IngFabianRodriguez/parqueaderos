"""Maintenance window endpoints — RF-108."""
from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Annotated

from app.db.session import AsyncSession, get_db
from app.services.maintenance_window_service import MaintenanceWindowService
from app.schemas.monitoring import (
    MaintenanceWindowCreate, MaintenanceWindowUpdate, MaintenanceWindowResponse,
)


router = APIRouter(prefix="/maintenance-windows", tags=["maintenance"])


def _get_tenant_id(x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None) -> UUID:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing X-Tenant-Id header")
    return UUID(x_tenant_id)


@router.post(
    "",
    response_model=MaintenanceWindowResponse,
    status_code=201,
    summary="Create maintenance window (RF-108)",
)
async def create_maintenance_window(
    window_in: MaintenanceWindowCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Create a new maintenance window. Overlapping windows return 409."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    return await service.create_window(tenant_id, window_in)


@router.get(
    "",
    response_model=list[MaintenanceWindowResponse],
    summary="List maintenance windows",
)
async def list_maintenance_windows(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """List all maintenance windows for the tenant."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    return await service.list_windows(tenant_id)


@router.get(
    "/{window_id}",
    response_model=MaintenanceWindowResponse,
    summary="Get maintenance window",
)
async def get_maintenance_window(
    window_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Get a specific maintenance window."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    result = await service.get_window(tenant_id, window_id)
    if not result:
        raise HTTPException(status_code=404, detail="Maintenance window not found")
    return result


@router.patch(
    "/{window_id}/extend",
    response_model=MaintenanceWindowResponse,
    summary="Extend maintenance window",
)
async def extend_maintenance_window(
    window_id: UUID,
    new_end_time: datetime,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Extend an active maintenance window."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    result = await service.extend_window(tenant_id, window_id, new_end_time)
    if not result:
        raise HTTPException(status_code=404, detail="Maintenance window not found")
    return result


@router.delete(
    "/{window_id}",
    status_code=204,
    summary="Cancel maintenance window",
)
async def cancel_maintenance_window(
    window_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Cancel a scheduled or active maintenance window."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    result = await service.cancel_window(tenant_id, window_id)
    if not result:
        raise HTTPException(status_code=404, detail="Maintenance window not found")


@router.get(
    "/{window_id}/silenced-alerts",
    summary="Get silenced alerts for a window",
)
async def get_silenced_alerts(
    window_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Return alerts silenced by a maintenance window."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MaintenanceWindowService(db)
    return await service.get_silenced_alerts(tenant_id, window_id)