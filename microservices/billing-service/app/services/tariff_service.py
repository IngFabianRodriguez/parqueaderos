"""Tariff business logic service."""

from typing import Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.tariff_repository import TariffRepository
from app.schemas.billing import (
    TariffCreate,
    TariffResponse,
    TariffListResponse,
)


class TariffService:
    """Service for Tariff business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TariffRepository(session)

    async def create_tariff(
        self,
        tenant_id: str,
        user_id: str,
        data: TariffCreate,
    ) -> TariffResponse:
        """Create a new tariff."""
        tariff = await self.repo.create(
            tenant_id=tenant_id,
            sede_id=data.sede_id,
            name=data.name,
            tariff_type=data.tariff_type,
            amount=data.amount,
            currency=data.currency,
            billing_period=data.billing_period,
            vehicle_type=data.vehicle_type,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
        )
        return TariffResponse(
            id=tariff.id,
            tenant_id=tariff.tenant_id,
            sede_id=tariff.sede_id,
            name=tariff.name,
            tariff_type=tariff.tariff_type,
            amount=tariff.amount,
            currency=tariff.currency,
            billing_period=tariff.billing_period,
            vehicle_type=tariff.vehicle_type,
            valid_from=tariff.valid_from,
            valid_to=tariff.valid_to,
            is_active=tariff.is_active,
            created_at=tariff.created_at,
            updated_at=tariff.updated_at,
        )

    async def get_tariff(self, tariff_id: str, tenant_id: str) -> Optional[TariffResponse]:
        """Get tariff by ID."""
        tariff = await self.repo.get_by_id(tariff_id, tenant_id)
        if not tariff:
            return None
        return TariffResponse(
            id=tariff.id,
            tenant_id=tariff.tenant_id,
            sede_id=tariff.sede_id,
            name=tariff.name,
            tariff_type=tariff.tariff_type,
            amount=tariff.amount,
            currency=tariff.currency,
            billing_period=tariff.billing_period,
            vehicle_type=tariff.vehicle_type,
            valid_from=tariff.valid_from,
            valid_to=tariff.valid_to,
            is_active=tariff.is_active,
            created_at=tariff.created_at,
            updated_at=tariff.updated_at,
        )

    async def list_tariffs(
        self,
        tenant_id: str,
        sede_id: Optional[str] = None,
    ) -> TariffListResponse:
        """List tariffs for a tenant."""
        if sede_id:
            tariffs = await self.repo.list_by_sede(sede_id, tenant_id)
        else:
            tariffs = []
        items = [
            TariffResponse(
                id=t.id,
                tenant_id=t.tenant_id,
                sede_id=t.sede_id,
                name=t.name,
                tariff_type=t.tariff_type,
                amount=t.amount,
                currency=t.currency,
                billing_period=t.billing_period,
                vehicle_type=t.vehicle_type,
                valid_from=t.valid_from,
                valid_to=t.valid_to,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tariffs
        ]
        return TariffListResponse(items=items, total=len(items))

    async def update_tariff(
        self,
        tariff_id: str,
        tenant_id: str,
        data: TariffCreate,
    ) -> Optional[TariffResponse]:
        """Update a tariff."""
        tariff = await self.repo.update(
            tariff_id,
            tenant_id,
            sede_id=data.sede_id,
            name=data.name,
            tariff_type=data.tariff_type,
            amount=data.amount,
            currency=data.currency,
            billing_period=data.billing_period,
            vehicle_type=data.vehicle_type,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
        )
        if not tariff:
            return None
        return TariffResponse(
            id=tariff.id,
            tenant_id=tariff.tenant_id,
            sede_id=tariff.sede_id,
            name=tariff.name,
            tariff_type=tariff.tariff_type,
            amount=tariff.amount,
            currency=tariff.currency,
            billing_period=tariff.billing_period,
            vehicle_type=tariff.vehicle_type,
            valid_from=tariff.valid_from,
            valid_to=tariff.valid_to,
            is_active=tariff.is_active,
            created_at=tariff.created_at,
            updated_at=tariff.updated_at,
        )

    async def deactivate_tariff(self, tariff_id: str, tenant_id: str) -> bool:
        """Deactivate a tariff."""
        return await self.repo.deactivate(tariff_id, tenant_id)