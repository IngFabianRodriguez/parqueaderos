"""Business logic for infrastructure and application metrics — RF-103, RF-104, RF-105."""
from __future__ import annotations

import structlog
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from app.db.session import AsyncSession
from app.repositories.monitoring import MetricRecordRepository, ServiceRegistryRepository
from app.schemas.monitoring import (
    InfrastructureMetricsResponse,
    ApplicationMetricsResponse,
    MetricSample,
    MetricsQuery,
    TopSlowEndpoint,
)


logger = structlog.get_logger(__name__)


class MetricsService:
    """Handles infrastructure and application metrics. RF-103, RF-104, RF-105."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._repo = MetricRecordRepository(session)
        self._registry_repo = ServiceRegistryRepository(session)

    async def record_infrastructure_metrics(
        self,
        tenant_id: UUID,
        service_id: str,
        cpu: dict[str, float],
        memory: dict[str, float],
        disk: dict[str, float],
        network: dict[str, float],
    ) -> list[MetricSample]:
        """Record infrastructure metrics (CPU, RAM, disk, network). RF-103."""
        recorded = []
        timestamp = datetime.utcnow()

        for metric_name, value in cpu.items():
            m = await self._repo.create(
                tenant_id,
                service_id=service_id,
                metric_name=f"cpu_{metric_name}",
                metric_type="cpu",
                value=int(value),
                unit="percent",
                labels={},
                recorded_at=timestamp,
            )
            recorded.append(m)

        for metric_name, value in memory.items():
            m = await self._repo.create(
                tenant_id,
                service_id=service_id,
                metric_name=f"memory_{metric_name}",
                metric_type="memory",
                value=int(value),
                unit="bytes",
                labels={},
                recorded_at=timestamp,
            )
            recorded.append(m)

        for metric_name, value in disk.items():
            m = await self._repo.create(
                tenant_id,
                service_id=service_id,
                metric_name=f"disk_{metric_name}",
                metric_type="disk",
                value=int(value),
                unit="bytes",
                labels={},
                recorded_at=timestamp,
            )
            recorded.append(m)

        for metric_name, value in network.items():
            m = await self._repo.create(
                tenant_id,
                service_id=service_id,
                metric_name=f"network_{metric_name}",
                metric_type="network",
                value=int(value),
                unit="bytes",
                labels={},
                recorded_at=timestamp,
            )
            recorded.append(m)

        return recorded

    async def record_application_metrics(
        self,
        tenant_id: UUID,
        service_id: str,
        latency_p50_ms: float,
        latency_p95_ms: float,
        latency_p99_ms: float,
        throughput_rpm: float,
        error_rate_percent: float,
    ) -> list[MetricSample]:
        """Record application-level metrics (latency, throughput, error rate). RF-104."""
        recorded = []
        timestamp = datetime.utcnow()

        for label, value in [
            ("latency_p50", latency_p50_ms),
            ("latency_p95", latency_p95_ms),
            ("latency_p99", latency_p99_ms),
        ]:
            m = await self._repo.create(
                tenant_id,
                service_id=service_id,
                metric_name=label,
                metric_type="latency",
                value=int(value),
                unit="ms",
                labels={},
                recorded_at=timestamp,
            )
            recorded.append(m)

        m = await self._repo.create(
            tenant_id,
            service_id=service_id,
            metric_name="throughput_rpm",
            metric_type="throughput",
            value=int(throughput_rpm),
            unit="rpm",
            labels={},
            recorded_at=timestamp,
        )
        recorded.append(m)

        m = await self._repo.create(
            tenant_id,
            service_id=service_id,
            metric_name="error_rate",
            metric_type="error_rate",
            value=int(error_rate_percent * 100),  # Store as basis points
            unit="percent",
            labels={},
            recorded_at=timestamp,
        )
        recorded.append(m)

        return recorded

    async def get_infrastructure_metrics(
        self, tenant_id: UUID, service_id: str, from_: datetime, to: datetime
    ) -> InfrastructureMetricsResponse:
        """Query infrastructure metrics for a service. RF-103."""
        samples = await self._repo.query(
            tenant_id, service_id=service_id, from_=from_, to=to
        )

        cpu, memory, disk, network = {}, {}, {}, {}
        for s in samples:
            name = s.metric_name
            if s.metric_type == "cpu":
                cpu[name] = float(s.value)
            elif s.metric_type == "memory":
                memory[name] = float(s.value)
            elif s.metric_type == "disk":
                disk[name] = float(s.value)
            elif s.metric_type == "network":
                network[name] = float(s.value)

        return InfrastructureMetricsResponse(
            service_id=service_id,
            timestamp=datetime.utcnow(),
            cpu=cpu,
            memory=memory,
            disk=disk,
            network=network,
        )

    async def get_application_metrics(
        self, tenant_id: UUID, service_id: str, from_: datetime, to: datetime
    ) -> ApplicationMetricsResponse:
        """Query application metrics for a service. RF-104."""
        samples = await self._repo.query(
            tenant_id, service_id=service_id, metric_type="latency", from_=from_, to=to
        )

        # Aggregate to get latest percentiles
        values = {s.metric_name: s.value for s in samples}
        return ApplicationMetricsResponse(
            service_id=service_id,
            timestamp=datetime.utcnow(),
            latency_p50_ms=float(values.get("latency_p50", 0)),
            latency_p95_ms=float(values.get("latency_p95", 0)),
            latency_p99_ms=float(values.get("latency_p99", 0)),
            throughput_rpm=float(values.get("throughput_rpm", 0)),
            error_rate_percent=float(values.get("error_rate", 0)) / 100,
        )

    async def get_top_slow_endpoints(
        self, tenant_id: UUID, limit: int = 10
    ) -> list[TopSlowEndpoint]:
        """Return top N slowest endpoints across all services. RF-104."""
        from app.db.models import MetricSample
        from sqlalchemy import select, func

        # Query for latency_p99 samples
        result = await self._s.execute(
            select(
                MetricSample.service_id,
                MetricSample.metric_name,
                func.avg(MetricSample.value).label("avg_latency"),
                func.max(MetricSample.value).label("max_latency"),
            )
            .where(
                MetricSample.tenant_id == tenant_id,
                MetricSample.metric_name == "latency_p99",
            )
            .group_by(MetricSample.service_id, MetricSample.metric_name)
            .order_by(func.avg(MetricSample.value).desc())
            .limit(limit)
        )
        rows = result.all()
        return [
            TopSlowEndpoint(
                service_id=r.service_id,
                endpoint=r.metric_name,
                method="GET",
                avg_latency_ms=float(r.avg_latency or 0),
                p99_latency_ms=float(r.max_latency or 0),
                calls_per_minute=0.0,  # Would need throughput metric
            )
            for r in rows
        ]

    async def export_metrics(
        self, tenant_id: UUID, query: MetricsQuery, format_: str = "json"
    ) -> dict:
        """Export metrics in CSV or JSON format. RF-103, RF-104."""
        samples = await self._repo.query(
            tenant_id,
            service_id=query.service_id,
            metric_type=query.metric_type.value if query.metric_type else None,
            from_=query.from_,
            to=query.to,
        )

        return {
            "format": format_,
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": [
                {
                    "name": s.metric_name,
                    "value": s.value,
                    "unit": s.unit,
                    "labels": s.labels_ or {},
                    "timestamp": s.recorded_at.isoformat(),
                }
                for s in samples
            ],
        }