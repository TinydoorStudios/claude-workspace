#!/usr/bin/env python3
"""Import the Advance List spreadsheet into events + acts.

Groups rows by Event Name + Date + Venue into events, upserts each band, and
assigns it to its slot (with set time). Idempotent — re-run after editing the
sheet and it updates in place. Emailing is separate (draft_emails.py).

  python3 import_sheet.py lists/advance_list_template.xlsx
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db
from sheet import read_advance_sheet
import fieldspec as fs

SLOTS = ("opener", "direct_support", "headliner")


def to_date(s):
    if not s:
        return None
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def get_or_create_event(cur, name, venue, event_date, series):
    cur.execute(
        """SELECT id FROM events
           WHERE COALESCE(name,'')=COALESCE(%s,'')
             AND COALESCE(venue,'')=COALESCE(%s,'')
             AND event_date IS NOT DISTINCT FROM %s""",
        (name, venue, event_date),
    )
    row = cur.fetchone()
    if row:
        return row["id"]
    return db.create_event(cur, name, venue, event_date, series=series)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet", help="advance list .xlsx")
    args = ap.parse_args()

    rows = read_advance_sheet(args.sheet)
    if not rows:
        print("No data rows found (only examples/blanks?).", file=sys.stderr)
        sys.exit(1)

    # group by (event_name, event_date, venue)
    groups = {}
    for r in rows:
        key = (r.get("event_name") or "", r.get("event_date") or "", r.get("venue") or "")
        groups.setdefault(key, []).append(r)

    events_made = acts_made = 0
    with db.get_conn() as conn:
        for (ename, edate, evenue), acts in groups.items():
            series = next((a.get("series") for a in acts if a.get("series")), None)
            # event-level details: first non-empty value across the group's rows
            details = {}
            for k in fs.EVENT_DETAIL_KEYS:
                v = next((a.get(k) for a in acts if a.get(k) not in (None, "")), None)
                if v is not None:
                    details[k] = v
            with conn.cursor() as cur:
                eid = get_or_create_event(cur, ename or None, evenue or None,
                                          to_date(edate), series)
                db.update_event_details(cur, eid, details)
                events_made += 1
                for a in acts:
                    slot = (a.get("slot") or "").strip().lower() or "headliner"
                    if slot not in SLOTS:
                        print(f"  ! bad slot '{slot}' for {a['artist_name']} — skipped")
                        continue
                    artist_id = db.upsert_artist(cur, a["artist_name"],
                                                 email=a.get("contact_email"))
                    # band-detail overrides typed into the sheet (non-empty only)
                    sheet_fields = {k: a[k] for k in fs.BAND_KEYS
                                    if a.get(k) not in (None, "")}
                    db.add_act(cur, eid, slot, artist_id, set_time=a.get("set_time"),
                               sheet_fields=sheet_fields)
                    acts_made += 1
            conn.commit()
            print(f"  event: {ename or '(unnamed)'} @ {evenue or '?'} {edate or '?'} "
                  f"— {len(acts)} act(s)")

    print(f"\nImported {events_made} event(s), {acts_made} act(s). "
          f"Generate a day-sheet with:  python3 daysheet.py --event <id>")
    print("List events:  python3 event.py list")


if __name__ == "__main__":
    main()
