import asyncio
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.models.wallet import Wallet
from app.schemas.wallet import OperationType
from app.services.wallet import (
    InsufficientFundsError,
    WalletService,
)


@pytest.mark.asyncio
async def test_create_wallet_in_database(db_session_factory):
    wallet_id = None

    try:
        async with db_session_factory() as session:
            service = WalletService(session)
            wallet = await service.create_wallet()

            wallet_id = wallet.id

            assert wallet.id is not None
            assert wallet.balance == Decimal("0.00")

            result = await session.execute(select(func.count()).select_from(Wallet))

            assert result.scalar_one() >= 1
    finally:
        if wallet_id is not None:
            async with db_session_factory() as session:
                wallet = await session.get(Wallet, wallet_id)

                if wallet is not None:
                    await session.delete(wallet)
                    await session.commit()


@pytest.mark.asyncio
async def test_concurrent_withdrawals_cannot_overdraw(
    db_session_factory,
):
    async with db_session_factory() as session:
        service = WalletService(session)
        wallet = await service.create_wallet()
        wallet.balance = Decimal("100.00")
        wallet_id = wallet.id
        await session.commit()

    async def withdraw():
        async with db_session_factory() as session:
            service = WalletService(session)
            return await service.process_operation(
                wallet_id=wallet_id,
                operation_type=OperationType.WITHDRAW,
                amount=Decimal("70.00"),
            )

    try:
        results = await asyncio.gather(
            withdraw(),
            withdraw(),
            return_exceptions=True,
        )

        successes = [result for result in results if isinstance(result, Decimal)]
        failures = [
            result for result in results if isinstance(result, InsufficientFundsError)
        ]

        assert len(successes) == 1
        assert len(failures) == 1

        async with db_session_factory() as session:
            service = WalletService(session)
            balance = await service.get_balance(wallet_id)

        assert balance == Decimal("30.00")

    finally:
        async with db_session_factory() as session:
            wallet = await session.get(Wallet, wallet_id)

            if wallet is not None:
                await session.delete(wallet)
                await session.commit()
