#!/usr/bin/env python3
"""Reader for the 3CDC Advance List spreadsheet (tools/lists/advance_list_template.xlsx).

Normalizes each data row to a dict. Skips the gray example rows and blanks.
Columns: Event Name, Event Date, Venue, Series, Slot, Set Time, Artist Name,
Contact Email, Notes.
"""
import datetime as dt
from pathlib import Path

FIELDS = {
    "event name": "event_name",
    "event date": "event_date",
    "venue": "venue",
    "series": "series",
    "slot": "slot",
    "set time": "set_time",
    "artist name": "artist_name",
    "contact email": "contact_email",
    "notes": "notes",
}


def _norm_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, (dt.datetime, dt.date)):
        return v.date().isoformat() if isinstance(v, dt.datetime) else v.isoformat()
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return s  # leave as-is; downstream parser will try again


def read_advance_sheet(path):
    from openpyxl import load_workbook
    wb = load_workbook(Path(path), data_only=True)
    ws = wb["Advance List"] if "Advance List" in wb.sheetnames else wb.active
    header = {}
    for i, cell in enumerate(ws[1], start=1):
        key = FIELDS.get(str(cell.value or "").strip().lower())
        if key:
            header[i] = key
    rows = []
    for row in ws.iter_rows(min_row=2):
        rec = {}
        for cell in row:
            key = header.get(cell.column)
            if key:
                rec[key] = cell.value
        artist = (str(rec.get("artist_name") or "")).strip()
        notes = (str(rec.get("notes") or "")).strip().upper()
        if not artist or "EXAMPLE ROW" in notes:
            continue
        rec = {k: (str(v).strip() if isinstance(v, str) else v) for k, v in rec.items()}
        rec["artist_name"] = artist
        rec["event_date"] = _norm_date(rec.get("event_date"))
        rows.append(rec)
    return rows
