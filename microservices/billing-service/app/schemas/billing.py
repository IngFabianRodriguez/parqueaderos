"""Pydantic schemas for billing-service."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# Tariff schemas
class TariffCreate(BaseModel):
    sede_id: str
    name: str = Field(..., min_length=1, max_length=255)
    tariff_type: str = Field(..., min_length=1, max_length=20)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="COP", max_length=3)
    billing_period: Optional[str] = None
    vehicle_type: Optional[str] = None
    valid_from: datetime
    valid_to: Optional[datetime] = None


class TariffResponse(BaseModel):
    id: str
    tenant_id: str
    sede_id: str
    name: str
    tariff_type: str
    amount: Decimal
    currency: str
    billing_period: Optional[str] = None
    vehicle_type: Optional[str] = None
    valid_from: datetime
    valid_to: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TariffListResponse(BaseModel):
    items: list[TariffResponse]
    total: int


# Invoice schemas
class InvoiceCreate(BaseModel):
    customer_id: str
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_nit: Optional[str] = None
    sede_id: str
    lines: list[dict]  # [{"description": "...", "quantity": 1, "unit_price": 1000}]
    due_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    invoice_number: str
    customer_id: str
    customer_name: str
    customer_nit: Optional[str] = None
    sede_id: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    status: str
    dian_id: Optional[str] = None
    dian_status: Optional[str] = None
    issued_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int


class InvoiceLineResponse(BaseModel):
    id: str
    invoice_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    amount: Decimal

    class Config:
        from_attributes = True


# Wallet schemas
class WalletTopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)


class WalletResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    balance: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Morosos schemas
class MorosoResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    customer_name: str
    invoice_id: str
    amount_due: Decimal
    days_overdue: int
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MorosoListResponse(BaseModel):
    items: list[MorosoResponse]
    total: int