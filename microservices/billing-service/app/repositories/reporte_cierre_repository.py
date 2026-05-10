"""Repository for ReporteCierre operations (RF-173)."""

from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReporteCierre


class ReporteCierreRepository:
    """Repository for ReporteCierre CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        turno_id: str,
        operador_id: str,
        sede_id: str,
        pdf_url: Optional[str] = None,
        hash_documento: Optional[str] = None,
        firma_digital: Optional[str] = None,
        resumen_json: Optional[str] = None,
        generado_ok: bool = True,
    ) -> ReporteCierre:
        """Create a new reporte cierre."""
        reporte = ReporteCierre(
            id=str(uuid4()),
            tenant_id=tenant_id,
            turno_id=turno_id,
            operador_id=operador_id,
            sede_id=sede_id,
            pdf_url=pdf_url,
            hash_documento=hash_documento,
            firma_digital=firma_digital,
            resumen_json=resumen_json,
            generado_ok=generado_ok,
            created_at=datetime.utcnow(),
        )
        self.session.add(reporte)
        await self.session.flush()
        return reporte

    async def get_by_id(self, reporte_id: str, tenant_id: str) -> Optional[ReporteCierre]:
        """Get reporte cierre by ID."""
        result = await self.session.execute(
            select(ReporteCierre).where(
                ReporteCierre.id == reporte_id, ReporteCierre.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_turno(self, turno_id: str, tenant_id: str) -> Optional[ReporteCierre]:
        """Get reporte cierre by turno ID."""
        result = await self.session.execute(
            select(ReporteCierre).where(
                ReporteCierre.turno_id == turno_id, ReporteCierre.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        reporte_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[ReporteCierre]:
        """Update a reporte cierre record."""
        await self.session.execute(
            update(ReporteCierre)
            .where(ReporteCierre.id == reporte_id, ReporteCierre.tenant_id == tenant_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(reporte_id, tenant_id)