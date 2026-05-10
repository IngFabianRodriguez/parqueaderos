"""Repository for NotificacionCierre operations (RF-174)."""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NotificacionCierre


class NotificacionCierreRepository:
    """Repository for NotificacionCierre CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        turno_id: str,
        operador_id: str,
        administrador_id: str,
        sede_id: str,
        canales_utilizados: Optional[str] = None,
        estado_envio: str = "pendiente",
        contenido_json: Optional[str] = None,
        timestamp_envio: Optional[datetime] = None,
    ) -> NotificacionCierre:
        """Create a new notificacion cierre."""
        notificacion = NotificacionCierre(
            id=str(uuid4()),
            tenant_id=tenant_id,
            turno_id=turno_id,
            operador_id=operador_id,
            administrador_id=administrador_id,
            sede_id=sede_id,
            canales_utilizados=canales_utilizados,
            estado_envio=estado_envio,
            contenido_json=contenido_json,
            timestamp_envio=timestamp_envio,
            created_at=datetime.utcnow(),
        )
        self.session.add(notificacion)
        await self.session.flush()
        return notificacion

    async def get_by_id(self, notificacion_id: str, tenant_id: str) -> Optional[NotificacionCierre]:
        """Get notificacion cierre by ID."""
        result = await self.session.execute(
            select(NotificacionCierre).where(
                NotificacionCierre.id == notificacion_id,
                NotificacionCierre.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_sede(
        self,
        sede_id: str,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[NotificacionCierre], int]:
        """List notificaciones by sede."""
        query = select(NotificacionCierre).where(
            NotificacionCierre.sede_id == sede_id,
            NotificacionCierre.tenant_id == tenant_id,
        ).order_by(NotificacionCierre.created_at.desc())
        count_query = select(func.count()).select_from(NotificacionCierre).where(
            NotificacionCierre.sede_id == sede_id,
            NotificacionCierre.tenant_id == tenant_id,
        )
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        return list(result.scalars().all()), total

    async def update_estado(
        self,
        notificacion_id: str,
        tenant_id: str,
        estado_envio: str,
        timestamp_envio: Optional[datetime] = None,
    ) -> Optional[NotificacionCierre]:
        """Update estado of notificacion."""
        await self.session.execute(
            update(NotificacionCierre)
            .where(
                NotificacionCierre.id == notificacion_id,
                NotificacionCierre.tenant_id == tenant_id,
            )
            .values(
                estado_envio=estado_envio,
                timestamp_envio=timestamp_envio or datetime.utcnow(),
            )
        )
        await self.session.flush()
        return await self.get_by_id(notificacion_id, tenant_id)