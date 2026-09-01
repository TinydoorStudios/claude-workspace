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
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else (APP / "data")


def main():
    files = sorted(DATA.glob("*.json"))
    if not files:
        print(f"No submission JSON found in {DATA}")
        return
    loaded = skipped = failed = 0
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
        file_info = None
        if rec.get("stage_plot_file"):
            file_info = {"filename": rec["stage_plot_file"],
                         "stored_name": rec["stage_plot_file"]}
        try:
            a, s, sub = db.record_submission(rec, file_info=file_info, source="backfill")
            print(f"  loaded {f.name} -> artist {a}, show {s}, submission {sub}")
            loaded += 1
        except Exception as e:
            print(f"  FAIL {f.name}: {e}")
            failed += 1
    print(f"\nBackfill done: {loaded} loaded, {skipped} skipped (no band), {failed} failed.")


if __name__ == "__main__":
    main()
