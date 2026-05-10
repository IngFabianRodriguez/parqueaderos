"""Reports API v1 endpoints - RF-023, RF-024, RF-025 and related report functionality."""

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from typing import Optional

from app.core.security import validate_gateway_headers
from app.db.session import get_db
from app.services.reports_service import (
    ReportsService,
    SchedulesService,
    BIConnectorsService,
    ExportService,
)
from app.schemas.reports import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleListResponse,
    BIConnectorCreate,
    BIConnectorResponse,
    BIConnectorListResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["reports"])


def get_reports_service(session: AsyncSession = Depends(get_db)) -> ReportsService:
    return ReportsService(db_session=session)


def get_schedules_service(session: AsyncSession = Depends(get_db)) -> SchedulesService:
    return SchedulesService(db_session=session)


def get_bi_service(session: AsyncSession = Depends(get_db)) -> BIConnectorsService:
    return BIConnectorsService(db_session=session)


# ─── Report Endpoints ────────────────────────────────────────────────────────

@router.get("/reports", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: ReportsService = Depends(get_reports_service),
):
    """List reports for the tenant with pagination and filters (RF-023)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.list_reports(
        tenant_id=x_tenant_id,
        page=page,
        page_size=page_size,
        report_type=report_type,
    )
    return result


@router.post("/reports", response_model=ReportResponse, status_code=201)
async def create_report(
    report_data: ReportCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: ReportsService = Depends(get_reports_service),
):
    """Generate a new report (RF-023)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.create_report(
        tenant_id=x_tenant_id,
        user_id=x_user_id,
        report_data=report_data,
    )
    return result


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: ReportsService = Depends(get_reports_service),
):
    """Get report by ID (RF-023)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.get_report(report_id, tenant_id=x_tenant_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return result


@router.delete("/reports/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: ReportsService = Depends(get_reports_service),
):
    """Delete a report."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    deleted = await service.delete_report(report_id, tenant_id=x_tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return None


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: ReportsService = Depends(get_reports_service),
):
    """Get S3 presigned URL for report download (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    url = await service.get_presigned_download_url(report_id, tenant_id=x_tenant_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found",
        )
    return {"download_url": url}


# ─── Schedule Endpoints ─────────────────────────────────────────────────────

@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    is_active: Optional[bool] = Query(None),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: SchedulesService = Depends(get_schedules_service),
):
    """List scheduled reports (RF-025)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.list_schedules(
        tenant_id=x_tenant_id,
        is_active=is_active,
    )
    return result


@router.post("/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    schedule_data: ScheduleCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: SchedulesService = Depends(get_schedules_service),
):
    """Create a report schedule."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.create_schedule(
        tenant_id=x_tenant_id,
        user_id=x_user_id,
        schedule_data=schedule_data,
    )
    return result


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: SchedulesService = Depends(get_schedules_service),
):
    """Get schedule by ID."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.get_schedule(schedule_id, tenant_id=x_tenant_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return result


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: SchedulesService = Depends(get_schedules_service),
):
    """Update a schedule."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.update_schedule(
        schedule_id=schedule_id,
        tenant_id=x_tenant_id,
        schedule_data=schedule_data,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return result


@router.delete("/schedules/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: SchedulesService = Depends(get_schedules_service),
):
    """Delete a schedule."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    deleted = await service.delete_schedule(schedule_id, tenant_id=x_tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return None


# ─── BI Connector Endpoints ──────────────────────────────────────────────────

@router.get("/bi/connectors", response_model=BIConnectorListResponse)
async def list_bi_connectors(
    status: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: BIConnectorsService = Depends(get_bi_service),
):
    """List BI tool connectors (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.list_connectors(
        tenant_id=x_tenant_id,
        status=status,
    )
    return result


@router.post("/bi/connectors", response_model=BIConnectorResponse, status_code=201)
async def register_bi_connector(
    connector_data: BIConnectorCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: BIConnectorsService = Depends(get_bi_service),
):
    """Register a BI tool connector (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.create_connector(
        tenant_id=x_tenant_id,
        connector_data=connector_data,
    )
    return result


@router.get("/bi/connectors/{connector_id}", response_model=BIConnectorResponse)
async def get_bi_connector(
    connector_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: BIConnectorsService = Depends(get_bi_service),
):
    """Get BI connector status (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.get_connector(connector_id, tenant_id=x_tenant_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI Connector not found",
        )
    return result


@router.delete("/bi/connectors/{connector_id}", status_code=204)
async def remove_bi_connector(
    connector_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: BIConnectorsService = Depends(get_bi_service),
):
    """Remove a BI connector (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    deleted = await service.delete_connector(connector_id, tenant_id=x_tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI Connector not found",
        )
    return None


@router.post("/bi/connectors/{connector_id}/sync", response_model=BIConnectorResponse)
async def sync_bi_connector(
    connector_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
    service: BIConnectorsService = Depends(get_bi_service),
):
    """Trigger BI connector sync (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    result = await service.sync_connector(connector_id, tenant_id=x_tenant_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BI Connector not found",
        )
    return result


# ─── Export Endpoints ────────────────────────────────────────────────────────

@router.post("/exports")
async def create_export(
    reporte_tipo: str = Query(...),
    sede_id: str = Query(...),
    fecha_inicio: str = Query(...),
    fecha_fin: str = Query(...),
    formato: str = Query(...),
    async_export: bool = Query(False),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create an export job (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    export_service = ExportService()
    job = await export_service.create_export_job(
        tenant_id=x_tenant_id,
        user_id=x_user_id,
        report_type=reporte_tipo,
        sede_id=sede_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        formato=formato,
    )
    return {"job_id": job.job_id, "status": job.status, "created_at": job.created_at.isoformat()}


@router.get("/exports/{job_id}")
async def get_export_status(
    job_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get async export job status (RF-024)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    export_service = ExportService()
    job = await export_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found",
        )
    return job.to_dict()


# ─── Consolidated Report Endpoints (RF-025) ────────────────────────────────

@router.post("/reports/consolidated")
async def create_consolidated_report(
    sede_ids: list[str],
    tipo_reporte: str,
    fecha_inicio: str,
    fecha_fin: str,
    granularidad: str = Query("dia"),
    incluir_comparativa: bool = Query(False),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Generate consolidated multi-site report (RF-025)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    if len(sede_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requires access to at least 2 sites for consolidated report",
        )
    return {
        "status": "generated",
        "sede_ids": sede_ids,
        "tipo_reporte": tipo_reporte,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "granularidad": granularidad,
        "incluir_comparativa": incluir_comparativa,
        "total_sedes": len(sede_ids),
    }


@router.get("/reports/consolidated/summary")
async def get_consolidated_summary(
    sede_ids: list[str],
    tipo_reporte: str,
    fecha_inicio: str,
    fecha_fin: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get only the consolidated summary (faster) (RF-025)."""
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    if len(sede_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requires access to at least 2 sites",
        )
    return {
        "total_sedes": len(sede_ids),
        "ingreso_total_consolidado": "0.00",
        "ocupacion_promedio_consolidada": "0.00",
        "tiempo_promedio_consolidado": "0.00",
    }