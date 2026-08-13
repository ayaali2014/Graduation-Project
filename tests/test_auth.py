def test_create_user_success(client):
    response = client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "password" not in body


def test_create_user_duplicate_email_rejected(client):
    payload = {"username": "bob", "email": "bob@example.com", "password": "supersecret123"}
    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)
    assert response.status_code == 409


def test_login_success_and_me(client):
    client.post(
        "/users/",
        json={"username": "carol", "email": "carol@example.com", "password": "supersecret123"},
    )
    login_response = client.post(
        "/login",
        json={"email": "carol@example.com", "password": "supersecret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "carol@example.com"


def test_login_wrong_password_rejected(client):
    client.post(
        "/users/",
        json={"username": "dave", "email": "dave@example.com", "password": "supersecret123"},
    )
    response = client.post(
        "/login",
        json={"email": "dave@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_without_token_rejected(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_me_with_invalid_token_rejected(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token"},
    )
    assert response.status_code == 401
