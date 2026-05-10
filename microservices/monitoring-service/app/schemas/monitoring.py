"""Pydantic schemas for monitoring-service — RF-100 to RF-115."""
from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime, timedelta
from typing import Optional, Any
from uuid import UUID, uuid4
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class ServiceStatus(str, Enum):
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertType(str, Enum):
    SERVICE_DOWN = "SERVICE_DOWN"
    SERVICE_DEGRADED = "SERVICE_DEGRADED"
    LATENCY_ANOMALY = "LATENCY_ANOMALY"
    ERROR_RATE_HIGH = "ERROR_RATE_HIGH"
    DISK_SPACE_LOW = "DISK_SPACE_LOW"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"
    CPU_SATURATED = "CPU_SATURATED"
    SERVICE_RECOVERY = "SERVICE_RECOVERY"
    LATENCY_RECOVERED = "LATENCY_RECOVERED"


class AlertStatus(str, Enum):
    FIRING = "FIRING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    SILENCED = "SILENCED"


class NotificationChannelType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"


class MetricType(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


# ─────────────────────────────────────────────────────────────────────────────
# Service Health (RF-100, RF-101)
# ─────────────────────────────────────────────────────────────────────────────

class DependencyStatus(BaseModel):
    name: str
    status: ServiceStatus
    latency_ms: Optional[int] = None
    message: Optional[str] = None


class MemoryStatus(BaseModel):
    rss_mb: int
    heap_used_mb: int
    gc_triggered: bool = False


class ServiceHealthDetail(BaseModel):
    service: str
    version: str
    timestamp: datetime
    status: ServiceStatus
    dependencies: list[DependencyStatus]
    memory: Optional[MemoryStatus] = None

    class Config:
        from_attributes = True


class ServiceHealthRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    service_id: str
    service_name: str
    status: ServiceStatus
    latency_ms: Optional[int] = None
    version: Optional[str] = None
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    last_check: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        from_attributes = True


class ServiceHealthCreate(BaseModel):
    service_id: str
    service_name: str
    status: ServiceStatus
    latency_ms: Optional[int] = None
    version: Optional[str] = None
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class ServiceHealthUpdate(BaseModel):
    status: Optional[ServiceStatus] = None
    latency_ms: Optional[int] = None
    metadata_: Optional[dict[str, Any]] = Field(default=None, alias="metadata_")


# ─────────────────────────────────────────────────────────────────────────────
# Alert Rules (RF-106)
# ─────────────────────────────────────────────────────────────────────────────

class AlertRuleCondition(BaseModel):
    metric: str
    operator: str = Field(..., pattern=r"^(gt|gte|lt|lte|eq|neq)$")
    threshold: float
    window_seconds: int = Field(default=300, ge=1, le=3600)


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    severity: AlertSeverity
    condition: AlertRuleCondition
    cooldown_seconds: int = Field(default=300, ge=0, le=86400)
    enabled: bool = True
    service_id: Optional[str] = None  # None = all services


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    severity: Optional[AlertSeverity] = None
    condition: Optional[AlertRuleCondition] = None
    cooldown_seconds: Optional[int] = Field(None, ge=0, le=86400)
    enabled: Optional[bool] = None
    service_id: Optional[str] = None


class AlertRuleResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    severity: AlertSeverity
    condition: AlertRuleCondition
    cooldown_seconds: int
    enabled: bool
    service_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Alerts (RF-102, RF-109)
# ─────────────────────────────────────────────────────────────────────────────

class AlertCreate(BaseModel):
    rule_id: Optional[UUID] = None
    service_id: str
    service_name: Optional[str] = None
    type_: AlertType = Field(..., alias="type")
    severity: AlertSeverity
    message: str
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata_")


class AlertPayload(BaseModel):
    down_since: Optional[datetime] = None
    last_latency_ms: Optional[int] = None
    retry_count: Optional[int] = None
    current_latency_ms: Optional[int] = None
    baseline_p95_ms: Optional[int] = None
    threshold_ms: Optional[int] = None
    affected_endpoints: Optional[list[str]] = None


class AlertResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    rule_id: Optional[UUID] = None
    service_id: str
    service_name: Optional[str] = None
    type_: AlertType = Field(..., alias="type")
    severity: AlertSeverity
    status: AlertStatus
    message: str
    payload: Optional[AlertPayload] = None
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[UUID] = None
    silenced_until: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class AlertListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    alerts: list[AlertResponse]


class AlertAcknowledgeRequest(BaseModel):
    note: Optional[str] = None


class AlertSilenceRequest(BaseModel):
    until: datetime
    reason: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Maintenance Windows (RF-108)
# ─────────────────────────────────────────────────────────────────────────────

class MaintenanceWindowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    services_affected: list[str] = Field(default_factory=lambda: ["all"])
    severities_affected: list[AlertSeverity] = Field(
        default_factory=lambda: [AlertSeverity.CRITICAL, AlertSeverity.WARNING, AlertSeverity.INFO]
    )
    notify_on_end: bool = True


class MaintenanceWindowUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notify_on_end: Optional[bool] = None


class MaintenanceWindowResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    start_time: datetime
    end_time: datetime
    services_affected: list[str]
    severities_affected: list[AlertSeverity]
    notify_on_end: bool
    estado: str  # scheduled, active, ended, cancelled
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Notification Channels (RF-107)
# ─────────────────────────────────────────────────────────────────────────────

class EmailConfig(BaseModel):
    addresses: list[str]  # Comma-separated email addresses
    smtp_host: str | None = None
    smtp_port: int | None = None


class SlackConfig(BaseModel):
    webhook_url: HttpUrl
    channel: Optional[str] = None


class PagerDutyConfig(BaseModel):
    integration_key: str
    service_name: Optional[str] = None


class WebhookConfig(BaseModel):
    url: HttpUrl
    headers: dict[str, str] = Field(default_factory=dict)
    auth_type: Optional[str] = None  # none, basic, bearer


class SMSConfig(BaseModel):
    provider: str  # twilio, nexmo, etc.
    phone_numbers: list[str]


NotificationChannelConfig = EmailConfig | SlackConfig | PagerDutyConfig | WebhookConfig | SMSConfig


class NotificationChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: NotificationChannelType
    configuration: NotificationChannelConfig
    enabled: bool = True


class NotificationChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    configuration: Optional[NotificationChannelConfig] = None
    enabled: Optional[bool] = None


class NotificationChannelResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    channel_type: NotificationChannelType
    configuration: dict[str, Any]  # sanitized — no secrets
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Metrics (RF-103, RF-104, RF-105)
# ─────────────────────────────────────────────────────────────────────────────

class MetricSample(BaseModel):
    name: str
    value: float
    unit: str
    labels: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InfrastructureMetricsResponse(BaseModel):
    service_id: str
    timestamp: datetime
    cpu: dict[str, float]
    memory: dict[str, float]
    disk: dict[str, float]
    network: dict[str, float]


class ApplicationMetricsResponse(BaseModel):
    service_id: str
    timestamp: datetime
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rpm: float
    error_rate_percent: float


class MetricsQuery(BaseModel):
    service_id: Optional[str] = None
    metric_type: Optional[MetricType] = None
    from_: datetime = Field(..., alias="from")
    to: datetime
    resolution: Optional[str] = None  # 15s, 1m, 5m
    labels: dict[str, str] = Field(default_factory=dict)


class MetricsExportResponse(BaseModel):
    format_: str = Field(..., alias="format")  # csv, json
    metrics: list[MetricSample]
    generated_at: datetime


class TopSlowEndpoint(BaseModel):
    service_id: str
    endpoint: str
    method: str
    avg_latency_ms: float
    p99_latency_ms: float
    calls_per_minute: float


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard (RF-101)
# ─────────────────────────────────────────────────────────────────────────────

class DashboardServiceEntry(BaseModel):
    service_id: str
    service_name: str
    status: ServiceStatus
    last_check: datetime
    latency_ms: Optional[int] = None
    uptime_percent_30d: float
    down_since: Optional[datetime] = None
    dependencies_summary: list[dict[str, str]]


class DashboardResponse(BaseModel):
    generated_at: datetime
    refresh_interval_seconds: int = 30
    services: list[DashboardServiceEntry]


# ─────────────────────────────────────────────────────────────────────────────
# SLA (RF-111, RF-113)
# ─────────────────────────────────────────────────────────────────────────────

class SLAReportRequest(BaseModel):
    service_id: str
    start_date: datetime
    end_date: datetime
    slo_threshold_percent: float = 99.9


class SLAReportResponse(BaseModel):
    service_id: str
    uptime_percentage: float
    total_incidents: int
    mttr_minutes: float
    slo_compliant: bool
    slo_threshold_percent: float
    downtime_minutes: float
    incident_details: list[dict[str, Any]] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# On-Call (RF-110)
# ─────────────────────────────────────────────────────────────────────────────

class OnCallScheduleCreate(BaseModel):
    user_id: UUID
    start_time: datetime
    end_time: datetime
    rotation_type: str = "weekly"  # daily, weekly, custom


class OnCallScheduleResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    rotation_type: str
    is_current: bool = False

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Business Metrics (RF-114)
# ─────────────────────────────────────────────────────────────────────────────

class BusinessMetricsResponse(BaseModel):
    tenant_id: UUID
    timestamp: datetime
    total_transactions: int
    total_revenue_cop: float
    active_sedes: int
    active_users: int
    alerts_fired: int
    alerts_resolved: int


# ─────────────────────────────────────────────────────────────────────────────
# Distributed Tracing (RF-115)
# ─────────────────────────────────────────────────────────────────────────────

class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    tags: dict[str, str] = Field(default_factory=dict)
    status_code: Optional[int] = None


class TraceSearchRequest(BaseModel):
    trace_id: Optional[str] = None
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    from_: datetime = Field(..., alias="from")
    to: datetime
    limit: int = Field(default=100, le=1000)


class TraceSearchResponse(BaseModel):
    traces: list[TraceSpan]
    total: int