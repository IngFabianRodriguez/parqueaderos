"""Pydantic schemas for monitoring-service."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ServiceHealthResponse(BaseModel):
    service_id: str
    status: str
    latency_ms: Optional[int] = None
    last_check: datetime


class AlertCreate(BaseModel):
    rule_id: Optional[UUID] = None
    service_id: str
    severity: str
    message: str
    metadata: dict = Field(default_factory=dict)


class AlertResponse(BaseModel):
    id: UUID
    service_id: str
    severity: str
    message: str
    acknowledged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]


class SLAReportRequest(BaseModel):
    service_id: str
    start_date: datetime
    end_date: datetime


class SLAReportResponse(BaseModel):
    service_id: str
    uptime_percentage: float
    total_incidents: int
    mttr_minutes: float
    slo_compliant: bool
