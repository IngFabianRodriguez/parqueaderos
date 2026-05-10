"""Dataclasses/POPOs for reports-service (no pydantic v2)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ReportCreate:
    """Input schema for creating a report."""
    name: str
    report_type: str  # 'ingresos', 'ocupacion', 'tiempo_promedio'
    format: str = "pdf"  # 'pdf', 'csv', 'xlsx'
    parameters: Optional[dict] = None


@dataclass
class ReportResponse:
    """Output schema for a report."""
    id: str
    tenant_id: str
    name: str
    report_type: str
    format: str
    status: str  # 'pending', 'generating', 'ready', 'failed'
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    parameters: Optional[dict] = None
    generated_by: str
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "report_type": self.report_type,
            "format": self.format,
            "status": self.status,
            "file_url": self.file_url,
            "file_size_bytes": self.file_size_bytes,
            "parameters": self.parameters,
            "generated_by": self.generated_by,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class ReportListResponse:
    """Paginated list of reports."""
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int

    def to_dict(self) -> dict:
        return {
            "items": [r.to_dict() for r in self.items],
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
        }


@dataclass
class ScheduleCreate:
    """Input schema for creating a report schedule."""
    name: str
    report_type: str
    schedule_cron: str
    format: str = "pdf"
    parameters: Optional[dict] = None
    recipients: Optional[list[str]] = None
    is_active: bool = True


@dataclass
class ScheduleResponse:
    """Output schema for a schedule."""
    id: str
    tenant_id: str
    name: str
    report_type: str
    schedule_cron: str
    format: str
    parameters: Optional[dict] = None
    recipients: Optional[list[str]] = None
    is_active: bool
    created_by: str
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "report_type": self.report_type,
            "schedule_cron": self.schedule_cron,
            "format": self.format,
            "parameters": self.parameters,
            "recipients": self.recipients,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class ScheduleListResponse:
    """List of schedules."""
    items: list[ScheduleResponse]
    total: int

    def to_dict(self) -> dict:
        return {
            "items": [s.to_dict() for s in self.items],
            "total": self.total,
        }


@dataclass
class BIConnectorCreate:
    """Input schema for creating a BI connector."""
    name: str
    connector_type: str  # 'tableau', 'powerbi', 'looker'
    config: dict


@dataclass
class BIConnectorResponse:
    """Output schema for a BI connector."""
    id: str
    tenant_id: str
    name: str
    connector_type: str
    status: str  # 'connected', 'disconnected', 'error'
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "connector_type": self.connector_type,
            "status": self.status,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class BIConnectorListResponse:
    """List of BI connectors."""
    items: list[BIConnectorResponse]
    total: int

    def to_dict(self) -> dict:
        return {
            "items": [b.to_dict() for b in self.items],
            "total": self.total,
        }


@dataclass
class ReportFilter:
    """Filter criteria for listing reports."""
    tenant_id: str
    report_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class ScheduleFilter:
    """Filter criteria for listing schedules."""
    tenant_id: str
    is_active: Optional[bool] = None


@dataclass
class BIConnectorFilter:
    """Filter criteria for listing BI connectors."""
    tenant_id: str
    status: Optional[str] = None


@dataclass
class ExportJobResponse:
    """Response for async export job."""
    job_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }