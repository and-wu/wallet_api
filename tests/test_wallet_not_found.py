from decimal import Decimal
from uuid import UUID

import pytest

from app.schemas.wallet import OperationType
from app.services.wallet import WalletNotFoundError


@pytest.mark.asyncio
async def test_operation_with_nonexistent_wallet(service):
    # Проверяем обращение к несуществующему кошельку

    with pytest.raises(WalletNotFoundError):
        await service.process_operation(
            wallet_id=UUID("00000000-0000-0000-0000-000000000001"),
            operation_type=OperationType.DEPOSIT,
            amount=Decimal("25.00"),
        )

    service.session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_withdraw_from_nonexistent_wallet(service):
    # Проверяем снятие с несуществующего кошелька

    with pytest.raises(WalletNotFoundError):
        await service.process_operation(
            wallet_id=UUID("00000000-0000-0000-0000-000000000001"),
            operation_type=OperationType.WITHDRAW,
            amount=Decimal("25.00"),
        )

    service.session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_balance_for_nonexistent_wallet(service):
    # теста на получения баланса несуществующего кошелька
    with pytest.raises(WalletNotFoundError):
        await service.get_balance(UUID("00000000-0000-0000-0000-000000000001"))
