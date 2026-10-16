from decimal import Decimal
from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_get_balance_successfully(service):
    # тест успешного получения баланса
    wallet = type(
        "FakeWallet",
        (),
        {"balance": Decimal("125.50")},
    )()

    service.repository.get_by_id.return_value = wallet

    result = await service.get_balance(UUID("00000000-0000-0000-0000-000000000001"))

    assert result == Decimal("125.50")
    service.repository.get_by_id.assert_awaited_once()
