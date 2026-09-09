#!/usr/bin/env python3
"""Crew report — who's staffing every venue over the next N days, straight
from the same public 3CDC staffing sheet staffing.py reads (Brian,
2026-09-09: "show me the fuller crew report" — the first real use of
staff_for()'s Tech/Stagehand/Stage Support/Other coverage, not just Mix).

Fetches the schedule + codes sheets ONCE and reuses them across every
venue/date in range — staff_for() itself fetches fresh per call, which is
fine for a single lookup but far too slow for a report spanning 5 venues
across many days.

    python3 crew_report.py [--days 14] [--out FILE]
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import staffing as st

from jinja2 import Environment, FileSystemLoader

TEMPLATES = HERE / "email_templates"

VENUE_COLORS = {
    "Fountain Square": "#2E6DA4", "Washington Park": "#15803D",
    "Memorial Hall": "#7C3AED", "Elm Street Plaza": "#B45309",
    "Zeigler Park / Court Street Plaza / Imagination Alley": "#0369A1",
}


def _mix_for(raw, codes_rows):
    tokens = st._split_mix_cell(raw)
    if len(tokens) not in (1, 2):
        return {"foh": None, "mon": None}
    foh = st._format_row(st._resolve_row(tokens[0], codes_rows))
    mon = st._format_row(st._resolve_row(tokens[1], codes_rows)) if len(tokens) == 2 else None
    return {"foh": foh, "mon": mon}


def _unique_blocks():
    """SCHEDULE_COLUMNS has 3 venue names sharing one physical column set
    (Zeigler Park / Court Street Plaza / Imagination Alley) — de-dupe so
    that block's rows aren't read (and shown) three times, and give it one
    combined display name instead of picking an arbitrary one of the three."""
    blocks = {}
    order = []
    for venue, cols in st.SCHEDULE_COLUMNS.items():
        key = tuple(sorted(cols.items()))
        if key not in blocks:
            blocks[key] = {"cols": cols, "names": []}
            order.append(key)
        blocks[key]["names"].append(venue)
    out = []
    for key in order:
        b = blocks[key]
        label = b["names"][0] if len(b["names"]) == 1 else " / ".join(b["names"])
        out.append((label, b["cols"]))
    return out


def build_report(days=14, start=None):
    start = start or dt.date.today()
    end = start + dt.timedelta(days=days)

    schedule_rows = st._fetch_csv(st.SCHEDULE_GID)
    codes_rows = st._fetch_csv(st.CODES_GID)

    by_date = {}
    for venue, cols in _unique_blocks():
        need = max(cols.values())
        for row in schedule_rows:
            if len(row) <= need:
                continue
            d = st._parse_date(row[cols["date"]])
            if not d or d < start or d > end:
                continue
            has_content = any((row[c] or "").strip() for k, c in cols.items() if k != "date")
            if not has_content:
                continue
            event = (row[cols["event"]] or "").strip() if "event" in cols else ""
            entry = {
                "venue": venue, "event": event or "(unnamed)", "date": d,
                "color": VENUE_COLORS.get(venue, "#374151"),
                "mix": _mix_for((row[cols["mix"]] or "").strip(), codes_rows) if "mix" in cols else {"foh": None, "mon": None},
                "tech": [], "stagehand": [], "stage_support": [], "other": [],
            }
            for key in st._OTHER_ROLE_KEYS:
                col = cols.get(key)
                if col is None:
                    continue
                names = st._resolve_names(st._split_mix_cell((row[col] or "").strip()), codes_rows)
                if key == "stagehand_support":
                    entry["stagehand"] = names
                    entry["stage_support"] = names
                else:
                    entry[key] = names
            by_date.setdefault(d, []).append(entry)

    days_out = []
    d = start
    while d <= end:
        rows = sorted(by_date.get(d, []), key=lambda e: e["venue"])
        days_out.append({"date": d, "label": d.strftime("%A, %b %-d"), "rows": rows})
        d += dt.timedelta(days=1)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    tpl = env.get_template("crew_report.html.j2")
    return tpl.render(
        start=start.strftime("%b %-d"), end=end.strftime("%b %-d, %Y"), days=days_out,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    html = build_report(days=args.days)
    if args.out:
        args.out.write_text(html)
        print(f"Saved: {args.out}")
    else:
        print(html)


if __name__ == "__main__":
    main()
