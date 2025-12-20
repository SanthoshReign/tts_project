from pydantic import BaseModel


class UserNameBranch(BaseModel):
    id: int
    name: str
    branch: str

    class Config:
        from_attributes = True