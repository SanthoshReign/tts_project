import os
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_invoice_pdf(payment):
    buffer = BytesIO()
    os.makedirs("invoices", exist_ok = True)

    file_path = f"invoices/{payment.invoice_no}.pdf"
    c = canvas.Canvas(buffer, pagesize = A4)

    y = 800
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "vendor Payment Invoice")
    y -= 60
    # y -= 40
    # c.setFont("Helvetica", 10)
    # c.drawString(50, y, f"Invoice No: {vendor_payment.invoice_no}")
    # y -= 20
    # c.drawString(50, y, f"Vendor: {vendor_payment.vendor_name}")
    # y -= 20
    # c.drawString(50, y, f"Branch: {vendor_payment.branch}")
    # y -= 20
    # c.drawString(50, y, f"Date: {vendor_payment.invoice_date}")
    #
    # y -= 30
    # c.drawString(50, y, f"Date: {vendor_payment.payment_method}")
    #
    # c.drawString(50, y, f"Vendor: {vendor_payment.total_amount}")
    # y -= 20
    # c.drawString(50, y, f"Branch: {vendor_payment.amount_paid}")
    # y -= 20
    # c.drawString(50, y, f"Date: {vendor_payment.balance}")

    fields = [
        ("Invoice No", payment.invoice_no),
        ("Vendor Name", payment.vendor_name),
        ("Branch", payment.branch),
        ("Payment Date", str(payment.invoice_date)),
        ("Payment Method", payment.payment_method),
        ("Total Amount", f"{payment.total_amount:.2f}"),
        ("Amount Paid", f"{payment.amount_paid:.2f}"),
        ("Balance Amount", f"{payment.balance:.2f}"),
        ("Status", payment.status),
    ]

    for label, value in fields:
        c.drawString(50, y, f"{label}: {value}")
        y -= 25

    c.showPage()
    c.save()
    # return file_path

    buffer.seek(0)
    return buffer.read()