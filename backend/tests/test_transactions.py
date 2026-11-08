
from app.models.ledger_entry import LedgerEntry
from app.models.transaction import Transaction
from unittest.mock import patch

from app.services import ledger_service

def register_and_login(client, email):
    client.post(
        "/auth/register",
        json={
            "full_name": "Transaction Test User",
            "email": email,
            "password": "TestPass123!"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPass123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_account(client, headers):
    response = client.post(
        "/accounts/",
        json={"account_type": "savings"},
        headers=headers
    )

    assert response.status_code == 201

    return response.json()["id"]


def get_balance(client, account_id, headers):
    response = client.get(
        f"/accounts/{account_id}/balance",
        headers=headers
    )

    assert response.status_code == 200

    return response.json()["balance_paise"]


def test_successful_deposit(client):
    headers = register_and_login(client, "deposit@example.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 10000,
            "idempotency_key": "deposit-test-001"
        },
        headers=headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["transaction_type"] == "deposit"
    assert data["amount_paise"] == 10000
    assert data["status"] == "posted"

    assert get_balance(client, account_id, headers) == 10000


def test_duplicate_deposit_does_not_add_money_twice(client):
    headers = register_and_login(client, "duplicate@example.com")
    account_id = create_account(client, headers)

    request_data = {
        "account_id": account_id,
        "amount_paise": 5000,
        "idempotency_key": "duplicate-deposit-001"
    }

    first_response = client.post(
        "/transactions/deposit",
        json=request_data,
        headers=headers
    )

    second_response = client.post(
        "/transactions/deposit",
        json=request_data,
        headers=headers
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["id"] == second_response.json()["id"]

    assert get_balance(client, account_id, headers) == 5000


def test_idempotency_key_reuse_with_different_amount_rejected(client):
    headers = register_and_login(client, "keyreuse@example.com")
    account_id = create_account(client, headers)

    first_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 5000,
            "idempotency_key": "reuse-key-001"
        },
        headers=headers
    )

    second_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 8000,
            "idempotency_key": "reuse-key-001"
        },
        headers=headers
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400

    assert get_balance(client, account_id, headers) == 5000


def test_withdrawal_from_empty_account_rejected(client):
    headers = register_and_login(client, "withdrawempty@example.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount_paise": 1000,
            "idempotency_key": "empty-withdraw-001"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert get_balance(client, account_id, headers) == 0


def test_successful_withdrawal(client):
    headers = register_and_login(client, "withdraw@example.com")
    account_id = create_account(client, headers)

    deposit_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 10000,
            "idempotency_key": "withdraw-deposit-001"
        },
        headers=headers
    )

    assert deposit_response.status_code == 201

    withdrawal_response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount_paise": 3000,
            "idempotency_key": "withdraw-test-001"
        },
        headers=headers
    )

    assert withdrawal_response.status_code == 201
    assert withdrawal_response.json()["status"] == "posted"

    assert get_balance(client, account_id, headers) == 7000


def test_successful_transfer(client):
    headers = register_and_login(client, "transfer@example.com")

    source_account_id = create_account(client, headers)
    destination_account_id = create_account(client, headers)

    deposit_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": source_account_id,
            "amount_paise": 10000,
            "idempotency_key": "transfer-deposit-001"
        },
        headers=headers
    )

    assert deposit_response.status_code == 201

    transfer_response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount_paise": 3500,
            "idempotency_key": "transfer-test-001"
        },
        headers=headers
    )

    assert transfer_response.status_code == 201
    assert transfer_response.json()["status"] == "posted"

    assert get_balance(client, source_account_id, headers) == 6500
    assert get_balance(client, destination_account_id, headers) == 3500


def test_transfer_with_insufficient_balance_rejected(client):
    headers = register_and_login(client, "transferempty@example.com")

    source_account_id = create_account(client, headers)
    destination_account_id = create_account(client, headers)

    response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount_paise": 1000,
            "idempotency_key": "empty-transfer-001"
        },
        headers=headers
    )

    assert response.status_code == 400

    assert get_balance(client, source_account_id, headers) == 0
    assert get_balance(client, destination_account_id, headers) == 0


def test_transaction_history(client):
    headers = register_and_login(client, "history@example.com")
    account_id = create_account(client, headers)

    deposit_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 7500,
            "idempotency_key": "history-deposit-001"
        },
        headers=headers
    )

    assert deposit_response.status_code == 201

    history_response = client.get(
        "/transactions/history",
        headers=headers
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["id"] == deposit_response.json()["id"]
    assert history[0]["amount_paise"] == 7500


def test_posted_transaction_has_balanced_ledger_entries(client, test_db):
    headers = register_and_login(client, "ledgercheck@example.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount_paise": 12000,
            "idempotency_key": "ledger-balance-test-001"
        },
        headers=headers
    )

    assert response.status_code == 201

    transaction_id = response.json()["id"]

    transaction = (
        test_db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    assert transaction is not None
    assert transaction.status == "posted"

    entries = (
        test_db.query(LedgerEntry)
        .filter(LedgerEntry.transaction_id == transaction_id)
        .all()
    )

    debit_total = sum(
        entry.amount_paise
        for entry in entries
        if entry.entry_type == "debit"
    )

    credit_total = sum(
        entry.amount_paise
        for entry in entries
        if entry.entry_type == "credit"
    )

    assert len(entries) == 2
    assert debit_total == 12000
    assert credit_total == 12000
    assert debit_total == credit_total
    assert debit_total == transaction.amount_paise

def test_failed_deposit_rolls_back_transaction_and_ledger_entries(
    client,
    test_db
):
    headers = register_and_login(client, "rollback@example.com")
    account_id = create_account(client, headers)

    # Simulate a failure during ledger balance verification.
    with patch.object(
        ledger_service,
        "verify_transaction_balance",
        side_effect=ValueError("Simulated transaction failure")
    ):
        response = client.post(
            "/transactions/deposit",
            json={
                "account_id": account_id,
                "amount_paise": 5000,
                "idempotency_key": "rollback-test-001"
            },
            headers=headers
        )

    # The API should reject the failed transaction.
    assert response.status_code == 400

    # No transaction should remain in the database.
    transaction_count = (
        test_db.query(Transaction)
        .filter(
            Transaction.idempotency_key == "rollback-test-001"
        )
        .count()
    )

    assert transaction_count == 0

    # No ledger entries should remain.
    entry_count = test_db.query(LedgerEntry).count()

    assert entry_count == 0

    # The customer's balance must remain zero.
    assert get_balance(client, account_id, headers) == 0
