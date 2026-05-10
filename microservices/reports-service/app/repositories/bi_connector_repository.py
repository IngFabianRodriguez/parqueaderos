"""Repository for BIConnector entities."""
import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BIConnector


class BIConnectorRepository:
    """Repository for BIConnector CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        name: str,
        connector_type: str,
        config: dict,
    ) -> BIConnector:
        """Create a new BI connector."""
        connector = BIConnector(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            connector_type=connector_type,
            config=json.dumps(config),
            status="disconnected",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(connector)
        await self.session.flush()
        return connector

    async def get_by_id(self, connector_id: str, tenant_id: str) -> Optional[BIConnector]:
        """Get a BI connector by ID within a tenant."""
        result = await self.session.execute(
            select(BIConnector).where(
                and_(BIConnector.id == connector_id, BIConnector.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_connectors(
        self,
        tenant_id: str,
        status: Optional[str] = None,
    ) -> tuple[list[BIConnector], int]:
        """List BI connectors for a tenant."""
        conditions = [BIConnector.tenant_id == tenant_id]
        if status:
            conditions.append(BIConnector.status == status)

        count_query = select(func.count()).select_from(BIConnector).where(*conditions)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = (
            select(BIConnector)
            .where(*conditions)
            .order_by(BIConnector.created_at.desc())
        )
        result = await self.session.execute(query)
        connectors = list(result.scalars().all())
        return connectors, total

    async def update_status(
        self,
        connector_id: str,
        status: str,
        last_sync_at: Optional[datetime] = None,
        last_error: Optional[str] = None,
    ) -> Optional[BIConnector]:
        """Update connector status."""
        connector = await self.session.get(BIConnector, connector_id)
        if not connector:
            return None
        connector.status = status
        if last_sync_at is not None:
            connector.last_sync_at = last_sync_at
        if last_error is not None:
            connector.last_error = last_error
        connector.updated_at = datetime.utcnow()
        await self.session.flush()
        return connector

    async def delete(self, connector_id: str, tenant_id: str) -> bool:
        """Delete a BI connector within a tenant."""
        connector = await self.get_by_id(connector_id, tenant_id)
        if not connector:
            return False
        await self.session.delete(connector)
        await self.session.flush()
        return True