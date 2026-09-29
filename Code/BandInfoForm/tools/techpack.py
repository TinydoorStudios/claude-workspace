#!/usr/bin/env python3
"""Branded venue tech packs (3CDC brand rollout phase 5, 2026-09-29).

Content lives in tools/techpacks/<slug>.json — facts only, each unverified
item marked "confirm": true. This renders it as a one-to-two page PDF in the
3CDC look: venue colors, 3CDC + venue logos, Avenir Next.

    python3 techpack.py fountain-square            # DRAFT, confirm items highlighted
    python3 techpack.py fountain-square --final    # refuses while any confirm remains;
                                                   # writes app/brand/techpacks/<slug>.pdf

Runs on the Mac: the Avenir Next faces are read from macOS's own font files.
The finished PDF is committed and ships with the app (/techpack/<slug>.pdf).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "app"))
import brand  # noqa: E402

CONTENT = HERE / "techpacks"
FINAL_DIR = brand.BRAND_DIR / "techpacks"

_AV = "/System/Library/Fonts/Avenir Next.ttc"
_AVC = "/System/Library/Fonts/Avenir Next Condensed.ttc"
for name, path, idx in [("Av", _AV, 7), ("Av-Demi", _AV, 2), ("Av-It", _AV, 4),
                        ("AvC-Demi", _AVC, 2), ("AvC-Med", _AVC, 5)]:
    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
pdfmetrics.registerFontFamily("Av", normal="Av", bold="Av-Demi", italic="Av-It", boldItalic="Av-Demi")

CHARCOAL = colors.HexColor("#595A5C")
RULE = colors.HexColor("#D9D9DB")
FLAG_BG = colors.HexColor("#FFF1B8")
FLAG_FG = colors.HexColor("#8A5A00")


def styles(pal):
    acc = colors.HexColor(pal["accent"])
    return {
        "title": ParagraphStyle("title", fontName="AvC-Demi", fontSize=22, leading=25,
                                textColor=acc),
        "sub": ParagraphStyle("sub", fontName="Av", fontSize=10, leading=13, textColor=CHARCOAL),
        "intro": ParagraphStyle("intro", fontName="Av", fontSize=9.5, leading=13.5,
                                textColor=CHARCOAL, spaceBefore=6),
        "h": ParagraphStyle("h", fontName="AvC-Demi", fontSize=12.5, leading=15, textColor=acc),
        "label": ParagraphStyle("label", fontName="AvC-Demi", fontSize=9, leading=12,
                                textColor=CHARCOAL),
        "body": ParagraphStyle("body", fontName="Av", fontSize=9, leading=12.4,
                               textColor=CHARCOAL, alignment=TA_LEFT),
        "cell": ParagraphStyle("cell", fontName="Av", fontSize=9, leading=12, textColor=CHARCOAL),
        # table header sits on the venue's button color, so it takes the
        # button's text color (dark on Washington Park's olive, white elsewhere)
        "cellh": ParagraphStyle("cellh", fontName="AvC-Demi", fontSize=9.5, leading=12,
                                textColor=colors.HexColor(pal["button_fg"])),
        "foot": ParagraphStyle("foot", fontName="Av", fontSize=7.5, leading=9, textColor=CHARCOAL),
    }


def _text(item):
    return item if isinstance(item, str) else item.get("text", "")


def _is_flag(item):
    return isinstance(item, dict) and item.get("confirm")


def _para(item, st, draft):
    t = escape(_text(item))
    if _is_flag(item) and draft:
        t = (f'<font name="AvC-Demi" color="#8A5A00">CONFIRM</font>&nbsp;&nbsp;'
             f'<font color="#8A5A00">{t}</font>')
    return Paragraph(t, st)


def count_flags(data):
    n = 0
    for s in data["sections"]:
        n += sum(1 for it in s.get("items", []) if _is_flag(it))
        for row in (s.get("table") or {}).get("rows", []):
            n += sum(1 for c in row if _is_flag(c))
    return n


def section_flow(sec, st, pal, width, draft):
    out = []
    head = Table([[Paragraph(escape(sec["title"].upper()), st["h"])]], colWidths=[width])
    head.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 2.2, colors.HexColor(pal["secondary"])),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    out.append(head)
    out.append(Spacer(1, 5))
    flags = []

    tbl = sec.get("table")
    if tbl:
        n = len(tbl["head"])
        cw = [1.25 * inch] + [(width - 1.25 * inch) / (n - 1)] * (n - 1)
        rows = [[Paragraph(escape(h), st["cellh"]) for h in tbl["head"]]]
        for ri, r in enumerate(tbl["rows"], start=1):
            row = []
            for ci, c in enumerate(r):
                row.append(Paragraph(escape(_text(c)), st["label"]) if ci == 0 else _para(c, st["cell"], draft))
                if _is_flag(c) and draft:
                    flags.append((ci, ri))
            rows.append(row)
        t = Table(rows, colWidths=cw)
        ts = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(pal["button_bg"])),
              ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
              ("LEFTPADDING", (0, 0), (-1, -1), 5)]
        ts += [("BACKGROUND", f, f, FLAG_BG) for f in flags]
        t.setStyle(TableStyle(ts))
        out += [t, Spacer(1, 6)]

    items = sec.get("items", [])
    if items and all(isinstance(i, str) or "label" not in i for i in items):
        cols = sec.get("columns", 1)
        if cols > 1:
            per = -(-len(items) // cols)
            grid = [[Paragraph("• " + escape(_text(items[c * per + r])), st["body"])
                     if c * per + r < len(items) else "" for c in range(cols)] for r in range(per)]
            t = Table(grid, colWidths=[width / cols] * cols)
            t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 1),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
            out.append(t)
        else:
            for it in items:
                out.append(Paragraph("• " + escape(_text(it)), st["body"]))
                out.append(Spacer(1, 2))
    elif items:
        rows, fl = [], []
        for ri, it in enumerate(items):
            rows.append([Paragraph(escape(it.get("label", "")), st["label"]), _para(it, st["body"], draft)])
            if _is_flag(it) and draft:
                fl.append(ri)
        t = Table(rows, colWidths=[1.35 * inch, width - 1.35 * inch])
        ts = [("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("LINEBELOW", (0, 0), (-1, -2), 0.5, RULE),
              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, -1), 8),
              ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2)]
        ts += [("BACKGROUND", (1, r), (1, r), FLAG_BG) for r in fl]
        t.setStyle(TableStyle(ts))
        out.append(t)
    return [KeepTogether(out), Spacer(1, 11)]


def build(slug, final=False, out=None):
    data = json.loads((CONTENT / f"{slug}.json").read_text())
    flags = count_flags(data)
    if final and flags:
        sys.exit(f"{slug}: {flags} item(s) still marked confirm; not building the final PDF")
    draft = not final
    venue = data["venue"]
    v = brand.venue_profile(venue)
    pal = brand.palette(venue)
    st = styles(pal)
    if out is None:
        out = FINAL_DIR / f"{slug}.pdf" if final else HERE / "filled" / f"{slug}-techpack-DRAFT.pdf"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    L = R = 0.6 * inch
    W = letter[0] - L - R
    today = dt.date.today().strftime("%B %Y")
    corp = brand.BRAND_DIR / brand.brand()["corporate"]["logos"]["primary"]
    vlogo = brand.BRAND_DIR / "logos" / f"{v['slug']}-typelogo.png"
    foot_logo = brand.BRAND_DIR / brand.brand()["corporate"]["logos"]["horizontal"]

    def logo(path, h):
        from PIL import Image as PI
        w, hh = PI.open(path).size
        return Image(str(path), width=h * w / hh, height=h)

    def on_page(c, doc):
        c.saveState()
        c.setFillColor(colors.HexColor(pal["primary"]))
        c.rect(0, letter[1] - 8, letter[0], 8, stroke=0, fill=1)
        c.setStrokeColor(RULE)
        c.line(L, 0.62 * inch, letter[0] - R, 0.62 * inch)
        fl = logo(foot_logo, 0.22 * inch)
        fl.drawOn(c, L, 0.3 * inch)
        c.setFont("Av", 7.5)
        c.setFillColor(CHARCOAL)
        c.drawRightString(letter[0] - R, 0.38 * inch,
                          f"{venue} · {v['address']} · Updated {today} · Page {doc.page}")
        if draft:
            c.setFont("AvC-Demi", 9)
            c.setFillColor(FLAG_FG)
            c.drawCentredString(letter[0] / 2, letter[1] - 0.32 * inch,
                                f"DRAFT: {flags} item(s) to confirm before this goes to bands")
        c.restoreState()

    doc = SimpleDocTemplate(str(out), pagesize=letter, leftMargin=L, rightMargin=R,
                            topMargin=0.55 * inch, bottomMargin=0.8 * inch,
                            title=f"{venue} Tech Pack", author="3CDC Events / Production")
    head = Table([[logo(corp, 0.34 * inch), logo(vlogo, 0.30 * inch)]], colWidths=[W / 2, W / 2])
    head.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    flow = [head, Spacer(1, 14),
            Paragraph("TECHNICAL INFORMATION FOR PERFORMERS", st["title"]),
            Paragraph(escape(f"{venue}" + (f" · {data['subtitle']}" if data.get("subtitle") else "")
                             + f" · {v['address']}"), st["sub"]),
            Paragraph(escape(data.get("intro", "")), st["intro"]), Spacer(1, 12)]
    for sec in data["sections"]:
        flow += section_flow(sec, st, pal, W, draft)
    doc.build(flow, onFirstPage=on_page, onLaterPages=on_page)
    return out, flags


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="+")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    for s in a.slug:
        path, n = build(s, final=a.final)
        print(f"{path}  ({'final' if a.final else f'draft, {n} to confirm'})")
