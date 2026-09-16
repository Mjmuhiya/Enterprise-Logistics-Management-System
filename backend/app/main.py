from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Shipment, User
from app.repositories import add_status_history, get_customer_by_user_id, get_shipment, list_shipments
from app.schemas import ShipmentCreate, ShipmentStatusUpdate, TokenResponse, UserCreate, UserLogin
from app.security import create_access_token, decode_access_token
from app.services import authenticate_user, create_shipment, register_user

app = FastAPI(
    title="LogiFlow Enterprise API",
    version="1.2.0",
    description="REST API for intelligent logistics and supply chain management.",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

STATUS_FLOW = {
    "CREATED": {"PICKUP_SCHEDULED", "CANCELLED"},
    "PICKUP_SCHEDULED": {"IN_TRANSIT", "CANCELLED"},
    "IN_TRANSIT": {"OUT_FOR_DELIVERY", "DELIVERY_FAILED"},
    "OUT_FOR_DELIVERY": {"DELIVERED", "DELIVERY_FAILED"},
    "DELIVERY_FAILED": {"OUT_FOR_DELIVERY", "CANCELLED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}


@app.get("/api/v1/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "logiflow-api"}


@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register(user: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        created = register_user(db, str(user.email), user.password, user.role, user.first_name, user.last_name)
    except ValueError as exc:
        message = str(exc)
        code = 409 if message == "User already exists" else 400
        raise HTTPException(status_code=code, detail=message) from exc
    return TokenResponse(access_token=create_access_token(str(created.id), created.role.name))


@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, str(credentials.email), credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(str(user.id), user.role.name))


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user_id = UUID(payload["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    allowed = {role.upper() for role in roles}

    def dependency(user: User = Depends(current_user)) -> User:
        if user.role.name.upper() not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency


def shipment_response(shipment: Shipment) -> dict:
    return {
        "id": str(shipment.id),
        "tracking_number": shipment.tracking_number,
        "customer_id": str(shipment.customer_id),
        "origin": shipment.origin_address,
        "destination": shipment.destination_address,
        "weight_kg": float(shipment.weight_kg),
        "status": shipment.status,
        "created_at": shipment.created_at,
        "updated_at": shipment.updated_at,
    }


@app.post("/api/v1/shipments", status_code=status.HTTP_201_CREATED, tags=["Shipments"])
def create_shipment_endpoint(payload: ShipmentCreate, user: User = Depends(require_role("CUSTOMER", "ADMIN")), db: Session = Depends(get_db)) -> dict:
    customer_id = payload.customer_id if hasattr(payload, "customer_id") and payload.customer_id else None
    if user.role.name.upper() == "CUSTOMER":
        customer = get_customer_by_user_id(db, user.id)
        if not customer:
            raise HTTPException(status_code=409, detail="Customer profile not found")
        customer_id = customer.id
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required for administrators")
    shipment = create_shipment(db, customer_id, payload.origin, payload.destination, payload.weight_kg, payload.tracking_number)
    return shipment_response(shipment)


@app.get("/api/v1/shipments", tags=["Shipments"])
def list_shipments_endpoint(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    customer_id = None
    if user.role.name.upper() == "CUSTOMER":
        customer = get_customer_by_user_id(db, user.id)
        if not customer:
            return []
        customer_id = customer.id
    return [shipment_response(shipment) for shipment in list_shipments(db, customer_id)]


@app.get("/api/v1/shipments/{shipment_id}", tags=["Shipments"])
def get_shipment_endpoint(shipment_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    shipment = get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    if user.role.name.upper() == "CUSTOMER":
        customer = get_customer_by_user_id(db, user.id)
        if not customer or shipment.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Shipment access denied")
    return shipment_response(shipment)


@app.patch("/api/v1/shipments/{shipment_id}/status", tags=["Tracking"])
def update_status(shipment_id: UUID, payload: ShipmentStatusUpdate, user: User = Depends(require_role("DRIVER", "WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)) -> dict:
    shipment = get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    new_status = payload.status.upper()
    if new_status not in STATUS_FLOW.get(shipment.status, set()):
        raise HTTPException(status_code=400, detail=f"Invalid transition from {shipment.status} to {new_status}")
    old_status = shipment.status
    shipment.status = new_status
    add_status_history(db, shipment.id, old_status, new_status, user.id, payload.notes)
    db.commit()
    db.refresh(shipment)
    return shipment_response(shipment)
