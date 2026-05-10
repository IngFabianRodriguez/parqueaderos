"""Repository for ReportSchedule entities."""
import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReportSchedule


class ScheduleRepository:
    """Repository for ReportSchedule CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        name: str,
        report_type: str,
        schedule_cron: str,
        created_by: str,
        format: str = "pdf",
        parameters: Optional[dict] = None,
        recipients: Optional[list[str]] = None,
        is_active: bool = True,
    ) -> ReportSchedule:
        """Create a new schedule."""
        schedule = ReportSchedule(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            report_type=report_type,
            schedule_cron=schedule_cron,
            format=format,
            parameters=json.dumps(parameters) if parameters else None,
            recipients=json.dumps(recipients) if recipients else None,
            is_active=is_active,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(schedule)
        await self.session.flush()
        return schedule

    async def get_by_id(self, schedule_id: str, tenant_id: str) -> Optional[ReportSchedule]:
        """Get a schedule by ID within a tenant."""
        result = await self.session.execute(
            select(ReportSchedule).where(
                and_(ReportSchedule.id == schedule_id, ReportSchedule.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_schedules(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None,
    ) -> tuple[list[ReportSchedule], int]:
        """List schedules for a tenant."""
        conditions = [ReportSchedule.tenant_id == tenant_id]
        if is_active is not None:
            conditions.append(ReportSchedule.is_active == is_active)

        count_query = select(func.count()).select_from(ReportSchedule).where(*conditions)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = (
            select(ReportSchedule)
            .where(*conditions)
            .order_by(ReportSchedule.created_at.desc())
        )
        result = await self.session.execute(query)
        schedules = list(result.scalars().all())
        return schedules, total

    async def update(
        self,
        schedule_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        schedule_cron: Optional[str] = None,
        format: Optional[str] = None,
        parameters: Optional[dict] = None,
        recipients: Optional[list[str]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[ReportSchedule]:
        """Update schedule fields."""
        schedule = await self.get_by_id(schedule_id, tenant_id)
        if not schedule:
            return None
        if name is not None:
            schedule.name = name
        if schedule_cron is not None:
            schedule.schedule_cron = schedule_cron
        if format is not None:
            schedule.format = format
        if parameters is not None:
            schedule.parameters = json.dumps(parameters)
        if recipients is not None:
            schedule.recipients = json.dumps(recipients)
        if is_active is not None:
            schedule.is_active = is_active
        schedule.updated_at = datetime.utcnow()
        await self.session.flush()
        return schedule

    async def update_run_times(
        self,
        schedule_id: str,
        last_run_at: datetime,
        next_run_at: datetime,
    ) -> Optional[ReportSchedule]:
        """Update the last_run_at and next_run_at timestamps."""
        schedule = await self.session.get(ReportSchedule, schedule_id)
        if not schedule:
            return None
        schedule.last_run_at = last_run_at
        schedule.next_run_at = next_run_at
        await self.session.flush()
        return schedule

    async def delete(self, schedule_id: str, tenant_id: str) -> bool:
        """Delete a schedule within a tenant."""
        schedule = await self.get_by_id(schedule_id, tenant_id)
        if not schedule:
            return False
        await self.session.delete(schedule)
        await self.session.flush()
        return True