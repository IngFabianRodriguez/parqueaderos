"""JWT validation and security utilities.

Validates JWT tokens from API Gateway via headers:
  - X-User-Id: User identifier
  - X-Rol: User role
  - X-Tenant-Id: Tenant identifier
"""

from typing import Optional
from fastapi import HTTPException, status


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
    """Check if user role has required permission level."""
    role_hierarchy = {"admin": 3, "operador": 2, "cliente": 1}
    return role_hierarchy.get(rol, 0) >= role_hierarchy.get(required_rol, 0)