"""Invoice business logic service."""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceLineResponse,
)


class InvoiceService:
    """Service for Invoice business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InvoiceRepository(session)

    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique = str(uuid4())[:8].upper()
        return f"INV-{timestamp}-{unique}"

    async def create_invoice(
        self,
        tenant_id: str,
        user_id: str,
        data: InvoiceCreate,
    ) -> InvoiceResponse:
        """Create a new invoice with lines."""
        # Calculate totals
        subtotal = Decimal("0.00")
        tax_amount = Decimal("0.00")
        lines_data = []

        for line_dict in data.lines:
            desc = line_dict.get("description", "")
            qty = Decimal(str(line_dict.get("quantity", "1.00")))
            unit_price = Decimal(str(line_dict.get("unit_price", "0.00")))
            tax_rate = Decimal(str(line_dict.get("tax_rate", "0.00")))
            line_subtotal = qty * unit_price
            line_tax = line_subtotal * (tax_rate / Decimal("100"))
            subtotal += line_subtotal
            tax_amount += line_tax
            lines_data.append({
                "description": desc,
                "quantity": qty,
                "unit_price": unit_price,
                "tax_rate": tax_rate,
            })

        total = subtotal + tax_amount

        invoice = await self.repo.create(
            tenant_id=tenant_id,
            invoice_number=self._generate_invoice_number(),
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            sede_id=data.sede_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
            currency="COP",
            customer_nit=data.customer_nit,
            status="draft",
            due_date=data.due_date,
        )

        # Create lines
        for ld in lines_data:
            await self.repo.create_line(
                invoice_id=invoice.id,
                description=ld["description"],
                unit_price=ld["unit_price"],
                quantity=ld["quantity"],
                tax_rate=ld["tax_rate"],
            )

        return InvoiceResponse(
            id=invoice.id,
            tenant_id=invoice.tenant_id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=invoice.customer_name,
            customer_nit=invoice.customer_nit,
            sede_id=invoice.sede_id,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total=invoice.total,
            currency=invoice.currency,
            status=invoice.status,
            dian_id=invoice.dian_id,
            dian_status=invoice.dian_status,
            issued_at=invoice.issued_at,
            due_date=invoice.due_date,
            paid_at=invoice.paid_at,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )

    async def get_invoice(self, invoice_id: str, tenant_id: str) -> Optional[InvoiceResponse]:
        """Get invoice by ID."""
        invoice = await self.repo.get_by_id(invoice_id, tenant_id)
        if not invoice:
            return None
        return InvoiceResponse(
            id=invoice.id,
            tenant_id=invoice.tenant_id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=invoice.customer_name,
            customer_nit=invoice.customer_nit,
            sede_id=invoice.sede_id,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total=invoice.total,
            currency=invoice.currency,
            status=invoice.status,
            dian_id=invoice.dian_id,
            dian_status=invoice.dian_status,
            issued_at=invoice.issued_at,
            due_date=invoice.due_date,
            paid_at=invoice.paid_at,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )

    async def list_invoices(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        sede_id: Optional[str] = None,
    ) -> InvoiceListResponse:
        """List invoices with pagination."""
        invoices, total = await self.repo.list(
            tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            customer_id=customer_id,
            sede_id=sede_id,
        )
        items = [
            InvoiceResponse(
                id=inv.id,
                tenant_id=inv.tenant_id,
                invoice_number=inv.invoice_number,
                customer_id=inv.customer_id,
                customer_name=inv.customer_name,
                customer_nit=inv.customer_nit,
                sede_id=inv.sede_id,
                subtotal=inv.subtotal,
                tax_amount=inv.tax_amount,
                total=inv.total,
                currency=inv.currency,
                status=inv.status,
                dian_id=inv.dian_id,
                dian_status=inv.dian_status,
                issued_at=inv.issued_at,
                due_date=inv.due_date,
                paid_at=inv.paid_at,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
            for inv in invoices
        ]
        return InvoiceListResponse(items=items, total=total, page=page, page_size=page_size)

    async def issue_to_dian(self, invoice_id: str, tenant_id: str) -> Optional[InvoiceResponse]:
        """Issue invoice to DIAN (electronic invoicing)."""
        invoice = await self.repo.get_by_id(invoice_id, tenant_id)
        if not invoice:
            return None
        # Simulate DIAN issuance - in production would call DIAN API
        updated = await self.repo.update(
            invoice_id,
            tenant_id,
            status="issued",
            dian_id=f"DIAN-{uuid4().hex[:16].upper()}",
            dian_status="accepted",
            issued_at=datetime.utcnow(),
        )
        if not updated:
            return None
        return InvoiceResponse(
            id=updated.id,
            tenant_id=updated.tenant_id,
            invoice_number=updated.invoice_number,
            customer_id=updated.customer_id,
            customer_name=updated.customer_name,
            customer_nit=updated.customer_nit,
            sede_id=updated.sede_id,
            subtotal=updated.subtotal,
            tax_amount=updated.tax_amount,
            total=updated.total,
            currency=updated.currency,
            status=updated.status,
            dian_id=updated.dian_id,
            dian_status=updated.dian_status,
            issued_at=updated.issued_at,
            due_date=updated.due_date,
            paid_at=updated.paid_at,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def cancel_invoice(self, invoice_id: str, tenant_id: str) -> Optional[InvoiceResponse]:
        """Cancel an invoice."""
        invoice = await self.repo.get_by_id(invoice_id, tenant_id)
        if not invoice:
            return None
        if invoice.status == "cancelled":
            return await self.get_invoice(invoice_id, tenant_id)
        updated = await self.repo.update(invoice_id, tenant_id, status="cancelled")
        if not updated:
            return None
        return InvoiceResponse(
            id=updated.id,
            tenant_id=updated.tenant_id,
            invoice_number=updated.invoice_number,
            customer_id=updated.customer_id,
            customer_name=updated.customer_name,
            customer_nit=updated.customer_nit,
            sede_id=updated.sede_id,
            subtotal=updated.subtotal,
            tax_amount=updated.tax_amount,
            total=updated.total,
            currency=updated.currency,
            status=updated.status,
            dian_id=updated.dian_id,
            dian_status=updated.dian_status,
            issued_at=updated.issued_at,
            due_date=updated.due_date,
            paid_at=updated.paid_at,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def get_invoice_lines(self, invoice_id: str, tenant_id: str) -> List[InvoiceLineResponse]:
        """Get invoice lines."""
        invoice = await self.repo.get_by_id(invoice_id, tenant_id)
        if not invoice:
            return []
        lines = await self.repo.get_lines(invoice_id)
        return [
            InvoiceLineResponse(
                id=line.id,
                invoice_id=line.invoice_id,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_rate=line.tax_rate,
                amount=line.amount,
            )
            for line in lines
        ]