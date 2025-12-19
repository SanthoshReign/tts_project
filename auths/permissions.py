# Role -> permissions mapping
from fastapi import Depends, HTTPException

from routers.user import get_current_user

ROLE_PERMISSIONS = {
    "admin" : {"view", "view_all_users", "view_all_clients", "edit", "delete"},
    "manager": {"view", "view_all_clients", "edit"},
    "designer": {"view", "view_all_clients"},
    "employee": {"view", "view_all_clients"}
}

def require_permission(permission: str):
    def permission_checker(current_user = Depends(get_current_user)):
        role = current_user.role.lower()

        allowed_permissions = ROLE_PERMISSIONS.get(role, set())

        if permission not in allowed_permissions:
            raise HTTPException(
                status_code = 403,
                detail = f"{role} cannot perform '{permission}' action"
            )
        return current_user

    return permission_checker