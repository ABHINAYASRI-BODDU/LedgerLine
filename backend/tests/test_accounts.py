
def register_and_login(client, email):
    client.post(
        "/auth/register",
        json={
            "full_name": "Account Test User",
            "email": email,
            "password": "TestPass123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPass123!"
        }
    )

    return {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }


def test_create_savings_account(client):
    headers = register_and_login(client, "savings@example.com")

    response = client.post(
        "/accounts/",
        json={"account_type": "savings"},
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["account_type"] == "savings"
    assert response.json()["status"] == "active"
    assert response.json()["currency"] == "INR"


def test_list_my_accounts(client):
    headers = register_and_login(client, "listaccounts@example.com")

    client.post(
        "/accounts/",
        json={"account_type": "savings"},
        headers=headers
    )

    response = client.get("/accounts/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_customer_cannot_access_another_users_account(client):
    first_headers = register_and_login(client, "first@example.com")
    second_headers = register_and_login(client, "second@example.com")

    account_response = client.post(
        "/accounts/",
        json={"account_type": "savings"},
        headers=first_headers
    )

    account_id = account_response.json()["id"]

    response = client.get(
        f"/accounts/{account_id}",
        headers=second_headers
    )

    assert response.status_code == 404


def test_get_account_balance(client):
    headers = register_and_login(client, "balance@example.com")

    account_response = client.post(
        "/accounts/",
        json={"account_type": "savings"},
        headers=headers
    )

    account_id = account_response.json()["id"]

    response = client.get(
        f"/accounts/{account_id}/balance",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["balance_paise"] == 0
    assert response.json()["balance"] == 0
    assert response.json()["currency"] == "INR"


def test_create_account_without_token(client):
    response = client.post(
        "/accounts/",
        json={"account_type": "savings"}
    )

    assert response.status_code == 401
