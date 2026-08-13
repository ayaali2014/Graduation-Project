import io


def _auth_headers(client, email="uploader@example.com", password="supersecret123"):
    client.post(
        "/users/",
        json={"username": "uploader", "email": email, "password": password},
    )
    login_response = client.post("/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_requires_authentication(client):
    response = client.post(
        "/files",
        files={"file": ("video.mp4", io.BytesIO(b"not-a-real-video"), "video/mp4")},
    )
    assert response.status_code == 401


def test_upload_rejects_wrong_extension(client):
    headers = _auth_headers(client)
    response = client.post(
        "/files",
        headers=headers,
        files={"file": ("payload.txt", io.BytesIO(b"hello"), "video/mp4")},
    )
    assert response.status_code == 415


def test_upload_rejects_disallowed_declared_content_type(client):
    headers = _auth_headers(client, email="uploader2@example.com")
    response = client.post(
        "/files",
        headers=headers,
        files={"file": ("video.mp4", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 415


def test_upload_rejects_content_not_matching_declared_type(client):
    headers = _auth_headers(client, email="uploader3@example.com")
    response = client.post(
        "/files",
        headers=headers,
        files={"file": ("video.mp4", io.BytesIO(b"just some plain text content"), "video/mp4")},
    )
    assert response.status_code == 415


def test_download_requires_authentication(client):
    response = client.get("/download")
    assert response.status_code == 401
