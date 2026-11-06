
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    account_type: Literal["savings", "checking"]


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
