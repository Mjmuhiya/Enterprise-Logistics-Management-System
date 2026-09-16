from fastapi.testclient import TestClient

from app.main import app, next_customer_id

client = TestClient(app)


def auth(email="shipment@example.com", role="customer"):
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!", "role": role})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_customer_can_create_and_read_own_shipment():
    email = "customer-shipment@example.com"
    headers = auth(email)
    customer_id = next_customer_id(email)
    response = client.post("/api/v1/shipments", headers=headers, json={
        "customer_id": customer_id,
        "origin": "Pretoria",
        "destination": "Johannesburg",
        "weight_kg": 12.5,
        "description": "Electronics"
    })
    assert response.status_code == 201
    shipment_id = response.json()["id"]

    response = client.get(f"/api/v1/shipments/{shipment_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "created"


def test_invalid_status_transition_is_rejected():
    email = "driver-shipment@example.com"
    customer_headers = auth(email, "customer")
    customer_id = next_customer_id(email)
    created = client.post("/api/v1/shipments", headers=customer_headers, json={
        "customer_id": customer_id,
        "origin": "Pretoria",
        "destination": "Cape Town",
        "weight_kg": 5
    })
    shipment_id = created.json()["id"]

    driver_headers = auth("driver@example.com", "driver")
    response = client.patch(f"/api/v1/shipments/{shipment_id}/status", headers=driver_headers, json={"status": "delivered"})
    assert response.status_code == 400
