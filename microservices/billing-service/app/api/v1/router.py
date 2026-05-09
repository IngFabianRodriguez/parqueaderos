"""Billing API v1 endpoints.

TODO(RF-012): Implement tariff endpoints:
  - GET /tariffs - List tariffs
  - POST /tariffs - Create tariff
  - GET /tariffs/{tariff_id} - Get tariff
  - PATCH /tariffs/{tariff_id} - Update tariff
  - DELETE /tariffs/{tariff_id} - Deactivate tariff

TODO(RF-012): Implement invoice endpoints:
  - GET /invoices - List invoices
  - POST /invoices - Create invoice (DIAN)
  - GET /invoices/{invoice_id} - Get invoice
  - POST /invoices/{invoice_id}/issue - Issue to DIAN
  - POST /invoices/{invoice_id}/cancel - Cancel invoice
  - GET /invoices/{invoice_id}/pdf - Download PDF

TODO(RF-012): Implement wallet endpoints:
  - GET /wallet - Get wallet balance
  - POST /wallet/topup - Top up wallet

TODO(RF-012): Implement morosos endpoints:
  - GET /morosos - List delinquent customers
  - POST /morosos/{id}/resolve - Mark as resolved
"""

from fastapi import APIRouter, Depends, Header
from typing import Optional

from app.core.security import validate_gateway_headers
from app.schemas.billing import (
    TariffCreate, TariffResponse, TariffListResponse,
    InvoiceCreate, InvoiceResponse, InvoiceListResponse, InvoiceLineResponse,
    WalletTopUpRequest, WalletResponse,
    MorosoResponse, MorosoListResponse,
)

router = APIRouter(tags=["billing"])


# ─── Tariffs ─────────────────────────────────────────────────────────────────

@router.get("/tariffs", response_model=TariffListResponse)
async def list_tariffs(
    sede_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List tariffs.

    TODO(RF-012): Implement tariff listing.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_tariffs")


@router.post("/tariffs", response_model=TariffResponse, status_code=201)
async def create_tariff(
    tariff_data: TariffCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create a new tariff.

    TODO(RF-012): Implement tariff creation.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement create_tariff")


@router.get("/tariffs/{tariff_id}", response_model=TariffResponse)
async def get_tariff(
    tariff_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get tariff by ID.

    TODO(RF-012): Implement get tariff.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement get_tariff")


@router.patch("/tariffs/{tariff_id}", response_model=TariffResponse)
async def update_tariff(
    tariff_id: str,
    tariff_data: TariffCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Update a tariff.

    TODO(RF-012): Implement tariff update.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement update_tariff")


@router.delete("/tariffs/{tariff_id}", status_code=204)
async def deactivate_tariff(
    tariff_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Deactivate a tariff.

    TODO(RF-012): Implement deactivate tariff.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement deactivate_tariff")


# ─── Invoices ─────────────────────────────────────────────────────────────────

@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    sede_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List invoices.

    TODO(RF-012): Implement invoice listing.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_invoices")


@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    invoice_data: InvoiceCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create and optionally issue invoice to DIAN.

    TODO(RF-012): Implement invoice creation with DIAN integration.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement create_invoice")


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get invoice by ID.

    TODO(RF-012): Implement get invoice.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement get_invoice")


@router.post("/invoices/{invoice_id}/issue", response_model=InvoiceResponse)
async def issue_invoice(
    invoice_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Issue invoice to DIAN for electronic invoicing.

    TODO(RF-012): Implement DIAN issuance.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement issue_invoice")


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Cancel an invoice.

    TODO(RF-012): Implement invoice cancellation.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement cancel_invoice")


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Download invoice PDF.

    TODO(RF-012): Implement PDF download.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement download_invoice_pdf")


# ─── Wallet ───────────────────────────────────────────────────────────────────

@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get wallet balance.

    TODO(RF-012): Implement get wallet.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement get_wallet")


@router.post("/wallet/topup", response_model=WalletResponse)
async def topup_wallet(
    request: WalletTopUpRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Top up wallet balance.

    TODO(RF-012): Implement wallet top-up.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement topup_wallet")


# ─── Morosos ───────────────────────────────────────────────────────────────────

@router.get("/morosos", response_model=MorosoListResponse)
async def list_morosos(
    page: int = 1,
    page_size: int = 20,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List delinquent customers (morosos).

    TODO(RF-012): Implement morosos listing.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_morosos")


@router.post("/morosos/{moroso_id}/resolve", response_model=MorosoResponse)
async def resolve_moroso(
    moroso_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Mark moroso as resolved (paid).

    TODO(RF-012): Implement resolve moroso.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement resolve_moroso")