
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.services.ledger_service import get_account_balance
from app.database import get_db
from app.dependencies.permissions import get_current_user, require_role
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import (
    create_account,
    get_user_accounts,
    get_account_by_id,
    update_account_status
)

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_account(
        db=db,
        account_data=account_data,
        current_user=current_user
    )


@router.get(
    "/",
    response_model=list[AccountResponse]
)
def list_my_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_accounts(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{account_id}",
    response_model=AccountResponse
)
def get_my_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = get_account_by_id(
        db=db,
        account_id=account_id,
        current_user=current_user
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    return account


@router.patch(
    "/{account_id}/status",
    response_model=AccountResponse
)
def change_account_status(
    account_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    if new_status not in ["active", "frozen", "closed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account status"
        )

    return update_account_status(
        db=db,
        account_id=account_id,
        new_status=new_status
    )
@router.get("/{account_id}/balance")
def get_my_account_balance(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = get_account_by_id(
        db=db,
        account_id=account_id,
        current_user=current_user
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    balance_paise = get_account_balance(db, account)

    return {
        "account_id": account.id,
        "balance_paise": balance_paise,
        "balance": balance_paise / 100,
        "currency": account.currency
    }