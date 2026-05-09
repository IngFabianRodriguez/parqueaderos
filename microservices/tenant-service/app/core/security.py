"""Security utilities - JWT validation from gateway headers."""
from fastapi import Header, HTTPException
from typing import Optional


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


def validate_gateway_headers(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_rol: Optional[str] = Header(None, alias="X-Rol"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
) -> dict:
    """Validate and extract gateway headers.
    
    Returns dict with user_id, rol, tenant_id.
    Raises HTTPException 401 if any required header is missing.
    """
    if not x_user_id:
        raise UnauthorizedException("Missing X-User-Id header")
    if not x_rol:
        raise UnauthorizedException("Missing X-Rol header")
    if not x_tenant_id:
        raise UnauthorizedException("Missing X-Tenant-Id header")
    
    return {"user_id": x_user_id, "rol": x_rol, "tenant_id": x_tenant_id}


def require_tenant_admin(rol: str) -> None:
    """Require tenant_admin or superadmin role."""
    if rol not in ("tenant_admin", "superadmin"):
        raise ForbiddenException("Requires tenant_admin or superadmin role")


def check_permission(user_rol: str, required_rol: str) -> bool:
    """Check if user_rol has permission for required_rol."""
    role_hierarchy = {
        "superadmin": ["superadmin", "tenant_admin", "sede_manager", "operador", "cliente"],
        "tenant_admin": ["tenant_admin", "sede_manager", "operador", "cliente"],
        "sede_manager": ["sede_manager", "operador", "cliente"],
        "operador": ["operador", "cliente"],
        "cliente": ["cliente"],
    }
    return required_rol in role_hierarchy.get(user_rol, [])
