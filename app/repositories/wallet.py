from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self) -> Wallet:
        wallet = Wallet()

        self.session.add(wallet)

        await self.session.flush()

        return wallet

    async def get_by_id(self, wallet_id: UUID) -> Wallet | None:
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )

        return result.scalar_one_or_none()

    async def get_by_id_for_update(
        self,
        wallet_id: UUID,
    ) -> Wallet | None:
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        )
        return result.scalar_one_or_none()
