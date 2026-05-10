"""SQLAlchemy models for monitoring-service — RF-100 to RF-115."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, JSON, Integer, Boolean,
    ForeignKey, Text, Index, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# ─────────────────────────────────────────────────────────────────────────────
# Base mixin with tenant_id for multi-tenancy
# ─────────────────────────────────────────────────────────────────────────────

class TenantMixin:
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True, primary_key=False)


class TimestampsMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Service Registry (RF-100, RF-101)
# ─────────────────────────────────────────────────────────────────────────────

class ServiceRegistry(Base, TenantMixin, TimestampsMixin):
    """Registry of microservices that report health."""
    __tablename__ = "service_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), nullable=False, unique=True)
    service_name = Column(String(255), nullable=False)
    health_url = Column(String(500), nullable=False)  # URL of /health endpoint
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSON, default=dict)

    health_records = relationship("ServiceHealthRecord", back_populates="service", lazy="noload")

    __table_args__ = (
        Index("ix_service_registry_tenant_active", "tenant_id", "is_active"),
    )


class ServiceHealthRecord(Base, TenantMixin, TimestampsMixin):
    """Time-series of service health checks."""
    __tablename__ = "service_health_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("service_registry.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(20), nullable=False)  # UP, DEGRADED, DOWN, UNKNOWN
    latency_ms = Column(Integer, nullable=True)
    response_code = Column(Integer, nullable=True)
    error_message = Column(String(500), nullable=True)
    version = Column(String(50), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    last_check = Column(DateTime(timezone=True), nullable=False)
    checked_at = Column(DateTime(timezone=True), nullable=False)

    service = relationship("ServiceRegistry", back_populates="health_records")

    __table_args__ = (
        Index("ix_service_health_tenant_service", "tenant_id", "service_id"),
        Index("ix_service_health_last_check", "last_check"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Alert Rules (RF-106)
# ─────────────────────────────────────────────────────────────────────────────

class AlertRule(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # CRITICAL, WARNING, INFO
    # condition stored as JSON: {"metric": "cpu", "operator": "gt", "threshold": 80, "window_seconds": 300}
    condition = Column(JSON, nullable=False)
    cooldown_seconds = Column(Integer, default=300)
    enabled = Column(Boolean, default=True)
    service_id = Column(String(100), nullable=True)  # None = all services

    alerts = relationship("Alert", back_populates="rule", lazy="noload")

    __table_args__ = (
        Index("ix_alert_rules_tenant_enabled", "tenant_id", "enabled"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Alerts (RF-102, RF-109)
# ─────────────────────────────────────────────────────────────────────────────

class Alert(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True)
    service_id = Column(String(100), nullable=False)
    service_name = Column(String(255), nullable=True)
    type_ = Column("type", String(50), nullable=False)  # SERVICE_DOWN, LATENCY_ANOMALY, etc.
    severity = Column(String(20), nullable=False)
    status = Column(String(20), default="FIRING")  # FIRING, ACKNOWLEDGED, RESOLVED, SILENCED
    message = Column(String(500), nullable=False)
    payload = Column(JSON, default=dict)  # down_since, retry_count, etc.
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    silenced_until = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    rule = relationship("AlertRule", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_tenant_status", "tenant_id", "status"),
        Index("ix_alerts_tenant_severity", "tenant_id", "severity"),
        Index("ix_alerts_created_at", "created_at"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Maintenance Windows (RF-108)
# ─────────────────────────────────────────────────────────────────────────────

class MaintenanceWindow(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "maintenance_windows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    # "all" or list of service IDs
    services_affected = Column(JSON, default=lambda: ["all"])
    severities_affected = Column(JSON, default=lambda: ["CRITICAL", "WARNING", "INFO"])
    notify_on_end = Column(Boolean, default=True)
    estado = Column(String(20), default="scheduled")  # scheduled, active, ended, cancelled

    __table_args__ = (
        Index("ix_maintenance_tenant_active", "tenant_id", "estado"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Notification Channels (RF-107)
# ─────────────────────────────────────────────────────────────────────────────

class NotificationChannel(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "notification_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    channel_type = Column(String(30), nullable=False)  # email, slack, pagerduty, webhook, sms
    configuration = Column(JSON, nullable=False)  # channel-specific config
    enabled = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_notification_channels_tenant_enabled", "tenant_id", "enabled"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# On-Call Schedules (RF-110)
# ─────────────────────────────────────────────────────────────────────────────

class OnCallSchedule(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "on_call_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_name = Column(String(255), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    rotation_type = Column(String(20), default="weekly")  # daily, weekly, custom
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_oncall_tenant_active", "tenant_id", "is_active"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Latency History for baseline (RF-102)
# ─────────────────────────────────────────────────────────────────────────────

class LatencyHistory(Base, TenantMixin):
    __tablename__ = "latency_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), nullable=False, index=True)
    latency_ms = Column(Integer, nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metric_name = Column(String(100), nullable=True, default="http_request_latency")
    metric_type = Column(String(30), nullable=True, default="latency")
    unit = Column(String(20), nullable=True, default="ms")
    labels_ = Column("labels", JSON, default=dict)

    __table_args__ = (
        Index("ix_latency_history_service_recorded", "service_id", "recorded_at"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# SLA Reports (RF-113)
# ─────────────────────────────────────────────────────────────────────────────

class SLAReport(Base, TenantMixin, TimestampsMixin):
    __tablename__ = "sla_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    uptime_percentage = Column(Integer, nullable=False)
    total_incidents = Column(Integer, default=0)
    mttr_minutes = Column(Integer, nullable=True)
    slo_compliant = Column(Boolean, default=False)
    slo_threshold_percent = Column(Integer, default=999)  # e.g. 999 = 99.9%
    downtime_minutes = Column(Integer, default=0)
    incident_details = Column(JSON, default=list)

    __table_args__ = (
        Index("ix_sla_reports_tenant_service", "tenant_id", "service_id"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Metric Samples (RF-103, RF-104)
# ─────────────────────────────────────────────────────────────────────────────

class MetricSample(Base, TenantMixin):
    __tablename__ = "metric_samples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(30), nullable=False)  # cpu, memory, disk, network, latency, throughput
    value = Column(Integer, nullable=False)
    unit = Column(String(20), nullable=True)
    labels = Column(JSON, default=dict)
    recorded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_metric_samples_service_type_recorded", "service_id", "metric_type", "recorded_at"),
        # Range partition by recorded_at would be ideal in production
    )