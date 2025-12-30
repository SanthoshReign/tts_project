from pydantic import BaseModel
from typing import List

from schemas.client import GetClient
from schemas.vendor import VendorResponse


class VendorWithClients(BaseModel):
    id: int
    vendor_name: str

    clients: List[GetClient] = []

    class Config:
        from_attributes = True

class ClientWithVendors(BaseModel):
    id: int
    name: str

    vendors: List[VendorResponse] = []

    class Config:
        from_attributes = True