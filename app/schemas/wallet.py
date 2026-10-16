from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class WalletOperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)

class WalletResponse(BaseModel):
    id:UUID
    balance: Decimal
