#!/usr/bin/env python3
"""VM side of staff-booking seeding.

  seed_bookings.py --json          # print bookings not yet in the sheet (JSON)
  seed_bookings.py --seed 1,2,3    # stamp those booking ids as seeded
  seed_bookings.py --edited        # print bookings edited SINCE seeding (JSON)
  seed_bookings.py --synced 1,2,3  # stamp those as matching the sheet again
  seed_bookings.py --removals-json # print pending sheet removals (JSON)
  seed_bookings.py --removed 1,2,3 # stamp those applied + retire their orphaned docs

The caller fetches the JSON, writes the rows into the local spreadsheet
(append_bookings.py), then stamps them so they aren't handled twice. --edited /
--synced are the 2026-09-15 write-back: an edit made in the app has to reach the
sheet, or the next pipeline run rebuilds the bill from the old row.
--removals-json / --removed are root cause A (audit 2026-09-16): a purged or
merged-away show's sheet row is deleted before the rebuild, or it resurrects.
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

RETIRE_PREFIX = {"purge": "PURGED", "merge": "SUPERSEDED"}


def retire_doc(rel_path, reason):
    """Rename a filed doc that lost its last act to "PURGED - <name>" (or
    "SUPERSEDED - …" after a merge) in its own folder — out of every glob the
    pipeline matches (`MMDDYY * Prod Adv.docx`, the desired stem), never
    deleted. Returns the new path, or None when there's nothing to rename."""
    sys.path.insert(0, str(HERE))
    import fieldspec as fs
    p = Path(rel_path)
    if not p.is_absolute():
        p = fs.real_dropbox_root() / p
    if not p.exists():
        return None
    target = p.with_name(f"{RETIRE_PREFIX.get(reason, 'PURGED')} - {p.name}")
    n = 2
    while target.exists():
        target = p.with_name(f"{RETIRE_PREFIX.get(reason, 'PURGED')} ({n}) - {p.name}")
        n += 1
    p.rename(target)
    return target


def main():
    args = sys.argv[1:]
    if "--json" in args:
        with db.get_conn() as conn, conn.cursor() as cur:
            rows = db.unseeded_bookings(cur)
        print(json.dumps(rows, default=str))
    elif "--edited" in args:
        with db.get_conn() as conn, conn.cursor() as cur:
            rows = db.edited_bookings(cur)
        print(json.dumps(rows, default=str))
    elif "--synced" in args:
        i = args.index("--synced")
        ids = [int(x) for x in args[i + 1].split(",") if x.strip().isdigit()]
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_bookings_synced(cur, ids)
            conn.commit()
        print(f"synced {len(ids)} booking(s)", file=sys.stderr)
    elif "--removals-json" in args:
        with db.get_conn() as conn, conn.cursor() as cur:
            rows = db.pending_sheet_removals(cur)
        print(json.dumps(rows, default=str))
    elif "--removed" in args:
        i = args.index("--removed")
        ids = [int(x) for x in args[i + 1].split(",") if x.strip().isdigit()]
        with db.get_conn() as conn, conn.cursor() as cur:
            rows = db.mark_sheet_removals_applied(cur, ids)
            retired = []
            for r in rows:
                if not r.get("doc_path"):
                    continue
                try:
                    new = retire_doc(r["doc_path"], r["reason"])
                except OSError as e:
                    print(f"  ! couldn't rename {r['doc_path']}: {e!r}", file=sys.stderr)
                    continue
                if new:
                    print(f"  doc retired  {Path(r['doc_path']).name} -> {new.name}", file=sys.stderr)
                    retired.append((r, new))
            if retired:
                import mailer
                items = "".join(
                    f"<li>{mailer.esc(r['artist_name'] or '')} — {mailer.esc(r['venue'])} "
                    f"{r['event_date'].strftime('%m/%d')}: <b>{mailer.esc(new.name)}</b></li>"
                    for r, new in retired)
                db.queue_digest_item(
                    cur, "doc", f"Advance doc retired — {len(retired)}",
                    "<p>These filed docs lost their last act (show deleted, or merged into a "
                    "show that already had its own doc). Each was renamed in its own folder, "
                    "not deleted — carry over any hand edits you still need:</p>"
                    f"<ul>{items}</ul>")
            conn.commit()
        print(f"applied {len(rows)} sheet removal(s)", file=sys.stderr)
    elif "--seed" in args:
        i = args.index("--seed")
        ids = [int(x) for x in args[i + 1].split(",") if x.strip().isdigit()]
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_bookings_seeded(cur, ids)
            conn.commit()
        print(f"seeded {len(ids)} booking(s)", file=sys.stderr)
    else:
        print("usage: seed_bookings.py --json | --seed <ids> | --edited | --synced <ids> "
              "| --removals-json | --removed <ids>",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
