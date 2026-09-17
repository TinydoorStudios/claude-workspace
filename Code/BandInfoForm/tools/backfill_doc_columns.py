#!/usr/bin/env python3
"""One-off (root cause B, audit 2026-09-16): give every upcoming filed doc its
column map and move its provenance onto artist keys.

For each filed_docs row with event_date >= today and an empty `columns`:
  - read the doc's own act-name header and match each column's name to an
    artist (docmerge.header_column_map — the bill's acts, then any artist on
    file by match_key)
  - rewrite `cells` keys `Section|colN[|i]` -> `Section|a<artist_id>[|i]` for
    the columns that matched
  - rewrite the cell_key of that doc's OPEN notices the same way, so "Keep doc"
    / "Use new" / supersede all land on the artist's key

Never touches a .docx. Safe to re-run: rows that already have a map are
skipped. --dry-run prints what it would do and writes nothing.

    python3 backfill_doc_columns.py [--dry-run]
"""
import argparse
import datetime as dt
import json
import re
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

from docx import Document

COL_KEY = re.compile(r"^(.*)\|col([123])(\|\d+)?$")


def rekey(key, cols):
    m = COL_KEY.match(key or "")
    if not m or m.group(1) in ("Act names", "") or cols.get(int(m.group(2))) is None:
        return key
    return f"{m.group(1)}|a{cols[int(m.group(2))]}{m.group(3) or ''}"


def acts_for(cur, venue, date):
    cur.execute("SELECT id FROM events WHERE venue=%s AND event_date=%s", (venue, date))
    acts = []
    for e in cur.fetchall():
        acts += db.event_acts(cur, e["id"])
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT * FROM filed_docs WHERE event_date >= %s
                       ORDER BY event_date, venue""", (dt.date.today(),))
        rows = cur.fetchall()
        done = 0
        for reg in rows:
            label = f"{reg['venue']} {reg['event_date']} {Path(reg['path']).name}"
            if reg.get("columns"):
                print(f"  have map   {label}")
                continue
            path = docmerge._abs_from_reg(reg["path"])
            if not path.exists():
                print(f"  ! missing  {label}")
                continue
            try:
                doc = Document(str(path))
            except Exception as e:  # noqa: BLE001
                print(f"  ! unreadable {label}: {e!r}")
                continue
            cols = docmerge.header_column_map(doc, acts_for(cur, reg["venue"], reg["event_date"]))
            cells = {rekey(k, cols): v for k, v in (reg["cells"] or {}).items()}
            moved = sum(1 for k in (reg["cells"] or {}) if rekey(k, cols) != k)
            cur.execute("""SELECT id, cell_key FROM doc_notices WHERE venue=%s AND event_date=%s
                           AND event_key=%s AND resolved_at IS NULL AND cell_key IS NOT NULL""",
                        (reg["venue"], reg["event_date"], reg["event_key"]))
            notices = [(n["id"], n["cell_key"], rekey(n["cell_key"], cols)) for n in cur.fetchall()]
            notices = [n for n in notices if n[1] != n[2]]
            print(f"  map {json.dumps(cols)}  {moved} cell key(s), {len(notices)} open notice(s)  {label}")
            for nid, old, new in notices:
                print(f"      notice {nid}: {old} -> {new}")
            if args.dry_run:
                continue
            cur.execute("UPDATE filed_docs SET columns=%s::jsonb, cells=%s::jsonb WHERE id=%s",
                        (json.dumps({str(k): v for k, v in cols.items()}), json.dumps(cells), reg["id"]))
            for nid, _old, new in notices:
                cur.execute("UPDATE doc_notices SET cell_key=%s WHERE id=%s", (new, nid))
            done += 1
        if not args.dry_run:
            conn.commit()
    print(f"{'would back-fill' if args.dry_run else 'back-filled'} "
          f"{done if not args.dry_run else sum(1 for r in rows if not r.get('columns'))} doc(s)")


if __name__ == "__main__":
    main()
