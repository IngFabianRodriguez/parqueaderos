"""Repository for Tariff operations."""

from typing import Optional, List
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Tariff


class TariffRepository:
    """Repository for Tariff CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        sede_id: str,
        name: str,
        tariff_type: str,
        amount: Decimal,
        currency: str = "COP",
        billing_period: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
    ) -> Tariff:
        """Create a new tariff."""
        tariff = Tariff(
            id=str(uuid4()),
            tenant_id=tenant_id,
            sede_id=sede_id,
            name=name,
            tariff_type=tariff_type,
            amount=amount,
            currency=currency,
            billing_period=billing_period,
            vehicle_type=vehicle_type,
            valid_from=valid_from or datetime.utcnow(),
            valid_to=valid_to,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(tariff)
        await self.session.flush()
        return tariff

    async def get_by_id(self, tariff_id: str, tenant_id: str) -> Optional[Tariff]:
        """Get tariff by ID."""
        result = await self.session.execute(
            select(Tariff).where(Tariff.id == tariff_id, Tariff.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list_by_sede(self, sede_id: str, tenant_id: str, active_only: bool = True) -> List[Tariff]:
        """List tariffs by sede."""
        query = select(Tariff).where(Tariff.sede_id == sede_id, Tariff.tenant_id == tenant_id)
        if active_only:
            query = query.where(Tariff.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, tariff_id: str, tenant_id: str, **kwargs) -> Optional[Tariff]:
        """Update a tariff."""
        kwargs["updated_at"] = datetime.utcnow()
        await self.session.execute(
            update(Tariff)
            .where(Tariff.id == tariff_id, Tariff.tenant_id == tenant_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(tariff_id, tenant_id)

    async def deactivate(self, tariff_id: str, tenant_id: str) -> bool:
        """Deactivate a tariff."""
        result = await self.session.execute(
            update(Tariff)
            .where(Tariff.id == tariff_id, Tariff.tenant_id == tenant_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.session.flush()
        return result.rowcount > 0