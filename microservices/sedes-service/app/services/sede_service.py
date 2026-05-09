"""Sede business logic service.

Implements CRUD operations for sedes, zonas, espacios and
disponibilidad tracking per RF-001 to RF-004 and RF-010 to RF-017.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Sede, Zona, Espacio, OcupacionHistorial

logger = logging.getLogger(__name__)


class SedeNotFoundError(Exception):
    """Raised when sede is not found."""

    def __init__(self, sede_id: str):
        self.sede_id = sede_id
        super().__init__(f"Sede not found: {sede_id}")


class ZonaNotFoundError(Exception):
    """Raised when zona is not found."""

    def __init__(self, zona_id: str):
        self.zona_id = zona_id
        super().__init__(f"Zona not found: {zona_id}")


class EspacioNotFoundError(Exception):
    """Raised when espacio is not found."""

    def __init__(self, espacio_id: str):
        self.espacio_id = espacio_id
        super().__init__(f"Espacio not found: {espacio_id}")


class DuplicateSlugError(Exception):
    """Raised when slug already exists for a tenant."""

    def __init__(self, slug: str, tenant_id: str):
        self.slug = slug
        self.tenant_id = tenant_id
        super().__init__(f"Slug '{slug}' already exists for tenant {tenant_id}")


class SedeService:
    """Service for sede business logic.

    Provides CRUD operations, pagination, filtering, and soft delete
    for multi-tenant sede management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize service with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def create_sede(
        self,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Sede:
        """Create a new sede.

        Args:
            tenant_id: Multi-tenant identifier
            data: Sede creation data (nombre, slug, direccion, etc.)

        Returns:
            Created sede instance

        Raises:
            DuplicateSlugError: If slug already exists for tenant
        """
        # Check for duplicate slug
        existing = await self.db.execute(
            select(Sede).where(
                Sede.slug == data.get("slug"),
                Sede.tenant_id == tenant_id,
                Sede.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateSlugError(data.get("slug"), tenant_id)

        now = datetime.now(timezone.utc)
        sede = Sede(
            id=uuid.uuid4().hex,
            tenant_id=tenant_id,
            nombre=data.get("nombre"),
            slug=data.get("slug"),
            direccion=data.get("direccion"),
            ciudad=data.get("ciudad"),
            departamento=data.get("departamento"),
            pais=data.get("pais", "Colombia"),
            latitud=data.get("latitud"),
            longitud=data.get("longitud"),
            telefono=data.get("telefono"),
            email=data.get("email"),
            capacidad=data.get("capacidad", 0),
            espacios_activos=data.get("espacios_activos", 0),
            estado=data.get("estado", True),
            horarios=data.get("horarios"),
            servicios=data.get("servicios"),
            created_at=now,
            updated_at=now,
        )

        self.db.add(sede)
        await self.db.commit()
        await self.db.refresh(sede)

        logger.info("Created sede", extra={"sede_id": sede.id, "tenant_id": tenant_id})
        return sede

    async def get_sede(self, sede_id: str, tenant_id: str) -> Sede:
        """Get sede by ID for specific tenant.

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier

        Returns:
            Sede instance

        Raises:
            SedeNotFoundError: If sede does not exist
        """
        result = await self.db.execute(
            select(Sede).where(
                Sede.id == sede_id,
                Sede.tenant_id == tenant_id,
                Sede.deleted_at.is_(None),
            )
        )
        sede = result.scalar_one_or_none()

        if not sede:
            raise SedeNotFoundError(sede_id)

        return sede

    async def list_sedes(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        filtros: Optional[dict[str, Any]] = None,
    ) -> tuple[list[Sede], int]:
        """List sedes for tenant with pagination and filtering.

        Args:
            tenant_id: Tenant identifier
            page: Page number (1-indexed)
            page_size: Items per page
            filtros: Optional filters (estado, ciudad, departamento)

        Returns:
            Tuple of (list of sedes, total count)
        """
        query = select(Sede).where(
            Sede.tenant_id == tenant_id,
            Sede.deleted_at.is_(None),
        )

        if filtros:
            if "estado" in filtros and filtros["estado"] is not None:
                query = query.where(Sede.estado == filtros["estado"])
            if "ciudad" in filtros and filtros["ciudad"]:
                query = query.where(Sede.ciudad == filtros["ciudad"])
            if "departamento" in filtros and filtros["departamento"]:
                query = query.where(Sede.departamento == filtros["departamento"])

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Sede.created_at.desc())

        result = await self.db.execute(query)
        sedes = list(result.scalars().all())

        return sedes, total

    async def update_sede(
        self,
        sede_id: str,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Sede:
        """Update sede fields.

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier
            data: Fields to update

        Returns:
            Updated sede

        Raises:
            SedeNotFoundError: If sede does not exist
        """
        sede = await self.get_sede(sede_id, tenant_id)

        update_data = {"updated_at": datetime.now(timezone.utc)}

        # Only update provided fields
        allowed_fields = [
            "nombre", "direccion", "ciudad", "departamento", "pais",
            "latitud", "longitud", "telefono", "email", "capacidad",
            "espacios_activos", "estado", "horarios", "servicios",
        ]

        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_data[field] = data[field]

        await self.db.execute(
            update(Sede).where(Sede.id == sede_id).values(**update_data)
        )
        await self.db.commit()
        await self.db.refresh(sede)

        logger.info("Updated sede", extra={"sede_id": sede_id})
        return sede

    async def delete_sede(self, sede_id: str, tenant_id: str) -> bool:
        """Soft delete sede (mark as deleted).

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier

        Returns:
            True if deleted

        Raises:
            SedeNotFoundError: If sede does not exist
        """
        sede = await self.get_sede(sede_id, tenant_id)
        now = datetime.now(timezone.utc)

        await self.db.execute(
            update(Sede)
            .where(Sede.id == sede_id)
            .values(deleted_at=now, updated_at=now, estado=False)
        )
        await self.db.commit()

        logger.info("Soft deleted sede", extra={"sede_id": sede_id})
        return True


class ZonaService:
    """Service for zona business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def create_zona(
        self,
        sede_id: str,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Zona:
        """Create a new zona within a sede.

        Args:
            sede_id: Parent sede identifier
            tenant_id: Multi-tenant identifier
            data: Zona creation data

        Returns:
            Created zona instance
        """
        now = datetime.now(timezone.utc)
        zona = Zona(
            id=uuid.uuid4().hex,
            sede_id=sede_id,
            tenant_id=tenant_id,
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            tipo=data.get("tipo", "general"),
            capacidad=data.get("capacidad", 0),
            espacios_disponibles=data.get("espacios_disponibles", 0),
            piso=data.get("piso"),
            estado=data.get("estado", True),
            created_at=now,
            updated_at=now,
        )

        self.db.add(zona)
        await self.db.commit()
        await self.db.refresh(zona)

        logger.info("Created zona", extra={"zona_id": zona.id, "sede_id": sede_id})
        return zona

    async def get_zona(self, zona_id: str, tenant_id: str) -> Zona:
        """Get zona by ID.

        Args:
            zona_id: Zona identifier
            tenant_id: Tenant identifier

        Returns:
            Zona instance

        Raises:
            ZonaNotFoundError: If zona does not exist
        """
        result = await self.db.execute(
            select(Zona).where(
                Zona.id == zona_id,
                Zona.tenant_id == tenant_id,
            )
        )
        zona = result.scalar_one_or_none()

        if not zona:
            raise ZonaNotFoundError(zona_id)

        return zona

    async def list_zonas(
        self,
        sede_id: str,
        tenant_id: str,
    ) -> list[Zona]:
        """List zonas for a sede.

        Args:
            sede_id: Parent sede identifier
            tenant_id: Tenant identifier

        Returns:
            List of zonas
        """
        query = select(Zona).where(
            Zona.sede_id == sede_id,
            Zona.tenant_id == tenant_id,
        ).order_by(Zona.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_zona(
        self,
        zona_id: str,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Zona:
        """Update zona fields.

        Args:
            zona_id: Zona identifier
            tenant_id: Tenant identifier
            data: Fields to update

        Returns:
            Updated zona

        Raises:
            ZonaNotFoundError: If zona does not exist
        """
        zona = await self.get_zona(zona_id, tenant_id)

        update_data = {"updated_at": datetime.now(timezone.utc)}

        allowed_fields = [
            "nombre", "descripcion", "tipo", "capacidad",
            "espacios_disponibles", "piso", "estado",
        ]

        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_data[field] = data[field]

        await self.db.execute(
            update(Zona).where(Zona.id == zona_id).values(**update_data)
        )
        await self.db.commit()
        await self.db.refresh(zona)

        logger.info("Updated zona", extra={"zona_id": zona_id})
        return zona

    async def delete_zona(self, zona_id: str, tenant_id: str) -> bool:
        """Delete zona (soft delete).

        Args:
            zona_id: Zona identifier
            tenant_id: Tenant identifier

        Returns:
            True if deleted

        Raises:
            ZonaNotFoundError: If zona does not exist
        """
        zona = await self.get_zona(zona_id, tenant_id)
        now = datetime.now(timezone.utc)

        await self.db.execute(
            update(Zona)
            .where(Zona.id == zona_id)
            .values(estado=False, updated_at=now)
        )
        await self.db.commit()

        logger.info("Deleted zona", extra={"zona_id": zona_id})
        return True


class EspacioService:
    """Service for espacio business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def create_espacio(
        self,
        zona_id: str,
        sede_id: str,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Espacio:
        """Create a new espacio within a zona.

        Args:
            zona_id: Parent zona identifier
            sede_id: Parent sede identifier
            tenant_id: Multi-tenant identifier
            data: Espacio creation data

        Returns:
            Created espacio instance
        """
        now = datetime.now(timezone.utc)
        espacio = Espacio(
            id=uuid.uuid4().hex,
            zona_id=zona_id,
            sede_id=sede_id,
            tenant_id=tenant_id,
            numero=data.get("numero"),
            piso=data.get("piso"),
            tipo=data.get("tipo", "general"),
            estado=data.get("estado", "disponible"),
            descripcion=data.get("descripcion"),
            created_at=now,
            updated_at=now,
        )

        self.db.add(espacio)
        await self.db.commit()
        await self.db.refresh(espacio)

        logger.info(
            "Created espacio",
            extra={"espacio_id": espacio.id, "zona_id": zona_id},
        )
        return espacio

    async def get_espacio(self, espacio_id: str, tenant_id: str) -> Espacio:
        """Get espacio by ID.

        Args:
            espacio_id: Espacio identifier
            tenant_id: Tenant identifier

        Returns:
            Espacio instance

        Raises:
            EspacioNotFoundError: If espacio does not exist
        """
        result = await self.db.execute(
            select(Espacio).where(
                Espacio.id == espacio_id,
                Espacio.tenant_id == tenant_id,
            )
        )
        espacio = result.scalar_one_or_none()

        if not espacio:
            raise EspacioNotFoundError(espacio_id)

        return espacio

    async def list_espacios(
        self,
        zona_id: str,
        tenant_id: str,
        tipo: Optional[str] = None,
    ) -> list[Espacio]:
        """List espacios for a zona with optional tipo filter.

        Args:
            zona_id: Parent zona identifier
            tenant_id: Tenant identifier
            tipo: Optional filter by space type (cubierta, descubierta, vip, moto)

        Returns:
            List of espacios
        """
        query = select(Espacio).where(
            Espacio.zona_id == zona_id,
            Espacio.tenant_id == tenant_id,
        )

        if tipo:
            query = query.where(Espacio.tipo == tipo)

        query = query.order_by(Espacio.numero)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_espacio(
        self,
        espacio_id: str,
        tenant_id: str,
        data: dict[str, Any],
    ) -> Espacio:
        """Update espacio fields.

        Args:
            espacio_id: Espacio identifier
            tenant_id: Tenant identifier
            data: Fields to update

        Returns:
            Updated espacio

        Raises:
            EspacioNotFoundError: If espacio does not exist
        """
        espacio = await self.get_espacio(espacio_id, tenant_id)

        update_data = {"updated_at": datetime.now(timezone.utc)}

        allowed_fields = ["numero", "piso", "tipo", "estado", "descripcion"]

        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_data[field] = data[field]

        await self.db.execute(
            update(Espacio).where(Espacio.id == espacio_id).values(**update_data)
        )
        await self.db.commit()
        await self.db.refresh(espacio)

        logger.info("Updated espacio", extra={"espacio_id": espacio_id})
        return espacio

    async def delete_espacio(self, espacio_id: str, tenant_id: str) -> bool:
        """Delete espacio (soft delete).

        Args:
            espacio_id: Espacio identifier
            tenant_id: Tenant identifier

        Returns:
            True if deleted

        Raises:
            EspacioNotFoundError: If espacio does not exist
        """
        espacio = await self.get_espacio(espacio_id, tenant_id)

        await self.db.execute(
            delete(Espacio).where(Espacio.id == espacio_id)
        )
        await self.db.commit()

        logger.info("Deleted espacio", extra={"espacio_id": espacio_id})
        return True


class DisponibilidadService:
    """Service for disponibilidad and ocupacion tracking."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def get_disponibilidad(
        self,
        sede_id: str,
        tenant_id: str,
        incluye_zonas: bool = True,
        tipo_espacio: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get real-time disponibilidad for a sede.

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier
            incluye_zonas: Whether to include per-zone breakdown
            tipo_espacio: Optional filter by space type

        Returns:
            Dict with disponibilidad data

        Raises:
            SedeNotFoundError: If sede does not exist
        """
        # Verify sede exists
        sede_result = await self.db.execute(
            select(Sede).where(
                Sede.id == sede_id,
                Sede.tenant_id == tenant_id,
                Sede.deleted_at.is_(None),
            )
        )
        sede = sede_result.scalar_one_or_none()
        if not sede:
            raise SedeNotFoundError(sede_id)

        # Get zonas
        zonas_query = select(Zona).where(
            Zona.sede_id == sede_id,
            Zona.tenant_id == tenant_id,
        )
        zonas_result = await self.db.execute(zonas_query)
        zonas = list(zonas_result.scalars().all())

        zonas_data = []
        total_espacios = 0
        total_disponibles = 0
        total_ocupados = 0

        for zona in zonas:
            # Count espacios in this zona
            espacios_query = select(Espacio).where(
                Espacio.zona_id == zona.id,
                Espacio.tenant_id == tenant_id,
            )
            if tipo_espacio:
                espacios_query = espacios_query.where(Espacio.tipo == tipo_espacio)

            espacios_result = await self.db.execute(espacios_query)
            espacios = list(espacios_result.scalars().all())

            total = len(espacios)
            disponibles = sum(1 for e in espacios if e.estado == "disponible")
            ocupados = sum(1 for e in espacios if e.estado == "ocupado")

            total_espacios += total
            total_disponibles += disponibles
            total_ocupados += ocupados

            if incluye_zonas:
                ocupacion_pct = (ocupados / total * 100) if total > 0 else 0.0
                zonas_data.append({
                    "zona_id": zona.id,
                    "nombre": zona.nombre,
                    "tipo": zona.tipo,
                    "total": total,
                    "disponibles": disponibles,
                    "ocupados": ocupados,
                    "ocupacion_pct": round(ocupacion_pct, 2),
                })

        ocupacion_pct = (total_ocupados / total_espacios * 100) if total_espacios > 0 else 0.0

        return {
            "sede_id": sede_id,
            "nombre": sede.nombre,
            "total_espacios": total_espacios,
            "espacios_disponibles": total_disponibles,
            "espacios_ocupados": total_ocupados,
            "ocupacion_pct": round(ocupacion_pct, 2),
            "zonas": zonas_data,
        }

    async def get_ocupacion_historial(
        self,
        sede_id: str,
        tenant_id: str,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> list[dict[str, Any]]:
        """Get historical ocupacion data for a sede.

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier
            fecha_inicio: Start date for the query
            fecha_fin: End date for the query

        Returns:
            List of ocupacion records

        Raises:
            SedeNotFoundError: If sede does not exist
        """
        # Verify sede exists
        sede_result = await self.db.execute(
            select(Sede).where(
                Sede.id == sede_id,
                Sede.tenant_id == tenant_id,
                Sede.deleted_at.is_(None),
            )
        )
        sede = sede_result.scalar_one_or_none()
        if not sede:
            raise SedeNotFoundError(sede_id)

        query = select(OcupacionHistorial).where(
            OcupacionHistorial.sede_id == sede_id,
            OcupacionHistorial.tenant_id == tenant_id,
            OcupacionHistorial.fecha >= fecha_inicio,
            OcupacionHistorial.fecha <= fecha_fin,
        ).order_by(OcupacionHistorial.fecha, OcupacionHistorial.hora)

        result = await self.db.execute(query)
        records = result.scalars().all()

        return [
            {
                "fecha": r.fecha,
                "hora": r.hora,
                "espacios_totales": r.espacios_totales,
                "espacios_ocupados": r.espacios_ocupados,
                "ocupacion_pct": r.ocupacion_pct,
            }
            for r in records
        ]

    async def record_ocupacion(
        self,
        sede_id: str,
        tenant_id: str,
        fecha: datetime,
        hora: int,
        espacios_totales: int,
        espacios_ocupados: int,
    ) -> OcupacionHistorial:
        """Record ocupacion snapshot for historical tracking.

        Args:
            sede_id: Sede identifier
            tenant_id: Tenant identifier
            fecha: Date of the record
            hora: Hour of the day (0-23)
            espacios_totales: Total spaces count
            espacios_ocupados: Occupied spaces count

        Returns:
            Created or updated ocupacion record
        """
        ocupacion_pct = (espacios_ocupados / espacios_totales * 100) if espacios_totales > 0 else 0.0
        now = datetime.now(timezone.utc)

        # Check if record exists for this sede/fecha/hora
        existing_result = await self.db.execute(
            select(OcupacionHistorial).where(
                OcupacionHistorial.sede_id == sede_id,
                OcupacionHistorial.fecha == fecha,
                OcupacionHistorial.hora == hora,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            await self.db.execute(
                update(OcupacionHistorial)
                .where(OcupacionHistorial.id == existing.id)
                .values(
                    espacios_totales=espacios_totales,
                    espacios_ocupados=espacios_ocupados,
                    ocupacion_pct=ocupacion_pct,
                )
            )
            existing.espacios_totales = espacios_totales
            existing.espacios_ocupados = espacios_ocupados
            existing.ocupacion_pct = ocupacion_pct
            await self.db.commit()
            return existing
        else:
            record = OcupacionHistorial(
                id=uuid.uuid4().hex,
                sede_id=sede_id,
                tenant_id=tenant_id,
                fecha=fecha,
                hora=hora,
                espacios_totales=espacios_totales,
                espacios_ocupados=espacios_ocupados,
                ocupacion_pct=ocupacion_pct,
                created_at=now,
            )
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
            return record