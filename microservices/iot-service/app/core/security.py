"""JWT / security helpers — IoT Service.

RBAC Role Hierarchy:
  - superadmin: Full system access (level 5)
  - admin_tenant: Tenant admin access (level 4)
  - supervisor: Supervisor operations (level 3)
  - operador: Basic operations (level 2)
  - cliente: Read-only access (level 1)

Role-based device command permissions:
  - superadmin, admin_tenant: Can send commands to any device
  - supervisor, operador: Can send commands to devices in their tenant
  - cliente: Cannot send commands (read-only)
"""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings

security = HTTPBearer()
settings = get_settings()

# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    "superadmin": 5,
    "admin_tenant": 4,
    "supervisor": 3,
    "operador": 2,
    "cliente": 1,
}

# Roles allowed to send commands to devices
COMMAND_ROLES = {"superadmin", "admin_tenant", "supervisor", "operador"}

# Roles with admin privileges
ADMIN_ROLES = {"superadmin", "admin_tenant"}


class TokenData(BaseModel):
    """Decoded JWT payload from API Gateway."""

    sub: str
    tenant_id: str
    role: Optional[str] = "cliente"


def decode_token(token: str) -> TokenData:
    """Validate JWT signed by API Gateway."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience="iot-service",
        )
        return TokenData(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_tenant(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenData:
    """Dependency: extract & validate tenant from JWT Bearer."""
    return decode_token(credentials.credentials)


def check_permission(role: str, required_role: str) -> bool:
    """Check if user role meets minimum required role level.

    Args:
        role: Current user role
        required_role: Minimum role required (level from ROLE_HIERARCHY)

    Returns:
        True if user has sufficient role level
    """
    role_level = ROLE_HIERARCHY.get(role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return role_level >= required_level


def can_send_command(role: str) -> bool:
    """Check if role can send commands to IoT devices.

    Args:
        role: Current user role

    Returns:
        True if role is allowed to send commands
    """
    return role in COMMAND_ROLES


def is_admin(role: str) -> bool:
    """Check if role has admin privileges.

    Args:
        role: Current user role

    Returns:
        True if role has admin privileges
    """
    return role in ADMIN_ROLES