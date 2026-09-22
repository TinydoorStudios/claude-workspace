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

# 2026-09-21 sweep (PRIOR-10): Excel turns a typed '7:30 PM' into a time (or a
# '3-4' into a date); every reader gets the house clock string instead.
SCHEDULE_KEYS = set(fs.ACT_SCHEDULE_KEYS) | {"curfew"}
_EXCEL_EPOCH_DAYS = {dt.date(1899, 12, 30), dt.date(1899, 12, 31), dt.date(1900, 1, 1),
                     dt.date(1904, 1, 1)}


def _clock(t):
    """dt.time -> '7:30p', the same house format as app._minutes_to_clock."""
    return f"{t.hour % 12 or 12}:{t.minute:02d}{'a' if t.hour < 12 else 'p'}"


def _cell_text(key, v, where):
    """A cell value as the text every reader expects (event_date is left to _norm_date)."""
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip()
    if key == "event_date":
        return v
    if isinstance(v, dt.timedelta):                     # a '[h]:mm' format
        secs = int(v.total_seconds()) % 86400
        v = dt.time(secs // 3600, secs % 3600 // 60)
    if isinstance(v, dt.datetime):
        if v.date() in _EXCEL_EPOCH_DAYS or (key in SCHEDULE_KEYS and v.time() != dt.time(0)):
            v = v.time()
        else:
            print(f"  ! {where}: Excel turned '{key}' into a date — retype it as text",
                  file=sys.stderr)
            return v.date().isoformat()
    elif isinstance(v, dt.date):
        print(f"  ! {where}: Excel turned '{key}' into a date — retype it as text", file=sys.stderr)
        return v.isoformat()
    if isinstance(v, dt.time):
        if key == "set_time":                           # a set LENGTH, not a clock: minutes
            return str(v.hour * 60 + v.minute)
        return _clock(v)
    if isinstance(v, bool):                             # the Yes/No dropdown columns
        return "Yes" if v else "No"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


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
                # 2026-09-21 sweep (PIPE-1): a '../…' Stage Plot value is a link
                # target openpyxl copied in after a row shift, never typed — skip it.
                if (key == "stage_plot_desc" and isinstance(cell.value, str)
                        and cell.value.strip().startswith("../")):
                    continue
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
        rec = {k: _cell_text(k, v, f"row {row[0].row} {k}") for k, v in rec.items()}
        rec["artist_name"] = artist
        rec["event_date"] = _norm_date(rec.get("event_date"))
        rows.append(rec)
    return rows
