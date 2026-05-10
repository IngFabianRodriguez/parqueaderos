"""Repository layer for monitoring-service."""
from __future__ import annotations

# Import from consolidated monitoring.py
from app.repositories.monitoring import (
    ServiceRegistryRepository,
    HealthCheckRecordRepository,
    LatencyRecordRepository,
    AlertRepository,
    AlertRuleRepository,
    NotificationChannelRepository,
    MaintenanceWindowRepository,
    MetricRecordRepository,
    SLAReportRepository,
)

__all__ = [
    "ServiceRegistryRepository",
    "HealthCheckRecordRepository",
    "LatencyRecordRepository",
    "AlertRepository",
    "AlertRuleRepository",
    "NotificationChannelRepository",
    "MaintenanceWindowRepository",
    "MetricRecordRepository",
    "SLAReportRepository",
]