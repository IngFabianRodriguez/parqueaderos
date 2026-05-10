"""Repository for Justificacion operations (RF-171)."""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JustificacionDiferencia


class JustificacionRepository:
    """Repository for JustificacionDiferencia CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        conciliacion_id: str,
        operador_id: str,
        motivo: str,
        descripcion: str,
        evidencia_foto_url: Optional[str] = None,
        evidencia_pendiente: bool = False,
    ) -> JustificacionDiferencia:
        """Create a new justificacion record."""
        justificacion = JustificacionDiferencia(
            id=str(uuid4()),
            tenant_id=tenant_id,
            conciliacion_id=conciliacion_id,
            operador_id=operador_id,
            motivo=motivo,
            descripcion=descripcion,
            evidencia_foto_url=evidencia_foto_url,
            evidencia_pendiente=evidencia_pendiente,
            estado="pendiente_aprobacion",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(justificacion)
        await self.session.flush()
        return justificacion

    async def get_by_id(self, justificacion_id: str, tenant_id: str) -> Optional[JustificacionDiferencia]:
        """Get justificacion by ID."""
        result = await self.session.execute(
            select(JustificacionDiferencia).where(
                JustificacionDiferencia.id == justificacion_id,
                JustificacionDiferencia.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_conciliacion(self, conciliacion_id: str, tenant_id: str) -> Optional[JustificacionDiferencia]:
        """Get justificacion by conciliacion ID."""
        result = await self.session.execute(
            select(JustificacionDiferencia).where(
                JustificacionDiferencia.conciliacion_id == conciliacion_id,
                JustificacionDiferencia.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        justificacion_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[JustificacionDiferencia]:
        """Update a justificacion record."""
        kwargs["updated_at"] = datetime.utcnow()
        await self.session.execute(
            update(JustificacionDiferencia)
            .where(
                JustificacionDiferencia.id == justificacion_id,
                JustificacionDiferencia.tenant_id == tenant_id,
            )
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(justificacion_id, tenant_id)

    async def review(
        self,
        justificacion_id: str,
        tenant_id: str,
        administrador_id: str,
        estado: str,
        comentario_revision: Optional[str] = None,
    ) -> Optional[JustificacionDiferencia]:
        """Review (approve/reject) a justificacion."""
        return await self.update(
            justificacion_id,
            tenant_id,
            estado=estado,
            administrador_revisor=administrador_id,
            fecha_revision=datetime.utcnow(),
            comentario_revision=comentario_revision,
        )

    async def exists_for_turno(self, conciliacion_id: str, tenant_id: str) -> bool:
        """Check if justificacion exists for a conciliacion."""
        result = await self.session.execute(
            select(func.count()).select_from(JustificacionDiferencia).where(
                JustificacionDiferencia.conciliacion_id == conciliacion_id,
                JustificacionDiferencia.tenant_id == tenant_id,
            )
        )
        return (result.scalar() or 0) > 0