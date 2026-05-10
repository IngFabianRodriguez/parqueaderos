"""JWT validation and security utilities.

Validates JWT tokens from API Gateway via headers:
  - X-User-Id: User identifier
  - X-Rol: User role
  - X-Tenant-Id: Tenant identifier

RBAC Role Hierarchy:
  - superadmin: Full system access (level 5)
  - admin_tenant: Tenant admin access (level 4)
  - supervisor: Supervisor operations (level 3)
  - operador: Basic operations (level 2)
  - cliente: Read-only access (level 1)
"""

from typing import Optional, List
from fastapi import HTTPException, status

# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    "superadmin": 5,
    "admin_tenant": 4,
    "supervisor": 3,
    "operador": 2,
    "cliente": 1,
}

# Roles that have admin privileges
ADMIN_ROLES = {"superadmin", "admin_tenant"}


def validate_gateway_headers(
    user_id: Optional[str],
    rol: Optional[str],
    tenant_id: Optional[str],
) -> dict:
    """Validate gateway headers and return context.

    Args:
        user_id: User identifier from gateway
        rol: User role from gateway
        tenant_id: Tenant identifier from gateway

    Returns:
        dict with validated headers

    Raises:
        HTTPException: If required headers are missing
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Rol header",
        )
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-Id header",
        )

    return {"user_id": user_id, "rol": rol, "tenant_id": tenant_id}


def check_permission(rol: str, required_rol: str) -> bool:
    """Check if user role has required permission level.

    Args:
        rol: Current user role
        required_rol: Minimum role required

    Returns:
        True if user has sufficient permissions
    """
    role_level = ROLE_HIERARCHY.get(rol, 0)
    required_level = ROLE_HIERARCHY.get(required_rol, 0)
    return role_level >= required_level


def require_role(rol: str, allowed_roles: List[str]) -> bool:
    """Check if user role is in allowed roles list.

    Args:
        rol: Current user role
        allowed_roles: List of allowed roles

    Returns:
        True if user role is allowed
    """
    return rol in allowed_roles


def is_admin(rol: str) -> bool:
    """Check if role has admin privileges.

    Args:
        rol: Current user role

    Returns:
        True if role has admin privileges
    """
    return rol in ADMIN_ROLES