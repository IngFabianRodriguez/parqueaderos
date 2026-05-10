"""JWT / security helpers — ANPR Service. Pure Python, no pydantic."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()
security = HTTPBearer()


@dataclass
class TokenData:
    """Decoded JWT payload from API Gateway."""
    sub: str
    tenant_id: str
    role: str | None = None


def decode_token(token: str) -> TokenData:
    """Validate JWT signed by API Gateway."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience="anpr-service",
        )
        return TokenData(
            sub=payload.get("sub", ""),
            tenant_id=payload.get("tenant_id", ""),
            role=payload.get("role"),
        )
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


def tenant_id_from_token(token_data: TokenData) -> uuid.UUID:
    """Extract tenant_id as UUID from token data."""
    return uuid.UUID(token_data.tenant_id)