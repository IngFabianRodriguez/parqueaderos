"""API v1 router for monitoring-service."""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.monitoring import (
    ServiceHealthResponse,
    AlertCreate,
    AlertResponse,
    AlertListResponse,
    SLAReportRequest,
    SLAReportResponse,
)
from app.core.security import get_current_tenant

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health/services", response_model=list[ServiceHealthResponse])
async def list_service_health(
    tenant_id: str = Depends(get_current_tenant),
):
    """List health status of all services for a tenant."""
    # TODO(RF-100): Implement health check aggregation
    return []


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    tenant_id: str = Depends(get_current_tenant),
):
    """Create a new alert."""
    # TODO(RF-101): Implement alert creation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    tenant_id: str = Depends(get_current_tenant),
):
    """List alerts for tenant."""
    # TODO(RF-102): Implement alert listing
    return {"alerts": []}


@router.post("/sla/report", response_model=SLAReportResponse)
async def get_sla_report(
    request: SLAReportRequest,
    tenant_id: str = Depends(get_current_tenant),
):
    """Generate SLA report."""
    # TODO(RF-104): Implement SLA reporting
    raise HTTPException(status_code=501, detail="Not implemented")
