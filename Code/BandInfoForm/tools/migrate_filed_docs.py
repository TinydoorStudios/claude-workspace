#!/usr/bin/env python3
"""One-time (2026-09-13 audit #2): adopt every current show's existing filed
advance doc into the `filed_docs` registry and rename it to the new
"<event/series> - <headliner>" filename IN PLACE — content untouched, never a
second copy. Past shows are left completely alone (their recap extraction
already references the old names).

Dry run by default; --apply to rename + register. Sends nothing.

  python3 migrate_filed_docs.py            # plan
  python3 migrate_filed_docs.py --apply
"""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import docmerge
import fieldspec as fs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    today = dt.date.today()
    problems = 0

    with db.get_conn() as conn, conn.cursor() as cur:
        events = db.list_events(cur)
        per_day = {}
        for e in events:
            per_day[(e["venue"], e["event_date"])] = per_day.get((e["venue"], e["event_date"]), 0) + 1
        loaded = [(db.get_event(cur, e["id"]), db.event_acts(cur, e["id"])) for e in events]

    for ev, acts in sorted(loaded, key=lambda x: (x[0].get("event_date") or dt.date.min)):
        d, venue = ev.get("event_date"), ev.get("venue")
        if not d or d < today:
            continue
        folder = fs.real_dropbox_root() / fs.real_venue_folder(venue) / fs.real_month_folder(venue, d)
        desired = folder / f"{fs.advance_stem(fs.event_display_name(ev, acts), d)}.docx"
        old_base = folder / f"{fs.advance_stem(ev.get('name') or ev.get('series') or '', d)}.docx"
        key = docmerge.event_key(ev)
        cands = sorted(folder.glob(f"{d.strftime('%m%d%y')} * Prod Adv.docx")) if folder.exists() else []

        with db.get_conn() as conn, conn.cursor() as cur:
            reg = db.get_filed_doc(cur, venue, d, key)
        if reg:
            print(f"  registered already  {d} {venue}: {reg['path']}")
            continue

        if desired.exists():
            src = desired
        elif old_base.exists():
            src = old_base
        elif len(cands) == 1 and per_day.get((venue, d), 1) == 1:
            src = cands[0]
        elif not cands:
            print(f"  no doc yet          {d} {venue}: will be created on its next run -> {desired.name}")
            continue
        else:
            print(f"  ! AMBIGUOUS         {d} {venue}: {[c.name for c in cands]} — not touched")
            problems += 1
            continue

        if docmerge.word_lock_present(src):
            print(f"  ! OPEN IN WORD      {d} {venue}: {src.name} — not touched, re-run later")
            problems += 1
            continue

        rename = src.name != desired.name
        if rename and desired.exists():
            print(f"  ! TARGET EXISTS     {d} {venue}: {desired.name} — not touched")
            problems += 1
            continue
        print(f"  {'rename + register' if rename else 'register         '} {d} {venue}: "
              f"{src.name}" + (f"  ->  {desired.name}" if rename else ""))
        if args.apply:
            sha = docmerge.sha256_file(src)
            if rename:
                os.rename(src, desired)
            with db.get_conn() as conn, conn.cursor() as cur:
                db.upsert_filed_doc(cur, venue, d, key, docmerge._rel_to_root(desired), sha, seeded=True)
                conn.commit()

    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'} — {problems} item(s) need a look.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
