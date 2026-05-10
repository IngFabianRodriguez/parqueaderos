"""Notification repository — CRUD operations for Notification model."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Notification


class NotificationRepository:
    """Repository for Notification model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        user_id: str,
        notification_type: str,
        channel: str,
        recipient: str,
        subject: Optional[str],
        content: str,
        metadata: Optional[dict] = None,
    ) -> Notification:
        """Create a new notification record."""
        notification = Notification(
            id=uuid4().hex,
            tenant_id=tenant_id,
            user_id=user_id,
            type=notification_type,
            channel=channel,
            recipient=recipient,
            subject=subject,
            content=content,
            metadata=metadata,
            status="pending",
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: str, tenant_id: str, limit: int = 50
    ) -> list[Notification]:
        """List notifications for a user."""
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.tenant_id == tenant_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[Notification], int]:
        """List notifications for a tenant with pagination."""
        query = select(Notification).where(Notification.tenant_id == tenant_id)
        if status:
            query = query.where(Notification.status == status)

        count_result = await self.session.execute(
            select(Notification.id).where(Notification.tenant_id == tenant_id)
        )
        total = len(list(count_result.scalars().all()))

        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        notifications = list(result.scalars().all())
        return notifications, total

    async def update_status(
        self,
        notification_id: str,
        status: str,
        sent_at: Optional[datetime] = None,
    ) -> Optional[Notification]:
        """Update notification status."""
        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status=status, sent_at=sent_at or datetime.utcnow())
        )
        await self.session.commit()
        return await self.get_by_id(notification_id)

    async def mark_failed(self, notification_id: str, error: Optional[str] = None) -> Optional[Notification]:
        """Mark notification as failed."""
        metadata = {"error": error} if error else None
        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status="failed", metadata=metadata)
        )
        await self.session.commit()
        return await self.get_by_id(notification_id)

    async def delete(self, notification_id: str) -> bool:
        """Delete a notification."""
        result = await self.session.execute(
            delete(Notification).where(Notification.id == notification_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def bulk_create(
        self,
        items: list[dict],
    ) -> list[Notification]:
        """Bulk create notifications."""
        notifications = [
            Notification(
                id=uuid4().hex,
                tenant_id=item["tenant_id"],
                user_id=item["user_id"],
                type=item["type"],
                channel=item["channel"],
                recipient=item["recipient"],
                subject=item.get("subject"),
                content=item["content"],
                metadata=item.get("metadata"),
                status="pending",
            )
            for item in items
        ]
        self.session.add_all(notifications)
        await self.session.commit()
        for n in notifications:
            await self.session.refresh(n)
        return notifications