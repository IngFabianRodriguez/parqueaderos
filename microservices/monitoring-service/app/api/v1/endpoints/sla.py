"""SLA reporting endpoints — RF-111, RF-113."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from typing import Annotated

from app.db.session import AsyncSession, get_db
from app.services.sla_service import SLAService
from app.schemas.monitoring import SLAReportRequest, SLAReportResponse


router = APIRouter(prefix="/sla", tags=["sla"])


def _get_tenant_id(x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None) -> UUID:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing X-Tenant-Id header")
    return UUID(x_tenant_id)


@router.post(
    "/report",
    response_model=SLAReportResponse,
    summary="Generate SLA report (RF-113)",
)
async def generate_sla_report(
    request: SLAReportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
) -> SLAReportResponse:
    """Generate an SLA report for a service within a date range."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = SLAService(db)
    return await service.generate_report(tenant_id, request)


@router.get(
    "/uptime/{service_id}",
    summary="Current uptime percentage",
)
async def get_current_uptime(
    service_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> dict:
    """Calculate current uptime percentage for a service over the last N days."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = SLAService(db)
    uptime = await service.get_current_uptime(tenant_id, service_id, days=days)
    return {
        "service_id": service_id,
        "uptime_percent": uptime,
        "window_days": days,
    }