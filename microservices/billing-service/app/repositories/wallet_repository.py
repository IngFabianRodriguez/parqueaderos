"""Repository for Wallet operations."""

from typing import Optional
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Wallet


class WalletRepository:
    """Repository for Wallet CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(self, user_id: str, tenant_id: str) -> Optional[Wallet]:
        """Get wallet by user ID."""
        result = await self.session.execute(
            select(Wallet).where(Wallet.user_id == user_id, Wallet.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: str,
        user_id: str,
        balance: Decimal = Decimal("0.00"),
        currency: str = "COP",
    ) -> Wallet:
        """Create a new wallet."""
        wallet = Wallet(
            id=str(uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            balance=balance,
            currency=currency,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(wallet)
        await self.session.flush()
        return wallet

    async def topup(self, wallet_id: str, amount: Decimal) -> Optional[Wallet]:
        """Add funds to wallet."""
        await self.session.execute(
            update(Wallet)
            .where(Wallet.id == wallet_id)
            .values(
                balance=Wallet.balance + amount,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.flush()
        result = await self.session.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str, tenant_id: str) -> Wallet:
        """Get existing wallet or create new one."""
        wallet = await self.get_by_user(user_id, tenant_id)
        if wallet is None:
            wallet = await self.create(tenant_id, user_id)
        return wallet

    async def update_balance(self, wallet_id: str, new_balance: Decimal) -> Optional[Wallet]:
        """Set wallet balance to specific value."""
        await self.session.execute(
            update(Wallet)
            .where(Wallet.id == wallet_id)
            .values(balance=new_balance, updated_at=datetime.utcnow())
        )
        await self.session.flush()
        result = await self.session.execute(select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()