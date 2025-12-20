from typing import Optional

from pydantic import BaseModel

from auths.enums import Branches


class AddVendor(BaseModel):
    vendor_name: str
    category: str
    contact_person: str
    phone: str
    address: str
    branch: Branches
    gst_no: str

class EditVendor(BaseModel):
    vendor_name : Optional[str] = None
    category: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    branch: Optional[Branches] = None
    gst_no: Optional[str] = None


class VendorResponse(BaseModel):
    id: int
    vendor_name: str
    category: str
    contact_person: str
    phone: str
    address: str
    branch: Branches
    gst_no: str

