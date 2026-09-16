from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models import Customer, Shipment, User
from app.repositories import add_status_history, get_customer_by_user_id, get_role, get_user_by_email
from app.security import hash_password, verify_password


VALID_ROLES = {"ADMIN", "CUSTOMER", "DRIVER", "WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "FINANCE_OFFICER"}


def register_user(db: Session, email: str, password: str, role_name: str = "CUSTOMER", first_name: str = "", last_name: str = "") -> User:
    role_name = role_name.upper()
    if role_name not in VALID_ROLES:
        raise ValueError("Invalid role")
    if get_user_by_email(db, email):
        raise ValueError("User already exists")
    role = get_role(db, role_name)
    if role is None:
        raise ValueError("Role is not seeded in the database")
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        role_id=role.id,
        first_name=first_name,
        last_name=last_name,
    )
    db.add(user)
    db.flush()
    if role_name == "CUSTOMER":
        db.add(Customer(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def create_shipment(db: Session, customer_id: UUID, origin: str, destination: str, weight_kg: float, tracking_number: str | None = None) -> Shipment:
    shipment = Shipment(
        tracking_number=tracking_number or f"LF-{uuid4().hex[:12].upper()}",
        customer_id=customer_id,
        origin_address=origin,
        destination_address=destination,
        weight_kg=weight_kg,
        status="CREATED",
    )
    db.add(shipment)
    db.flush()
    db.add(ShipmentStatusHistory(shipment_id=shipment.id, old_status=None, new_status="CREATED"))
    db.commit()
    db.refresh(shipment)
    return shipment
