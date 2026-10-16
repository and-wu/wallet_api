from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.wallet import WalletOperationRequest, WalletResponse
from app.services.wallet import (
    InsufficientFundsError,
    WalletNotFoundError,
    WalletService,
)

router = APIRouter(prefix="/api/v1/wallets", tags=["Wallets"])


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    service = WalletService(session)
    wallet = await service.create_wallet()

    return WalletResponse(
        id=wallet.id,
        balance=wallet.balance,
    )


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    service = WalletService(session)

    try:
        balance = await service.get_balance(wallet_id)
    except WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return WalletResponse(id=wallet_id, balance=balance)


@router.post("/{wallet_id}/operation", response_model=WalletResponse)
async def process_wallet_operation(
    wallet_id: UUID,
    operation: WalletOperationRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
):
    service = WalletService(session)

    try:
        balance = await service.process_operation(
            wallet_id=wallet_id,
            operation_type=operation.operation_type,
            amount=operation.amount,
        )
    except WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    except InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )

    return WalletResponse(id=wallet_id, balance=balance)
