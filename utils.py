# utils.py
# PDF generation & some helpers

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import datetime
import os
from PIL import Image

def generate_bill_pdf_bytes(bill: dict, logo_path: str = "logo.png", paid_stamp: bool = False) -> bytes:
    """
    Generate a professional PDF for a single bill.
    - bill: dict with keys like bill_no, customer_name, customer_type, units, energy_charge, fixed_charge, gst, total, status, created_at
    - logo_path: optional path to a small logo file in project folder (png/jpg), else header text used
    - paid_stamp: if True, a 'PAID' watermark is added
    Returns: bytes of PDF
    """

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 18 * mm

    # Header: logo (left) and company info (right)
    y = height - margin
    if os.path.exists(logo_path):
        try:
            # load and resize image to fit
            img = Image.open(logo_path)
            # keep aspect ratio: max width 40mm, max height 20mm
            max_w = 40 * mm
            max_h = 20 * mm
            ratio = min(max_w / img.width * mm, max_h / img.height * mm)
            img_reader = ImageReader(logo_path)
            c.drawImage(img_reader, margin, y - 20*mm, width=40*mm, preserveAspectRatio=True, mask='auto')
        except Exception:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, y - 10, "Electricity Board")
    else:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y - 10, "Electricity Board")

    # Company details on right
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - margin, y - 4, "Electricity Board Pvt. Ltd.")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, y - 16, "123, Powerhouse Road, City, State")
    c.drawRightString(width - margin, y - 28, "Phone: +91-99999-99999 | support@electricityboard.com")

    # Horizontal rule
    c.setStrokeColor(colors.HexColor("#1f77b4"))
    c.setLineWidth(1.5)
    c.line(margin, y - 32, width - margin, y - 32)

    # Bill title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y - 48, f"Tax Invoice / Electricity Bill")
    c.setFont("Helvetica", 9)
    c.drawString(margin, y - 62, f"Issue Date: {bill.get('created_at')}")

    # Bill information box
    box_y = y - 90
    box_h = 60
    c.roundRect(margin, box_y - box_h, width - 2*margin, box_h, 6, stroke=1, fill=0)

    # Left column: customer details
    left_x = margin + 6
    cx = left_x
    cy = box_y - 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(cx, cy, "BILL TO:")
    c.setFont("Helvetica", 9)
    c.drawString(cx, cy - 14, f"Name: {bill.get('customer_name')}")
    c.drawString(cx, cy - 28, f"Type: {bill.get('customer_type')}")
    c.drawString(cx, cy - 42, f"Bill No: {bill.get('bill_no')}")

    # Right column: invoice meta
    rx = width - margin - 140
    c.setFont("Helvetica-Bold", 10)
    c.drawString(rx, cy, "Invoice Details:")
    c.setFont("Helvetica", 9)
    c.drawString(rx, cy - 14, f"Date: {bill.get('created_at')}")
    c.drawString(rx, cy - 28, f"Status: {bill.get('status')}")
    c.drawString(rx, cy - 42, f"Units: {bill.get('units')} kWh")

    # Charges table header
    table_top = box_y - box_h - 20
    col1_x = margin
    col2_x = width - margin - 80
    row_h = 18

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#f2f2f2"))
    c.rect(col1_x, table_top - row_h, width - 2*margin, row_h, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawString(col1_x + 6, table_top - 14, "Charge Description")
    c.drawRightString(width - margin - 6, table_top - 14, "Amount (₹)")

    # Charges rows
    charges = [
        ("Energy Charge", bill.get("energy_charge", 0.0)),
        ("Fixed Charge", bill.get("fixed_charge", 0.0)),
        ("GST (18%)", bill.get("gst", 0.0)),
    ]
    y_row = table_top - row_h
    c.setFont("Helvetica", 10)
    for desc, amt in charges:
        y_row -= row_h
        c.drawString(col1_x + 6, y_row + 6, desc)
        c.drawRightString(width - margin - 6, y_row + 6, f"₹ {amt:,.2f}")

    # Spacer
    y_row -= 6

    # Total row
    y_row -= row_h
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#fff7e6"))
    c.rect(col1_x, y_row, width - 2*margin, row_h, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawString(col1_x + 6, y_row + 6, "Total Payable")
    c.drawRightString(width - margin - 6, y_row + 6, f"₹ {bill.get('total', 0.0):,.2f}")

    # Payment notes and signature
    notes_y = y_row - 40
    c.setFont("Helvetica-Oblique", 9)
    note_text = "Please pay within 15 days. Late payment may attract surcharge. For disputes contact support@electricityboard.com"
    c.drawString(margin, notes_y + 20, note_text)

    # Signature box
    sig_x = width - margin - 120
    c.line(sig_x, notes_y - 6, sig_x + 120, notes_y - 6)
    c.setFont("Helvetica", 9)
    c.drawRightString(sig_x + 120, notes_y - 18, "Authorized Signatory")

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    footer_text = f"Generated: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | Electricity Board Pvt. Ltd. | www.example.com"
    c.drawCentredString(width/2, 15*mm, footer_text)

    # Optional PAID watermark
    if paid_stamp or (str(bill.get("status")).lower() == "paid"):
        c.saveState()
        c.setFont("Helvetica-Bold", 80)
        c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
        c.translate(width/2, height/2)
        c.rotate(30)
        c.drawCentredString(0, 0, "PAID")
        c.restoreState()

    c.showPage()
    c.save()
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
