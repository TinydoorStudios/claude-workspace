#!/usr/bin/env python3
"""Washington Park Garage parking-validation sheet (2026-10-01).

One page for any show or event whose advance says parking is the Washington Park
garage: how the validation works plus an aerial with the two entrances marked.
Branded like the venue tech packs (Washington Park colors, 3CDC mark, Avenir Next).

    python3 parkingdoc.py            # writes the PDF + the annotated aerial next to it

The aerial is a Google Maps satellite capture (wp-garage-aerial-source.jpg, taken
2026-10-01). Google's attribution line prints under it. To re-capture, open Maps in
satellite view with Globe view and Labels off at ~20z and save the region; then
re-measure ENTRANCES below (pixel coordinates in the source image).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "app"))
import brand  # noqa: E402

OUT_NAME = "Washington Park Garage Parking.pdf"
SOURCE = HERE / "wp-garage-aerial-source.jpg"
ANNOTATED = HERE / "wp-garage-aerial-annotated.jpg"
CROP_BOTTOM = 690          # the capture carries Google's map controls below this line

# (number, marker x, marker y, label, label side) in source-image pixels
ENTRANCES = [
    (1, 195, 402, "Elm Street entrance", "right"),
    (2, 1392, 446, "Race Street entrance", "left"),
]
STREETS = [("ELM ST", 52, 560, 90), ("RACE ST", 1476, 130, 90)]   # text, x, y, rotation

_AV = "/System/Library/Fonts/Avenir Next.ttc"
_AVC = "/System/Library/Fonts/Avenir Next Condensed.ttc"
for name, path, idx in [("Av", _AV, 7), ("Av-Demi", _AV, 2), ("Av-It", _AV, 4),
                        ("AvC-Demi", _AVC, 2)]:
    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
pdfmetrics.registerFontFamily("Av", normal="Av", bold="Av-Demi", italic="Av-It", boldItalic="Av-Demi")

CHARCOAL = colors.HexColor("#595A5C")
RULE = colors.HexColor("#D9D9DB")
MARK = (196, 32, 51)       # 3CDC red, PMS 200 C

INTRO = ("Parking for your show is validated at the Washington Park Garage, the underground "
         "garage beneath Washington Park, directly across Elm Street from Memorial Hall.")
STEPS = [
    ("Pull a ticket at the entry kiosk.",
     "Take it, keep it with you, and don't lose it. You'll need it to leave."),
    ("Watch for your validation QR code.",
     "We'll email it ahead of your show. Save it to your phone so it's ready at the exit."),
    ("Scan your ticket, then the QR code, on the way out.",
     "At the exit, scan your original ticket first, then the QR code. That validates your parking, "
     "so you won't pay."),
]
ENTRANCE_NOTE = ("Two entrances lead to the same garage: Elm Street, across from Music Hall, and "
                 "Race Street at 13th Street. Use whichever is easier from your route.")
HELP = ("If a code won't scan, ask the garage attendant or text your day-of contact.")
CREDIT = "Aerial imagery: Google Maps. Imagery ©2026 Airbus, Maxar Technologies; map data ©2026 Google."


def annotate():
    """Source aerial + numbered entrance markers + street names -> ANNOTATED."""
    im = Image.open(SOURCE).convert("RGBA").crop((0, 0, 1512, CROP_BOTTOM))
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    big = ImageFont.truetype(_AV, 34, index=2)
    mid = ImageFont.truetype(_AV, 26, index=2)
    for n, x, y, label, side in ENTRANCES:
        r = 30
        d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=(255, 255, 255, 255))
        d.ellipse((x - r, y - r, x + r, y + r), fill=MARK + (255,))
        d.text((x, y - 1), str(n), font=big, fill=(255, 255, 255, 255), anchor="mm")
        tw = d.textlength(label, font=mid)
        pw, ph = tw + 36, 46
        px = x + r + 12 if side == "right" else x - r - 12 - pw
        d.rounded_rectangle((px, y - ph / 2, px + pw, y + ph / 2), radius=23, fill=(255, 255, 255, 235))
        d.text((px + pw / 2, y - 1), label, font=mid, fill=(35, 31, 32, 255), anchor="mm")
    small = ImageFont.truetype(_AV, 22, index=2)
    for text, x, y, rot in STREETS:
        tw = int(d.textlength(text, font=small))
        tag = Image.new("RGBA", (tw + 28, 38), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rounded_rectangle((0, 0, tw + 27, 37), radius=19, fill=(35, 31, 32, 205))
        td.text(((tw + 28) / 2, 19), text, font=small, fill=(255, 255, 255, 255), anchor="mm")
        tag = tag.rotate(rot, expand=True)
        over.alpha_composite(tag, (int(x - tag.width / 2), int(y - tag.height / 2)))
    # north arrow, top-left
    d.polygon([(46, 34), (30, 74), (46, 64), (62, 74)], fill=(255, 255, 255, 235))
    d.text((46, 98), "N", font=mid, fill=(255, 255, 255, 255), anchor="mm",
           stroke_width=3, stroke_fill=(35, 31, 32, 255))
    Image.alpha_composite(im, over).convert("RGB").save(ANNOTATED, quality=92)
    return ANNOTATED


def build(out_dir=None):
    pal = brand.palette("Washington Park")
    v = brand.venue_profile("Washington Park")
    annotate()
    out = Path(out_dir or HERE.parent.parent / "app" / "brand" / "parking") / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    acc = colors.HexColor(pal["accent"])
    st = {
        "title": ParagraphStyle("t", fontName="AvC-Demi", fontSize=24, leading=27, textColor=acc),
        "sub": ParagraphStyle("s", fontName="Av", fontSize=10.5, leading=14, textColor=CHARCOAL),
        "intro": ParagraphStyle("i", fontName="Av", fontSize=10.5, leading=15, textColor=CHARCOAL),
        "h": ParagraphStyle("h", fontName="AvC-Demi", fontSize=13, leading=16, textColor=acc),
        "step": ParagraphStyle("st", fontName="Av-Demi", fontSize=11, leading=14, textColor=CHARCOAL),
        "stepb": ParagraphStyle("sb", fontName="Av", fontSize=10, leading=14, textColor=CHARCOAL),
        "note": ParagraphStyle("n", fontName="Av", fontSize=9.5, leading=13.5, textColor=CHARCOAL),
        "cap": ParagraphStyle("c", fontName="Av-It", fontSize=7.5, leading=10, textColor=CHARCOAL),
        "num": ParagraphStyle("nu", fontName="AvC-Demi", fontSize=15, leading=18,
                              textColor=colors.HexColor(pal["button_fg"]), alignment=1),
    }
    L = R = 0.6 * inch
    W = letter[0] - L - R
    corp = brand.BRAND_DIR / brand.brand()["corporate"]["logos"]["primary"]
    vlogo = brand.BRAND_DIR / "logos" / f"{v['slug']}-typelogo.png"
    foot = brand.BRAND_DIR / brand.brand()["corporate"]["logos"]["horizontal"]

    def logo(path, h):
        w, hh = Image.open(path).size
        return RLImage(str(path), width=h * w / hh, height=h)

    def on_page(c, doc):
        c.saveState()
        c.setFillColor(colors.HexColor(pal["primary"]))
        c.rect(0, letter[1] - 8, letter[0], 8, stroke=0, fill=1)
        c.setStrokeColor(RULE)
        c.line(L, 0.62 * inch, letter[0] - R, 0.62 * inch)
        logo(foot, 0.22 * inch).drawOn(c, L, 0.3 * inch)
        c.setFont("Av", 7.5)
        c.setFillColor(CHARCOAL)
        c.drawRightString(letter[0] - R, 0.38 * inch, f"Washington Park · {v['address']}")
        c.restoreState()

    doc = SimpleDocTemplate(str(out), pagesize=letter, leftMargin=L, rightMargin=R,
                            topMargin=0.55 * inch, bottomMargin=0.8 * inch,
                            title="Washington Park Garage Parking", author="3CDC Events / Production")
    head = Table([[logo(corp, 0.34 * inch), logo(vlogo, 0.30 * inch)]], colWidths=[W / 2, W / 2])
    head.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    flow = [head, Spacer(1, 14),
            Paragraph("PARKING &amp; VALIDATION", st["title"]),
            Paragraph("Washington Park Garage · 1230 Elm St, Cincinnati, OH 45202", st["sub"]),
            Spacer(1, 10), Paragraph(escape(INTRO), st["intro"]), Spacer(1, 12)]

    rows = []
    for i, (head_t, body_t) in enumerate(STEPS, 1):
        rows.append([Paragraph(str(i), st["num"]),
                     [Paragraph(escape(head_t), st["step"]), Paragraph(escape(body_t), st["stepb"])]])
    t = Table(rows, colWidths=[0.42 * inch, W - 0.42 * inch])
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, -1), 10),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LINEBELOW", (0, 0), (-1, -2), 0.5, RULE)]
    for r in range(len(rows)):
        ts += [("BACKGROUND", (0, r), (0, r), colors.HexColor(pal["button_bg"])),
               ("VALIGN", (0, r), (0, r), "MIDDLE"),
               ("TOPPADDING", (0, r), (0, r), 11), ("BOTTOMPADDING", (0, r), (0, r), 11)]
    t.setStyle(TableStyle(ts))
    flow += [t, Spacer(1, 14)]

    flow += [Paragraph("WHERE TO ENTER", st["h"]), Spacer(1, 4),
             Paragraph(escape(ENTRANCE_NOTE), st["note"]), Spacer(1, 7)]
    iw, ih = Image.open(ANNOTATED).size
    flow += [RLImage(str(ANNOTATED), width=W, height=W * ih / iw), Spacer(1, 3),
             Paragraph(escape(CREDIT), st["cap"]), Spacer(1, 10),
             Paragraph(escape(HELP), st["note"])]
    doc.build(flow, onFirstPage=on_page)
    return out


if __name__ == "__main__":
    print(build())
