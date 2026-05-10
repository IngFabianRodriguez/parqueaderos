"""Repository for Invoice operations."""

from typing import Optional, List
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Invoice, InvoiceLine


class InvoiceRepository:
    """Repository for Invoice CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        tenant_id: str,
        invoice_number: str,
        customer_id: str,
        customer_name: str,
        sede_id: str,
        subtotal: Decimal,
        tax_amount: Decimal,
        total: Decimal,
        currency: str = "COP",
        customer_nit: Optional[str] = None,
        status: str = "draft",
        due_date: Optional[datetime] = None,
    ) -> Invoice:
        """Create a new invoice."""
        invoice = Invoice(
            id=str(uuid4()),
            tenant_id=tenant_id,
            invoice_number=invoice_number,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_nit=customer_nit,
            sede_id=sede_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
            currency=currency,
            status=status,
            due_date=due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(invoice)
        await self.session.flush()
        return invoice

    async def create_line(
        self,
        invoice_id: str,
        description: str,
        unit_price: Decimal,
        quantity: Decimal = Decimal("1.00"),
        tax_rate: Decimal = Decimal("0.00"),
    ) -> InvoiceLine:
        """Create an invoice line."""
        amount = quantity * unit_price
        line = InvoiceLine(
            id=str(uuid4()),
            invoice_id=invoice_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate,
            amount=amount,
            created_at=datetime.utcnow(),
        )
        self.session.add(line)
        await self.session.flush()
        return line

    async def get_by_id(self, invoice_id: str, tenant_id: str) -> Optional[Invoice]:
        """Get invoice by ID."""
        result = await self.session.execute(
            select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, invoice_number: str, tenant_id: str) -> Optional[Invoice]:
        """Get invoice by number."""
        result = await self.session.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_number, Invoice.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        sede_id: Optional[str] = None,
    ) -> tuple[List[Invoice], int]:
        """List invoices with pagination."""
        query = select(Invoice).where(Invoice.tenant_id == tenant_id)
        count_query = select(func.count()).select_from(Invoice).where(Invoice.tenant_id == tenant_id)

        if status:
            query = query.where(Invoice.status == status)
            count_query = count_query.where(Invoice.status == status)
        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)
            count_query = count_query.where(Invoice.customer_id == customer_id)
        if sede_id:
            query = query.where(Invoice.sede_id == sede_id)
            count_query = count_query.where(Invoice.sede_id == sede_id)

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return list(result.scalars().all()), total

    async def update(self, invoice_id: str, tenant_id: str, **kwargs) -> Optional[Invoice]:
        """Update an invoice."""
        kwargs["updated_at"] = datetime.utcnow()
        await self.session.execute(
            update(Invoice)
            .where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(invoice_id, tenant_id)

    async def get_lines(self, invoice_id: str) -> List[InvoiceLine]:
        """Get invoice lines."""
        result = await self.session.execute(
            select(InvoiceLine).where(InvoiceLine.invoice_id == invoice_id)
        )
        return list(result.scalars().all())