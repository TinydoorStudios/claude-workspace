#!/usr/bin/env python3
"""Advance email drafting engine.

Give it a batch list (CSV or JSON) of shows to advance. For each artist it:
  - upserts the artist + the show into the database,
  - decides NEW vs RETURNING using the cross-venue 6-month lookback,
  - renders a draft email (returning drafts summarize what we have on file,
    recap the band's last filed advance document if one can be found, and
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
import forms_config
sys.path.insert(0, str(HERE))
import daysheet
import fieldspec as fs
import staffing
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


def us_date(d):
    """M/D/Y for anything shown IN a drafted email — Brian's US convention.
    Filenames and the console summary table stay ISO (sorts correctly)."""
    if not d:
        return ""
    if isinstance(d, str):
        d = parse_date(d)
    return d.strftime("%m/%d/%Y") if d else ""


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


def _first_name(s):
    """'Dali Amador' -> 'Dali' — the initial advance email's greeting uses
    only the contact's first name plus the band name (Brian, 2026-09-13:
    'Hello Dali and The Amador Sisters,' not the full contact name). Only
    the GREETING changes; the prefill token (_token, below) still carries
    the full contact_name into the band's own form untouched — that's a
    form field value, not a greeting."""
    s = (s or "").strip()
    return s.split()[0] if s else ""


def _norm_cmp(s):
    """Whitespace-collapsed, lowercased — same normalization the rest of
    this codebase uses for 'are these the same, ignoring typing noise'
    comparisons (artists.match_key)."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _greeting_contact_name(contact_name, band_name):
    """Brian, 2026-09-13: a solo act that books under their own name (band
    name IS the contact, exactly, nothing else added) doesn't need both —
    'Hello Dali Amador,' not 'Hello Dali and Dali Amador,'. Returns '' in
    that case, which the template's own {% if contact_name %} already
    collapses the greeting down to just the band name — no template
    change needed. Otherwise returns the usual first-name-only greeting
    (_first_name)."""
    if contact_name and _norm_cmp(contact_name) == _norm_cmp(band_name):
        return ""
    return _first_name(contact_name)


def _split_subject(rendered):
    """A rendered advance*.md.j2's first line is always 'Subject: ...' —
    split it off from the rest of the body. app.py's automated lifecycle
    path uses this to send via Outlook directly (live-send migration,
    2026-09-13); for a manual CSV/xlsx batch run of this file's own CLI,
    whoever turns a tools/drafts/*.md file into a real Outlook draft treats
    that first line as the subject (a human/LLM step, not code — see
    ARCHITECTURE.md's 'Sending' section)."""
    first, _, rest = rendered.partition("\n")
    return first, rest.lstrip("\n")


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
                "event_name": r.get("event_name") or "",
                "email_note": r.get("email_note") or "",
                "location": r.get("location") or "",
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
                      f"{(' on ' + us_date(sub['show_date'])) if sub.get('show_date') else ''}"),
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
    ap.add_argument("--out", type=Path, default=None,
                    help="write drafts here instead of tools/drafts/ (the lifecycle's private run folder)")
    args = ap.parse_args()
    out_dir = args.out or DRAFTS
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_batch(args.batch)
    if not rows:
        print("No rows found in batch.", file=sys.stderr)
        sys.exit(1)

    advance_t = env.get_template("advance.md.j2")
    # Only rendered for a series in ve.BILINGUAL_SERIES (Salsa On The Square,
    # 2026-09-12) — every other series never touches this template.
    advance_es_t = env.get_template("advance_es.md.j2")

    # the bill for each event (rows sharing event name + date + venue), in set
    # order — earliest set start first (Brian, 2026-09-15). Slots are retired,
    # and the band-facing copy never labelled anyone the opener anyway: what an
    # artist actually wants out of this block is who else is on and when.
    bills = {}

    def _bill_key(r):
        # same grouping as import_sheet.py: one internal bill per venue+date,
        # a 3rd-party booking is its own bill (Brian, 2026-09-14)
        party = ("3p:" + (r.get("event_name") or r.get("name") or "")) if db.is_third_party(r.get("series")) else ""
        return (party, r.get("show_date") or "", r.get("venue") or "")

    for r in rows:
        key = _bill_key(r)
        bills.setdefault(key, []).append({
            "name": r.get("name") or "",
            "set_time": r.get("set_time") or "",
            "set_start": r.get("event_start") or "",
        })
    for acts in bills.values():
        acts.sort(key=lambda a: (db.parse_clock(a["set_start"]) is None,
                                 db.parse_clock(a["set_start"]) or 0, a["name"]))

    summary = []
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            removed = db.pending_removal_idents(cur)
        today = dt.date.today()
        for r in rows:
            try:
                name = r["name"]
                venue = r.get("venue")
                show_date = parse_date(r.get("show_date"))
                series = r.get("series") or None
                # root cause A (audit 2026-09-16): never mint a show for a row
                # the app removed (sheet deletion pending), nor for a past date
                # — a stale row for a show that's already happened can only
                # resurrect something deleted, never book anything.
                if db.removal_ident(name, venue, show_date) in removed:
                    print(f"  skip {name} {show_date}: removed in the app", file=sys.stderr)
                    continue
                if show_date and show_date < today:
                    with conn.cursor() as cur:
                        if not db.show_for_booking(cur, name, venue, show_date):
                            continue
                # Brian, 2026-09-12: Salsa On The Square's advance email goes out
                # English-then-Spanish in one message with two form links, no
                # exceptions asked for elsewhere — every other series is
                # completely unaffected by everything gated on this flag below.
                is_bilingual = bool(series) and ve.is_bilingual_series(series)
                email = r.get("email") or None
                bill = bills.get(_bill_key(r), [])
                deadline = ""
                if show_date:
                    d = show_date - dt.timedelta(days=10)
                    deadline = us_date(d) if d >= dt.date.today() else ""

                with conn.cursor() as cur:
                    artist_id = db.upsert_artist(cur, name, email=email)
                    show_id = db.upsert_show(cur, artist_id, venue, show_date, series=series)
                    prior = db.played_within(cur, artist_id, show_date, months=args.months,
                                             exclude_show_id=show_id)
                conn.commit()

                if args.mark_sent:
                    with conn.cursor() as cur:
                        db.stamp_email_sent(cur, show_id)
                    conn.commit()

                # Day-of contact (audit #15): the MIX ENGINEER's name + cell from the
                # staffing sheet (FSQ and WP), then the booking's Lead, then — if
                # neither exists yet — say it comes the week of the show and drop
                # the "text them 5 minutes out" line (there's no one to text).
                day_of_contact = ""
                engineer_contact = False
                # audit 2026-09-16 #23: the lifecycle's welcome batch keys
                # this row "name", not "artist_name" (see main()'s `name =
                # r["name"]` above) — r.get("artist_name") was always None
                # on that path, so the mix-engineer lookup silently fell
                # through to the booking Lead (or nothing) for every
                # welcome sent through the live lifecycle, not just the
                # CSV/xlsx batch path this also serves.
                eng = (staffing.engineer_for(venue, show_date,
                                             series=r.get("series"),
                                             event_name=r.get("event_name"),
                                             artist_name=name,
                                             event_start=r.get("event_start"))
                       if venue in ("Fountain Square", "Washington Park") else None)
                if eng:
                    day_of_contact = eng
                    engineer_contact = True
                elif r.get("lead_name"):
                    day_of_contact = r["lead_name"] + (
                        f" ({r['lead_phone']})" if r.get("lead_phone") else "")

                email_extra = {}
                if venue == "Washington Park":
                    loc_name = r.get("location") or ""
                    loc_cfg = forms_config.WP_LOCATIONS.get(loc_name)
                    email_extra["location"] = loc_name or "confirm with your day-of contact"
                    email_extra["stage_size"] = (loc_cfg["stage_size"] if loc_cfg
                                                  else "confirm with your day-of contact")
                    # Lighting exists only at the Main Stage; Porch and Bandstand
                    # have none, so the LD line is dropped from their emails
                    # entirely (Brian, 2026-09-11).
                    email_extra["lighting_line"] = (
                        "\n- Lighting: we provide a house LD."
                        if loc_name == "Main Stage" else "")
                    # Drum riser is a Main Stage option only; Porch/Bandstand have
                    # none, so drop "flat vs. drum riser" from their emails too.
                    email_extra["riser_phrase"] = (
                        "flat vs. drum riser, " if loc_name == "Main Stage" else "")
                def _setlen(v):
                    v = str(v).strip()
                    return f"{v} min" if v.isdigit() else v
                set_line = ""
                if r.get("set_time"):
                    set_line = f"Set length: {_setlen(r['set_time'])}"

                # Review 2026-09-14 (M3): a blank schedule field is TBD, not the
                # Fountain Square default — a WP/Court/ESP booking with no times
                # used to email the band FSQ's day as fact.
                def sched(k, lang="en"):
                    return r.get(k) or (fs.SCHEDULE_TBD_ES if lang == "es" else fs.SCHEDULE_TBD)

                # A series can lock its own schedule (Brian, 2026-09-09: Salsa On
                # The Square runs a fixed 3-set/2-break night that never
                # changes). That wins over whatever a staffer types on the
                # booking — a full replacement of the Day Schedule block, not
                # just the generic 5 fields filled in differently.
                custom_schedule = ve.schedule_block_for(venue, series) if series else None
                schedule_locked = bool(custom_schedule)
                if custom_schedule:
                    schedule_block = custom_schedule
                else:
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
                        when = a.get("set_start") or "time TBC"
                        line = f"  - {when}  {a['name']}"
                        if a.get("set_time"):
                            line += f" — {_setlen(a['set_time'])}"
                        lines.append(line)
                    bill_block = "\n".join(lines)

                # ── Spanish half of a bilingual send (ve.BILINGUAL_SERIES) ──
                # Same shape as the English block above, Spanish labels around
                # the same underlying times/names. schedule_block_for(lang="es")
                # returns None (never falls back to English prose) if the
                # series file has no "## Schedule (Español)" section, in which
                # case the generic 5-row Spanish schedule is built instead —
                # same as the English path's own fallback.
                set_line_es = bill_block_es = ""
                schedule_block_es, schedule_locked_es = "", False
                if is_bilingual:
                    custom_schedule_es = ve.schedule_block_for(venue, series, lang="es")
                    schedule_locked_es = bool(custom_schedule_es)
                    if custom_schedule_es:
                        schedule_block_es = custom_schedule_es
                    else:
                        rl = ve.SCHEDULE_ROW_LABELS_ES
                        schedule_block_es = "\n".join([
                            f"  {sched('load_in', 'es')}    {rl['load_in']}",
                            f"  {sched('soundcheck', 'es')}    {rl['soundcheck']}",
                            f"  {sched('event_start', 'es')}    {rl['event_start']}",
                            f"  {sched('event_end', 'es')}   {rl['event_end']}",
                            f"  {sched('curfew', 'es')}   {rl['curfew']}",
                        ])
                    if r.get("set_time"):
                        set_line_es = f"{ve.SET_LENGTH_LABEL_ES}: {_setlen(r['set_time'])}"
                    if len(bill) > 1:
                        lines_es = [ve.BILL_HEADER_ES]
                        for a in bill:
                            when = a.get("set_start") or ve.TIME_TBC_ES
                            line = f"  - {when}  {a['name']}"
                            if a.get("set_time"):
                                line += f" — {_setlen(a['set_time'])}"
                            lines_es.append(line)
                        bill_block_es = "\n".join(lines_es)

                # Is this a multi-artist night? Counted from the bookings table
                # (Brian, 2026-09-15), which knows about an artist as soon as staff
                # logs the booking — so artist 1 knows it's a multi-artist night on
                # day one even if the others aren't in THIS batch. That's what the
                # retired "Bands on the Bill" answer was for; it's counted now
                # rather than typed. Falls back to this batch's own bill.
                try:
                    with conn.cursor() as cur:
                        booked_n = db.artist_count_for_event(cur, venue, show_date, series=series)
                except Exception:
                    booked_n = 0
                multiband = (booked_n or 0) >= 2 or bool(bill_block)

                token = _token(artist_id, venue, show_date, series, r.get("location"),
                               r.get("contact_name"), r.get("contact_email") or r.get("email"))
                with conn.cursor() as cur:
                    short_code = db.get_or_create_short_link(cur, token)
                conn.commit()
                returning = bool(prior)
                kind = "RETURNING" if returning else "NEW"

                advance_recap = None
                if returning and prior.get("venue") and prior.get("show_date"):
                    # DB first — the nightly extraction (tools/extract_advance_recap.py,
                    # 3 days after the show) stores this durably, independent of
                    # events/event_acts (which package_run.py truncates + rebuilds
                    # every run) and of the filed .docx still being where it was
                    # filed. Live-parse the file only as a fallback for a show too
                    # recent for the nightly job to have caught yet.
                    stored = None
                    if prior.get("show_id"):
                        with conn.cursor() as cur:
                            stored = db.get_advance_recap_by_show(cur, prior["show_id"])
                    if stored:
                        advance_recap = {"venue": stored["venue"],
                                          "show_date": us_date(stored["show_date"]),
                                          "rows": [tuple(pair) for pair in stored["recap"]]}
                        print(f"  (recap: db, {stored['source_docx']})")
                    else:
                        found = daysheet.read_filed_advance(prior["venue"], prior["show_date"], name)
                        if found:
                            recap_path, recap_rows = found
                            advance_recap = {"venue": prior["venue"],
                                              "show_date": us_date(prior["show_date"]),
                                              "rows": recap_rows}
                            print(f"  (recap: live file, {recap_path.name})")

                last_rows = summarize_submission(prior) if returning else []
                personal_note_en = (r.get("email_note") or "").strip()
                blocks_en = ve.blocks_for(venue, series=series, third_party=db.is_third_party(series),
                                          **email_extra)
                if not day_of_contact:
                    blocks_en = ve.without_text_on_arrival(blocks_en, lang="en")
                ctx = dict(
                    name=name, contact_name=_greeting_contact_name(r.get("contact_name"), name), venue=venue,
                    blocks=blocks_en, common_requirements=ve.COMMON_REQUIREMENTS,
                    engineer_contact=engineer_contact,
                    personal_note=(f"{personal_note_en}\n\n" if personal_note_en else ""),
                    event_name=r.get("event_name") or "",
                    series=series or "",
                    show_date=us_date(show_date),
                    advancing_contact=fs.ADVANCING_CONTACT, day_of_contact=day_of_contact,
                    set_line=set_line, schedule_block=schedule_block, bill_block=bill_block,
                    multiband=multiband, schedule_locked=schedule_locked,
                    form_link=f"{PUBLIC_URL}/s/{short_code}", deadline=deadline,
                    returning=returning, last=last_rows,
                    advance_recap=advance_recap,
                )

                if is_bilingual:
                    # Same booking, Spanish labels/blocks. personal_note and
                    # advance_recap are left out of this half on purpose — a
                    # staffer's ad hoc note is written in English and would
                    # read oddly repeated verbatim under the Spanish section,
                    # and advance_recap's row labels come from the filed docx's
                    # own English column headers (fieldspec.py's full label
                    # set), not the handful this module translates for `last` —
                    # the English half above already carries both, nothing is
                    # lost by not duplicating them here untranslated.
                    ctx_es = dict(ctx)
                    blocks_es = ve.blocks_for(venue, series=series, lang="es",
                                              third_party=db.is_third_party(series), **email_extra)
                    if not day_of_contact:
                        blocks_es = ve.without_text_on_arrival(blocks_es, lang="es")
                    ctx_es.update(
                        blocks=blocks_es,
                        common_requirements=ve.COMMON_REQUIREMENTS_ES,
                        personal_note="",
                        set_line=set_line_es, schedule_block=schedule_block_es,
                        bill_block=bill_block_es, schedule_locked=schedule_locked_es,
                        form_link=f"{PUBLIC_URL}/s/{short_code}?lang=es",
                        last=[(ve.SUMMARY_LABELS_ES.get(k, k), v) for k, v in last_rows],
                        advance_recap=None,
                    )
                    subject_line, body_en = _split_subject(advance_t.render(**ctx))
                    _, body_es = _split_subject(advance_es_t.render(**ctx_es))
                    sep = "─" * 42
                    body = (f"{subject_line}\n\n{body_en}\n\n{sep}\n"
                            f"ESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}")
                else:
                    body = advance_t.render(**ctx)

                fname = f"{slug(name)}__{show_date.isoformat() if show_date else 'nodate'}__{kind.lower()}.md"
                (out_dir / fname).write_text(body)
                summary.append((kind, name, venue,
                                show_date.isoformat() if show_date else "?",
                                email or "(no email)", fname))
            except Exception as e:  # noqa: BLE001 — one bad row must never sink the whole batch (audit 2026-09-16 #15)
                print(f"[draft_emails] {r.get('name')}: {e!r}", file=sys.stderr)
                continue

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
    print(f"\n{len(summary)} drafts written to {out_dir}  "
          f"({n_ret} returning, {len(summary)-n_ret} new).")
    print("Nothing was sent. Review the drafts, then send from Outlook once approved.")


def _token(artist_id, venue, show_date, series=None, location=None,
           contact_name=None, contact_email=None):
    """contact_name/contact_email are the STAFF-typed booking contact (Brian,
    2026-09-09) — carried into the band's own form as an editable starting
    value at /f/<token>, same as venue/date/location already are. Never
    locked: a band can always correct what staff typed."""
    from itsdangerous import URLSafeSerializer
    secret = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
    signer = URLSafeSerializer(secret, salt="advance-prefill")
    return signer.dumps({"a": artist_id,
                         "s": {"venue": venue,
                               "date": show_date.isoformat() if show_date else None,
                               "series": series or None,
                               "location": location or None,
                               "contact_name": (contact_name or "").strip() or None,
                               "contact_email": (contact_email or "").strip() or None}})


def _q(s):
    from urllib.parse import quote
    return quote(s or "")


if __name__ == "__main__":
    main()
