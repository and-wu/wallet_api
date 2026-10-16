from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.schemas.wallet import OperationType
from app.services.wallet import InsufficientFundsError, WalletService


@pytest.fixture
def service_and_wallet():
    # Создаём фейковый кошелёк
    wallet = type(
        "FakeWallet",
        (),
        {"balance": Decimal("100.00")},
    )()

    # Создаём фейковый репозиторий
    repository = AsyncMock()
    repository.get_by_id_for_update.return_value = wallet

    # Создаём сервис без настоящей базы данных
    service = WalletService.__new__(WalletService)
    service.session = AsyncMock()
    service.repository = repository

    # Имитируем начало транзакции
    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=None)
    transaction.__aexit__ = AsyncMock(return_value=False)
    service.session.begin = MagicMock(return_value=transaction)

    return service, wallet


@pytest.mark.asyncio
async def test_withdraw_with_insufficient_funds(service_and_wallet):
    # Проверяем, что списание большей суммы вызывает ошибку
    service, wallet = service_and_wallet
    wallet.balance = Decimal("50.00")

    with pytest.raises(InsufficientFundsError):
        await service.process_operation(
            wallet_id=UUID("00000000-0000-0000-0000-000000000001"),
            operation_type=OperationType.WITHDRAW,
            amount=Decimal("100.00"),
        )

    # Баланс не должен измениться.
    assert wallet.balance == Decimal("50.00")


@pytest.mark.asyncio
async def test_withdraw_successfully(service_and_wallet):
    # Проверяем успешное списание денег с кошелька
    service, wallet = service_and_wallet

    result = await service.process_operation(
        wallet_id=UUID("00000000-0000-0000-0000-000000000001"),
        operation_type=OperationType.WITHDRAW,
        amount=Decimal("30.00"),
    )

    assert result == Decimal("70.00")
    assert wallet.balance == Decimal("70.00")
    service.session.flush.assert_awaited_once()
    service.repository.get_by_id_for_update.assert_awaited_once_with(
        UUID("00000000-0000-0000-0000-000000000001")
    )
    service.session.begin.assert_called_once_with()


@pytest.mark.asyncio
async def test_deposit_successfully(service_and_wallet):
    # Проверяем успешное пополнение кошелька
    service, wallet = service_and_wallet

    result = await service.process_operation(
        wallet_id=UUID("00000000-0000-0000-0000-000000000001"),
        operation_type=OperationType.DEPOSIT,
        amount=Decimal("25.50"),
    )

    assert result == Decimal("125.50")
    assert wallet.balance == Decimal("125.50")
    service.session.flush.assert_awaited_once()
    service.repository.get_by_id_for_update.assert_awaited_once_with(
        UUID("00000000-0000-0000-0000-000000000001")
    )
