"""Metrics endpoints — RF-103, RF-104, RF-105."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Annotated
from datetime import datetime

from app.db.session import AsyncSession, get_db
from app.services.metrics_service import MetricsService
from app.services.sla_service import BusinessMetricsService
from app.schemas.monitoring import (
    MetricsQuery, MetricsExportResponse, TopSlowEndpoint,
    BusinessMetricsResponse,
)


router = APIRouter(prefix="/metrics", tags=["metrics"])


def _get_tenant_id(x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None) -> UUID:
    if not x_tenant_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Missing X-Tenant-Id header")
    return UUID(x_tenant_id)


@router.get(
    "/infrastructure",
    summary="Infrastructure metrics (RF-103)",
)
async def get_infrastructure_metrics(
    service_id: Annotated[str, Query(description="Service ID to query")],
    from_: Annotated[datetime, Query(alias="from", description="Start time (ISO 8601)")],
    to: Annotated[datetime, Query(description="End time (ISO 8601)")],
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Query infrastructure metrics (CPU, RAM, disk, network) for a service."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MetricsService(db)
    return await service.get_infrastructure_metrics(tenant_id, service_id, from_, to)


@router.get(
    "/application",
    summary="Application metrics (RF-104)",
)
async def get_application_metrics(
    service_id: Annotated[str, Query(description="Service ID to query")],
    from_: Annotated[datetime, Query(alias="from", description="Start time (ISO 8601)")],
    to: Annotated[datetime, Query(description="End time (ISO 8601)")],
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Query application metrics (latency, throughput, error rate) for a service."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MetricsService(db)
    return await service.get_application_metrics(tenant_id, service_id, from_, to)


@router.get(
    "/top-slow",
    response_model=list[TopSlowEndpoint],
    summary="Top slow endpoints (RF-104)",
)
async def get_top_slow_endpoints(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Return the top N slowest endpoints across all services."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MetricsService(db)
    return await service.get_top_slow_endpoints(tenant_id, limit=limit)


@router.get(
    "/export",
    response_model=MetricsExportResponse,
    summary="Export metrics (RF-103, RF-104)",
)
async def export_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
    service_id: Annotated[str | None, Query(description="Service ID")] = None,
    metric_type: Annotated[str | None, Query(description="Metric type: cpu, memory, disk, network, latency, throughput")] = None,
    from_: Annotated[datetime | None, Query(alias="from", description="Start time (ISO 8601)")] = None,
    to: Annotated[datetime | None, Query(description="End time (ISO 8601)")] = None,
    format_: Annotated[str, Query(alias="format", description="Export format: json or csv")] = "json",
):
    """Export metrics in JSON or CSV format."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = MetricsService(db)
    # Default to last 24h
    if from_ is None:
        from_ = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    if to is None:
        to = datetime.utcnow()

    query = MetricsQuery(
        service_id=service_id,
        metric_type=metric_type,
        from_=from_,
        to=to,
    )
    return await service.export_metrics(tenant_id, query, format_=format_)


@router.get(
    "/business",
    response_model=BusinessMetricsResponse,
    summary="Business metrics (RF-114)",
)
async def get_business_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Query(alias="X-Tenant-Id")] = None,
):
    """Return aggregated business metrics for the tenant."""
    tenant_id = _get_tenant_id(x_tenant_id)
    service = BusinessMetricsService()
    return await service.get_metrics(tenant_id)