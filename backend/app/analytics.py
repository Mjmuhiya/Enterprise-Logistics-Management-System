from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user
from app.models import Driver, InventoryItem, Shipment, User

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/operations")
def operations_summary(_: User = Depends(current_user), db: Session = Depends(get_db)):
    total_shipments = db.scalar(select(func.count()).select_from(Shipment)) or 0
    delivered = db.scalar(select(func.count()).select_from(Shipment).where(Shipment.status == "DELIVERED")) or 0
    active_fleet = db.scalar(select(func.count()).select_from(Driver).where(Driver.availability_status == "ASSIGNED")) or 0
    low_stock = db.scalar(select(func.count()).select_from(InventoryItem).where(InventoryItem.quantity <= InventoryItem.reorder_level)) or 0
    delivery_success_rate = round((delivered / total_shipments) * 100, 2) if total_shipments else 0.0
    status_rows = db.execute(select(Shipment.status, func.count()).group_by(Shipment.status)).all()
    return {
        "total_shipments": total_shipments,
        "delivered_shipments": delivered,
        "delivery_success_rate_percent": delivery_success_rate,
        "assigned_drivers": active_fleet,
        "low_stock_items": low_stock,
        "shipments_by_status": {status: count for status, count in status_rows},
    }
