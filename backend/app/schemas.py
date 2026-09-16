from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "CUSTOMER"
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ShipmentCreate(BaseModel):
    origin: str = Field(min_length=2, max_length=1000)
    destination: str = Field(min_length=2, max_length=1000)
    weight_kg: float = Field(gt=0)
    tracking_number: str | None = Field(default=None, min_length=3, max_length=50)
    customer_id: UUID | None = None


class ShipmentStatusUpdate(BaseModel):
    status: str
    notes: str | None = Field(default=None, max_length=1000)
