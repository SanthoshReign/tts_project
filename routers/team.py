from fastapi import Depends, HTTPException, Body, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from db import getDb
from auths.auth import decode_token
from auths.permissions import require_permission

from models.team import Team
from schemas.team import TeamResponse, AddTeam, UpdateTeam

token_auth_scheme = HTTPBearer()

router = APIRouter(prefix='/team', tags = ['Teams'])

# ----------------------------------------------------------------------------------------------------------------------------------------------------
@router.post('/add-team', response_model = TeamResponse)
def add_team(
        team: AddTeam,
        credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
        db: Session = Depends(getDb),
        # current_user = Depends(require_admin)   # only admin
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get('role').lower() != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Admin privileges required'
        )

    # check if the team name is already exist on the database
    existing = db.query(Team).filter(Team.team_name == team.team_name and Team.branch == team.branch).first()

    if existing:
        raise HTTPException(status_code=400, detail="Team already exist in given branch")

    new_team = Team(
        team_name=team.team_name,
        description=team.description,
        created_by = payload.get('user_id'),
        branch=team.branch,
        status=team.status
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team

# ---------------------------------------------------------------------------------------------------------------------------------------------

@router.patch('/update-team/{team_id}')
def update_team(team_id: int,
                team_data: UpdateTeam = Body(...),
                admin= Depends(require_permission("edit")),
                db: Session = Depends(getDb)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code = 404, detail = "Team not found")

    updates = team_data.model_dump(exclude_unset=True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(team, field, value)

    # allow only admins to change team, branch, role, active status of an employee

    db.commit()
    db.refresh(team)

    return {
        "message": "Update Successfully",
        "Updated fields": list(updates.keys())
    }


# -----------------------------------------------------------------------------------------------------------
# only admin is allowed to delete user
@router.delete('/delete-team/{team_id}')
def delete_team(
        team_id: int,
        admin = Depends(require_permission("delete")),
        db: Session = Depends(getDb)
):
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code = 404, detail = "Team not found")

    db.delete(team)
    db.commit()

    return {"message" : "Team Deleted Successfully"}