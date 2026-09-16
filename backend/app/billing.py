from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import current_user, require_role
from app.models import Invoice, Shipment, User

router = APIRouter(prefix="/api/v1/invoices", tags=["Billing"])


class InvoiceCreate(BaseModel):
    shipment_id: UUID
    subtotal: Decimal = Field(ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, _: User = Depends(require_role("FINANCE_OFFICER", "OPERATIONS_MANAGER", "ADMIN")), db: Session = Depends(get_db)):
    if not db.get(Shipment, payload.shipment_id):
        raise HTTPException(status_code=404, detail="Shipment not found")
    if db.scalar(select(Invoice).where(Invoice.shipment_id == payload.shipment_id)):
        raise HTTPException(status_code=409, detail="Invoice already exists for shipment")
    invoice = Invoice(
        invoice_number=f"INV-{uuid4().hex[:10].upper()}",
        shipment_id=payload.shipment_id,
        subtotal=payload.subtotal,
        tax_amount=payload.tax_amount,
        total_amount=payload.subtotal + payload.tax_amount,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice_response(invoice)


@router.get("")
def list_invoices(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return [invoice_response(item) for item in db.scalars(select(Invoice).order_by(Invoice.issued_at.desc()))]


def invoice_response(invoice: Invoice) -> dict:
    return {
        "id": str(invoice.id),
        "invoice_number": invoice.invoice_number,
        "shipment_id": str(invoice.shipment_id),
        "subtotal": float(invoice.subtotal),
        "tax_amount": float(invoice.tax_amount),
        "total_amount": float(invoice.total_amount),
        "status": invoice.status,
        "issued_at": invoice.issued_at,
    }
