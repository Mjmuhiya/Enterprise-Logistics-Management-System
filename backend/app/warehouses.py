from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user, require_role
from app.models import User, Warehouse

router = APIRouter(prefix="/api/v1/warehouses", tags=["Warehouses"])


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    address: str = Field(min_length=5)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_warehouse(payload: WarehouseCreate, _: User = Depends(require_role("WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    warehouse = Warehouse(name=payload.name, address=payload.address)
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse_response(warehouse)


@router.get("")
def list_warehouses(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return [warehouse_response(item) for item in db.scalars(select(Warehouse).order_by(Warehouse.created_at.desc()))]


def warehouse_response(warehouse: Warehouse) -> dict:
    return {"id": str(warehouse.id), "name": warehouse.name, "address": warehouse.address, "created_at": warehouse.created_at}
