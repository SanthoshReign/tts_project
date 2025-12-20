from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ----------------------- Input response Format ----------------
# ----------- SignUp ---------------------
class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    branch: str
    team: str
    role: str

# ------------ Login ---------------------
class LoginUser(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str

# ------- Update User Details -------
class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# ------ Update User Details by Admin ---
class AdminUpdateUser(BaseModel):
    branch: Optional[str] = None
    team: Optional[str] = None
    role: Optional[str] = None

# --------------------- Output Response --------------------------
class UserOut(BaseModel):
    message: str
    access_token: str
    token_type: str
    id: int
    username: str
    email: EmailStr

    class config:
        # This allows Pydantic to read ORM objects directly
        orm_mode = True

class SuccessMessage(BaseModel):
    message: str
    username: str
    email: EmailStr

class GetUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    branch: str
    team: str
    role: str
    is_active: bool

    class config:
        # This allows Pydantic to read ORM objects directly
        orm_mode = True

