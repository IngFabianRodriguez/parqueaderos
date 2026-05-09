"""Sedes API v1 endpoints.

Implements CRUD endpoints for RF-001 to RF-004 and RF-010 to RF-017:
  - POST /sedes - Create sede
  - GET /sedes - List sedes (filter by tenant)
  - GET /sedes/{sede_id} - Get sede by ID
  - PUT /sedes/{sede_id} - Update sede
  - DELETE /sedes/{sede_id} - Soft delete sede
  - GET /sedes/{sede_id}/zonas - List zonas
  - POST /sedes/{sede_id}/zonas - Create zona
  - GET /sedes/{sede_id}/zonas/{zona_id}/espacios - List espacios
  - POST /sedes/{sede_id}/zonas/{zona_id}/espacios - Create espacio
  - GET /sedes/{sede_id}/disponibilidad - Get disponibilidad
  - GET /sedes/{sede_id}/ocupacion - Historial ocupación
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_gateway_headers
from app.db.session import get_db
from app.schemas.sede import (
    DisponibilidadResponse,
    DisponibilidadZona,
    EspacioCreate,
    EspacioListResponse,
    EspacioResponse,
    EspacioUpdate,
    OcupacionHistorialItem,
    OcupacionHistorialResponse,
    SedeCreate,
    SedeListResponse,
    SedeResponse,
    SedeUpdate,
    ZonaCreate,
    ZonaListResponse,
    ZonaResponse,
    ZonaUpdate,
)
from app.services.sede_service import (
    DisponibilidadService,
    DuplicateSlugError,
    EspacioNotFoundError,
    EspacioService,
    SedeNotFoundError,
    SedeService,
    ZonaNotFoundError,
    ZonaService,
)

router = APIRouter(prefix="/sedes", tags=["sedes"])


# ============== DEPENDENCIES ==============

def get_sede_service(db: AsyncSession = Depends(get_db)) -> SedeService:
    """Dependency to get SedeService instance."""
    return SedeService(db)


def get_zona_service(db: AsyncSession = Depends(get_db)) -> ZonaService:
    """Dependency to get ZonaService instance."""
    return ZonaService(db)


def get_espacio_service(db: AsyncSession = Depends(get_db)) -> EspacioService:
    """Dependency to get EspacioService instance."""
    return EspacioService(db)


def get_disponibilidad_service(db: AsyncSession = Depends(get_db)) -> DisponibilidadService:
    """Dependency to get DisponibilidadService instance."""
    return DisponibilidadService(db)


# ============== SEDE ENDPOINTS ==============

@router.post(
    "/",
    response_model=SedeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sede",
)
async def create_sede(
    sede_data: SedeCreate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: SedeService = Depends(get_sede_service),
):
    """Create a new sede.

    Args:
        sede_data: Sede creation data
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Sede service instance

    Returns:
        Created sede

    Raises:
        HTTPException: If validation fails or server error
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        data = sede_data.model_dump()
        sede = await service.create_sede(tenant_id=x_tenant_id, data=data)
        return SedeResponse.model_validate(sede)

    except DuplicateSlugError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Sede with slug '{sede_data.slug}' already exists",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sede: {str(e)}",
        )


@router.get(
    "/",
    response_model=SedeListResponse,
    summary="List all sedes for tenant",
)
async def list_sedes(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    estado: Optional[bool] = Query(default=None, description="Filter by active state"),
    ciudad: Optional[str] = Query(default=None, description="Filter by city"),
    departamento: Optional[str] = Query(default=None, description="Filter by department"),
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: SedeService = Depends(get_sede_service),
):
    """List all sedes for the tenant with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        estado: Optional filter by active state
        ciudad: Optional filter by city
        departamento: Optional filter by department
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Sede service instance

    Returns:
        Paginated list of sedes
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    filtros = {}
    if estado is not None:
        filtros["estado"] = estado
    if ciudad:
        filtros["ciudad"] = ciudad
    if departamento:
        filtros["departamento"] = departamento

    sedes, total = await service.list_sedes(
        tenant_id=x_tenant_id,
        page=page,
        page_size=page_size,
        filtros=filtros if filtros else None,
    )

    pages = math.ceil(total / page_size) if page_size > 0 else 0

    return SedeListResponse(
        items=[SedeResponse.model_validate(s) for s in sedes],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{sede_id}",
    response_model=SedeResponse,
    summary="Get sede by ID",
)
async def get_sede(
    sede_id: str,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: SedeService = Depends(get_sede_service),
):
    """Get sede by ID.

    Args:
        sede_id: Sede identifier
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Sede service instance

    Returns:
        Sede details

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        sede = await service.get_sede(sede_id, tenant_id=x_tenant_id)
        return SedeResponse.model_validate(sede)
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )


@router.put(
    "/{sede_id}",
    response_model=SedeResponse,
    summary="Update sede",
)
async def update_sede(
    sede_id: str,
    sede_data: SedeUpdate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: SedeService = Depends(get_sede_service),
):
    """Update sede fields.

    Args:
        sede_id: Sede identifier
        sede_data: Fields to update
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Sede service instance

    Returns:
        Updated sede

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        data = sede_data.model_dump(exclude_unset=True)
        sede = await service.update_sede(sede_id, tenant_id=x_tenant_id, data=data)
        return SedeResponse.model_validate(sede)
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )


@router.delete(
    "/{sede_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sede (soft delete)",
)
async def delete_sede(
    sede_id: str,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: SedeService = Depends(get_sede_service),
):
    """Soft delete a sede.

    Args:
        sede_id: Sede identifier
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Sede service instance

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        await service.delete_sede(sede_id, tenant_id=x_tenant_id)
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )


# ============== ZONA ENDPOINTS ==============

@router.get(
    "/{sede_id}/zonas",
    response_model=ZonaListResponse,
    summary="List zonas for a sede",
)
async def list_zonas(
    sede_id: str,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: ZonaService = Depends(get_zona_service),
    sede_service: SedeService = Depends(get_sede_service),
):
    """List all zonas for a sede.

    Args:
        sede_id: Parent sede identifier
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Zona service instance
        sede_service: Sede service instance (for validation)

    Returns:
        List of zonas

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    # Verify sede exists
    try:
        await sede_service.get_sede(sede_id, tenant_id=x_tenant_id)
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )

    zonas = await service.list_zonas(sede_id=sede_id, tenant_id=x_tenant_id)
    return ZonaListResponse(
        items=[ZonaResponse.model_validate(z) for z in zonas],
        total=len(zonas),
    )


@router.post(
    "/{sede_id}/zonas",
    response_model=ZonaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new zona",
)
async def create_zona(
    sede_id: str,
    zona_data: ZonaCreate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: ZonaService = Depends(get_zona_service),
    sede_service: SedeService = Depends(get_sede_service),
):
    """Create a new zona within a sede.

    Args:
        sede_id: Parent sede identifier
        zona_data: Zona creation data
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Zona service instance
        sede_service: Sede service instance (for validation)

    Returns:
        Created zona

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    # Verify sede exists
    try:
        await sede_service.get_sede(sede_id, tenant_id=x_tenant_id)
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )

    data = zona_data.model_dump()
    zona = await service.create_zona(sede_id=sede_id, tenant_id=x_tenant_id, data=data)
    return ZonaResponse.model_validate(zona)


@router.put(
    "/{sede_id}/zonas/{zona_id}",
    response_model=ZonaResponse,
    summary="Update zona",
)
async def update_zona(
    sede_id: str,
    zona_id: str,
    zona_data: ZonaUpdate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: ZonaService = Depends(get_zona_service),
):
    """Update zona fields.

    Args:
        sede_id: Parent sede identifier
        zona_id: Zona identifier
        zona_data: Fields to update
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Zona service instance

    Returns:
        Updated zona

    Raises:
        HTTPException: If zona not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        data = zona_data.model_dump(exclude_unset=True)
        zona = await service.update_zona(zona_id, tenant_id=x_tenant_id, data=data)
        return ZonaResponse.model_validate(zona)
    except ZonaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona not found: {zona_id}",
        )


@router.delete(
    "/{sede_id}/zonas/{zona_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete zona",
)
async def delete_zona(
    sede_id: str,
    zona_id: str,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: ZonaService = Depends(get_zona_service),
):
    """Delete a zona (soft delete).

    Args:
        sede_id: Parent sede identifier
        zona_id: Zona identifier
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Zona service instance

    Raises:
        HTTPException: If zona not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        await service.delete_zona(zona_id, tenant_id=x_tenant_id)
    except ZonaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona not found: {zona_id}",
        )


# ============== ESPACIO ENDPOINTS ==============

@router.get(
    "/{sede_id}/zonas/{zona_id}/espacios",
    response_model=EspacioListResponse,
    summary="List espacios for a zona",
)
async def list_espacios(
    sede_id: str,
    zona_id: str,
    tipo: Optional[str] = Query(default=None, description="Filter by space type"),
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    espacio_service: EspacioService = Depends(get_espacio_service),
    zona_service: ZonaService = Depends(get_zona_service),
):
    """List all espacios for a zona with optional tipo filter.

    Args:
        sede_id: Parent sede identifier
        zona_id: Parent zona identifier
        tipo: Optional filter by space type (cubierta, descubierta, vip, moto)
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        espacio_service: Espacio service instance
        zona_service: Zona service instance (for validation)

    Returns:
        List of espacios

    Raises:
        HTTPException: If zona not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    # Verify zona exists
    try:
        await zona_service.get_zona(zona_id, tenant_id=x_tenant_id)
    except ZonaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona not found: {zona_id}",
        )

    espacios = await espacio_service.list_espacios(
        zona_id=zona_id,
        tenant_id=x_tenant_id,
        tipo=tipo,
    )
    return EspacioListResponse(
        items=[EspacioResponse.model_validate(e) for e in espacios],
        total=len(espacios),
    )


@router.post(
    "/{sede_id}/zonas/{zona_id}/espacios",
    response_model=EspacioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new espacio",
)
async def create_espacio(
    sede_id: str,
    zona_id: str,
    espacio_data: EspacioCreate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    espacio_service: EspacioService = Depends(get_espacio_service),
    zona_service: ZonaService = Depends(get_zona_service),
):
    """Create a new espacio within a zona.

    Args:
        sede_id: Parent sede identifier
        zona_id: Parent zona identifier
        espacio_data: Espacio creation data
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        espacio_service: Espacio service instance
        zona_service: Zona service instance (for validation)

    Returns:
        Created espacio

    Raises:
        HTTPException: If zona not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    # Verify zona exists
    try:
        await zona_service.get_zona(zona_id, tenant_id=x_tenant_id)
    except ZonaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona not found: {zona_id}",
        )

    data = espacio_data.model_dump()
    espacio = await espacio_service.create_espacio(
        zona_id=zona_id,
        sede_id=sede_id,
        tenant_id=x_tenant_id,
        data=data,
    )
    return EspacioResponse.model_validate(espacio)


@router.put(
    "/{sede_id}/zonas/{zona_id}/espacios/{espacio_id}",
    response_model=EspacioResponse,
    summary="Update espacio",
)
async def update_espacio(
    sede_id: str,
    zona_id: str,
    espacio_id: str,
    espacio_data: EspacioUpdate,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    espacio_service: EspacioService = Depends(get_espacio_service),
):
    """Update espacio fields.

    Args:
        sede_id: Parent sede identifier
        zona_id: Parent zona identifier
        espacio_id: Espacio identifier
        espacio_data: Fields to update
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        espacio_service: Espacio service instance

    Returns:
        Updated espacio

    Raises:
        HTTPException: If espacio not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        data = espacio_data.model_dump(exclude_unset=True)
        espacio = await espacio_service.update_espacio(
            espacio_id, tenant_id=x_tenant_id, data=data
        )
        return EspacioResponse.model_validate(espacio)
    except EspacioNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Espacio not found: {espacio_id}",
        )


@router.delete(
    "/{sede_id}/zonas/{zona_id}/espacios/{espacio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete espacio",
)
async def delete_espacio(
    sede_id: str,
    zona_id: str,
    espacio_id: str,
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    espacio_service: EspacioService = Depends(get_espacio_service),
):
    """Delete an espacio.

    Args:
        sede_id: Parent sede identifier
        zona_id: Parent zona identifier
        espacio_id: Espacio identifier
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        espacio_service: Espacio service instance

    Raises:
        HTTPException: If espacio not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        await espacio_service.delete_espacio(espacio_id, tenant_id=x_tenant_id)
    except EspacioNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Espacio not found: {espacio_id}",
        )


# ============== DISPONIBILIDAD ENDPOINTS ==============

@router.get(
    "/{sede_id}/disponibilidad",
    response_model=DisponibilidadResponse,
    summary="Get disponibilidad for a sede",
)
async def get_disponibilidad(
    sede_id: str,
    incluye_zonas: bool = Query(default=True, description="Include per-zone breakdown"),
    tipo_espacio: Optional[str] = Query(default=None, description="Filter by space type"),
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: DisponibilidadService = Depends(get_disponibilidad_service),
):
    """Get real-time disponibilidad for a sede.

    Args:
        sede_id: Sede identifier
        incluye_zonas: Whether to include per-zone breakdown
        tipo_espacio: Optional filter by space type (cubierta, descubierta, vip, moto)
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Disponibilidad service instance

    Returns:
        Disponibilidad data

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        data = await service.get_disponibilidad(
            sede_id=sede_id,
            tenant_id=x_tenant_id,
            incluye_zonas=incluye_zonas,
            tipo_espacio=tipo_espacio,
        )

        zonas = [
            DisponibilidadZona(
                zona_id=z["zona_id"],
                nombre=z["nombre"],
                tipo=z["tipo"],
                total=z["total"],
                disponibles=z["disponibles"],
                ocupados=z["ocupados"],
                ocupacion_pct=z["ocupacion_pct"],
            )
            for z in data["zonas"]
        ]

        return DisponibilidadResponse(
            sede_id=data["sede_id"],
            nombre=data["nombre"],
            total_espacios=data["total_espacios"],
            espacios_disponibles=data["espacios_disponibles"],
            espacios_ocupados=data["espacios_ocupados"],
            ocupacion_pct=data["ocupacion_pct"],
            zonas=zonas,
        )
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )


@router.get(
    "/{sede_id}/ocupacion",
    response_model=OcupacionHistorialResponse,
    summary="Get ocupacion historial for a sede",
)
async def get_ocupacion_historial(
    sede_id: str,
    fecha_inicio: datetime = Query(..., description="Start date for the query"),
    fecha_fin: datetime = Query(..., description="End date for the query"),
    x_user_id: Optional[str] = Header(None, description="User ID from gateway"),
    x_rol: Optional[str] = Header(None, description="User role from gateway"),
    x_tenant_id: Optional[str] = Header(None, description="Tenant ID from gateway"),
    service: DisponibilidadService = Depends(get_disponibilidad_service),
):
    """Get historical ocupacion data for a sede.

    Args:
        sede_id: Sede identifier
        fecha_inicio: Start date for the query
        fecha_fin: End date for the query
        x_user_id: Gateway user ID header
        x_rol: Gateway role header
        x_tenant_id: Gateway tenant ID header
        service: Disponibilidad service instance

    Returns:
        Historial of ocupacion records

    Raises:
        HTTPException: If sede not found
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)

    try:
        records = await service.get_ocupacion_historial(
            sede_id=sede_id,
            tenant_id=x_tenant_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        datos = [
            OcupacionHistorialItem(
                fecha=r["fecha"],
                hora=r["hora"],
                espacios_totales=r["espacios_totales"],
                espacios_ocupados=r["espacios_ocupados"],
                ocupacion_pct=r["ocupacion_pct"],
            )
            for r in records
        ]

        return OcupacionHistorialResponse(
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            datos=datos,
        )
    except SedeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sede not found: {sede_id}",
        )