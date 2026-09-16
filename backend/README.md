# LogiFlow Backend

Backend service for the LogiFlow Enterprise platform.

## Architecture

```text
API Router
   ↓
Controller / Endpoint
   ↓
Schema Validation
   ↓
Service Layer (business rules)
   ↓
Repository / Data Access
   ↓
PostgreSQL
```

## Initial responsibilities

- `/api/v1/health` — service health
- `/api/v1/auth/*` — authentication and RBAC
- `/api/v1/shipments/*` — shipment lifecycle
- `/api/v1/drivers/*` — driver management
- `/api/v1/vehicles/*` — fleet management
- `/api/v1/warehouses/*` — inventory management
- `/api/v1/routes/*` — route planning/optimisation
- `/api/v1/invoices/*` — billing
- `/api/v1/analytics/*` — operational KPIs

Business logic must remain in services rather than being embedded directly in HTTP handlers.
