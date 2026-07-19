#!/usr/bin/env python3
"""
show.status.json — per-show pipeline state.

One small JSON file in every show folder tracking where the show sits in the
five-stage chain (PIPELINE.md): scaffolded → packet_built → ses_built →
verified → published. Written by scaffold_show.py, stamped automatically by
build_packet.py and the .ses engine; "published" is stamped by the wiki push
skill. "verified" is OPTIONAL/informational (rule 2026-07-19: shows are
one-offs — publishing gates on Brian's explicit go, never on a console check;
stamp verified only if he volunteers that the file ran on the desk).

Downstream consumers (send-it, show-wiki-push, any resume) read this instead
of guessing from folder recency.

CLI:
    python3 show_status.py stamp --folder <show dir> --stage <stage> [--note "…"]
    python3 show_status.py show  --folder <show dir>

Stamping is idempotent (re-stamping updates the timestamp/note) and creates
the file if missing, inferring venue/date/name from the folder path
(`<Venue>/YYYY-MM-DD Show Name/`). Library use: stamp(folder, stage, ...)
never raises on I/O problems unless strict=True — a status stamp must never
break a build.
"""
import argparse
import datetime
import json
import os
import re
import sys

FILENAME = "show.status.json"
STAGES = ("scaffolded", "packet_built", "ses_built", "verified", "published")


def _path(folder):
    return os.path.join(folder, FILENAME)


def load(folder):
    """Return the status dict, or None if no status file exists."""
    try:
        with open(_path(folder), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _infer(folder):
    """Best-effort venue/date/name from `<Venue>/YYYY-MM-DD Show Name`."""
    base = os.path.basename(os.path.normpath(folder))
    venue = os.path.basename(os.path.dirname(os.path.normpath(folder)))
    m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(.+)$", base)
    date, name = (m.group(1), m.group(2)) if m else (None, base)
    return venue or None, date, name


def stamp(folder, stage, note=None, extra=None, strict=False):
    """Stamp a stage (timestamp now). Creates the file if missing."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r} — one of {STAGES}")
    try:
        st = load(folder)
        if st is None:
            venue, date, name = _infer(folder)
            st = {"show": name, "venue": venue, "date": date, "stages": {}}
        st.setdefault("stages", {})
        entry = {"at": datetime.datetime.now().isoformat(timespec="seconds")}
        if note:
            entry["note"] = note
        st["stages"][stage] = entry
        if extra:
            st.update(extra)
        with open(_path(folder), "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
            f.write("\n")
        return st
    except Exception:
        if strict:
            raise
        print(f"  (show_status: could not stamp {stage!r} in {folder} — "
              "non-fatal, continuing)", file=sys.stderr)
        return None


def render(st):
    if not st:
        return "no show.status.json"
    lines = [f"{st.get('show')} — {st.get('venue')} {st.get('date') or ''}".rstrip()]
    for s in STAGES:
        e = (st.get("stages") or {}).get(s)
        mark = f"✓ {e['at']}" + (f"  ({e['note']})" if e.get("note") else "") if e else "—"
        lines.append(f"  {s:<13s} {mark}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-show pipeline status file.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stamp")
    p.add_argument("--folder", required=True)
    p.add_argument("--stage", required=True, choices=STAGES)
    p.add_argument("--note")
    p = sub.add_parser("show")
    p.add_argument("--folder", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "stamp":
        st = stamp(a.folder, a.stage, note=a.note, strict=True)
        print(render(st))
    else:
        print(render(load(a.folder)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
