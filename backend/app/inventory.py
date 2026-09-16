from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.models import User
from app.main import current_user, require_role

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])

INVENTORY: dict[UUID, dict] = {}


class InventoryItemCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=150)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)


class InventoryAdjustment(BaseModel):
    quantity: int = Field(ge=0)


@router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: InventoryItemCreate, user: User = Depends(require_role("WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN"))):
    item_id = uuid4()
    item = {
        "id": str(item_id),
        "sku": payload.sku,
        "name": payload.name,
        "quantity": payload.quantity,
        "reorder_level": payload.reorder_level,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    INVENTORY[item_id] = item
    return item


@router.get("/items")
def list_items(user: User = Depends(current_user)):
    return list(INVENTORY.values())


@router.patch("/items/{item_id}")
def adjust_item(item_id: UUID, payload: InventoryAdjustment, user: User = Depends(require_role("WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN"))):
    item = INVENTORY.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    item["quantity"] = payload.quantity
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return item
