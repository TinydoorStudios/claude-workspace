#!/usr/bin/env python3
"""Event (bill) manager — group artist submissions into a day-sheet.

The advance form is per-artist; the day-sheet DOC is per-event and always has
three artist columns. This puts artists on a bill. Nothing assigns a position:
Artist 1/2/3 is derived from set start — earliest plays first — so adding an
artist with an earlier start renumbers the bill by itself.

  python3 event.py create --name "513 Airwaves w/ Inhaler" --venue "Fountain Square" --date 2026-09-20
  python3 event.py add-act --event 1 --artist "Buffalo Wabs and the Price Hill Hustle" --set-start 9:00pm
  python3 event.py add-act --event 1 --artist "The Cincy Suns" --set-start 7:00pm
  python3 event.py list
  python3 event.py show --event 1

Then generate the document with:  python3 daysheet.py --event 1
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


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def cmd_create(args):
    with db.get_conn() as conn, conn.cursor() as cur:
        eid = db.create_event(cur, args.name, args.venue, parse_date(args.date),
                              series=args.series)
        conn.commit()
    print(f"Created event {eid}: {args.name} @ {args.venue} {args.date}")
    print(f"Add acts:  python3 event.py add-act --event {eid} --artist \"...\" --set-start 9:00pm")


def cmd_add_act(args):
    if args.set_start and db.parse_clock(args.set_start) is None:
        print(f"couldn't read --set-start '{args.set_start}' — try 9:00pm", file=sys.stderr)
        sys.exit(1)
    with db.get_conn() as conn, conn.cursor() as cur:
        if not db.get_event(cur, args.event):
            print(f"No event {args.event}", file=sys.stderr); sys.exit(1)
        artist = db.find_artist_by_name(cur, args.artist)
        if not artist:
            print(f"No artist matching '{args.artist}'. Advance them first "
                  f"(draft_emails.py) or check the name.", file=sys.stderr)
            sys.exit(1)
        sub = db.newest_submission(cur, artist["id"])
        db.add_act(cur, args.event, artist["id"], submission_id=args.submission,
                   set_start=args.set_start, set_end=args.set_end,
                   load_in=args.load_in, soundcheck=args.soundcheck)
        conn.commit()
        acts = db.event_acts(cur, args.event)
    tag = "has a submission" if sub else "NO submission yet"
    place = next((db.artist_label(a["artist_order"]) for a in acts
                  if a.get("artist") and a["artist"]["id"] == artist["id"]), "unplaced")
    print(f"Event {args.event}: {place} = {artist['name']} ({tag})")


def cmd_list(args):
    with db.get_conn() as conn, conn.cursor() as cur:
        rows = db.list_events(cur)
    if not rows:
        print("No events yet."); return
    for e in rows:
        print(f"  [{e['id']}] {e['event_date'] or '?'}  {e['venue'] or '?':16} "
              f"{e['name'] or '(unnamed)'}  — {e['acts']} act(s)")


def cmd_show(args):
    with db.get_conn() as conn, conn.cursor() as cur:
        e = db.get_event(cur, args.event)
        if not e:
            print(f"No event {args.event}", file=sys.stderr); sys.exit(1)
        acts = db.event_acts(cur, args.event)
    print(f"Event {e['id']}: {e['name']}  @ {e['venue']}  {e['event_date']}")
    if not acts:
        print("  (no acts assigned)")
    for a in acts:
        who = a["artist"]["name"] if a.get("artist") else "(none)"
        sub = "submission ✓" if a.get("submission") else "no submission"
        when = a.get("set_start") or "no set time"
        print(f"  {db.artist_label(a['artist_order']):10} {when:>9}  {who}  [{sub}]")


def main():
    ap = argparse.ArgumentParser(description="Event/bill manager for day-sheets")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create"); c.set_defaults(fn=cmd_create)
    c.add_argument("--name", required=True); c.add_argument("--venue", required=True)
    c.add_argument("--date", required=True); c.add_argument("--series")

    a = sub.add_parser("add-act"); a.set_defaults(fn=cmd_add_act)
    a.add_argument("--event", type=int, required=True)
    a.add_argument("--artist", required=True)
    a.add_argument("--set-start", dest="set_start", help="e.g. 9:00pm — decides Artist 1/2/3")
    a.add_argument("--set-end", dest="set_end")
    a.add_argument("--load-in", dest="load_in")
    a.add_argument("--soundcheck")
    a.add_argument("--submission", type=int, default=None)

    l = sub.add_parser("list"); l.set_defaults(fn=cmd_list)
    s = sub.add_parser("show"); s.set_defaults(fn=cmd_show)
    s.add_argument("--event", type=int, required=True)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
