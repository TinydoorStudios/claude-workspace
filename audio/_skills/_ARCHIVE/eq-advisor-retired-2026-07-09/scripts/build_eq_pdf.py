#!/usr/bin/env python3
"""
build_eq_pdf.py — render an EQ Advisor recommendation to a PDF in Brian's house style.

Usage:
    python3 build_eq_pdf.py <spec.json> <output.pdf>
    python3 build_eq_pdf.py --sample <output.pdf>     # writes a built-in sample, for testing

Deliverable style: landscape, ReportLab, Brian's color scheme, canonical EQ band layout.
Every cell is a wrapping Paragraph so nothing clips (Brian's content-visibility rule).

SPEC SCHEMA (JSON)
------------------
{
  "title": "EQ Recommendation",            # optional, defaults to "EQ Recommendation"
  "subtitle": "optional line under title",  # optional
  "meta": {                                 # all optional; shown in the sub-bar
    "venue": "Memorial Hall",
    "console": "DiGiCo Quantum 225",
    "genre": "Blues-rock",
    "date": "2026-06-23",
    "rev": "A",
    "mode": "Live",                         # Live | Post
    "engineer": "Brian Lloyd"
  },
  "eq_columns": ["HPF","LPF","Band 4","Band 3","Band 2","Band 1"],   # optional; default = Q225
  "channels": [
    {
      "ch": "13",                           # optional
      "instrument": "Electric Gtr (cab)",   # required
      "mic": "SM57",                        # optional but recommended
      "section": "guitar",                  # drums|bass|guitar|keys|vocal|horns|strings|ambient|other
      "phantom": false,                     # true -> shows a check; ribbon flag overrides to NO
      "ribbon": false,                      # true -> 48V cell shows NO in red
      "bands": {                            # keys must match eq_columns; missing -> dash
        "HPF": "100 @ 18", "LPF": "Off",
        "Band 4": "—", "Band 3": "+4 @ 2.5k Q1.0",
        "Band 2": "-5 @ 450 Q2.0", "Band 1": "-4 @ 300 Q1.8"
      },
      "flags": ["No 48V — ribbon"],         # optional, rendered in the warning band
      "reasoning": "Quick-summary paragraph, written like a colleague.",   # optional but expected
      "sources": ["KB: eq-starting-points", "LAB: SM57 on cab (url)"],     # optional
      "confirmations": ["Confirmed with Brian: kept low-mid body"]          # optional
    }
  ],
  "global_notes": "optional closing note",
  "global_sources": ["optional list if you prefer one Sources block"]
}
"""

import json
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether,
)

# ---- Brian's house palette -------------------------------------------------
HEADER_BG   = colors.HexColor("#1A1A2E")
SUBHEAD_BG  = colors.HexColor("#0F3460")
ACCENT      = colors.HexColor("#E94560")
ALT_ROW     = colors.HexColor("#E8EEF7")
TOUR        = colors.HexColor("#FFF3CD")
WARNING     = colors.HexColor("#FFE4B5")

SECTION_COLORS = {
    "drums":   colors.HexColor("#D4E8D4"),
    "bass":    colors.HexColor("#D4D4E8"),
    "guitar":  colors.HexColor("#E8E4D4"),
    "keys":    colors.HexColor("#E8D4E8"),
    "vocal":   colors.HexColor("#E8D4D4"),
    "horns":   colors.HexColor("#E8E4D4"),
    "strings": colors.HexColor("#E8D4E8"),
    "ambient": colors.HexColor("#C7D2FE"),
    "other":   colors.white,
}

DEFAULT_EQ_COLUMNS = ["HPF", "LPF", "Band 4", "Band 3", "Band 2", "Band 1"]

# ---- styles ----------------------------------------------------------------
_ss = getSampleStyleSheet()

def _style(name, **kw):
    base = dict(fontName="Helvetica", fontSize=8, leading=10, alignment=TA_LEFT,
                textColor=colors.black)
    base.update(kw)
    return ParagraphStyle(name, parent=_ss["Normal"], **base)

ST_TITLE   = _style("eqTitle", fontName="Helvetica-Bold", fontSize=18, leading=21,
                    textColor=colors.white)
ST_SUBTTL  = _style("eqSubtitle", fontSize=10, leading=12, textColor=colors.white)
ST_META    = _style("eqMeta", fontSize=9, leading=12, textColor=colors.white)
ST_TH      = _style("eqTH", fontName="Helvetica-Bold", fontSize=8, leading=9.5,
                    textColor=colors.white)
ST_CELL    = _style("eqCell", fontSize=8, leading=9.5)
ST_CELL_B  = _style("eqCellB", fontName="Helvetica-Bold", fontSize=8, leading=9.5)
ST_CELL_C  = _style("eqCellC", fontSize=8, leading=9.5, alignment=1)  # centered
ST_NO48    = _style("eqNo48", fontName="Helvetica-Bold", fontSize=8, leading=9.5,
                    alignment=1, textColor=ACCENT)
ST_CARDHEAD= _style("eqCardHead", fontName="Helvetica-Bold", fontSize=10, leading=12,
                    textColor=colors.white)
ST_BODY    = _style("eqBody", fontSize=9.5, leading=13)
ST_FLAG    = _style("eqFlag", fontName="Helvetica-Bold", fontSize=9, leading=12,
                    textColor=colors.HexColor("#7a3b00"))
ST_CONF    = _style("eqConf", fontSize=9, leading=12, textColor=colors.HexColor("#0F3460"))
ST_SRC     = _style("eqSrc", fontSize=8, leading=11, textColor=colors.HexColor("#444444"))
ST_SECHEAD = _style("eqSecHead", fontName="Helvetica-Bold", fontSize=11, leading=13,
                    textColor=colors.white)


def P(text, st=ST_CELL):
    if text is None:
        text = ""
    return Paragraph(str(text), st)


def bar(text_or_flowable, bg, pad=8, style=None):
    """A full-width colored bar containing a paragraph (or flowable list)."""
    content = text_or_flowable
    if isinstance(text_or_flowable, str):
        content = Paragraph(text_or_flowable, style or ST_SECHEAD)
    t = Table([[content]], colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad - 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad - 2),
    ]))
    return t


# ---- page geometry ---------------------------------------------------------
PAGE = landscape(letter)
MARGIN = 0.4 * inch
USABLE_W = PAGE[0] - 2 * MARGIN


def build(spec, out_path):
    title = spec.get("title", "EQ Recommendation")
    subtitle = spec.get("subtitle", "")
    meta = spec.get("meta", {})
    eq_cols = spec.get("eq_columns", DEFAULT_EQ_COLUMNS)
    channels = spec.get("channels", [])

    doc = SimpleDocTemplate(
        out_path, pagesize=PAGE,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title=title, author=meta.get("engineer", "Brian Lloyd"),
    )
    story = []

    # --- title bar ---
    tflow = [Paragraph(title, ST_TITLE)]
    if subtitle:
        tflow.append(Paragraph(subtitle, ST_SUBTTL))
    story.append(bar(tflow, HEADER_BG, pad=12))

    # --- meta sub-bar ---
    bits = []
    for label, key in [("Venue", "venue"), ("Date", "date"), ("Console", "console"),
                       ("Genre", "genre"), ("Mode", "mode"), ("Rev", "rev"),
                       ("Engineer", "engineer")]:
        if meta.get(key):
            bits.append(f"<b>{label}:</b> {meta[key]}")
    if bits:
        story.append(bar(Paragraph("&nbsp;&nbsp;|&nbsp;&nbsp;".join(bits), ST_META),
                         SUBHEAD_BG, pad=7))
    story.append(Spacer(1, 10))

    # --- EQ table ---
    story.append(_eq_table(channels, eq_cols))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Whole-dB values, cuts-first. Band order high→low; band numbers match the console "
        "(1 = LF, 4 = HF). Gain @ frequency, Q, type.", ST_SRC))
    story.append(Spacer(1, 14))

    # --- reasoning cards ---
    story.append(bar("Reasoning &amp; Sources", SUBHEAD_BG, pad=7))
    story.append(Spacer(1, 8))
    for ch in channels:
        story.append(_reason_card(ch))
        story.append(Spacer(1, 10))

    # --- global notes / sources ---
    if spec.get("global_notes"):
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Notes:</b> {spec['global_notes']}", ST_BODY))
    if spec.get("global_sources"):
        story.append(Spacer(1, 4))
        srcs = "<br/>".join(f"• {s}" for s in spec["global_sources"])
        story.append(Paragraph(f"<b>Sources:</b><br/>{srcs}", ST_SRC))

    doc.build(story)
    return out_path


def _eq_table(channels, eq_cols):
    head = [P("CH", ST_TH), P("Instrument", ST_TH), P("Mic / DI", ST_TH), P("48V", ST_TH)]
    head += [P(c, ST_TH) for c in eq_cols]
    rows = [head]

    section_row_colors = []
    for ch in channels:
        sect = (ch.get("section") or "other").lower()
        section_row_colors.append(SECTION_COLORS.get(sect, colors.white))
        bands = ch.get("bands", {})
        # 48V cell
        if ch.get("ribbon"):
            v48 = P("NO", ST_NO48)
        elif ch.get("phantom"):
            v48 = P("ON", ST_CELL_C)
        else:
            v48 = P("–", ST_CELL_C)
        row = [
            P(ch.get("ch", ""), ST_CELL_C),
            P(ch.get("instrument", ""), ST_CELL_B),
            P(ch.get("mic", ""), ST_CELL),
            v48,
        ]
        for c in eq_cols:
            row.append(P(bands.get(c, "–"), ST_CELL_C))
        rows.append(row)

    # column widths
    fixed = {"CH": 0.4 * inch, "Instrument": 1.7 * inch, "Mic / DI": 1.3 * inch, "48V": 0.45 * inch}
    used = sum(fixed.values())
    band_w = (USABLE_W - used) / max(len(eq_cols), 1)
    col_widths = [fixed["CH"], fixed["Instrument"], fixed["Mic / DI"], fixed["48V"]] + \
                 [band_w] * len(eq_cols)

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9aa3b2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, rc in enumerate(section_row_colors, start=1):
        style.append(("BACKGROUND", (0, i), (-1, i), rc))
    t.setStyle(TableStyle(style))
    return t


def _reason_card(ch):
    head_bits = []
    if ch.get("ch"):
        head_bits.append(f"CH {ch['ch']}")
    head_bits.append(ch.get("instrument", ""))
    if ch.get("mic"):
        head_bits.append(f"— {ch['mic']}")
    header = bar(" ".join(head_bits).strip(), HEADER_BG, pad=6, style=ST_CARDHEAD)

    body = []
    if ch.get("flags"):
        flag_txt = "&nbsp;&nbsp;".join(f"! {f}" for f in ch["flags"])
        body.append(bar(Paragraph(flag_txt, ST_FLAG), WARNING, pad=5))
        body.append(Spacer(1, 4))
    if ch.get("reasoning"):
        body.append(Paragraph(ch["reasoning"], ST_BODY))
    if ch.get("confirmations"):
        body.append(Spacer(1, 3))
        for c in ch["confirmations"]:
            body.append(Paragraph(f"&bull; {c}", ST_CONF))
    if ch.get("sources"):
        body.append(Spacer(1, 3))
        srcs = "<br/>".join(f"• {s}" for s in ch["sources"])
        body.append(Paragraph(f"<b>Sources:</b><br/>{srcs}", ST_SRC))

    inner = Table([[body]], colWidths=[USABLE_W])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd6e2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([header, inner])


# ---- sample (for testing) --------------------------------------------------
SAMPLE = {
    "title": "EQ Recommendation",
    "subtitle": "Mic- and genre-aware starting point — confirm by ear",
    "meta": {"venue": "Memorial Hall", "console": "DiGiCo Quantum 225",
             "genre": "Blues-rock", "date": "2026-06-23", "rev": "A",
             "mode": "Live", "engineer": "Brian Lloyd"},
    "eq_columns": DEFAULT_EQ_COLUMNS,
    "channels": [
        {"ch": "13", "instrument": "Electric Gtr (cab)", "mic": "SM57", "section": "guitar",
         "phantom": False,
         "bands": {"HPF": "100 @ 18", "LPF": "Off", "Band 4": "–",
                   "Band 3": "+4 @ 2.5k Q1.0", "Band 2": "-5 @ 450 Q2.0",
                   "Band 1": "-4 @ 300 Q1.8"},
         "reasoning": ("SM57 builds box and honk around 300–500 Hz on a driven cab, so the "
                       "two low-mid cuts do the heavy lifting. The 300 Hz cut also sits on Memo's "
                       "250–315 Hz standing wave, so it earns its keep twice. Blues-rock wants "
                       "body, so the cuts stay moderate and the presence lift at 2.5k brings the "
                       "bite back without getting harsh."),
         "sources": ["KB: eq-starting-points", "KB: mic-library (SM57 — tame box ~400)",
                     "LAB: SM57 on guitar cab (forums.prosoundweb.com)"],
         "confirmations": ["Confirmed with Brian: keep low-mid body for the blues feel"]},
        {"ch": "15", "instrument": "Electric Gtr (blend)", "mic": "Royer R-121", "section": "guitar",
         "ribbon": True,
         "bands": {"HPF": "Off", "LPF": "12k", "Band 4": "–", "Band 3": "–",
                   "Band 2": "-3 @ 350 Q2.0", "Band 1": "+3 @ 150 Q1.0"},
         "flags": ["NO 48V — ribbon. Destroys the R-121."],
         "reasoning": ("Blend partner to the SM57 on the AxeMount — treated as one signal. "
                       "Low-mids backed off about half (350 Hz cut) so the ribbon's body doesn't "
                       "stack on the 57's midrange. Sits 6–10 dB under the 57; sum in mono and "
                       "flip polarity if the blend thins out."),
         "sources": ["KB: mic-library (Two-Mic Blends)", "KB: Royer AxeMount blend guide"]},
    ],
    "global_notes": "Starting points only. Verify by ear against the room before the doors open.",
}


def main(argv):
    if len(argv) >= 2 and argv[0] == "--sample":
        build(SAMPLE, argv[1])
        print(f"wrote sample -> {argv[1]}")
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 1
    with open(argv[0], "r", encoding="utf-8") as f:
        spec = json.load(f)
    build(spec, argv[1])
    print(f"wrote -> {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
