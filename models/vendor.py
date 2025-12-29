from sqlalchemy import Column, Integer, String

from auths.enums import Branches
from db import Base


class Vendor(Base):
    __tablename__ = "vendor_table"

    id = Column(Integer, primary_key = True)
    vendor_name = Column(String)
    category = Column(String)
    contact_person = Column(String)
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(String)
    branch = Column(String, nullable = False)
    gst_no = Column(String)