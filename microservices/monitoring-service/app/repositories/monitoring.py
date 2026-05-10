"""Repository layer for monitoring-service — all data access objects."""
from __future__ import annotations

from datetime import datetime, timedelta
import uuid
from uuid import UUID
from typing import Optional

from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ServiceRegistry,
    ServiceHealthRecord as HealthCheckRecord,
    Alert,
    AlertRule,
    NotificationChannel,
    MaintenanceWindow,
    LatencyHistory as MetricRecord,
    SLAReport,
)


# ─────────────────────────────────────────────────────────────────────────────
# ServiceRegistryRepository
# ─────────────────────────────────────────────────────────────────────────────

class ServiceRegistryRepository:
    """Data access for service_registry table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_service_id(
        self, tenant_id: UUID, service_id: str
    ) -> Optional[ServiceRegistry]:
        stmt = select(ServiceRegistry).where(
            and_(
                ServiceRegistry.tenant_id == tenant_id,
                ServiceRegistry.service_id == service_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self, tenant_id: UUID) -> list[ServiceRegistry]:
        stmt = select(ServiceRegistry).where(
            and_(
                ServiceRegistry.tenant_id == tenant_id,
                ServiceRegistry.is_active == True,
            )
        ).order_by(ServiceRegistry.service_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, tenant_id: UUID, service_id: str, name: str, **kwargs) -> ServiceRegistry:
        record = ServiceRegistry(
            id=UUID.__new__(UUID),
            tenant_id=tenant_id,
            service_id=service_id,
            service_name=name,
            **{k: v for k, v in kwargs.items() if k in ("health_url", "internal_url", "is_active", "metadata_")},
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update_health(
        self,
        registry: ServiceRegistry,
        status: str,
        latency_ms: Optional[int] = None,
        error_msg: Optional[str] = None,
    ) -> tuple[ServiceRegistry, Optional[HealthCheckRecord]]:
        registry.last_health_status = status
        registry.last_health_at = datetime.utcnow()
        registry.last_latency_ms = latency_ms

        record = HealthCheckRecord(
            id=UUID.__new__(UUID),
            tenant_id=registry.tenant_id,
            service_id=registry.service_id,
            status=status,
            latency_ms=latency_ms,
            error_message=error_msg,
            checked_at=datetime.utcnow(),
        )
        self.session.add(record)
        await self.session.flush()
        return registry, record


# ─────────────────────────────────────────────────────────────────────────────
# HealthCheckRecordRepository
# ─────────────────────────────────────────────────────────────────────────────

class HealthCheckRecordRepository:
    """Data access for health_check_record table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        tenant_id: UUID,
        service_id: str,
        status: str,
        latency_ms: Optional[int] = None,
        response_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> HealthCheckRecord:
        record = HealthCheckRecord(
            id=UUID.__new__(UUID),
            tenant_id=tenant_id,
            service_id=service_id,
            status=status,
            latency_ms=latency_ms,
            response_code=response_code,
            error_message=error_message,
            checked_at=datetime.utcnow(),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_recent(
        self, tenant_id: UUID, service_id: str, limit: int = 100
    ) -> list[HealthCheckRecord]:
        stmt = (
            select(HealthCheckRecord)
            .where(
                and_(
                    HealthCheckRecord.tenant_id == tenant_id,
                    HealthCheckRecord.service_id == service_id,
                )
            )
            .order_by(desc(HealthCheckRecord.checked_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# LatencyRecordRepository
# ─────────────────────────────────────────────────────────────────────────────

class LatencyRecordRepository:
    """Data access for metric_record table (latency metrics)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        tenant_id: UUID,
        service_id: str,
        metric_name: str,
        value: float,
        unit: str = "ms",
        labels: Optional[dict] = None,
    ) -> MetricRecord:
        record = MetricRecord(
            id=UUID.__new__(UUID),
            tenant_id=tenant_id,
            service_id=service_id,
            metric_type="latency",
            metric_name=metric_name,
            value=value,
            unit=unit,
            labels_=labels or {},
            recorded_at=datetime.utcnow(),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def query(
        self, tenant_id: UUID, service_id: str, from_: datetime, to: datetime
    ) -> list[MetricRecord]:
        stmt = (
            select(MetricRecord)
            .where(
                and_(
                    MetricRecord.tenant_id == tenant_id,
                    MetricRecord.service_id == service_id,
                    MetricRecord.recorded_at >= from_,
                    MetricRecord.recorded_at <= to,
                )
            )
            .order_by(MetricRecord.recorded_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# AlertRepository
# ─────────────────────────────────────────────────────────────────────────────

class AlertRepository:
    """Data access for alert table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.flush()
        return alert

    async def get_by_id(self, tenant_id: UUID, alert_id: UUID) -> Optional[Alert]:
        stmt = select(Alert).where(
            and_(Alert.tenant_id == tenant_id, Alert.id == alert_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        service_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Alert], int]:
        conditions = [Alert.tenant_id == tenant_id]
        if status:
            conditions.append(Alert.status == status)
        if severity:
            conditions.append(Alert.severity == severity)
        if service_id:
            conditions.append(Alert.service_id == service_id)

        count_stmt = select(func.count(Alert.id)).where(*conditions)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()

        offset = (page - 1) * page_size
        stmt = (
            select(Alert)
            .where(*conditions)
            .order_by(desc(Alert.created_at))
            .limit(page_size)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def acknowledge(self, alert: Alert, user_id: UUID) -> Alert:
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        await self.session.flush()
        return alert

    async def silence(self, alert: Alert, until: datetime) -> Alert:
        alert.status = "SILENCED"
        alert.silenced_until = until
        await self.session.flush()
        return alert

    async def resolve(self, alert: Alert) -> Alert:
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.utcnow()
        await self.session.flush()
        return alert

    async def has_recent_firing(
        self, tenant_id: UUID, service_id: str, alert_type: str, cooldown_seconds: int = 300
    ) -> bool:
        since = datetime.utcnow() - timedelta(seconds=cooldown_seconds)
        stmt = select(func.count(Alert.id)).where(
            and_(
                Alert.tenant_id == tenant_id,
                Alert.service_id == service_id,
                Alert.type_ == alert_type,
                Alert.status == "FIRING",
                Alert.created_at >= since,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() > 0


# ─────────────────────────────────────────────────────────────────────────────
# AlertRuleRepository
# ─────────────────────────────────────────────────────────────────────────────

class AlertRuleRepository:
    """Data access for alert_rule table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rule: AlertRule) -> AlertRule:
        self.session.add(rule)
        await self.session.flush()
        return rule

    async def get_by_id(self, tenant_id: UUID, rule_id: UUID) -> Optional[AlertRule]:
        stmt = select(AlertRule).where(
            and_(AlertRule.tenant_id == tenant_id, AlertRule.id == rule_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, tenant_id: UUID, enabled_only: bool = False) -> list[AlertRule]:
        conditions = [AlertRule.tenant_id == tenant_id]
        if enabled_only:
            conditions.append(AlertRule.enabled == True)
        stmt = select(AlertRule).where(*conditions).order_by(AlertRule.created_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, rule: AlertRule) -> AlertRule:
        await self.session.flush()
        return rule

    async def delete(self, tenant_id: UUID, rule_id: UUID) -> bool:
        stmt = delete(AlertRule).where(
            and_(AlertRule.tenant_id == tenant_id, AlertRule.id == rule_id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0


# ─────────────────────────────────────────────────────────────────────────────
# NotificationChannelRepository
# ─────────────────────────────────────────────────────────────────────────────

class NotificationChannelRepository:
    """Data access for notification_channel table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, channel: NotificationChannel) -> NotificationChannel:
        self.session.add(channel)
        await self.session.flush()
        return channel

    async def get_by_id(self, tenant_id: UUID, channel_id: UUID) -> Optional[NotificationChannel]:
        stmt = select(NotificationChannel).where(
            and_(NotificationChannel.tenant_id == tenant_id, NotificationChannel.id == channel_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_enabled(self, tenant_id: UUID) -> list[NotificationChannel]:
        stmt = select(NotificationChannel).where(
            and_(NotificationChannel.tenant_id == tenant_id, NotificationChannel.enabled == True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# MaintenanceWindowRepository
# ─────────────────────────────────────────────────────────────────────────────

class MaintenanceWindowRepository:
    """Data access for maintenance_window table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, window: MaintenanceWindow) -> MaintenanceWindow:
        self.session.add(window)
        await self.session.flush()
        return window

    async def get_by_id(self, tenant_id: UUID, window_id: UUID) -> Optional[MaintenanceWindow]:
        stmt = select(MaintenanceWindow).where(
            and_(MaintenanceWindow.tenant_id == tenant_id, MaintenanceWindow.id == window_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, tenant_id: UUID) -> list[MaintenanceWindow]:
        stmt = (
            select(MaintenanceWindow)
            .where(MaintenanceWindow.tenant_id == tenant_id)
            .order_by(MaintenanceWindow.start_time)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(self, tenant_id: UUID) -> list[MaintenanceWindow]:
        now = datetime.utcnow()
        stmt = select(MaintenanceWindow).where(
            and_(
                MaintenanceWindow.tenant_id == tenant_id,
                MaintenanceWindow.estado == "active",
                MaintenanceWindow.start_time <= now,
                MaintenanceWindow.end_time >= now,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, window: MaintenanceWindow) -> MaintenanceWindow:
        await self.session.flush()
        return window

    async def delete(self, tenant_id: UUID, window_id: UUID) -> bool:
        stmt = delete(MaintenanceWindow).where(
            and_(MaintenanceWindow.tenant_id == tenant_id, MaintenanceWindow.id == window_id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0


# ─────────────────────────────────────────────────────────────────────────────
# MetricRecordRepository
# ─────────────────────────────────────────────────────────────────────────────

class MetricRecordRepository:
    """Data access for metric_record table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: MetricRecord) -> MetricRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def query(
        self,
        tenant_id: UUID,
        service_id: Optional[str],
        metric_type: Optional[str],
        from_: datetime,
        to: datetime,
    ) -> list[MetricRecord]:
        conditions = [
            MetricRecord.tenant_id == tenant_id,
            MetricRecord.recorded_at >= from_,
            MetricRecord.recorded_at <= to,
        ]
        if service_id:
            conditions.append(MetricRecord.service_id == service_id)
        if metric_type:
            conditions.append(MetricRecord.metric_type == metric_type)

        stmt = (
            select(MetricRecord)
            .where(*conditions)
            .order_by(MetricRecord.recorded_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# SLAReportRepository
# ─────────────────────────────────────────────────────────────────────────────

class SLAReportRepository:
    """Data access for sla_report table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report: SLAReport) -> SLAReport:
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_latest(
        self, tenant_id: UUID, service_id: str, sla_type: str
    ) -> Optional[SLAReport]:
        stmt = (
            select(SLAReport)
            .where(
                and_(
                    SLAReport.tenant_id == tenant_id,
                    SLAReport.service_id == service_id,
                    SLAReport.sla_type == sla_type,
                )
            )
            .order_by(desc(SLAReport.generated_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(
        self, tenant_id: UUID, service_id: str, limit: int = 12
    ) -> list[SLAReport]:
        stmt = (
            select(SLAReport)
            .where(
                and_(
                    SLAReport.tenant_id == tenant_id,
                    SLAReport.service_id == service_id,
                )
            )
            .order_by(desc(SLAReport.generated_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())