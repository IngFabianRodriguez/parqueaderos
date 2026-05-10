"""Device repository — CRUD operations for Device model."""

from typing import Optional
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Device


class DeviceRepository:
    """Repository for Device model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        user_id: str,
        device_token: str,
        device_type: str,
    ) -> Device:
        """Create a new device registration."""
        device = Device(
            id=uuid4().hex,
            tenant_id=tenant_id,
            user_id=user_id,
            device_token=device_token,
            device_type=device_type,
            is_active=True,
        )
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
        result = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, device_token: str) -> Optional[Device]:
        """Get device by token (for deduplication)."""
        result = await self.session.execute(
            select(Device).where(Device.device_token == device_token)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: str, tenant_id: str
    ) -> list[Device]:
        """List devices for a user."""
        result = await self.session.execute(
            select(Device).where(
                Device.user_id == user_id,
                Device.tenant_id == tenant_id,
                Device.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def update(
        self,
        device_id: str,
        is_active: Optional[bool] = None,
        device_token: Optional[str] = None,
    ) -> Optional[Device]:
        """Update a device."""
        values = {}
        if is_active is not None:
            values["is_active"] = is_active
        if device_token is not None:
            values["device_token"] = device_token

        if not values:
            return await self.get_by_id(device_id)

        await self.session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(**values)
        )
        await self.session.commit()
        return await self.get_by_id(device_id)

    async def deactivate(self, device_id: str) -> bool:
        """Deactivate a device."""
        result = await self.session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete(self, device_id: str) -> bool:
        """Delete a device."""
        result = await self.session.execute(
            delete(Device).where(Device.id == device_id)
        )
        await self.session.commit()
        return result.rowcount > 0