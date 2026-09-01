#!/usr/bin/env python3
"""Fill the 513 Airwaves production day-sheet from an event's advance submissions.

Writes only the BAND-provided cells of the three-act grid (Stage Plot, Engineer,
Monitors/IEM, Scenic, Merch, Parking, Drink Tix, Dressing-room tent, Backline,
Contact). The schedule and internal cells (PA, consoles, lead, paying?) are left
exactly as the template has them — those aren't band data.

Each act fills its own column:  opener = cols 1-2, direct_support = 3-4,
headliner = 5-6 (matching the template's OPENER / DIR SUPPORT / HEADLINER labels).

  python3 daysheet.py --event 1
  python3 daysheet.py --event 1 --template doc_templates/513_airwaves_daysheet.docx --out out.docx

Drop the blank template at tools/doc_templates/513_airwaves_daysheet.docx.
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db

from docx import Document

TEMPLATES = HERE / "doc_templates"
FILLED = HERE / "filled"
FILLED.mkdir(exist_ok=True)
DEFAULT_TEMPLATE = TEMPLATES / "513_airwaves_daysheet.docx"

# slot -> first grid column of its merged pair
SLOT_COL = {"opener": 1, "direct_support": 3, "headliner": 5}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower().rstrip("?")


def act_cells(sub):
    """Map one act's submission to {normalized row label: cell text}. Only rows we
    fill are returned; everything else is left as the template has it."""
    if not sub:
        return {}
    d = sub.get("data") or {}

    def g(k):
        v = sub.get(k)
        return v if v not in (None, "") else d.get(k, "")

    out = {}

    # Stage Plot
    sp = d.get("stage_plot_desc", "")
    if d.get("stage_plot_file"):
        sp = (sp + " (file on record)").strip()
    if sp:
        out["stage plot"] = sp

    # Engineer
    oe = g("own_engineer")
    if oe:
        out["engineer"] = "House" if str(oe).lower().startswith("no") else "Own (coordinating)"

    # Monitors / IEM
    mons = g("monitors")
    parts = []
    if mons not in (None, ""):
        parts.append(f"{mons} wedges")
    if sub.get("own_iems") is True:
        ie = "own IEMs"
        ss = g("split_snake")
        if ss:
            ie += f" (split: {ss})"
        parts.append(ie)
    if parts:
        out["monitors/ iem"] = " · ".join(parts)

    # Scenic: drum riser + any other scenic elements (banner, backdrop, LED wall...)
    st = g("stage_type")
    riser = ""
    if st:
        riser = "Drum riser - YES" if "riser" in str(st).lower() else "Drum riser - no"
    scenic_note = d.get("scenic", "")
    scenic = "; ".join(x for x in (riser, scenic_note) if x)
    if scenic:
        out["scenic"] = scenic

    # Merch
    if sub.get("merch") is not None:
        out["merch"] = "Yes" if sub.get("merch") else "No"

    # Parking
    if sub.get("large_vehicle") is not None:
        out["parking"] = "Large vehicle" if sub.get("large_vehicle") else "Standard"

    # Drink Tix = performers + crew count
    perf = g("performers")
    if perf not in (None, ""):
        out["drink tix"] = str(perf)

    # Dressing room tent
    bt = g("band_tent")
    if bt:
        out["dressing room tent"] = "Yes" if str(bt).lower().startswith("yes") else "No"

    # Backline (only overwrite the template's N/A if the band noted something)
    bl = d.get("backline", "")
    if bl:
        out["backline"] = bl

    # Contact
    cn, cp = g("contact_name"), g("contact_phone")
    contact = " ".join(x for x in (cn, cp) if x).strip()
    if contact:
        out["contact"] = contact

    return out


def set_cell(cell, text):
    """Replace a cell's text while keeping its paragraph formatting."""
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r.text = ""
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)


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
    """The EVENT INFORMATION table — the one with a 'Stage Plot' row."""
    for t in all_tables(doc):
        for r in t.rows:
            if r.cells and norm(r.cells[0].text) == "stage plot":
                return t
    return None


def fill(event_id, template, out_path=None):
    if not template.exists():
        print(f"Template not found: {template}\nDrop the blank 513 day-sheet there.",
              file=sys.stderr)
        sys.exit(1)

    with db.get_conn() as conn, conn.cursor() as cur:
        event = db.get_event(cur, event_id)
        if not event:
            print(f"No event {event_id}", file=sys.stderr); sys.exit(1)
        acts = db.event_acts(cur, event_id)

    doc = Document(str(template))
    grid = find_grid(doc)
    if grid is None:
        print("Couldn't find the EVENT INFORMATION grid in the template.", file=sys.stderr)
        sys.exit(1)

    # index rows by normalized label
    rows_by_label = {}
    for r in grid.rows:
        if r.cells:
            rows_by_label.setdefault(norm(r.cells[0].text), r)

    filled_acts = 0
    for a in acts:
        col = SLOT_COL.get(a["slot"])
        if col is None or not a.get("submission"):
            continue
        cells = act_cells(a["submission"])
        if cells:
            filled_acts += 1
        for label, value in cells.items():
            row = rows_by_label.get(label)
            if not row:
                continue
            # write to both columns of the merged pair (idempotent if truly merged)
            for ci in (col, col + 1):
                if ci < len(row.cells):
                    set_cell(row.cells[ci], value)

    if out_path is None:
        tag = re.sub(r"[^A-Za-z0-9]+", "_",
                     event.get("name") or f"event{event_id}").strip("_")
        date = event.get("event_date")
        out_path = FILLED / f"{tag}__{date or 'nodate'}__daysheet.docx"
    doc.save(out_path)
    print(f"Filled day-sheet: {out_path}")
    print(f"  event {event_id}: {event.get('name')} @ {event.get('venue')} {event.get('event_date')}")
    print(f"  {filled_acts} of {len(acts)} act(s) had a submission to fill.")
    for a in acts:
        who = a["artist"]["name"] if a.get("artist") else "(none)"
        mark = "✓" if a.get("submission") else "— no submission"
        print(f"    {a['slot']:16} {who} {mark}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", type=int, required=True)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    fill(args.event, args.template, args.out)


if __name__ == "__main__":
    main()
