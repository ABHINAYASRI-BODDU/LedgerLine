from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry

from app.services.ledger_integrity import verify_ledger_integrity


def create_test_transaction(db, amount_paise=10000):
    user = User(
        full_name="Integrity Test User",
        email="integrity@example.com",
        hashed_password="test_hash",
        role="customer"
    )
    db.add(user)
    db.flush()

    account = Account(
        account_number="LL9876543210",
        user_id=user.id,
        account_type="savings",
        currency="INR",
        status="active"
    )
    db.add(account)
    db.flush()

    customer_ledger = LedgerAccount(
        code="CUSTOMER_INTEGRITY_TEST",
        name="Integrity Test Account",
        category="liability",
        account_id=account.id,
        is_system=False
    )

    db.add(customer_ledger)
    db.flush()

    system_ledger = (
        db.query(LedgerAccount)
        .filter(LedgerAccount.code == "SYS_CASH")
        .first()
    )

    transaction = Transaction(
        transaction_type="deposit",
        amount_paise=amount_paise,
        destination_account_id=account.id,
        initiated_by=user.id,
        status="posted"
    )

    db.add(transaction)
    db.flush()

    debit_entry = LedgerEntry(
        transaction_id=transaction.id,
        ledger_account_id=system_ledger.id,
        entry_type="debit",
        amount_paise=amount_paise
    )

    credit_entry = LedgerEntry(
        transaction_id=transaction.id,
        ledger_account_id=customer_ledger.id,
        entry_type="credit",
        amount_paise=amount_paise
    )

    db.add_all([debit_entry, credit_entry])
    db.commit()

    return transaction


def test_valid_ledger_passes_integrity_check(test_db):
    create_test_transaction(test_db)

    result = verify_ledger_integrity(test_db)

    assert result["is_valid"] is True
    assert result["checked_transactions"] == 1
    assert result["invalid_transactions"] == []


def test_unbalanced_ledger_fails_integrity_check(test_db):
    transaction = create_test_transaction(test_db)

    # Change the transaction amount to simulate corrupted data.
    transaction.amount_paise = 15000
    test_db.commit()

    result = verify_ledger_integrity(test_db)

    assert result["is_valid"] is False
    assert result["checked_transactions"] == 1
    assert len(result["invalid_transactions"]) == 1

    invalid_transaction = result["invalid_transactions"][0]

    assert invalid_transaction["transaction_id"] == transaction.id
    assert invalid_transaction["transaction_amount_paise"] == 15000
    assert invalid_transaction["debit_total_paise"] == 10000
    assert invalid_transaction["credit_total_paise"] == 10000