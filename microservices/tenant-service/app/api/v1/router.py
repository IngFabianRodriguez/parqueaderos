"""Tenant API v1 endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from typing import Optional
from uuid import UUID

from app.core.security import validate_gateway_headers, require_tenant_admin
from app.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
    TenantListResponse,
    TenantConfigGet,
    TenantUsageResponse,
    PlanEnum,
)
from app.services.tenant_service import TenantService
from app.db.session import get_db

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=TenantResponse, status_code=201)
async def create_tenant(
    tenant_data: TenantCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create a new tenant.
    
    RF-029: El sistema debe permitir crear un nuevo tenant.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    require_tenant_admin(x_rol)
    
    async for db in get_db():
        service = TenantService(db)
        tenant = await service.create_tenant(
            name=tenant_data.name,
            plan=tenant_data.plan,
            config=tenant_data.config or {},
        )
        return tenant


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List all tenants (superadmin) or just the current tenant.
    
    RF-030: El sistema debe listar tenants con paginación.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    
    async for db in get_db():
        service = TenantService(db)
        tenants, total = await service.list_tenants(
            requesting_tenant_id=x_tenant_id,
            requesting_rol=x_rol,
            page=page,
            page_size=page_size,
        )
        return TenantListResponse(
            tenants=tenants,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get tenant by ID.
    
    RF-031: El sistema debe permitir consultar un tenant por su ID.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    
    async for db in get_db():
        service = TenantService(db)
        tenant = await service.get_tenant(tenant_id, x_tenant_id, x_rol)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Update tenant.
    
    RF-032: El sistema debe permitir actualizar datos del tenant.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    require_tenant_admin(x_rol)
    
    async for db in get_db():
        service = TenantService(db)
        tenant = await service.update_tenant(tenant_id, x_tenant_id, x_rol, tenant_data)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: UUID,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Soft-delete (suspend) a tenant.
    
    RF-033: El sistema debe permitir suspender un tenant.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    require_tenant_admin(x_rol)
    
    async for db in get_db():
        service = TenantService(db)
        success = await service.suspend_tenant(tenant_id, x_tenant_id, x_rol)
        if not success:
            raise HTTPException(status_code=404, detail="Tenant not found")


@router.post("/{tenant_id}/reactivate", response_model=TenantResponse)
async def reactivate_tenant(
    tenant_id: UUID,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Reactivate a suspended tenant.
    
    RF-034: El sistema debe permitir reactiv ar un tenant suspendido.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    require_tenant_admin(x_rol)
    
    async for db in get_db():
        service = TenantService(db)
        tenant = await service.reactivate_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant


@router.get("/{tenant_id}/config", response_model=TenantConfigGet)
async def get_tenant_config(
    tenant_id: UUID,
    key: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get tenant configuration.
    
    RF-035: El sistema debe permitir consultar configuración del tenant.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    
    async for db in get_db():
        service = TenantService(db)
        config = await service.get_config(tenant_id, x_tenant_id, key)
        return config


@router.put("/{tenant_id}/config", response_model=TenantConfigGet)
async def set_tenant_config(
    tenant_id: UUID,
    config_data: dict,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Set tenant configuration.
    
    RF-036: El sistema debe permitir actualizar configuración del tenant.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    require_tenant_admin(x_rol)
    
    async for db in get_db():
        service = TenantService(db)
        result = await service.set_config(tenant_id, x_tenant_id, config_data)
        return result


@router.get("/{tenant_id}/usage", response_model=TenantUsageResponse)
async def get_tenant_usage(
    tenant_id: UUID,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get tenant usage statistics.
    
    RF-037: El sistema debe mostrar uso del tenant (sedes, usuarios, llamadas).
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    
    async for db in get_db():
        service = TenantService(db)
        usage = await service.get_usage(tenant_id, x_tenant_id, x_rol)
        return usage
