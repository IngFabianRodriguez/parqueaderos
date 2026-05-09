"""Payments service business logic."""

from typing import Optional
from decimal import Decimal
import uuid

from app.db.session import AsyncSessionLocal
from app.db.models import Wallet, Transaction, PaymentMethod, Refund


class PaymentsService:
    """Service for payment operations."""

    @staticmethod
    async def get_wallet_by_id(wallet_id: str) -> Optional[Wallet]:
        """Get wallet by ID."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(Wallet).where(Wallet.id == wallet_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_wallets_by_user(user_id: str, tenant_id: str) -> list[Wallet]:
        """Get all wallets for a user in a tenant."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Wallet).where(Wallet.user_id == user_id, Wallet.tenant_id == tenant_id)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create_wallet(tenant_id: str, user_id: str) -> Wallet:
        """Create a new wallet."""
        async with AsyncSessionLocal() as session:
            wallet = Wallet(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                balance=Decimal("0.00"),
            )
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet

    @staticmethod
    async def get_transaction_by_id(transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
            return result.scalar_one_or_none()


payments_service = PaymentsService()