#!/usr/bin/env python3
"""Daily digest — one morning email covering (Brian, 2026-09-09; combined
with the standalone Crew Report the same day per "the two emails combined
into one"):
  1. Today's shows: band names, venue, start/end times, from advance-db.
  2. Today's crew: every venue staffed today per the public 3CDC staffing
     sheet — Mix/Tech/Stagehand/Stage Support/Other — regardless of
     whether the event has a tracked advance (reuses crew_report.py's
     collect_days(), scoped to just today).
  3. Advancing activity in the last 24 hours: new advance drafts sent out
     (outbound) and bands who responded (inbound) — two separate lanes,
     not the same thing said twice.
  4. Every show within 14 days, ranked soonest-first, with its live
     advance status (queued/awaiting/ready_to_send/followup_due/
     followup_drafted/responded/finalized) — "a clear sight on the bands that are
     advancing properly and bands that are not responding." This is the
     ONLY section that looks past today — Brian wants the 14-day window
     for advance status specifically, not for shows/crew detail.

Fired by n8n's "Daily Digest" workflow (n8n/daily_digest.json), which hits
POST /internal/daily-digest on app.py and SENDS the result for real, to
blloyd@3cdc.org — unlike every band-facing advance email, this is Brian's
own internal ops summary, not something that needs his review first. The
standalone "Crew Report" workflow's daily cron trigger was removed since
section 2 above now covers it every morning; its on-demand webhook (a
full 14-day, all-venue pull) still works standalone.

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
import crew_report as cr
import venue_email as ve

from jinja2 import Environment, FileSystemLoader

TEMPLATES = HERE / "email_templates"

# Same palette as status_log.py's STATE_STYLE / merge_status.py's STATE_FILL —
# one consistent look across every status surface in the pipeline. "responded"
# relabeled "Advancing In Progress" and "finalized" added (Brian, 2026-09-13),
# kept in sync with status_log.py's own STATE_STYLE — see that file's comment
# for why.
sys.path.insert(0, str(HERE.parent))
import status_labels as SL
STATE_STYLE = {k: (v[0], "#" + v[2], "#" + v[3]) for k, v in SL.STATE.items()}

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
        ev["start"] = ev["load_in"] or ev["event_start"] or "—"
        ev["end"] = ev["curfew"] or ev["event_end"] or "—"
        out.append(ev)
    return out


def _today_crew(today):
    """Every venue staffed today per the public 3CDC staffing sheet —
    Mix/Tech/Stagehand/Stage Support/Other — same rows crew_report.py's
    standalone 14-day report would show for today, just scoped to one
    day. Independent of advance-db: a venue staffed today with no
    tracked band still shows up here (Brian, 2026-09-09)."""
    try:
        by_date = cr.collect_days(today, today)
    except Exception as e:  # noqa: BLE001 — a staffing-sheet hiccup shouldn't break the digest
        print(f"[daily_digest] crew lookup failed: {e!r}", file=sys.stderr)
        return []
    return sorted(by_date.get(today, []), key=lambda e: e["venue"])


def build_digest(days_ahead=14, hours_back=24):
    today = dt.date.today()
    today_crew = _today_crew(today)
    with db.get_conn() as conn, conn.cursor() as cur:
        today_shows = _today_shows(cur, today)
        drafted = db.advances_drafted_since(cur, hours=hours_back)
        responded = db.advances_responded_since(cur, hours=hours_back)
        upcoming = db.upcoming_advance_status(cur, days=days_ahead)
        # audit #21: flag a missed 9am lifecycle check yesterday
        yday = today - dt.timedelta(days=1)
        missed_yesterday = not db.job_ran_since(
            cur, "advance-lifecycle", "cron", dt.datetime.combine(yday, dt.time(8, 55))) or False
        if missed_yesterday:
            cur.execute("SELECT 1 FROM job_runs WHERE job='advance-lifecycle' AND source='cron' LIMIT 1")
            missed_yesterday = cur.fetchone() is not None  # only once cron tagging exists
        # review 2026-09-14 (E1): open decisions + everything that used to be
        # its own alert email (doc notices, submission matches, set-time clashes,
        # the 3-day unresponded list, thank-you / day-before failures)
        needs = db.needs_attention(cur)
        queued = db.undelivered_digest_items(cur)
        db.mark_digest_items_delivered(cur, [q["id"] for q in queued])
        conn.commit()

    public_url = __import__("os").environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
    for it in needs:
        it["link"] = (public_url + it["link_path"]) if it.get("link_path") else None

    for row in upcoming:
        row["style"] = STATE_STYLE.get(row["state"], (row["state"] or "—", "#E5E7EB", "#374151"))

    # autoescape: band/venue names are user-typed (audit cleanup)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    tpl = env.get_template("daily_digest.html.j2")
    html = tpl.render(
        today=today.strftime("%A, %B ") + str(today.day) + today.strftime(", %Y"),
        today_shows=today_shows, today_crew=today_crew,
        drafted=drafted, responded=responded, upcoming=upcoming,
        missed_yesterday=missed_yesterday, needs=needs, queued=queued,
        dashboard_url=public_url + "/dashboard",
    )
    subject = f"Advance Digest — {today.strftime('%a %m/%d')}"
    if needs:
        subject += f" — {len(needs)} need{'s' if len(needs) == 1 else ''} you"
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
