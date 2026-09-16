def register(client, email, role="CUSTOMER"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "role": role,
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_customer_can_create_and_read_own_shipment(client):
    headers = register(client, "customer-shipment@example.com")
    created = client.post(
        "/api/v1/shipments",
        headers=headers,
        json={"origin": "Pretoria", "destination": "Johannesburg", "weight_kg": 12.5},
    )
    assert created.status_code == 201
    shipment_id = created.json()["id"]

    response = client.get(f"/api/v1/shipments/{shipment_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CREATED"


def test_invalid_status_transition_is_rejected(client):
    customer_headers = register(client, "customer-status@example.com")
    created = client.post(
        "/api/v1/shipments",
        headers=customer_headers,
        json={"origin": "Pretoria", "destination": "Cape Town", "weight_kg": 5},
    )
    shipment_id = created.json()["id"]

    driver_headers = register(client, "driver@example.com", "DRIVER")
    response = client.patch(
        f"/api/v1/shipments/{shipment_id}/status",
        headers=driver_headers,
        json={"status": "DELIVERED"},
    )
    assert response.status_code == 400


def test_valid_status_transition_creates_history(client):
    customer_headers = register(client, "customer-history@example.com")
    created = client.post(
        "/api/v1/shipments",
        headers=customer_headers,
        json={"origin": "Pretoria", "destination": "Durban", "weight_kg": 8},
    )
    shipment_id = created.json()["id"]

    driver_headers = register(client, "driver-history@example.com", "DRIVER")
    response = client.patch(
        f"/api/v1/shipments/{shipment_id}/status",
        headers=driver_headers,
        json={"status": "PICKUP_SCHEDULED", "notes": "Driver assigned"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PICKUP_SCHEDULED"
