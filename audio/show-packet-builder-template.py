"""
Show Packet Builder — Brian Lloyd / 3CDC / Jazz At The Memo
ReportLab PDF generator for FOH channel EQ setup packets.

Supports: Behringer Wing, DiGiCo Quantum 225
Output: Multi-page PDF matching KSO Simon & Garfunkel visual standard

Document order:
  1. Cover page
  2. Input List
  3. Patching page (AES first, then Local)
  4. Cross-Patch page (sorted by stage box location)
  5. EQ channel pages (one per channel)
  6. Reference page
  7. Stage Plot (5-zone grid, if available)
"""

import math
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line, Polygon, PolyLine, Rect, String, Circle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable,
    Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ---------------------------------------------------------------------------
# PAGE MARKS — feed the MASTER PDF's clickable quick-links page (2026-07-27)
# ---------------------------------------------------------------------------

class PageMark(Flowable):
    """Zero-size flowable that records which page it landed on.

    Dropped into the story right after a PageBreak so the recorded page is the
    page the following block starts on. build_show_packet returns the collected
    list; build_packet.py turns it into the MASTER's quick-links + bookmarks.
    """

    def __init__(self, sink, kind, label, **meta):
        Flowable.__init__(self)
        self._sink, self._kind, self._label, self._meta = sink, kind, label, meta
        self.width = self.height = 0

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        self._sink.append(dict(kind=self._kind, label=self._label,
                               page=self.canv.getPageNumber(), **self._meta))

# ---------------------------------------------------------------------------
# COLOR SYSTEM
# ---------------------------------------------------------------------------

# Console accent colors
WING_DARK    = colors.HexColor("#1A1A1A")
WING_MID     = colors.HexColor("#3A3A3A")
WING_RED     = colors.HexColor("#9B2222")   # Wing signature red
WING_LIGHT   = colors.HexColor("#E8E8E8")

DIGICO_DARK  = colors.HexColor("#1A3A5C")   # DiGiCo navy
DIGICO_MID   = colors.HexColor("#2E6DA4")
DIGICO_LIGHT = colors.HexColor("#D6E4F0")

# Input List section colors: (header, alt-row)
SEC_COLORS = {
    "DRUMS":   ("#FDE68A", "#FEF3C7"),
    "RHYTHM":  ("#BBF7D0", "#DCFCE7"),
    "PIANO":   ("#FBCFE8", "#FCE7F3"),
    "STRINGS": ("#BFDBFE", "#DBEAFE"),
    "HORNS":   ("#FCD9B4", "#FFEDD5"),
    "VOCALS":  ("#DDD6FE", "#EDE9FE"),
    "AMBIENT": ("#C7D2FE", "#E0E7FF"),
    "SPARE":   ("#E5E7EB", "#F3F4F6"),
}

# EQ channel accent bars
DRUMS_BAR   = colors.HexColor("#5A4A3A")
BASS_BAR    = colors.HexColor("#6B4F2A")
GUITAR_BAR  = colors.HexColor("#3A5A4A")
KEYS_BAR    = colors.HexColor("#3A3A6A")
PIANO_BAR   = colors.HexColor("#4A3A6A")
STRINGS_BAR = colors.HexColor("#5A3A3A")
HORNS_BAR   = colors.HexColor("#6A4A1A")
VOCALS_BAR  = colors.HexColor("#4A1A4A")
AMBIENT_BAR = colors.HexColor("#1A3A4A")
TBD_BAR     = colors.HexColor("#5A5A5A")

# EQ row background colors
LC_BG    = colors.HexColor("#D0D8E8")   # filter bands (LC, HC)
SHELF_BG = colors.HexColor("#D8E0D0")   # shelf bands
BELL_BG  = colors.white                  # bell bands
OFF_BG   = colors.HexColor("#F4F4F4")   # OFF / unused bands

# Input List structure
SPEC_TITLE  = colors.HexColor("#1F2937")
SPEC_SUB    = colors.HexColor("#374151")
SPEC_HDR    = colors.HexColor("#111827")
EMERALD     = colors.HexColor("#065F46")   # 48V checkmark
SECTION_BG  = colors.HexColor("#F4F0E8")   # warm cream — mic notes, engineer notes

# ---------------------------------------------------------------------------
# STYLE HELPERS
# ---------------------------------------------------------------------------

styles = getSampleStyleSheet()


def mks(name, parent='Normal', **kw):
    return ParagraphStyle(name, parent=styles[parent], **kw)


def get_console_colors(console):
    """Return (dark, mid, accent) for the given console key."""
    if console == "digico":
        return DIGICO_DARK, DIGICO_MID, DIGICO_MID
    return WING_DARK, WING_MID, WING_RED


# ---------------------------------------------------------------------------
# SHARED COMPONENTS
# ---------------------------------------------------------------------------

def hbar(text, bg, fsize=12):
    """Full-width dark header bar."""
    s = mks(f'hb_{text[:8]}', 'Normal', fontSize=fsize, textColor=colors.white,
            fontName='Helvetica-Bold', alignment=TA_LEFT)
    t = Table([[Paragraph(text, s)]], colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def section_bar(text, bg):
    """Section divider bar between instrument groups on EQ pages."""
    s = mks(f'sb_{text[:8]}', 'Normal', fontSize=11, textColor=colors.white,
            fontName='Helvetica-Bold', alignment=TA_CENTER)
    t = Table([[Paragraph(text, s)]], colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def channel_header(ch_num, ch_name, mic_name, accent_bg):
    """Per-channel header bar."""
    s1 = mks(f'chh_{ch_num}', 'Normal', fontSize=14, textColor=colors.white,
             fontName='Helvetica-Bold', alignment=TA_LEFT)
    s2 = mks(f'chh2_{ch_num}', 'Normal', fontSize=10, textColor=colors.white,
             fontName='Helvetica-Oblique', alignment=TA_LEFT)
    t = Table([
        [Paragraph(f'<b>Ch {ch_num}</b>  |  {ch_name}', s1)],
        [Paragraph(f'Mic: {mic_name}', s2)],
    ], colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), accent_bg),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _esc(s):
    """Escape user prose for reportlab's Paragraph markup parser.

    An unescaped "&" (e.g. "R&B") is read as a malformed entity and renders as
    "R&B;". Caught on the 2026-08-01 Repertoire build.
    """
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def mic_notes_box(text):
    """Warm cream box for mic character notes."""
    s = mks('mn', 'Normal', fontSize=8.5, textColor=colors.HexColor("#333333"),
            fontName='Helvetica', alignment=TA_LEFT, leading=12)
    t = Table([[Paragraph(f'<b>Mic Notes:</b> {_esc(text)}', s)]], colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#3A3A3A")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def engineer_notes_box(text, console="wing"):
    """Accent-bordered engineer notes box."""
    dark, mid, accent = get_console_colors(console)
    s = mks('su', 'Normal', fontSize=8.5, textColor=colors.HexColor("#333333"),
            fontName='Helvetica-Oblique', alignment=TA_LEFT, leading=12)
    t = Table([[Paragraph(f'<b>Engineer Notes:</b> {_esc(text)}', s)]], colWidths=[7.3 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF6EE")),
        ('BOX', (0, 0), (-1, -1), 0.6, accent),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


# ---------------------------------------------------------------------------
# EQ RESPONSE CARD  (2026-07-28)
# ---------------------------------------------------------------------------
# One filled curve per input, drawn straight from the channel's own numbers, so
# the shape of the move is readable before the table below is read. Same content
# as the table it sits above: every active band marked with its gain, frequency
# and Q, plus the HPF/LPF. Vector, not an image — it stays sharp at any zoom and
# adds nothing to the file size worth counting.
#
# Filters are DRAWN at 12 dB/oct: the console stores a slope per channel but the
# packet spec does not carry one, so the corner frequency is exact and the
# steepness is a stand-in. Labelled on the card so nobody reads it as gospel.

CURVE_FS = 48000.0          # sample rate the biquads are evaluated at
CURVE_DB = 18.0             # vertical range, ±dB
CURVE_STEPS = 190           # points across the plot


def _bq_mag(c, w):
    """|H(e^jw)| for a biquad [b0,b1,b2,a0,a1,a2]."""
    b0, b1, b2, a0, a1, a2 = c
    cw, sw = math.cos(w), math.sin(w)
    c2, s2 = math.cos(2 * w), math.sin(2 * w)
    nr, ni = b0 + b1 * cw + b2 * c2, -(b1 * sw + b2 * s2)
    dr, di = a0 + a1 * cw + a2 * c2, -(a1 * sw + a2 * s2)
    den = dr * dr + di * di
    return math.sqrt((nr * nr + ni * ni) / den) if den else 1.0


def _bq_peak(f, g, q):
    A = 10 ** (g / 40.0)
    w = 2 * math.pi * f / CURVE_FS
    al = math.sin(w) / (2 * max(q, 0.1))
    cw = math.cos(w)
    return [1 + al * A, -2 * cw, 1 - al * A, 1 + al / A, -2 * cw, 1 - al / A]


def _bq_shelf(f, g, q, high):
    A = 10 ** (g / 40.0)
    w = 2 * math.pi * f / CURVE_FS
    cw, sw = math.cos(w), math.sin(w)
    al = sw / 2 * math.sqrt((A + 1 / A) * (1 / max(q, 0.1) - 1) + 2)
    tsa = 2 * math.sqrt(A) * al
    if high:
        return [A * ((A + 1) + (A - 1) * cw + tsa), -2 * A * ((A - 1) + (A + 1) * cw),
                A * ((A + 1) + (A - 1) * cw - tsa), (A + 1) - (A - 1) * cw + tsa,
                2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - tsa]
    return [A * ((A + 1) - (A - 1) * cw + tsa), 2 * A * ((A - 1) - (A + 1) * cw),
            A * ((A + 1) - (A - 1) * cw - tsa), (A + 1) + (A - 1) * cw + tsa,
            -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - tsa]


def _bq_pole(f, hp):
    """12 dB/oct Butterworth — see the note above about slope."""
    w = 2 * math.pi * f / CURVE_FS
    cw, al = math.cos(w), math.sin(w) / (2 * 0.7071)
    if hp:
        return [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2, 1 + al, -2 * cw, 1 - al]
    return [(1 - cw) / 2, 1 - cw, (1 - cw) / 2, 1 + al, -2 * cw, 1 - al]


_NUM = re.compile(r'-?\d+(?:\.\d+)?')


def _num(text):
    """First number in a cell like '+4 dB', '2.5 kHz', '1.07k', '—'. None if absent."""
    if text is None:
        return None
    s = str(text).strip()
    m = _NUM.search(s.replace(",", ""))
    if not m:
        return None
    v = float(m.group())
    if re.search(r'k(?:hz)?\b', s, re.I):
        v *= 1000
    return v


def curve_from_rows(rows):
    """Build the numeric curve spec from the same rows eq_table() renders.

    Lets a caller that only has the display strings still get a card. A caller
    holding real numbers should pass `curve` directly instead — nothing is
    re-parsed then.
    """
    hpf = lpf = None
    bands = []
    for r in rows:
        typ = str(r.get("type", "")).strip()
        if typ == "LC":
            hpf = _num(r.get("freq"))
            continue
        if typ == "HC":
            lpf = _num(r.get("freq"))
            continue
        if typ == "OFF":
            continue
        g, f = _num(r.get("gain")), _num(r.get("freq"))
        if g is None or f is None:
            continue
        bands.append(dict(b=_num(r.get("band")) or 0, gain=g, freq=f,
                          q=_num(r.get("q")) or 1.0, shelf=(typ.lower() == "shelf"),
                          deq="DYNAMIC" in str(r.get("notes", "")).upper()))
    return dict(hpf=hpf, lpf=lpf, bands=bands)


def _fmt_hz(f):
    if f is None:
        return "off"
    return f"{f / 1000:g}k" if f >= 1000 else f"{f:g}"


def eq_curve_card(curve, accent, width=7.3 * inch, height=1.42 * inch):
    """Filled EQ response curve for one input. Returns a Drawing (a flowable).

    curve: {"hpf": Hz|None, "lpf": Hz|None,
            "bands": [{"b":1-4, "gain":dB, "freq":Hz, "q":float,
                       "shelf":bool, "deq":bool}, ...]}
    accent: the channel's section accent colour — the curve is drawn in it and
            filled with a wash of it, so the card reads as part of its section.
    """
    if not curve:
        return Spacer(1, 0)
    W, H = float(width), float(height)
    PL, PR, PT, PB = 32.0, 8.0, 20.0, 15.0
    x0, x1 = PL, W - PR
    y0, y1 = PB, H - PT
    lo = math.log10(20.0)
    span = math.log10(20000.0) - lo

    def X(f):
        return x0 + (math.log10(max(f, 20.0)) - lo) / span * (x1 - x0)

    def Y(db):
        db = max(-CURVE_DB, min(CURVE_DB, db))
        return y0 + (db + CURVE_DB) / (2 * CURVE_DB) * (y1 - y0)

    if not isinstance(accent, colors.Color):
        accent = colors.HexColor(str(accent))
    wash = colors.Color(accent.red, accent.green, accent.blue, alpha=0.20)
    faint = colors.HexColor("#E2E7EE")
    axis = colors.HexColor("#9AA5B4")
    ink = colors.HexColor("#3D4757")

    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=colors.HexColor("#FBFCFD"),
               strokeColor=colors.HexColor("#D3DAE4"), strokeWidth=0.5))

    # grid
    for f in (50, 100, 200, 500, 1000, 2000, 5000, 10000):
        d.add(Line(X(f), y0, X(f), y1, strokeColor=faint, strokeWidth=0.4))
    for db in (12, 6, -6, -12):
        d.add(Line(x0, Y(db), x1, Y(db), strokeColor=faint, strokeWidth=0.4))
    d.add(Line(x0, Y(0), x1, Y(0), strokeColor=axis, strokeWidth=0.6))
    for db in (12, 0, -12):
        d.add(String(4, Y(db) - 2.2, f"{db:+g}" if db else "0",
                     fontName="Helvetica", fontSize=5.8, fillColor=axis))
    for f, lbl in ((100, "100"), (1000, "1k"), (10000, "10k")):
        d.add(String(X(f), y0 - 8.5, lbl, fontName="Helvetica", fontSize=5.8,
                     fillColor=axis, textAnchor="middle"))

    # response
    chain = []
    for b in curve.get("bands", []):
        g = float(b.get("gain") or 0)
        if abs(g) < 0.05:
            continue
        f, q = float(b["freq"]), float(b.get("q") or 1.0)
        chain.append(_bq_shelf(f, g, q, int(b.get("b", 2)) >= 3) if b.get("shelf")
                     else _bq_peak(f, g, q))
    if curve.get("hpf") and float(curve["hpf"]) > 20:
        chain.append(_bq_pole(float(curve["hpf"]), True))
    if curve.get("lpf"):
        chain.append(_bq_pole(float(curve["lpf"]), False))

    pts = []
    for i in range(CURVE_STEPS + 1):
        f = 10 ** (lo + span * i / CURVE_STEPS)
        w = 2 * math.pi * f / CURVE_FS
        m = 1.0
        for c in chain:
            m *= _bq_mag(c, w)
        pts.append((X(f), Y(20 * math.log10(max(m, 1e-6)))))

    fill = [x0, Y(0)] + [v for p in pts for v in p] + [x1, Y(0)]
    d.add(Polygon(fill, fillColor=wash, strokeColor=None))
    d.add(PolyLine([v for p in pts for v in p], strokeColor=accent, strokeWidth=1.3,
                   strokeLineJoin=1))

    # filter markers
    for f, lbl in ((curve.get("hpf"), "HPF"), (curve.get("lpf"), "LPF")):
        if not f or (lbl == "HPF" and float(f) <= 20):
            continue
        xf = X(float(f))
        d.add(Line(xf, y0, xf, y1, strokeColor=axis, strokeWidth=0.7,
                   strokeDashArray=[2, 2]))
        right = xf > x1 - 46          # flip the label inward near the plot edge
        d.add(String(xf - 2 if right else xf + 2, y1 - 6,
                     f"{lbl} {_fmt_hz(float(f))}", fontName="Helvetica-Bold",
                     fontSize=5.8, fillColor=axis,
                     textAnchor="end" if right else "start"))

    # band markers — gain, frequency, Q, and a D when the band is dynamic.
    # Labels are nudged vertically off each other so clustered bands stay legible.
    placed = []
    marks = []
    for b in curve.get("bands", []):
        g = float(b.get("gain") or 0)
        if abs(g) < 0.05:
            continue
        f, q = float(b["freq"]), float(b.get("q") or 1.0)
        tag = f"B{int(b.get('b', 0))} {g:+g} @{_fmt_hz(f)} Q{q:g}"
        if b.get("deq"):
            tag += " D"
        marks.append((X(f), Y(g), g, tag))
    for bx, by, g, tag in sorted(marks, key=lambda m: m[0]):
        d.add(Circle(bx, by, 2.3, fillColor=accent, strokeColor=colors.white,
                     strokeWidth=0.6))
        tw = len(tag) * 3.0
        tx = min(max(bx - tw / 2, x0 + 1), x1 - tw - 1)
        step = 7.0 if g >= 0 else -7.0
        ty = by + 5 if g >= 0 else by - 10
        for _ in range(5):
            box = (tx, ty, tx + tw, ty + 6)
            if not any(box[0] < p[2] and p[0] < box[2] and box[1] < p[3] and p[1] < box[3]
                       for p in placed):
                break
            ty += step
        ty = min(max(ty, y0 + 2), y1 - 7)
        placed.append((tx, ty, tx + tw, ty + 6))
        d.add(String(tx, ty, tag, fontName="Helvetica-Bold", fontSize=5.8, fillColor=ink))

    d.add(String(x0, H - 11, "EQ RESPONSE", fontName="Helvetica-Bold", fontSize=6.4,
                 fillColor=ink))
    d.add(String(x1, H - 11, "HPF/LPF drawn at 12 dB/oct — corner exact, slope indicative",
                 fontName="Helvetica", fontSize=5.6, fillColor=axis, textAnchor="end"))
    return d


# ---------------------------------------------------------------------------
# EQ TABLE
# ---------------------------------------------------------------------------

def eq_table(rows, console="wing"):
    """
    EQ table. rows = list of dicts:
      band, freq, type, gain, q, notes
    type values: 'LC', 'HC', 'Shelf', 'Bell', 'OFF'
    console: 'wing' or 'digico'

    Wing band order:  LC → L → 1 → 2 → 3 → 4 → HC  (no H/High Shelf)
    DiGiCo band order: LC → L → 1 → 2 → 3 → 4 → HC
    Dynamic EQ (DiGiCo): append to notes field inline:
      "DYNAMIC: Thresh -26dBFS / Ratio 4:1 / Att 8ms / Rel 80ms / Max -3dB additional"
    """
    dark, mid, accent = get_console_colors(console)

    cb_s = mks('cb', 'Normal', fontSize=8.5, textColor=colors.white,
               fontName='Helvetica-Bold', alignment=TA_CENTER)
    cn_s = mks('cn', 'Normal', fontSize=8, textColor=colors.black,
               fontName='Helvetica', alignment=TA_LEFT, leading=11)
    cs_s = mks('cs', 'Normal', fontSize=7.5, textColor=colors.HexColor("#333333"),
               fontName='Helvetica', alignment=TA_LEFT, leading=11)

    COL_W = [0.55 * inch, 0.75 * inch, 0.7 * inch, 0.55 * inch, 0.5 * inch, 4.25 * inch]
    hdrs = ["Band", "Freq", "Type", "Gain", "Q", "Notes / Rationale"]
    data = [[Paragraph(h, cb_s) for h in hdrs]]

    for r in rows:
        type_v = r.get('type', 'Bell')
        data.append([
            Paragraph(str(r.get('band', '')), cn_s),
            Paragraph(str(r.get('freq', '—')), cn_s),
            Paragraph(str(type_v), cn_s),
            Paragraph(str(r.get('gain', '—')), cn_s),
            Paragraph(str(r.get('q', '—')), cn_s),
            Paragraph(str(r.get('notes', '')), cs_s),
        ])

    t = Table(data, colWidths=COL_W, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), dark),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#888888")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 1), (4, -1), 'CENTER'),
    ]
    for i, row in enumerate(rows, 1):
        type_v = row.get('type', 'Bell')
        if type_v == 'OFF':
            bg = OFF_BG
        elif type_v in ('LC', 'HC'):
            bg = LC_BG
        elif type_v == 'Shelf':
            bg = SHELF_BG
        else:
            bg = BELL_BG
        cmds.append(('BACKGROUND', (0, i), (-1, i), bg))
    t.setStyle(TableStyle(cmds))
    return t


# ---------------------------------------------------------------------------
# EQ PAGE ASSEMBLY
# ---------------------------------------------------------------------------

def build_eq_pages(channels, console="wing", marks=None):
    """
    channels: list of dicts with keys:
      ch, name, mic, section, accent (HexColor), mic_notes, bands (list), summary
      curve: optional numeric response spec for the EQ card (see eq_curve_card).
             Omit it and the card is derived from `bands` by curve_from_rows().
    marks: optional list — collects PageMark entries for the MASTER quick-links page.
    """
    story = []
    sections_grouped = {}
    for ch in channels:
        sections_grouped.setdefault(ch["section"], []).append(ch)

    for section_label, section_channels in sections_grouped.items():
        accent_bg = section_channels[0]["accent"]
        if marks is not None:
            story.append(PageMark(marks, "section", section_label))
        story.append(section_bar(f"━  {section_label}  ━", bg=accent_bg))
        story.append(Spacer(1, 8))
        for ch in section_channels:
            if marks is not None:
                story.append(PageMark(marks, "channel", str(ch["name"]),
                                      ch=ch["ch"], section=section_label))
            story.append(channel_header(ch["ch"], ch["name"], ch["mic"], ch["accent"]))
            story.append(Spacer(1, 4))
            story.append(eq_curve_card(ch.get("curve") or curve_from_rows(ch["bands"]),
                                       ch["accent"]))
            story.append(Spacer(1, 4))
            story.append(mic_notes_box(ch["mic_notes"]))
            story.append(Spacer(1, 4))
            story.append(eq_table(ch["bands"], console=console))
            story.append(Spacer(1, 4))
            story.append(engineer_notes_box(ch["summary"], console=console))
            story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# INPUT LIST PAGE
# ---------------------------------------------------------------------------

def build_input_list_page(channels, show_name, venue, date, rev,
                          foh_engineer, mon_engineer, show_time, console="wing"):
    """
    channels: list of dicts:
      ch, name, mic, section, patch, phantom_48v (bool), stand, notes
    """
    story = []
    dark, mid, accent = get_console_colors(console)

    title_s = mks('itl', 'Normal', fontSize=18, textColor=colors.white,
                  fontName='Helvetica-Bold', alignment=TA_CENTER)
    sub_s   = mks('isb', 'Normal', fontSize=9.5, textColor=colors.white,
                  fontName='Helvetica-Bold', alignment=TA_LEFT)
    hdr_s   = mks('ihd', 'Normal', fontSize=10, textColor=colors.white,
                  fontName='Helvetica-Bold', alignment=TA_CENTER)
    sec_s   = mks('isc', 'Normal', fontSize=11, textColor=colors.black,
                  fontName='Helvetica-Bold', alignment=TA_LEFT)
    dat_s   = mks('idt', 'Normal', fontSize=9.5, textColor=colors.black,
                  fontName='Helvetica', alignment=TA_LEFT, leading=11)
    chk_s   = mks('ick', 'Normal', fontSize=12, textColor=EMERALD,
                  fontName='Helvetica-Bold', alignment=TA_CENTER)
    spr_s   = mks('isp', 'Normal', fontSize=9.5, textColor=colors.HexColor("#9CA3AF"),
                  fontName='Helvetica-Oblique', alignment=TA_LEFT)

    # Column widths: Ch · Instrument · Mic/DI · Patch · 48V · Stand · Notes
    COL_W = [0.40 * inch, 1.45 * inch, 1.85 * inch, 0.85 * inch,
             0.45 * inch, 0.65 * inch, 1.65 * inch]

    title_t = Table([[Paragraph(show_name, title_s)]], colWidths=[7.3 * inch])
    title_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SPEC_TITLE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(title_t)

    sub_data = [
        [Paragraph(f"<b>VENUE:</b> {venue}", sub_s),
         Paragraph(f"<b>DATE:</b> {date}", sub_s),
         Paragraph(f"<b>REV:</b> {rev}", sub_s)],
        [Paragraph(f"<b>FOH:</b> {foh_engineer}", sub_s),
         Paragraph(f"<b>MON:</b> {mon_engineer}", sub_s),
         Paragraph(f"<b>SHOW TIME:</b> {show_time}", sub_s)],
    ]
    sub_t = Table(sub_data, colWidths=[3.0 * inch, 2.15 * inch, 2.15 * inch])
    sub_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SPEC_SUB),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sub_t)
    story.append(Spacer(1, 8))

    hdrs = ["Ch", "Instrument", "Mic / DI", "Patch", "48V", "Stand", "Notes"]
    table_data = [[Paragraph(h, hdr_s) for h in hdrs]]
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), SPEC_HDR),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#9CA3AF")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]

    row_idx = 1
    prev_sec = None
    for ch_data in channels:
        section = ch_data.get("section", "SPARE")
        is_spare = ch_data["name"] == "SPARE"
        is_first = (section != prev_sec)
        prev_sec = section
        hdr_hex, alt_hex = SEC_COLORS.get(section, ("#E5E7EB", "#F3F4F6"))
        hdr_c = colors.HexColor(hdr_hex)
        alt_c = colors.HexColor(alt_hex)

        if is_first:
            table_data.append([Paragraph(f"  ▌ {section}", sec_s), "", "", "", "", "", ""])
            style_cmds += [
                ('SPAN', (0, row_idx), (-1, row_idx)),
                ('BACKGROUND', (0, row_idx), (-1, row_idx), hdr_c),
                ('LINEABOVE', (0, row_idx), (-1, row_idx), 1.5, colors.HexColor("#111827")),
                ('TOPPADDING', (0, row_idx), (-1, row_idx), 5),
                ('BOTTOMPADDING', (0, row_idx), (-1, row_idx), 5),
            ]
            row_idx += 1

        p48v = "✓" if ch_data.get("phantom_48v") else ""
        row = [
            Paragraph(str(ch_data["ch"]),          spr_s if is_spare else dat_s),
            Paragraph(ch_data["name"],              spr_s if is_spare else dat_s),
            Paragraph(ch_data.get("mic", "—"),     spr_s if is_spare else dat_s),
            Paragraph(ch_data.get("patch", "—"),   spr_s if is_spare else dat_s),
            Paragraph(p48v, chk_s),
            Paragraph(ch_data.get("stand", "—"),   spr_s if is_spare else dat_s),
            Paragraph(ch_data.get("notes", ""),    spr_s if is_spare else dat_s),
        ]
        table_data.append(row)
        style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx),
                           alt_c if row_idx % 2 == 0 else colors.white))
        row_idx += 1

    tbl = Table(table_data, colWidths=COL_W, repeatRows=1)
    tbl.setStyle(TableStyle(style_cmds))
    story.append(tbl)
    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# COVER PAGE
# ---------------------------------------------------------------------------

def build_cover_page(show_name, venue, date, console_label, foh_engineer,
                     mon_engineer, show_time, rev, channel_count,
                     style_note, contents_list, console="wing"):
    story = []
    dark, mid, accent = get_console_colors(console)

    title_s = mks('ct', 'Title', fontSize=26, textColor=colors.white,
                  fontName='Helvetica-Bold', alignment=TA_CENTER)
    sub_s   = mks('cs', 'Normal', fontSize=13, textColor=colors.white,
                  fontName='Helvetica-Bold', alignment=TA_CENTER, leading=18)
    lbl_s   = mks('cl', 'Normal', fontSize=10, textColor=colors.HexColor("#374151"),
                  fontName='Helvetica-Bold', alignment=TA_LEFT)
    val_s   = mks('cv', 'Normal', fontSize=11, textColor=colors.black,
                  fontName='Helvetica', alignment=TA_LEFT)
    note_s  = mks('cn2', 'Normal', fontSize=9, textColor=colors.HexColor("#333333"),
                  fontName='Helvetica', leading=13)

    story.append(Spacer(1, 0.5 * inch))

    banner = Table([
        [Paragraph(show_name, title_s)],
        [Paragraph(f"FOH CHANNEL EQ SETUP — {console_label}", sub_s)],
    ], colWidths=[7.3 * inch])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), dark),
        ('TOPPADDING', (0, 0), (0, 0), 24),
        ('BOTTOMPADDING', (0, 1), (0, 1), 24),
        ('TOPPADDING', (0, 1), (0, 1), 0),
    ]))
    story.append(banner)
    story.append(Spacer(1, 0.3 * inch))

    meta = [
        ("Show",              show_name),
        ("Show Date",         date),
        ("Venue",             venue),
        ("Console",           console_label),
        ("Channels",          str(channel_count)),
        ("FOH Engineer",      foh_engineer),
        ("Monitor Engineer",  mon_engineer),
        ("Show Time",         show_time),
        ("Rev",               rev),
    ]
    meta_rows = [[Paragraph(l, lbl_s), Paragraph(v, val_s)] for l, v in meta]
    meta_t = Table(meta_rows, colWidths=[1.8 * inch, 5.5 * inch])
    meta_t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F9FAFB")),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 0.25 * inch))

    contents_text = "<b>DOCUMENT CONTENTS</b><br/><br/>" + \
                    "<br/>".join(f"<b>{i + 1}. {item}</b>" for i, item in enumerate(contents_list))
    cnt_t = Table([[Paragraph(contents_text, note_s)]], colWidths=[7.3 * inch])
    cnt_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('BOX', (0, 0), (-1, -1), 1.2, dark),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cnt_t)
    story.append(Spacer(1, 0.2 * inch))

    style_t = Table([[Paragraph(f"<b>SHOW STYLE:</b> {_esc(style_note)}", note_s)]],
                    colWidths=[7.3 * inch])
    style_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#92400E")),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(style_t)
    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# MAIN ASSEMBLY
# ---------------------------------------------------------------------------

def build_show_packet(output_path, show_data, input_list_channels,
                      eq_channels, console="wing"):
    """
    output_path:          str — save path for PDF
    show_data:            dict — show_name, venue, date, console_label, foh_engineer,
                                 mon_engineer, show_time, rev, channel_count, style_note
    input_list_channels:  list of dicts for input list (ch, name, mic, section,
                                                         patch, phantom_48v, stand, notes)
    eq_channels:          list of dicts for EQ pages (ch, name, mic, section, accent,
                                                       mic_notes, bands, summary)
    console:              'wing' or 'digico'

    Returns the page map (list of dicts: kind, label, page, + ch/section on
    channel entries) — the MASTER PDF's quick-links page is built from it.
    """
    marks = []
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.5 * inch,  bottomMargin=0.5 * inch,
    )
    story = []

    contents = [
        "Cover Page — show, venue, and personnel",
        "Input List — color-coded full channel patch sheet",
        "Patching — AES and Local inputs sorted by port",
        f"EQ Setup — {show_data['channel_count']} channels for {show_data['console_label']}",
        "Reference — EQ structure, pan guide, bus grouping, soundcheck order",
    ]

    story.append(PageMark(marks, "doc", "Cover"))
    story += build_cover_page(
        show_name=show_data["show_name"],
        venue=show_data["venue"],
        date=show_data["date"],
        console_label=show_data["console_label"],
        foh_engineer=show_data["foh_engineer"],
        mon_engineer=show_data.get("mon_engineer", "TBD"),
        show_time=show_data.get("show_time", "TBD"),
        rev=show_data.get("rev", "Rev 1.0"),
        channel_count=show_data["channel_count"],
        style_note=show_data["style_note"],
        contents_list=contents,
        console=console,
    )

    story.append(PageMark(marks, "doc", "Input List"))
    story += build_input_list_page(
        channels=input_list_channels,
        show_name=show_data["show_name"],
        venue=show_data["venue"],
        date=show_data["date"],
        rev=show_data.get("rev", "Rev 1.0"),
        foh_engineer=show_data["foh_engineer"],
        mon_engineer=show_data.get("mon_engineer", "TBD"),
        show_time=show_data.get("show_time", "TBD"),
        console=console,
    )

    story += build_eq_pages(eq_channels, console=console, marks=marks)

    doc.build(story)
    print(f"Packet built: {output_path}")
    return marks


# ---------------------------------------------------------------------------
# CHANNEL DATA FORMAT (reference)
# ---------------------------------------------------------------------------
#
# input_list_channels entry:
# {
#   "ch": 1,
#   "name": "Kick",
#   "mic": "Earthworks DM6",       # full name, no shorthand
#   "section": "DRUMS",            # DRUMS / RHYTHM / PIANO / STRINGS / HORNS / VOCALS / AMBIENT / SPARE
#   "patch": "Local 1",            # "Local 1" or "AES-1" — never abbreviate
#   "phantom_48v": False,          # True = ✓ checkmark; False = blank
#   "stand": "Short",              # Short / Tall / Boom / Bar / Clip / DI / —
#   "notes": "",
# }
#
# eq_channels entry:
# {
#   "ch": 1,
#   "name": "Kick",
#   "mic": "Earthworks DM6",
#   "section": "DRUMS",
#   "accent": DRUMS_BAR,
#   "mic_notes": "SeisMic design ...",
#   "bands": [
#     {"band": "LC",  "freq": "40 Hz",   "type": "LC",    "gain": "—",    "q": "18 dB/oct", "notes": "..."},
#     {"band": "L",   "freq": "80 Hz",   "type": "Shelf", "gain": "+2 dB","q": "—",         "notes": "..."},
#     {"band": "1",   "freq": "250 Hz",  "type": "Bell",  "gain": "-3 dB","q": "1.8",       "notes": "..."},
#     {"band": "2",   "freq": "800 Hz",  "type": "Bell",  "gain": "-2 dB","q": "1.5",       "notes": "..."},
#     {"band": "3",   "freq": "3.5 kHz", "type": "Bell",  "gain": "+2 dB","q": "1.0",       "notes": "..."},
#     {"band": "4",   "freq": "—",       "type": "OFF",   "gain": "—",    "q": "—",         "notes": "Not needed"},
#     {"band": "HC",  "freq": "—",       "type": "OFF",   "gain": "—",    "q": "—",         "notes": ""},
#     # NOTE: No H (High Shelf) band unless explicitly requested
#   ],
#   "summary": "Engineer notes for this channel.",
# }
#
# DiGiCo Dynamic EQ — append inline to notes field:
#   "DYNAMIC: Thresh -26dBFS / Ratio 4:1 / Att 8ms / Rel 80ms / Max -3dB additional"
