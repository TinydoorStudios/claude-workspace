#!/usr/bin/env python3
"""Who's staffing a given show — read from Brian's public 3CDC staffing sheet.

Same two "publish to web" CSV tabs SPL-Monitor's showinfo.py already reads for
the FSQ show/engineer banner (docs.google.com export, no auth):
  - schedule sheet: one shared spreadsheet, a day-by-venue grid — each venue gets
    its own Date/DOTW/Event/Mix/Tech/Stagehand/Stage Support/Other block of
    columns side by side (5 venue blocks total — see SCHEDULE_COLUMNS).
  - codes sheet: mix-code -> First/Last/Cell lookup (second tab, same spreadsheet).

engineer_for()/engineers_for() (Mix only — FOH/Mon) are the original,
long-verified functions everything else in this pipeline (the day-sheet's
Engineer row, the WP email's day-of-contact line) actually depends on -
untouched. staff_for() (2026-09-09) is additive: every OTHER role
(Tech/Stagehand/Stage Support/Other) at any of the 5 venues, read-only, no
shared code path with Mix.

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
# FSQ's matches SPL-Monitor's config.json scheduleColumns; WP confirmed
# 2026-09-07 (same sheet, its own block starts a few columns over). Full
# column set (Date/DOTW/Event/Mix/Tech/Stagehand/Stage Support/Other) learned
# 2026-09-09 by reading the sheet's own row-0/row-1 headers directly rather
# than guessing — row 1 literally names each block's venue. Two things worth
# knowing about the shape: Memorial Hall has its own block here (not wired
# anywhere else in this pipeline yet — that's fine, staffing.py just reflects
# what the sheet has); and Zeigler Park / Court Street Plaza / Imagination
# Alley share ONE combined block (same columns for all three) where
# Stagehand and Stage Support are also merged into a single column — the
# source data genuinely doesn't distinguish them there, so this module
# doesn't invent a split. Elm Street Plaza also merges Stagehand/Stage
# Support into one column, but has its own separate block otherwise.
SCHEDULE_COLUMNS = {
    "Fountain Square": {"date": 6, "event": 8, "mix": 9, "tech": 10,
                         "stagehand": 11, "stage_support": 12, "other": 14},
    "Washington Park": {"date": 15, "event": 17, "mix": 18, "tech": 19,
                         "stagehand": 20, "stage_support": 21, "other": 22},
    "Memorial Hall": {"date": 23, "event": 25, "mix": 26, "tech": 27,
                       "stagehand": 28, "stage_support": 29, "other": 30},
    "Zeigler Park": {"date": 31, "event": 33, "mix": 34, "tech": 35,
                      "stagehand_support": 36, "other": 37},
    "Court Street Plaza": {"date": 31, "event": 33, "mix": 34, "tech": 35,
                            "stagehand_support": 36, "other": 37},
    "Imagination Alley": {"date": 31, "event": 33, "mix": 34, "tech": 35,
                           "stagehand_support": 36, "other": 37},
    "Elm Street Plaza": {"date": 38, "event": 40, "mix": 41, "tech": 42,
                          "stagehand_support": 43, "other": 44},
}

# Every non-mix role, keyed the same way SCHEDULE_COLUMNS spells it per venue
# (some venues have separate stagehand/stage_support columns, some have them
# merged into one stagehand_support column — staff_for() reports back under
# whichever key(s) that venue's block actually has).
_OTHER_ROLE_KEYS = ("tech", "stagehand", "stage_support", "stagehand_support", "other")


def _export_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SCHEDULE_SHEET_ID}/export?format=csv&gid={gid}"


_CSV_CACHE = {}          # gid -> (fetched_at, rows)
_CSV_TTL = 300           # seconds — one package_run (seconds) reuses; a long-
                         # lived app process still refreshes every 5 min.


def _fetch_csv(gid, timeout=10):
    """Fetch (and briefly cache) a sheet tab. The cache keeps a full package_run
    — which fills one doc per event, each reading the schedule — from hitting
    Google Sheets N times (and, if the sheet is down, waiting N×timeout);
    (Brian, 2026-09-11)."""
    hit = _CSV_CACHE.get(gid)
    if hit and (dt.datetime.now().timestamp() - hit[0]) < _CSV_TTL:
        return hit[1]
    with urllib.request.urlopen(_export_url(gid), timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    _CSV_CACHE[gid] = (dt.datetime.now().timestamp(), rows)
    return rows


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


def _clock_minutes(text, assume_pm=True):
    """'6:00pm' / '6:00p' / '11am' / '7' -> minutes since midnight, or None.
    With no am/pm the sheet convention applies (PM unless assume_pm=False):
    evening shows are the norm (Brian, 2026-09-11). 12am/12pm handled."""
    if not text:
        return None
    m = re.match(r"^\s*\*{0,2}(\d{1,2})(?::(\d{2}))?\s*(am|pm|a|p)?\b",
                 str(text).strip().lower())
    if not m:
        return None
    h, mn = int(m.group(1)), int(m.group(2) or 0)
    if not (0 <= h <= 12 and 0 <= mn < 60) or h == 0:
        return None
    suf = m.group(3)
    pm = suf.startswith("p") if suf else assume_pm
    if h == 12:
        h = 0
    return (h + (12 if pm else 0)) * 60 + mn


def _event_cell_range(cell):
    """(start_min, end_min) from the '(<start>-<end>)' part of an Event cell
    like 'Kidney Walk (7a-1p)' or 'OTR Performs (2-8)', else None. A range
    whose end lands before its start (e.g. '(11-2)' meaning 11am-2pm) is
    corrected by reading the start as AM."""
    line = (cell or "").strip().splitlines()[0] if (cell or "").strip() else ""
    paren = re.search(r"\(([^)]*)\)", line)
    if not paren:
        return None
    rng = re.search(
        r"(\*{0,2}\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)\s*-\s*"
        r"(\*{0,2}\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)", paren.group(1), re.I)
    if not rng:
        return None
    a, b = _clock_minutes(rng.group(1)), _clock_minutes(rng.group(2))
    if a is None or b is None:
        return None
    if b <= a:
        a2 = _clock_minutes(rng.group(1), assume_pm=False)
        if a2 is not None and a2 < b:
            a = a2
        else:
            return None
    return a, b


def _pick_staffed_row(staffed, series=None, event_name=None, artist_name=None,
                      event_start=None):
    """The mix cell for THIS show from [(event_cell, mix), ...] — see the
    rules in _mix_tokens(). None when the day is double-booked and nothing
    singles a row out."""
    if len(staffed) == 1:
        return staffed[0][1]
    hints = [h.strip().lower() for h in (series, event_name, artist_name)
             if h and str(h).strip()]
    if hints:
        hit = [mix for ev, mix in staffed
               if any(h in ev.lower() for h in hints)]
        if len(hit) == 1:
            return hit[0]
        if len(hit) > 1 and len(set(hit)) == 1:
            return hit[0]
    start = _clock_minutes(event_start)
    if start is not None:
        hit = []
        for ev, mix in staffed:
            rng = _event_cell_range(ev)
            if rng and rng[0] <= start < rng[1]:
                hit.append(mix)
        if len(hit) == 1:
            return hit[0]
        if len(hit) > 1 and len(set(hit)) == 1:
            return hit[0]
    if len({mix for _, mix in staffed}) == 1:
        return staffed[0][1]  # same crew on every row — no ambiguity
    return None


def _mix_tokens(venue, show_date, series=None, event_name=None,
                artist_name=None, event_start=None):
    """(tokens, codes_rows) for the show staffed on show_date at venue, or
    None if the venue isn't wired, the sheet is unreachable, or the date
    isn't staffed yet. tokens may be empty, or 3+ long for a messy cell —
    callers decide what counts as resolvable. `series` / `event_name` /
    `artist_name` / `event_start` are hints for a double-booked day (see
    below); any may be None."""
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
    # date match misses real data entirely — so only rows with an actual mix
    # value count.
    #
    # Two real events on one date (the 2026-09-07 gap; real example WP
    # 9/13/26: "Kidney Walk (7a-1p)" GH and "OTR Performs - CCM Movies (2-8)"
    # JM): pick the row for THIS show, never guess. In order —
    #   1. one staffed row on the date -> that's it (single-event day,
    #      unchanged behaviour);
    #   2. a row whose Event cell names the show's series, event name or
    #      band name (same rule event_times_for() uses);
    #   3. the row whose Event-cell time range contains the booking's event
    #      start ("(7a-1p)" holds an 11:00am show, "(2-8)" a 6:00pm one);
    #   4. still ambiguous -> None, so the Engineer row / day-of contact is
    #      left for a human rather than filled with the wrong person
    #      (Brian, 2026-09-15: the old "take the first row" fallback was the
    #      remaining hole).
    need = max(cols.values())
    ev_col = cols.get("event")
    staffed = []  # (event_cell_text, mix)
    for row in schedule_rows:
        if len(row) <= need:
            continue
        if _parse_date(row[cols["date"]]) != show_date:
            continue
        mix = (row[cols["mix"]] or "").strip()
        if not mix:
            continue
        staffed.append(((row[ev_col] or "") if ev_col is not None else "", mix))
    if not staffed:
        return None

    raw_mix = _pick_staffed_row(staffed, series, event_name, artist_name,
                                event_start)
    if not raw_mix:
        return None

    return _split_mix_cell(raw_mix), codes_rows


def _event_time(tok):
    """One side of an Event-cell range ('*4:15', '10', '9a', '11am') -> house
    time '4:15p'. An explicit a/am or p/pm is honored (audit cleanup — a
    daytime event used to get a 9:00p crew call); with no suffix, PM is
    assumed (Brian, 2026-09-11: evening shows are the norm)."""
    tok = re.sub(r"[*\s]", "", tok).lower()
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?(am|pm|a|p)?", tok)
    if not m:
        return None
    suffix = "a" if (m.group(3) or "").startswith("a") else "p"
    return f"{int(m.group(1))}:{int(m.group(2) or 0):02d}{suffix}"


def event_times_for(venue, show_date, series=None):
    """{'crew_call','curfew'} for this venue+date, read from the staffing
    sheet's Event cell — the '<Event> (<crew>-<curfew>)' pattern (Brian,
    2026-09-11, all sites; e.g. 'Jazz (3:30-10)' -> crew 3:30p, curfew 10:00p).
    Both times PM. When `series` is given and a date has more than one event
    row, the row whose Event cell names that series wins (so a double-booked day
    doesn't hand back the wrong show's times); otherwise the first parseable row
    is used. None if the venue isn't wired, the sheet is unreachable, the date
    isn't on it, or no row has a (start-end) range — callers fall back to their
    computed schedule."""
    cols = SCHEDULE_COLUMNS.get(venue)
    if not cols or not show_date:
        return None
    if isinstance(show_date, str):
        try:
            show_date = dt.date.fromisoformat(show_date)
        except ValueError:
            return None
    try:
        rows = _fetch_csv(SCHEDULE_GID)
    except Exception as e:  # noqa: BLE001 — sheet down isn't fatal
        print(f"[staffing] fetch failed: {e!r}", flush=True)
        return None
    ev_col = cols["event"]
    need = max(cols.values())
    target = (series or "").strip().lower()
    first = None
    for row in rows:
        if len(row) <= need:
            continue
        if _parse_date(row[cols["date"]]) != show_date:
            continue
        cell = (row[ev_col] or "").strip()
        if not cell:
            continue
        line = cell.splitlines()[0]
        paren = re.search(r"\(([^)]*)\)", line)
        if not paren:
            continue
        rng = re.search(
            r"(\*{0,2}\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)\s*-\s*"
            r"(\*{0,2}\d{1,2}(?::\d{2})?\s*(?:am|pm|a|p)?)",
            paren.group(1), re.I)
        if not rng:
            continue
        crew, curfew = _event_time(rng.group(1)), _event_time(rng.group(2))
        if not (crew and curfew):
            continue
        rec = {"crew_call": crew, "curfew": curfew}
        # prefer the row whose Event name matches the show's series on a
        # multi-event day; otherwise keep the first parseable row.
        if target and target in line.lower():
            return rec
        if first is None:
            first = rec
    return first


def engineer_for(venue, show_date, series=None, event_name=None,
                 artist_name=None, event_start=None):
    """'Gyasi Henderson (513-313-2431)' for the FOH engineer staffed on
    show_date at venue — or None if the venue isn't wired, the sheet is
    unreachable, the date isn't staffed yet, or the mix cell doesn't cleanly
    resolve to 1 or 2 codes (a 3+-name staggered-shift cell isn't guessed at
    here either — same rule as engineers_for()). When the cell has two codes
    (FOH/Mon), this is the first (FOH) one; see engineers_for() for both.
    `series` / `event_name` / `artist_name` / `event_start` pick the right
    row on a double-booked day; if none does, None rather than a guess."""
    found = _mix_tokens(venue, show_date, series, event_name,
                        artist_name, event_start)
    if not found:
        return None
    tokens, codes_rows = found
    if len(tokens) not in (1, 2):
        return None
    return _format_row(_resolve_row(tokens[0], codes_rows), with_cell=True)


def engineers_for(venue, show_date, series=None, event_name=None,
                  artist_name=None, event_start=None):
    """{'foh': 'First Last', 'mon': 'First Last'} (either may be None) for the
    show staffed on show_date at venue. One set of initials in the Mix column
    is FOH only — Mon stays None, for staff to fill by hand (Brian,
    2026-09-08); two is FOH then Mon. A cell with zero, three-plus, or an
    unconfirmed ('?') token resolves to nothing rather than guess. Never
    raises. `series` / `event_name` / `artist_name` / `event_start` pick the
    right row on a double-booked day; if none does, empty rather than a
    guess."""
    empty = {"foh": None, "mon": None}
    found = _mix_tokens(venue, show_date, series, event_name,
                        artist_name, event_start)
    if not found:
        return empty
    tokens, codes_rows = found
    if len(tokens) not in (1, 2):
        return empty
    foh = _format_row(_resolve_row(tokens[0], codes_rows))
    mon = _format_row(_resolve_row(tokens[1], codes_rows)) if len(tokens) == 2 else None
    return {"foh": foh, "mon": mon}


# ── every other role: Tech / Stagehand / Stage Support / Other ─────────────
# Mix keeps engineer_for()/engineers_for() exactly as they are above (real
# code, real doc, don't touch) — the roles below are additive, read-only,
# and don't share a code path with them, so there's no regression risk to
# the already-verified Mix behavior.

def _row_for(venue, show_date):
    """(row, cols, codes_rows) for the schedule-sheet row matching
    venue/show_date — or None if the venue isn't wired, the sheet is
    unreachable, or no row for that date has ANY real content. Unlike the
    Mix-only _mix_tokens(), a row counts as 'the real one' if ANY column in
    that venue's block is filled in (event name, Mix, or any other role) —
    a blank filler row for an unstaffed day is skipped the same way, but a
    row where only e.g. Stagehand got filled in (Mix still blank) is still
    found. When more than one row for the date has real content (two
    events same day), still just takes the first — same already-flagged,
    deliberately-deferred gap as Mix has."""
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
    for row in schedule_rows:
        if len(row) <= need:
            continue
        if _parse_date(row[cols["date"]]) != show_date:
            continue
        has_content = any((row[c] or "").strip() for k, c in cols.items() if k != "date")
        if has_content:
            return row, cols, codes_rows
    return None


def _format_row_or_raw(token, codes_rows):
    """Resolved name if the code/first-name matches, otherwise the raw token
    itself (Brian, 2026-09-10: for the crew email, an unrecognized letter
    sequence should still show up rather than silently vanish — 'we can
    manually figure out what that is'). Day-sheet paperwork stays on the
    stricter _format_row(_resolve_row(...)) path — this fallback is only
    for staff_for()'s crew-report/digest email output."""
    name = _format_row(_resolve_row(token, codes_rows))
    return name if name else token


def _resolve_names(tokens, codes_rows):
    """Every token, resolved to a real person where possible — otherwise the
    raw code itself, so it's visible instead of silently dropped. Unlike
    Mix, a non-mix role has no positional meaning (no FOH-vs-Mon to
    preserve), so there's no 'exactly 1 or 2' gate: every token in the cell
    comes back as something. Zero names back (an empty cell) is still a
    normal, common answer — most roles are blank most days."""
    return [_format_row_or_raw(t, codes_rows) for t in tokens]


def staff_for(venue, show_date):
    """Every staffing role assigned for the show at venue/show_date, straight
    from the sheet's own Mix/Tech/Stagehand/Stage Support/Other columns
    (Brian, 2026-09-09: 'teach yourself the other positions'). Returns
    {'mix': {'foh':.., 'mon':..}, 'tech': [...], 'stagehand': [...],
    'stage_support': [...], 'other': [...]} — mix keeps its FOH/Mon split
    (see engineers_for()); every other role is just a list of whoever's
    real name resolves, in the order the cell lists them. A venue whose
    sheet block merges Stagehand and Stage Support into one column
    (Zeigler Park / Court Street Plaza / Imagination Alley / Elm Street
    Plaza) reports that same list under BOTH 'stagehand' and
    'stage_support' — the source data doesn't distinguish them there, so
    this doesn't invent a split. Never raises."""
    empty = {"mix": {"foh": None, "mon": None}, "tech": [], "stagehand": [],
             "stage_support": [], "other": []}
    found = _row_for(venue, show_date)
    if not found:
        return empty
    row, cols, codes_rows = found

    out = dict(empty)
    mix_tokens = _split_mix_cell((row[cols["mix"]] or "").strip()) if cols.get("mix") is not None else []
    if len(mix_tokens) in (1, 2):
        out["mix"] = {
            "foh": _format_row_or_raw(mix_tokens[0], codes_rows),
            "mon": _format_row_or_raw(mix_tokens[1], codes_rows) if len(mix_tokens) == 2 else None,
        }

    for key in _OTHER_ROLE_KEYS:
        col = cols.get(key)
        if col is None:
            continue
        names = _resolve_names(_split_mix_cell((row[col] or "").strip()), codes_rows)
        if key == "stagehand_support":
            out["stagehand"] = names
            out["stage_support"] = names
        else:
            out[key] = names
    return out
