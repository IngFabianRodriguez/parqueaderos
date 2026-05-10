"""Repository for Turno operations (RF-172)."""

from typing import Optional, List
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Turno


class TurnoRepository:
    """Repository for Turno CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        operador_id: str,
        sede_id: str,
        caja_id: str,
        estado: str = "abierto",
        hora_inicio: Optional[datetime] = None,
    ) -> Turno:
        """Create a new turno."""
        turno = Turno(
            id=str(uuid4()),
            tenant_id=tenant_id,
            operador_id=operador_id,
            sede_id=sede_id,
            caja_id=caja_id,
            estado=estado,
            hora_inicio=hora_inicio or datetime.utcnow(),
            total_pasajes=Decimal("0.00"),
            total_recargas=Decimal("0.00"),
            total_otros=Decimal("0.00"),
            total_ingresos=Decimal("0.00"),
            total_aperturas=Decimal("0.00"),
            cantidad_alertas_atendidas=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(turno)
        await self.session.flush()
        return turno

    async def get_by_id(self, turno_id: str, tenant_id: str) -> Optional[Turno]:
        """Get turno by ID."""
        result = await self.session.execute(
            select(Turno).where(Turno.id == turno_id, Turno.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_operador(self, operador_id: str, tenant_id: str) -> Optional[Turno]:
        """Get active (open) turno for an operator."""
        result = await self.session.execute(
            select(Turno).where(
                Turno.operador_id == operador_id,
                Turno.tenant_id == tenant_id,
                Turno.estado == "abierto",
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        turno_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[Turno]:
        """Update a turno record."""
        kwargs["updated_at"] = datetime.utcnow()
        await self.session.execute(
            update(Turno)
            .where(Turno.id == turno_id, Turno.tenant_id == tenant_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(turno_id, tenant_id)

    async def close(
        self,
        turno_id: str,
        tenant_id: str,
        total_pasajes: Decimal,
        total_recargas: Decimal,
        total_otros: Decimal,
        total_ingresos: Decimal,
        total_aperturas: Decimal,
        cantidad_alertas: int = 0,
    ) -> Optional[Turno]:
        """Close a turno with final totals."""
        return await self.update(
            turno_id,
            tenant_id,
            estado="cerrado",
            hora_cierre=datetime.utcnow(),
            total_pasajes=total_pasajes,
            total_recargas=total_recargas,
            total_otros=total_otros,
            total_ingresos=total_ingresos,
            total_aperturas=total_aperturas,
            cantidad_alertas_atendidas=cantidad_alertas,
        )

    async def list_by_sede(
        self,
        sede_id: str,
        tenant_id: str,
        estado: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Turno], int]:
        """List turnos by sede."""
        query = select(Turno).where(Turno.sede_id == sede_id, Turno.tenant_id == tenant_id)
        count_query = select(func.count()).select_from(Turno).where(
            Turno.sede_id == sede_id, Turno.tenant_id == tenant_id
        )
        if estado:
            query = query.where(Turno.estado == estado)
            count_query = count_query.where(Turno.estado == estado)
        query = query.order_by(Turno.hora_inicio.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        return list(result.scalars().all()), total