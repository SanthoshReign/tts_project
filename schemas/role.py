from typing import Optional

from pydantic import BaseModel


class CreateRole(BaseModel):
    role_name: str
    permission: str

class UpdateRole(BaseModel):
    role_name: Optional[str] = None
    permission: Optional[str] = None

    class Config:
        from_attributes = True

# ------------ response model ------------
class RoleResponse(BaseModel):
    id: int
    role_name: str
    permission: str

    class Config:
        from_attributes = True
