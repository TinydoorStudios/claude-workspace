#!/usr/bin/env python3
"""Daily digest — one morning email covering (Brian, 2026-09-09):
  1. Today's shows: crew (from the public 3CDC staffing sheet), band
     names, venue, start/end times.
  2. Advancing activity in the last 24 hours: new advance drafts sent out
     (outbound) and bands who responded (inbound) — two separate lanes,
     not the same thing said twice.
  3. Every show within 14 days, ranked soonest-first, with its live
     advance status (queued/awaiting/ready_to_send/followup_due/
     followup_drafted/responded) — "a clear sight on the bands that are
     advancing properly and bands that are not responding."

Fired by n8n's "Daily Digest" workflow (n8n/daily_digest.json), which hits
POST /internal/daily-digest on app.py and SENDS the result for real, to
blloyd@3cdc.org — unlike every band-facing advance email, this is Brian's
own internal ops summary, not something that needs his review first.

    python3 daily_digest.py             # print the rendered HTML
    python3 daily_digest.py --out FILE  # save it instead
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import staffing
import venue_email as ve

from jinja2 import Environment, FileSystemLoader

TEMPLATES = HERE / "email_templates"

# Same palette as status_log.py's STATE_STYLE / merge_status.py's STATE_FILL —
# one consistent look across every status surface in the pipeline.
STATE_STYLE = {
    "queued":           ("Not Started",    "#E5E7EB", "#1F2937"),
    "awaiting":         ("Drafted",        "#FEF3C7", "#78350F"),
    "ready_to_send":    ("Ready to Send",  "#C7D2FE", "#1E3A5F"),
    "followup_due":     ("Follow-up Due",  "#FFE4B5", "#7C2D12"),
    "followup_drafted": ("Follow-up Sent", "#DBEAFE", "#1E3A5F"),
    "responded":        ("Completed",      "#C6EFCE", "#14532D"),
}

SCHEDULE_FIELDS = ("load_in", "soundcheck", "event_start", "event_end", "curfew")


def _today_shows(cur, today):
    """One entry per (venue, event) booked today — band names merged across
    every act on the bill, schedule fields coalesced across whichever
    band's booking row actually has them filled in."""
    rows = db.bookings_on(cur, today)
    events = {}
    order = []
    for r in rows:
        key = (r["venue"], r["event_name"] or "")
        ev = events.get(key)
        if ev is None:
            ev = {
                "event_name": r["event_name"] or "(untitled)",
                "venue": r["venue"], "location": r["location"],
                "series": r["series"], "bands": [],
                **{f: None for f in SCHEDULE_FIELDS},
            }
            events[key] = ev
            order.append(key)
        if r["artist_name"] and r["artist_name"] not in ev["bands"]:
            ev["bands"].append(r["artist_name"])
        for f in SCHEDULE_FIELDS:
            if not ev[f] and r[f]:
                ev[f] = r[f]

    out = []
    for key in order:
        ev = events[key]
        venue = ev["venue"]
        # A locked series never shows schedule fields on the booking form at
        # all (Brian, 2026-09-09) — fall back to its own crew schedule's
        # first/last timed rows so today's digest isn't just blank dashes.
        if ev["series"] and not (ev["event_start"] or ev["load_in"]):
            timed = [(label, t) for label, t in ve.crew_schedule_for(venue, ev["series"]) if t]
            if timed:
                ev["load_in"] = ev["load_in"] or timed[0][1]
                ev["curfew"] = ev["curfew"] or timed[-1][1]
        try:
            names = staffing.engineers_for(venue, today.isoformat()) if venue else {}
        except Exception as e:  # noqa: BLE001 — a staffing-sheet hiccup shouldn't break the digest
            print(f"[daily_digest] staffing lookup failed: {e!r}", file=sys.stderr)
            names = {}
        crew_bits = []
        if names.get("foh"):
            crew_bits.append(f"FOH – {names['foh']}")
        if names.get("mon"):
            crew_bits.append(f"Mon – {names['mon']}")
        ev["crew"] = " / ".join(crew_bits) or "—"
        ev["start"] = ev["load_in"] or ev["event_start"] or "—"
        ev["end"] = ev["curfew"] or ev["event_end"] or "—"
        out.append(ev)
    return out


def build_digest(days_ahead=14, hours_back=24):
    today = dt.date.today()
    with db.get_conn() as conn, conn.cursor() as cur:
        today_shows = _today_shows(cur, today)
        drafted = db.advances_drafted_since(cur, hours=hours_back)
        responded = db.advances_responded_since(cur, hours=hours_back)
        upcoming = db.upcoming_advance_status(cur, days=days_ahead)

    for row in upcoming:
        row["style"] = STATE_STYLE.get(row["state"], (row["state"] or "—", "#E5E7EB", "#374151"))

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)))
    tpl = env.get_template("daily_digest.html.j2")
    html = tpl.render(
        today=today.strftime("%A, %B ") + str(today.day) + today.strftime(", %Y"),
        today_shows=today_shows, drafted=drafted, responded=responded, upcoming=upcoming,
    )
    subject = f"Advance Digest — {today.strftime('%a %m/%d')}"
    if today_shows:
        subject += f" — {len(today_shows)} show{'s' if len(today_shows) != 1 else ''} today"
    return subject, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, help="save the rendered HTML here instead of printing")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()
    subject, html = build_digest(days_ahead=args.days, hours_back=args.hours)
    if args.out:
        args.out.write_text(html)
        print(f"Subject: {subject}\nSaved: {args.out}")
    else:
        print(f"Subject: {subject}\n\n{html}")


if __name__ == "__main__":
    main()
