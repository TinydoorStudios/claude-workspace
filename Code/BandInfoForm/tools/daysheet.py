#!/usr/bin/env python3
"""Fill an advance day-sheet — single-band, 2-band, or 3-band — from an
event. The old 513 Airwaves-specific template is retired; nothing here
references it.

Template is picked automatically by VENUE + how many acts the event has:
  Fountain Square, 1 act  -> doc_templates/FSQ Single Band Advance.docx
  Fountain Square, 2 acts -> doc_templates/FSQ 2 Band Advance.docx
  Fountain Square, 3 acts -> doc_templates/FSQ 3 Band Advance.docx
  Washington Park, 1 act  -> doc_templates/WP Single Band Advance.docx
  (Washington Park has no 2/3-band template yet — those events error out
  with a clear message instead of silently reusing the wrong template.)
Acts map to columns left-to-right in event_acts' own slot_order (opener,
direct_support, headliner) — whichever slots the event actually has, in that
order, so a 2-band show booked as opener+headliner or as
direct_support+headliner both land correctly without a slot-name lookup.

Source of truth is the advance SPREADSHEET (event + any band overrides); the
advance FORM fills whatever the sheet left blank — the spreadsheet value
wins, same merge policy as the email drafts. Writes:
  - EVENT INFORMATION: Date / Event always; Band (single-band only — a
    multi-band show's names go on the act-header row instead); TONIGHT —
    MC/DJ (multi-band only)
  - Location (Washington Park only — Main Stage/Porch/Bandstand, from the
    sheet's Location column, seeded from bookings.location at booking time)
  - Event Type / Paying?, Lead name + cell
  - per-act: Set Length, act name (multi-band header row), Stage Plot,
    Monitors, IEMs, Input Notes (also carries any lighting request / split
    snake text — there's no dedicated cell for those), Stage Type, Scenic
    Notes, Merch, Parking, Drink Tix, Dressing Room Tent, Backline, Band
    Contact — Name / Cell
  - Engineer (FOH – / Mon –), same value repeated into every act column —
    pulled from the public 3CDC staffing sheet via staffing.engineers_for()
    (Brian, 2026-09-08); a line left as its unfilled placeholder ('FOH – ')
    means the sheet didn't resolve a clean name for that show, not that the
    row was skipped
  - the crew SCHEDULE table (Crew Call / Load In-Sound Check / Performance /
    Load-out / Curfew) — ONLY for a series with a locked '## Crew Schedule'
    section (venue_email.crew_schedule_for(); Brian, 2026-09-09: Salsa On
    The Square's times never change, so there's no reason to leave this for
    a same-day hand call the way every other show's crew schedule needs)

Left BLANK, always — no data source, or a same-day production call Brian
makes by hand (2026-09-03: "the granular items we will add by hand"):
  - the crew SCHEDULE table for every OTHER show (the minute-by-minute
    choreography is normally a day-of call, not form data)
  - Consoles, PA, Subs, LIGHTING (Pre-Scheduled/Live), VIDEO, Buyout

  python3 daysheet.py --event 1
"""
import argparse
import copy
import itertools
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import fieldspec as fs
import staffing
import venue_email as ve

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from urllib.parse import quote

TEMPLATES = HERE / "doc_templates"
FILLED = HERE / "filled"
FILLED.mkdir(exist_ok=True)
TEMPLATES_BY_VENUE = {
    "Fountain Square": {
        1: TEMPLATES / "FSQ Single Band Advance.docx",
        2: TEMPLATES / "FSQ 2 Band Advance.docx",
        3: TEMPLATES / "FSQ 3 Band Advance.docx",
    },
    "Washington Park": {
        1: TEMPLATES / "WP Single Band Advance.docx",
        # no 2/3-band WP template yet
    },
}
# kept for callers that don't pass one / don't know the venue yet
TEMPLATE_BY_ACTS = TEMPLATES_BY_VENUE["Fountain Square"]
DEFAULT_TEMPLATE = TEMPLATE_BY_ACTS[1]


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower().rstrip("?")


def _yn(b):
    return "Yes" if b is True else ("No" if b is False else None)


def form_fields(sub):
    """Flatten a form submission to sheet-key -> string, for merging."""
    if not sub:
        return {}
    d = sub.get("data") or {}
    out = {
        "contact_name": sub.get("contact_name") or d.get("contact_name"),
        "contact_phone": sub.get("contact_phone") or d.get("contact_phone"),
        "stage_type": sub.get("stage_type") or d.get("stage_type"),
        "monitors": (str(sub["monitors"]) if sub.get("monitors") is not None
                     else d.get("monitors")),
        "uses_iems": d.get("uses_iems"),
        "own_iems": _yn(sub.get("own_iems")) or d.get("own_iems"),
        "split_snake": sub.get("split_snake") or d.get("split_snake"),
        "stage_plot_desc": d.get("stage_plot_desc"),
        "input_notes": d.get("input_notes"),
        "backline": d.get("backline"),
        "own_engineer": sub.get("own_engineer") or d.get("own_engineer"),
        "scenic": d.get("scenic"),
        "lighting": d.get("lighting"),
        "merch": _yn(sub.get("merch")) or d.get("merch"),
        "band_tent": sub.get("band_tent") or d.get("band_tent"),
        "performers": (str(sub["performers"]) if sub.get("performers") is not None
                       else d.get("performers")),
        "large_vehicle": _yn(sub.get("large_vehicle")) or d.get("large_vehicle"),
        "stage_plot_file": d.get("stage_plot_file"),
    }
    return {k: v for k, v in out.items() if v not in (None, "")}


def merged_fields(act):
    """Spreadsheet overrides win; the form fills the blanks."""
    f = form_fields(act.get("submission"))
    for k, v in (act.get("sheet_fields") or {}).items():
        if v not in (None, ""):
            f[k] = v
    return f


def act_row_values(f):
    """Merged fields -> {normalized day-sheet row label: cell text}, matching
    the current templates' row set (Monitors/IEMs and Stage Type/Scenic
    Notes are separate rows now, not blended)."""
    out = {}
    if not f:
        return out

    saved = f.get("_stageplot_saved")
    if saved:
        out["stage plot"] = f"See DB — {saved}"
    else:
        sp = f.get("stage_plot_desc", "")
        if f.get("stage_plot_file"):
            sp = (sp + " (file on record)").strip()
        if sp:
            out["stage plot"] = sp

    if f.get("monitors") not in (None, ""):
        out["monitors"] = f"{f['monitors']} wedges"
    uses_iems = f.get("uses_iems")
    if uses_iems:
        out["iems"] = Checkbox(["Yes", "No"], uses_iems)
    elif f.get("own_iems"):
        # older submissions predate the "do you use IEMs" question — fall
        # back to the own-system answer, same as before this field existed
        out["iems"] = Checkbox(["Yes", "No"], f["own_iems"])

    notes = []
    if f.get("input_notes"):
        notes.append(f["input_notes"])
    if str(uses_iems or "").lower() == "yes" and f.get("own_iems"):
        notes.append(f"Own IEM system: {f['own_iems']}")
    if str(f.get("own_iems", "")).lower() == "yes" and f.get("split_snake"):
        notes.append(f"Split snake: {f['split_snake']}")
    if f.get("lighting"):
        notes.append(f"Lighting request: {f['lighting']}")
    if notes:
        out["input notes"] = " · ".join(notes)

    if f.get("stage_type"):
        out["stage type"] = Checkbox(
            ["Flat", "Riser"], "Riser" if "riser" in str(f["stage_type"]).lower() else "Flat")
    if f.get("scenic"):
        out["scenic notes"] = f["scenic"]

    if f.get("merch"):
        out["merch"] = f["merch"]
    if f.get("large_vehicle"):
        out["parking"] = "Large vehicle" if str(f["large_vehicle"]).lower() == "yes" else "Standard"
    if f.get("performers") not in (None, ""):
        out["drink tix"] = str(f["performers"])
    if f.get("band_tent"):
        out["dressing room tent"] = "Yes" if str(f["band_tent"]).lower().startswith("yes") else "No"
    if f.get("backline"):
        out["backline"] = f["backline"]
    if f.get("contact_name"):
        out["band contact — name"] = f["contact_name"]
    if f.get("contact_phone"):
        out["band contact — cell"] = f["contact_phone"]
    return out


class Checkbox:
    """Sentinel act_row_values() hands back for a checkbox-group field instead
    of a pre-rendered string — carries the raw (labels, chosen) so fill()
    can build real Word checkbox controls for it via set_checkbox_paragraph()
    instead of dropping plain text through set_cell() (Brian, 2026-09-08:
    the old ☐/☒ characters weren't real checkboxes — couldn't be clicked)."""
    __slots__ = ("labels", "chosen")

    def __init__(self, labels, chosen):
        self.labels = labels
        self.chosen = chosen


CHECKBOX_UNCHECKED = "☐"
CHECKBOX_CHECKED = "☒"
_sdt_id_counter = itertools.count(100000000)


def _make_checkbox_sdt(checked=False):
    """One real Word 'Check Box Content Control' (<w:sdt> + <w14:checkbox>)
    holding a single ☐/☒ run — genuinely clickable in Word, not a plain typed
    character. The visible glyph lives in an ordinary <w:t> run inside
    sdtContent, so anything that just reads run text (python-docx's own
    .text, LibreOffice's PDF converter used for the nightly recap
    extraction) still sees the right character without understanding sdt
    semantics at all."""
    sdt = OxmlElement('w:sdt')
    sdtPr = OxmlElement('w:sdtPr')
    id_el = OxmlElement('w:id')
    id_el.set(qn('w:val'), str(next(_sdt_id_counter)))
    sdtPr.append(id_el)
    checkbox = OxmlElement('w14:checkbox')
    checked_el = OxmlElement('w14:checked')
    checked_el.set(qn('w14:val'), '1' if checked else '0')
    checkbox.append(checked_el)
    checked_state = OxmlElement('w14:checkedState')
    checked_state.set(qn('w14:val'), '2612')
    checked_state.set(qn('w14:font'), 'MS Gothic')
    checkbox.append(checked_state)
    unchecked_state = OxmlElement('w14:uncheckedState')
    unchecked_state.set(qn('w14:val'), '2610')
    unchecked_state.set(qn('w14:font'), 'MS Gothic')
    checkbox.append(unchecked_state)
    sdtPr.append(checkbox)
    sdt.append(sdtPr)
    sdt.append(OxmlElement('w:sdtEndPr'))
    sdtContent = OxmlElement('w:sdtContent')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = CHECKBOX_CHECKED if checked else CHECKBOX_UNCHECKED
    r.append(t)
    sdtContent.append(r)
    sdt.append(sdtContent)
    return sdt


def full_text(paragraph):
    """A paragraph's visible text, including a run nested inside a checkbox
    content control (<w:sdt>). python-docx's own Paragraph.text only reads
    DIRECT <w:r>/<w:hyperlink> children, so it silently drops the checkbox
    glyph now that real Word checkboxes live in <w:sdt>/<w:sdtContent> —
    used anywhere this file reads a FILLED cell's content back out (the
    recap extraction). Label-matching (norm(r.cells[0].text)) doesn't need
    this — a label cell never contains a checkbox."""
    return "".join(t.text or "" for t in paragraph._p.iter(qn('w:t')))


def full_cell_text(cell):
    return "\n".join(full_text(p) for p in cell.paragraphs)


def _clear_paragraph(paragraph):
    """Strip every run/control out of a paragraph, leaving its <w:pPr> (if
    any) intact, ready to rebuild from scratch."""
    p = paragraph._p
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)


def set_checkbox_paragraph(paragraph, labels, chosen, prefix=""):
    """Rebuild `paragraph` from scratch as prefix + a real, clickable Word
    checkbox for every label ('☐ Label     ☐ Label ...'), whichever one
    matches `chosen` (via norm(), same loose match checkbox_pair always
    used) checked. `chosen` falsy or matching nothing leaves every box
    unchecked — used both to fill a real answer and to build each
    template's blank baseline, so a row the pipeline never touches is still
    a real, hand-checkable group instead of dead text."""
    _clear_paragraph(paragraph)
    if prefix:
        paragraph.add_run(prefix)
    for i, label in enumerate(labels):
        checked = bool(chosen) and norm(chosen) == norm(label)
        paragraph._p.append(_make_checkbox_sdt(checked))
        sep = "     " if i < len(labels) - 1 else ""
        paragraph.add_run(f" {label}{sep}")
    return paragraph


def iter_paragraphs_deep(container):
    """Every paragraph anywhere in `container` (a Document or a table cell) —
    body-level paragraphs plus every paragraph inside every table/cell,
    however deeply nested."""
    for p in container.paragraphs:
        yield p
    for t in getattr(container, "tables", []):
        for row in t.rows:
            for cell in row.cells:
                yield from iter_paragraphs_deep(cell)


def convert_plain_checkboxes(paragraph):
    """Catch-all for any ☐/☒ still sitting in `paragraph` as plain typed
    text rather than a real control — static template content no fill()
    function ever writes to (Brian, 2026-09-08: 'Drink Tickets'/'Talking
    points'/'Dashboard parking permit' in the Band Deliverables list, and
    the LIGHTING row's Pre-Scheduled/Live pair, were all missed by the
    first pass, which only converted the specific rows the code actually
    fills). Splits each run containing a glyph into real-control-in,
    plain-text-around, preserving the run's own formatting on the
    surrounding text and each glyph's existing checked/unchecked state —
    it doesn't know the 'right' answer for content it never wrote, only
    that it should be clickable like everything else. No-op on a run with
    no plain glyph (already-real controls, e.g. from
    set_checkbox_paragraph, are untouched since their glyph lives inside
    an <w:sdt>, not a direct <w:r>)."""
    p = paragraph._p
    for r_el in list(p.findall(qn('w:r'))):
        text = "".join(t.text or "" for t in r_el.findall(qn('w:t')))
        if CHECKBOX_UNCHECKED not in text and CHECKBOX_CHECKED not in text:
            continue
        rPr_el = r_el.find(qn('w:rPr'))
        pieces, buf = [], ""
        for ch in text:
            if ch in (CHECKBOX_UNCHECKED, CHECKBOX_CHECKED):
                if buf:
                    pieces.append(('text', buf))
                    buf = ""
                pieces.append(('box', ch == CHECKBOX_CHECKED))
            else:
                buf += ch
        if buf:
            pieces.append(('text', buf))
        for kind, val in pieces:
            if kind == 'box':
                new_el = _make_checkbox_sdt(checked=val)
            else:
                new_el = OxmlElement('w:r')
                if rPr_el is not None:
                    new_el.append(copy.deepcopy(rPr_el))
                t_el = OxmlElement('w:t')
                t_el.set(qn('xml:space'), 'preserve')
                t_el.text = val
                new_el.append(t_el)
            r_el.addprevious(new_el)
        p.remove(r_el)


def set_cell(cell, text):
    text = "" if text is None else str(text)
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r.text = ""
    (p.runs[0] if p.runs else p.add_run("")).text = text


def set_cell_link(cell, text, target):
    """Replace a cell's content with a single clickable hyperlink (blue, underlined).
    `target` is a relative path — the stage plot sits in the same folder as the doc,
    so Word resolves it wherever the folder lives."""
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    r_id = cell.part.relate_to(target, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1"); rPr.append(color)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rPr.append(u)
    run.append(rPr)
    t = OxmlElement("w:t"); t.text = text; run.append(t)
    link.append(run)
    p._p.append(link)


def set_para_text(paragraph, text):
    for extra in list(paragraph.runs[1:]):
        extra._element.getparent().remove(extra._element)
    (paragraph.runs[0] if paragraph.runs else paragraph.add_run("")).text = text


def append_to_run(paragraph, prefix, value):
    """Find the run starting with `prefix` and set it to prefix+value — used
    for label+blank lines like 'TONIGHT — MC: ' that have no separate blank
    run of their own to target."""
    for r in paragraph.runs:
        if r.text.strip().startswith(prefix.strip()):
            r.text = f"{prefix}{value}"
            return True
    return False


def all_tables(doc):
    out = []
    def rec(tbls):
        for t in tbls:
            out.append(t)
            for row in t.rows:
                for cell in row.cells:
                    rec(cell.tables)
    rec(doc.tables)
    return out


def find_grid(doc):
    """The one big EVENT INFORMATION -> MISC table (right-hand side)."""
    for t in all_tables(doc):
        for r in t.rows:
            if r.cells and norm(r.cells[0].text) == "event information":
                return t
    return None


def find_lead_table(doc):
    """The small Lead/Cell table (left-hand side)."""
    for t in all_tables(doc):
        if len(t.rows) == 2 and norm(t.rows[0].cells[0].text) == "lead":
            return t
    return None


def find_schedule_table(doc):
    """The small day-of crew table, left-hand side (time blank in cells[0],
    label in cells[-1]: Crew Call / Load In/Sound Check / Performance /
    Load-out / Curfew) — the minute-by-minute crew choreography, distinct
    from the EVENT INFORMATION grid's own header info and from the advance
    EMAIL's separate free-text 'Day Schedule:' block (venue_email's
    schedule_block_for)."""
    for t in all_tables(doc):
        if t.rows and norm(t.rows[0].cells[-1].text) == "crew call":
            return t
    return None


def fill_header(grid, event, acts, single):
    """EVENT INFORMATION value cell: Date / Event / Band (single-band only) /
    TONIGHT — MC/DJ (multi-band only) — each its own paragraph."""
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event information":
            value_cell = r.cells[1]
            date = event.get("event_date").isoformat() if event.get("event_date") else ""
            for p in value_cell.paragraphs:
                t = p.text.strip()
                if t.startswith("Date:"):
                    set_para_text(p, f"Date: {date}" if date else "Date:")
                elif t.startswith("Event:"):
                    set_para_text(p, f"Event: {event.get('name') or ''}")
                elif t.startswith("Band:") and single:
                    bands = ", ".join(a["artist"]["name"] for a in acts if a.get("artist"))
                    set_para_text(p, f"Band: {bands}" if bands else "Band:")
                elif t.startswith("TONIGHT"):
                    det = event.get("details") or {}
                    if det.get("mc"):
                        append_to_run(p, "TONIGHT — MC: ", det["mc"])
                    if det.get("dj"):
                        append_to_run(p, "     DJ: ", det["dj"])
            return


def fill_event_type(grid, event, n=1):
    """Event Type / Paying Band — an event-level fact, but the 2/3-band
    templates repeat this row once per act column (same shape as Engineer/
    Consoles), so it's written into every column, not just the first
    (fixed 2026-09-08 — cells 2/3 used to stay pristine-blank forever on a
    multi-band bill)."""
    det = event.get("details") or {}
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event type":
            for value_cell in r.cells[1:1 + n]:
                paras = value_cell.paragraphs
                if len(paras) >= 1 and det.get("event_type"):
                    set_checkbox_paragraph(
                        paras[0],
                        ["Internal Event:", "Third Party Event:"],
                        "Internal Event:" if norm(det["event_type"]) == "internal" else "Third Party Event:",
                    )
                if len(paras) >= 2 and det.get("paying_band"):
                    yn = "Yes" if norm(det["paying_band"]) == "yes" else "No"
                    set_checkbox_paragraph(paras[1], ["Yes", "No"], yn,
                                            prefix="Are we paying the band?   ")
            return


WP_LOCATIONS = ["Main Stage", "Porch", "Bandstand"]


def fill_location(grid, event):
    """WP-only Location row (☐ Main Stage ☐ Porch ☐ Bandstand) — checked from
    the booking (events.details.location, seeded via the sheet's Location
    column). No-op if the template has no Location row (FSQ) or the event has
    no location on file yet."""
    det = event.get("details") or {}
    loc = det.get("location")
    if not loc:
        return
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "location":
            set_checkbox_paragraph(r.cells[1].paragraphs[0], WP_LOCATIONS, loc)
            return


def fill_engineer(grid, event, n):
    """Engineer row (FOH – / Mon –), same value repeated into every act
    column — it's one FOH engineer and one Mon engineer for the whole SHOW,
    not per band, same as how the Consoles row already repeats its (static)
    value across columns. Pulled from the public 3CDC staffing sheet
    (Brian, 2026-09-08: cross-reference the Mix column's initials against the
    staffing sheet's codes tab; one set of initials is FOH only, two is
    FOH then Mon). Leaves a line as-is ('FOH – ' / 'Mon – ', blank) whenever
    the sheet doesn't cleanly resolve a name, so a same-day production call
    by hand is exactly as easy as it always was."""
    venue = event.get("venue")
    date = event.get("event_date")
    if not venue or not date:
        return
    try:
        names = staffing.engineers_for(venue, date.isoformat())
    except Exception as e:  # noqa: BLE001 — a staffing-sheet hiccup shouldn't break the fill
        print(f"[daysheet] engineer lookup failed: {e!r}", file=sys.stderr)
        return
    if not names.get("foh") and not names.get("mon"):
        return
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "engineer":
            for cell in r.cells[1:1 + n]:
                for p in cell.paragraphs:
                    t = p.text.strip()
                    if t.startswith("FOH") and names.get("foh"):
                        set_para_text(p, f"FOH – {names['foh']}")
                    elif t.startswith("Mon") and names.get("mon"):
                        set_para_text(p, f"Mon – {names['mon']}")
            return


def fill_crew_schedule(doc, event):
    """The day-of crew table (top-left, normally Crew Call / Load In-Sound
    Check / Performance / Load-out / Curfew, all blank for a same-day hand
    call) — for a series with a locked '## Crew Schedule' section, its rows
    are REPLACED wholesale with the series' own list, one real table row
    per time change (Brian, 2026-09-09: a multi-set series like Salsa On
    The Square needs its own row per set/break, not several sub-events
    crammed into one cell — hard to read). No-op if the event has no
    venue/series, the series has no Crew Schedule section, or the template
    has no crew table at all."""
    venue = event.get("venue")
    series = event.get("series")
    if not venue or not series:
        return
    rows = ve.crew_schedule_for(venue, series)
    if not rows:
        return
    table = find_schedule_table(doc)
    if not table:
        return
    # Clone the template's own first row for every replacement row, so each
    # keeps its exact cell formatting/borders/shading — then drop every
    # original row and build the new set fresh in order.
    template_tr = copy.deepcopy(table.rows[0]._tr)
    tbl_el = table._tbl
    for r in list(table.rows):
        tbl_el.remove(r._tr)
    for label, time_value in rows:
        tbl_el.append(copy.deepcopy(template_tr))
        new_row = table.rows[-1]
        set_cell(new_row.cells[0], time_value)
        set_cell(new_row.cells[-1], label)


def fill_lead(doc, event):
    det = event.get("details") or {}
    t = find_lead_table(doc)
    if not t:
        return
    if det.get("lead_name"):
        set_cell(t.rows[0].cells[1], det["lead_name"])
    if det.get("lead_phone"):
        set_cell(t.rows[1].cells[1], det["lead_phone"])


def act_columns(grid, n_acts):
    """Row -> its N value cells, keyed by normalized label. Cells inside a
    colSpan report once per spanned grid column in python-docx, so a
    single-value row (Event Type, MISC header, …) still resolves fine —
    callers that expect N distinct act cells use cells[1:1+n_acts]."""
    rows = {}
    for r in grid.rows:
        label = norm(r.cells[0].text)
        if label:
            rows.setdefault(label, r)
    return rows


def fill(event_id, template=None, out_path=None, stageplot_names=None):
    """stageplot_names: {artist name -> filed stage-plot filename}. When an act's
    plot was downloaded and filed next to this doc, its Stage Plot cell reads
    'See DB — <filename>' instead of the inline description."""
    stageplot_names = stageplot_names or {}
    with db.get_conn() as conn, conn.cursor() as cur:
        event = db.get_event(cur, event_id)
        if not event:
            print(f"No event {event_id}", file=sys.stderr); sys.exit(1)
        acts = db.event_acts(cur, event_id)
        declared_n = db.band_count_for_event(cur, event.get("venue"), event.get("event_date"))

    # a declared "bands on the bill" (Brian, 2026-09-08 — set per booking, so
    # it's known even before every act has its own event_acts row yet) wins
    # over the real act count for TEMPLATE SHAPE, so a bill entered one band
    # at a time still gets the right N-band document from the first band on —
    # acts not yet booked just render blank in their column, filled in as
    # each band's booking arrives. Falls back to the real count when nobody
    # declared one.
    n = max(len(acts), declared_n) if declared_n else len(acts)
    if template is None:
        venue = event.get("venue") or "Fountain Square"
        by_venue = TEMPLATES_BY_VENUE.get(venue, {})
        template = by_venue.get(n)
        if template is None:
            available = sorted(by_venue) or "none"
            print(f"Event {event_id} @ {venue} has {n} act(s) — no template for "
                  f"that venue/count combo (have templates for {available} act(s) "
                  f"at {venue}).", file=sys.stderr)
            sys.exit(1)
    if not template.exists():
        print(f"Template not found: {template}", file=sys.stderr)
        sys.exit(1)

    doc = Document(str(template))
    grid = find_grid(doc)
    if grid is None:
        print("Couldn't find the EVENT INFORMATION table.", file=sys.stderr); sys.exit(1)

    single = n == 1
    fill_header(grid, event, acts, single)
    fill_location(grid, event)
    fill_event_type(grid, event, n)
    fill_engineer(grid, event, n)
    fill_crew_schedule(doc, event)
    fill_lead(doc, event)

    # Column for one act: a 3-band bill has an unambiguous 1:1 slot->column
    # mapping (opener=1/direct support=2/headliner=3, per SLOT_ORDER), so use
    # the act's own slot_order directly — critical once a bill can be entered
    # one act at a time (the band_count override above): a lone direct_support
    # act has no opener/headliner rows yet, and a plain enumerate() position
    # would put it in column 1 regardless (real bug, caught on Sylmar's actual
    # direct-support booking landing under Opener on the filled sheet). A
    # 2-band bill is deliberately more flexible — it's ANY 2 of the 3 slots
    # (opener+headliner or direct_support+headliner both valid), so there's no
    # fixed slot->column table for it; keep the original relative-rank-among-
    # the-acts-present behavior there (and trivially for a single-band bill).
    def _col(a, i):
        return a["slot_order"] if n >= 3 else 1 + i

    # multi-band act-name header row: bold slot label already printed by the
    # template, second paragraph is the blank line for the actual band name
    if not single:
        for r in grid.rows:
            if r.cells and r.cells[0].text.strip() == "" and any(
                    c.paragraphs and c.paragraphs[0].runs and c.paragraphs[0].runs[0].bold
                    for c in r.cells[1:1 + n]):
                for i, a in enumerate(acts):
                    if not a.get("artist"):
                        continue
                    ci = _col(a, i)
                    if ci < len(r.cells) and len(r.cells[ci].paragraphs) >= 2:
                        set_para_text(r.cells[ci].paragraphs[1], a["artist"]["name"])
                break

    rows_by_label = act_columns(grid, n)
    filled_acts = 0
    for i, a in enumerate(acts):
        mf = merged_fields(a)
        if a.get("set_time"):
            mf_set_length = a["set_time"]
        else:
            mf_set_length = None
        who = a["artist"]["name"] if a.get("artist") else None
        saved_plot = stageplot_names.get(who) if who else None
        if saved_plot:
            mf["_stageplot_saved"] = saved_plot
        values = act_row_values(mf)
        if mf_set_length:
            values["set length"] = mf_set_length
        if values:
            filled_acts += 1
        for label, text in values.items():
            row = rows_by_label.get(label)
            if not row:
                continue
            ci = _col(a, i)
            if ci >= len(row.cells):
                continue
            if label == "stage plot" and saved_plot:
                set_cell_link(row.cells[ci], text, quote(saved_plot))
            elif isinstance(text, Checkbox):
                cell = row.cells[ci]
                for extra in cell.paragraphs[1:]:
                    extra._element.getparent().remove(extra._element)
                set_checkbox_paragraph(cell.paragraphs[0], text.labels, text.chosen)
            else:
                set_cell(row.cells[ci], text)

    if out_path is None:
        tag = re.sub(r"[^A-Za-z0-9]+", "_", event.get("name") or f"event{event_id}").strip("_")
        date = event.get("event_date")
        out_path = FILLED / f"{tag}__{date or 'nodate'}__daysheet.docx"
    doc.save(out_path)
    print(f"Filled day-sheet ({n}-band template): {out_path}")
    print(f"  {event.get('name')} @ {event.get('venue')} {event.get('event_date')} "
          f"— {filled_acts}/{len(acts)} act(s) filled")
    for a in acts:
        who = a["artist"]["name"] if a.get("artist") else "(none)"
        src = []
        if a.get("submission"):
            src.append("form")
        if a.get("sheet_fields"):
            src.append("sheet")
        tag = ("+".join(src)) if src else "no data"
        print(f"    {a['slot']:16} {who}  [{tag}]  {a.get('set_time') or ''}")
    return out_path


# ── reading a PAST advance back out (for the returning-artist recap email) ──
#
# events/event_acts get TRUNCATEd and rebuilt from the live sheet on every
# package_run.py pass (see its own docstring) — they're a working model, not a
# history. The filed .docx in the venue tree is the only thing that durably
# remembers what was actually on a past show's advance, staff overrides
# included, so this reads the real file back rather than reconstructing from
# the DB. Brian's explicit call (2026-09-07) over the DB-reconstruction option.

NYQUIST_DEFAULT = Path.home() / "Dropbox" / "Nyquist"  # same default run_now.py uses

# event-level rows (not band-specific) plus the staff-only production rows
# daysheet.py's own module docstring lists as "left BLANK, always — ... a
# same-day production call Brian makes by hand": never band-submitted, so a
# filled-in one is Brian's internal note, not something to echo back to the
# band, and a blank one is just template boilerplate ("No scenic elements",
# "N/A") rather than real on-file data either way.
RECAP_EXCLUDE_ROWS = {
    "event information", "event type", "location", "set length",
    "engineer", "consoles", "pa", "subs", "lighting", "video", "buyout",
}


def _candidate_docs(venue, event_date, root=None):
    """Filed advance(s) for this venue+date, per package_run.py's own filing
    scheme (<VenueAbbr>/<Year>/<MM Month>/<MMDDYY> <Event Name> advance.docx) —
    globbed by date stamp since a past event's real name isn't reliably in the
    DB any more (events/event_acts is a working model, not an archive)."""
    root = Path(root) if root else NYQUIST_DEFAULT
    folder = root / fs.venue_abbr(venue) / str(event_date.year) / fs.month_folder(event_date)
    if not folder.exists():
        return []
    stamp = event_date.strftime("%m%d%y")
    return sorted(folder.glob(f"{stamp} * advance.docx"))


def _act_count_and_column(grid, target_norm, require_name_match):
    """(n_acts, ci) — n_acts is how many act columns this document actually
    has (so a blank pristine copy of the SAME template variant can be diffed
    against it), ci is target_norm's column (1-based, matching act_columns'
    cells[ci]), or None if it can't be resolved. Single-band templates put the
    name on one "Band:" line inside EVENT INFORMATION — no ambiguity once
    there's only one candidate file, so require_name_match lets a confirmed
    single-band file resolve even when the Band: line is blank/stale, but
    forces a real name match when there's more than one candidate for the
    same venue+date. Multi-band templates put each act's name in its header
    row, one name per column (mirrors fill()'s own header-row detection)."""
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event information":
            band_lines = [p.text.strip() for p in r.cells[1].paragraphs
                          if p.text.strip().lower().startswith("band:")]
            if band_lines:
                confirmed = any(target_norm and target_norm in norm(t) for t in band_lines)
                return 1, (1 if (confirmed or not require_name_match) else None)
            break
    for r in grid.rows:
        if r.cells and r.cells[0].text.strip() == "" and any(
                c.paragraphs and c.paragraphs[0].runs and c.paragraphs[0].runs[0].bold
                for c in r.cells[1:]):
            n_acts = len(r.cells) - 1
            for i, c in enumerate(r.cells[1:], start=1):
                if len(c.paragraphs) >= 2 and norm(c.paragraphs[1].text) == target_norm:
                    return n_acts, i  # confirmed
            return n_acts, None
    return 1, None


def _template_defaults(venue, n_acts, ci):
    """label(norm) -> the PRISTINE template's own default text in that act
    column. A filled doc's row that still matches this is unfilled boilerplate
    ("N/A", "No scenic elements", a blank "FOH – \\nMon –") rather than real
    on-file data, regardless of which specific placeholder text the template
    happens to use for that row — cheaper and more general than hardcoding
    every known placeholder string."""
    template = TEMPLATES_BY_VENUE.get(venue, {}).get(n_acts)
    if not template or not template.exists():
        return {}
    try:
        doc = Document(str(template))
    except Exception:
        return {}
    grid = find_grid(doc)
    if grid is None:
        return {}
    return {norm(r.cells[0].text): full_cell_text(r.cells[ci]).strip()
            for r in grid.rows if r.cells and ci < len(r.cells)}


def read_filed_advance(venue, event_date, artist_name, root=None):
    """(path, [(row label, cell text), ...]) for `artist_name`'s column on their
    most recently filed advance at venue/event_date — or None if no filed doc
    can be found or matched. Row labels keep the document's own text (title
    case, "Band Contact — Name", etc.) rather than the internal norm() form.
    Drops rows still matching the blank template's own default text — a row
    daysheet.fill() never wrote to reads back as boilerplate, not real data."""
    candidates = _candidate_docs(venue, event_date, root)
    if not candidates:
        return None
    target = norm(artist_name)
    ambiguous = len(candidates) > 1
    for path in candidates:
        try:
            doc = Document(str(path))
        except Exception:
            continue
        grid = find_grid(doc)
        if grid is None:
            continue
        n_acts, ci = _act_count_and_column(grid, target, require_name_match=ambiguous)
        if ci is None:
            continue
        defaults = _template_defaults(venue, n_acts, ci)
        rows = []
        for r in grid.rows:
            label_norm = norm(r.cells[0].text)
            if not label_norm or label_norm in RECAP_EXCLUDE_ROWS or ci >= len(r.cells):
                continue
            text = full_cell_text(r.cells[ci]).strip()
            if not text or text == defaults.get(label_norm, "").strip():
                continue
            rows.append((r.cells[0].text.strip().rstrip(":").strip(), text))
        if rows:
            return path, rows
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", type=int, required=True)
    ap.add_argument("--template", type=Path, default=None,
                     help="override the auto-picked (by act count) template")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    fill(args.event, args.template, args.out)


if __name__ == "__main__":
    main()
