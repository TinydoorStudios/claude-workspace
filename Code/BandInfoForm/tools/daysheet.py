#!/usr/bin/env python3
"""Fill an advance day-sheet from an event — every venue, every band count
(1/2/3), ONE template: doc_templates/3CDC Universal Show Advance.docx
(Brian, 2026-09-11: "make sure all of the advancing workflow uses the new
three band generic doc"). The five retired venue-specific templates (FSQ
Single/2/3-Band, WP Single/2-Band) are no longer used to fill anything —
they're left on disk only as historical reference and so recap-extraction
can still diff an old already-filed doc against the right pristine shape
while it ages out of the catch-up window.

The document always has all 3 act columns (ARTIST 1 / ARTIST 2 / ARTIST 3),
regardless of how many artists are really on the bill — unused columns just
render blank. Column assignment is now as simple as it sounds: the act's
artist_order IS its column, and artist_order comes from set start — earliest
plays first (Brian, 2026-09-15). A single artist is ARTIST 1 in column 1.

That replaced a slot -> column rule where a 1-artist bill printed under
HEADLINER in column 3 and a 2-artist bill used columns 2 and 3. There are no
slots now: an artist booked later with an earlier set time simply becomes
Artist 1 and everyone else shifts right, with nothing copied or moved.

Source of truth is the advance SPREADSHEET (event + any band overrides); the
advance FORM fills whatever the sheet left blank — the spreadsheet value
wins, same merge policy as the email drafts. Writes:
  - EVENT INFORMATION: Date / Event / Venue / Location / TONIGHT — MC/DJ
  - Location: Fountain Square is always "Main Stage" (its only location);
    Washington Park (and anywhere else) uses whatever's on file for the
    booking (bookings.location) — free text, not a fixed checkbox set,
    since it has to generalize past WP's own three named spots
  - Event Type / Paying?, Lead name + cell
  - per-act: Set Length, act name (header row), Stage Plot, Monitors, IEMs,
    Number of IEMs, Input Notes (also carries own-IEM-system / split-snake
    text — there's no dedicated cell for those), Stage Type, Scenic Notes,
    Lighting Notes, Merch, Parking, Number of Performers, Dressing Room
    Tent, Backline, Band Contact — Name/Cell
  - Engineer (FOH – / Mon –), same value repeated into every act column —
    pulled from the public 3CDC staffing sheet via staffing.engineers_for()
    (Brian, 2026-09-08); a line left as its unfilled placeholder ('FOH – ')
    means the sheet didn't resolve a clean name for that show, not that the
    row was skipped. An act whose own_engineer answer starts with "Yes"
    gets "TOUR" in its own column instead (Brian, 2026-09-15) — see
    _tour_engineer_cols
  - the crew SCHEDULE table (Crew Call / Load In-Sound Check / Performance /
    Load-out / Curfew) — ONLY for a series with a locked '## Crew Schedule'
    section (venue_email.crew_schedule_for(); Brian, 2026-09-09: Salsa On
    The Square's times never change, so there's no reason to leave this for
    a same-day hand call the way every other show's crew schedule needs)

Left BLANK, always — no data source, or a same-day production call Brian
makes by hand (2026-09-03: "the granular items we will add by hand";
2026-09-11: PA/Consoles joined this list once one template had to work for
every venue — no honest single default for either one generalizes):
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

# Every venue, every band count — ONE template (Brian, 2026-09-11).
UNIVERSAL_TEMPLATE = TEMPLATES / "3CDC Universal Show Advance.docx"

# Retired — fill() never picks from these again, and _template_defaults()
# doesn't either (an already-filed doc could be genuinely old-shaped OR a
# new 3-column universal doc that happens to match one of these by act
# count; there's no reliable way to tell which from the file alone, and
# guessing wrong is worse than just always diffing against the current
# template). Left on disk purely as historical/manual reference — not
# deleted, just no longer read by anything here.
#   FSQ Single/2/3 Band Advance.docx, WP Single/2 Band Advance.docx


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
        "iem_count": d.get("iem_count"),
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
        # audit #7: the count questions that replaced large_vehicle never
        # reached the doc — Parking was blank on every new submission.
        "vehicle_count": (str(sub["vehicle_count"]) if sub.get("vehicle_count") is not None
                          else d.get("vehicle_count")),
        "large_vehicle_count": (str(sub["large_vehicle_count"]) if sub.get("large_vehicle_count") is not None
                                else d.get("large_vehicle_count")),
        "stage_plot_file": d.get("stage_plot_file"),
        "stage_escort_name": d.get("stage_escort_name"),
        "stage_escort_cell": d.get("stage_escort_cell"),
        # "Anything else we should know?" (Brian, 2026-09-14) -> the doc's
        # Additional Info row, last in the grid
        "additional": d.get("additional"),
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

    if str(uses_iems or "").lower() == "yes" and f.get("iem_count") not in (None, ""):
        out["number of iems"] = str(f["iem_count"])

    notes = []
    if f.get("input_notes"):
        notes.append(f["input_notes"])
    if str(uses_iems or "").lower() == "yes" and f.get("own_iems"):
        notes.append(f"Own IEM system: {f['own_iems']}")
    if str(f.get("own_iems", "")).lower() == "yes" and f.get("split_snake"):
        notes.append(f"Split snake: {f['split_snake']}")
    if notes:
        out["input notes"] = " · ".join(notes)

    if f.get("lighting"):
        out["lighting notes"] = f["lighting"]

    if f.get("stage_type"):
        out["stage type"] = Checkbox(
            ["Flat", "Riser"], "Riser" if "riser" in str(f["stage_type"]).lower() else "Flat")
    if f.get("scenic"):
        out["scenic notes"] = f["scenic"]

    if f.get("merch"):
        out["merch"] = f["merch"]
    def _int(v):
        try:
            return int(str(v).strip())
        except (TypeError, ValueError):
            return None

    vc, lvc, lv = _int(f.get("vehicle_count")), _int(f.get("large_vehicle_count")), f.get("large_vehicle")
    # Parking (audit #7): "3 vehicles: 1 large, 2 standard". Counts win; the
    # old Yes/No large_vehicle is only the fallback for older submissions.
    # A non-numeric value never crashes the fill — it's just skipped.
    if vc is not None:
        noun = "vehicle" if vc == 1 else "vehicles"
        if lvc is not None and 0 < lvc <= vc:
            out["parking"] = f"{vc} {noun}: {lvc} large, {vc - lvc} standard"
        elif lvc == 0:
            out["parking"] = f"{vc} {noun}: all standard"
        else:
            out["parking"] = f"{vc} {noun}"
    elif lvc is not None:
        out["parking"] = f"{lvc} large vehicle{'s' if lvc != 1 else ''}"
    elif lv:
        out["parking"] = "Large vehicle" if str(lv).lower() == "yes" else "Standard"
    if f.get("performers") not in (None, ""):
        out["number of performers"] = str(f["performers"])
        # Drink Tix = 2x band/crew headcount (Brian, 2026-09-13) — computed,
        # never band- or staff-entered; skip silently if performers isn't a
        # clean number rather than write garbage into the cell.
        try:
            out["drink tix"] = str(int(f["performers"]) * 2)
        except (TypeError, ValueError):
            pass
    if f.get("band_tent"):
        out["dressing room tent"] = "Yes" if str(f["band_tent"]).lower().startswith("yes") else "No"
    if f.get("backline"):
        out["backline"] = f["backline"]
    # Salsa stage-escort rep (audit #15) goes under the main contact.
    esc_name, esc_cell = (f.get("stage_escort_name") or "").strip(), (f.get("stage_escort_cell") or "").strip()
    name, cell = (f.get("contact_name") or "").strip(), (f.get("contact_phone") or "").strip()
    if esc_name and name and norm(esc_name) == norm(name):
        name = f"{name} (stage escort)"
    elif esc_name:
        name = f"{name}\nStage escort: {esc_name}" if name else f"Stage escort: {esc_name}"
    if esc_cell and cell and esc_cell != cell:
        cell = f"{cell}\nEscort: {esc_cell}"
    elif esc_cell and not cell:
        cell = f"Escort: {esc_cell}"
    if name:
        out["band contact — name"] = name
    if cell:
        out["band contact — cell"] = cell
    if f.get("additional"):
        out["additional info"] = f["additional"]
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
    # a "\n" in text becomes a Word line break inside the one paragraph
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


def _location_for(event):
    """Where within the venue this show is happening (Brian, 2026-09-11):
    Fountain Square is always "Main Stage" — there's no other location
    there. Washington Park (and anywhere else) uses whatever's on file for
    the booking (events.details.location, seeded from bookings.location) —
    free text, not a fixed checkbox set, since a single cross-venue field
    can't assume WP's three named spots apply everywhere."""
    if event.get("venue") == "Fountain Square":
        return "Main Stage"
    det = event.get("details") or {}
    return det.get("location") or ""


def fill_header(grid, event):
    """EVENT INFORMATION value cell: Date / Event / Venue / Location /
    TONIGHT — MC/DJ — each its own paragraph. This is ONE cell shared
    across all 3 act columns (confirmed via the raw XML: 2 real <w:tc>
    elements in this row, not 4 — python-docx's own .cells accessor just
    reports the shared one three times), so it's written once, not per
    column."""
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event information":
            value_cell = r.cells[1]
            date = event.get("event_date").isoformat() if event.get("event_date") else ""
            venue = event.get("venue") or ""
            location = _location_for(event)
            for p in value_cell.paragraphs:
                t = p.text.strip()
                if t.startswith("Date:"):
                    set_para_text(p, f"Date: {date}" if date else "Date:")
                elif t.startswith("Event:"):
                    set_para_text(p, f"Event: {event.get('name') or ''}")
                elif t.startswith("Venue:"):
                    set_para_text(p, f"Venue: {venue}" if venue else "Venue:")
                elif t.startswith("Location:"):
                    set_para_text(p, f"Location: {location}" if location else "Location:")
                elif t.startswith("TONIGHT"):
                    det = event.get("details") or {}
                    if det.get("mc"):
                        append_to_run(p, "TONIGHT — MC: ", det["mc"])
                    if det.get("dj"):
                        append_to_run(p, "     DJ: ", det["dj"])
            return


def _active_cols(n):
    """Which of the universal template's 3 value columns are in play for an
    n-artist bill: the first n, left to right (Brian, 2026-09-15). Event-level
    rows that repeat across every act column (Event Type, Engineer) use this so
    they don't print into a column no artist occupies.

    Until 2026-09-15 this was NOT a contiguous slice — a 1-artist bill lived in
    column 3 and a 2-artist bill in columns 2 and 3, because the columns were
    Opener/Direct Support/Headliner and a lone act was the headliner."""
    return list(range(1, min(max(n, 1), 3) + 1))


def _act_col(a, n):
    """Which of the 3 act columns this act's data goes into: its artist_order,
    which advance_db.order_acts derived from set start. Capped at 3 — a fourth
    artist on a bill has nowhere to print, and the template is the constraint,
    not the model. Shared with fill_engineer's per-column TOUR check so the two
    never drift apart."""
    return min(a.get("artist_order") or 1, 3)


def _tour_engineer_cols(acts, n):
    """Column indices whose act brings its own engineer — own_engineer
    starts with "Yes" (fieldspec.py's "Yes — bringing our own (we'll
    coordinate)") — so that column reads "TOUR" instead of the house
    staffing-sheet name (Brian, 2026-09-15, RatBoys/FSQ 9/18: the band said
    so on the form, Brian confirmed it with a staff edit, and neither ever
    reached this row — own_engineer had nowhere to go before this)."""
    cols = set()
    for a in acts or []:
        if a.get("_cancelled"):
            continue
        oe = (merged_fields(a).get("own_engineer") or "").strip().lower()
        if oe.startswith("yes"):
            cols.add(_act_col(a, n))
    return cols


def fill_event_type(grid, event, n=1):
    """Event Type / Paying Band — an event-level fact, but the 2/3-band
    templates repeat this row once per act column (same shape as Engineer/
    Consoles), so it's written into every column actually in play for this
    band count, not just the first n (fixed 2026-09-08 — cells 2/3 used to
    stay pristine-blank forever on a multi-band bill; fixed again 2026-09-11
    when a 1-band bill's act moved to column 3, not column 1)."""
    det = dict(event.get("details") or {})
    # audit #16: the booking's Series pick decides it — "3rd Party" is a
    # Third Party Event, every named series (and "Stand-Alone Internal") is
    # Internal. Only a show with no series at all falls back to a typed type.
    series = (event.get("series") or "").strip()
    if series:
        det["event_type"] = "Third Party" if series.lower() == "3rd party" else "Internal"
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event type":
            for ci in _active_cols(n):
                if ci >= len(r.cells):
                    continue
                value_cell = r.cells[ci]
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


def fill_engineer(grid, event, n, acts=None):
    """Engineer row (FOH – / Mon –), same house value repeated into every
    act column — it's one FOH engineer and one Mon engineer for the whole
    SHOW, not per band, same as how the Consoles row already repeats its
    (static) value across columns. Pulled from the public 3CDC staffing
    sheet (Brian, 2026-09-08: cross-reference the Mix column's initials
    against the staffing sheet's codes tab; one set of initials is FOH
    only, two is FOH then Mon).

    Exception (Brian, 2026-09-15): an act bringing its own engineer gets
    "TOUR" in ITS column instead of the house name — see
    _tour_engineer_cols. Leaves a line as-is ('FOH – ' / 'Mon – ', blank)
    for any other column whenever the sheet doesn't cleanly resolve a
    name, so a same-day production call by hand is exactly as easy as it
    always was."""
    venue = event.get("venue")
    date = event.get("event_date")
    tour_cols = _tour_engineer_cols(acts, n)
    names = {}
    if venue and date:
        try:
            det = event.get("details") or {}
            names = staffing.engineers_for(
                venue, date.isoformat(),
                series=event.get("series"), event_name=event.get("name"),
                artist_name=next((a["artist"]["name"] for a in (acts or [])
                                  if a.get("artist") and not a.get("_cancelled")),
                                 None),
                event_start=det.get("event_start"))
        except Exception as e:  # noqa: BLE001 — a staffing-sheet hiccup shouldn't break the fill
            print(f"[daysheet] engineer lookup failed: {e!r}", file=sys.stderr)
            names = {}
    if not tour_cols and not names.get("foh") and not names.get("mon"):
        return
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "engineer":
            for ci in _active_cols(n):
                if ci >= len(r.cells):
                    continue
                cell = r.cells[ci]
                tour = ci in tour_cols
                for p in cell.paragraphs:
                    t = p.text.strip()
                    if t.startswith("FOH") and (tour or names.get("foh")):
                        set_para_text(p, "FOH – TOUR" if tour else f"FOH – {names['foh']}")
                    elif t.startswith("Mon") and (tour or names.get("mon")):
                        set_para_text(p, "Mon – TOUR" if tour else f"Mon – {names['mon']}")
            return


def _shift_house_time(s, minutes):
    """Shift a house-format time string ('6:00p') by minutes; '' if unparseable."""
    import datetime as _dt
    s = (s or "").strip().lower().replace(" ", "")
    if not s:
        return ""
    ap = None
    if s and s[-1] in ("a", "p"):
        ap, s = s[-1], s[:-1]
    t = None
    for fmt in ("%I:%M", "%I", "%H:%M"):
        try:
            t = _dt.datetime.strptime(s, fmt)
            break
        except ValueError:
            continue
    if t is None:
        return ""
    h = t.hour
    if ap == "p" and h < 12:
        h += 12
    elif ap == "a" and h == 12:
        h = 0
    base = t.replace(hour=h)
    out = (base + _dt.timedelta(minutes=minutes)).strftime("%I:%M%p").lstrip("0").lower()
    return out[:-1]  # '4:00pm' -> '4:00p'


def _artist_schedule_times(acts, event):
    """{artist_order: {load-in/sound check/set starts/set ends: time}} — each
    artist's OWN schedule, off its own booking.

    Before 2026-09-15 there was no such thing: load_in / soundcheck /
    event_start / event_end were collapsed onto the EVENT as "first non-empty
    value across the bill's rows", so on any multi-artist bill one artist's
    times printed against another's rows. FSQ 9/18/26 is the case that showed
    it — the doc read Headliner Load-In 7:00pm and Headliner End 8:45pm for a
    band that played 9:00–10:00, because those were the second act's times.

    A single-artist bill still falls back to the event details, so events
    written before the per-act columns existed keep filling in."""
    out = {}
    det = event.get("details") or {}
    real = [a for a in (acts or []) if not a.get("_cancelled")]
    for a in real:
        col = min(a.get("artist_order") or 1, 3)
        fallback = det if len(real) == 1 else {}
        out[col] = {
            "load-in": a.get("load_in") or fallback.get("load_in"),
            "sound check": a.get("soundcheck") or fallback.get("soundcheck"),
            "line check": a.get("soundcheck") or fallback.get("soundcheck"),
            "set starts": a.get("set_start") or fallback.get("event_start"),
            "set ends": a.get("set_end") or fallback.get("event_end"),
        }
    return out


# Schedule-row labels in the template read "Artist 3 Load-In", and a changeover
# row combines two: "Artist 1 Set Starts/ Artist 2 Load-In". One cell, one time
# — the FIRST fragment wins, which is the one the row is named for.
_SCHED_KEYWORDS = [
    ("set starts", ("set starts", "starts")),
    ("set ends", ("set end", "end")),
    ("sound check", ("sound check",)),
    ("line check", ("line check",)),
    ("load-in", ("load-in", "load in")),
]


def _schedule_row_value(label, per_artist):
    """The time for one schedule row, or None. Reads 'Artist N <what>' out of
    the row's own label so the mapping can't drift from the template's wording
    the way a hard-coded row list would."""
    for fragment in str(label or "").split("/"):
        frag = norm(fragment)
        m = re.search(r"artist\s*(\d)", frag)
        if not m:
            continue
        times = per_artist.get(int(m.group(1)))
        if not times:
            continue
        for key, needles in _SCHED_KEYWORDS:
            if any(nd in frag for nd in needles) and times.get(key):
                return times[key]
    return None


def _third_line(cell):
    """The act header cell's third paragraph — the set-time line under the
    artist's name. Cloned from the name line the first time so it matches that
    cell's font, then reused on every later fill (a doc regenerated twice must
    not grow a fourth and fifth line)."""
    if len(cell.paragraphs) >= 3:
        return cell.paragraphs[2]
    name_p = cell.paragraphs[1]
    new_p = copy.deepcopy(name_p._p)
    name_p._p.addnext(new_p)
    para = cell.paragraphs[2]
    for r in list(para.runs)[1:]:
        r._element.getparent().remove(r._element)
    if para.runs:
        para.runs[0].text = ""
    return para


def set_time_range(act):
    """'9:00pm–10:00pm' for the act's own set — the third line under the
    artist's name in its AUDIO column (Brian, 2026-09-15). Just the start if
    there's no end on file, blank if there's no time at all."""
    start = (act.get("set_start") or "").strip()
    end = (act.get("set_end") or "").strip()
    if start and end:
        return f"{start}–{end}"
    return start or ""


# "Artist 1", "Artist 2", "Artist 3" anywhere in a schedule row's label —
# including a changeover row that names two of them.
_ARTIST_TOKEN = re.compile(r"artist\s*([123])\b", re.I)


def name_schedule_labels(table, acts):
    """Put the real artist names into the schedule rows: '4:30pm Artist 3
    Load-In' becomes '4:30pm RatBoys Load-In' (Brian, 2026-09-15).

    Driven by the SAME artist_order that decides the AUDIO columns, so a name in
    the schedule can't drift from the name at the top of its column — they are
    two renderings of one list.

    A position nobody occupies (a 2-artist bill has no Artist 3) has its half of
    the label dropped rather than printed: the row goes blank instead of reading
    "Artist 3 Load-In" with no time beside it, and a changeover row naming one
    real artist and one empty position keeps the real half ("Ricky Nye Set
    Starts", not "... / Artist 2 Load-In"). The row itself stays — blank, like
    any other unfilled row — because the table's shape is what docmerge lines an
    already-filed doc up against.

    A cancelled act keeps its name here; its column header is what says
    CANCELLED, and its rows have no times.

    Runs LAST, after the times are in, and over whatever rows the table ended
    up with — so it covers a locked series schedule (which replaces every row
    wholesale from the series file) exactly the same as the template's own."""
    names = {}
    for a in acts or []:
        if a.get("artist") and a.get("artist_order"):
            names[min(a["artist_order"], 3)] = a["artist"]["name"]
    if not names:
        return
    for row in table.rows:
        if not row.cells:
            continue
        cell = row.cells[-1]
        label = cell.text.strip()
        if not label:
            continue
        tokens = [int(t) for t in _ARTIST_TOKEN.findall(label)]
        if tokens and all(t in names for t in tokens):
            # every position in this label is played — substitute in place so
            # the row's own punctuation and spacing survive untouched
            new = _ARTIST_TOKEN.sub(lambda m: names[int(m.group(1))], label)
        elif tokens:
            # part (or all) of this row belongs to a position nobody plays. A
            # row with a time keeps its real half; a row with no time at all
            # goes blank rather than leaving an orphaned "Changeover" behind.
            if not row.cells[0].text.strip():
                new = ""
            else:
                kept = [
                    _ARTIST_TOKEN.sub(lambda m: names[int(m.group(1))], f).strip()
                    for f in label.split("/")
                    if not (_ARTIST_TOKEN.findall(f)
                            and not any(int(t) in names for t in _ARTIST_TOKEN.findall(f)))
                ]
                new = " / ".join(k for k in kept if k)
        else:
            continue              # Crew Call, Load Out, Curfew — nobody's row
        if new != label:
            set_cell(cell, new)


def fill_crew_schedule(doc, event, acts=None):
    """The day-of crew table (Crew Call / per-artist Load-In & Sound Check /
    Starts / Set Ends / Load Out / Curfew).

    Two ways it gets filled:
      1. A series with a locked '## Crew Schedule' section (e.g. Salsa On The
         Square) REPLACES the rows wholesale with the series' own list, one
         row per time change (Brian, 2026-09-09).
      2. Otherwise, fill the template's OWN rows — every artist's rows, each
         from that artist's own booking (Brian, 2026-09-15). Crew Call and
         Curfew stay event-level: they belong to the night, not to an act.

    The rows are NOT in artist order and aren't meant to be: the top of the
    bill loads in and sound checks first, so the block runs Artist 3 Load-In,
    Artist 3 Sound Check, Artist 1 Load-In, and so on down to Artist 3's set.
    That's the real order of the day; the numbering just isn't sequential
    inside it (Brian's call, 2026-09-15).
    No-op only if the template has no crew table at all."""
    table = find_schedule_table(doc)
    if not table:
        return
    venue = event.get("venue")
    series = event.get("series")
    locked = ve.crew_schedule_for(venue, series) if (venue and series) else []
    if locked:
        # Clone the template's own first row for every replacement row, so each
        # keeps its exact cell formatting/borders/shading — then drop every
        # original row and build the new set fresh in order.
        template_tr = copy.deepcopy(table.rows[0]._tr)
        tbl_el = table._tbl
        for r in list(table.rows):
            tbl_el.remove(r._tr)
        for label, time_value in locked:
            tbl_el.append(copy.deepcopy(template_tr))
            new_row = table.rows[-1]
            set_cell(new_row.cells[0], time_value)
            set_cell(new_row.cells[-1], label)
        name_schedule_labels(table, acts)
        return
    # No locked schedule: fill the template's own labelled rows from the event's
    # derived times. Crew Call and Curfew come from the staffing sheet's Event
    # cell when present (Brian, 2026-09-11, all sites — 'Jazz (3:30-10)'); they
    # fall back to computed (crew = start - 2:00) / booking curfew otherwise.
    det = event.get("details") or {}
    per_artist = _artist_schedule_times(acts, event)
    # Crew call is anchored on the FIRST load-in of the day — whoever that is —
    # falling back to the earliest set start, then the event's own start.
    load_ins = [t.get("load-in") for t in per_artist.values() if t.get("load-in")]
    starts = [t.get("set starts") for t in per_artist.values() if t.get("set starts")]
    anchor = (min(load_ins, key=lambda v: (db.parse_clock(v) is None, db.parse_clock(v) or 0))
              if load_ins else None)
    start = (min(starts, key=lambda v: (db.parse_clock(v) is None, db.parse_clock(v) or 0))
             if starts else det.get("event_start"))
    staff_times = {}
    try:
        import staffing
        staff_times = staffing.event_times_for(
            venue, event.get("event_date"), series=event.get("series")) or {}
    except Exception:
        staff_times = {}
    crew_call = (staff_times.get("crew_call")
                 or (_shift_house_time(anchor, -60) if anchor else "")
                 or (_shift_house_time(start, -120) if start else ""))
    curfew = staff_times.get("curfew") or det.get("curfew")
    event_level = {"crew call": crew_call, "curfew": curfew}
    for r in table.rows:
        label = r.cells[-1].text
        val = event_level.get(norm(label)) or _schedule_row_value(label, per_artist)
        if val:
            set_cell(r.cells[0], val)
    name_schedule_labels(table, acts)


def _consoles_text(event):
    """Console line for the Consoles row (Brian, 2026-09-11):
      - Fountain Square: FOH is DiGiCo; the M32 monitor desk is listed by
        DEFAULT only for 513 Airwaves and Salsa — every other FSQ show adds
        monitors by hand when needed, so it isn't printed.
      - Washington Park Main Stage: FOH is M32 (monitors added when needed).
      - Washington Park Porch / Bandstand: one M32R.
      - Anywhere else: left blank for now."""
    venue = event.get("venue")
    det = event.get("details") or {}
    loc = (det.get("location") or "").strip()
    # Match the SERIES only (not a band name) so a band literally called
    # "Salsa ___" doesn't trip the monitor default (Brian, 2026-09-11).
    series = (event.get("series") or "").lower()
    if venue == "Fountain Square":
        default_mon = ("513 airwaves" in series) or ("salsa" in series)
        return "FOH: DiGiCo Quantum 225" + (" · Mon: M32" if default_mon else "")
    if venue == "Washington Park":
        if loc in ("Porch", "Bandstand"):
            return "M32R"
        return "FOH: M32"
    return ""


def fill_consoles(grid, event):
    """Write the Consoles row from _consoles_text() into EVERY act column
    (Artist 1 / Artist 2 / Artist 3), so the console shows under each artist
    on the bill (Brian, 2026-09-12). No-op if blank (a venue with no rule) or
    the row isn't in this template."""
    text = _consoles_text(event)
    if not text:
        return
    for r in grid.rows:
        if norm(r.cells[0].text) == "consoles" and len(r.cells) > 1:
            for c in r.cells[1:]:
                set_cell(c, text)
            break


def fill_lead(doc, event):
    det = event.get("details") or {}
    t = find_lead_table(doc)
    if not t:
        return
    if det.get("lead_name"):
        set_cell(t.rows[0].cells[1], det["lead_name"])
    if det.get("lead_phone"):
        set_cell(t.rows[1].cells[1], det["lead_phone"])


def _series_without_riser(series):
    try:
        sys.path.insert(0, str(HERE.parent))
        import forms_config
        return bool(series) and forms_config.SERIES.get(series, {}).get("drum_riser") is False
    except Exception:
        return False


def act_columns(grid, n_acts):
    """Row -> its N value cells, keyed by normalized label. Cells inside a
    colSpan report once per spanned grid column in python-docx, so a
    single-value row (Event Type, MISC header, …) still resolves fine —
    callers that need a specific act's column use _col()/_active_cols(),
    not a contiguous cells[1:1+n] slice (retired 2026-09-11 — a 1- or
    2-band bill's acts don't sit in the first n columns any more)."""
    rows = {}
    for r in grid.rows:
        label = norm(r.cells[0].text)
        if label:
            rows.setdefault(label, r)
    return rows


def fill(event_id, template=None, out_path=None, stageplot_names=None):
    """Build and SAVE a fresh day-sheet to out_path (CLI / tools/filled only).
    The live filing path never calls this — it goes through
    docmerge.file_event_doc, which never overwrites a filed doc."""
    doc, event, acts, n = build(event_id, template=template, stageplot_names=stageplot_names)
    if out_path is None:
        tag = re.sub(r"[^A-Za-z0-9]+", "_", event.get("name") or f"event{event_id}").strip("_")
        date = event.get("event_date")
        out_path = FILLED / f"{tag}__{date or 'nodate'}__daysheet.docx"
    doc.save(out_path)
    print(f"Filled day-sheet ({n}-band template): {out_path}")
    return out_path


def build(event_id, template=None, stageplot_names=None):
    """(Document, event, acts, n) — the day-sheet as the pipeline would write it
    fresh from the template, in memory, never saved here.
    stageplot_names: {artist name -> filed stage-plot filename}. When an act's
    plot was downloaded and filed next to this doc, its Stage Plot cell reads
    'See DB — <filename>' instead of the inline description."""
    stageplot_names = stageplot_names or {}
    with db.get_conn() as conn, conn.cursor() as cur:
        event = db.get_event(cur, event_id)
        if not event:
            print(f"No event {event_id}", file=sys.stderr); sys.exit(1)
        acts = db.event_acts(cur, event_id)
        booked_n = db.artist_count_for_event(cur, event.get("venue"), event.get("event_date"),
                                             series=event.get("series"))
        # a cancelled band's info never goes into the doc (audit #4); its
        # column header reads "CANCELLED — <band>" so the doc says so
        # (review 2026-09-14, M4) — the act stays in `acts` for column
        # layout, its cells are left blank/template.
        cur.execute("SELECT artist_id FROM shows WHERE venue=%s AND show_date=%s AND cancelled_at IS NOT NULL",
                    (event.get("venue"), event.get("event_date")))
        cancelled = {r["artist_id"] for r in cur.fetchall()}
        for a in acts:
            a["_cancelled"] = a.get("artist_id") in cancelled

    # How many artists this bill really has. The bookings table knows about an
    # artist as soon as staff logs the booking — before the act has its own
    # event_acts row — so the larger of the two wins and a bill entered one
    # artist at a time still reserves the right number of columns. Until
    # 2026-09-15 this came from a "Bands on the Bill" number staff typed; it's
    # counted now (advance_db.artist_count_for_event), so it can't disagree
    # with the bookings it's counting.
    n = max(len(acts), booked_n or 0)
    if template is None:
        template = UNIVERSAL_TEMPLATE
    if not template.exists():
        print(f"Template not found: {template}", file=sys.stderr)
        sys.exit(1)

    doc = Document(str(template))
    grid = find_grid(doc)
    if grid is None:
        print("Couldn't find the EVENT INFORMATION table.", file=sys.stderr); sys.exit(1)

    fill_header(grid, event)
    fill_event_type(grid, event, n)
    fill_engineer(grid, event, n, acts=acts)
    fill_consoles(grid, event)
    fill_crew_schedule(doc, event, acts)
    fill_lead(doc, event)

    # Which of the 3 act columns this act's data goes into — its position on
    # the bill, earliest set start first. See _act_col.
    def _col(a):
        return _act_col(a, n)

    # act-name header row, three lines (Brian, 2026-09-15): the bold label the
    # template already prints (ARTIST 1:/ARTIST 2:/ARTIST 3:), then the artist's
    # name on the template's own blank second line, then their set time. The
    # third line is added here — the template has no paragraph for it — cloned
    # from the name line so it inherits that cell's font and spacing.
    for r in grid.rows:
        if r.cells and r.cells[0].text.strip() == "" and any(
                c.paragraphs and c.paragraphs[0].runs and c.paragraphs[0].runs[0].bold
                for c in r.cells[1:]):
            for a in acts:
                if not a.get("artist"):
                    continue
                ci = _col(a)
                if ci < len(r.cells) and len(r.cells[ci].paragraphs) >= 2:
                    label = a["artist"]["name"]
                    if a.get("_cancelled"):
                        label = f"CANCELLED — {label}"
                    set_para_text(r.cells[ci].paragraphs[1], label)
                    set_para_text(_third_line(r.cells[ci]), set_time_range(a))
            break

    rows_by_label = act_columns(grid, n)
    filled_acts = 0
    no_riser_series = _series_without_riser(event.get("series"))
    for a in acts:
        if a.get("_cancelled"):
            continue
        mf = merged_fields(a)
        if no_riser_series and not mf.get("stage_type"):
            mf["stage_type"] = "Flat stage"  # audit #15: no risers for this series
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
            ci = _col(a)
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

    return doc, event, acts, n


# ── reading a PAST advance back out (for the returning-artist recap email) ──
#
# events/event_acts get TRUNCATEd and rebuilt from the live sheet on every
# package_run.py pass (see its own docstring) — they're a working model, not a
# history. The filed .docx in the venue tree is the only thing that durably
# remembers what was actually on a past show's advance, staff overrides
# included, so this reads the real file back rather than reconstructing from
# the DB. Brian's explicit call (2026-09-07) over the DB-reconstruction option.

NYQUIST_DEFAULT = fs.nyquist_root()  # same default run_now.py uses
# 2026-09-12: filed advance docs live in the REAL Dropbox venue folders now,
# not Nyquist — see fieldspec.real_venue_folder()/real_month_folder().

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
    scheme (<Real Venue Folder>/<MM.YYYY Code>/<MMDDYY> <Event Name> Prod
    Adv.docx, in the real Dropbox tree) — globbed by date stamp since a past
    event's real name isn't reliably in the DB any more (events/event_acts is
    a working model, not an archive)."""
    # Registry first (2026-09-13 audit #2): the doc(s) the pipeline actually
    # filed for this venue+date, newest write first — never filename sort
    # order. Only when nothing is registered (a show filed before the
    # registry existed) fall back to the date-stamp glob, newest-modified first.
    if root is None:
        try:
            with db.get_conn() as conn, conn.cursor() as cur:
                rows = db.filed_docs_for(cur, venue, event_date)
            hits = []
            for r in rows:
                p = Path(r["path"])
                p = p if p.is_absolute() else fs.real_dropbox_root() / p
                if p.exists():
                    hits.append(p)
            if hits:
                return hits
        except Exception as e:  # noqa: BLE001 — fall back to the folder scan
            print(f"[daysheet] filed_docs lookup failed: {e!r}", file=sys.stderr)
    root = Path(root) if root else fs.real_dropbox_root()
    folder = root / fs.real_venue_folder(venue) / fs.real_month_folder(venue, event_date)
    if not folder.exists():
        return []
    stamp = event_date.strftime("%m%d%y")
    return sorted(folder.glob(f"{stamp} * Prod Adv.docx"),
                  key=lambda p: p.stat().st_mtime, reverse=True)


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


def _template_defaults(ci):
    """label(norm) -> the pristine universal template's own default text in
    that act column. A filled doc's row that still matches this is unfilled
    boilerplate ("N/A", a blank "FOH – \\nMon –") rather than real on-file
    data, regardless of which specific placeholder text the template happens
    to use for that row — cheaper and more general than hardcoding every
    known placeholder string. Only meaningful for a doc actually filed under
    the universal template (2026-09-11 on); an older doc filed under one of
    the retired venue-specific templates may occasionally show its own old
    boilerplate as if it were real, until it ages out of the recap-
    extraction catch-up window — a narrow, self-resolving gap, not a crash."""
    if not UNIVERSAL_TEMPLATE.exists():
        return {}
    try:
        doc = Document(str(UNIVERSAL_TEMPLATE))
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
        defaults = _template_defaults(ci)
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
