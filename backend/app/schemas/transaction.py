from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DepositRequest(BaseModel):
    account_id: int = Field(gt=0)
    amount_paise: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=100)
class WithdrawalRequest(BaseModel):
    account_id: int = Field(gt=0)
    amount_paise: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=100)
class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount_paise: int
    source_account_id: int | None
    destination_account_id: int | None
    initiated_by: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
class TransferRequest(BaseModel):
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)
    amount_paise: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=100)