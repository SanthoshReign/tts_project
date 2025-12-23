from decimal import Decimal

from sqlalchemy import Column, Integer, String, Date, Float

from db import Base

class VendorPayment(Base):
    __tablename__ = "vendor_payments"

    id = Column(Integer, primary_key = True, index = True)

    vendor_name = Column(String(100), index = True)
    branch = Column(String(60))

    invoice_date = Column(Date)
    invoice_no = Column(String(100))
    invoice_path = Column(String(255))

    total_amount = Column(Float)
    amount_paid = Column(Float)
    balance = Column(Float)

    payment_method = Column(String(60))
    payment_date = Column(Date)
    status = Column(String(60))
