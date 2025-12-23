from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from db import getDb
from models.vendor import Vendor
from schemas.vendor import AddVendor, VendorResponse, EditVendor

router = APIRouter(prefix = '/vendors', tags = ['vendors'])

# ----------------- ADD VENDOR ---------------------------------------------------------
@router.post('/add-vendor')
def add_vendor(vendor: AddVendor, db: Session = Depends(getDb)):
    existing = db.query(Vendor).filter(Vendor.vendor_name == vendor.vendor_name).first()

    if existing:
        raise HTTPException(status_code = 401, detail = "Vendor already exist")

    new_vendor = Vendor(
        vendor_name = vendor.vendor_name,
        category = vendor.category,
        contact_person = vendor.contact_person,
        phone = vendor.phone,
        address = vendor.address,
        branch = vendor.branch,
        gst_no = vendor.gst_no
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return {
        "message": "Vendor added successfully"
    }

# ---------------------- GET ALL VENDORS -------------------------------------------------
@router.get('/', response_model = list[VendorResponse])
def get_vendors(db: Session = Depends(getDb)):
    return db.query(Vendor).all()

# ---------------------- GET VENDOR ------------------------------------------------------
@router.get('/{vendor_id}', response_model = VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(getDb)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

    if not vendor:
        raise HTTPException(status_code = 404, detail = "Vendor not found")

    return vendor


# -------------------------- DELETE VENDOR -----------------------------------------------
@router.delete('/{vendor_id}')
def delete_vendor(vendor_id : int , db: Session = Depends(getDb)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    db.delete(vendor)
    db.commit()

# -------------------------- UPDATE VENDOR -----------------------------------------------------------------------------
@router.patch('/edit-vendor/{vendor_id}')
def edit_vendor(vendor_id: int, vendor_update : EditVendor = Body(...), db: Session = Depends(getDb)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    updates = vendor_update.model_dump(exclude_unset=True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)

    return {
        "message": "Vendor Updated Successfully",
        "Updated fields": list(updates.keys())
    }

# ----------------------------------------------------------------------------------------------------------------------