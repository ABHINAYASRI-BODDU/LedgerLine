
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Customer",
            "email": "customer1@example.com",
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test Customer"
    assert data["email"] == "customer1@example.com"
    assert data["role"] == "customer"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_duplicate_email_rejected(client):
    user_data = {
        "full_name": "Test Customer",
        "email": "duplicate@example.com",
        "password": "TestPass123!"
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Login Customer",
            "email": "login@example.com",
            "password": "TestPass123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Wrong Password Customer",
            "email": "wrong@example.com",
            "password": "TestPass123!"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPass123!"
        }
    )

    assert response.status_code == 401


def test_get_current_user(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Profile Customer",
            "email": "profile@example.com",
            "password": "TestPass123!"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "profile@example.com",
            "password": "TestPass123!"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"


def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401

