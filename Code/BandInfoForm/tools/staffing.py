#!/usr/bin/env python3
"""Who's engineering a given show — read from Brian's public 3CDC staffing sheet.

Same two "publish to web" CSV tabs SPL-Monitor's showinfo.py already reads for
the FSQ show/engineer banner (docs.google.com export, no auth):
  - schedule sheet: one shared spreadsheet, a day-by-venue grid — each venue gets
    its own Date/DOTW/Event/Mix block of columns side by side.
  - codes sheet: mix-code -> First/Last/Cell lookup (second tab, same spreadsheet).

Only wired for venues in SCHEDULE_COLUMNS below. Never raises — an unreachable
sheet, an unstaffed date, or an unresolved code all just return None, and the
caller falls back to whatever it would otherwise use (e.g. a manually-entered
day-of contact).
"""
import csv
import datetime as dt
import io
import urllib.request

SCHEDULE_SHEET_ID = "10idHRrZrEjj1bwuexXIMQ6GY3tr0pXOd2YQcO60NnJw"
SCHEDULE_GID = "1413426845"
CODES_GID = "809527620"

# venue -> 0-based column indices within the schedule sheet's day-by-venue grid.
# FSQ's matches SPL-Monitor's config.json scheduleColumns; WP confirmed 2026-09-07
# (same sheet, its own block starts a few columns over).
SCHEDULE_COLUMNS = {
    "Fountain Square": {"date": 6, "event": 8, "mix": 9},
    "Washington Park": {"date": 15, "event": 17, "mix": 18},
}


def _export_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SCHEDULE_SHEET_ID}/export?format=csv&gid={gid}"


def _fetch_csv(gid, timeout=10):
    with urllib.request.urlopen(_export_url(gid), timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(text)))


def _parse_date(s):
    s = (s or "").strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def engineer_for(venue, show_date):
    """'Gyasi Henderson (513-313-2431)' for the mix-code staffed on show_date at
    venue — or None if the venue isn't wired, the sheet is unreachable, the date
    isn't staffed yet, or the code doesn't resolve to a name."""
    cols = SCHEDULE_COLUMNS.get(venue)
    if not cols or not show_date:
        return None
    if isinstance(show_date, str):
        try:
            show_date = dt.date.fromisoformat(show_date)
        except ValueError:
            return None

    try:
        schedule_rows = _fetch_csv(SCHEDULE_GID)
        codes_rows = _fetch_csv(CODES_GID)
    except Exception as e:  # noqa: BLE001 — sheet down/unreachable isn't fatal
        print(f"[staffing] fetch failed: {e!r}", flush=True)
        return None

    need = max(cols.values())
    mix_code = None
    for row in schedule_rows:
        if len(row) <= need:
            continue
        if _parse_date(row[cols["date"]]) == show_date:
            mix_code = (row[cols["mix"]] or "").strip() or None
            break
    if not mix_code:
        return None

    for row in codes_rows[2:]:  # row 0 = section labels, row 1 = column headers
        if len(row) < 3 or row[0].strip() != mix_code:
            continue
        name = f"{row[1].strip()} {row[2].strip()}".strip()
        if not name:
            return None
        cell = row[4].strip() if len(row) > 4 else ""
        return f"{name} ({cell})" if cell else name
    return None
