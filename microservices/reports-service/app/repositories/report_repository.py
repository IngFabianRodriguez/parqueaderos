"""Repository for Report entities."""
import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Report


class ReportRepository:
    """Repository for Report CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        name: str,
        report_type: str,
        generated_by: str,
        format: str = "pdf",
        parameters: Optional[dict] = None,
    ) -> Report:
        """Create a new report record."""
        report = Report(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            report_type=report_type,
            format=format,
            status="pending",
            parameters=json.dumps(parameters) if parameters else None,
            generated_by=generated_by,
            created_at=datetime.utcnow(),
        )
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_by_id(self, report_id: str, tenant_id: str) -> Optional[Report]:
        """Get a report by ID within a tenant."""
        result = await self.session.execute(
            select(Report).where(
                and_(Report.id == report_id, Report.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        report_type: Optional[str] = None,
    ) -> tuple[list[Report], int]:
        """List reports for a tenant with pagination."""
        conditions = [Report.tenant_id == tenant_id]
        if report_type:
            conditions.append(Report.report_type == report_type)

        # Count total
        count_query = select(func.count()).select_from(Report).where(*conditions)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Fetch page
        offset = (page - 1) * page_size
        query = (
            select(Report)
            .where(*conditions)
            .order_by(Report.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        reports = list(result.scalars().all())
        return reports, total

    async def update_status(
        self,
        report_id: str,
        status: str,
        file_url: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Report]:
        """Update report status and completion details."""
        report = await self.session.get(Report, report_id)
        if not report:
            return None
        report.status = status
        if status == "ready":
            report.completed_at = datetime.utcnow()
        if file_url is not None:
            report.file_url = file_url
        if file_size_bytes is not None:
            report.file_size_bytes = file_size_bytes
        if error_message is not None:
            report.error_message = error_message
        await self.session.flush()
        return report

    async def delete(self, report_id: str, tenant_id: str) -> bool:
        """Delete a report within a tenant."""
        report = await self.get_by_id(report_id, tenant_id)
        if not report:
            return False
        await self.session.delete(report)
        await self.session.flush()
        return True