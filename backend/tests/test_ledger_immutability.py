import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry


def create_ledger_entry(db):
    user = User(
        full_name="Test User",
        email="immutable@example.com",
        hashed_password="test_hash",
        role="customer"
    )
    db.add(user)
    db.flush()

    account = Account(
        account_number="LL1234567890",
        user_id=user.id,
        account_type="savings",
        currency="INR",
        status="active"
    )
    db.add(account)
    db.flush()

    ledger_account = LedgerAccount(
        code="CUSTOMER_IMMUTABLE_TEST",
        name="Immutable Test Account",
        category="liability",
        account_id=account.id,
        is_system=False
    )
    db.add(ledger_account)
    db.flush()

    transaction = Transaction(
        transaction_type="deposit",
        amount_paise=10000,
        destination_account_id=account.id,
        initiated_by=user.id,
        status="posted"
    )
    db.add(transaction)
    db.flush()

    entry = LedgerEntry(
        transaction_id=transaction.id,
        ledger_account_id=ledger_account.id,
        entry_type="credit",
        amount_paise=10000
    )
    db.add(entry)
    db.commit()

    return entry.id


def test_ledger_entry_update_is_blocked(test_db):
    entry_id = create_ledger_entry(test_db)

    entry = test_db.get(LedgerEntry, entry_id)
    entry.amount_paise = 5000

    with pytest.raises(IntegrityError, match="Ledger entries are immutable"):
        test_db.commit()

    test_db.rollback()

    unchanged_entry = test_db.get(LedgerEntry, entry_id)
    assert unchanged_entry.amount_paise == 10000


def test_ledger_entry_delete_is_blocked(test_db):
    entry_id = create_ledger_entry(test_db)

    entry = test_db.get(LedgerEntry, entry_id)
    test_db.delete(entry)

    with pytest.raises(IntegrityError, match="Ledger entries are immutable"):
        test_db.commit()

    test_db.rollback()

    existing_entry = test_db.get(LedgerEntry, entry_id)
    assert existing_entry is not None
    assert existing_entry.amount_paise == 10000