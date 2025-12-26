import cloudinary.uploader
from io import BytesIO

def upload_invoice_pdf(pdf_bytes: bytes, invoice_no: str) -> str:
    response = cloudinary.uploader.upload(
        file=BytesIO(pdf_bytes),
        resource_type="raw",     # IMPORTANT for PDFs
        folder="invoices",
        public_id=invoice_no,
        overwrite=True
    )

    return response["secure_url"]