"""Pydantic schemas for payments."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class WalletCreate(BaseModel):
    user_id: str


class WalletResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    balance: Decimal
    currency: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WalletTopUpRequest(BaseModel):
    wallet_id: str
    amount: Decimal = Field(..., gt=0)
    payment_method_id: Optional[str] = None


class TransactionCreate(BaseModel):
    wallet_id: str
    type: str
    amount: Decimal = Field(..., gt=0)
    reference: Optional[str] = None
    description: Optional[str] = None
    sede_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    tenant_id: str
    wallet_id: str
    type: str
    amount: Decimal
    currency: str
    status: str
    reference: Optional[str]
    description: Optional[str]
    sede_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentMethodCreate(BaseModel):
    type: str
    provider: Optional[str] = None
    token: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    type: str
    provider: Optional[str]
    last_four: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    transaction_id: str
    amount: Optional[Decimal] = None
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: str
    tenant_id: str
    transaction_id: str
    amount: Decimal
    reason: Optional[str]
    status: str
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True