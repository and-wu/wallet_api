from uuid import UUID

import pytest
from httpx import AsyncClient


# Вспомогательная функция для создания кошелька через API.
# Возвращает JSON с id и начальным балансом.
async def create_wallet(client: AsyncClient) -> dict:
    response = await client.post("/api/v1/wallets")

    assert response.status_code == 201
    return response.json()


# Вспомогательная функция для выполнения операции с кошельком.
# Принимает ID кошелька, тип операции и сумму.
async def make_operation(
    client: AsyncClient,
    wallet_id: str,
    operation_type: str,
    amount: str,
):
    return await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={
            "operation_type": operation_type,
            "amount": amount,
        },
    )


# Проверяем создание кошелька и его начальный баланс.
@pytest.mark.asyncio
async def test_create_wallet(client: AsyncClient):
    data = await create_wallet(client)

    assert UUID(data["id"])
    assert data["balance"] == "0.00"


# Проверяем получение баланса созданного кошелька.
@pytest.mark.asyncio
async def test_get_wallet_balance(client: AsyncClient):
    wallet = await create_wallet(client)

    response = await client.get(f"/api/v1/wallets/{wallet['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "id": wallet["id"],
        "balance": "0.00",
    }


# Проверяем пополнение кошелька.
@pytest.mark.asyncio
async def test_deposit_via_api(client: AsyncClient):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "DEPOSIT",
        "150.50",
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "150.50"


# Проверяем снятие средств с достаточным балансом.
@pytest.mark.asyncio
async def test_withdraw_via_api(client: AsyncClient):
    wallet = await create_wallet(client)

    deposit_response = await make_operation(
        client,
        wallet["id"],
        "DEPOSIT",
        "200.00",
    )
    assert deposit_response.status_code == 200

    response = await make_operation(
        client,
        wallet["id"],
        "WITHDRAW",
        "75.50",
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "124.50"


# Проверяем отказ при снятии суммы, превышающей баланс.
# После ошибки баланс должен остаться неизменным.
@pytest.mark.asyncio
async def test_withdraw_with_insufficient_funds(
    client: AsyncClient,
):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "WITHDRAW",
        "50.00",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

    balance_response = await client.get(f"/api/v1/wallets/{wallet['id']}")

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == "0.00"


# Проверяем получение несуществующего кошелька.
@pytest.mark.asyncio
async def test_get_nonexistent_wallet(client: AsyncClient):
    wallet_id = str(UUID("00000000-0000-0000-0000-000000000001"))

    response = await client.get(f"/api/v1/wallets/{wallet_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


# Проверяем пополнение несуществующего кошелька.
@pytest.mark.asyncio
async def test_deposit_to_nonexistent_wallet(
    client: AsyncClient,
):
    wallet_id = str(UUID("00000000-0000-0000-0000-000000000001"))

    response = await make_operation(
        client,
        wallet_id,
        "DEPOSIT",
        "10.00",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


# Проверяем снятие с несуществующего кошелька.
@pytest.mark.asyncio
async def test_withdraw_from_nonexistent_wallet(
    client: AsyncClient,
):
    wallet_id = str(UUID("00000000-0000-0000-0000-000000000001"))

    response = await make_operation(
        client,
        wallet_id,
        "WITHDRAW",
        "10.00",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


# Проверяем отклонение некорректного UUID.
@pytest.mark.asyncio
async def test_get_wallet_with_invalid_uuid(
    client: AsyncClient,
):
    response = await client.get("/api/v1/wallets/not-a-uuid")

    assert response.status_code == 422


# Проверяем отклонение нулевой суммы.
@pytest.mark.asyncio
async def test_operation_with_zero_amount(
    client: AsyncClient,
):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "DEPOSIT",
        "0.00",
    )

    assert response.status_code == 422


# Проверяем отклонение отрицательной суммы.
@pytest.mark.asyncio
async def test_operation_with_negative_amount(
    client: AsyncClient,
):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "DEPOSIT",
        "-10.00",
    )

    assert response.status_code == 422


# Проверяем отклонение суммы с более чем двумя десятичными знаками.
@pytest.mark.asyncio
async def test_operation_with_too_many_decimal_places(
    client: AsyncClient,
):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "DEPOSIT",
        "10.123",
    )

    assert response.status_code == 422


# Проверяем отклонение неизвестного типа операции.
@pytest.mark.asyncio
async def test_operation_with_invalid_type(
    client: AsyncClient,
):
    wallet = await create_wallet(client)

    response = await make_operation(
        client,
        wallet["id"],
        "TRANSFER",
        "10.00",
    )

    assert response.status_code == 422
