from fastapi import Depends, HTTPException, Body, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from db import getDb
from auths.auth import hash_password, verify_password, create_token, create_reset_token, decode_token
from jose import JWTError

from models.user import User
from schemas.user import SuccessMessage, CreateUser, LoginUser, GetUser, UpdateUser

token_auth_scheme = HTTPBearer()

router = APIRouter(prefix = '/user', tags = ['User'])

# --------------------------------
# SIGN UP
# --------------------------------
@router.post('/create-user', response_model = SuccessMessage)
def signup(user: CreateUser, db: Session = Depends(getDb)):
    # check existing 'user'
    # 'User' - database, user - incoming user credentials from front-end
    existing = db.query(User).filter((User.email == user.email) or (User.username == user.username)).first()

    if existing:
        raise HTTPException(status_code = 400, detail = "Username or Email already exist")

    hashed_password = hash_password(user.password)

    new_user = User(username = user.username, email = user.email, password_hashed = hashed_password,
                    branch = user.branch, team = user.team, role = user.role.capitalize())

    db.add(new_user)
    db.commit()        # update changes on the database
    db.refresh(new_user)

    return {"message": "User Registered Successfully", "username" : new_user.username, "email": new_user.email}

# ---------------------------------------
# LOGIN
# ---------------------------------------

@router.post('/login')
def login(
        user: LoginUser,
        db: Session = Depends(getDb)
):
    # check user email in the database first
    db_user = db.query(User).filter(User.email == user.email).first()

    # if not db_user.is_active:
    #     raise HTTPException(status_code = 400, detail = "User has been deleted")

    if not db_user:
        raise HTTPException(status_code = 400, detail = "Invalid Email")

    if not verify_password(user.password, db_user.password_hashed):
        raise HTTPException(status_code = 400, detail = "Invalid Password")

    token = create_token({'sub': db_user.email, 'user_id': db_user.id, 'role': db_user.role})

    return {
        "message" : "Login Successfully!",
        "access_token": token,
        "token_type": "bearer",
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "branch": db_user.branch,
        "team": db_user.team,
        "role": db_user.role
    }

# ------------------------------------------------
# FORGOT PASSWORD
# ------------------------------------------------

@router.post('/forgot-password')
def forgot_password(email: str, db: Session = Depends(getDb)):
    # User is the database class
    password_reset_user = db.query(User).filter(User.email == email).first()

    if not password_reset_user:
        raise HTTPException(status_code = 401, detail = "User not found")

    # Generate reset token
    reset_token = create_reset_token(password_reset_user.email)

    # now, we need to send reset link to email, but for simplicity we are just printing and returning it
    reset_link = f"http://localhost:8000/reset-token?token={reset_token}" # now, we need to create the endpoint /reset-token

    print("Password Reset link: ", reset_link)

    return {
        "message" : "Password reset link is sent to you email",
        "Reset Link": reset_link
    }


# ------------------------------------------------------
# RESET PASSWORD
# ------------------------------------------------------

@router.post("/reset-password")                                    # Depends - dependency injection
def reset_password(token: str, new_password: str, db: Session = Depends(getDb)):
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        payload = decode_token(token)

        if payload.get("purpose") != "Password_Reset":
            raise HTTPException(status_code = 400, detail = "Invalid Token")

        email = payload.get('sub')

    except JWTError:
        raise HTTPException(status_code= 401, detail = "Invalid or expired token")

    # find the user in the database
    password_reset_user = db.query(User).filter(User.email == email).first()

    if not password_reset_user:
        raise HTTPException(status_code = 404, detail = "User not found")

    # Update and commit new password
    password_reset_user.password_hashed = hash_password(new_password)
    db.add(password_reset_user) # sometimes this line is necessary
    db.commit()
    db.refresh(password_reset_user)

    return {"message": "Password has been reset successfully!!!"}


# ------------------------------------------------------------
# GET USER DETAILS
# ------------------------------------------------------------
# SHOW USER DETAILS USING TOKEN

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme), db: Session = Depends(getDb)):
    # extract token only without "Bearer "
    token = credentials.credentials
    try:
        payload = decode_token(token)
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code = 401, detail= "Invalid Token")

    except JWTError:
        raise HTTPException(status_code = 401, detail= "Unauthorised Token")

    # find user on the database using email
    user_details = db.query(User).filter(User.email == email).first()

    if not user_details:
        raise HTTPException(status_code = 404, detail = "User not found")

    return user_details

@router.get("/get-user", response_model = GetUser)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "branch": current_user.branch,
        "team": current_user.team,
        "role": current_user.role,
        "is_active": current_user.is_active
    }

# ------------------------------------------------------------
# UPDATE USER (EMPLOYEE IS ALLOWED TO UPDATE ONLY USERNAME, PASSWORD, AND EMAIL ( PASSWORD IS HANDLED SEPARATELY)
# ------------------------------------------------------------
# Why ONE API is Better
# Multiple APIs (BAD at scale)
# POST /user/update-email
# POST /user/update-password
# POST /user/update-role
# POST /user/update-status
#
# Problems:
# API explosion
# Hard to maintain
# Hard to version
# More frontend complexity
# More permissions logic duplicated

# Use ONE update API per resource (user), not separate APIs for each field.
# Use PATCH (partial update), not PUT.
# Benefits:
# Clean REST design
# Scales well
# Easy frontend integration
# Easier RBAC
# Easier auditing

@router.patch('/update-user/me')
def update_user_profile(new_data: UpdateUser = Body(...), db: Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    updates = new_data.model_dump(exclude_unset = True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(current_user, field, value)

    # allow only admins to change team, branch, role, active status of an employee

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Update Successfully",
        "Updated fields": list(updates.keys())
    }
