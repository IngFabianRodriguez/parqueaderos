"""Webhook repository — CRUD operations for Webhook model."""

import secrets
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Webhook


class WebhookRepository:
    """Repository for Webhook model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        name: str,
        url: str,
        event_type: str,
        secret: Optional[str] = None,
    ) -> Webhook:
        """Create a new webhook."""
        webhook = Webhook(
            id=uuid4().hex,
            tenant_id=tenant_id,
            name=name,
            url=url,
            event_type=event_type,
            secret=secret or secrets.token_urlsafe(32),
            is_active=True,
        )
        self.session.add(webhook)
        await self.session.commit()
        await self.session.refresh(webhook)
        return webhook

    async def get_by_id(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        result = await self.session.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        event_type: Optional[str] = None,
    ) -> tuple[list[Webhook], int]:
        """List webhooks for a tenant."""
        query = select(Webhook).where(Webhook.tenant_id == tenant_id)
        if event_type:
            query = query.where(Webhook.event_type == event_type)

        count_result = await self.session.execute(
            select(Webhook.id).where(Webhook.tenant_id == tenant_id)
        )
        total = len(list(count_result.scalars().all()))

        query = query.order_by(Webhook.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        webhooks = list(result.scalars().all())
        return webhooks, total

    async def update(
        self,
        webhook_id: str,
        data: dict,
    ) -> Optional[Webhook]:
        """Update a webhook."""
        update_values = {k: v for k, v in data.items() if v is not None}
        if not update_values:
            return await self.get_by_id(webhook_id)

        await self.session.execute(
            update(Webhook)
            .where(Webhook.id == webhook_id)
            .values(**update_values)
        )
        await self.session.commit()
        return await self.get_by_id(webhook_id)

    async def deactivate(self, webhook_id: str) -> bool:
        """Deactivate a webhook."""
        result = await self.session.execute(
            update(Webhook)
            .where(Webhook.id == webhook_id)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        result = await self.session.execute(
            delete(Webhook).where(Webhook.id == webhook_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_event_type(
        self, tenant_id: str, event_type: str
    ) -> list[Webhook]:
        """Get active webhooks for a given event type."""
        result = await self.session.execute(
            select(Webhook).where(
                Webhook.tenant_id == tenant_id,
                Webhook.event_type == event_type,
                Webhook.is_active == True,
            )
        )
        return list(result.scalars().all())