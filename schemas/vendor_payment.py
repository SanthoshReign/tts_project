from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class VendorPaymentCreate(BaseModel):
    vendor_name: str
    branch: str

    total_amount: float= Field(default=0, ge=0)
    amount_paid: float = Field(default=0, ge=0)

    payment_method: str
    payment_date: date

class UpdateVendorPayment(BaseModel):
    vendor_name: Optional[str] = None
    branch: Optional[str] = None

    total_amount: Optional[float] = Field(default=0, ge=0)
    amount_paid: Optional[float] = Field(default=0, ge=0)

    payment_method: Optional[str] = None
    payment_date: Optional[date] = None

    class Config:
        from_attributes = True
