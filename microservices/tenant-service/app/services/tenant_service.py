"""Tenant service business logic."""
import logging
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantConfigGet,
    TenantUsageResponse,
    PlanEnum,
    TenantStatus,
)

logger = logging.getLogger(__name__)


class TenantService:
    """Service for tenant management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(
        self,
        name: str,
        plan: PlanEnum,
        config: Optional[dict] = None,
    ) -> TenantResponse:
        """Create a new tenant with trial plan."""
        from app.db.models import Tenant, TenantConfig
        
        tenant = Tenant(
            name=name,
            plan=plan.value,
            status=TenantStatus.TRIAL.value,
            config=config or {},
        )
        self.db.add(tenant)
        try:
            await self.db.flush()
            await self.db.refresh(tenant)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(f"Tenant with name '{name}' already exists")
        
        logger.info(f"Created tenant {tenant.id} with plan {plan.value}")
        return self._to_response(tenant)

    async def get_tenant(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        requesting_rol: str,
    ) -> Optional[TenantResponse]:
        """Get tenant by ID with access control."""
        from app.db.models import Tenant
        
        # Tenant can only see itself unless it's superadmin
        if str(tenant_id) != requesting_tenant_id and requesting_rol != "superadmin":
            raise PermissionError("Access denied to this tenant")
        
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        
        return self._to_response(tenant)

    async def list_tenants(
        self,
        requesting_tenant_id: str,
        requesting_rol: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TenantResponse], int]:
        """List tenants with pagination."""
        from app.db.models import Tenant
        from sqlalchemy import func, select
        
        query = select(Tenant)
        
        # Non-superadmin can only see their own tenant
        if requesting_rol != "superadmin":
            query = query.where(Tenant.id == UUID(requesting_tenant_id))
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        tenants = result.scalars().all()
        
        return [self._to_response(t) for t in tenants], total

    async def update_tenant(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        requesting_rol: str,
        data: TenantUpdate,
    ) -> Optional[TenantResponse]:
        """Update tenant data."""
        from app.db.models import Tenant
        
        if str(tenant_id) != requesting_tenant_id and requesting_rol != "superadmin":
            raise PermissionError("Access denied")
        
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = result.scalar_one_or_none()
            return self._to_response(tenant) if tenant else None
        
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.db.execute(
            update(Tenant).where(Tenant.id == tenant_id).values(**update_data)
        )
        await self.db.flush()
        
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        logger.info(f"Updated tenant {tenant_id}")
        return self._to_response(tenant) if tenant else None

    async def suspend_tenant(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        requesting_rol: str,
    ) -> bool:
        """Suspend a tenant (soft delete)."""
        from app.db.models import Tenant
        
        if str(tenant_id) != requesting_tenant_id and requesting_rol != "superadmin":
            raise PermissionError("Access denied")
        
        await self.db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(status=TenantStatus.SUSPENDED.value, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        
        logger.info(f"Suspended tenant {tenant_id}")
        return True

    async def reactivate_tenant(self, tenant_id: UUID) -> Optional[TenantResponse]:
        """Reactivate a suspended tenant."""
        from app.db.models import Tenant
        
        await self.db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(status=TenantStatus.ACTIVE.value, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        logger.info(f"Reactivated tenant {tenant_id}")
        return self._to_response(tenant) if tenant else None

    async def get_config(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        key: Optional[str] = None,
    ) -> TenantConfigGet:
        """Get tenant configuration."""
        from app.db.models import Tenant
        
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise ValueError("Tenant not found")
        
        if key:
            return TenantConfigGet(config={key: tenant.config.get(key)})
        
        return TenantConfigGet(config=tenant.config or {})

    async def set_config(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        config_data: dict,
    ) -> TenantConfigGet:
        """Set tenant configuration (partial or full update)."""
        from app.db.models import Tenant
        
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise ValueError("Tenant not found")
        
        current_config = tenant.config or {}
        current_config.update(config_data)
        
        await self.db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(config=current_config, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        
        logger.info(f"Updated config for tenant {tenant_id}")
        return TenantConfigGet(config=current_config)

    async def get_usage(
        self,
        tenant_id: UUID,
        requesting_tenant_id: str,
        requesting_rol: str,
    ) -> TenantUsageResponse:
        """Get tenant usage statistics."""
        from app.db.models import Tenant, TenantUser
        from sqlalchemy import select, func
        
        if str(tenant_id) != requesting_tenant_id and requesting_rol != "superadmin":
            raise PermissionError("Access denied")
        
        # Count users
        users_count = await self.db.execute(
            select(func.count()).select_from(TenantUser).where(TenantUser.tenant_id == tenant_id)
        )
        users_count = users_count.scalar() or 0

        return TenantUsageResponse(
            tenant_id=tenant_id,
            sedes_count=0,  # Sede is managed by sedes-service, not tenant-service
            users_count=users_count,
            api_calls_today=0,  # TODO: integrate with API gateway metrics
            active_sessions=0,   # TODO: integrate with Redis session store
        )

    def _to_response(self, tenant) -> TenantResponse:
        """Convert model to response schema."""
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            plan=PlanEnum(tenant.plan),
            status=TenantStatus(tenant.status),
            config=tenant.config or {},
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
