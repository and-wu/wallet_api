from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.repositories.wallet import WalletRepository
from app.schemas.wallet import OperationType


class WalletNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class WalletService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = WalletRepository(session)

    async def create_wallet(self) -> Wallet:
        async with self.session.begin():
            wallet = await self.repository.create()

        return wallet

    async def get_balance(self, wallet_id: UUID) -> Decimal:
        wallet = await self.repository.get_by_id(wallet_id)

        if wallet is None:
            raise WalletNotFoundError

        return wallet.balance

    async def process_operation(
        self,
        wallet_id: UUID,
        operation_type: OperationType,
        amount: Decimal,
    ) -> Decimal:
        async with self.session.begin():
            wallet = await self.repository.get_by_id_for_update(wallet_id)

            if wallet is None:
                raise WalletNotFoundError

            if operation_type == OperationType.DEPOSIT:
                wallet.balance += amount

            elif operation_type == OperationType.WITHDRAW:
                if wallet.balance < amount:
                    raise InsufficientFundsError

                wallet.balance -= amount

            await self.session.flush()

            return wallet.balance
