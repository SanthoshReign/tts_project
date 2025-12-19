from pydantic import BaseModel


class UserNameBranch(BaseModel):
    name: str
    branch: str

    class Config:
        from_attributes = True