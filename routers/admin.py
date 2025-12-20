from fastapi import Depends, HTTPException, Body, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from auths.auth import decode_token
from datetime import datetime, UTC

from db import getDb
from auths.permissions import require_permission
from models.user import User, AuditLog
from schemas.user import AdminUpdateUser, GetUser

token_auth_scheme = HTTPBearer()

router = APIRouter(prefix = '/admin', tags = ['Admin'])

def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    db: Session = Depends(getDb)
):
    # Allow access only if the authenticated user is an admin
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid or expired token"
        )

    user_id = payload.get('user_id')
    role = payload.get('role')

    # check expiry
    if payload.get('exp') and datetime.now(UTC).timestamp() > payload['exp']:
        raise HTTPException(status_code=401, detail="Token Expired")

    if role.lower() not in ["admin", "manager"]:
        raise HTTPException(
            status_code = 403,
            detail= 'Admin/manager privileges required'
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )

    return user

# ------------------------------------------------------------
# GET ALL USERS
# ------------------------------------------------------------

@router.get('/get-all-users', response_model = list[GetUser])
def get_all_users_details(
        # admin= Depends(require_admin) ,
        db: Session = Depends(getDb)
):

    users = db.query(User).all()

    return users

# ------------------------------------------------------------
# DELETE USER AFTER LOGIN BY ONLY ADMIN
# ------------------------------------------------------------

@router.delete("/delete-user/{employee_id}")
def delete_user(
        employee_id: int,
        # admin= Depends(require_permission("delete")),
        db: Session = Depends(getDb)
):
    # Delete the user by id and commit
    # admin_id = admin.id

    # Avoid admin deleting himself/herself
    # if admin_id == employee_id:
    #     raise HTTPException(status_code = 400, detail = "Admin cannot delete himself")

    # fetch deleting user from database
    deleting_user = db.query(User).filter(User.id == employee_id).first()

    if not deleting_user:
        raise HTTPException(status_code = 404, detail = "User not found")

    # if user is already deleted
    if not deleting_user.is_active:
        raise HTTPException(status_code = 404, detail = "User is already deleted")

    # One admin cannot delete another admin - Only a superadmin delete admin
    # if deleting_user.role.lower() == 'admin':
    #     raise HTTPException(status_code = 404, detail = "One admin cannot delete another admin")

    # No one can delete superadmin
    # if deleting_user.role.lower() == "superadmin":
    #     raise HTTPException(status_code = 403, detail = "Unauthorised to delete superadmin")

    # safe delete - deactivating employee
    deleting_user.is_active = False

    # Audit log
    # log = AuditLog(
    #     action = "Delete_user",
    #     performed_by = db.query(User.username).filter(User.id == admin_id).first(),
    #     target_user = deleting_user.username
    # )
    # db.add(log)
    db.commit()
    # db.refresh(log)
    db.refresh(deleting_user)

    return {"message": "User Deleted Successfully"}

# ------------------------------------------------------------
# UPDATE USER (ADMIN IS ALLOWED TO UPDATE ONLY TEAM, BRANCH, AND ROLE)
# ------------------------------------------------------------
@router.patch('/update-user')
def update_user_profile_admin(
        employee_id: int,
        updating_data : AdminUpdateUser = Body(...),
        # admin = Depends(require_permission("edit")),
        db: Session = Depends(getDb)
):
    # admin_id = admin.id

    employee_data = db.query(User).filter(User.id == employee_id).first()

    if not employee_data:
        raise HTTPException(status_code = 404, detail = "User not found")

    updates = updating_data.model_dump(exclude_unset=True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(employee_data, field, value)

    # allow only admins to change team, branch, role, active status of an employee

    db.commit()
    db.refresh(employee_data)

    return {
        "message": "Update Successfully",
        "Updated fields": list(updates.keys())
    }
