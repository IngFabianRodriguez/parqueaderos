"""Unit tests for reports-service models, schemas, and services."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json

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
    ExportJobResponse,
)


class TestReportSchemas:
    """Tests for Report dataclass schemas."""

    def test_report_create_valid(self):
        """Test ReportCreate with all fields."""
        data = ReportCreate(
            name="Monthly Revenue",
            report_type="ingresos",
            format="pdf",
            parameters={"sede_id": "uuid-123"},
        )
        assert data.name == "Monthly Revenue"
        assert data.report_type == "ingresos"
        assert data.format == "pdf"
        assert data.parameters == {"sede_id": "uuid-123"}

    def test_report_create_minimal(self):
        """Test ReportCreate with only required fields."""
        data = ReportCreate(name="Test", report_type="ocupacion")
        assert data.name == "Test"
        assert data.report_type == "ocupacion"
        assert data.format == "pdf"
        assert data.parameters is None

    def test_report_response_to_dict(self):
        """Test ReportResponse.to_dict()."""
        now = datetime.utcnow()
        resp = ReportResponse(
            id="r-123",
            tenant_id="t-456",
            name="Test Report",
            report_type="ingresos",
            format="pdf",
            status="ready",
            file_url="https://s3.example.com/file.pdf",
            file_size_bytes=2048,
            parameters={"key": "value"},
            generated_by="user-789",
            error_message=None,
            created_at=now,
            completed_at=now,
        )
        d = resp.to_dict()
        assert d["id"] == "r-123"
        assert d["tenant_id"] == "t-456"
        assert d["status"] == "ready"
        assert d["file_size_bytes"] == 2048
        assert d["parameters"] == {"key": "value"}
        assert "created_at" in d

    def test_report_list_response_to_dict(self):
        """Test ReportListResponse.to_dict()."""
        now = datetime.utcnow()
        items = [
            ReportResponse(
                id="r-1",
                tenant_id="t-1",
                name="Report 1",
                report_type="ingresos",
                format="pdf",
                status="ready",
                generated_by="u-1",
                created_at=now,
            ),
            ReportResponse(
                id="r-2",
                tenant_id="t-1",
                name="Report 2",
                report_type="ocupacion",
                format="csv",
                status="pending",
                generated_by="u-1",
                created_at=now,
            ),
        ]
        lst = ReportListResponse(items=items, total=2, page=1, page_size=20)
        d = lst.to_dict()
        assert d["total"] == 2
        assert len(d["items"]) == 2
        assert d["items"][0]["id"] == "r-1"

    def test_report_filter_defaults(self):
        """Test ReportFilter default values."""
        f = ReportFilter(tenant_id="t-123")
        assert f.report_type is None
        assert f.status is None
        assert f.page == 1
        assert f.page_size == 20


class TestScheduleSchemas:
    """Tests for Schedule dataclass schemas."""

    def test_schedule_create_valid(self):
        """Test ScheduleCreate with all fields."""
        data = ScheduleCreate(
            name="Weekly Report",
            report_type="ingresos",
            schedule_cron="0 8 * * 1",
            format="xlsx",
            parameters={"sede_id": "uuid-123"},
            recipients=["admin@example.com", "user@example.com"],
            is_active=True,
        )
        assert data.name == "Weekly Report"
        assert data.schedule_cron == "0 8 * * 1"
        assert data.recipients == ["admin@example.com", "user@example.com"]

    def test_schedule_response_to_dict(self):
        """Test ScheduleResponse.to_dict()."""
        now = datetime.utcnow()
        resp = ScheduleResponse(
            id="s-123",
            tenant_id="t-456",
            name="Test Schedule",
            report_type="ingresos",
            schedule_cron="0 8 * * 1",
            format="pdf",
            parameters=None,
            recipients=["admin@example.com"],
            is_active=True,
            created_by="user-789",
            last_run_at=None,
            next_run_at=None,
            created_at=now,
            updated_at=now,
        )
        d = resp.to_dict()
        assert d["id"] == "s-123"
        assert d["schedule_cron"] == "0 8 * * 1"
        assert d["is_active"] is True
        assert d["recipients"] == ["admin@example.com"]

    def test_schedule_list_response_to_dict(self):
        """Test ScheduleListResponse.to_dict()."""
        now = datetime.utcnow()
        items = [
            ScheduleResponse(
                id="s-1",
                tenant_id="t-1",
                name="Schedule 1",
                report_type="ingresos",
                schedule_cron="0 8 * * 1",
                format="pdf",
                is_active=True,
                created_by="u-1",
                created_at=now,
                updated_at=now,
            ),
        ]
        lst = ScheduleListResponse(items=items, total=1)
        d = lst.to_dict()
        assert d["total"] == 1
        assert len(d["items"]) == 1


class TestBIConnectorSchemas:
    """Tests for BIConnector dataclass schemas."""

    def test_bi_connector_create_valid(self):
        """Test BIConnectorCreate."""
        data = BIConnectorCreate(
            name="Power BI",
            connector_type="powerbi",
            config={"api_key": "secret", "workspace": "default"},
        )
        assert data.connector_type == "powerbi"
        assert data.config["workspace"] == "default"

    def test_bi_connector_response_to_dict(self):
        """Test BIConnectorResponse.to_dict()."""
        now = datetime.utcnow()
        resp = BIConnectorResponse(
            id="c-123",
            tenant_id="t-456",
            name="Tableau Connector",
            connector_type="tableau",
            status="connected",
            last_sync_at=now,
            last_error=None,
            created_at=now,
            updated_at=now,
        )
        d = resp.to_dict()
        assert d["id"] == "c-123"
        assert d["connector_type"] == "tableau"
        assert d["status"] == "connected"

    def test_bi_connector_list_response_to_dict(self):
        """Test BIConnectorListResponse.to_dict()."""
        now = datetime.utcnow()
        items = [
            BIConnectorResponse(
                id="c-1",
                tenant_id="t-1",
                name="Connector 1",
                connector_type="looker",
                status="disconnected",
                created_at=now,
                updated_at=now,
            ),
        ]
        lst = BIConnectorListResponse(items=items, total=1)
        d = lst.to_dict()
        assert d["total"] == 1
        assert d["items"][0]["connector_type"] == "looker"


class TestExportJobResponse:
    """Tests for ExportJobResponse schema."""

    def test_export_job_response_to_dict(self):
        """Test ExportJobResponse.to_dict()."""
        now = datetime.utcnow()
        job = ExportJobResponse(
            job_id="job-123",
            status="completed",
            url="https://s3.example.com/exports/job-123.csv",
            created_at=now,
        )
        d = job.to_dict()
        assert d["job_id"] == "job-123"
        assert d["status"] == "completed"
        assert "created_at" in d


class TestReportModels:
    """Tests for SQLAlchemy Report model."""

    def test_report_model_creation(self, sample_report_model):
        """Test Report model attributes."""
        assert sample_report_model.id == "report-123"
        assert sample_report_model.tenant_id == "tenant-456"
        assert sample_report_model.report_type == "ingresos"
        assert sample_report_model.status == "ready"
        assert sample_report_model.file_size_bytes == 1024

    def test_report_model_defaults(self):
        """Test Report model default values."""
        from app.db.models import Report
        from datetime import datetime
        r = Report(
            id="test-id",
            tenant_id="tenant-id",
            name="Test",
            report_type="test",
            format="pdf",
            status="pending",
            generated_by="user",
            created_at=datetime.utcnow(),
        )
        assert r.file_url is None
        assert r.file_size_bytes is None
        assert r.error_message is None

    def test_schedule_model_creation(self, sample_schedule_model):
        """Test ReportSchedule model attributes."""
        assert sample_schedule_model.id == "schedule-123"
        assert sample_schedule_model.schedule_cron == "0 8 * * 1"
        assert sample_schedule_model.is_active is True

    def test_bi_connector_model_creation(self, sample_bi_connector_model):
        """Test BIConnector model attributes."""
        assert sample_bi_connector_model.id == "connector-123"
        assert sample_bi_connector_model.connector_type == "powerbi"
        assert sample_bi_connector_model.status == "connected"


class TestReportsService:
    """Tests for ReportsService business logic."""

    @pytest.mark.asyncio
    async def test_create_report(self, reports_service, mock_session):
        """Test creating a report via service."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        report_data = ReportCreate(
            name="Test Report",
            report_type="ingresos",
            format="pdf",
        )
        # Mock the repository's create method
        with patch.object(
            reports_service, '_db_session', mock_session
        ):
            result = await reports_service.create_report(
                tenant_id="tenant-123",
                user_id="user-456",
                report_data=report_data,
            )
            assert result is not None
            assert result.tenant_id == "tenant-123"
            assert result.name == "Test Report"

    @pytest.mark.asyncio
    async def test_list_reports(self, reports_service, mock_session):
        """Test listing reports."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await reports_service.list_reports(
            tenant_id="tenant-123",
            page=1,
            page_size=20,
        )
        assert isinstance(result, ReportListResponse)
        assert result.total == 0
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, reports_service, mock_session):
        """Test getting a non-existent report."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await reports_service.get_report("nonexistent", "tenant-123")
        assert result is None


class TestSchedulesService:
    """Tests for SchedulesService business logic."""

    @pytest.mark.asyncio
    async def test_create_schedule(self, schedules_service, mock_session):
        """Test creating a schedule."""
        schedule_data = ScheduleCreate(
            name="Weekly Report",
            report_type="ingresos",
            schedule_cron="0 8 * * 1",
            format="pdf",
        )
        result = await schedules_service.create_schedule(
            tenant_id="tenant-123",
            user_id="user-456",
            schedule_data=schedule_data,
        )
        assert result is not None
        assert result.name == "Weekly Report"

    @pytest.mark.asyncio
    async def test_list_schedules(self, schedules_service, mock_session):
        """Test listing schedules."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await schedules_service.list_schedules(
            tenant_id="tenant-123",
            is_active=True,
        )
        assert isinstance(result, ScheduleListResponse)
        assert result.total == 0


class TestBIConnectorsService:
    """Tests for BIConnectorsService business logic."""

    @pytest.mark.asyncio
    async def test_create_connector(self, bi_connectors_service, mock_session):
        """Test creating a BI connector."""
        connector_data = BIConnectorCreate(
            name="Power BI",
            connector_type="powerbi",
            config={"api_key": "secret"},
        )
        result = await bi_connectors_service.create_connector(
            tenant_id="tenant-123",
            connector_data=connector_data,
        )
        assert result is not None
        assert result.name == "Power BI"
        assert result.connector_type == "powerbi"

    @pytest.mark.asyncio
    async def test_list_connectors(self, bi_connectors_service, mock_session):
        """Test listing BI connectors."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await bi_connectors_service.list_connectors(
            tenant_id="tenant-123",
            status=None,
        )
        assert isinstance(result, BIConnectorListResponse)
        assert result.total == 0


class TestExportService:
    """Tests for ExportService."""

    @pytest.mark.asyncio
    async def test_create_export_job(self, export_service):
        """Test creating an export job."""
        job = await export_service.create_export_job(
            tenant_id="tenant-123",
            user_id="user-456",
            report_type="ingresos",
            sede_id="sede-789",
            fecha_inicio="2024-01-01",
            fecha_fin="2024-01-31",
            formato="csv",
        )
        assert job is not None
        assert job.job_id is not None
        assert job.status == "pending"

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, export_service):
        """Test getting status of non-existent job."""
        result = await export_service.get_job_status("nonexistent-job")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_job_status_success(self, export_service):
        """Test getting status of existing job."""
        job = await export_service.create_export_job(
            tenant_id="tenant-123",
            user_id="user-456",
            report_type="ingresos",
            sede_id="sede-789",
            fecha_inicio="2024-01-01",
            fecha_fin="2024-01-31",
            formato="csv",
        )
        result = await export_service.get_job_status(job.job_id)
        assert result is not None
        assert result.job_id == job.job_id
        assert result.status == "pending"


class TestSecurityModule:
    """Tests for security utilities."""

    def test_validate_gateway_headers_success(self):
        """Test validate_gateway_headers with valid inputs."""
        from app.core.security import validate_gateway_headers

        result = validate_gateway_headers(
            user_id="user-123",
            rol="admin",
            tenant_id="tenant-456",
        )
        assert result == {
            "user_id": "user-123",
            "rol": "admin",
            "tenant_id": "tenant-456",
        }

    def test_validate_gateway_headers_missing_user_id(self):
        """Test validate_gateway_headers raises when user_id missing."""
        from app.core.security import validate_gateway_headers
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            validate_gateway_headers(None, "admin", "tenant-456")
        assert exc_info.value.status_code == 401
        assert "Missing X-User-Id header" in exc_info.value.detail

    def test_validate_gateway_headers_missing_rol(self):
        """Test validate_gateway_headers raises when rol missing."""
        from app.core.security import validate_gateway_headers
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            validate_gateway_headers("user-123", None, "tenant-456")
        assert exc_info.value.status_code == 401
        assert "Missing X-Rol header" in exc_info.value.detail

    def test_validate_gateway_headers_missing_tenant_id(self):
        """Test validate_gateway_headers raises when tenant_id missing."""
        from app.core.security import validate_gateway_headers
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            validate_gateway_headers("user-123", "admin", None)
        assert exc_info.value.status_code == 401
        assert "Missing X-Tenant-Id header" in exc_info.value.detail

    def test_check_permission_admin(self):
        """Test check_permission for admin role."""
        from app.core.security import check_permission

        assert check_permission("admin", "admin") is True
        assert check_permission("admin", "operador") is True
        assert check_permission("admin", "cliente") is True

    def test_check_permission_operador(self):
        """Test check_permission for operador role."""
        from app.core.security import check_permission

        assert check_permission("operador", "operador") is True
        assert check_permission("operador", "cliente") is True
        assert check_permission("operador", "admin") is False

    def test_check_permission_cliente(self):
        """Test check_permission for cliente role."""
        from app.core.security import check_permission

        assert check_permission("cliente", "cliente") is True
        assert check_permission("cliente", "operador") is False
        assert check_permission("cliente", "admin") is False

    def test_check_permission_unknown_role(self):
        """Test check_permission for unknown role."""
        from app.core.security import check_permission

        assert check_permission("unknown", "cliente") is False
        assert check_permission(None, "cliente") is False