"""Payments API v1 endpoints.

TODO(RF-010): Implement payment endpoints:
  - GET /wallets - List user wallets
  - POST /wallets - Create wallet
  - GET /wallets/{wallet_id} - Get wallet details
  - POST /wallets/{wallet_id}/topup - Top up wallet
  - GET /transactions - List transactions
  - POST /transactions - Create transaction
  - GET /transactions/{transaction_id} - Get transaction
  - GET /payment-methods - List payment methods
  - POST /payment-methods - Add payment method
  - DELETE /payment-methods/{id} - Remove payment method
  - GET /refunds - List refunds
  - POST /refunds - Create refund
"""

from fastapi import APIRouter, Depends, Header
from typing import Optional

from app.core.security import validate_gateway_headers
from app.schemas.payments import (
    WalletCreate, WalletResponse, WalletTopUpRequest,
    TransactionCreate, TransactionResponse,
    PaymentMethodCreate, PaymentMethodResponse,
    RefundRequest, RefundResponse,
)

router = APIRouter(tags=["payments"])


@router.get("/wallets", response_model=list[WalletResponse])
async def list_wallets(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List user wallets.

    TODO(RF-010): Implement wallet listing with pagination.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_wallets")


@router.post("/wallets", response_model=WalletResponse, status_code=201)
async def create_wallet(
    wallet_data: WalletCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create a new wallet.

    TODO(RF-010): Implement wallet creation.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement create_wallet")


@router.get("/wallets/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get wallet by ID.

    TODO(RF-010): Implement get wallet.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement get_wallet")


@router.post("/wallets/{wallet_id}/topup", response_model=TransactionResponse)
async def topup_wallet(
    wallet_id: str,
    request: WalletTopUpRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Top up wallet balance.

    TODO(RF-010): Implement wallet top-up.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement topup_wallet")


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    wallet_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List transactions.

    TODO(RF-010): Implement transaction listing with filters.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_transactions")


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction_data: TransactionCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create a new transaction.

    TODO(RF-010): Implement transaction creation.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement create_transaction")


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Get transaction by ID.

    TODO(RF-010): Implement get transaction.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement get_transaction")


@router.get("/payment-methods", response_model=list[PaymentMethodResponse])
async def list_payment_methods(
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List user payment methods.

    TODO(RF-010): Implement payment methods listing.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_payment_methods")


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=201)
async def add_payment_method(
    payment_method_data: PaymentMethodCreate,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Add a new payment method.

    TODO(RF-010): Implement add payment method.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement add_payment_method")


@router.delete("/payment-methods/{payment_method_id}", status_code=204)
async def remove_payment_method(
    payment_method_id: str,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Remove a payment method.

    TODO(RF-010): Implement remove payment method.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement remove_payment_method")


@router.get("/refunds", response_model=list[RefundResponse])
async def list_refunds(
    transaction_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """List refunds.

    TODO(RF-010): Implement refunds listing.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement list_refunds")


@router.post("/refunds", response_model=RefundResponse, status_code=201)
async def create_refund(
    refund_data: RefundRequest,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header(None),
):
    """Create a refund.

    TODO(RF-010): Implement refund creation.
    """
    validate_gateway_headers(x_user_id, x_rol, x_tenant_id)
    raise NotImplementedError("TODO: Implement create_refund")