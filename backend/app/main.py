from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas import ShipmentCreate, ShipmentStatusUpdate, TokenResponse, UserCreate, UserLogin
from app.security import create_access_token, decode_access_token, hash_password, verify_password

app = FastAPI(title="LogiFlow Enterprise API", version="1.1.0", description="REST API for intelligent logistics and supply chain management.")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Temporary in-memory stores for Phase 2. SQLAlchemy persistence is the next persistence layer.
USERS: dict[str, dict] = {}
SHIPMENTS: dict[int, dict] = {}
NEXT_SHIPMENT_ID = 1
VALID_ROLES = {"customer", "driver", "warehouse_manager", "admin"}
STATUS_FLOW = {"created": {"assigned"}, "assigned": {"picked_up"}, "picked_up": {"in_transit"}, "in_transit": {"out_for_delivery"}, "out_for_delivery": {"delivered"}, "delivered": set()}


@app.get("/api/v1/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "logiflow-api"}


@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register(user: UserCreate) -> TokenResponse:
    email = str(user.email).lower()
    if email in USERS:
        raise HTTPException(status_code=409, detail="User already exists")
    if user.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    USERS[email] = {"email": email, "password_hash": hash_password(user.password), "role": user.role}
    return TokenResponse(access_token=create_access_token(email, user.role))


@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(credentials: UserLogin) -> TokenResponse:
    record = USERS.get(str(credentials.email).lower())
    if not record or not verify_password(credentials.password, record["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(record["email"], record["role"]))


def current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    record = USERS.get(payload["sub"])
    if not record:
        raise HTTPException(status_code=401, detail="User not found")
    return record


def require_role(*roles: str):
    def dependency(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency


@app.post("/api/v1/shipments", status_code=status.HTTP_201_CREATED, tags=["Shipments"])
def create_shipment(payload: ShipmentCreate, user: dict = Depends(require_role("customer", "admin"))) -> dict:
    global NEXT_SHIPMENT_ID
    shipment = {"id": NEXT_SHIPMENT_ID, **payload.model_dump(), "status": "created"}
    SHIPMENTS[NEXT_SHIPMENT_ID] = shipment
    NEXT_SHIPMENT_ID += 1
    return shipment


@app.get("/api/v1/shipments", tags=["Shipments"])
def list_shipments(user: dict = Depends(current_user)) -> list[dict]:
    if user["role"] == "customer":
        return [s for s in SHIPMENTS.values() if s["customer_id"] == s.get("customer_id")]
    return list(SHIPMENTS.values())


@app.get("/api/v1/shipments/{shipment_id}", tags=["Shipments"])
def get_shipment(shipment_id: int, user: dict = Depends(current_user)) -> dict:
    shipment = SHIPMENTS.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@app.patch("/api/v1/shipments/{shipment_id}/status", tags=["Tracking"])
def update_status(shipment_id: int, payload: ShipmentStatusUpdate, user: dict = Depends(require_role("driver", "warehouse_manager", "admin"))) -> dict:
    shipment = SHIPMENTS.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    if payload.status not in STATUS_FLOW.get(shipment["status"], set()):
        raise HTTPException(status_code=400, detail=f"Invalid transition from {shipment['status']} to {payload.status}")
    shipment["status"] = payload.status
    return shipment
