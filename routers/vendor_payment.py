from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db import getDb
from models.vendor_payment import VendorPayment
from schemas.vendor_payment import VendorPaymentCreate, UpdateVendorPayment
from utils.cloudinary_upload import upload_invoice_pdf
from utils.invoice_generator import generate_invoice_pdf

router = APIRouter(prefix='/vendor_payments' ,tags=['vendor_payments'])

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_status(total, paid):
    if paid >= total:
        return "PAID"
    elif paid < total > 0:
        return "PARTIAL"
    else:
        return "UNPAID"

@router.post('/create-vendor-payment')
def create_vendor_payment(ven_pay: VendorPaymentCreate, db: Session = Depends(getDb)):
    balance = ven_pay.total_amount - ven_pay.amount_paid

    invoice_no = generate_invoice_number()
    status = generate_status(ven_pay.total_amount, ven_pay.amount_paid)

    new_vendor_payment = VendorPayment(
        vendor_name= ven_pay.vendor_name,
        branch = ven_pay.branch,
        invoice_date= date.today(),
        invoice_no = invoice_no,
        total_amount = ven_pay.total_amount,
        amount_paid = ven_pay.amount_paid,
        balance = balance,

        payment_method = ven_pay.payment_method,
        payment_date = ven_pay.payment_date,
        status = status
    )

    db.add(new_vendor_payment)
    db.commit()

    # Auto generate invoice
    invoice_path = generate_invoice_pdf(new_vendor_payment)

    # Upload to Cloudinary
    invoice_url = upload_invoice_pdf(invoice_path, invoice_no)


    new_vendor_payment.invoice_path = invoice_url
    db.commit()

    return {
        "message": "Vendor Payment added successfully",
        "vendor_name" : new_vendor_payment.vendor_name,
        "invoice_no" : new_vendor_payment.invoice_no,
        "invoice_date" : new_vendor_payment.invoice_date
    }

# -----------------------------------------------------------------------------

@router.get("/invoice/{invoice_no}")
def download_invoice(invoice_no: str, db: Session = Depends(getDb)):
    payment = db.query(VendorPayment).filter(
        VendorPayment.invoice_no == invoice_no
    ).first()

    if not payment or not payment.invoice_path:
        raise HTTPException(404, "Invoice not found")

    # return FileResponse(payment.invoice_path, media_type="application/pdf")
    return payment


# ---------------------------------------------------------------------------------
@router.patch('/update-vendor-payment/{invoice_no}')
def update_vendor_payment(invoice_no: str, update_data : UpdateVendorPayment = Body(...),db: Session = Depends(getDb)):
    vendor = db.query(VendorPayment).filter(VendorPayment.invoice_no == invoice_no).first()

    if not vendor:
        raise HTTPException(status_code = 404, detail = "Vendor Payment not found")

    updates = update_data.model_dump(exclude_unset = True)

    if not updates:
        return {"Message": "No updates"}

    # change/update only needed fields
    for field, value in updates.items():
        setattr(vendor, field, value)

    # recalculate balance AFTER updates
    if "amount_paid" in updates or "total_amount" in updates:
        vendor.balance = vendor.total_amount - vendor.amount_paid

    db.commit()
    db.refresh(vendor)

    return {
        "message": "Vendor Payment Updated Successfully",
        "Updated fields": list(updates.keys())
    }

# -----------------------------------------------------------------------------------------
@router.delete('/delete-vendor-payment/{invoice_no}')
def delete_vendor_payment(invoice_no: str, db: Session = Depends(getDb)):
    vendor = db.query(VendorPayment).filter(VendorPayment.invoice_no == invoice_no).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor Payment not found")

    db.delete(vendor)
    db.commit()

    return {
        "message": "Vendor Payment details deleted successfully"
    }

# ------------------------------------------------------------------------------------------