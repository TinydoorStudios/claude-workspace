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
    args = ap.parse_args()

    rows = load_batch(args.batch)
    if not rows:
        print("No rows found in batch.", file=sys.stderr)
        sys.exit(1)

    new_t = env.get_template("new.md.j2")
    ret_t = env.get_template("returning.md.j2")

    summary = []
    with db.get_conn() as conn:
        for r in rows:
            name = r["name"]
            venue = r.get("venue")
            show_date = parse_date(r.get("show_date"))
            series = r.get("series") or None
            email = r.get("email") or None

            with conn.cursor() as cur:
                artist_id = db.upsert_artist(cur, name, email=email)
                show_id = db.upsert_show(cur, artist_id, venue, show_date,
                                         series=series, status="not_advanced")
                prior = db.played_within(cur, artist_id, show_date, months=args.months)
            conn.commit()

            token = None
            kind = "NEW"
            ctx = dict(name=name, venue=venue, email=email,
                       show_date=show_date.isoformat() if show_date else "",
                       public_url=PUBLIC_URL)
            if prior:
                kind = "RETURNING"
                # token carries artist id + this booking context
                token = _token(artist_id, venue, show_date)
                ctx["form_link"] = f"{PUBLIC_URL}/f/{token}"
                ctx["last"] = summarize_submission(prior)
                body = ret_t.render(**ctx)
            else:
                base = f"{PUBLIC_URL}/?venue={_q(venue)}"
                if series:
                    base += f"&series={_q(series)}"
                ctx["form_link"] = base
                body = new_t.render(**ctx)

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


def _token(artist_id, venue, show_date):
    from itsdangerous import URLSafeSerializer
    secret = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
    signer = URLSafeSerializer(secret, salt="advance-prefill")
    return signer.dumps({"a": artist_id,
                         "s": {"venue": venue,
                               "date": show_date.isoformat() if show_date else None}})


def _q(s):
    from urllib.parse import quote
    return quote(s or "")


if __name__ == "__main__":
    main()
