"""Business logic for service health checks — RF-100, RF-101, RF-102."""
from __future__ import annotations

import httpx
import structlog
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from app.db.session import AsyncSession
from app.repositories.monitoring import (
    ServiceRegistryRepository,
    AlertRepository,
    LatencyRecordRepository,
)
from app.schemas.monitoring import (
    DashboardResponse, DashboardServiceEntry,
    ServiceStatus, AlertType, AlertSeverity, AlertCreate,
)


logger = structlog.get_logger(__name__)

# Timeouts for health check calls
HEALTH_CHECK_TIMEOUT = 10.0  # seconds
RETRY_COUNT = 3
RETRY_BACKOFF = 2.0  # seconds


class HealthCheckService:
    """Aggregates health status from all registered services (RF-100, RF-101)."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._registry_repo = ServiceRegistryRepository(session)
        self._alert_repo = AlertRepository(session)
        self._latency_repo = LatencyRecordRepository(session)
        self._http = httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT)

    async def close(self):
        await self._http.aclose()

    async def check_service(self, tenant_id: UUID, service_id: str) -> dict:
        """
        Perform active health check against a registered service.
        Returns detailed status including DB/Redis/Kafka checks.
        RF-100.
        """
        svc = await self._registry_repo.get_by_service_id(tenant_id, service_id)
        if not svc:
            return {
                "service_id": service_id,
                "status": ServiceStatus.UNKNOWN,
                "latency_ms": None,
                "last_check": datetime.utcnow(),
                "error": "Service not registered",
            }

        # Attempt up to RETRY_COUNT retries
        last_error = None
        for attempt in range(RETRY_COUNT):
            try:
                start = datetime.utcnow()
                response = await self._http.get(svc.health_url)
                latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "service_id": service_id,
                        "service_name": svc.service_name,
                        "status": ServiceStatus(data.get("status", "UP")),
                        "latency_ms": latency_ms,
                        "version": data.get("version"),
                        "last_check": datetime.utcnow(),
                        "dependencies": data.get("dependencies", []),
                        "memory": data.get("memory"),
                    }
                elif response.status_code >= 500:
                    last_error = f"HTTP {response.status_code}"
                else:
                    # 4xx — service is up but returned error
                    return {
                        "service_id": service_id,
                        "service_name": svc.service_name,
                        "status": ServiceStatus.DEGRADED,
                        "latency_ms": latency_ms,
                        "last_check": datetime.utcnow(),
                        "error": f"HTTP {response.status_code}",
                    }
            except httpx.TimeoutException:
                last_error = "Timeout"
            except httpx.RequestError as exc:
                last_error = str(exc)

            if attempt < RETRY_COUNT - 1:
                await self._async_sleep(RETRY_BACKOFF * (attempt + 1))

        # All retries failed
        return {
            "service_id": service_id,
            "service_name": svc.service_name,
            "status": ServiceStatus.DOWN,
            "latency_ms": None,
            "last_check": datetime.utcnow(),
            "error": last_error,
        }

    async def check_all_services(self, tenant_id: UUID) -> list[dict]:
        """Check health of all active registered services."""
        services = await self._registry_repo.list_active(tenant_id)
        results = []
        for svc in services:
            result = await self.check_service(tenant_id, svc.service_id)
            results.append(result)

            # Update DB with latest status
            await self._registry_repo.update_health(
                tenant_id=tenant_id,
                service_id=svc.service_id,
                status=result.get("status", ServiceStatus.UNKNOWN).value,
                latency_ms=result.get("latency_ms"),
                version=result.get("version"),
                metadata_={"error": result.get("error")},
            )

            # Record latency for baseline calculation
            if result.get("latency_ms"):
                await self._latency_repo.record(
                    tenant_id, svc.service_id, result["latency_ms"]
                )

        return results

    async def build_dashboard(self, tenant_id: UUID) -> DashboardResponse:
        """Build the health dashboard response. RF-101."""
        services = await self.check_all_services(tenant_id)
        entries = []
        for svc in services:
            # Get uptime from recent history
            uptime_30d = await self._calculate_uptime(tenant_id, svc["service_id"], days=30)
            down_since = None
            if svc["status"] == ServiceStatus.DOWN:
                # Find when it went down
                down_since = await self._get_down_since(tenant_id, svc["service_id"])

            entries.append(
                DashboardServiceEntry(
                    service_id=svc["service_id"],
                    service_name=svc.get("service_name", svc["service_id"]),
                    status=svc["status"],
                    last_check=svc["last_check"],
                    latency_ms=svc.get("latency_ms"),
                    uptime_percent_30d=uptime_30d,
                    down_since=down_since,
                    dependencies_summary=[
                        {"name": d["name"], "status": d["status"]}
                        for d in svc.get("dependencies", [])
                    ],
                )
            )
        return DashboardResponse(
            generated_at=datetime.utcnow(),
            refresh_interval_seconds=30,
            services=entries,
        )

    async def detect_service_down(
        self, tenant_id: UUID, service_id: str, down_since: datetime
    ) -> Optional[Alert]:
        """
        When a service is confirmed DOWN, create a CRITICAL alert.
        Implements RF-102 detection flow.
        """
        # Check cooldown — don't spam alerts
        if await self._alert_repo.has_recent_firing(
            tenant_id, service_id, AlertType.SERVICE_DOWN.value, cooldown_seconds=60
        ):
            return None

        svc = await self._registry_repo.get_by_service_id(tenant_id, service_id)
        service_name = svc.service_name if svc else service_id

        alert_create = AlertCreate(
            service_id=service_id,
            service_name=service_name,
            type_=AlertType.SERVICE_DOWN,
            severity=AlertSeverity.CRITICAL,
            message=f"Service {service_name} is DOWN since {down_since.isoformat()}",
            metadata_={"down_since": down_since.isoformat(), "retry_count": RETRY_COUNT},
        )
        return await self._alert_repo.create(tenant_id, **alert_create.model_dump())

    async def detect_latency_anomaly(
        self, tenant_id: UUID, service_id: str, current_latency_ms: int
    ) -> Optional[Alert]:
        """
        Detect if current latency is > 2x baseline_p95.
        Implements RF-102 latency anomaly detection.
        """
        baseline = await self._latency_repo.get_baseline_p95(tenant_id, service_id)
        if baseline is None:
            return None  # Not enough history

        threshold = baseline * 2

        # Only alert if 2 consecutive readings above threshold
        # For now, single reading above threshold triggers warning
        if current_latency_ms <= threshold:
            return None

        if await self._alert_repo.has_recent_firing(
            tenant_id, service_id, AlertType.LATENCY_ANOMALY.value, cooldown_seconds=300
        ):
            return None

        svc = await self._registry_repo.get_by_service_id(tenant_id, service_id)
        service_name = svc.service_name if svc else service_id

        alert_create = AlertCreate(
            service_id=service_id,
            service_name=service_name,
            type_=AlertType.LATENCY_ANOMALY,
            severity=AlertSeverity.WARNING,
            message=f"Latency anomaly detected: {current_latency_ms}ms vs baseline {int(baseline)}ms",
            metadata_={
                "current_latency_ms": current_latency_ms,
                "baseline_p95_ms": int(baseline),
                "threshold_ms": int(threshold),
            },
        )
        return await self._alert_repo.create(tenant_id, **alert_create.model_dump())

    async def _calculate_uptime(
        self, tenant_id: UUID, service_id: str, days: int = 30
    ) -> float:
        """Calculate uptime percentage over the last N days."""
        from app.db.models import ServiceHealthRecord
        from sqlalchemy import select, and_, func

        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self._s.execute(
            select(func.count(ServiceHealthRecord.id)).where(
                and_(
                    ServiceHealthRecord.tenant_id == tenant_id,
                    ServiceHealthRecord.service_id == service_id,
                    ServiceHealthRecord.last_check >= cutoff,
                )
            )
        )
        total = result.scalar() or 0
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
        up_count = up_result.scalar() or 0
        return round((up_count / total) * 100, 2)

    async def _get_down_since(
        self, tenant_id: UUID, service_id: str
    ) -> Optional[datetime]:
        """Find when a service first went down."""
        from app.db.models import ServiceHealthRecord
        from sqlalchemy import select, and_, asc

        result = await self._s.execute(
            select(ServiceHealthRecord.last_check)
            .where(
                and_(
                    ServiceHealthRecord.tenant_id == tenant_id,
                    ServiceHealthRecord.service_id == service_id,
                    ServiceHealthRecord.status == "DOWN",
                )
            )
            .order_by(asc(ServiceHealthRecord.last_check))
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    @staticmethod
    async def _async_sleep(seconds: float):
        import asyncio
        await asyncio.sleep(seconds)