# Phase 2 — Authentication & Shipment Lifecycle

## Objective
Implement a secure vertical slice from identity to shipment tracking while maintaining explicit software-engineering traceability.

## Connectivity
```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant SEC as JWT/Security
    participant DOM as Shipment Domain
    participant DB as PostgreSQL

    C->>API: POST /auth/login
    API->>SEC: verify password
    SEC-->>API: signed JWT
    API-->>C: access token
    C->>API: POST /shipments + Bearer token
    API->>SEC: validate JWT + role
    SEC-->>API: authenticated identity
    API->>DOM: validate shipment command
    DOM-->>API: valid shipment
    API->>DB: persist shipment
    DB-->>API: result
    API-->>C: shipment response
```

## Shipment state machine
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

## Traceability
| Requirement | Design | Implementation | Verification |
|---|---|---|---|
| User authentication | JWT + password hashing | `/auth/register`, `/auth/login` | `test_auth.py` |
| RBAC | Role dependency | `require_role()` | shipment authorization tests |
| Shipment creation | REST command | `POST /shipments` | shipment integration test |
| Shipment tracking | State machine | `GET /shipments/{id}` | retrieval test |
| Valid status changes | Domain transition rules | `STATUS_FLOW` | invalid transition test |

## Academic alignment
- **Requirements engineering:** explicit functional requirements and acceptance behaviour.
- **Design:** sequence and state diagrams before implementation.
- **Implementation:** layered API/security/domain separation.
- **Testing:** automated integration tests linked to requirements.
- **Quality:** authentication, authorization, validation and traceability.

> PostgreSQL persistence is introduced through the SQLAlchemy foundation and is the next hardening step for the vertical slice.
