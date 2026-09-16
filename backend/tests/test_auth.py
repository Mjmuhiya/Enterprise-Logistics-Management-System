from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login():
    email = "phase2@example.com"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!", "role": "customer"})
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_duplicate_registration_is_rejected():
    email = "duplicate@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"})
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"})
    assert response.status_code == 409
