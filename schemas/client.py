
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
    sales_branch_manager: str
    designer: str

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

    sales_branch_manager: str
    designer: str

    class Config:
        from_attributes = True

# ------------------- Update Client --------------

class UpdateClient(BaseModel):
    name: Optional[str]= None
    dob: Optional[date]= None
    email: Optional[EmailStr]= None
    anniversary: Optional[date] = None
    mobile: Optional[str]= None
    occupation: Optional[str]= None
    address_of_property: Optional[str]= None
    project_value: Optional[int]= None
    location: Optional[str]= None
    type_of_property: Optional[str]= None
    billing_address: Optional[str]= None
    sales_branch_manager: Optional[str]= None
    designer: Optional[str]= None

    class Config:
        from_attributes = True
