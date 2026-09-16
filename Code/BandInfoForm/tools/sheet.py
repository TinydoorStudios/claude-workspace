#!/usr/bin/env python3
"""Reader for the 3CDC Advance List spreadsheet (tools/lists/advance_list_template.xlsx).

Normalizes each data row to a dict. Skips the gray example rows and blanks.
Columns: Event Name, Event Date, Venue, Series, Start, Set Length, Artist Name,
Contact Email, Notes.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fieldspec as fs

# column label (lowercased) -> internal key, for every column in the spec
FIELDS = {lbl.lower(): key for (lbl, key, _ch) in fs.ALL_COLUMNS}
FIELDS["notes"] = "notes"  # tolerate a legacy Notes column if present


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


def _band_owned(wb):
    """Cells the band filled (from merge_status' hidden map) -> their value.

    A band-filled cell is a live mirror of the form, NOT a Brian override, so the
    importer must read it as blank; only cells Brian typed himself win."""
    meta = {}
    if "_advance_meta" in wb.sheetnames:
        for row in wb["_advance_meta"].iter_rows(values_only=True):
            if row and row[0]:
                meta[str(row[0])] = "" if len(row) < 2 or row[1] is None else str(row[1])
    return meta


def read_advance_sheet(path):
    from openpyxl import load_workbook
    wb = load_workbook(Path(path), data_only=True)
    owned = _band_owned(wb)
    ws = wb["Advance List"] if "Advance List" in wb.sheetnames else wb.active
    # Find the header row wherever it is (a group-label row may sit above it) and
    # map columns by LABEL, not position — so columns can be reordered or removed.
    header, header_row, best = {}, 1, 0
    for ridx in range(1, 8):
        m = {}
        for cell in ws[ridx]:
            key = FIELDS.get(str(cell.value or "").strip().lower())
            if key:
                m[cell.column] = key
        if len(m) > best:
            best, header_row, header = len(m), ridx, m
    if not header:
        return []
    rows = []
    for row in ws.iter_rows(min_row=header_row + 1):
        # audit 2026-09-16 #22 (root cause D): the band-owned check below
        # needs this row's own identity (band/venue/date) to build the same
        # content-based _advance_meta key merge_status.py now writes — a
        # first pass over the row's raw values resolves that identity
        # before the second pass applies the mirror check per cell.
        raw = {}
        for cell in row:
            key = header.get(cell.column)
            if key:
                raw[key] = cell.value
        band = str(raw.get("artist_name") or "").strip()
        venue = str(raw.get("venue") or "").strip()
        date = _norm_date(raw.get("event_date")) or ""

        rec = {}
        for cell in row:
            key = header.get(cell.column)
            if key:
                content_key = fs.advance_meta_key(band, venue, date, key)
                addr = f"r{cell.row}c{cell.column}"  # pre-2026-09-16 key, migration fallback only
                mirrored = owned.get(content_key)
                if mirrored is None:
                    mirrored = owned.get(addr)
                if mirrored is not None and str(cell.value or "") == mirrored:
                    continue  # band-filled mirror, not a Brian override
                rec[key] = cell.value
        artist = (str(rec.get("artist_name") or "")).strip()
        notes = (str(rec.get("notes") or "")).strip().upper()
        if not artist or "EXAMPLE ROW" in notes or artist.upper().startswith("EXAMPLE"):
            continue
        rec = {k: (str(v).strip() if isinstance(v, str) else v) for k, v in rec.items()}
        rec["artist_name"] = artist
        rec["event_date"] = _norm_date(rec.get("event_date"))
        rows.append(rec)
    return rows
