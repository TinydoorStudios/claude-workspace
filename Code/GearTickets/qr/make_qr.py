#!/usr/bin/env python3
"""
Printable QR sheet for the gear ticket form — one code, every venue.

There used to be five codes, one per venue, each prefilling the Venue field.
That meant five different stickers to print, laminate, and keep on the right
road case, and a code that silently reports the wrong site the moment a case
moves. One code for everything is harder to get wrong: Venue is a required
dropdown on the form, so nobody can submit without picking one.

    python3 make_qr.py            # writes Gear_Ticket_QR_Codes.pdf next to this file
"""

import os

import qrcode
from qrcode.image.pil import PilImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

URL = "https://tickets.tinydoorstudios.com/form/gear-ticket"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Gear_Ticket_QR_Codes.pdf")
PNG_DIR = os.path.join(HERE, "png")
PNG = os.path.join(PNG_DIR, "GEAR_TICKET.png")


def qr_image(url: str) -> PilImage:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # survives scuffs and gaffe tape
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def build():
    os.makedirs(PNG_DIR, exist_ok=True)
    qr_image(URL).save(PNG)

    c = canvas.Canvas(OUT, pagesize=letter)
    page_w, page_h = letter

    c.setFillColorRGB(0.12, 0.16, 0.22)
    c.rect(0, page_h - 1.5 * inch, page_w, 1.5 * inch, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(page_w / 2, page_h - 1.02 * inch, "SOMETHING BROKEN?")

    c.setFillColorRGB(0.12, 0.16, 0.22)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(page_w / 2, page_h - 2.45 * inch, "SCAN IT. PICK YOUR SITE.")

    size = 4.6 * inch
    c.drawImage(
        ImageReader(PNG),
        (page_w - size) / 2,
        page_h - 7.6 * inch,
        width=size,
        height=size,
    )

    c.setFont("Helvetica", 20)
    c.drawCentredString(page_w / 2, page_h - 8.15 * inch, "Tell us what happened. Add photos.")
    c.setFont("Helvetica", 15)
    c.setFillColorRGB(0.35, 0.38, 0.43)
    c.drawCentredString(page_w / 2, page_h - 8.55 * inch, "Takes about 30 seconds. No login, no app.")

    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.35, 0.38, 0.43)
    c.drawCentredString(page_w / 2, 1.15 * inch, "For questions, call")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(0.12, 0.16, 0.22)
    c.drawCentredString(page_w / 2, 0.88 * inch, "Brian Lloyd  ·  315-404-5648")

    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.6, 0.62, 0.66)
    c.drawCentredString(page_w / 2, 0.45 * inch, URL)

    c.showPage()
    c.save()
    print(f"wrote {OUT}")
    print(f"png   {PNG}")
    print(f"url   {URL}")


if __name__ == "__main__":
    build()
