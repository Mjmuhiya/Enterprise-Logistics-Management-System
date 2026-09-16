from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user, require_role
from app.models import InventoryItem, User, Warehouse

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


class InventoryItemCreate(BaseModel):
    warehouse_id: UUID
    sku: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)


class InventoryAdjustment(BaseModel):
    quantity: int = Field(ge=0)


@router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: InventoryItemCreate, _: User = Depends(require_role("WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    if not db.get(Warehouse, payload.warehouse_id):
        raise HTTPException(status_code=404, detail="Warehouse not found")
    existing = db.scalar(select(InventoryItem).where(InventoryItem.warehouse_id == payload.warehouse_id, InventoryItem.sku == payload.sku))
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists in this warehouse")
    item = InventoryItem(warehouse_id=payload.warehouse_id, sku=payload.sku, item_name=payload.name, quantity=payload.quantity, reorder_level=payload.reorder_level)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item_response(item)


@router.get("/items")
def list_items(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return [item_response(item) for item in db.scalars(select(InventoryItem).order_by(InventoryItem.sku))]


@router.patch("/items/{item_id}")
def adjust_item(item_id: UUID, payload: InventoryAdjustment, _: User = Depends(require_role("WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    return item_response(item)


def item_response(item: InventoryItem) -> dict:
    return {
        "id": str(item.id),
        "warehouse_id": str(item.warehouse_id),
        "sku": item.sku,
        "name": item.item_name,
        "quantity": item.quantity,
        "reorder_level": item.reorder_level,
        "low_stock": item.quantity <= item.reorder_level,
    }
