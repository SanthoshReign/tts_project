from sqlalchemy import Column, Integer, String

from auths.enums import Branches
from db import Base


class Vendor(Base):
    id = Column(Integer, primary_keys = True)
    vendor_name = Column(String)
    category = Column(String)
    contact_person = Column(String)
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(String)
    branch = Branches
    gst_no = Column(String)