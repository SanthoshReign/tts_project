
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

from schemas.common import UserNameBranch


# ------------- Create Client -----------------
class CreateClient(BaseModel):
    name: str
    dob: date
    email: EmailStr
    anniversary: Optional[date] = None
    mobile: str
    occupation: str
    address_of_property: str
    project_value: int
    location: str
    type_of_property: str
    billing_address: str

# ---------------- Get Client --------------
class GetClient(BaseModel):
    id: int
    name: str
    dob: date
    email: EmailStr
    anniversary: Optional[date] = None
    mobile: str
    occupation: str
    address_of_property: str
    project_value: int
    location: str
    type_of_property: str
    billing_address: str

    sales_branch_manager: UserNameBranch
    designer: UserNameBranch

    class Config:
        from_attributes = True
