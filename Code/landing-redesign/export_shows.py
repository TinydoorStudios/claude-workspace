#!/usr/bin/env python3
"""
Shows board feed for tinydoorstudios.com/rack/ (gated).

Scans the show folders (`audio/<Venue>/YYYY-MM-DD Show Name/`), reads each
show.status.json, and writes deploy/rack/shows.json covering the last 3 days
through the next 21. Show folders live on the Mac, so this runs here and
push-shows.command ships the result to the VM.

    python3 export_shows.py            # write deploy/rack/shows.json
    python3 export_shows.py --print    # also dump it to stdout
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.normpath(os.path.join(HERE, "..", "..", "audio"))
OUT = os.path.join(HERE, "deploy", "rack", "shows.json")

VENUES = {  # folder → (short tag, needs a Q225 .ses)
    "Fountain Square": ("FSQ", True),
    "Memorial Hall": ("MEMO", True),
    "Washington Park": ("WP", False),
    "Elm Street Plaza": ("ESP", False),
}
BACK, AHEAD = 3, 21
STAGES = ("scaffolded", "packet_built", "ses_built", "published")


def scan(today):
    lo = today - datetime.timedelta(days=BACK)
    hi = today + datetime.timedelta(days=AHEAD)
    shows = []
    for venue, (tag, needs_ses) in VENUES.items():
        vdir = os.path.join(AUDIO, venue)
        if not os.path.isdir(vdir):
            continue
        for name in os.listdir(vdir):
            m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.+)$", name)
            if not m:
                continue
            try:
                d = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            if not lo <= d <= hi:
                continue
            folder = os.path.join(vdir, name)
            try:
                with open(os.path.join(folder, "show.status.json"), encoding="utf-8") as f:
                    st = json.load(f)
            except (OSError, ValueError):
                st = {}
            stages = st.get("stages", {})
            files = os.listdir(folder)
            wiki = (stages.get("published") or {}).get("note") or ""
            shows.append({
                "date": m.group(1),
                "show": st.get("show") or m.group(2),
                "venue": tag,
                "needs_ses": needs_ses,
                "stages": {k: (stages.get(k) or {}).get("at") for k in STAGES},
                "rev": st.get("rev"),
                "plot": any(re.search(r"stage plot", f, re.I) for f in files),
                "wiki": ("https://" + wiki) if wiki.startswith("kb.") else None,
            })
    shows.sort(key=lambda s: (s["date"], s["venue"], s["show"]))
    return shows


def main():
    today = datetime.date.today()
    data = {
        "generated": int(datetime.datetime.now().timestamp()),
        "today": today.isoformat(),
        "shows": scan(today),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, OUT)
    if "--print" in sys.argv:
        print(json.dumps(data, indent=1))
    else:
        print(f"{len(data['shows'])} shows → {OUT}")


if __name__ == "__main__":
    main()
