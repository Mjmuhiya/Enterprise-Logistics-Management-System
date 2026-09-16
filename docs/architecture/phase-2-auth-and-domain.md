# Phase 2 — Authentication, RBAC & Shipment Domain

## Objective
Implement the first protected business workflows while preserving traceability from requirements to API behaviour and automated tests.

## Security flow
```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant AUTH as Auth Service
    participant DB as PostgreSQL

    C->>API: POST /api/v1/auth/register
    API->>AUTH: Validate + hash password
    AUTH->>DB: Persist user
    DB-->>AUTH: User created
    AUTH-->>C: JWT access token
    C->>API: Authorization: Bearer JWT
    API->>AUTH: Decode + validate token
    AUTH-->>API: User + role
    API->>DB: Execute authorized operation
    DB-->>API: Result
    API-->>C: JSON response
```

## RBAC matrix
| Capability | Customer | Driver | Warehouse Manager | Admin |
|---|---:|---:|---:|---:|
| Register/Login | ✓ | ✓ | ✓ | ✓ |
| View shipments | ✓ | ✓ | ✓ | ✓ |
| Create shipment | ✓ | — | — | ✓ |
| Change shipment status | — | ✓ | ✓ | ✓ |

## Shipment lifecycle
```mermaid
stateDiagram-v2
    [*] --> created
    created --> assigned
    assigned --> picked_up
    picked_up --> in_transit
    in_transit --> out_for_delivery
    out_for_delivery --> delivered
    delivered --> [*]
```

## Test strategy
- Authentication: registration, login and protected endpoints.
- Authorization: role-based access to shipment operations.
- Domain validation: invalid shipment status transitions return HTTP 400.
- Integration: API requests are exercised through FastAPI TestClient.

## Academic traceability
| Requirement | Design | Implementation | Verification |
|---|---|---|---|
| Secure user access | JWT + RBAC | `security.py`, auth endpoints | `test_auth_shipments.py` |
| Shipment management | REST resource | shipment endpoints | integration tests |
| Controlled lifecycle | state transition model | `STATUS_FLOW` | transition test |
