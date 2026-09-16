def test_register_and_login(client):
    payload = {
        "email": "phase3@example.com",
        "password": "Password123!",
        "role": "CUSTOMER",
        "first_name": "Phase",
        "last_name": "Three",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"

    response = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_duplicate_registration_is_rejected(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "first_name": "Duplicate",
        "last_name": "User",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
