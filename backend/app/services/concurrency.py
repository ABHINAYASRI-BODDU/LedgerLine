from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.account import Account


def lock_accounts_for_money_movement(
    db: Session,
    account_ids: list[int]
) -> dict[int, Account]:
    """
    Acquire database locks before checking balances.

    SQLite:
        Uses BEGIN IMMEDIATE to reserve the write transaction.

    PostgreSQL:
        Uses SELECT FOR UPDATE to lock account rows.
    """

    unique_ids = sorted(set(account_ids))

    if not unique_ids:
        raise ValueError("At least one account is required.")

    dialect = db.get_bind().dialect.name

    if dialect == "sqlite":
        # End the earlier read transaction.
        db.rollback()

        # Acquire the SQLite write reservation.
        db.execute(text("BEGIN IMMEDIATE"))

        accounts = (
            db.query(Account)
            .filter(Account.id.in_(unique_ids))
            .order_by(Account.id.asc())
            .all()
        )

    elif dialect == "postgresql":
        # Lock account rows in a consistent order.
        accounts = (
            db.query(Account)
            .filter(Account.id.in_(unique_ids))
            .order_by(Account.id.asc())
            .with_for_update()
            .all()
        )

    else:
        raise RuntimeError(
            f"Unsupported database dialect: {dialect}"
        )

    account_map = {
        account.id: account
        for account in accounts
    }

    if len(account_map) != len(unique_ids):
        raise ValueError("One or more accounts were not found.")

    return account_map