"""Business logic for maintenance windows — RF-108."""
from __future__ import annotations

import structlog
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.db.session import AsyncSession
from app.repositories.monitoring import MaintenanceWindowRepository
from app.schemas.monitoring import (
    MaintenanceWindowCreate, MaintenanceWindowUpdate, MaintenanceWindowResponse,
)


logger = structlog.get_logger(__name__)


class MaintenanceWindowService:
    """Manages maintenance windows. RF-108."""

    def __init__(self, session: AsyncSession):
        self._s = session
        self._repo = MaintenanceWindowRepository(session)

    async def create_window(
        self, tenant_id: UUID, window_in: MaintenanceWindowCreate
    ) -> MaintenanceWindowResponse:
        # Validate times don't overlap with existing active windows
        existing = await self._repo.list(tenant_id)
        for w in existing:
            if w.estado not in ("active", "scheduled"):
                continue
            if (
                window_in.start_time < w.end_time
                and window_in.end_time > w.start_time
            ):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=409,
                    detail="Time window overlaps with existing maintenance window",
                )

        data = window_in.model_dump()
        # Convert enums to values
        data["services_affected"] = data.get("services_affected", ["all"])
        data["severities_affected"] = [
            s.value if hasattr(s, "value") else s for s in data.get("severities_affected", [])
        ]

        window = await self._repo.create(tenant_id, **data)
        logger.info("maintenance_window_created", window_id=str(window.id))
        return MaintenanceWindowResponse.model_validate(window)

    async def list_windows(self, tenant_id: UUID) -> list[MaintenanceWindowResponse]:
        windows = await self._repo.list(tenant_id)
        return [MaintenanceWindowResponse.model_validate(w) for w in windows]

    async def get_window(
        self, tenant_id: UUID, window_id: UUID
    ) -> Optional[MaintenanceWindowResponse]:
        window = await self._repo.get_by_id(tenant_id, window_id)
        return MaintenanceWindowResponse.model_validate(window) if window else None

    async def extend_window(
        self, tenant_id: UUID, window_id: UUID, new_end_time: datetime
    ) -> Optional[MaintenanceWindowResponse]:
        window = await self._repo.get_by_id(tenant_id, window_id)
        if not window:
            return None
        window.end_time = new_end_time
        await self._s.flush()
        logger.info("maintenance_window_extended", window_id=str(window_id))
        return MaintenanceWindowResponse.model_validate(window)

    async def cancel_window(
        self, tenant_id: UUID, window_id: UUID
    ) -> Optional[MaintenanceWindowResponse]:
        window = await self._repo.get_by_id(tenant_id, window_id)
        if not window:
            return None
        updated = await self._repo.update_status(window, "cancelled")
        logger.info("maintenance_window_cancelled", window_id=str(window_id))
        return MaintenanceWindowResponse.model_validate(updated)

    async def get_silenced_alerts(
        self, tenant_id: UUID, window_id: UUID
    ) -> list[dict]:
        """Return alerts that were silenced by this maintenance window."""
        from app.repositories.monitoring import AlertRepository
        from app.db.models import Alert

        window = await self._repo.get_by_id(tenant_id, window_id)
        if not window:
            return []

        alert_repo = AlertRepository(self._s)
        alerts, _ = await alert_repo.list(
            tenant_id, status="SILENCED", limit=100
        )
        return [
            {
                "alert_id": str(a.id),
                "service_id": a.service_id,
                "message": a.message,
                "silenced_until": a.silenced_until.isoformat() if a.silenced_until else None,
            }
            for a in alerts
        ]