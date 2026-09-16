from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User
from app.main import current_user, require_role

router = APIRouter(prefix="/api/v1/fleet", tags=["Fleet"])

DRIVERS: dict[UUID, dict] = {}
VEHICLES: dict[UUID, dict] = {}


class DriverCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=5, max_length=30)
    licence_number: str = Field(min_length=3, max_length=80)


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=3, max_length=30)
    vehicle_type: str = Field(min_length=2, max_length=80)
    capacity_kg: float = Field(gt=0)


@router.post("/drivers", status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, user: User = Depends(require_role("OPERATIONS_MANAGER", "ADMIN"))):
    driver_id = uuid4()
    DRIVERS[driver_id] = {
        "id": str(driver_id),
        "name": payload.name,
        "phone": payload.phone,
        "licence_number": payload.licence_number,
        "status": "AVAILABLE",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return DRIVERS[driver_id]


@router.get("/drivers")
def list_drivers(user: User = Depends(current_user)):
    return list(DRIVERS.values())


@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, user: User = Depends(require_role("OPERATIONS_MANAGER", "ADMIN"))):
    vehicle_id = uuid4()
    VEHICLES[vehicle_id] = {
        "id": str(vehicle_id),
        "registration_number": payload.registration_number,
        "vehicle_type": payload.vehicle_type,
        "capacity_kg": payload.capacity_kg,
        "status": "AVAILABLE",
    }
    return VEHICLES[vehicle_id]


@router.get("/vehicles")
def list_vehicles(user: User = Depends(current_user)):
    return list(VEHICLES.values())
