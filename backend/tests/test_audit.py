
from sqlalchemy import inspect

from app.models.account import Account
from app.models.transaction_attempt import TransactionAttempt
from app.services.audit_service import record_failed_attempt


def test_audit_table_is_available(test_db):
    table_names = inspect(test_db.get_bind()).get_table_names()

    assert "transaction_attempts" in table_names


def test_failed_attempt_is_saved(test_db):
    session_factory = test_db.get_bind()

    from sqlalchemy.orm import sessionmaker

    TestSessionLocal = sessionmaker(
        bind=session_factory,
        autocommit=False,
        autoflush=False
    )

    record_failed_attempt(
        transaction_type="withdrawal",
        amount_paise=5000,
        initiated_by=1,
        failure_reason="Insufficient balance",
        source_account_id=None,
        idempotency_key="audit-test-001",
        session_factory=TestSessionLocal
    )

    attempt = (
        test_db.query(TransactionAttempt)
        .filter(
            TransactionAttempt.idempotency_key == "audit-test-001"
        )
        .first()
    )

    assert attempt is not None
    assert attempt.transaction_type == "withdrawal"
    assert attempt.amount_paise == 5000
    assert attempt.failure_reason == "Insufficient balance"


def test_failed_withdrawal_api_creates_audit_record(client):
    from tests.test_transactions import register_and_login, create_account

    headers = register_and_login(client, "audituser@example.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount_paise": 5000,
            "idempotency_key": "failed-withdrawal-audit-001"
        },
        headers=headers
    )

    assert response.status_code == 400

    audit_db = client.app.state.test_session_factory()

    try:
        attempt = (
            audit_db.query(TransactionAttempt)
            .filter(
                TransactionAttempt.idempotency_key
                == "failed-withdrawal-audit-001"
            )
            .first()
        )

        assert attempt is not None
        assert attempt.transaction_type == "withdrawal"
        assert attempt.amount_paise == 5000
        assert attempt.initiated_by is not None
        assert attempt.failure_reason == "Insufficient balance."
    finally:
        audit_db.close()


def test_failed_deposit_api_creates_audit_record(client):
    from tests.test_transactions import register_and_login, create_account

    headers = register_and_login(client, "auditdeposit@example.com")
    account_id = create_account(client, headers)

    audit_db = client.app.state.test_session_factory()

    try:
        account = (
            audit_db.query(Account)
            .filter(Account.id == account_id)
            .first()
        )

        assert account is not None

        account.status = "frozen"
        audit_db.commit()
    finally:
        audit_db.close()

    response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 5000,
            "idempotency_key": "failed-deposit-audit-001"
        },
        headers=headers
    )

    assert response.status_code == 400

    audit_db = client.app.state.test_session_factory()

    try:
        attempt = (
            audit_db.query(TransactionAttempt)
            .filter(
                TransactionAttempt.idempotency_key
                == "failed-deposit-audit-001"
            )
            .first()
        )

        assert attempt is not None
        assert attempt.transaction_type == "deposit"
        assert attempt.amount_paise == 5000
        assert attempt.initiated_by is not None
        assert attempt.failure_reason == (
            "Deposits are allowed only for active accounts."
        )
    finally:
        audit_db.close()

def test_failed_transfer_api_creates_audit_record(client):
    from tests.test_transactions import register_and_login, create_account

    headers = register_and_login(client, "audittransfer@example.com")

    source_account_id = create_account(client, headers)
    destination_account_id = create_account(client, headers)

    response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount_paise": 5000,
            "idempotency_key": "failed-transfer-audit-001"
        },
        headers=headers
    )

    assert response.status_code == 400

    audit_db = client.app.state.test_session_factory()

    try:
        attempt = (
            audit_db.query(TransactionAttempt)
            .filter(
                TransactionAttempt.idempotency_key
                == "failed-transfer-audit-001"
            )
            .first()
        )

        assert attempt is not None
        assert attempt.transaction_type == "transfer"
        assert attempt.amount_paise == 5000
        assert attempt.source_account_id == source_account_id
        assert attempt.destination_account_id == destination_account_id
        assert attempt.initiated_by is not None
        assert attempt.failure_reason == "Insufficient balance."
    finally:
        audit_db.close()

