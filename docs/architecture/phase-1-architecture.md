# Phase 1 Architecture Specification

## Objective

Establish a traceable architecture before feature implementation. The architecture separates presentation, API, business logic, persistence and external services.

## Quality Attributes

- Security: JWT authentication, RBAC, validation and auditability.
- Maintainability: modular service/repository boundaries.
- Testability: business logic isolated from transport and persistence.
- Scalability: stateless API and independently deployable services.
- Reliability: database constraints, transactions and health checks.
- Observability: structured logging and health endpoints.

## Connectivity Contract

```text
Client
  -> HTTPS
Frontend
  -> REST/JSON
API
  -> Authentication + Validation
Service Layer
  -> Repository Layer
PostgreSQL
```

## Academic traceability

| Requirement | Design evidence | Implementation evidence | Verification |
|---|---|---|---|
| Shipment creation | Shipment service + data model | `/shipments` endpoint | SHP tests |
| Shipment tracking | Status history model | Tracking endpoint | API/E2E tests |
| RBAC | Security boundary | JWT/RBAC middleware | Security tests |
| Inventory | Warehouse/inventory entities | Inventory service | Integration tests |
| Route optimisation | Route service | Optimisation algorithm | Algorithm tests |

## Architecture decision

The first implementation uses **FastAPI + PostgreSQL** because it provides a clear API-first foundation and supports rapid development, automated testing and OpenAPI documentation. The domain boundaries are deliberately framework-independent so the platform can evolve into additional services later.
