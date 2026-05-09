"""Pydantic schemas for reports-service."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


# Report schemas
class ReportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(..., min_length=1, max_length=50)
    format: str = Field(default="pdf", max_length=20)
    parameters: Optional[dict] = None


class ReportResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    report_type: str
    format: str
    status: str
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    parameters: Optional[dict] = None
    generated_by: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int


# Schedule schemas
class ScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(..., min_length=1, max_length=50)
    schedule_cron: str = Field(..., min_length=1, max_length=100)
    format: str = Field(default="pdf", max_length=20)
    parameters: Optional[dict] = None
    recipients: Optional[list[str]] = None
    is_active: bool = True


class ScheduleResponse(BaseModel):
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleListResponse(BaseModel):
    items: list[ScheduleResponse]
    total: int


# BI Connector schemas
class BIConnectorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    connector_type: str = Field(..., min_length=1, max_length=50)
    config: dict


class BIConnectorResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    connector_type: str
    status: str
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BIConnectorListResponse(BaseModel):
    items: list[BIConnectorResponse]
    total: int