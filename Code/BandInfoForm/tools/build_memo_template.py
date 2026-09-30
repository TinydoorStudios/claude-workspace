#!/usr/bin/env python3
"""Build the Memorial Hall Prod Adv template. Reproducible.

Merges the two Memo advance docs Brian was running in 2026 (the 2018
"Memo Production Advance - BLANK" and the monthly "MEMO Adv -" sheet) into
one branded one-page doc in the universal template's layout: schedule + crew
down the left, the event grid on the right with ARTIST 1 / ARTIST 2 columns.
Advance only: the BLANK's post-show notes page was dropped (Brian, 2026-09-29).

The same code draws the blank template and the filled doc: memo_doc.py
passes a Values object and every box/cell renders from it, so the filed doc
can never drift from the template's layout.

Two variants: one artist (the default, ~95% of Memo shows) and two artists.
template_for(n_acts) picks between them at fill time.

    python3 build_memo_template.py            -> both into doc_templates/
    python3 build_memo_template.py some/dir   -> both into some/dir
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent / "app", HERE.parent):
    if (_c / "brand.py").exists():
        sys.path.insert(0, str(_c))
        break
import brand  # noqa: E402
from brand_docx import BODY, LABEL, RULE, BAR, PANEL, LOGO_H  # noqa: E402

OUT = HERE / "doc_templates" / "Memo Show Advance.docx"
OUT2 = HERE / "doc_templates" / "Memo Show Advance - 2 Artists.docx"
BOX = "☐"
BOXED = "☒"
SZ = 8.5          # body size
LBL_SZ = 8.5
MEMO = brand.venue_profile("Memorial Hall")
ACCENT = MEMO["secondary"]["hex"].lstrip("#").upper()   # Memo purple

LEFT_W = Inches(2.05)
RIGHT_W = Inches(5.45)
GL = Inches(1.15)                       # grid label column
GAP = "\u2003\u2003"                    # between checkbox options
ROW_TB = 14                             # cell top/bottom padding, twips
# Every size in this file is scaled by PROFILE["k"]; a filled two-artist doc
# runs compact so it stays on one page (Brian, 2026-09-29: one page, always).
PROFILE = {"k": 1.0, "grid_tb1": ROW_TB, "grid_tb2": 4}
BLANK_PROFILE = dict(PROFILE)
FILLED_1 = {"k": 0.94, "grid_tb1": 4, "grid_tb2": 4}     # a filled one-artist doc
COMPACT = {"k": 0.88, "grid_tb1": 0, "grid_tb2": 0}      # filled two-artist, or a long one-artist



# ---------------------------------------------------------------- xml helpers
def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def borders(table, color=RULE, sz=4, inside=True):
    tblpr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        if edge.startswith("inside") and not inside:
            e.set(qn("w:val"), "nil")
        else:
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), str(sz))
            e.set(qn("w:color"), color)
        b.append(e)
    tblpr.append(b)


def no_borders(table):
    tblpr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "nil")
        b.append(e)
    tblpr.append(b)


def cell_margins(table, lr=60, tb=10):
    tblpr = table._tbl.tblPr
    m = OxmlElement("w:tblCellMar")
    for edge, v in (("top", tb), ("left", lr), ("bottom", tb), ("right", lr)):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        m.append(e)
    tblpr.append(m)


def fixed(table, widths):
    table.autofit = False
    tblpr = table._tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblpr.append(lay)
    for row in table.rows:
        for c, w in zip(row.cells, widths):
            c.width = w


def tight(p, before=0, after=0):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.0


def put(cell, text, *, size=SZ, bold=False, italic=False, font=BODY,
        color=None, align=None, first=True):
    """Write text into a cell. '\n' starts a new paragraph."""
    for i, line in enumerate(text.split("\n")):
        p = cell.paragraphs[0] if (first and i == 0) else cell.add_paragraph()
        tight(p)
        if align:
            p.alignment = align
        r = p.add_run(line)
        r.font.size = Pt(round(size * PROFILE["k"] * 4) / 4)
        r.font.name = font
        r.bold = bold
        r.italic = italic
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return cell


def label(cell, text, **kw):
    kw.setdefault("size", LBL_SZ)
    return put(cell, text, font=LABEL, bold=True, **kw)


def bar(table, text, cols):
    row = table.add_row()
    c = row.cells[0].merge(row.cells[cols - 1]) if cols > 1 else row.cells[0]
    shade(c, BAR)
    label(c, text, color="FFFFFF", size=8.5)
    return row


# ---------------------------------------------------------------- values
class Values:
    """What the doc prints. Empty = the blank template. memo_doc.py fills it:
      event   {field: value}        event-level answers (memo_fields per_act=False)
      acts    [{field: value}, ...]  one dict per artist column, name under "_name"
      crew    [(role, name), ...]    CREW table rows, in order
    """
    def __init__(self, event=None, acts=None, crew=None):
        self.event = event or {}
        self.acts = acts or []
        self.crew = crew

    def ev(self, k):
        v = self.event.get(k)
        return "" if v is None else v

    def act(self, i, k):
        a = self.acts[i] if i < len(self.acts) else {}
        v = a.get(k)
        return "" if v is None else v


BLANK = Values()


def opts(options, sel, gap):
    """Checkbox group; ticks `sel` (a str, or a list for a multi group)."""
    chosen = set(sel) if isinstance(sel, (list, tuple, set)) else {sel}
    return gap.join(f"{BOXED if o in chosen else BOX} {o}" for o in options)


def blank(v, n=8):
    return v if str(v).strip() else "_" * n


CREW_ROLES = [
    "FOH", "Monitors", "LX", "Stage Hand", "Stage Hand", "Video",
    "Stage Support", "Stage Support", "Stage Support", "Memo Lead",
]
SCHEDULE = [
    ("Crew Call", "crew_call"), ("Backline Load-In", "backline_load_in"),
    ("Artist Load-In", "artist_load_in"), ("Sound Check", "sound_check"),
    ("Crew Break", "crew_break"), ("Security Meeting", "security_meeting"),
    ("Doors", "doors"), ("House", "house"),
    ("Set 1 Start", "set_1"), ("Set 1 End", "set_1_end"),
    ("Intermission (20m)", None),
    ("Set 2 Start", "set_2"), ("Set 2 End", "set_2_end"),
    ("End of Show / Load-Out", "end_of_show"), ("Curfew (+90 min)", "curfew"),
]


# ---------------------------------------------------------------- page 1
def left_column(cell, V=BLANK):
    cell.paragraphs[0].text = ""
    label(cell, "SCHEDULE", size=9.5)

    t = cell.add_table(rows=0, cols=2)
    borders(t)
    cell_margins(t, tb=ROW_TB)
    for s, key in SCHEDULE:
        r = t.add_row()
        put(r.cells[0], V.ev(key) if key else "", size=7.5)
        put(r.cells[1], s)
        if key is None:
            put(r.cells[1], opts(("Yes", "No"), V.ev("intermission"), GAP),
                size=7, first=False)
    fixed(t, [Inches(0.5), Inches(1.4)])

    p = cell.add_paragraph()
    tight(p, before=4)
    label(cell, "CREW", size=9.5, first=False)
    crew = V.crew if V.crew is not None else [
        (k, "Joe · 216-288-7269" if k == "Memo Lead" else "") for k in CREW_ROLES]
    t = cell.add_table(rows=0, cols=2)
    borders(t)
    cell_margins(t, tb=ROW_TB)
    for k, v in crew:
        r = t.add_row()
        label(r.cells[0], k, size=7.5)
        put(r.cells[1], v or "")
    fixed(t, [Inches(0.72), Inches(1.18)])

    notes = [
        ("House notes:", True, False),
        ("At Memo, techs are generally not responsible for paying the band.", False, True),
        ("Artists and clients are always welcome to the coffee/tea set-ups "
         "in the dressing rooms.", False, True),
        ("Route pre-roll to the ballrooms and theater. Route show video and "
         "audio to the ballrooms.", False, True),
        ("**When they arrive, introduce yourself to the client, [NAME], so "
         "they can put faces to names.", True, False),
    ]
    for text, b, it in notes:
        p = cell.add_paragraph()
        tight(p, before=3)
        r = p.add_run(text)
        r.font.size = Pt(7.5)
        r.font.name = LABEL if text.endswith(":") else BODY
        r.bold = b
        r.italic = it


def grid(cell, artists=1, V=BLANK):
    cell.paragraphs[0].text = ""
    tight(cell.paragraphs[0])
    n = artists + 1
    gap = GAP if artists == 1 else " "   # narrower columns, tighter options
    t = cell.add_table(rows=0, cols=n)
    borders(t)
    cell_margins(t, lr=55, tb=PROFILE["grid_tb1"] if artists == 1 else PROFILE["grid_tb2"])

    def whole(r):
        return r.cells[1].merge(r.cells[-1]) if n > 2 else r.cells[1]

    def row(lbl, fn):
        """Per-artist row: fn(i) -> text for artist column i."""
        r = t.add_row()
        label(r.cells[0], lbl, align=WD_ALIGN_PARAGRAPH.RIGHT)
        for i, c in enumerate(r.cells[1:]):
            put(c, fn(i))
        return r

    def erow(lbl, text):
        """Event-level row, one merged value cell."""
        r = t.add_row()
        label(r.cells[0], lbl, align=WD_ALIGN_PARAGRAPH.RIGHT)
        put(whole(r), text)
        return r

    def yn(key, extra=""):
        return lambda i: opts(("Yes", "No"), V.act(i, key), gap) if not extra else \
            f"{BOXED if V.act(i, key) == 'Yes' else BOX} Yes{extra(i)}{gap}" \
            f"{BOXED if V.act(i, key) == 'No' else BOX} No"

    def ch(key, options):
        return lambda i: opts(options, V.act(i, key), gap)

    def txt(key):
        return lambda i: V.act(i, key)

    # EVENT INFORMATION
    r = t.add_row()
    shade(r.cells[0], BAR)
    label(r.cells[0], "EVENT\nINFORMATION", color="FFFFFF", size=8.5)
    c = whole(r)
    shade(c, PANEL)
    put(c, f"Date: {V.ev('_date')}\nEvent: {V.ev('_event')}\nPresenter: {V.ev('presenter')}\n"
           "Venue: Memorial Hall · 1225 Elm St, Cincinnati OH 45202")
    erow("Event Type", opts(("Internal Event", "Third Party Event"), V.ev("event_type"), gap)
         .replace("Third Party Event", "Third Party Event:"))

    bar(t, "AUDIO", n)
    r = t.add_row()
    for i, c in enumerate(r.cells[1:]):
        nm = V.act(i, "_name")
        head = "ARTIST:" if artists == 1 else f"ARTIST {i + 1}:"
        label(c, f"{head} {nm}".strip(),
              align=None if artists == 1 else WD_ALIGN_PARAGRAPH.CENTER)
    row("Set Length", txt("set_length"))
    row("Stage Plot", txt("_stage_plot"))
    def eng(i, own, name):
        o = V.act(i, own)
        return V.act(i, name) or ("House" if o == "House" else "Tour (TBD)" if o == "Yes" else "")
    row("Engineer", lambda i: f"FOH – {eng(i, 'own_foh', 'engineer_foh')}\n"
                              f"Mon – {eng(i, 'own_mon', 'engineer_mon')}")
    row("Consoles", lambda i: f"FOH –  {opts(('House Q225', 'Tour'), V.act(i, 'console_foh'), gap)}\n"
                              f"Mon –  {opts(('House', 'Tour'), V.act(i, 'console_mon'), gap)}")
    iem = lambda i: opts(("Yes", "No"), V.act(i, "iems"), gap)  # noqa: E731

    def iem_more(i):
        """own rig / split, the FSQ chain — only once IEMs = Yes"""
        if V.act(i, "iems") != "Yes":
            return ""
        own = V.act(i, "own_iems")
        s = f"Own rig: {own or '—'}"
        if own == "Yes":
            s += f"{gap}Split: {V.act(i, 'split_snake') or '—'}"
        return "\n" + s
    if artists > 1:
        row("Monitors / IEMs", lambda i: f"Wedges: {V.act(i, 'wedges')}{gap}IEMs #: {V.act(i, 'iem_count')}"
                                         f"\nIEMs:  {iem(i)}{iem_more(i)}")
    else:
        row("Monitors / IEMs", lambda i: f"Wedges: {V.act(i, 'wedges')}{gap}{gap}IEMs:  {iem(i)}"
                                         f"{gap}#: {V.act(i, 'iem_count')}{iem_more(i)}")
    row("Input Notes", txt("input_notes"))
    row("Backline", lambda i: opts(("Yes", "No"), V.act(i, "backline"), gap) + "  (brings all)"
        + (f"\n{V.act(i, 'backline_notes')}" if V.act(i, "backline_notes") else ""))

    bar(t, "LIGHTING", n)
    row("LD", ch("ld", ("House LD", "Artist LD")))
    row("LX Console", ch("lx_console", ("Memo", "Tour")))
    row("Ground Package", yn("ground_package"))
    row("Lighting Notes", txt("lighting_notes"))

    bar(t, "SCENIC", n)
    row("Risers", lambda i: opts(("Yes", "No"), V.act(i, "risers"), gap)
        + f"{gap}#: {V.act(i, 'riser_count')}{gap}(4' x 8' x 1')")
    row("Grand Piano", yn("grand_piano"))
    row("Scenic Notes", txt("scenic_notes"))

    bar(t, "MISC", n)
    rooms = ("A", "B", "C", "D", "Studio", "Any")
    row("Dressing Rooms", lambda i: gap.join(
        f"{k} {BOXED if k in (V.act(i, 'dressing_rooms') or []) else BOX}" for k in rooms))
    srooms = ("A", "B", "C", "D", "Studio", "None")
    erow("Stage Support", gap.join(
        f"{k} {BOXED if k in (V.ev('stage_support_rooms') or []) else BOX}" for k in srooms))
    row("Performers", txt("performers"))
    money = lambda key: yn(key, extra=lambda i: f"  $ {blank(V.act(i, key + '_amount'))}")  # noqa: E731
    row("Hospitality", money("hospitality"))
    row("Buyout", money("buyout"))

    def parking(i):
        sel = V.act(i, "parking")
        dash, wp = V.act(i, "dashboard_passes"), V.act(i, "wp_passes")
        veh = ", ".join(f"{V.act(i, k)} {lbl}" for k, lbl in (
            ("veh_personal", "personal"), ("veh_sprinter", "sprinter"), ("veh_bus", "bus"),
            ("veh_semi", "semi")) if str(V.act(i, k)).strip() not in ("", "0"))
        s = (f"{BOXED if sel == 'SP+ Lot' else BOX} SP+ Lot — Dashboard passes: {blank(dash, 4)}\n"
             f"{BOXED if sel == 'Washington Park' else BOX} Washington Park — passes: {blank(wp, 4)}"
             f"{gap}{BOXED if sel == 'No' else BOX} No")
        return s + (f"\nVehicles: {veh}" if veh else "")
    row("Parking", parking)
    row("Hotel", yn("hotel"))
    row("Merch", ch("merch", ("They sell", "Memo sells", "No")))
    row("Runner", yn("runner"))
    row("Ground Transport", yn("ground_transport"))
    row("Meet & Greet", yn("meet_greet"))
    row("Photography", yn("photography"))
    row("Photo Restrictions", txt("photo_restrictions"))
    erow("Settlement", opts(("Yes", "No"), V.ev("settlement"), gap)
         + f"{gap}Contact: {V.ev('settlement_contact')}")
    if artists > 1:
        row("Band Contact", lambda i: f"Name: {V.act(i, 'contact_name')}\nCell: {V.act(i, 'contact_phone')}"
                                      f"\nEmail: {V.act(i, 'contact_email')}")
    else:
        row("Band Contact", lambda i: f"Name: {V.act(i, 'contact_name')}\n"
                                      f"Cell: {V.act(i, 'contact_phone')}{gap}{gap}{gap}{gap}"
                                      f"Email: {V.act(i, 'contact_email')}")
    row("Additional Info", txt("additional_info"))
    r = erow("Internal Notes", V.ev("internal_notes"))   # staff-only on the form
    shade(whole(r), PANEL)

    gv = (RIGHT_W - GL - Inches(0.1)) // artists
    fixed(t, [GL] + [gv] * artists)


# ---------------------------------------------------------------- build
def new_doc():
    d = Document()
    st = d.styles["Normal"]
    st.font.name = BODY
    st.font.size = Pt(SZ)
    st.font.color.rgb = RGBColor.from_string(BAR)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), BODY)
    tight(st)

    sec = d.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(0.5)
    sec.top_margin = Inches(0.65)
    sec.bottom_margin = Inches(0.3)
    sec.header_distance = Inches(0.3)

    # header: 3CDC mark left, Memo wordmark right (same as daysheet stamps)
    hp = sec.header.paragraphs[0]
    width = sec.page_width - sec.left_margin - sec.right_margin
    ts = hp.paragraph_format.tab_stops
    for pos in (Inches(3.25), Inches(6.5)):   # the Header style's own stops
        ts.add_tab_stop(pos, WD_TAB_ALIGNMENT.CLEAR)
    ts.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
    corp = brand.brand()["corporate"]["logos"]["primary"]
    hp.add_run().add_picture(str(brand.BRAND_DIR / corp), height=LOGO_H)
    hp.add_run("\t")
    hp.add_run().add_picture(
        str(brand.BRAND_DIR / "logos" / f"{MEMO['slug']}-typelogo.png"),
        height=Inches(0.26))

    return d


def finish(d, out):
    # Word needs a body paragraph after the last table; keep it 1pt high
    p = d.add_paragraph()
    tight(p)
    p.add_run(" ").font.size = Pt(1)
    p.paragraph_format.line_spacing = Pt(1)
    d.save(str(out))
    return out


def _text_load(V):
    """Rough count of wrapped value lines a filled doc adds (~70 chars/line at
    the one-artist width) — enough to tell a light fill from a long one."""
    n = 0
    for a in V.acts:
        for v in a.values():
            if isinstance(v, str) and v.strip():
                n += sum(len(line) // 70 for line in v.splitlines())
    return n


def _profile_for(artists, V):
    if V is BLANK:
        return BLANK_PROFILE
    if artists > 1 or _text_load(V) > 4:
        return COMPACT
    return FILLED_1


def build_advance(out=OUT, artists=1, V=BLANK):
    PROFILE.update(_profile_for(artists, V))
    d = new_doc()
    p = d.add_paragraph()
    tight(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("“The 3CDC Tech Team’s purpose is to provide professional "
                  "event support that enriches the Cincinnati community while "
                  "maintaining safe and respectful environments and prioritizing "
                  "integrity, teamwork and quality.”")
    r.italic = True
    r.font.size = Pt(7.5)
    p = d.add_paragraph()
    tight(p, after=4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("MEMORIAL HALL PRODUCTION ADVANCE")
    r.font.name = LABEL
    r.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor.from_string(ACCENT)

    outer = d.add_table(rows=1, cols=2)
    outer.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(outer, inside=True)
    cell_margins(outer, lr=60, tb=40)
    left_column(outer.rows[0].cells[0], V)
    grid(outer.rows[0].cells[1], artists, V)
    for c in outer.rows[0].cells:
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    fixed(outer, [LEFT_W, RIGHT_W])

    return finish(d, out)


def template_for(n_acts):
    """Template the doc-fill should start from: one artist unless a second
    act is booked into the same show."""
    return OUT2 if n_acts >= 2 else OUT


if __name__ == "__main__":
    dst = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT.parent
    print("wrote", build_advance(dst / OUT.name, 1))
    print("wrote", build_advance(dst / OUT2.name, 2))
