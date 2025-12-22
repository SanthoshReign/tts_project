from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class PaymentItemCreate(BaseModel):
    item_name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class PaymentCreate(BaseModel):
    vendor_name: str
    branch: str

    purchase_order_no: str
    purchase_order_date: date

    tax_percent: float = Field(default=0, ge=0)
    other_charges: float = Field(default=0, ge=0)
    paid_amount: float = Field(default=0, ge=0)

    payment_method: str
    payment_date: date

    items: List[PaymentItemCreate]

class PaymentItemResponse(BaseModel):
    item_name: str
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int

    vendor_name: str
    branch: str
    purchase_order_no: str
    purchase_order_date: date

    tax_percent: float = Field(default=0, ge=0)
    other_charges: float = Field(default=0, ge=0)


    subtotal: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    balance_amount: float

    payment_method: str
    payment_date: date

    # created_at: date

    items: List[PaymentItemResponse]

    class Config:
        from_attributes = True


# ------------------------------------- UPDATE -------------------------------------

class PaymentItemUpdate(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[float] = Field(default=None, gt=0)

class PaymentUpdate(BaseModel):
    vendor_name: Optional[str]
    branch: Optional[str]
    purchase_order_date: Optional[date]

    tax_percent: Optional[float] = Field(ge=0)
    other_charges: Optional[float] = Field(ge=0)
    paid_amount: Optional[float] = Field(ge=0)

    items: Optional[List[PaymentItemUpdate]]