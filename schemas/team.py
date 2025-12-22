from typing import Optional
from pydantic import BaseModel
from auths.enums import Branches

# ----------- Adding Team -----------------

class AddTeam(BaseModel):
    team_name: str
    description: str
    branch: Branches
    status: bool

# ----------- Update Team ------------------

class UpdateTeam(BaseModel):
    team_name: Optional[str] = None
    description: Optional[str] = None
    branch: Optional[Branches] = None
    status: Optional[bool] = None

# ------------ Team Response ------------------

class TeamResponse(BaseModel):
    id: int
    team_name: str
    description: Optional[str]
    # created_by: int
    branch: Branches
    status: bool

    class config:
        from_attributes = True