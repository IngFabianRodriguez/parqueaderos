"""Repository for Moroso operations."""

from typing import Optional, List
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Moroso


class MorosoRepository:
    """Repository for Moroso CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        customer_id: str,
        customer_name: str,
        invoice_id: str,
        amount_due: Decimal,
        days_overdue: int = 0,
        status: str = "active",
    ) -> Moroso:
        """Create a new moroso record."""
        moroso = Moroso(
            id=str(uuid4()),
            tenant_id=tenant_id,
            customer_id=customer_id,
            customer_name=customer_name,
            invoice_id=invoice_id,
            amount_due=amount_due,
            days_overdue=days_overdue,
            status=status,
            created_at=datetime.utcnow(),
        )
        self.session.add(moroso)
        await self.session.flush()
        return moroso

    async def get_by_id(self, moroso_id: str, tenant_id: str) -> Optional[Moroso]:
        """Get moroso by ID."""
        result = await self.session.execute(
            select(Moroso).where(Moroso.id == moroso_id, Moroso.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, page: int = 1, page_size: int = 20) -> tuple[List[Moroso], int]:
        """List morosos with pagination."""
        query = select(Moroso).where(Moroso.tenant_id == tenant_id, Moroso.status == "active")
        count_query = select(func.count()).select_from(Moroso).where(
            Moroso.tenant_id == tenant_id, Moroso.status == "active"
        )
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        return list(result.scalars().all()), total

    async def resolve(self, moroso_id: str, tenant_id: str) -> Optional[Moroso]:
        """Mark moroso as resolved (paid)."""
        await self.session.execute(
            update(Moroso)
            .where(Moroso.id == moroso_id, Moroso.tenant_id == tenant_id)
            .values(status="paid", resolved_at=datetime.utcnow())
        )
        await self.session.flush()
        return await self.get_by_id(moroso_id, tenant_id)