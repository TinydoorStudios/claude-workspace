#!/usr/bin/env python3
"""Replay disk-saved submissions into Postgres.

The form always saves each submission to disk first (data/*.json). This tool
walks those files and records any that aren't yet in the database — a safety net
if the DB was down when a submission came in, or for a first import. Idempotent:
re-running won't duplicate an artist (match_key) and skips files already loaded.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = None
for _cand in (HERE.parent, HERE.parent / "app"):  # deployed flat, or repo layout
    if (_cand / "advance_db.py").exists():
        APP = _cand
        sys.path.insert(0, str(APP))
        break
import advance_db as db

# where the deployed app keeps disk records; override with arg 1
DATA = APP / "data"


def _already_loaded(cur, rec):
    cur.execute("""SELECT 1 FROM submissions sub JOIN artists a ON a.id = sub.artist_id
                   WHERE sub.data->>'_submitted_at' = %s
                     AND (a.match_key = %s OR sub.data->>'band_name' = %s) LIMIT 1""",
                (rec.get("_submitted_at"), db.normalize(rec.get("band_name")), rec.get("band_name")))
    return cur.fetchone() is not None


def main():
    """Dry run by default (audit #22): lists what WOULD load. --apply loads
    only files not already in the database (matched on submit timestamp +
    band), so re-running never duplicates. Sends nothing."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", nargs="?", default=str(DATA))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    files = sorted(Path(args.data_dir).glob("*.json"))
    if not files:
        print(f"No submission JSON found in {args.data_dir}")
        return
    loaded = skipped = present = failed = 0
    for f in files:
        try:
            rec = json.loads(f.read_text())
        except Exception as e:
            print(f"  skip (unreadable) {f.name}: {e}")
            failed += 1
            continue
        if not rec.get("band_name"):
            skipped += 1
            continue
        with db.get_conn() as conn, conn.cursor() as cur:
            if _already_loaded(cur, rec):
                present += 1
                continue
        if not args.apply:
            print(f"  would load {f.name}")
            loaded += 1
            continue
        file_info = None
        if rec.get("stage_plot_file"):
            file_info = {"filename": rec["stage_plot_file"],
                         "stored_name": rec["stage_plot_file"]}
        try:
            res = db.record_submission(rec, file_info=file_info, source="backfill",
                                       resolve_booking=False, carry_plot=False)
            print(f"  loaded {f.name} -> artist {res['artist_id']}, show {res['show_id']}, "
                  f"submission {res['submission_id']}")
            loaded += 1
        except Exception as e:
            print(f"  FAIL {f.name}: {e}")
            failed += 1
    verb = "loaded" if args.apply else "would load"
    print(f"\nBackfill {'done' if args.apply else 'DRY RUN'}: {loaded} {verb}, {present} already in DB, "
          f"{skipped} skipped (no band), {failed} failed.")


if __name__ == "__main__":
    main()
