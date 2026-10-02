#!/usr/bin/env python3
"""Memorial Hall load-in and flat-lot parking sheets (2026-10-01).

Rebuilds Andi's two Word-era sheets with Google satellite + Street View captures:
  Memorial Hall Load In Instructions.pdf         every Memo show (WP garage or SP+ lot)
  Memorial Hall Flat Lot Parking Instructions.pdf   shows whose Parking is "SP+ Lot"

    python3 memodocs.py

Pixel coordinates below are in the source captures (memo-lot-aerial-source.png,
memo-door-streetview-source.png). Imagery: Google Maps, captured 2026-10-01.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

import parkingdoc as P

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "app" / "brand" / "parking"
AERIAL = HERE / "memo-lot-aerial-source.png"
STREET = HERE / "memo-door-streetview-source.png"

DOOR = (620, 503)                      # freight elevator door, south face of the annex
STAR_BLUE = (58, 110, 200)
YELLOW = (255, 214, 0)
RED = (214, 24, 40)
# the stalls along Memo's west wall (corners, clockwise from top-left)
STALLS = [(491, 180), (556, 180), (602, 472), (549, 472)]   # follows the slant of the back wall
LOT_ENTRY_ARROW = ((945, 72), (800, 72))   # tail -> tip, pointing west into the lot off Elm Street
CREDIT = "Imagery: Google Maps and Google Street View. Imagery ©2026 Google, Airbus, Maxar Technologies."

CREDIT_LOAD = CREDIT


def clean_aerial():
    """Source aerial with the Metropolis POI label and the Innago card removed."""
    im = Image.open(AERIAL).convert("RGB")
    a = np.array(im).astype(float)
    ref = a[100:170, 300:420].reshape(-1, 3)
    med, sd = np.median(ref, axis=0), ref.std(axis=0)
    from scipy.ndimage import gaussian_filter
    x0, y0, x1, y1 = 350, 214, 540, 262
    rng = np.random.default_rng(5)
    noise = gaussian_filter(rng.normal(0, 1, (y1 - y0, x1 - x0)), 1.2)[:, :, None] * 2.2
    a[y0:y1, x0:x1] = np.clip(med + noise * sd * 0.35, 0, 255)
    out = Image.fromarray(a.astype("uint8"))
    mask = Image.new("L", out.size, 0)
    ImageDraw.Draw(mask).rectangle((x0, y0, x1, y1), fill=255)
    return Image.composite(out, im, mask.filter(ImageFilter.GaussianBlur(4)))


def star(d, cx, cy, r, fill=STAR_BLUE):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill + (255,), outline=(255, 255, 255, 255))
    # a white keyline so it reads on any background
    d.line(pts + [pts[0]], fill=(255, 255, 255, 255), width=max(3, int(r / 9)), joint="curve")


def pill(d, text, cx, cy, size, anchor="mm", fill=(255, 255, 255, 240), ink=(35, 31, 32, 255)):
    from PIL import ImageFont
    font = ImageFont.truetype(P._AV, size, index=2)
    tw = d.textlength(text, font=font)
    pw, ph = tw + size * 1.2, size * 1.75
    x0 = cx - pw / 2 if anchor == "mm" else (cx if anchor == "lm" else cx - pw)
    d.rounded_rectangle((x0, cy - ph / 2, x0 + pw, cy + ph / 2), radius=ph / 2, fill=fill)
    d.text((x0 + pw / 2, cy - 1), text, font=font, fill=ink, anchor="mm")


def tag(over, text, x, y, rot, size):
    from PIL import ImageFont
    d = ImageDraw.Draw(over)
    font = ImageFont.truetype(P._AV, size, index=2)
    tw = int(d.textlength(text, font=font))
    t = Image.new("RGBA", (tw + int(size * 1.1), int(size * 1.6)), (0, 0, 0, 0))
    td = ImageDraw.Draw(t)
    td.rounded_rectangle((0, 0, t.width - 1, t.height - 1), radius=t.height // 2, fill=(35, 31, 32, 205))
    td.text((t.width / 2, t.height / 2), text, font=font, fill=(255, 255, 255, 255), anchor="mm")
    t = t.rotate(rot, expand=True)
    over.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))


def north_arrow(d, x, y, s=1.0):
    from PIL import ImageFont
    d.polygon([(x, y), (x - 16 * s, y + 40 * s), (x, y + 30 * s), (x + 16 * s, y + 40 * s)],
              fill=(255, 255, 255, 240))
    d.text((x, y + 62 * s), "N", font=ImageFont.truetype(P._AV, int(30 * s), index=2),
           fill=(255, 255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(35, 31, 32, 255))


def annotate_loadin_aerial():
    crop = (360, 250, 1200, 660)
    im = clean_aerial().convert("RGBA")
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    star(d, DOOR[0], DOOR[1] + 4, 34)
    pill(d, "Freight elevator door", DOOR[0] + 135, DOOR[1] + 68, 28, anchor="mm")
    tag(over, "GRANT ST", 485, 612, 13, 26)
    tag(over, "ELM ST", 1020, 330, 82, 26)
    north_arrow(d, 400, 285)
    out = Image.alpha_composite(im, over).convert("RGB").crop(crop)
    path = HERE / "memo-loadin-aerial-annotated.jpg"
    out.save(path, quality=92)
    return path


def annotate_lot_aerial():
    crop = (0, 0, 1230, 650)
    im = clean_aerial().convert("RGBA")
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    # reserved stalls
    d.polygon(STALLS, fill=YELLOW + (120,), outline=YELLOW + (255,))
    d.line(STALLS + [STALLS[0]], fill=YELLOW + (255,), width=5, joint="curve")
    pill(d, "Reserved spaces, coned off", 330, 130, 28, anchor="mm", fill=(255, 214, 0, 245))
    d.line([(395, 146), (505, 235)], fill=YELLOW + (255,), width=5)
    # entry arrow
    (tx, ty), (hx, hy) = LOT_ENTRY_ARROW
    d.line([(tx, ty), (hx + 40, hy)], fill=(255, 255, 255, 255), width=40)
    d.line([(tx, ty), (hx + 40, hy)], fill=RED + (255,), width=26)
    d.polygon([(hx - 8, hy), (hx + 52, hy - 44), (hx + 52, hy + 44)], fill=(255, 255, 255, 255))
    d.polygon([(hx, hy), (hx + 46, hy - 34), (hx + 46, hy + 34)], fill=RED + (255,))
    pill(d, "Enter from Elm Street", 790, 128, 28, anchor="mm")
    # door
    star(d, DOOR[0], DOOR[1] + 4, 36)
    pill(d, "Freight elevator door", DOOR[0] + 40, DOOR[1] + 70, 28, anchor="mm")
    tag(over, "GRANT ST", 290, 605, 13, 26)
    tag(over, "ELM ST", 1010, 330, 82, 26)
    north_arrow(d, 70, 24)
    out = Image.alpha_composite(im, over).convert("RGB").crop(crop)
    path = HERE / "memo-lot-aerial-annotated.jpg"
    out.save(path, quality=92)
    return path


def annotate_door_photo():
    im = Image.open(STREET).convert("RGB")
    # drop the little Street View link bubble stuck to the brick above the door
    patch = im.crop((226, 420, 271, 465))
    im.paste(patch.filter(ImageFilter.GaussianBlur(0.6)), (300, 420))
    im = im.convert("RGBA")
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    star(d, 410, 590, 58)
    pill(d, "Freight elevator door", 410, 700, 34, anchor="mm")
    out = Image.alpha_composite(im, over).convert("RGB")
    path = HERE / "memo-door-photo-annotated.jpg"
    out.save(path, quality=92)
    return path


def doc(name, flow_fn):
    pal = P.brand.palette("Memorial Hall")
    v = P.brand.venue_profile("Memorial Hall")
    acc = colors.HexColor(pal["accent"])
    from reportlab.lib.styles import ParagraphStyle
    st = {
        "title": ParagraphStyle("t", fontName="AvC-Demi", fontSize=24, leading=27, textColor=acc),
        "sub": ParagraphStyle("s", fontName="Av", fontSize=10.5, leading=14, textColor=P.CHARCOAL),
        "intro": ParagraphStyle("i", fontName="Av", fontSize=10.5, leading=15, textColor=P.CHARCOAL),
        "h": ParagraphStyle("h", fontName="AvC-Demi", fontSize=13, leading=16, textColor=acc),
        "step": ParagraphStyle("st", fontName="Av-Demi", fontSize=11, leading=14, textColor=P.CHARCOAL),
        "stepb": ParagraphStyle("sb", fontName="Av", fontSize=10, leading=14, textColor=P.CHARCOAL),
        "note": ParagraphStyle("n", fontName="Av", fontSize=9.5, leading=13.5, textColor=P.CHARCOAL),
        "cap": ParagraphStyle("c", fontName="Av-It", fontSize=7.5, leading=10, textColor=P.CHARCOAL),
        "num": ParagraphStyle("nu", fontName="AvC-Demi", fontSize=15, leading=18,
                              textColor=colors.HexColor(pal["button_fg"]), alignment=1),
    }
    L = R = 0.6 * inch
    W = letter[0] - L - R
    corp = P.brand.BRAND_DIR / P.brand.brand()["corporate"]["logos"]["primary"]
    vlogo = P.brand.BRAND_DIR / "logos" / f"{v['slug']}-typelogo.png"
    foot = P.brand.BRAND_DIR / P.brand.brand()["corporate"]["logos"]["horizontal"]

    def logo(path, h):
        w, hh = Image.open(path).size
        return RLImage(str(path), width=h * w / hh, height=h)

    def on_page(c, dd):
        c.saveState()
        c.setFillColor(colors.HexColor(pal["primary"]))
        c.rect(0, letter[1] - 8, letter[0], 8, stroke=0, fill=1)
        c.setFillColor(colors.HexColor(pal["secondary"]))
        c.rect(0, letter[1] - 8, letter[0] * 0.18, 8, stroke=0, fill=1)
        c.setStrokeColor(P.RULE)
        c.line(L, 0.62 * inch, letter[0] - R, 0.62 * inch)
        logo(foot, 0.22 * inch).drawOn(c, L, 0.3 * inch)
        c.setFont("Av", 7.5)
        c.setFillColor(P.CHARCOAL)
        c.drawRightString(letter[0] - R, 0.38 * inch, f"Memorial Hall · {v['address']}")
        c.restoreState()

    out = OUT_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    sdoc = SimpleDocTemplate(str(out), pagesize=letter, leftMargin=L, rightMargin=R, topMargin=0.55 * inch,
                             bottomMargin=0.8 * inch, title=name[:-4], author="3CDC Events / Production")
    head = Table([[logo(corp, 0.34 * inch), logo(vlogo, 0.30 * inch)]], colWidths=[W / 2, W / 2])
    head.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    flow = [head, Spacer(1, 8)] + flow_fn(st, pal, W, logo)
    sdoc.build(flow, onFirstPage=on_page)
    return out


def steps_table(st, pal, W, steps):
    rows = [[Paragraph(str(i), st["num"]),
             [Paragraph(escape(h), st["step"])] + ([Paragraph(escape(b), st["stepb"])] if b else [])]
            for i, (h, b) in enumerate(steps, 1)]
    t = Table(rows, colWidths=[0.42 * inch, W - 0.42 * inch])
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, -1), 10),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LINEBELOW", (0, 0), (-1, -2), 0.5, P.RULE)]
    for r in range(len(rows)):
        ts += [("BACKGROUND", (0, r), (0, r), colors.HexColor(pal["button_bg"])),
               ("VALIGN", (0, r), (0, r), "MIDDLE"),
               ("TOPPADDING", (0, r), (0, r), 7), ("BOTTOMPADDING", (0, r), (0, r), 7)]
    t.setStyle(TableStyle(ts))
    return t


def fit(path, width):
    w, h = Image.open(path).size
    return RLImage(str(path), width=width, height=width * h / w)


def loadin_flow(st, pal, W, logo):
    aerial = annotate_loadin_aerial()
    photo = annotate_door_photo()
    steps = [("Text your onsite contact when you're 10 minutes out.",
              "Use the onsite contact named in your advance email."),
             ("Arrive at the freight elevator door on Grant Street.",
              "It's the blue star on the map and in the photo.")]
    pw = W * 0.56
    flow = [Paragraph("LOAD-IN", st["title"]),
            Paragraph("Memorial Hall · GPS address: 1225 Elm Street, Cincinnati, OH 45202", st["sub"]),
            Spacer(1, 8), Paragraph("Welcome to Memorial Hall!", st["intro"]), Spacer(1, 8),
            steps_table(st, pal, W, steps), Spacer(1, 10),
            fit(aerial, W), Spacer(1, 8)]
    ph = Image.open(photo).size
    pimg = RLImage(str(photo), width=pw, height=pw * ph[1] / ph[0])
    side = [Paragraph("THE DOOR", st["h"]), Spacer(1, 4),
            Paragraph("A gray metal door under a dark canopy, at the west end of the building on Grant Street. "
                      "It opens into the freight elevator.", st["note"]),
            Spacer(1, 8), Paragraph(escape(CREDIT_LOAD), st["cap"])]
    two = Table([[pimg, side]], colWidths=[pw + 0.2 * inch, W - pw - 0.2 * inch])
    two.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (0, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return flow + [two]


def lot_flow(st, pal, W, logo):
    aerial = annotate_lot_aerial()
    photo = annotate_door_photo()
    steps = [("Enter the lot from Elm Street.", "Follow the red arrow on the map."),
             ("Park in the yellow spaces behind the building.",
              "They'll be coned off for your arrival."),
             ("Load in at the freight elevator door on Grant Street.",
              "It's the blue star. Text your onsite contact when you're 10 minutes out.")]
    pw = W * 0.5
    flow = [Paragraph("RESERVED PARKING", st["title"]),
            Paragraph("Memorial Hall · Flat lot behind the building · 1225 Elm Street", st["sub"]),
            Spacer(1, 8), Paragraph("Welcome to Memorial Hall! We have reserved parking for your performance.",
                                    st["intro"]), Spacer(1, 8),
            steps_table(st, pal, W, steps), Spacer(1, 10), fit(aerial, W), Spacer(1, 8)]
    ph = Image.open(photo).size
    pimg = RLImage(str(photo), width=pw, height=pw * ph[1] / ph[0])
    side = [Paragraph("THE DOOR", st["h"]), Spacer(1, 4),
            Paragraph("The freight elevator door is on Grant Street, at the south end of the reserved spaces.",
                      st["note"]), Spacer(1, 8), Paragraph(escape(CREDIT), st["cap"])]
    two = Table([[pimg, side]], colWidths=[pw + 0.2 * inch, W - pw - 0.2 * inch])
    two.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (0, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return flow + [two]


if __name__ == "__main__":
    for name, fn in (("Memorial Hall Load In Instructions.pdf", loadin_flow),
                     ("Memorial Hall Flat Lot Parking Instructions.pdf", lot_flow)):
        print(doc(name, fn))
