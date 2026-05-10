"""Reports business logic service."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from app.repositories.report_repository import ReportRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.bi_connector_repository import BIConnectorRepository
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
    ReportFilter,
    ScheduleFilter,
    BIConnectorFilter,
    ExportJobResponse,
)


def _report_to_response(report) -> ReportResponse:
    """Convert SQLAlchemy Report model to ReportResponse dataclass."""
    return ReportResponse(
        id=report.id,
        tenant_id=report.tenant_id,
        name=report.name,
        report_type=report.report_type,
        format=report.format,
        status=report.status,
        file_url=report.file_url,
        file_size_bytes=report.file_size_bytes,
        parameters=json.loads(report.parameters) if report.parameters else None,
        generated_by=report.generated_by,
        error_message=report.error_message,
        created_at=report.created_at,
        completed_at=report.completed_at,
    )


def _schedule_to_response(schedule) -> ScheduleResponse:
    """Convert SQLAlchemy ReportSchedule model to ScheduleResponse dataclass."""
    return ScheduleResponse(
        id=schedule.id,
        tenant_id=schedule.tenant_id,
        name=schedule.name,
        report_type=schedule.report_type,
        schedule_cron=schedule.schedule_cron,
        format=schedule.format,
        parameters=json.loads(schedule.parameters) if schedule.parameters else None,
        recipients=json.loads(schedule.recipients) if schedule.recipients else None,
        is_active=schedule.is_active,
        created_by=schedule.created_by,
        last_run_at=schedule.last_run_at,
        next_run_at=schedule.next_run_at,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def _connector_to_response(connector) -> BIConnectorResponse:
    """Convert SQLAlchemy BIConnector model to BIConnectorResponse dataclass."""
    return BIConnectorResponse(
        id=connector.id,
        tenant_id=connector.tenant_id,
        name=connector.name,
        connector_type=connector.connector_type,
        status=connector.status,
        last_sync_at=connector.last_sync_at,
        last_error=connector.last_error,
        created_at=connector.created_at,
        updated_at=connector.updated_at,
    )


class ReportsService:
    """Service for report generation and management."""

    def __init__(self, db_session: Optional[object] = None):
        self._db_session = db_session

    async def create_report(
        self,
        tenant_id: str,
        user_id: str,
        report_data: ReportCreate,
    ) -> ReportResponse:
        """Create a new report record and return response."""
        repo = ReportRepository(self._db_session)
        report = await repo.create(
            tenant_id=tenant_id,
            name=report_data.name,
            report_type=report_data.report_type,
            generated_by=user_id,
            format=report_data.format,
            parameters=report_data.parameters,
        )
        return _report_to_response(report)

    async def get_report(self, report_id: str, tenant_id: str) -> Optional[ReportResponse]:
        """Get a report by ID."""
        repo = ReportRepository(self._db_session)
        report = await repo.get_by_id(report_id, tenant_id)
        if not report:
            return None
        return _report_to_response(report)

    async def list_reports(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        report_type: Optional[str] = None,
    ) -> ReportListResponse:
        """List reports for a tenant with pagination."""
        repo = ReportRepository(self._db_session)
        reports, total = await repo.list_reports(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            report_type=report_type,
        )
        return ReportListResponse(
            items=[_report_to_response(r) for r in reports],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_report_status(
        self,
        report_id: str,
        status: str,
        file_url: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[ReportResponse]:
        """Update report status after generation."""
        repo = ReportRepository(self._db_session)
        report = await repo.update_status(
            report_id=report_id,
            status=status,
            file_url=file_url,
            file_size_bytes=file_size_bytes,
            error_message=error_message,
        )
        if not report:
            return None
        return _report_to_response(report)

    async def delete_report(self, report_id: str, tenant_id: str) -> bool:
        """Delete a report."""
        repo = ReportRepository(self._db_session)
        return await repo.delete(report_id, tenant_id)

    async def get_presigned_download_url(
        self, report_id: str, tenant_id: str
    ) -> Optional[str]:
        """Get S3 presigned URL for report download."""
        report = await self.get_report(report_id, tenant_id)
        if not report or not report.file_url:
            return None
        # In production, this would generate a real presigned URL
        # For now, return the file_url as-is
        return report.file_url


class SchedulesService:
    """Service for managing report schedules."""

    def __init__(self, db_session: Optional[object] = None):
        self._db_session = db_session

    async def create_schedule(
        self,
        tenant_id: str,
        user_id: str,
        schedule_data: ScheduleCreate,
    ) -> ScheduleResponse:
        """Create a new report schedule."""
        repo = ScheduleRepository(self._db_session)
        schedule = await repo.create(
            tenant_id=tenant_id,
            name=schedule_data.name,
            report_type=schedule_data.report_type,
            schedule_cron=schedule_data.schedule_cron,
            created_by=user_id,
            format=schedule_data.format,
            parameters=schedule_data.parameters,
            recipients=schedule_data.recipients,
            is_active=schedule_data.is_active,
        )
        return _schedule_to_response(schedule)

    async def get_schedule(
        self, schedule_id: str, tenant_id: str
    ) -> Optional[ScheduleResponse]:
        """Get a schedule by ID."""
        repo = ScheduleRepository(self._db_session)
        schedule = await repo.get_by_id(schedule_id, tenant_id)
        if not schedule:
            return None
        return _schedule_to_response(schedule)

    async def list_schedules(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None,
    ) -> ScheduleListResponse:
        """List schedules for a tenant."""
        repo = ScheduleRepository(self._db_session)
        schedules, total = await repo.list_schedules(
            tenant_id=tenant_id,
            is_active=is_active,
        )
        return ScheduleListResponse(
            items=[_schedule_to_response(s) for s in schedules],
            total=total,
        )

    async def update_schedule(
        self,
        schedule_id: str,
        tenant_id: str,
        schedule_data: ScheduleCreate,
    ) -> Optional[ScheduleResponse]:
        """Update a schedule."""
        repo = ScheduleRepository(self._db_session)
        schedule = await repo.update(
            schedule_id=schedule_id,
            tenant_id=tenant_id,
            name=schedule_data.name,
            schedule_cron=schedule_data.schedule_cron,
            format=schedule_data.format,
            parameters=schedule_data.parameters,
            recipients=schedule_data.recipients,
            is_active=schedule_data.is_active,
        )
        if not schedule:
            return None
        return _schedule_to_response(schedule)

    async def delete_schedule(self, schedule_id: str, tenant_id: str) -> bool:
        """Delete a schedule."""
        repo = ScheduleRepository(self._db_session)
        return await repo.delete(schedule_id, tenant_id)


class BIConnectorsService:
    """Service for managing BI connectors."""

    def __init__(self, db_session: Optional[object] = None):
        self._db_session = db_session

    async def create_connector(
        self,
        tenant_id: str,
        connector_data: BIConnectorCreate,
    ) -> BIConnectorResponse:
        """Register a new BI connector."""
        repo = BIConnectorRepository(self._db_session)
        connector = await repo.create(
            tenant_id=tenant_id,
            name=connector_data.name,
            connector_type=connector_data.connector_type,
            config=connector_data.config,
        )
        return _connector_to_response(connector)

    async def get_connector(
        self, connector_id: str, tenant_id: str
    ) -> Optional[BIConnectorResponse]:
        """Get a BI connector by ID."""
        repo = BIConnectorRepository(self._db_session)
        connector = await repo.get_by_id(connector_id, tenant_id)
        if not connector:
            return None
        return _connector_to_response(connector)

    async def list_connectors(
        self,
        tenant_id: str,
        status: Optional[str] = None,
    ) -> BIConnectorListResponse:
        """List BI connectors for a tenant."""
        repo = BIConnectorRepository(self._db_session)
        connectors, total = await repo.list_connectors(
            tenant_id=tenant_id,
            status=status,
        )
        return BIConnectorListResponse(
            items=[_connector_to_response(c) for c in connectors],
            total=total,
        )

    async def sync_connector(
        self, connector_id: str, tenant_id: str
    ) -> Optional[BIConnectorResponse]:
        """Trigger sync for a BI connector."""
        repo = BIConnectorRepository(self._db_session)
        connector = await repo.get_by_id(connector_id, tenant_id)
        if not connector:
            return None
        # Simulate sync: in production this would call the BI tool's API
        now = datetime.utcnow()
        connector = await repo.update_status(
            connector_id=connector_id,
            status="connected",
            last_sync_at=now,
            last_error=None,
        )
        return _connector_to_response(connector)

    async def delete_connector(self, connector_id: str, tenant_id: str) -> bool:
        """Delete a BI connector."""
        repo = BIConnectorRepository(self._db_session)
        return await repo.delete(connector_id, tenant_id)


class ExportService:
    """Service for handling async report exports."""

    def __init__(self):
        self._jobs = {}  # In-memory job store for demo purposes

    async def create_export_job(
        self,
        tenant_id: str,
        user_id: str,
        report_type: str,
        sede_id: str,
        fecha_inicio: str,
        fecha_fin: str,
        formato: str,
    ) -> ExportJobResponse:
        """Create an async export job."""
        job_id = str(uuid.uuid4())
        job = ExportJobResponse(
            job_id=job_id,
            status="pending",
            created_at=datetime.utcnow(),
        )
        self._jobs[job_id] = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "report_type": report_type,
            "sede_id": sede_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "formato": formato,
            "status": "pending",
        }
        return job

    async def get_job_status(self, job_id: str) -> Optional[ExportJobResponse]:
        """Get the status of an export job."""
        job_data = self._jobs.get(job_id)
        if not job_data:
            return None
        return ExportJobResponse(
            job_id=job_id,
            status=job_data["status"],
            created_at=job_data.get("created_at", datetime.utcnow()),
        )