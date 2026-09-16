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
  - Same date + series = ONE event; every artist becomes an act carrying its
        OWN schedule, derived from its own set time. Position on the bill is
        Artist 1/2/3, read off those times downstream — earliest plays first.
  - Event Name = "<Series> - <last artist of the night>".

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


# Standard day, all offsets in minutes from an act's own set time (Brian,
# 2026-09-11): crew call -2:00, load-in -1:00, sound check -0:30, start = show
# time, set is 3:00 long so end = +3:00, and curfew is 1:00 after the last set
# ends (+4:00). Crew call has no band-facing advance field, so it's computed for
# the record / staffing use but not written to the email schedule.
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


# ── group into events; each act carries its own schedule ─────────────────────
def build_events(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["date"], r["series"], r["venue"]), []).append(r)

    events = []
    for (d, series, venue), acts in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        # order by set time (times unknown sort last but stable)
        acts.sort(key=lambda a: (a["time"] is None, a["time"] or dt.time(0, 0)))
        n = len(acts)
        top_of_bill = acts[-1]["artist_name"]
        # Every act gets its OWN load-in / sound check / start / end, worked off
        # its own set time (Brian, 2026-09-15). Until then the whole day was
        # anchored on the last act and that one schedule was copied onto every
        # act row — which, now that set start decides who is Artist 1, would
        # have given a 3-act bill three identical start times and no order at
        # all. An earlier act's set ends when the next one starts; the last act
        # gets the standard 3:00 set.
        # Crew call and curfew stay event-level: crew call is 1:00 before the
        # FIRST load-in of the day, curfew 1:00 after the last set ends.
        for i, a in enumerate(acts):
            t = a["time"]
            nxt = acts[i + 1]["time"] if i + 1 < n else None
            if not t:
                a.update({k: "" for k in ("load_in", "soundcheck", "event_start", "event_end")})
                continue
            end = nxt if nxt else shift(d, t, SCHED_OFFSETS["event_end"])
            a.update({
                "load_in": house_time(shift(d, t, SCHED_OFFSETS["load_in"])),
                "soundcheck": house_time(shift(d, t, SCHED_OFFSETS["soundcheck"])),
                "event_start": house_time(t),
                "event_end": house_time(end),
            })
        first_load_in = next((a["time"] for a in acts if a["time"]), None)
        anchor = acts[-1]["time"]
        sched = {k: "" for k in ("crew_call", "curfew")}
        if anchor:
            sched["curfew"] = house_time(shift(d, anchor, SCHED_OFFSETS["curfew"]))
        if first_load_in:
            sched["crew_call"] = house_time(shift(d, first_load_in, SCHED_OFFSETS["crew_call"]))
        events.append({
            "event_name": f"{series} - {top_of_bill}",
            "event_date": d.isoformat(),
            "venue": venue,
            "location": acts[0]["location"],
            "series": series,
            "artist_count": str(n),
            "crew_call": sched["crew_call"],
            "curfew": sched["curfew"],
            "acts": acts,
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
        "load_in": act.get("load_in", ""),
        "soundcheck": act.get("soundcheck", ""),
        "event_start": act.get("event_start", ""),
        "event_end": act.get("event_end", ""),
        "curfew": ev["curfew"],
        # crew_call is derived (first load-in -1:00) but has no advance-doc
        # field — a staffing/crew figure, not band-facing, so it isn't written.
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
    for need in ("location",):
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
              f"series={ev['series']}  artists={ev['artist_count']}")
        print(f"     crew call {ev['crew_call'] or '—'} · curfew {ev['curfew'] or '—'}")
        for i, a in enumerate(ev["acts"], 1):
            print(f"       - Artist {i:<3} {a['artist_name']:24} "
                  f"{fmt_time(a['time']) or '(no time)':9} {a['contact_email']}"
                  + (f"  {a['contact_phone']}" if a['contact_phone'] else ""))
            if a.get("event_start"):
                print(f"           load-in {a['load_in']} · soundcheck {a['soundcheck']} · "
                      f"set {a['event_start']}–{a['event_end']}")
    print()


def seed_bookings(events):
    """Create a `bookings` row per act so a RiffPay import is a true booking
    entry (Brian, 2026-09-11). The advance pipeline's email/lifecycle path reads
    location + schedule from `bookings` (shows LEFT JOIN bookings), so without
    this the auto-drafted email for a RiffPay show comes out with a null
    location and a generic schedule. Dedup on venue+date+artist (delete+insert),
    so re-running is idempotent. Needs the advance DB — run on the VM; best
    effort, warns and returns 0 if the DB isn't reachable (e.g. run from the Mac)."""
    for cand in (HERE.parent, HERE.parent / "app"):
        if (cand / "advance_db.py").exists():
            sys.path.insert(0, str(cand))
            break
    try:
        import advance_db as db
    except Exception as e:  # noqa: BLE001
        print(f"  ! advance_db not importable — bookings NOT seeded ({e})", file=sys.stderr)
        return 0
    n = 0
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            for ev in events:
                for act in ev["acts"]:
                    cur.execute(
                        "DELETE FROM bookings WHERE venue=%s AND event_date=%s AND artist_name=%s",
                        (ev["venue"], ev["event_date"], act["artist_name"]))
                    db.insert_booking(cur, {
                        "event_name": ev["event_name"], "event_date": ev["event_date"],
                        "venue": ev["venue"], "location": ev["location"],
                        "series": ev["series"],
                        "load_in": act.get("load_in", ""), "soundcheck": act.get("soundcheck", ""),
                        "event_start": act.get("event_start", ""),
                        "event_end": act.get("event_end", ""),
                        "curfew": ev["curfew"],
                        "artist_name": act["artist_name"],
                        "contact_email": act["contact_email"],
                        "entered_by": "riffpay-import",
                    })
                    n += 1
            conn.commit()
    except Exception as e:  # noqa: BLE001
        print(f"  ! bookings NOT seeded (DB unreachable?): {e}", file=sys.stderr)
        return 0
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="RiffPay bookings CSV export")
    ap.add_argument("--sheet", type=Path,
                    help="advance-list .xlsx to append rows to")
    ap.add_argument("--today", help="pin today's date (YYYY-MM-DD); default = real today")
    ap.add_argument("--apply", action="store_true",
                    help="write rows to --sheet (default: preview only)")
    ap.add_argument("--no-db", action="store_true",
                    help="skip seeding bookings into the DB (sheet only)")
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
    if args.apply and not args.no_db:
        seeded = seed_bookings(events)
        print(f"Seeded {seeded} booking row(s) into the DB.")


if __name__ == "__main__":
    main()
