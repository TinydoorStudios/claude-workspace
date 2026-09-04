#!/usr/bin/env python3
"""Build the advance filing tree from the advance list spreadsheet.

The single entrypoint generate.command runs on the VM. It rebuilds events+acts
from the sheet (form submissions are never touched), then files each event into
the venue tree under --out:

    <VenueAbbr>/<Year>/<MM Month>/
        <MMDDYY> <Event Name> advance.docx
        Email Drafts/
            <MMDDYY> <Event Name> email - <Band>.md      (one per act)
            <MMDDYY> <Event Name> followup - <Band>.md    (only if queued)
    status.json                                            (for the sheet's Status)

The Mac's generate.command OVERLAYS this into the Advancing/ folder (never
deletes) so the tree accumulates as a real archive. Nothing is ever sent — the
send step moves to Outlook, so generate no longer stamps email_sent_at.

  python3 package_run.py lists/_current.xlsx --out _package
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import daysheet
import fieldspec as fs
from draft_emails import slug  # same slug the drafts are named with

PY = sys.executable
DRAFTS = HERE / "drafts"
FOLLOWUPS = HERE / "followups"
UPLOADS = HERE.parent / "data" / "uploads"      # where the form stores stage plots


def run(*args):
    subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, check=True)


def safe(s):
    """Filesystem-safe, human-readable — keep spaces, drop path-hostile chars."""
    s = re.sub(r"[/\\:*?\"<>|]+", "-", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)


def event_dir(out, ev, acts):
    """<out>/<VenueAbbr>/<Year>/<MM Month>/ for this event."""
    venue = fs.venue_abbr(ev.get("venue"))
    d = ev.get("event_date")
    if d:
        return out / safe(venue) / str(d.year) / fs.month_folder(d)
    return out / safe(venue) / "No Date"


def event_stem(ev, acts):
    d = ev.get("event_date")
    name = ev.get("name") or ", ".join(
        a["artist"]["name"] for a in acts if a.get("artist")) or "Untitled"
    if d:
        return fs.advance_stem(name, d)
    return f"{safe(name)} advance"


def find_one(folder, pattern):
    hits = sorted(folder.glob(pattern))
    return hits[0] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--out", default="_package")
    args = ap.parse_args()

    out = (HERE / args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # 1. rebuild the event/act model from the sheet (submissions untouched)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE events, event_acts RESTART IDENTITY CASCADE;")
        conn.commit()
    run("import_sheet.py", args.sheet)

    # 2. regenerate the flat draft/day-sheet artifacts into their working dirs
    #    (no --mark-sent: sending is the Outlook step, not generation)
    for d in (DRAFTS, FOLLOWUPS, daysheet.FILLED):
        if d.exists():
            for f in d.glob("*"):
                if f.is_file():
                    f.unlink()
    run("draft_emails.py", args.sheet)
    run("dump_followups.py")
    run("status_sheet.py", "--json", str(out / "status.json"))

    # 3. file each event into the venue tree
    n_events = n_emails = n_followups = n_plots = 0
    plot_rels = {}   # (band, venue, date) -> relative path to the filed stage plot
    with db.get_conn() as conn, conn.cursor() as cur:
        for e in db.list_events(cur):
            eid = e["id"]
            ev = db.get_event(cur, eid)
            acts = db.event_acts(cur, eid)
            folder = event_dir(out, ev, acts)
            folder.mkdir(parents=True, exist_ok=True)
            stem = event_stem(ev, acts)
            n_events += 1

            # download + file each band's stage plot next to the advance doc,
            # renamed to the show; the day-sheet cell then points at the file.
            d = ev.get("event_date")
            plot_stem = (fs.stageplot_stem(ev.get("name") or "Untitled", d)
                         if d else f"{safe(ev.get('name') or 'Untitled')} stageplot")
            plots = [(a, ((a.get("submission") or {}).get("data") or {}).get("stage_plot_file"))
                     for a in acts]
            plots = [(a, s) for (a, s) in plots if s]
            multi = len(plots) > 1
            stageplot_names = {}
            for a, stored in plots:
                src = UPLOADS / stored
                if not src.exists():
                    print(f"  ! stage plot file missing on server: {stored}")
                    continue
                band = a["artist"]["name"] if a.get("artist") else "band"
                ext = Path(stored).suffix
                fname = f"{plot_stem} - {safe(band)}{ext}" if multi else f"{plot_stem}{ext}"
                shutil.copy(src, folder / fname)
                stageplot_names[band] = fname
                rel = (folder / fname).relative_to(out).as_posix()
                key = (band.strip().lower(),
                       (ev.get("venue") or "").strip().lower(),
                       d.isoformat() if d else "")
                plot_rels[key] = rel
                n_plots += 1

            daysheet.fill(eid, out_path=folder / f"{stem}.docx",
                          stageplot_names=stageplot_names)

            date = ev.get("event_date").isoformat() if ev.get("event_date") else None
            drafts_dir = folder / fs.EMAIL_DRAFTS_DIR
            for a in acts:
                if not a.get("artist"):
                    continue
                name = a["artist"]["name"]
                sg = slug(name)
                draft = find_one(DRAFTS, f"{sg}__{date}__*.md" if date else f"{sg}__*.md")
                if draft:
                    drafts_dir.mkdir(exist_ok=True)
                    shutil.copy(draft, drafts_dir / f"{stem} email - {safe(name)}.md")
                    n_emails += 1
                fu = find_one(FOLLOWUPS, f"{sg}__followup.md")
                if fu:
                    drafts_dir.mkdir(exist_ok=True)
                    shutil.copy(fu, drafts_dir / f"{stem} followup - {safe(name)}.md")
                    n_followups += 1

    # 4. tell the status merge where each filed stage plot landed (for the sheet link)
    status_path = out / "status.json"
    if plot_rels and status_path.exists():
        recs = json.loads(status_path.read_text())
        for r in recs:
            key = ((r.get("band") or "").strip().lower(),
                   (r.get("venue") or "").strip().lower(),
                   (r.get("date") or "")[:10])
            if key in plot_rels:
                r["stageplot_rel"] = plot_rels[key]
        status_path.write_text(json.dumps(recs, indent=2, default=str))

    print(f"\nPackage built at {out}")
    print(f"  {n_events} event(s) filed · {n_emails} email(s) · "
          f"{n_followups} follow-up(s) · {n_plots} stage plot(s)")


if __name__ == "__main__":
    main()
