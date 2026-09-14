#!/usr/bin/env python3
"""
show_closeout_check.py — which shows are past their date and not closed out?

Walks every venue show folder, reads show.status.json, and lists shows whose
date has passed but which are missing `published` or `harvested`, plus any
folder with no status file at all. Run by the weekly show-closeout task and
usable by hand:

    python3 show_closeout_check.py            # human table
    python3 show_closeout_check.py --json     # for automation

Exit 0 always — this reports, it never blocks.
"""
import argparse, datetime, json, os, re, sys

AUDIO = os.path.expanduser("~/Documents/Claude/audio")
VENUES = ("Fountain Square", "Memorial Hall", "Washington Park", "Elm Street Plaza",
          "Court Street Plaza", "Zeigler Park", "Imagination Alley", "Greaves Concert Hall")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import show_status  # noqa: E402


def scan(today=None):
    today = today or datetime.date.today()
    rows = []
    for v in VENUES:
        vdir = os.path.join(AUDIO, v)
        if not os.path.isdir(vdir):
            continue
        for name in sorted(os.listdir(vdir)):
            m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.+)$", name)
            if not m:
                continue
            date = datetime.date.fromisoformat(m.group(1))
            folder = os.path.join(vdir, name)
            st = show_status.load(folder)
            stages = (st or {}).get("stages") or {}
            missing = []
            if st is None:
                missing.append("no status file")
            else:
                for s in ("packet_built", "ses_built", "published", "harvested"):
                    if s not in stages:
                        missing.append(s)
            if date <= today and missing:
                rows.append({"venue": v, "date": m.group(1), "show": m.group(2),
                             "days_ago": (today - date).days, "missing": missing,
                             "folder": folder})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = scan()
    if a.json:
        print(json.dumps(rows, indent=2)); return 0
    if not rows:
        print("All past shows are published and harvested."); return 0
    print(f"{len(rows)} past show(s) not closed out:\n")
    for r in rows:
        print(f"  {r['date']}  {r['show']:<45.45s} {r['venue']:<16s} {r['days_ago']:>4d}d  missing: {', '.join(r['missing'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
