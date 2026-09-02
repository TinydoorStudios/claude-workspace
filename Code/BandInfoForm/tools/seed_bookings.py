#!/usr/bin/env python3
"""VM side of staff-booking seeding.

  seed_bookings.py --json          # print bookings not yet in the sheet (JSON)
  seed_bookings.py --seed 1,2,3    # stamp those booking ids as seeded

generate.command fetches the JSON, appends the rows to the local spreadsheet
(append_bookings.py), then calls --seed so they never re-append.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db


def main():
    args = sys.argv[1:]
    if "--json" in args:
        with db.get_conn() as conn, conn.cursor() as cur:
            rows = db.unseeded_bookings(cur)
        print(json.dumps(rows, default=str))
    elif "--seed" in args:
        i = args.index("--seed")
        ids = [int(x) for x in args[i + 1].split(",") if x.strip().isdigit()]
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_bookings_seeded(cur, ids)
        conn.commit()
        print(f"seeded {len(ids)} booking(s)", file=sys.stderr)
    else:
        print("usage: seed_bookings.py --json | --seed <ids>", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
