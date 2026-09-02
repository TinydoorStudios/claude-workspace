#!/usr/bin/env python3
"""Build the whole Advancing/ output tree from the advance list spreadsheet.

The single entrypoint generate.command runs on the VM. It rebuilds events+acts
from the sheet (form submissions are never touched), then lays out, under --out:

    advance-status.xlsx
    Events/
        <date> — <event> (<venue>)/
            Day Sheet.docx
            Advance Email — <Band>.md          (one per act)
            Followups/<Band>.md                (only if one is queued)

The Mac's generate.command mirrors that tree straight into the Advancing/ folder,
so what the VM builds is exactly what Brian sees. Nothing is ever sent.

  python3 package_run.py lists/_current.xlsx --out _package
"""
import argparse
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
from draft_emails import slug  # same slug the drafts are named with

PY = sys.executable
DRAFTS = HERE / "drafts"
FOLLOWUPS = HERE / "followups"


def run(*args):
    subprocess.run([PY, *[str(a) for a in args]], cwd=HERE, check=True)


def safe(s):
    """Filesystem-safe, human-readable — keep spaces, drop path-hostile chars."""
    s = re.sub(r"[/\\:*?\"<>|]+", "-", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)


def event_folder_name(ev, acts):
    date = ev.get("event_date").isoformat() if ev.get("event_date") else "no-date"
    name = ev.get("name") or ", ".join(
        a["artist"]["name"] for a in acts if a.get("artist")) or "Untitled"
    venue = ev.get("venue") or "venue TBD"
    return safe(f"{date} — {name} ({venue})")


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
    events_dir = out / "Events"
    events_dir.mkdir(parents=True)

    # 1. rebuild the event/act model from the sheet (submissions untouched)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE events, event_acts RESTART IDENTITY CASCADE;")
        conn.commit()
    run("import_sheet.py", args.sheet)

    # 2. regenerate the flat draft/day-sheet artifacts into their working dirs
    for d in (DRAFTS, FOLLOWUPS, daysheet.FILLED):
        if d.exists():
            for f in d.glob("*"):
                if f.is_file():
                    f.unlink()
    run("draft_emails.py", args.sheet, "--mark-sent")
    run("dump_followups.py")
    run("status_sheet.py", "--json", str(out / "status.json"))

    # 3. compose the per-event tree
    n_events = n_daysheets = n_emails = n_followups = 0
    with db.get_conn() as conn, conn.cursor() as cur:
        events = db.list_events(cur)
        for e in events:
            eid = e["id"]
            ev = db.get_event(cur, eid)
            acts = db.event_acts(cur, eid)
            folder = events_dir / event_folder_name(ev, acts)
            folder.mkdir(parents=True, exist_ok=True)
            n_events += 1

            daysheet.fill(eid, daysheet.DEFAULT_TEMPLATE, out_path=folder / "Day Sheet.docx")
            n_daysheets += 1

            date = ev.get("event_date").isoformat() if ev.get("event_date") else None
            for a in acts:
                if not a.get("artist"):
                    continue
                name = a["artist"]["name"]
                sg = slug(name)
                pat = f"{sg}__{date}__*.md" if date else f"{sg}__*.md"
                draft = find_one(DRAFTS, pat)
                if draft:
                    shutil.copy(draft, folder / f"Advance Email — {safe(name)}.md")
                    n_emails += 1
                fu = find_one(FOLLOWUPS, f"{sg}__followup.md")
                if fu:
                    (folder / "Followups").mkdir(exist_ok=True)
                    shutil.copy(fu, folder / "Followups" / f"{safe(name)}.md")
                    n_followups += 1

    print(f"\nPackage built at {out}")
    print(f"  {n_events} event folder(s) · {n_daysheets} day-sheet(s) · "
          f"{n_emails} email(s) · {n_followups} follow-up(s)")


if __name__ == "__main__":
    main()
