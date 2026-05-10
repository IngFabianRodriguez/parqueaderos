"""Business logic for SLA reporting — RF-111, RF-113."""
from __future__ import annotations

import structlog
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from app.db.session import AsyncSession
from app.repositories.monitoring import SLAReportRepository
from app.schemas.monitoring import (
    SLAReportRequest, SLAReportResponse,
    BusinessMetricsResponse,
)


logger = structlog.get_logger(__name__)


class SLAService:
    """Manages SLA reports and uptime calculation. RF-111, RF-113."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._repo = SLAReportRepository(session)

    async def generate_report(
        self, tenant_id: UUID, request: SLAReportRequest
    ) -> SLAReportResponse:
        """
        Generate SLA report for a service between start_date and end_date.
        Implements RF-113.
        """
        from app.db.models import ServiceHealthRecord, Alert
        from sqlalchemy import select, func, and_

        service_id = request.service_id

        # 1. Calculate uptime percentage
        records_result = await self._s.execute(
            select(ServiceHealthRecord).where(
                and_(
                    ServiceHealthRecord.tenant_id == tenant_id,
                    ServiceHealthRecord.service_id == service_id,
                    ServiceHealthRecord.last_check >= request.start_date,
                    ServiceHealthRecord.last_check <= request.end_date,
                )
            )
        )
        records = list(records_result.scalars().all())
        total_checks = len(records)
        up_checks = sum(1 for r in records if r.status == "UP")

        uptime_percentage = (up_checks / total_checks * 100) if total_checks > 0 else 100.0

        # 2. Count incidents (DOWN events)
        incidents_result = await self._s.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.tenant_id == tenant_id,
                    Alert.service_id == service_id,
                    Alert.type_ == "SERVICE_DOWN",
                    Alert.created_at >= request.start_date,
                    Alert.created_at <= request.end_date,
                )
            )
        )
        total_incidents = incidents_result.scalar() or 0

        # 3. Calculate MTTR (Mean Time To Recovery)
        incidents_result = await self._s.execute(
            select(Alert).where(
                and_(
                    Alert.tenant_id == tenant_id,
                    Alert.service_id == service_id,
                    Alert.type_ == "SERVICE_DOWN",
                    Alert.resolved_at.isnot(None),
                    Alert.created_at >= request.start_date,
                    Alert.created_at <= request.end_date,
                )
            )
        )
        resolved_incidents = list(incidents_result.scalars().all())
        if resolved_incidents:
            total_recovery_time = sum(
                (r.resolved_at - r.created_at).total_seconds() / 60
                for r in resolved_incidents
                if r.resolved_at
            )
            mttr_minutes = total_recovery_time / len(resolved_incidents)
        else:
            mttr_minutes = 0.0

        # 4. Downtime minutes
        downtime_minutes = ((100 - uptime_percentage) / 100) * (
            (request.end_date - request.start_date).total_seconds() / 60
        )

        # 5. SLO compliance
        slo_compliant = uptime_percentage >= request.slo_threshold_percent

        # 6. Incident details
        incident_details = [
            {
                "id": str(r.id),
                "started_at": r.created_at.isoformat(),
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
                "duration_minutes": (
                    (r.resolved_at - r.created_at).total_seconds() / 60
                    if r.resolved_at else None
                ),
            }
            for r in resolved_incidents
        ]

        # 7. Persist report
        report = await self._repo.create(
            tenant_id,
            service_id=service_id,
            start_date=request.start_date,
            end_date=request.end_date,
            uptime_percentage=int(uptime_percentage * 100) / 100,
            total_incidents=total_incidents,
            mttr_minutes=int(mttr_minutes),
            slo_compliant=slo_compliant,
            slo_threshold_percent=int(request.slo_threshold_percent),
            downtime_minutes=int(downtime_minutes),
            incident_details=incident_details,
        )

        return SLAReportResponse(
            service_id=service_id,
            uptime_percentage=round(uptime_percentage, 2),
            total_incidents=total_incidents,
            mttr_minutes=round(mttr_minutes, 2),
            slo_compliant=slo_compliant,
            slo_threshold_percent=request.slo_threshold_percent,
            downtime_minutes=round(downtime_minutes, 2),
            incident_details=incident_details,
        )

    async def get_current_uptime(
        self, tenant_id: UUID, service_id: str, days: int = 30
    ) -> float:
        """Calculate current uptime percentage for last N days."""
        from app.db.models import ServiceHealthRecord
        from sqlalchemy import select, func, and_

        cutoff = datetime.utcnow() - timedelta(days=days)
        total_result = await self._s.execute(
            select(func.count(ServiceHealthRecord.id)).where(
                and_(
                    ServiceHealthRecord.tenant_id == tenant_id,
                    ServiceHealthRecord.service_id == service_id,
                    ServiceHealthRecord.last_check >= cutoff,
                )
            )
        )
        total = total_result.scalar() or 0
        if total == 0:
            return 100.0

        up_result = await self._s.execute(
            select(func.count(ServiceHealthRecord.id)).where(
                and_(
                    ServiceHealthRecord.tenant_id == tenant_id,
                    ServiceHealthRecord.service_id == service_id,
                    ServiceHealthRecord.last_check >= cutoff,
                    ServiceHealthRecord.status == "UP",
                )
            )
        )
        up = up_result.scalar() or 0
        return round((up / total) * 100, 2)


class BusinessMetricsService:
    """Business-level metrics for tenants. RF-114."""

    async def get_metrics(self, tenant_id: UUID) -> BusinessMetricsResponse:
        """
        Aggregate business metrics for a tenant.
        RF-114: transactions, revenue, active sedes, active users, alerts stats.
        """
        from app.db.models import Alert
        from sqlalchemy import select, func, and_

        # Count active alerts
        firing_result = await self._s.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.tenant_id == tenant_id, Alert.status == "FIRING")
            )
        )
        alerts_firing = firing_result.scalar() or 0

        resolved_result = await self._s.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.tenant_id == tenant_id,
                    Alert.status == "RESOLVED",
                    Alert.updated_at >= datetime.utcnow() - timedelta(days=1),
                )
            )
        )
        alerts_resolved = resolved_result.scalar() or 0

        return BusinessMetricsResponse(
            tenant_id=tenant_id,
            timestamp=datetime.utcnow(),
            total_transactions=0,  # Would cross-query transactions service
            total_revenue_cop=0.0,
            active_sedes=0,  # Would cross-query sedes service
            active_users=0,   # Would cross-query auth service
            alerts_fired=alerts_firing,
            alerts_resolved=alerts_resolved,
        )