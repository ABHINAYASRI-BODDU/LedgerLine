
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.account import Account
from app.models.transaction import Transaction
from app.database import get_db
from app.dependencies.permissions import get_current_user
from app.models.user import User
from app.schemas.transaction import (
    DepositRequest,
    WithdrawalRequest,
    TransferRequest,
    TransactionResponse
)
from app.services.account_service import get_account_by_id
from app.services.ledger_service import (
    record_deposit,
    record_withdrawal,
    record_transfer
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post(
    "/deposit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def deposit_money(
    deposit_data: DepositRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = get_account_by_id(
        db=db,
        account_id=deposit_data.account_id,
        current_user=current_user
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    try:
        transaction = record_deposit(
            db=db,
            account=account,
            amount_paise=deposit_data.amount_paise,
            initiated_by=current_user.id,
            idempotency_key=deposit_data.idempotency_key
        )

        return transaction

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post(
    "/withdraw",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def withdraw_money(
    withdrawal_data: WithdrawalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = get_account_by_id(
        db=db,
        account_id=withdrawal_data.account_id,
        current_user=current_user
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    try:
        transaction = record_withdrawal(
            db=db,
            account=account,
            amount_paise=withdrawal_data.amount_paise,
            initiated_by=current_user.id,
            idempotency_key=withdrawal_data.idempotency_key
        )

        return transaction

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post(
    "/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def transfer_money(
    transfer_data: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    source_account = get_account_by_id(
        db=db,
        account_id=transfer_data.source_account_id,
        current_user=current_user
    )

    if source_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )

    destination_account = get_account_by_id(
        db=db,
        account_id=transfer_data.destination_account_id,
        current_user=current_user
    )

    if destination_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )

    try:
        transaction = record_transfer(
            db=db,
            source_account=source_account,
            destination_account=destination_account,
            amount_paise=transfer_data.amount_paise,
            initiated_by=current_user.id,
            idempotency_key=transfer_data.idempotency_key
        )

        return transaction

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.get(
    "/history",
    response_model=list[TransactionResponse]
)
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_account_ids = db.query(Account.id).filter(
        Account.user_id == current_user.id
    ).subquery()

    transactions = db.query(Transaction).filter(
        or_(
            Transaction.source_account_id.in_(user_account_ids),
            Transaction.destination_account_id.in_(user_account_ids)
        )
    ).order_by(
        Transaction.created_at.desc()
    ).all()

    return transactions
