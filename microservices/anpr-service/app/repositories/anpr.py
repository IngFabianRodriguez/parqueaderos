"""Repository layer — data access objects for ANPR Service."""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select, and_, func, desc

from app.db.models import ANPRCamera, PlateDetection


class ANPRCameraRepository:
    """Data access for anpr_cameras table."""

    def __init__(self, session):
        self.session = session

    async def get_by_id(self, tenant_id: uuid.UUID, camera_id: uuid.UUID) -> Optional[ANPRCamera]:
        stmt = select(ANPRCamera).where(
            and_(ANPRCamera.tenant_id == tenant_id, ANPRCamera.id == camera_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        sede_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ANPRCamera]:
        conditions = [ANPRCamera.tenant_id == tenant_id]
        if sede_id is not None:
            conditions.append(ANPRCamera.sede_id == sede_id)
        if is_active is not None:
            conditions.append(ANPRCamera.is_active == is_active)
        stmt = (
            select(ANPRCamera)
            .where(*conditions)
            .order_by(ANPRCamera.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, camera: ANPRCamera) -> ANPRCamera:
        self.session.add(camera)
        await self.session.flush()
        return camera

    async def update(self, camera: ANPRCamera) -> ANPRCamera:
        await self.session.flush()
        return camera

    async def delete(self, camera: ANPRCamera) -> None:
        await self.session.delete(camera)


class PlateDetectionRepository:
    """Data access for plate_detections table."""

    def __init__(self, session):
        self.session = session

    async def get_by_id(self, tenant_id: uuid.UUID, detection_id: uuid.UUID) -> Optional[PlateDetection]:
        stmt = select(PlateDetection).where(
            and_(PlateDetection.tenant_id == tenant_id, PlateDetection.id == detection_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        camera_id: Optional[uuid.UUID] = None,
        plate_number: Optional[str] = None,
        detection_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PlateDetection]:
        conditions = [PlateDetection.tenant_id == tenant_id]
        if camera_id is not None:
            conditions.append(PlateDetection.camera_id == camera_id)
        if plate_number is not None:
            conditions.append(PlateDetection.plate_number.ilike(f"%{plate_number}%"))
        if detection_type is not None:
            conditions.append(PlateDetection.detection_type == detection_type)
        stmt = (
            select(PlateDetection)
            .where(*conditions)
            .order_by(PlateDetection.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, detection: PlateDetection) -> PlateDetection:
        self.session.add(detection)
        await self.session.flush()
        return detection

    async def count_recent(
        self,
        tenant_id: uuid.UUID,
        camera_id: uuid.UUID,
        hours: int = 24,
    ) -> int:
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = select(func.count(PlateDetection.id)).where(
            and_(
                PlateDetection.tenant_id == tenant_id,
                PlateDetection.camera_id == camera_id,
                PlateDetection.timestamp >= since,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_stats(
        self,
        tenant_id: uuid.UUID,
        camera_id: uuid.UUID,
        hours: int = 24,
    ) -> dict:
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = select(PlateDetection).where(
            and_(
                PlateDetection.tenant_id == tenant_id,
                PlateDetection.camera_id == camera_id,
                PlateDetection.timestamp >= since,
            )
        )
        result = await self.session.execute(stmt)
        detections = list(result.scalars().all())
        total = len(detections)
        avg_confidence = sum(d.confidence for d in detections) / total if total else 0.0
        entry_count = sum(1 for d in detections if d.detection_type == "entry")
        exit_count = sum(1 for d in detections if d.detection_type == "exit")
        return {
            "total_detections": total,
            "avg_confidence": round(avg_confidence, 3),
            "entries": entry_count,
            "exits": exit_count,
        }