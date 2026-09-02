#!/usr/bin/env python3
"""Advance email drafting engine.

Give it a batch list (CSV or JSON) of shows to advance. For each artist it:
  - upserts the artist + the show into the database (status: not_advanced),
  - decides NEW vs RETURNING using the cross-venue 6-month lookback,
  - renders a draft email (returning drafts summarize what we have on file and
    carry a prefilled form link),
  - writes the draft to tools/drafts/ and prints a summary table.

It DOES NOT SEND ANYTHING. Sending stays a human step. Run again any time; it is
idempotent on the artist/show rows.

Batch CSV columns (header row required): name, show_date, venue, series, email
  - name, show_date, venue required; series, email optional.
  - show_date: YYYY-MM-DD preferred (also accepts M/D/YYYY).

Usage:
  python3 draft_emails.py lists/example_batch.csv
  python3 draft_emails.py lists/batch.json --months 6
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):  # deployed flat, or repo layout
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db
sys.path.insert(0, str(HERE))
import fieldspec as fs
import venue_email as ve

from jinja2 import Environment, FileSystemLoader, select_autoescape

PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
DRAFTS = HERE / "drafts"
DRAFTS.mkdir(exist_ok=True)

env = Environment(
    loader=FileSystemLoader(str(HERE / "email_templates")),
    autoescape=select_autoescape(enabled_extensions=()),
    trim_blocks=True, lstrip_blocks=True,
)


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "band").lower()).strip("-")[:40] or "band"


def load_batch(path):
    p = Path(path)
    if p.suffix.lower() == ".xlsx":
        # the canonical Advance List spreadsheet
        from sheet import read_advance_sheet
        out = []
        for r in read_advance_sheet(p):
            out.append({
                "name": r.get("artist_name", ""),
                "show_date": r.get("event_date") or "",
                "venue": r.get("venue") or "",
                "series": r.get("series") or "",
                "email": r.get("contact_email") or "",
                "set_time": r.get("set_time") or "",
                "slot": r.get("slot") or "",
                "event_name": r.get("event_name") or "",
                "email_note": r.get("email_note") or "",
                "lead_name": r.get("lead_name") or "",
                "lead_phone": r.get("lead_phone") or "",
                "load_in": r.get("load_in") or "",
                "soundcheck": r.get("soundcheck") or "",
                "event_start": r.get("event_start") or "",
                "event_end": r.get("event_end") or "",
                "curfew": r.get("curfew") or "",
            })
        return out
    if p.suffix.lower() == ".json":
        rows = json.loads(p.read_text())
    else:
        with p.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        if not r.get("name"):
            continue
        out.append(r)
    return out


def summarize_submission(sub):
    """Human-readable 'here's what we have on file' block for returning artists."""
    if not sub:
        return []
    d = sub.get("data") or {}
    def yn(v): return "Yes" if v else ("No" if v is False else "—")
    lines = [
        ("Last show", f"{sub.get('venue') or '—'}"
                      f"{(' on ' + sub['show_date'].isoformat()) if sub.get('show_date') else ''}"),
        ("Performers + crew", sub.get("performers")),
        ("Monitors", sub.get("monitors")),
        ("Own IEMs", yn(sub.get("own_iems")) + (f" (split: {sub['split_snake']})"
                                                 if sub.get("split_snake") else "")),
        ("Stage", sub.get("stage_type")),
        ("Own engineer", sub.get("own_engineer")),
        ("Merch", yn(sub.get("merch"))),
        ("Band tent", sub.get("band_tent")),
        ("Large vehicle", yn(sub.get("large_vehicle"))),
    ]
    if d.get("backline"):
        lines.append(("Backline", d["backline"]))
    return [(k, v) for k, v in lines if v not in (None, "", "—")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", help="CSV or JSON list of shows to advance")
    ap.add_argument("--months", type=int, default=6, help="returning-artist lookback")
    ap.add_argument("--mark-sent", action="store_true",
                    help="stamp email_sent_at (generate.command uses this — sending = the send step)")
    args = ap.parse_args()

    rows = load_batch(args.batch)
    if not rows:
        print("No rows found in batch.", file=sys.stderr)
        sys.exit(1)

    advance_t = env.get_template("advance.md.j2")

    # the bill for each event (rows sharing event name + date + venue), in slot order
    SLOT_ORD = {"opener": 1, "direct_support": 2, "headliner": 3}
    bills = {}
    for r in rows:
        key = (r.get("event_name") or "", r.get("show_date") or "", r.get("venue") or "")
        bills.setdefault(key, []).append({
            "slot": r.get("slot") or "", "name": r.get("name") or "",
            "set_time": r.get("set_time") or "",
        })
    for acts in bills.values():
        acts.sort(key=lambda a: SLOT_ORD.get(a["slot"], 99))

    summary = []
    with db.get_conn() as conn:
        for r in rows:
            name = r["name"]
            venue = r.get("venue")
            show_date = parse_date(r.get("show_date"))
            series = r.get("series") or None
            email = r.get("email") or None
            bill = bills.get((r.get("event_name") or "",
                              r.get("show_date") or "", r.get("venue") or ""), [])
            deadline = ""
            if show_date:
                d = show_date - dt.timedelta(days=10)
                deadline = d.isoformat() if d >= dt.date.today() else ""

            with conn.cursor() as cur:
                artist_id = db.upsert_artist(cur, name, email=email)
                show_id = db.upsert_show(cur, artist_id, venue, show_date,
                                         series=series, status="not_advanced")
                prior = db.played_within(cur, artist_id, show_date, months=args.months)
            conn.commit()

            if args.mark_sent:
                with conn.cursor() as cur:
                    db.stamp_email_sent(cur, show_id)
                conn.commit()

            slot = (r.get("slot") or "").replace("_", " ")
            day_of_contact = ""
            if r.get("lead_name"):
                day_of_contact = r["lead_name"] + (
                    f" ({r['lead_phone']})" if r.get("lead_phone") else "")
            def _setlen(v):
                v = str(v).strip()
                return f"{v} min" if v.isdigit() else v
            set_line = ""
            if r.get("set_time"):
                set_line = f"Set length: {_setlen(r['set_time'])}" + (f" ({slot})" if slot else "")

            def sched(k):
                return r.get(k) or fs.SCHEDULE_DEFAULTS.get(k, "")
            schedule_block = "\n".join([
                f"  {sched('load_in')}    Load-In",
                f"  {sched('soundcheck')}    Sound Check",
                f"  {sched('event_start')}    Start of Event",
                f"  {sched('event_end')}   End of Event",
                f"  {sched('curfew')}   Curfew",
            ])

            bill_block = ""
            if len(bill) > 1:
                lines = ["The bill:"]
                for a in bill:
                    s = a["slot"].replace("_", " ")
                    line = f"  - {s}: {a['name']}"
                    if a.get("set_time"):
                        line += f" — {_setlen(a['set_time'])}"
                    lines.append(line)
                bill_block = "\n".join(lines)

            token = _token(artist_id, venue, show_date, series)
            returning = bool(prior)
            kind = "RETURNING" if returning else "NEW"
            ctx = dict(
                name=name, venue=venue,
                blocks=ve.blocks_for(venue), common_requirements=ve.COMMON_REQUIREMENTS,
                personal_note=(lambda n: f"{n}\n\n" if n else "")((r.get("email_note") or "").strip()),
                event_name=r.get("event_name") or "",
                show_date=show_date.isoformat() if show_date else "",
                advancing_contact=fs.ADVANCING_CONTACT, day_of_contact=day_of_contact,
                set_line=set_line, schedule_block=schedule_block, bill_block=bill_block,
                form_link=f"{PUBLIC_URL}/f/{token}", deadline=deadline,
                returning=returning, last=summarize_submission(prior) if returning else [],
            )
            body = advance_t.render(**ctx)

            fname = f"{slug(name)}__{show_date.isoformat() if show_date else 'nodate'}__{kind.lower()}.md"
            (DRAFTS / fname).write_text(body)
            summary.append((kind, name, venue,
                            show_date.isoformat() if show_date else "?",
                            email or "(no email)", fname))

    # summary table
    w = [max(len(str(x[i])) for x in summary + [("KIND", "ARTIST", "VENUE", "DATE", "EMAIL", "DRAFT")])
         for i in range(6)]
    hdr = ("KIND", "ARTIST", "VENUE", "DATE", "EMAIL", "DRAFT")
    line = "  ".join(str(hdr[i]).ljust(w[i]) for i in range(6))
    print(line)
    print("-" * len(line))
    for row in summary:
        print("  ".join(str(row[i]).ljust(w[i]) for i in range(6)))
    n_ret = sum(1 for s in summary if s[0] == "RETURNING")
    print(f"\n{len(summary)} drafts written to {DRAFTS}  "
          f"({n_ret} returning, {len(summary)-n_ret} new).")
    print("Nothing was sent. Review the drafts, then send from Gmail once approved.")


def _token(artist_id, venue, show_date, series=None):
    from itsdangerous import URLSafeSerializer
    secret = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
    signer = URLSafeSerializer(secret, salt="advance-prefill")
    return signer.dumps({"a": artist_id,
                         "s": {"venue": venue,
                               "date": show_date.isoformat() if show_date else None,
                               "series": series or None}})


def _q(s):
    from urllib.parse import quote
    return quote(s or "")


if __name__ == "__main__":
    main()
