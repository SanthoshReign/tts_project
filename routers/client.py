from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload

from db import getDb
from auths.permissions import require_permission
from routers.admin import require_admin
from routers.user import get_current_user
from schemas.client import CreateClient, GetClient, UpdateClient
from models.client import Client

router = APIRouter(prefix="/clients", tags=["Clients"])

token_auth_scheme = HTTPBearer()

@router.post('/create-client')
def create_client(client: CreateClient, admin = Depends(require_admin), db: Session = Depends(getDb)):
    # check if the client is already exist
    existing_client = db.query(Client).filter(Client.email == client.email).first()

    if existing_client:
        raise HTTPException(status_code = 401, detail = "Client already exist")

    new_client = Client(
        name = client.name,
        dob= client.dob,
        email= client.email,
        anniversary=client.anniversary,
        mobile = client.mobile,
        occupation = client.occupation,
        address_of_property = client.address_of_property,
        project_value = client.project_value,
        location = client.location,
        type_of_property = client.type_of_property,
        billing_address = client.billing_address
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {"message": "Client added successfully"}

# ---------------------------------------------------------------------------------------------------------------
# GET ALL CLIENTS - ANY EMPLOYEE

@router.get('/get-all-clients', response_model = list[GetClient])
def get_all_clients_details(access = Depends(get_current_user), user = Depends(require_permission("view_all_clients")), db: Session = Depends(getDb)):
    clients = db.query(Client).all()

    return clients

# -------------------------------------------------------------------------------------------------------------
# GET CLIENT - ANY EMPLOYEE

@router.get('/{client_id}', response_model = GetClient)
def get_client_details(client_id: int, access = Depends(get_current_user), user = Depends(require_permission("view")),db: Session = Depends(getDb)):
    client = (
        db.query(Client)
        .options(
            joinedload(Client.sales_managers_fk),
            joinedload(Client.designer_fk)
        )
        .filter(Client.id == client_id)
        .first()
    )

    if not client:
        raise HTTPException(
            status_code= 404,
            detail = "Client not found"
        )

    return client

# ---------------------------------------------------------------------------------------------------------------
# PATCH CLIENT (edit)

@router.patch('/{client_id')
def update_client(client_id: int, updateclient: UpdateClient = Body(...), db: Session = Depends(getDb)):
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code = 404, detail = "Client not found")

    updates = updateclient.model_dump(exclude_unset=True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(updateclient, field, value)

    db.commit()
    db.refresh(updateclient)

    return {
        "message": "Update Successfully",
        "Updated fields": list(updates.keys())
    }


