#!/usr/bin/env python3
"""Import a RiffPay bookings CSV into the Advance List spreadsheet.

RiffPay is the web booking portal's export. This tool is the bridge from that
export into the existing advance pipeline: it filters the export down to the
bookings we actually advance, groups them into events, and writes advance-list
rows that `package_run.py` / `import_sheet.py` / `draft_emails.py` consume
UNCHANGED. It stops at the spreadsheet — the DB upsert, the request emails and
the day-sheets are the VM pipeline's job (generate.command / run_now.py).

RiffPay CSV columns:
    Date, Time, Location, Booking Name, Status, Talent / Applicant,
    Contact Email, Contact Phone

Mapping (Brian, 2026-09-11):
  - Location  -> the venue. ONLY "Washington Park" is processed for now.
  - Booking Name -> the SERIES; the series also fixes the WP sub-venue stage:
        Neo Soul Nights -> Bandstand,  Blues & Brews -> Porch.
  - Status -> only "Confirmed" is processed (anything else isn't confirmed).
  - Talent / Applicant -> the band (artist) name.
  - Contact Email -> contact email.   Contact Phone -> contact phone if present.
  - Contact name is no longer required.
  - Only bookings dated TODAY or later are processed.
  - Same date + series = ONE event; bands become acts, slotted by set time:
        earliest = opener ... latest = headliner.
  - Event Name = "<Series> - <headliner band>".

Cancelled-event reconciliation is deliberately NOT handled here yet (a later
pass). Other venues open up by adding them to LOCATION_VENUES + SERIES_STAGE.

Usage:
  python3 import_riffpay.py riffpay.csv                 # preview only (no writes)
  python3 import_riffpay.py riffpay.csv --sheet X.xlsx --apply
  python3 import_riffpay.py riffpay.csv --today 2026-09-11   # pin "today"
"""
import argparse
import csv
import datetime as dt
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fieldspec as fs

# ── config: what we process, and how a series maps to a WP stage ──────────────
# Only these CSV Location values are processed, each normalized to a pipeline
# venue name. WP only for now — add a row here to open another site.
LOCATION_VENUES = {
    "washington park": "Washington Park",
}
STATUSES = {"confirmed"}  # only Confirmed bookings are real bookings

# Raw Booking Name (normalized) -> canonical series name.
SERIES_CANON = {
    "neo soul nights": "Neo Soul Nights",
    "neo soul night": "Neo Soul Nights",
    "neosoul night": "Neo Soul Nights",
    "neosoul nights": "Neo Soul Nights",
    "blues & brews": "Blues & Brews",
    "blues and brews": "Blues & Brews",
}
# Canonical series -> WP sub-venue stage (fieldspec Location choices).
SERIES_STAGE = {
    "Neo Soul Nights": "Bandstand",
    "Blues & Brews": "Porch",
}

SLOTS_BY_COUNT = {
    1: ["headliner"],
    2: ["opener", "headliner"],
    3: ["opener", "direct_support", "headliner"],
}
INPUT_SHEET = "Advance List"


def norm(v):
    return re.sub(r"\s+", " ", str(v or "").strip()).lower()


def _s(v):
    return "" if v is None else str(v).strip()


def parse_date(s):
    s = _s(s)
    for fmt in ("%a, %b %d, %Y", "%A, %B %d, %Y", "%b %d, %Y", "%B %d, %Y",
                "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_time(s):
    s = _s(s)
    for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
        try:
            return dt.datetime.strptime(s.upper().replace(".", ""), fmt).time()
        except ValueError:
            continue
    return None


def fmt_time(t):
    if not t:
        return ""
    return t.strftime("%-I:%M %p") if hasattr(t, "strftime") else ""


def house_time(t):
    """House schedule format: 6:00 PM -> '6:00p', 9:30 AM -> '9:30a'."""
    if not t:
        return ""
    s = t.strftime("%-I:%M%p").lower()   # '6:00pm'
    return s[:-1]                        # drop the trailing 'm' -> '6:00p'


def shift(base_date, t, minutes):
    """t shifted by +/- minutes, wrapped with base_date so it crosses the hour."""
    if not t:
        return None
    return (dt.datetime.combine(base_date, t) + dt.timedelta(minutes=minutes)).time()


# Standard day, all offsets in minutes from the headliner's show start (Brian,
# 2026-09-11): crew call -2:00, load-in -1:00, sound check -0:30, start = show
# time, set is 3:00 long so end = +3:00, and curfew is 1:00 after the set ends
# (+4:00). Crew call has no band-facing advance field, so it's computed for the
# record / staffing use but not written to the email schedule.
SCHED_OFFSETS = {"crew_call": -120, "load_in": -60, "soundcheck": -30,
                 "event_end": 180, "curfew": 240}


# ── read + filter the RiffPay export ──────────────────────────────────────────
def load_rows(csv_path, today):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        raw = list(csv.DictReader(f))
    kept, skipped = [], {"location": 0, "status": 0, "past": 0, "baddate": 0,
                         "no_series": 0, "no_band": 0}
    for r in raw:
        venue = LOCATION_VENUES.get(norm(r.get("Location")))
        if not venue:
            skipped["location"] += 1
            continue
        if norm(r.get("Status")) not in STATUSES:
            skipped["status"] += 1
            continue
        d = parse_date(r.get("Date"))
        if not d:
            skipped["baddate"] += 1
            continue
        if d < today:
            skipped["past"] += 1
            continue
        band = _s(r.get("Talent / Applicant"))
        if not band:
            skipped["no_band"] += 1
            continue
        canon = SERIES_CANON.get(norm(r.get("Booking Name")))
        if not canon:
            skipped["no_series"] += 1
            print(f"  ! unknown series {r.get('Booking Name')!r} for {band} "
                  f"({d}) — skipped; add it to SERIES_CANON", file=sys.stderr)
            continue
        kept.append({
            "venue": venue,
            "series": canon,
            "location": SERIES_STAGE.get(canon, ""),
            "date": d,
            "time": parse_time(r.get("Time")),
            "artist_name": band,
            "contact_email": _s(r.get("Contact Email")),
            "contact_phone": _s(r.get("Contact Phone")),
        })
    return kept, skipped


# ── group into events; slot by set time ───────────────────────────────────────
def build_events(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["date"], r["series"], r["venue"]), []).append(r)

    events = []
    for (d, series, venue), acts in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        # order by set time (times unknown sort last but stable)
        acts.sort(key=lambda a: (a["time"] is None, a["time"] or dt.time(0, 0)))
        n = len(acts)
        slots = SLOTS_BY_COUNT.get(n)
        if slots is None:
            print(f"  ! {series} @ {venue} {d}: {n} bands exceeds the 3-slot "
                  f"model — first=opener, last=headliner, middles=direct_support",
                  file=sys.stderr)
            slots = ["opener"] + ["direct_support"] * (n - 2) + ["headliner"]
        headliner = acts[-1]["artist_name"]
        # The production day is worked backward from the HEADLINER's set time —
        # the latest act (Brian, 2026-09-11). For a single-band night that's the
        # only act; on a multi-band night an earlier slot is a DJ / warm-up that
        # doesn't drive the day, so we anchor on the headliner (e.g. Neo Soul
        # anchors on the 6PM band, not the 5PM DJ). Offsets: crew -2:00, load-in
        # -1:00, soundcheck -0:30, start = the anchor.
        # NOTE: this assumes earlier slots don't need their own load-in. A real
        # opener BAND playing before the headliner would need its own timing —
        # revisit when that case actually appears.
        sched = {k: "" for k in ("event_start", "soundcheck", "load_in",
                                 "crew_call", "event_end", "curfew")}
        anchor = acts[-1]["time"]
        if anchor:
            sched = {
                "event_start": house_time(anchor),
                "soundcheck": house_time(shift(d, anchor, SCHED_OFFSETS["soundcheck"])),
                "load_in": house_time(shift(d, anchor, SCHED_OFFSETS["load_in"])),
                "crew_call": house_time(shift(d, anchor, SCHED_OFFSETS["crew_call"])),
                "event_end": house_time(shift(d, anchor, SCHED_OFFSETS["event_end"])),
                "curfew": house_time(shift(d, anchor, SCHED_OFFSETS["curfew"])),
            }
        events.append({
            "event_name": f"{series} - {headliner}",
            "event_date": d.isoformat(),
            "venue": venue,
            "location": acts[0]["location"],
            "series": series,
            "band_count": str(n),
            "event_start": sched["event_start"],
            "soundcheck": sched["soundcheck"],
            "load_in": sched["load_in"],
            "crew_call": sched["crew_call"],
            "event_end": sched["event_end"],
            "curfew": sched["curfew"],
            "acts": [dict(a, slot=slots[i]) for i, a in enumerate(acts)],
        })
    return events


# ── write rows into the advance-list sheet (by label; dedup) ──────────────────
def find_header_row(ws):
    labels = {lbl.lower() for (lbl, _k, _c) in fs.ALL_COLUMNS}
    best_row, best = 2, 0
    for r in range(1, 8):
        hits = sum(1 for c in ws[r] if _s(c.value).lower() in labels)
        if hits > best:
            best, best_row = hits, r
    return best_row


def act_to_cells(ev, act):
    """Flatten one act into internal-key -> value for the sheet."""
    return {
        "event_name": ev["event_name"],
        "event_date": ev["event_date"],
        "venue": ev["venue"],
        "location": ev["location"],
        "series": ev["series"],
        "band_count": ev["band_count"],
        "load_in": ev["load_in"],
        "soundcheck": ev["soundcheck"],
        "event_start": ev["event_start"],
        "event_end": ev["event_end"],
        "curfew": ev["curfew"],
        # crew_call is derived (start -2:00) but has no advance-doc field — it's
        # a staffing/crew figure, not band-facing, so it isn't written here.
        "slot": act["slot"],
        "artist_name": act["artist_name"],
        "contact_email": act["contact_email"],
        "contact_phone": act["contact_phone"],
    }


def write_sheet(sheet_path, events, apply):
    from openpyxl import load_workbook
    wb = load_workbook(sheet_path)
    ws = wb[INPUT_SHEET] if INPUT_SHEET in wb.sheetnames else wb.worksheets[0]
    hrow = find_header_row(ws)
    key_col = {}
    missing_labels = []
    for lbl, key, _c in fs.ALL_COLUMNS:
        col = next((c for c in range(1, ws.max_column + 1)
                    if _s(ws.cell(hrow, c).value) == lbl), None)
        if col:
            key_col[key] = col
    for need in ("location", "band_count"):
        if need not in key_col:
            missing_labels.append(need)
    if missing_labels:
        print(f"  ! target sheet is missing columns for {missing_labels} — "
              f"those values won't be written. Refresh it from "
              f"tools/lists/advance_list_template.xlsx.", file=sys.stderr)

    c_artist = key_col.get("artist_name")
    c_venue = key_col.get("venue")
    c_date = key_col.get("event_date")
    # existing identities (artist, venue, date) already in the sheet
    existing, last = set(), hrow
    for r in range(hrow + 1, ws.max_row + 1):
        a = _s(ws.cell(r, c_artist).value)
        if a:
            last = r
            existing.add((norm(a),
                          norm(ws.cell(r, c_venue).value) if c_venue else "",
                          _s(ws.cell(r, c_date).value)[:10] if c_date else ""))

    appended, dup = 0, 0
    row = last + 1
    for ev in events:
        for act in ev["acts"]:
            cells = act_to_cells(ev, act)
            ident = (norm(cells["artist_name"]), norm(cells["venue"]),
                     cells["event_date"][:10])
            if ident in existing:
                dup += 1
                continue
            for key, val in cells.items():
                col = key_col.get(key)
                if col and val not in (None, ""):
                    ws.cell(row, col).value = val
            existing.add(ident)
            row += 1
            appended += 1

    if apply and appended:
        wb.save(sheet_path)
    return appended, dup


def preview(events):
    print(f"\n{len(events)} event(s):\n")
    for ev in events:
        print(f"  {ev['event_date']}  {ev['event_name']}")
        print(f"     venue={ev['venue']}  stage={ev['location'] or '(?)'}  "
              f"series={ev['series']}  bands={ev['band_count']}")
        if ev["event_start"]:
            print(f"     schedule: crew {ev['crew_call']} · load-in {ev['load_in']} · "
                  f"soundcheck {ev['soundcheck']} · start {ev['event_start']} · "
                  f"end {ev['event_end']} · curfew {ev['curfew']}"
                  + ("  (anchored on headliner; earlier slots are DJ/warm-up)"
                     if int(ev["band_count"]) > 1 else ""))
        for a in ev["acts"]:
            print(f"       - {a['slot']:14} {a['artist_name']:24} "
                  f"{fmt_time(a['time']) or '(no time)':9} {a['contact_email']}"
                  + (f"  {a['contact_phone']}" if a['contact_phone'] else ""))
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="RiffPay bookings CSV export")
    ap.add_argument("--sheet", type=Path,
                    help="advance-list .xlsx to append rows to")
    ap.add_argument("--today", help="pin today's date (YYYY-MM-DD); default = real today")
    ap.add_argument("--apply", action="store_true",
                    help="write rows to --sheet (default: preview only)")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else dt.date.today()
    rows, skipped = load_rows(args.csv, today)
    print(f"Processing bookings dated >= {today.isoformat()}")
    print(f"Kept {len(rows)} booking(s). Skipped: " +
          ", ".join(f"{k}={v}" for k, v in skipped.items() if v))
    events = build_events(rows)
    preview(events)

    if not args.sheet:
        print("(preview only — pass --sheet PATH [--apply] to write rows)")
        return
    appended, dup = write_sheet(args.sheet, events, args.apply)
    verb = "Wrote" if args.apply else "Would write"
    print(f"{verb} {appended} new act row(s) to {args.sheet}"
          f"{'' if args.apply else ' (dry run — add --apply)'}; "
          f"{dup} already present.")


if __name__ == "__main__":
    main()
