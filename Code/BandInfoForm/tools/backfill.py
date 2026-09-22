#!/usr/bin/env python3
"""Replay disk-saved submissions into Postgres.

The form always saves each submission to disk first (data/*.json). This tool
walks those files and records any that aren't yet in the database — a safety net
if the DB was down when a submission came in, or for a first import. Idempotent:
re-running won't duplicate an artist (match_key) and skips files already loaded.
It also skips a record that reached the DB once and was later purged/deleted
(a sheet_removals tombstone, or a `_db` stamp with no live submission) — pass
--include-deleted to replay the latter after restoring an older DB dump.
"""
import json
import sys
from datetime import datetime
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


def _was_deleted(rec):
    """2026-09-21 sweep (PIPE-8): app.py stamps `_db` only after record_submission
    succeeded, so a stamped record that _already_loaded() can't find was purged,
    wiped by hand, or lost to a restore from an older dump. Returns its old id."""
    stamp = rec.get("_db")
    if isinstance(stamp, dict) and stamp.get("submission_id"):
        return stamp["submission_id"]
    return None


def _tombstone(cur, rec):
    """2026-09-21 sweep (PIPE-8): the sheet_removals row purge_show/merge wrote for
    this band+venue+date AFTER this record was submitted (an older tombstone must
    not swallow a later re-booking). Applied rows count too — they persist."""
    try:
        submitted = datetime.fromisoformat(str(rec.get("_submitted_at") or ""))
    except ValueError:
        submitted = None
    d = db.to_date(rec.get("show_date"))
    if not submitted or not d:
        return None
    cur.execute("SELECT to_regclass('sheet_removals') IS NOT NULL AS ok")
    if not cur.fetchone()["ok"]:
        return None
    keys = {db.normalize(rec.get("band_name"))}
    stamp = rec.get("_db") if isinstance(rec.get("_db"), dict) else {}
    try:
        artist_id = int(stamp.get("artist_id") or 0)
    except (TypeError, ValueError):
        artist_id = 0
    if artist_id:
        # purge_show tombstones under the booked artist's match_key, which can
        # differ from the typed band name after an auto-attach
        cur.execute("SELECT match_key FROM artists WHERE id=%s", (artist_id,))
        row = cur.fetchone()
        if row and row["match_key"]:
            keys.add(row["match_key"])
    # _submitted_at is naive VM-local time; the session TZ is America/New_York
    cur.execute("""SELECT id, reason, created_at FROM sheet_removals
                   WHERE lower(venue) = lower(%s) AND event_date = %s
                     AND match_key = ANY(%s) AND created_at > %s::timestamp
                   ORDER BY id DESC LIMIT 1""",
                (rec.get("venue") or "", d, list(keys), submitted))
    return cur.fetchone()


def main():
    """Dry run by default (audit #22): lists what WOULD load. --apply loads
    only files not already in the database (matched on submit timestamp +
    band), so re-running never duplicates. Records that were in the DB once
    and have since been purged/deleted are skipped by default (PIPE-8);
    --include-deleted replays the non-tombstoned ones. Sends nothing."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", nargs="?", default=str(DATA))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--include-deleted", action="store_true",
                    help="also replay records that were in the DB once and have since been "
                         "deleted — only after restoring the DB from a dump older than data/")
    args = ap.parse_args()
    files = sorted(Path(args.data_dir).glob("*.json"))
    if not files:
        print(f"No submission JSON found in {args.data_dir}")
        return
    loaded = skipped = present = failed = deleted = 0
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
            # 2026-09-21 sweep (PIPE-8): never resurrect a purged show — a tombstone
            # skips even with --include-deleted; dry run lists the same skips.
            t = _tombstone(cur, rec)
            if t:
                print(f"  skip (removed by {t['reason']} #{t['id']} on "
                      f"{t['created_at']:%Y-%m-%d}) {f.name}")
                deleted += 1
                continue
            sid = _was_deleted(rec)
            if sid and not args.include_deleted:
                print(f"  skip (was in DB as submission {sid}, since deleted — "
                      f"pass --include-deleted to replay) {f.name}")
                deleted += 1
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
          f"{skipped} skipped (no band), {deleted} skipped (deleted from DB since), "
          f"{failed} failed.")


if __name__ == "__main__":
    main()
