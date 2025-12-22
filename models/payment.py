from sqlalchemy import Column, Date, Integer, String, Float, ForeignKey, func, DECIMAL
from sqlalchemy.orm import relationship
from db import Base

class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id = Column(Integer, primary_key=True, index=True)

    vendor_name = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=False)

    purchase_order_no = Column(String)
    purchase_order_date = Column(Date)
    # reference_no = Column(String)

    tax_percent = Column(Float, default=0)
    other_charges = Column(Float, default=0)

    subtotal = Column(DECIMAL(12, 2))
    tax_amount = Column(Float)
    total_amount = Column(Float)

    paid_amount = Column(Float, default=0)
    balance_amount = Column(Float)

    payment_method = Column(String)
    payment_date = Column(Date)

    # created_at = Column(Date, server_default=func.now())

    items = relationship(
        "PaymentItem",
        back_populates="payment",
        cascade="all, delete-orphan"
    )

class PaymentItem(Base):
    __tablename__ = "payment_items"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payment_orders.id"), index = True)

    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    payment = relationship("PaymentOrder", back_populates="items")