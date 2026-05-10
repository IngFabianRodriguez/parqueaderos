"""Template repository — CRUD operations for Template model."""

from typing import Optional
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Template


class TemplateRepository:
    """Repository for Template model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        name: str,
        template_type: str,
        channel: str,
        content: str,
        subject: Optional[str] = None,
        variables: Optional[list[str]] = None,
    ) -> Template:
        """Create a new template."""
        template = Template(
            id=uuid4().hex,
            tenant_id=tenant_id,
            name=name,
            type=template_type,
            channel=channel,
            subject=subject,
            content=content,
            variables=variables or [],
            is_active=True,
        )
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def get_by_id(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        result = await self.session.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, name: str, tenant_id: str
    ) -> Optional[Template]:
        """Get template by name within a tenant."""
        result = await self.session.execute(
            select(Template).where(
                Template.name == name,
                Template.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        template_type: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> tuple[list[Template], int]:
        """List templates for a tenant with optional filters."""
        query = select(Template).where(Template.tenant_id == tenant_id)
        if template_type:
            query = query.where(Template.type == template_type)
        if channel:
            query = query.where(Template.channel == channel)

        count_result = await self.session.execute(
            select(Template.id).where(Template.tenant_id == tenant_id)
        )
        total = len(list(count_result.scalars().all()))

        query = query.order_by(Template.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        templates = list(result.scalars().all())
        return templates, total

    async def update(
        self,
        template_id: str,
        data: dict,
    ) -> Optional[Template]:
        """Update a template."""
        update_values = {k: v for k, v in data.items() if v is not None}
        if not update_values:
            return await self.get_by_id(template_id)

        await self.session.execute(
            update(Template)
            .where(Template.id == template_id)
            .values(**update_values)
        )
        await self.session.commit()
        return await self.get_by_id(template_id)

    async def deactivate(self, template_id: str) -> bool:
        """Deactivate a template."""
        result = await self.session.execute(
            update(Template)
            .where(Template.id == template_id)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete(self, template_id: str) -> bool:
        """Delete a template."""
        result = await self.session.execute(
            delete(Template).where(Template.id == template_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_active_by_type(
        self, tenant_id: str, template_type: str, channel: str
    ) -> Optional[Template]:
        """Get active template by type and channel."""
        result = await self.session.execute(
            select(Template).where(
                Template.tenant_id == tenant_id,
                Template.type == template_type,
                Template.channel == channel,
                Template.is_active == True,
            )
        )
        return result.scalar_one_or_none()