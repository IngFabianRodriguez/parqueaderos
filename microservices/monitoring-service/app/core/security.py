"""Security utilities - JWT validation from gateway headers."""
from fastapi import Header, HTTPException


async def get_current_tenant(
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    x_rol: str = Header(..., alias="X-Rol"),
) -> str:
    """Extract tenant from gateway headers."""
    return x_tenant_id
