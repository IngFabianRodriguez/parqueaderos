"""Health check endpoints — RF-100, RF-101."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import Annotated

from app.db.session import AsyncSession, get_db
from app.services.health_check_service import HealthCheckService
from app.schemas.monitoring import DashboardResponse, DashboardServiceEntry


router = APIRouter(prefix="/health", tags=["health"])


def _get_tenant_id(x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None) -> UUID:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing X-Tenant-Id header")
    return UUID(x_tenant_id)


@router.get(
    "/services",
    response_model=list[DashboardServiceEntry],
    summary="List health status of all services (RF-101)",
)
async def list_service_health(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Return aggregated health status for all registered services."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = HealthCheckService(db)
    try:
        dashboard = await service.build_dashboard(tenant_id)
        return dashboard.services
    finally:
        await service.close()


@router.get(
    "/services/{service_id}",
    response_model=DashboardServiceEntry,
    summary="Health check for a specific service (RF-100)",
)
async def get_service_health(
    service_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Perform active health check against a specific registered service."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = HealthCheckService(db)
    try:
        dashboard = await service.build_dashboard(tenant_id)
        for svc in dashboard.services:
            if svc.service_id == service_id:
                return svc
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    finally:
        await service.close()


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Health dashboard with all services (RF-101)",
)
async def get_health_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Return the health dashboard with status of all registered services."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = HealthCheckService(db)
    try:
        return await service.build_dashboard(tenant_id)
    finally:
        await service.close()


# ─────────────────────────────────────────────────────────────────────────────
# Liveness / Readiness probes (Kubernetes)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/live", summary="Liveness probe")
async def liveness():
    """Returns 200 if the process is alive. Used by Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def readiness(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Verifies DB connectivity.
    Used by Kubernetes readiness probe to determine if pod can receive traffic.
    """
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database not ready: {exc}")