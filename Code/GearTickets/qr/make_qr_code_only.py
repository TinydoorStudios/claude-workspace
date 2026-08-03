#!/usr/bin/env python3
"""
Compact QR card - the code plus the three things somebody needs to know.

Smaller and quieter than the full sheet in make_qr.py, so it fits on a road case
lid or a rack panel without shouting. Same code, same URL.

    python3 make_qr_code_only.py
"""

import os

import qrcode
from qrcode.image.pil import PilImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

URL = "https://tickets.tinydoorstudios.com/form/gear-ticket"

STEPS = [
    ("1", "Scan this code with your phone camera."),
    ("2", "Pick which site you're at."),
    ("3", "Say what happened. Add photos if you can."),
]

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Gear_Ticket_QR_Code_Only.pdf")
PNG = os.path.join(HERE, "png", "GEAR_TICKET.png")

INK = (0.12, 0.16, 0.22)
MUTED = (0.35, 0.38, 0.43)


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
    os.makedirs(os.path.dirname(PNG), exist_ok=True)
    qr_image(URL).save(PNG)

    c = canvas.Canvas(OUT, pagesize=letter)
    page_w, page_h = letter
    mid = page_w / 2

    c.setFillColorRGB(*INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(mid, page_h - 1.55 * inch, "SOMETHING BROKEN?")

    c.setFillColorRGB(*MUTED)
    c.setFont("Helvetica", 14)
    c.drawCentredString(mid, page_h - 1.9 * inch, "Report it in about 30 seconds. No login, no app.")

    size = 4.2 * inch
    qr_top = page_h - 2.35 * inch
    c.drawImage(
        ImageReader(PNG),
        (page_w - size) / 2,
        qr_top - size,
        width=size,
        height=size,
    )

    # Steps read as a left-aligned block, but the block is centred on the page.
    y = qr_top - size - 0.55 * inch
    block_left = mid - 2.15 * inch
    for num, text in STEPS:
        c.setFillColorRGB(*INK)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(block_left, y, num)
        c.setFont("Helvetica", 15)
        c.drawString(block_left + 0.28 * inch, y, text)
        y -= 0.34 * inch

    c.setFillColorRGB(*MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(mid, y - 0.18 * inch, "Not sure if it's worth reporting? Report it.")

    c.setFont("Helvetica", 11)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(mid, 1.15 * inch, "Questions:")
    c.setFont("Helvetica-Bold", 13)
    c.setFillColorRGB(*INK)
    c.drawCentredString(mid, 0.88 * inch, "Brian Lloyd  ·  315-404-5648")

    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.6, 0.62, 0.66)
    c.drawCentredString(mid, 0.45 * inch, URL)

    c.showPage()
    c.save()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
