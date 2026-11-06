from fastapi import HTTPException, status
import secrets

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate


def generate_account_number(db: Session) -> str:
    while True:
        # Generate a random 10-digit account number.
        number = f"LL{secrets.randbelow(10**10):010d}"

        # Check whether this account number already exists.
        existing_account = (
            db.query(Account)
            .filter(Account.account_number == number)
            .first()
        )

        # Return the number if it is unique.
        if existing_account is None:
            return number


def create_account(
    db: Session,
    account_data: AccountCreate,
    current_user: User
) -> Account:

    new_account = Account(
        account_number=generate_account_number(db),
        user_id=current_user.id,
        account_type=account_data.account_type,
        currency="INR",
        status="active"
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account

def get_user_accounts(
    db: Session,
    current_user: User
) -> list[Account]:

    accounts = (
        db.query(Account)
        .filter(Account.user_id == current_user.id)
        .order_by(Account.id.asc())
        .all()
    )

    return accounts

def get_account_by_id(
    db: Session,
    account_id: int,
    current_user: User
) -> Account | None:

    account = (
        db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == current_user.id
        )
        .first()
    )

    return account
def update_account_status(
    db: Session,
    account_id: int,
    new_status: str
) -> Account:

    account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    if account.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Closed accounts cannot be modified"
        )

    account.status = new_status

    db.commit()
    db.refresh(account)

    return account