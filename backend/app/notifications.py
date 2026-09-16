from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import Notification, User

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


class NotificationCreate(BaseModel):
    user_id: UUID
    shipment_id: UUID | None = None
    subject: str = Field(min_length=2, max_length=255)
    body: str = Field(min_length=2)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, _: User = Depends(require_role("OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    notification = Notification(
        user_id=payload.user_id,
        shipment_id=payload.shipment_id,
        channel="EMAIL",
        subject=payload.subject,
        body=payload.body,
        status="PENDING",
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification_response(notification)


@router.get("/user/{user_id}")
def list_user_notifications(user_id: UUID, _: User = Depends(require_role("CUSTOMER", "DRIVER", "WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    notifications = db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()))
    return [notification_response(item) for item in notifications]


def notification_response(item: Notification) -> dict:
    return {
        "id": str(item.id),
        "user_id": str(item.user_id),
        "shipment_id": str(item.shipment_id) if item.shipment_id else None,
        "channel": item.channel,
        "subject": item.subject,
        "body": item.body,
        "status": item.status,
        "created_at": item.created_at,
    }
