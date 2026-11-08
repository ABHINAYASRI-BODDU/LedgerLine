from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry
from app.services.concurrency import lock_accounts_for_money_movement


# Verify that the authenticated user owns the account.
def verify_account_ownership(account: Account, initiated_by: int):
    if account.user_id != initiated_by:
        raise ValueError("You do not own this account.")


# Check whether an idempotency key was already used.
def check_existing_transaction(
    db: Session,
    idempotency_key: str,
    initiated_by: int,
    transaction_type: str,
    amount_paise: int,
    source_account_id: int | None,
    destination_account_id: int | None
):
    existing_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.idempotency_key == idempotency_key
        )
        .first()
    )

    if existing_transaction is None:
        return None

    if (
        existing_transaction.initiated_by != initiated_by
        or existing_transaction.transaction_type != transaction_type
        or existing_transaction.amount_paise != amount_paise
        or existing_transaction.source_account_id != source_account_id
        or existing_transaction.destination_account_id != destination_account_id
    ):
        raise ValueError(
            "Idempotency key already used for a different transaction."
        )

    if existing_transaction.status != "posted":
        raise ValueError(
            "Existing transaction is not successfully posted."
        )

    return existing_transaction


# Verify debit and credit equality before posting.
def verify_transaction_balance(db: Session, transaction):
    debit_total = (
        db.query(func.sum(LedgerEntry.amount_paise))
        .filter(
            LedgerEntry.transaction_id == transaction.id,
            LedgerEntry.entry_type == "debit"
        )
        .scalar() or 0
    )

    credit_total = (
        db.query(func.sum(LedgerEntry.amount_paise))
        .filter(
            LedgerEntry.transaction_id == transaction.id,
            LedgerEntry.entry_type == "credit"
        )
        .scalar() or 0
    )

    if (
        debit_total != credit_total
        or debit_total != transaction.amount_paise
    ):
        raise ValueError("Transaction is not balanced.")


# Create the system ledger account if it does not exist.
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


# Get or create a customer's ledger account.
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


# Record a deposit.
def record_deposit(
    db: Session,
    account,
    amount_paise: int,
    initiated_by: int,
    idempotency_key: str
):
    if amount_paise <= 0:
        raise ValueError("Deposit amount must be positive.")

    # Save the ID before the helper rolls back the earlier read transaction.
    account_id = account.id

    try:
        locked_accounts = lock_accounts_for_money_movement(
            db,
            [account_id]
        )

        # Always use the freshly loaded account.
        account = locked_accounts[account_id]

        verify_account_ownership(account, initiated_by)

        existing_transaction = check_existing_transaction(
            db=db,
            idempotency_key=idempotency_key,
            initiated_by=initiated_by,
            transaction_type="deposit",
            amount_paise=amount_paise,
            source_account_id=None,
            destination_account_id=account_id
        )

        if existing_transaction is not None:
            return existing_transaction

        if account.status != "active":
            raise ValueError(
                "Deposits are allowed only for active accounts."
            )

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

        transaction = Transaction(
            transaction_type="deposit",
            amount_paise=amount_paise,
            source_account_id=None,
            destination_account_id=account_id,
            initiated_by=initiated_by,
            status="pending",
            idempotency_key=idempotency_key
        )

        db.add(transaction)
        db.flush()

        debit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=cash_ledger.id,
            entry_type="debit",
            amount_paise=amount_paise,
        )

        credit_entry = LedgerEntry(
            transaction_id=transaction.id,
            ledger_account_id=customer_ledger.id,
            entry_type="credit",
            amount_paise=amount_paise,
        )

        db.add_all([debit_entry, credit_entry])
        db.flush()

        verify_transaction_balance(db, transaction)

        transaction.status = "posted"

        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise


# Calculate the account balance from ledger entries.
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


# Record a withdrawal.
def record_withdrawal(
    db: Session,
    account,
    amount_paise: int,
    initiated_by: int,
    idempotency_key: str
):
    if amount_paise <= 0:
        raise ValueError("Withdrawal amount must be positive.")

    account_id = account.id

    try:
        locked_accounts = lock_accounts_for_money_movement(
            db,
            [account_id]
        )

        account = locked_accounts[account_id]

        verify_account_ownership(account, initiated_by)

        existing_transaction = check_existing_transaction(
            db=db,
            idempotency_key=idempotency_key,
            initiated_by=initiated_by,
            transaction_type="withdrawal",
            amount_paise=amount_paise,
            source_account_id=account_id,
            destination_account_id=None
        )

        if existing_transaction is not None:
            return existing_transaction

        if account.status != "active":
            raise ValueError(
                "Withdrawals are allowed only for active accounts."
            )

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
            source_account_id=account_id,
            destination_account_id=None,
            initiated_by=initiated_by,
            status="pending",
            idempotency_key=idempotency_key
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
        db.flush()

        verify_transaction_balance(db, transaction)

        transaction.status = "posted"

        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise


# Record a transfer.
def record_transfer(
    db: Session,
    source_account,
    destination_account,
    amount_paise: int,
    initiated_by: int,
    idempotency_key: str
):
    if amount_paise <= 0:
        raise ValueError("Transfer amount must be positive.")

    source_account_id = source_account.id
    destination_account_id = destination_account.id

    if source_account_id == destination_account_id:
        raise ValueError("Cannot transfer to the same account.")

    try:
        locked_accounts = lock_accounts_for_money_movement(
            db,
            [source_account_id, destination_account_id]
        )

        source_account = locked_accounts[source_account_id]
        destination_account = locked_accounts[destination_account_id]

        verify_account_ownership(source_account, initiated_by)
        verify_account_ownership(destination_account, initiated_by)

        existing_transaction = check_existing_transaction(
            db=db,
            idempotency_key=idempotency_key,
            initiated_by=initiated_by,
            transaction_type="transfer",
            amount_paise=amount_paise,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id
        )

        if existing_transaction is not None:
            return existing_transaction

        if source_account.status != "active":
            raise ValueError("Source account must be active.")

        if destination_account.status != "active":
            raise ValueError("Destination account must be active.")

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
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            initiated_by=initiated_by,
            status="pending",
            idempotency_key=idempotency_key
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
        db.flush()

        verify_transaction_balance(db, transaction)

        transaction.status = "posted"

        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise