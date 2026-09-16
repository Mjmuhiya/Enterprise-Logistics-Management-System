from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user, require_role
from app.models import Driver, User, Vehicle

router = APIRouter(prefix="/api/v1/fleet", tags=["Fleet"])


class DriverCreate(BaseModel):
    user_id: UUID
    phone: str | None = Field(default=None, max_length=30)
    licence_number: str = Field(min_length=3, max_length=100)


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=3, max_length=50)
    vehicle_type: str = Field(min_length=2, max_length=100)
    capacity_kg: float = Field(gt=0)


@router.post("/drivers", status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, _: User = Depends(require_role("OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="Driver user not found")
    if db.scalar(select(Driver).where(Driver.user_id == payload.user_id)):
        raise HTTPException(status_code=409, detail="Driver profile already exists")
    if db.scalar(select(Driver).where(Driver.licence_number == payload.licence_number)):
        raise HTTPException(status_code=409, detail="Licence number already exists")
    driver = Driver(user_id=payload.user_id, phone=payload.phone, licence_number=payload.licence_number)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver_response(driver)


@router.get("/drivers")
def list_drivers(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return [driver_response(driver) for driver in db.scalars(select(Driver).order_by(Driver.created_at.desc()))]


@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, _: User = Depends(require_role("OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    if db.scalar(select(Vehicle).where(Vehicle.registration_number == payload.registration_number)):
        raise HTTPException(status_code=409, detail="Vehicle registration already exists")
    vehicle = Vehicle(registration_number=payload.registration_number, vehicle_type=payload.vehicle_type, capacity_kg=payload.capacity_kg)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle_response(vehicle)


@router.get("/vehicles")
def list_vehicles(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return [vehicle_response(vehicle) for vehicle in db.scalars(select(Vehicle).order_by(Vehicle.created_at.desc()))]


def driver_response(driver: Driver) -> dict:
    return {
        "id": str(driver.id),
        "user_id": str(driver.user_id),
        "phone": driver.phone,
        "licence_number": driver.licence_number,
        "status": driver.availability_status,
        "created_at": driver.created_at,
    }


def vehicle_response(vehicle: Vehicle) -> dict:
    return {
        "id": str(vehicle.id),
        "registration_number": vehicle.registration_number,
        "vehicle_type": vehicle.vehicle_type,
        "capacity_kg": float(vehicle.capacity_kg),
        "status": vehicle.status,
        "created_at": vehicle.created_at,
    }
