#!/usr/bin/env python3
"""One-off (2026-09-17): fix stage-plot hyperlinks in already-filed docs.

Every doc filed before today's daysheet.py fix carries its stage-plot link
as a bare relative filename ("091826%20Wishy%20stageplot.pdf") — Word
resolved it against "wherever the folder lives" on disk, which only works
with real local filesystem access next to the doc. Broken outright on a
phone, fragile even on desktop when Dropbox hadn't downloaded the sibling
file yet. New docs get the fix automatically (daysheet.set_cell_link now
writes a real dropbox.com shared link, falling back to a stable app-served
/stage-plot/<venue>/<date>/<file> URL only when the Dropbox API call
fails); docmerge never rewrites a doc whose visible cell text hasn't
changed, so an already-filed doc's stale relationship never gets touched
by a normal pipeline run.

This script edits ONLY the hyperlink relationship XML (word/_rels/
document.xml.rels) — the external Target for any relationship that isn't
already a real (non-app-served) http(s) URL — and never touches cell
text, hand edits, or anything else in the document. set_cell_link is the
ONLY thing that ever writes one of these external hyperlinks, so any
matching relationship found here is unambiguously a stage-plot link. Also
upgrades an already-fixed app-served fallback link to a real Dropbox link
now that DROPBOX_* credentials exist, if one wasn't available yet the
first time this ran.

    python3 backfill_stageplot_links.py [--dry-run]
"""
import argparse
import datetime as dt
import shutil
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
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
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


FALLBACK_PREFIX = f"{PUBLIC_URL}/stage-plot/"


def _fname_needing_fix(target_s: str):
    """None if this Target is already a real (non-app-served) URL — nothing
    to do. Otherwise the plain stage-plot filename it should point at."""
    if target_s.startswith(FALLBACK_PREFIX):
        return unquote(target_s.rsplit("/", 1)[-1])
    if target_s.lower().startswith(("http://", "https://")):
        return None
    return unquote(target_s)


def fix_doc(path: Path, venue: str, event_date: dt.date, dry_run: bool) -> int:
    """Rewrites any relationship Target that isn't already a real URL in
    place — a bare relative filename, or the app-served fallback (upgraded
    to a real Dropbox link when one's available). Returns the number of
    links fixed (0 if the doc had none needing it).

    Finds the relationships to fix via a real XML parse (attribute order in
    python-docx's own output isn't guaranteed — Target before TargetMode in
    practice, not after), then does an exact literal substring replace of
    just each old Target="..." on the RAW bytes rather than re-serializing
    the tree, so everything else in the file — attribute order, quoting,
    whitespace — stays byte-identical."""
    with zipfile.ZipFile(path) as z:
        rels_path = "word/_rels/document.xml.rels"
        if rels_path not in z.namelist():
            return 0
        rels = z.read(rels_path)
        infos = z.infolist()

    root = ET.fromstring(rels)
    new_rels = rels
    fixed = 0
    for rel in root.findall(f"{{{RELS_NS}}}Relationship"):
        if rel.get("TargetMode") != "External":
            continue
        target_s = rel.get("Target") or ""
        fname = _fname_needing_fix(target_s)
        if fname is None:
            continue
        local_path = (fs.real_dropbox_root() / fs.real_venue_folder(venue) /
                      fs.real_month_folder(venue, event_date) / fname)
        new_url = fs.dropbox_shared_link(local_path) or (
            f"{FALLBACK_PREFIX}{quote(venue)}/{event_date.isoformat()}/{quote(fname)}")
        if new_url == target_s:
            continue
        old_attr = f'Target="{target_s}"'.encode("utf-8")
        if new_rels.count(old_attr) != 1:
            print(f"  ! {path.name}: Target attribute not uniquely matched, skipping this link ({target_s!r})")
            continue
        new_attr = f'Target="{new_url}"'.encode("utf-8")
        new_rels = new_rels.replace(old_attr, new_attr, 1)
        fixed += 1
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
