#!/usr/bin/env python3
"""Sheet side of staff bookings: append new ones, and push edits into the rows
that are already there.

--data appends any booking that isn't already a row (matched on event + date +
venue + artist) and prints the comma-separated ids it handled to STDOUT, so the
caller can stamp them seeded.

--edited (2026-09-15) UPDATES rows for bookings edited in the app after they
were seeded. Without this an edit died in the database: the next pipeline run
rebuilds events from the SHEET, so the old row simply reinstated itself — and
since the sheet's Start column now decides who is Artist 1, a stale row also
reorders the bill. Only the columns a booking owns are written; band-detail
columns (Monitors, Stage Type, ...) are the band's answers or Brian's own
overrides and are never touched. Prints synced ids to STDOUT.

A booking whose artist, venue or date was the thing that changed is found by the
identity its row was WRITTEN under (`_old_ident`), so a rename moves the row it
already has instead of stranding it.

  python3 append_bookings.py --list advance-list.xlsx --data bookings.json
  python3 append_bookings.py --list advance-list.xlsx --edited edited.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fieldspec as fs

from openpyxl import load_workbook

INPUT_SHEET = "Advance List"


def _s(v):
    return "" if v is None else str(v).strip()


def norm(v):
    return re.sub(r"\s+", " ", _s(v)).lower()


def find_header_row(ws):
    labels = {lbl.lower() for (lbl, _k, _c) in fs.ALL_COLUMNS}
    best_row, best = 2, 0
    for r in range(1, 8):
        hits = sum(1 for c in ws[r] if _s(c.value).lower() in labels)
        if hits > best:
            best, best_row = hits, r
    return best_row


def sheet_index(ws):
    """(header row, {internal key: column}) for the sheet as it stands."""
    hrow = find_header_row(ws)
    key_col = {}
    for c in range(1, ws.max_column + 1):
        lbl = _s(ws.cell(hrow, c).value)
        if lbl in fs.LABEL_TO_KEY:
            key_col[fs.LABEL_TO_KEY[lbl]] = c
    return hrow, key_col


def update_edited(sheet_path, data_path):
    """Write edited bookings back over their existing sheet rows."""
    edits = json.loads(data_path.read_text()) if data_path.exists() else []
    if not edits:
        print("no edited bookings to sync", file=sys.stderr)
        print("")
        return
    loaded_hash = fs.sheet_hash(sheet_path)
    wb = load_workbook(sheet_path)
    ws = wb[INPUT_SHEET] if INPUT_SHEET in wb.sheetnames else wb.worksheets[0]
    hrow, key_col = sheet_index(ws)
    c_artist, c_venue, c_date = (key_col.get("artist_name"), key_col.get("venue"),
                                 key_col.get("event_date"))
    if not c_artist:
        print("no Artist Name column; cannot sync edits", file=sys.stderr)
        print("")
        return

    rows_by_ident = {}
    for r in range(hrow + 1, ws.max_row + 1):
        a = _s(ws.cell(r, c_artist).value)
        if not a:
            continue
        ident = (norm(a),
                 norm(ws.cell(r, c_venue).value) if c_venue else "",
                 _s(ws.cell(r, c_date).value)[:10] if c_date else "")
        rows_by_ident.setdefault(ident, r)

    synced, changed_cells, missing = [], 0, []
    for b in edits:
        old = b.get("_old_ident") or {}
        candidates = [
            (norm(old.get("artist_name")), norm(old.get("venue")),
             _s(old.get("event_date"))[:10]),
            (norm(b.get("artist_name")), norm(b.get("venue")),
             _s(b.get("event_date"))[:10]),
        ]
        row = next((rows_by_ident[i] for i in candidates if i in rows_by_ident), None)
        if row is None:
            missing.append(f"{b.get('artist_name')} {b.get('event_date')}")
            continue
        for key in fs.SHEET_WRITEBACK_KEYS:
            col = key_col.get(key)
            if col is None:
                continue
            val = b.get(key)
            if val in (None, ""):
                continue        # an emptied field leaves whatever the sheet has
            val = _s(val)[:10] if key == "event_date" else _s(val)
            if _s(ws.cell(row, col).value) != val:
                print(f"  row {row} {b.get('artist_name')} · {key}: "
                      f"{_s(ws.cell(row, col).value)!r} -> {val!r}", file=sys.stderr)
                ws.cell(row, col).value = val
                changed_cells += 1
        synced.append(str(b["id"]))

    if changed_cells:
        try:
            fs.safe_save_workbook(wb, sheet_path, loaded_hash)
        except fs.SheetChangedError as e:
            print(f"  ! {e} — not saving, re-run to pick up the current sheet", file=sys.stderr)
            sys.exit(1)
    print(f"synced {len(synced)} edited booking(s), {changed_cells} cell(s)", file=sys.stderr)
    for m in missing:
        print(f"  ! no sheet row found for {m} — left alone", file=sys.stderr)
    print(",".join(synced))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True, type=Path)
    ap.add_argument("--data", type=Path)
    ap.add_argument("--edited", type=Path)
    args = ap.parse_args()
    if not args.data and not args.edited:
        ap.error("one of --data or --edited is required")
    if args.edited:
        update_edited(args.list, args.edited)
        return

    bookings = json.loads(args.data.read_text()) if args.data.exists() else []
    if not bookings:
        return
    loaded_hash = fs.sheet_hash(args.list)
    wb = load_workbook(args.list)
    ws = wb[INPUT_SHEET] if INPUT_SHEET in wb.sheetnames else wb.worksheets[0]

    hrow = find_header_row(ws)
    # key -> column, from the header row
    key_col = {}
    for c in range(1, ws.max_column + 1):
        lbl = _s(ws.cell(hrow, c).value)
        if lbl in fs.LABEL_TO_KEY:
            key_col[fs.LABEL_TO_KEY[lbl]] = c
    c_artist = key_col.get("artist_name")
    c_venue = key_col.get("venue")
    c_date = key_col.get("event_date")
    if not c_artist:
        print("no Artist Name column; cannot seed", file=sys.stderr)
        return

    # existing (artist, venue, date) identities already in the sheet
    existing = set()
    last = hrow
    for r in range(hrow + 1, ws.max_row + 1):
        a = _s(ws.cell(r, c_artist).value)
        if a:
            last = r
            existing.add((norm(a),
                          norm(ws.cell(r, c_venue).value) if c_venue else "",
                          _s(ws.cell(r, c_date).value)[:10] if c_date else ""))

    handled, appended = [], 0
    row = last + 1
    for b in bookings:
        handled.append(str(b["id"]))
        ident = (norm(b.get("artist_name")), norm(b.get("venue")),
                 _s(b.get("event_date"))[:10])
        if ident in existing:
            continue  # already represented (staff typed it, or a prior seed)
        for key, col in key_col.items():
            val = b.get(key)
            if val not in (None, ""):
                ws.cell(row, col).value = _s(val)
        existing.add(ident)
        row += 1
        appended += 1

    if appended:
        try:
            fs.safe_save_workbook(wb, args.list, loaded_hash)
        except fs.SheetChangedError as e:
            print(f"  ! {e} — not saving, re-run to pick up the current sheet", file=sys.stderr)
            sys.exit(1)
    print(f"appended {appended} new booking row(s)", file=sys.stderr)
    # STDOUT: ids to stamp seeded (handled whether appended or already present)
    print(",".join(handled))


if __name__ == "__main__":
    main()
