#!/usr/bin/env python3
"""Who's engineering a given show — read from Brian's public 3CDC staffing sheet.

Same two "publish to web" CSV tabs SPL-Monitor's showinfo.py already reads for
the FSQ show/engineer banner (docs.google.com export, no auth):
  - schedule sheet: one shared spreadsheet, a day-by-venue grid — each venue gets
    its own Date/DOTW/Event/Mix block of columns side by side.
  - codes sheet: mix-code -> First/Last/Cell lookup (second tab, same spreadsheet).

Only wired for venues in SCHEDULE_COLUMNS below. Never raises — an unreachable
sheet, an unstaffed date, or an unresolved code all just return None/blank, and
the caller falls back to whatever it would otherwise use (e.g. a manually-
entered day-of contact, or a hand-filled Engineer row).

The Mix cell itself is real, messy, hand-typed data — not just clean 2-letter
codes. Observed in the wild: a single code ("GH"); two codes for FOH/Mon
("JM /BL", "KS + AD"); a code with a trailing time range or note in parens
("KS (2-7:30)", "BL (Movie set-up ... - 5-8:30)"); a code marked unconfirmed
with a bare "?" ("BP?"); three-plus codes covering staggered shifts
("BP (*6:30-3); AD (8-8); SC (*6:30-3)"); an occasional first name used ad hoc
instead of the official code ("Cara" for code CGL); and non-staffing rows like
a meeting attendee roster. `_split_mix_cell` only returns tokens it's
confident are real per-show assignments — anything messier than 1 or 2 clean
tokens is left for a human to resolve rather than guessed at.
"""
import csv
import datetime as dt
import io
import re
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


def _clean_token(tok):
    """One raw split of a Mix cell -> a bare code/name, or None if it's
    unconfirmed (contains '?') or empty once its parenthetical time
    range/note is stripped. Never guesses at an uncertain assignment."""
    if "?" in tok:
        return None
    tok = re.sub(r"\([^)]*\)", "", tok).strip()
    return tok or None


def _split_mix_cell(raw):
    """Raw Mix-column text -> ordered list of clean tokens. Splits on the
    delimiters actually seen in the sheet (/, +, ;, ,); a 20-person meeting
    roster splits into many tokens same as a real 3-person staggered-shift
    row would — callers refuse to resolve anything but exactly 1 or 2 tokens,
    so neither is ever guessed at."""
    return [c for c in (_clean_token(p) for p in re.split(r"[/+;,]", raw)) if c]


def _resolve_row(token, codes_rows):
    """One cleaned token -> its codes-sheet row, or None. Matches the Code
    column first (case-insensitive), falling back to the First Name column
    since real schedule entries sometimes use a first name ad hoc instead of
    the official code (e.g. 'Cara' for code CGL)."""
    target = token.strip().lower()
    by_first_name = None
    for row in codes_rows[2:]:  # row 0 = section label, row 1 = column headers
        if len(row) < 3:
            continue
        if row[0].strip().lower() == target:
            return row
        if by_first_name is None and row[1].strip().lower() == target:
            by_first_name = row
    return by_first_name


def _format_row(row, with_cell=False):
    if not row:
        return None
    name = f"{row[1].strip()} {row[2].strip()}".strip()
    if not name:
        return None
    if with_cell:
        cell = row[4].strip() if len(row) > 4 else ""
        return f"{name} ({cell})" if cell else name
    return name


def _mix_tokens(venue, show_date):
    """(tokens, codes_rows) for the show staffed on show_date at venue, or
    None if the venue isn't wired, the sheet is unreachable, or the date
    isn't staffed yet. tokens may be empty, or 3+ long for a messy cell —
    callers decide what counts as resolvable."""
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

    # A date can have several grid rows: blank filler rows for an unstaffed
    # day, and/or more than one real event. Blank rows sort ahead of a real
    # one often enough (confirmed 2026-09-08, WP) that stopping at the first
    # date match misses real data entirely — so scan every matching row and
    # take the first with an actual mix value. When more than one row for the
    # date HAS a mix value (two real events same day), this still just takes
    # the first — a separate, already-flagged, deliberately-deferred gap
    # (2026-09-07: needs matching by event time, not fixed here).
    need = max(cols.values())
    raw_mix = None
    for row in schedule_rows:
        if len(row) <= need:
            continue
        if _parse_date(row[cols["date"]]) == show_date:
            candidate = (row[cols["mix"]] or "").strip()
            if candidate:
                raw_mix = candidate
                break
    if not raw_mix:
        return None

    return _split_mix_cell(raw_mix), codes_rows


def engineer_for(venue, show_date):
    """'Gyasi Henderson (513-313-2431)' for the FOH engineer staffed on
    show_date at venue — or None if the venue isn't wired, the sheet is
    unreachable, the date isn't staffed yet, or the mix cell doesn't cleanly
    resolve to 1 or 2 codes (a 3+-name staggered-shift cell isn't guessed at
    here either — same rule as engineers_for()). When the cell has two codes
    (FOH/Mon), this is the first (FOH) one; see engineers_for() for both."""
    found = _mix_tokens(venue, show_date)
    if not found:
        return None
    tokens, codes_rows = found
    if len(tokens) not in (1, 2):
        return None
    return _format_row(_resolve_row(tokens[0], codes_rows), with_cell=True)


def engineers_for(venue, show_date):
    """{'foh': 'First Last', 'mon': 'First Last'} (either may be None) for the
    show staffed on show_date at venue. One set of initials in the Mix column
    is FOH only — Mon stays None, for staff to fill by hand (Brian,
    2026-09-08); two is FOH then Mon. A cell with zero, three-plus, or an
    unconfirmed ('?') token resolves to nothing rather than guess. Never
    raises."""
    empty = {"foh": None, "mon": None}
    found = _mix_tokens(venue, show_date)
    if not found:
        return empty
    tokens, codes_rows = found
    if len(tokens) not in (1, 2):
        return empty
    foh = _format_row(_resolve_row(tokens[0], codes_rows))
    mon = _format_row(_resolve_row(tokens[1], codes_rows)) if len(tokens) == 2 else None
    return {"foh": foh, "mon": mon}
