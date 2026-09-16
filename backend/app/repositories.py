from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Role, Shipment, ShipmentStatusHistory, User


def get_role(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name.upper()))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_customer_by_user_id(db: Session, user_id: UUID) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.user_id == user_id))


def get_shipment(db: Session, shipment_id: UUID) -> Shipment | None:
    return db.get(Shipment, shipment_id)


def list_shipments(db: Session, customer_id: UUID | None = None) -> list[Shipment]:
    statement = select(Shipment).order_by(Shipment.created_at.desc())
    if customer_id:
        statement = statement.where(Shipment.customer_id == customer_id)
    return list(db.scalars(statement))


def add_status_history(db: Session, shipment_id: UUID, old_status: str | None, new_status: str, user_id: UUID, notes: str | None = None) -> ShipmentStatusHistory:
    history = ShipmentStatusHistory(
        shipment_id=shipment_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=user_id,
        notes=notes,
    )
    db.add(history)
    return history
