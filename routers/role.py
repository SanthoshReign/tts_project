from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from db import getDb
from models.role import Role
from schemas.role import CreateRole, UpdateRole, RoleResponse

router = APIRouter(prefix = '/roles', tags = ['Roles'])

# -------------------------------- Create Role ----------------------------------
@router.post('/create-role')
def create_role(role: CreateRole, db : Session = Depends(getDb)):
    existing = db.query(Role).filter(Role.role_name == role.role_name).first()

    if existing:
        raise HTTPException(status_code = 401, detail = "Role already exist")

    new_role = Role(role_name = role.role_name, permission = role.permission)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {"message": "Role created Successfully"}

# -------------------------------- Get All Roles ----------------------------------
@router.get('/', response_model = list[RoleResponse])
def get_roles(db: Session = Depends(getDb)):
    return db.query(Role).all()

# --------------------------------- Update Role ------------------------------------
@router.patch('/update-role/{role_id}')
def update_role(role_id: int, role_update : UpdateRole = Body(...), db: Session = Depends(getDb)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code = 404, detail = "Role not found")

    updates = role_update.model_dump(exclude_unset=True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)

    return {
        "message": "Client Updated Successfully",
        "Updated fields": list(updates.keys())
    }

# --------------------------------- Delete Role ------------------------------------
@router.delete("/delete-role/{role_id}")
def delete_role(role_id: int, db: Session = Depends(getDb)):
    role = db.query(Role).filter(Role.id == role_id).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(role)
    db.commit()

    return {
        "message": f"role {role.role_name} is deleted successfully"
    }



