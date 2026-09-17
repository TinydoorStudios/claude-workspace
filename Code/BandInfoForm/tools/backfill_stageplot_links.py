#!/usr/bin/env python3
"""One-off (2026-09-17): fix stage-plot hyperlinks in already-filed docs.

Every doc filed before today's daysheet.py fix carries its stage-plot link
as a bare relative filename ("091826%20Wishy%20stageplot.pdf") — Word
resolved it against "wherever the folder lives" on disk, which only works
with real local filesystem access next to the doc. Broken outright on a
phone, fragile even on desktop when Dropbox hadn't downloaded the sibling
file yet. New docs get the fix automatically (daysheet.set_cell_link now
writes a stable /stage-plot/<venue>/<date>/<file> URL); docmerge never
rewrites a doc whose visible cell text hasn't changed, so an already-filed
doc's stale relationship never gets touched by a normal pipeline run.

This script edits ONLY the hyperlink relationship XML (word/_rels/
document.xml.rels) — the external Target for any relationship that isn't
already a full URL — and never touches cell text, hand edits, or anything
else in the document. set_cell_link is the ONLY thing that ever writes a
relative-path external hyperlink into one of these docs, so any non-http
External relationship found here is unambiguously a stage-plot link.

    python3 backfill_stageplot_links.py [--dry-run]
"""
import argparse
import datetime as dt
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import fieldspec as fs

PUBLIC_URL = __import__("os").environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
REL_RE = re.compile(rb'(<Relationship[^>]*?TargetMode="External"[^>]*?Target=")([^"]*)("[^>]*/>)')


def fix_doc(path: Path, venue: str, event_date: dt.date, dry_run: bool) -> int:
    """Rewrites any non-http External relationship Target in place. Returns
    the number of links fixed (0 if the doc had none needing it)."""
    with zipfile.ZipFile(path) as z:
        rels_path = "word/_rels/document.xml.rels"
        if rels_path not in z.namelist():
            return 0
        rels = z.read(rels_path)
        names = z.namelist()
        infos = z.infolist()

    fixed = 0

    def repl(m):
        nonlocal fixed
        prefix, target, suffix = m.groups()
        target_s = target.decode("utf-8")
        if target_s.lower().startswith(("http://", "https://")):
            return m.group(0)
        fname = unquote(target_s)
        new_url = f"{PUBLIC_URL}/stage-plot/{quote(venue)}/{event_date.isoformat()}/{quote(fname)}"
        fixed += 1
        return prefix + new_url.encode("utf-8") + suffix

    new_rels = REL_RE.sub(repl, rels)
    if not fixed:
        return 0
    if dry_run:
        return fixed

    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".docx.tmp")
    Path(tmp_path).unlink()  # zipfile wants to create it itself
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            data = new_rels if info.filename == rels_path else zin.read(info.filename)
            zout.writestr(info, data)
    shutil.move(tmp_path, path)
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = fs.real_dropbox_root()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT venue, event_date, path FROM filed_docs WHERE event_date >= %s ORDER BY event_date",
                     (dt.date.today(),))
        rows = cur.fetchall()

    n_docs = n_links = 0
    for r in rows:
        p = root / r["path"]
        if not p.exists() or p.stat().st_size == 0:
            print(f"  ! skip (missing or online-only placeholder): {r['path']}")
            continue
        try:
            fixed = fix_doc(p, r["venue"], r["event_date"], args.dry_run)
        except (zipfile.BadZipFile, KeyError) as e:
            print(f"  ! {r['path']}: {e!r}")
            continue
        if fixed:
            n_docs += 1
            n_links += fixed
            tag = "would fix" if args.dry_run else "fixed"
            print(f"  {tag} {fixed} link(s): {r['path']}")

    print(f"{'would fix' if args.dry_run else 'fixed'} {n_links} stage-plot link(s) across {n_docs} doc(s)")


if __name__ == "__main__":
    main()
