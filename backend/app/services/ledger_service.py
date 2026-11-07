from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry

def create_system_ledger_accounts(db: Session):
    system_accounts = [
        {
            "code": "SYS_CASH",
            "name": "System Cash Account",
            "category": "asset",
        }
    ]

    for account_data in system_accounts:
        existing_account = (
            db.query(LedgerAccount)
            .filter(LedgerAccount.code == account_data["code"])
            .first()
        )

        if existing_account is None:
            ledger_account = LedgerAccount(
                **account_data,
                account_id=None,
                is_system=True,
            )
            db.add(ledger_account)

    db.commit()
def get_or_create_customer_ledger_account(db: Session, account):
    existing_ledger_account = (
        db.query(LedgerAccount)
        .filter(LedgerAccount.account_id == account.id)
        .first()
    )

    if existing_ledger_account:
        return existing_ledger_account

    ledger_account = LedgerAccount(
        code=f"CUSTOMER_{account.id}",
        name=f"Customer Account {account.id}",
        category="liability",
        account_id=account.id,
        is_system=False,
    )

    db.add(ledger_account)
    db.flush()

    return ledger_account
def record_deposit(
    db: Session,
    account,
    amount_paise: int,
    initiated_by: int
):
    if amount_paise <= 0:
        raise ValueError("Deposit amount must be positive.")

    if account.status != "active":
        raise ValueError("Deposits are allowed only for active accounts.")

    try:
        # Find the system cash ledger account
        cash_ledger = (
            db.query(LedgerAccount)
            .filter(LedgerAccount.code == "SYS_CASH")
            .first()
        )

        if cash_ledger is None:
            raise ValueError("System cash ledger account not found.")

        # Get or create the customer's ledger account
        customer_ledger = get_or_create_customer_ledger_account(
            db, account
        )

        # Create the transaction
        transaction = Transaction(
            transaction_type="deposit",
            amount_paise=amount_paise,
            source_account_id=None,
            destination_account_id=account.id,
            initiated_by=initiated_by,
            status="pending",
        )

        db.add(transaction)
        db.flush()

        # Debit the system cash account
        debit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=cash_ledger.id,
            entry_type="debit",
            amount_paise=amount_paise,
        )

        # Credit the customer's liability account
        credit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=customer_ledger.id,
            entry_type="credit",
            amount_paise=amount_paise,
        )

        db.add_all([debit_entry, credit_entry])

        transaction.status = "posted"

        db.commit()

        return transaction

    except Exception:
        db.rollback()
        raise
def get_account_balance(db: Session, account):
    customer_ledger = (
        db.query(LedgerAccount)
        .filter(LedgerAccount.account_id == account.id)
        .first()
    )

    if customer_ledger is None:
        return 0

    credits = (
        db.query(func.sum(LedgerEntry.amount_paise))
        .filter(
            LedgerEntry.ledger_account_id == customer_ledger.id,
            LedgerEntry.entry_type == "credit"
        )
        .scalar() or 0
    )

    debits = (
        db.query(func.sum(LedgerEntry.amount_paise))
        .filter(
            LedgerEntry.ledger_account_id == customer_ledger.id,
            LedgerEntry.entry_type == "debit"
        )
        .scalar() or 0
    )

    return credits - debits    
def record_withdrawal(
    db: Session,
    account,
    amount_paise: int,
    initiated_by: int
):
    if amount_paise <= 0:
        raise ValueError("Withdrawal amount must be positive.")

    if account.status != "active":
        raise ValueError("Withdrawals are allowed only for active accounts.")

    try:
        cash_ledger = (
            db.query(LedgerAccount)
            .filter(LedgerAccount.code == "SYS_CASH")
            .first()
        )

        if cash_ledger is None:
            raise ValueError("System cash ledger account not found.")

        customer_ledger = get_or_create_customer_ledger_account(
            db, account
        )

        current_balance = get_account_balance(db, account)

        if amount_paise > current_balance:
            raise ValueError("Insufficient balance.")

        transaction = Transaction(
            transaction_type="withdrawal",
            amount_paise=amount_paise,
            source_account_id=account.id,
            destination_account_id=None,
            initiated_by=initiated_by,
            status="pending",
        )

        db.add(transaction)
        db.flush()

        debit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=customer_ledger.id,
            entry_type="debit",
            amount_paise=amount_paise,
        )

        credit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=cash_ledger.id,
            entry_type="credit",
            amount_paise=amount_paise,
        )

        db.add_all([debit_entry, credit_entry])

        transaction.status = "posted"

        db.commit()

        return transaction

    except Exception:
        db.rollback()
        raise   
def record_transfer(
    db: Session,
    source_account,
    destination_account,
    amount_paise: int,
    initiated_by: int
):
    if amount_paise <= 0:
        raise ValueError("Transfer amount must be positive.")

    if source_account.id == destination_account.id:
        raise ValueError("Cannot transfer to the same account.")

    if source_account.status != "active":
        raise ValueError("Source account must be active.")

    if destination_account.status != "active":
        raise ValueError("Destination account must be active.")

    try:
        current_balance = get_account_balance(db, source_account)

        if amount_paise > current_balance:
            raise ValueError("Insufficient balance.")

        source_ledger = get_or_create_customer_ledger_account(
            db, source_account
        )

        destination_ledger = get_or_create_customer_ledger_account(
            db, destination_account
        )

        transaction = Transaction(
            transaction_type="transfer",
            amount_paise=amount_paise,
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            initiated_by=initiated_by,
            status="pending",
        )

        db.add(transaction)
        db.flush()

        debit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=source_ledger.id,
            entry_type="debit",
            amount_paise=amount_paise,
        )

        credit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=destination_ledger.id,
            entry_type="credit",
            amount_paise=amount_paise,
        )

        db.add_all([debit_entry, credit_entry])

        transaction.status = "posted"

        db.commit()

        return transaction

    except Exception:
        db.rollback()
        raise