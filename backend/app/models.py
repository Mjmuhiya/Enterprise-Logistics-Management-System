from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    role: Mapped[Role] = relationship()
    customer: Mapped["Customer | None"] = relationship(back_populates="user", uselist=False)
    driver: Mapped["Driver | None"] = relationship(back_populates="user", uselist=False)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    user: Mapped[User] = relationship(back_populates="customer")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="customer")


class Driver(Base):
    __tablename__ = "drivers"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    licence_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    availability_status: Mapped[str] = mapped_column(String(30), default="AVAILABLE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    user: Mapped[User] = relationship(back_populates="driver")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="AVAILABLE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="vehicle")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    inventory_items: Mapped[list["InventoryItem"]] = relationship(back_populates="warehouse")


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warehouse: Mapped[Warehouse] = relationship(back_populates="inventory_items")


class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tracking_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    driver_id: Mapped[UUID | None] = mapped_column(ForeignKey("drivers.id"), index=True)
    vehicle_id: Mapped[UUID | None] = mapped_column(ForeignKey("vehicles.id"), index=True)
    origin_address: Mapped[str] = mapped_column(Text, nullable=False)
    destination_address: Mapped[str] = mapped_column(Text, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="CREATED", nullable=False, index=True)
    estimated_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    customer: Mapped[Customer] = relationship(back_populates="shipments")
    driver: Mapped["Driver | None"] = relationship(back_populates="shipments")
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="shipments")


class ShipmentStatusHistory(Base):
    __tablename__ = "shipment_status_history"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status: Mapped[str | None] = mapped_column(String(40))
    new_status: Mapped[str] = mapped_column(String(40), nullable=False)
    changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    driver_id: Mapped[UUID | None] = mapped_column(ForeignKey("drivers.id"))
    vehicle_id: Mapped[UUID | None] = mapped_column(ForeignKey("vehicles.id"))
    route_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_distance_km: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    optimisation_method: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    stops: Mapped[list["RouteStop"]] = relationship(back_populates="route", cascade="all, delete-orphan")


class RouteStop(Base):
    __tablename__ = "route_stops"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    route_id: Mapped[UUID] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.id"), nullable=False)
    stop_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_arrival_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    route: Mapped[Route] = relationship(back_populates="stops")


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.id"), unique=True, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ISSUED", nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    shipment_id: Mapped[UUID | None] = mapped_column(ForeignKey("shipments.id"))
    channel: Mapped[str] = mapped_column(String(20), default="EMAIL", nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
