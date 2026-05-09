"""JWT / security helpers — IoT Service."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings

security = HTTPBearer()
settings = get_settings()


class TokenData(BaseModel):
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