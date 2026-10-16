import os
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import get_session
from app.main import app
from app.services.wallet import WalletService


@pytest.fixture
def service():
    repository = AsyncMock()
    repository.get_by_id.return_value = None
    repository.get_by_id_for_update.return_value = None

    wallet_service = WalletService.__new__(WalletService)
    wallet_service.session = AsyncMock()
    wallet_service.repository = repository

    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=None)
    transaction.__aexit__ = AsyncMock(return_value=False)

    wallet_service.session.begin = MagicMock(return_value=transaction)

    return wallet_service


@pytest_asyncio.fixture
async def db_session():
    database_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:password@127.0.0.1:5433/wallet_test_db",
    )

    engine = create_async_engine(database_url)

    async with engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session

        await transaction.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_factory():
    database_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:password@127.0.0.1:5433/wallet_test_db",
    )

    engine = create_async_engine(database_url)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield session_factory

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session_factory):
    async def override_get_session():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)
