"""Auth API v1 endpoints.

Endpoints for authentication:
  - POST /auth/register - User registration
  - POST /auth/login - User login
  - POST /auth/refresh - Refresh access token
  - POST /auth/logout - Logout user
  - POST /auth/mfa/setup - Setup MFA
  - POST /auth/mfa/verify - Verify MFA code
  - GET /auth/validate - Validate token
  - GET /auth/me - Get current user
  - POST /auth/password/reset - Request password reset
  - POST /auth/password/reset/confirm - Confirm password reset
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.core.security import validate_gateway_headers, check_permission, is_admin
from app.db.session import AsyncSessionLocal
from app.db.models import User, Session
from app.services.auth_service import AuthService, auth_service
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RefreshRequest, RefreshResponse,
    MFASetupResponse, MFAVerifyRequest, MFAVerifyResponse,
    PasswordResetRequest, PasswordResetConfirmRequest,
    UserResponse, ValidateTokenResponse, TokenPayload, ErrorResponse,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def parse_login_request(request: Request) -> LoginRequest:
    """Parse and validate login request from form data or JSON."""
    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type:
        # Handle form data (OAuth2 password flow)
        form_data = request._form
        email = form_data.get("username", [""])[0] if form_data.get("username") else ""
        password = form_data.get("password", [""])[0] if form_data.get("password") else ""
        return LoginRequest(email=email, password=password)
    else:
        # Handle JSON body
        body = request._json if hasattr(request, "_json") else {}
        return LoginRequest(
            email=body.get("email", ""),
            password=body.get("password", ""),
        )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Register a new user.

    Args:
        request: Registration data (email, password, full_name, tenant_id, rol)
        x_user_id: Gateway header (optional for internal calls)
        x_rol: Gateway header (optional for internal calls)
        x_tenant_id: Gateway header (optional for internal calls)

    Returns:
        Created user info

    Raises:
        HTTPException: If email already exists
    """
    body = await request.json()
    try:
        register_request = RegisterRequest(
            email=body.get("email", ""),
            password=body.get("password", ""),
            full_name=body.get("full_name"),
            tenant_id=body.get("tenant_id", ""),
            rol=body.get("rol", "cliente"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    async with AsyncSessionLocal() as session:
        # Check if email already exists
        result = await session.execute(select(User).where(User.email == register_request.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = AuthService.hash_password(register_request.password)
        new_user = User(
            id=user_id,
            tenant_id=register_request.tenant_id,
            email=register_request.email,
            hashed_password=hashed_password,
            full_name=register_request.full_name,
            rol=register_request.rol,
            is_verified=False,
            mfa_enabled=False,
            created_at=datetime.utcnow(),
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return UserResponse(
            id=new_user.id,
            tenant_id=new_user.tenant_id,
            email=new_user.email,
            full_name=new_user.full_name,
            rol=new_user.rol,
            is_verified=new_user.is_verified,
            mfa_enabled=new_user.mfa_enabled,
            created_at=new_user.created_at,
        )


@router.post("/login")
async def login(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """User login endpoint.

    Authenticates user with email and password, returns access and refresh tokens.

    Args:
        request: Login credentials (email, password)
        x_user_id: Gateway header (optional for internal calls)
        x_rol: Gateway header (optional for internal calls)
        x_tenant_id: Gateway header (optional for internal calls)

    Returns:
        LoginResponse with access_token, refresh_token, token_type, expires_in

    Raises:
        HTTPException: If credentials are invalid
    """
    body = await request.json()
    try:
        credentials = LoginRequest(
            email=body.get("email", ""),
            password=body.get("password", ""),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    async with AsyncSessionLocal() as session:
        # Get user by email
        result = await session.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()

        if not user or not AuthService.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Update last login
        user.last_login_at = datetime.utcnow()
        await session.commit()

        # Create tokens
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "tenant_id": user.tenant_id, "rol": user.rol},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh_token = AuthService.create_refresh_token()

        # Store session in database
        session_record = Session(
            id=str(uuid.uuid4()),
            user_id=user.id,
            tenant_id=user.tenant_id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
            is_revoked=False,
            created_at=datetime.utcnow(),
        )
        session.add(session_record)
        await session.commit()

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Refresh access token using a valid refresh token.

    Args:
        request: RefreshRequest containing the refresh_token
        x_user_id: Gateway header (optional for internal calls)
        x_rol: Gateway header (optional for internal calls)
        x_tenant_id: Gateway header (optional for internal calls)

    Returns:
        New access token with updated expiration

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    body = await request.json()
    refresh_token_value = body.get("refresh_token", "")

    async with AsyncSessionLocal() as session:
        # Find valid session with this refresh token
        result = await session.execute(
            select(Session).where(
                Session.refresh_token == refresh_token_value,
                Session.is_revoked == False,
            )
        )
        session_record = result.scalar_one_or_none()

        if not session_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if session_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        # Get user
        user_result = await session.execute(select(User).where(User.id == session_record.user_id))
        user = user_result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Create new access token
        new_access_token = AuthService.create_access_token(
            data={"sub": user.id, "tenant_id": user.tenant_id, "rol": user.rol},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        return RefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )


@router.post("/logout", status_code=204)
async def logout(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Logout user and revoke all sessions.

    Args:
        x_user_id: Gateway header for user identification
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        204 No Content on success
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    async with AsyncSessionLocal() as session:
        # Revoke all sessions for this user
        from sqlalchemy import update
        await session.execute(
            update(Session)
            .where(Session.user_id == x_user_id)
            .values(is_revoked=True)
        )
        await session.commit()

    return None


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Setup MFA for user with TOTP.

    Args:
        x_user_id: Gateway header for user identification
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        MFASetupResponse with TOTP secret and QR code URL

    Raises:
        HTTPException: If user already has MFA enabled or user not found
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == x_user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA already enabled for this user",
            )

        # Generate TOTP secret
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr_code_url = totp.provisioning_uri(name=user.email, issuer_name="Parqueaderos")

        # Store secret (encrypted in production)
        user.mfa_secret = secret
        await session.commit()

        return MFASetupResponse(secret=secret, qr_code_url=qr_code_url)


@router.post("/mfa/verify", response_model=MFAVerifyResponse)
async def mfa_verify(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Verify MFA code and enable MFA if setup.

    Args:
        request: MFAVerifyRequest with 6-digit code
        x_user_id: Gateway header for user identification
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        MFAVerifyResponse with verified=True if code is valid
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    body = await request.json()
    code = body.get("code", "")

    try:
        mfa_request = MFAVerifyRequest(code=code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == x_user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA not setup. Call /auth/mfa/setup first.",
            )

        # Verify TOTP code
        totp = pyotp.TOTP(user.mfa_secret)
        verified = totp.verify(mfa_request.code)

        if verified and not user.mfa_enabled:
            user.mfa_enabled = True
            await session.commit()

        return MFAVerifyResponse(verified=verified, mfa_enabled=user.mfa_enabled)


@router.get("/validate", response_model=ValidateTokenResponse)
async def validate_token(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Validate gateway token from headers.

    Args:
        x_user_id: User identifier from gateway
        x_rol: User role from gateway
        x_tenant_id: Tenant identifier from gateway

    Returns:
        ValidateTokenResponse with validity status and user context
    """
    if not x_user_id:
        return ValidateTokenResponse(valid=False)
    return ValidateTokenResponse(
        valid=True,
        user_id=x_user_id,
        tenant_id=x_tenant_id,
        rol=x_rol,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get current authenticated user info.

    Args:
        x_user_id: Gateway header for user identification
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        UserResponse with current user details

    Raises:
        HTTPException: If user not found
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == x_user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            full_name=user.full_name,
            rol=user.rol,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
        )


@router.post("/password/reset", status_code=202)
async def password_reset_request(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Request password reset email.

    Args:
        request: PasswordResetRequest with user email
        x_user_id: Gateway header (optional for internal calls)
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        202 Accepted (always returns success to prevent email enumeration)
    """
    body = await request.json()
    email = body.get("email", "")

    try:
        reset_request = PasswordResetRequest(email=email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Process password reset request via auth_service
    await auth_service.request_password_reset(reset_request.email)

    # For security, always return 202 to prevent email enumeration
    return None


@router.post("/password/reset/confirm")
async def password_reset_confirm(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Confirm password reset with token and set new password.

    Args:
        request: PasswordResetConfirmRequest with token and new_password
        x_user_id: Gateway header (optional for internal calls)
        x_rol: Gateway header (optional)
        x_tenant_id: Gateway header (optional)

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    body = await request.json()
    token = body.get("token", "")
    new_password = body.get("new_password", "")

    try:
        confirm_request = PasswordResetConfirmRequest(
            token=token,
            new_password=new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    success, message = await auth_service.confirm_password_reset(
        token=confirm_request.token,
        new_password=confirm_request.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return {"message": message}


# Need pyotp import for MFA
import pyotp