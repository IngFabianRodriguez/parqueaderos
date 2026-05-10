"""Preference repository — CRUD operations for UserPreference model."""

from typing import Optional
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserPreference


class PreferenceRepository:
    """Repository for UserPreference model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(
        self,
        tenant_id: str,
        user_id: str,
    ) -> UserPreference:
        """Get existing preferences or create default ones."""
        result = await self.session.execute(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.tenant_id == tenant_id,
            )
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            pref = UserPreference(
                id=uuid4().hex,
                tenant_id=tenant_id,
                user_id=user_id,
                email_enabled=True,
                push_enabled=True,
                sms_enabled=False,
                webhook_enabled=True,
            )
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)
        return pref

    async def get_by_user(
        self, user_id: str, tenant_id: str
    ) -> Optional[UserPreference]:
        """Get user preferences."""
        result = await self.session.execute(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        user_id: str,
        tenant_id: str,
        email_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        webhook_enabled: Optional[bool] = None,
    ) -> Optional[UserPreference]:
        """Update user preferences."""
        values = {}
        if email_enabled is not None:
            values["email_enabled"] = email_enabled
        if push_enabled is not None:
            values["push_enabled"] = push_enabled
        if sms_enabled is not None:
            values["sms_enabled"] = sms_enabled
        if webhook_enabled is not None:
            values["webhook_enabled"] = webhook_enabled

        if not values:
            return await self.get_by_user(user_id, tenant_id)

        pref = await self.get_or_create(tenant_id, user_id)
        for key, val in values.items():
            setattr(pref, key, val)

        await self.session.execute(
            update(UserPreference)
            .where(UserPreference.id == pref.id)
            .values(**values)
        )
        await self.session.commit()
        return await self.get_by_user(user_id, tenant_id)