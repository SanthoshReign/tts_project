# Linking Vendor and Client
# Many-to-Many relationship - one client may have multiple vendors and
# one vendor may have many clients.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from db import getDb
from models import Client
from models.vendor import Vendor

from schemas.vendor_client import VendorWithClients, ClientWithVendors


router = APIRouter(prefix = "/vendor_client", tags=['vendor_client'])

# LINKING VENDOR AND CLIENT
@router.post("/vendors/{vendor_id}/clients/{client_id}")
def link_vendor_client(
        vendor_id: int,
        client_id: int,
        db: Session = Depends(getDb),
):
    vendor = db.get(Vendor, vendor_id)
    client = db.get(Client, client_id)

    if not vendor or not client:
        raise HTTPException(status_code = 404, detail = "Vendor or Client not found")

    if client not in vendor.clients:
        vendor.clients.append(client)
    db.commit()

    return {
        "message": "Vendor linked to client"
    }



@router.get("/vendors/{vendor_id}/clients", response_model=VendorWithClients)
def get_vendor_clients(
        vendor_id: int,
        db: Session = Depends(getDb),
):
    vendor = (
        db.query(Vendor)
        .options(joinedload(Vendor.clients))
        .filter(Vendor.id == vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor


@router.get(
    "/clients/{client_id}/vendors",
    response_model=ClientWithVendors,
)
def get_client_vendors(
    client_id: int,
    db: Session = Depends(getDb),
):
    # an sql query
    client = (
        db.query(Client)
        .options(joinedload(Client.vendors))
        .filter(Client.id == client_id)
        .first()
    )

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client