from fastapi.testclient import TestClient

from app.main import app, USERS, SHIPMENTS

client = TestClient(app)


def setup_function():
    USERS.clear()
    SHIPMENTS.clear()


def test_register_and_login():
    response = client.post("/api/v1/auth/register", json={"email": "customer@example.com", "password": "StrongPass123!", "role": "customer"})
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"

    response = client.post("/api/v1/auth/login", json={"email": "customer@example.com", "password": "StrongPass123!"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_shipment_requires_authentication():
    response = client.get("/api/v1/shipments")
    assert response.status_code == 401


def test_shipment_status_transition_is_validated():
    client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "StrongPass123!", "role": "admin"})
    token = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "StrongPass123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    shipment = client.post("/api/v1/shipments", headers=headers, json={"customer_id": 1, "origin": "Pretoria", "destination": "Johannesburg", "weight_kg": 10}).json()
    invalid = client.patch(f"/api/v1/shipments/{shipment['id']}/status", headers=headers, json={"status": "delivered"})
    assert invalid.status_code == 400

    valid = client.patch(f"/api/v1/shipments/{shipment['id']}/status", headers=headers, json={"status": "assigned"})
    assert valid.status_code == 200
