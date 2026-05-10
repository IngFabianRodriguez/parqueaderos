"""Repository for Conciliacion operations (RF-169, RF-170)."""

from typing import Optional, List
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conciliacion


class ConciliacionRepository:
    """Repository for Conciliacion CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        turno_id: str,
        operador_id: str,
        sede_id: str,
        total_esperado: Decimal = Decimal("0.00"),
        total_fisico: Decimal = Decimal("0.00"),
        diferencia: Decimal = Decimal("0.00"),
        porcentaje_diferencia: Decimal = Decimal("0.00"),
        estado: str = "sin_datos",
        umbral_aplicado: Decimal = Decimal("0.5"),
    ) -> Conciliacion:
        """Create a new conciliacion record."""
        conciliacion = Conciliacion(
            id=str(uuid4()),
            tenant_id=tenant_id,
            turno_id=turno_id,
            operador_id=operador_id,
            sede_id=sede_id,
            total_esperado=total_esperado,
            total_fisico=total_fisico,
            diferencia=diferencia,
            porcentaje_diferencia=porcentaje_diferencia,
            estado=estado,
            umbral_aplicado=umbral_aplicado,
            fecha_ultima_conciliacion=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(conciliacion)
        await self.session.flush()
        return conciliacion

    async def get_by_id(self, conciliacion_id: str, tenant_id: str) -> Optional[Conciliacion]:
        """Get conciliacion by ID."""
        result = await self.session.execute(
            select(Conciliacion).where(
                Conciliacion.id == conciliacion_id, Conciliacion.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_turno(self, turno_id: str, tenant_id: str) -> Optional[Conciliacion]:
        """Get conciliacion by turno ID."""
        result = await self.session.execute(
            select(Conciliacion).where(
                Conciliacion.turno_id == turno_id, Conciliacion.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        conciliacion_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[Conciliacion]:
        """Update a conciliacion record."""
        kwargs["updated_at"] = datetime.utcnow()
        kwargs["fecha_ultima_conciliacion"] = datetime.utcnow()
        await self.session.execute(
            update(Conciliacion)
            .where(Conciliacion.id == conciliacion_id, Conciliacion.tenant_id == tenant_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(conciliacion_id, tenant_id)

    async def list_discrepancias(
        self,
        tenant_id: str,
        estado: Optional[str] = "en_discrepancia",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Conciliacion], int]:
        """List discrepancies (conciliaciones with estado en_discrepancia)."""
        query = select(Conciliacion).where(
            Conciliacion.tenant_id == tenant_id,
            Conciliacion.estado == estado,
        )
        count_query = select(func.count()).select_from(Conciliacion).where(
            Conciliacion.tenant_id == tenant_id,
            Conciliacion.estado == estado,
        )
        query = query.order_by(Conciliacion.fecha_ultima_conciliacion.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        return list(result.scalars().all()), total

    async def get_or_create_for_turno(
        self,
        tenant_id: str,
        turno_id: str,
        operador_id: str,
        sede_id: str,
    ) -> Conciliacion:
        """Get existing conciliacion for turno or create new one."""
        existing = await self.get_by_turno(turno_id, tenant_id)
        if existing:
            return existing
        return await self.create(tenant_id, turno_id, operador_id, sede_id)