#!/usr/bin/env python3
"""Fill the 513 Airwaves production day-sheet from an event.

Source of truth is the advance SPREADSHEET (event + any band overrides); the
advance FORM fills whatever the sheet left blank. This merges the two per act —
the spreadsheet value wins, the form fills the gaps — and writes:

  - header Date / Event / Band names        (from the event record)
  - AUDIO row set times per act             (from the sheet)
  - each act's band cells in its column      (opener 1-2 / support 3-4 / headliner 5-6)

The schedule detail rows and the internal cells (PA, consoles, subs, video,
buyout) are left as the template has them. Event Type / Paying? / MC / DJ / Lead
are stored on the event but not yet written into the doc (delicate checkbox
cells — next pass).

  python3 daysheet.py --event 1
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
sys.path.insert(0, str(HERE))
import advance_db as db

from docx import Document

TEMPLATES = HERE / "doc_templates"
FILLED = HERE / "filled"
FILLED.mkdir(exist_ok=True)
DEFAULT_TEMPLATE = TEMPLATES / "513_airwaves_daysheet.docx"

SLOT_COL = {"opener": 1, "direct_support": 3, "headliner": 5}
SLOT_AUDIO_LABEL = {"opener": "OPENER", "direct_support": "DIR SUPPORT",
                    "headliner": "HEADLINER"}


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


def act_cells(f):
    """Merged fields -> {normalized day-sheet row label: cell text}."""
    out = {}
    if not f:
        return out

    sp = f.get("stage_plot_desc", "")
    if f.get("stage_plot_file"):
        sp = (sp + " (file on record)").strip()
    if sp:
        out["stage plot"] = sp

    oe = f.get("own_engineer")
    if oe:
        out["engineer"] = "House" if str(oe).lower().startswith("no") else "Own (coordinating)"

    parts = []
    if f.get("monitors") not in (None, ""):
        parts.append(f"{f['monitors']} wedges")
    if str(f.get("own_iems", "")).lower() == "yes":
        ie = "own IEMs"
        if f.get("split_snake"):
            ie += f" (split: {f['split_snake']})"
        parts.append(ie)
    if parts:
        out["monitors/ iem"] = " · ".join(parts)

    if f.get("input_notes"):
        out["input notes"] = f["input_notes"]

    st = f.get("stage_type")
    riser = ("Drum riser - YES" if "riser" in str(st).lower() else "Drum riser - no") if st else ""
    scenic = "; ".join(x for x in (riser, f.get("scenic", "")) if x)
    if scenic:
        out["scenic"] = scenic

    if f.get("lighting"):
        out["lighting"] = f["lighting"]
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

    contact = " ".join(str(x) for x in (f.get("contact_name"), f.get("contact_phone"))
                       if x not in (None, "")).strip()
    if contact:
        out["contact"] = contact
    return out


def set_cell(cell, text):
    text = "" if text is None else str(text)
    p = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for r in list(p.runs):
        r.text = ""
    (p.runs[0] if p.runs else p.add_run("")).text = text


def set_multiline(cell, lines):
    """Set a cell to N lines, reusing existing paragraphs where possible."""
    paras = cell.paragraphs
    for i, line in enumerate(lines):
        if i < len(paras):
            p = paras[i]
            for r in list(p.runs):
                r.text = ""
            (p.runs[0] if p.runs else p.add_run("")).text = line
        else:
            cell.add_paragraph(line)
    # blank any leftover paragraphs
    for j in range(len(lines), len(paras)):
        for r in list(paras[j].runs):
            r.text = ""


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
    for t in all_tables(doc):
        for r in t.rows:
            if r.cells and norm(r.cells[0].text) == "stage plot":
                return t
    return None


def fill_header(grid, event, acts):
    """Row 0 value cell: Date / Event name / Band names (aligned to the labels)."""
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "event information":
            value_cell = r.cells[2]  # merged across cols 2-5
            bands = ", ".join(a["artist"]["name"] for a in acts if a.get("artist"))
            date = event.get("event_date").isoformat() if event.get("event_date") else ""
            set_multiline(value_cell, [date, event.get("name") or "", bands])
            return


def fill_audio_times(grid, acts):
    for r in grid.rows:
        if r.cells and norm(r.cells[0].text) == "audio":
            for a in acts:
                col = SLOT_COL.get(a["slot"])
                t = a.get("set_time")
                if col is None or not t:
                    continue
                label = SLOT_AUDIO_LABEL.get(a["slot"], a["slot"].upper())
                for ci in (col, col + 1):
                    if ci < len(r.cells):
                        set_cell(r.cells[ci], f"{label}: {t}")
            return


def fill(event_id, template, out_path=None):
    if not template.exists():
        print(f"Template not found: {template}", file=sys.stderr)
        sys.exit(1)
    with db.get_conn() as conn, conn.cursor() as cur:
        event = db.get_event(cur, event_id)
        if not event:
            print(f"No event {event_id}", file=sys.stderr); sys.exit(1)
        acts = db.event_acts(cur, event_id)

    doc = Document(str(template))
    grid = find_grid(doc)
    if grid is None:
        print("Couldn't find the EVENT INFORMATION grid.", file=sys.stderr); sys.exit(1)

    rows_by_label = {}
    for r in grid.rows:
        if r.cells:
            rows_by_label.setdefault(norm(r.cells[0].text), r)

    fill_header(grid, event, acts)
    fill_audio_times(grid, acts)

    filled_acts = 0
    for a in acts:
        col = SLOT_COL.get(a["slot"])
        if col is None:
            continue
        cells = act_cells(merged_fields(a))
        if cells:
            filled_acts += 1
        for label, value in cells.items():
            row = rows_by_label.get(label)
            if not row:
                continue
            for ci in (col, col + 1):
                if ci < len(row.cells):
                    set_cell(row.cells[ci], value)

    if out_path is None:
        tag = re.sub(r"[^A-Za-z0-9]+", "_", event.get("name") or f"event{event_id}").strip("_")
        date = event.get("event_date")
        out_path = FILLED / f"{tag}__{date or 'nodate'}__daysheet.docx"
    doc.save(out_path)
    print(f"Filled day-sheet: {out_path}")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", type=int, required=True)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    fill(args.event, args.template, args.out)


if __name__ == "__main__":
    main()
