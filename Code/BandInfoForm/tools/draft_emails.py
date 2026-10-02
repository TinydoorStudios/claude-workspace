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
        # 2026-09-24: performers is the on-stage count now, crew_count is the rest
        ("Performers", sub.get("performers")),
        ("Crew", sub.get("crew_count")),
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


# ── reminders (2026-09-24 research #1) ─────────────────────────────────────
# The T-10/7/3/1 bodies used to be byte-identical, so a band that ignored the
# first ignored all of them and none of them said what we were actually
# waiting on. Each tier now names what's missing for THAT show and says
# something the previous one didn't. Brian, 2026-09-24: the ask is always the
# form or a reply to this email — never "call us".

# 15/5/2 are Memorial Hall's extra rungs (Brian, 2026-09-29: welcome at 30,
# chases at 15/10/7/5/3/2/1); every other venue still runs 10/7/3/1.
REMINDER_TIERS = (15, 10, 7, 5, 3, 2, 1)

# What a band is still owing us, in words they'd use. Order is the order they
# get listed; missing_for_show caps the list so a reminder stays readable on a
# phone.
MISSING_LABELS = {
    "form":       {"en": "your advance form (we have nothing on file yet)",
                   "es": "su formulario de avance (todavía no tenemos nada registrado)"},
    "plot":       {"en": "your stage plot and input list",
                   "es": "su plano de escenario / lista de entradas"},
    "escort":     {"en": "a cell number for whoever's on stage that day",
                   "es": "un número de celular de quien esté en el escenario ese día"},
    "performers": {"en": "how many of you are on stage",
                   "es": "cuántas personas suben al escenario"},
    "monitors":   {"en": "how many monitor mixes you need",
                   "es": "cuántas mezclas de monitor necesitan"},
    "phone":      {"en": "a phone number where we can reach you",
                   "es": "un teléfono donde podamos localizarlos"},
    # nothing identifiable is missing (staff typed the answers in at booking) —
    # we're waiting on the band to confirm what we already hold.
    "confirm":    {"en": "a quick yes that what we have on file is right",
                   "es": "una confirmación rápida de que lo que tenemos registrado es correcto"},
}

_TIER_LEAD = {
    15: {"en": "We're about two weeks out from your show at {venue} on {day}, and we still need {missing}.",
         "es": "Faltan unas dos semanas para su show en {venue} el {day} y todavía necesitamos {missing}."},
    10: {"en": "We're ten days out from your show at {venue} on {day}, and we still need {missing}.",
         "es": "Faltan diez días para su show en {venue} el {day} y todavía necesitamos {missing}."},
    7:  {"en": "One week out from your show at {venue} on {day}. We still need {missing}.",
         "es": "Falta una semana para su show en {venue} el {day}. Todavía necesitamos {missing}."},
    5:  {"en": "Five days out from your show at {venue} on {day}, and we still need {missing}.",
         "es": "Faltan cinco días para su show en {venue} el {day} y todavía necesitamos {missing}."},
    3:  {"en": "Three days out from your show at {venue} on {day}, and we still need {missing}.",
         "es": "Faltan tres días para su show en {venue} el {day} y todavía necesitamos {missing}."},
    2:  {"en": "Two days out from your show at {venue} on {day}, and we still don't have {missing}.",
         "es": "Faltan dos días para su show en {venue} el {day} y todavía no tenemos {missing}."},
    1:  {"en": "Your show at {venue} on {day} is right on top of us, and we still don't have {missing}.",
         "es": "Su show en {venue} el {day} está a la vuelta de la esquina, y todavía no tenemos {missing}."},
}
# The part that makes each tier different: what happens next if we don't get it.
_TIER_THEN = {
    15: {"en": "We need this by {deadline}.",
         "es": "Lo necesitamos a más tardar el {deadline}."},
    10: {"en": "We need this by {deadline}.",
         "es": "Lo necesitamos a más tardar el {deadline}."},
    7:  {"en": "We need this by {deadline} so your show gets built in time.",
         "es": "Lo necesitamos a más tardar el {deadline} para tener su show armado a tiempo."},
    5:  {"en": "We're past the deadline, and your show gets built from this paperwork this week.",
         "es": "Ya pasó la fecha límite, y su show se arma con esta información esta semana."},
    3:  {"en": "Your engineer builds your show from this paperwork the day before the show, so right now it's the holdup.",
         "es": "Su ingeniero arma su show con esta información el día antes del show, así que por ahora es lo que nos tiene detenidos."},
    2:  {"en": "Your show gets built tomorrow, so today is the last good day to send it.",
         "es": "Su show se arma mañana, así que hoy es el último buen día para enviarlo."},
    1:  {"en": "If we don't hear back today, we'll set you up ad hoc on show day.",
         "es": "Si no tenemos noticias hoy, lo armamos sobre la marcha el día del show."},
}
# Only when the stage plot is one of the missing things (tier 3).
_PLOT_CLAUSE = {"en": "Without a stage plot you get a generic patch, and we sort out the rest at sound check.",
                "es": "Sin plano de escenario, les armamos un patch genérico y resolvemos el resto en la prueba de sonido."}
_TIER_ASK = {
    15: {"en": ("The form takes about five minutes, and you can upload every file there:",
                "If you've already sent this over, just ignore this note. You can also reply to this email."),
         "es": ("El formulario toma unos cinco minutos, y ahí pueden subir todos sus archivos:",
                "Si ya nos lo enviaron, ignoren este mensaje. También pueden responder a este correo.")},
    10: {"en": ("The form takes about five minutes:",
                "If you've already sent this over, just ignore this note. You can also reply to this email."),
         "es": ("El formulario toma unos cinco minutos:",
                "Si ya nos lo enviaron, ignoren este mensaje. También pueden responder a este correo.")},
    7:  {"en": ("Everything goes in here:",
                "If you've already sent this over, just ignore this note. You can also reply to this email."),
         "es": ("Todo va aquí:",
                "Si ya nos lo enviaron, ignoren este mensaje. También pueden responder a este correo.")},
    5:  {"en": ("Everything goes in here:",
                "Or reply to this email with the details and we'll enter them for you."),
         "es": ("Todo va aquí:",
                "O respondan a este correo con los datos y nosotros los ingresamos.")},
    2:  {"en": ("Still the fastest way:",
                "Or reply to this email with the details and we'll enter them for you."),
         "es": ("La forma más rápida sigue siendo esta:",
                "O respondan a este correo con los datos y nosotros los ingresamos.")},
    3:  {"en": ("Still the fastest way:",
                "Or reply to this email with the details and we'll enter them for you."),
         "es": ("La forma más rápida sigue siendo esta:",
                "O respondan a este correo con los datos y nosotros los ingresamos.")},
    1:  {"en": ("Last call:",
                "Reply to this email today with whatever you've got, and we'll get it in."),
         "es": ("Última llamada:",
                "Respondan a este correo hoy con lo que tengan y lo ingresamos.")},
}
_TIER_SUBJECT = {
    15: {"with": "Two weeks out — your show details by {deadline}",
         "without": "Two weeks out — we still need your show details"},
    10: {"with": "Reminder — we need your show details by {deadline}",
         "without": "Reminder — we still need your show details"},
    7:  {"with": "One week out — your show details by {deadline}",
         "without": "One week out — we still need your show details"},
    5:  {"with": "Five days out — we still need your show details",
         "without": "Five days out — we still need your show details"},
    2:  {"with": "Two days out — we still need your show details",
         "without": "Two days out — we still need your show details"},
    3:  {"with": "Three days out — your show details by {deadline}",
         "without": "Three days out — we still need your show details"},
    1:  {"with": "Last call — your show details by {deadline}",
         "without": "Last call — we still need your show details"},
}
_SIGNOFF = {"en": "Thanks,\n3CDC Events / Production",
            "es": "Gracias,\n3CDC Eventos / Producción"}


def tier_key(tier):
    """The copy tier for a days_before value: exact when it's one of ours,
    otherwise the nearest one (ties go to the wider window). A tier added
    upstream always lands on a real body instead of falling through to
    nothing."""
    try:
        tier = int(tier)
    except (TypeError, ValueError):
        return 7
    return min(REMINDER_TIERS, key=lambda k: (abs(k - tier), -k))


def missing_for_show(cur, show_id):
    """What this show is still missing, as MISSING_LABELS codes — no
    submission at all is the whole form; otherwise whatever the promoted
    columns and the raw form data say we never got. Capped at three: a band
    reads this on a phone, and a list of everything reads like a form."""
    cur.execute("""SELECT performers, monitors, contact_phone, data
                   FROM submissions WHERE show_id = %s
                   ORDER BY submitted_at DESC, id DESC LIMIT 1""", (show_id,))
    sub = cur.fetchone()
    if not sub:
        return ["form"]
    d = sub.get("data") or {}
    def blank(v):
        return not str(v or "").strip()
    out = []
    if blank(d.get("stage_plot_file")) and blank(d.get("stage_plot_desc")):
        out.append("plot")
    if blank(d.get("stage_escort_cell")):
        out.append("escort")
    if not sub.get("performers"):
        out.append("performers")
    if sub.get("monitors") is None:
        out.append("monitors")
    if blank(sub.get("contact_phone")):
        out.append("phone")
    return out[:3] or ["confirm"]


def missing_text(codes, lang="en"):
    parts = [MISSING_LABELS[c][lang] for c in (codes or []) if c in MISSING_LABELS]
    if not parts:
        parts = [MISSING_LABELS["confirm"][lang]]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + (" y " if lang == "es" else " and ") + parts[-1]


def chase_paragraph(tier, lang, venue, show_date, link, codes, deadline=None, set_line=""):
    """The "what we still need, by when, and where to put it" part of a
    reminder — no greeting, no sign-off. 2026-09-24 research #3: the week-out
    schedule email carries THESE bytes for a show that hasn't answered, so the
    old T-7 nudge folds into it instead of being reworded a second time and
    sent alongside. `set_line` is blank from there — the schedule block above
    it already prints the set."""
    key = tier_key(tier)
    lead = _TIER_LEAD[key][lang].format(venue=venue or "",
                                        day=ve.band_date(show_date, lang=lang),
                                        missing=missing_text(codes, lang))
    then = _TIER_THEN[key][lang]
    if "{deadline}" in then:
        then = then.format(deadline=ve.band_date(deadline, lang=lang)) if deadline else ""
    if key == 3 and "plot" in (codes or []):
        then = f"{then} {_PLOT_CLAUSE[lang]}".strip()
    intro, after = _TIER_ASK[key][lang]
    return (f"{(lead + ' ' + then).strip()}\n\n"
            + (f"{set_line}\n\n" if set_line else "")
            + f"{intro}\n\n{link}\n\n{after}")


def _reminder_half(tier, lang, band, contact_name, venue, show_date, link, codes,
                   deadline, set_times=None):
    gname = _greeting_contact_name(contact_name, band)
    if lang == "es":
        greeting = f"Hola {gname} y {band}" if gname else f"Hola {band}"
    else:
        greeting = f"Hello {gname} and {band}" if gname else f"Hello {band}"
    # research #7: what they're actually playing, when the booking knows it.
    set_txt = ve.set_line(*(set_times or ("", "", "")), lang=lang)
    return (f"{greeting},\n\n"
            + chase_paragraph(tier, lang, venue, show_date, link, codes, deadline,
                              set_line=set_txt)
            + f"\n\n{_SIGNOFF[lang]}")


def build_reminder(tier, band, contact_name, venue, show_date, link, codes,
                   deadline=None, bilingual=False, set_times=None):
    """(subject, body) for one reminder tier. `codes` come from
    missing_for_show, `deadline` from advance_db.advance_deadline — the same
    date the welcome printed. A deadline that isn't actually before the show
    (a show booked inside the window, or already today) is dropped rather than
    emailed as a date that reads wrong. `set_times` is the booking's
    (event_start, event_end, set_time) for the set line (research #7).
    bilingual appends the Spanish half, same shape as the welcome."""
    if deadline and show_date and deadline >= show_date:
        deadline = None
    shape = _TIER_SUBJECT[tier_key(tier)]
    base = (shape["with"].format(deadline=ve.band_date(deadline)) if deadline
            else shape["without"])
    subject = ve.band_subject(base, band, venue, show_date)
    body = _reminder_half(tier, "en", band, contact_name, venue, show_date,
                          link, codes, deadline, set_times)
    if bilingual:
        body_es = _reminder_half(tier, "es", band, contact_name, venue, show_date,
                                 f"{link}?lang=es", codes, deadline, set_times)
        sep = "─" * 42
        body = f"{body}\n\n{sep}\nESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}"
    return subject, body


def _bill_order(a):
    """Earliest set start first, untimed acts last, then by name."""
    return (db.parse_clock(a["set_start"]) is None,
            db.parse_clock(a["set_start"]) or 0, a["name"])


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
        acts.sort(key=_bill_order)

    summary = []
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            removed = db.pending_removal_idents(cur)
        bill_checked = set()   # 2026-09-21 sweep (FLOW-15): bill keys already topped up from bookings
        today = dt.date.today()
        for r in rows:
            try:
                name = r["name"]
                venue = r.get("venue")
                show_date = parse_date(r.get("show_date"))
                # 2026-09-21 sweep (DBB-6): an undated row minted a NEW show every run
                # (NULL never hits uq_shows_booking) — and there's nothing to welcome.
                if not show_date:
                    print(f"  skip {name}: no parseable show date ({r.get('show_date')!r})",
                          file=sys.stderr)
                    continue
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
                # 2026-09-21 sweep (FLOW-15): the bill comes from bookings too, not just
                # this batch — an act welcomed on another day still belongs on it. Batch
                # rows win for acts they carry; bookings only add the missing ones.
                bkey = _bill_key(r)
                if bkey not in bill_checked and venue and show_date:
                    bill_checked.add(bkey)
                    booked = []
                    if not db.is_third_party(series) or (r.get("event_name") or "").strip():
                        try:
                            with conn.cursor() as cur:
                                booked = db.acts_for_event(cur, venue, show_date, series=series,
                                                           event_name=r.get("event_name"))
                        except Exception as e:  # noqa: BLE001 — the batch-only bill still stands
                            conn.rollback()
                            print(f"[draft_emails] bill lookup failed for {venue} {show_date}: {e!r}",
                                  file=sys.stderr)
                            booked = []
                    acts = bills.setdefault(bkey, [])
                    have = {db.normalize(a["name"]) for a in acts}
                    for b in booked:
                        bname = b.get("name") or ""
                        if (not bname or db.normalize(bname) in have
                                or db.removal_ident(bname, venue, show_date) in removed):
                            continue
                        acts.append({"name": bname, "set_time": b.get("set_time") or "",
                                     "set_start": b.get("set_start") or ""})
                        have.add(db.normalize(bname))
                    acts.sort(key=_bill_order)
                bill = bills.get(bkey, [])
                # 2026-09-24 research #2: ONE deadline — advance_db.advance_deadline
                # is the only definition, so the welcome, every reminder tier and the
                # reminder subject all print the same date for a show.
                with conn.cursor() as cur:
                    booking_row = db.find_booking(cur, venue, show_date, name)
                deadline_date = db.advance_deadline(
                    show_date, booking_row.get("created_at") if booking_row else None, venue=venue)
                deadline = ve.band_date(deadline_date)
                deadline_es = ve.band_date(deadline_date, lang="es")

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
                       if venue in ("Fountain Square", "Washington Park", "Elm Street Plaza") else None)
                if eng:
                    day_of_contact = eng
                    engineer_contact = True
                elif r.get("lead_name"):
                    day_of_contact = r["lead_name"] + (
                        f" ({r['lead_phone']})" if r.get("lead_phone") else "")

                email_extra = {}
                if venue == "Washington Park":
                    # 2026-09-21 sweep (MAIL-11): the same stage the band's form resolves —
                    # a blank location on a Porch/Bandstand series follows SERIES_LOCATION.
                    loc_name = (forms_config.resolve_wp_location(venue, r.get("location"), series)
                                or (r.get("location") or ""))
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
                # 2026-09-24 research #7: the band gets the actual set, not just
                # its length — event_start/event_end ARE the set times (the
                # booking page derives the rest of the day from them).
                set_line = ve.set_line(r.get("event_start"), r.get("event_end"), r.get("set_time"))

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

                # Memorial Hall (Brian, 2026-09-29): the day-of contact is the FOH mix on
                # the staffing sheet that day (never the booking's lead), and the Day
                # Schedule is the FULL Memo day — every time staff have filled in, the
                # same rows the Prod Adv doc prints — not the five-row generic block.
                if venue == "Memorial Hall" and show_id:
                    email_extra["backline_text"] = ve.MEMO_BACKLINE_DEFAULT
                    email_extra["crew_text"] = ve.MEMO_CREW_DEFAULT
                    email_extra["parking_text"] = ve.MEMO_PARKING_DEFAULT
                    try:
                        import memo_doc
                        with conn.cursor() as cur:
                            memo_vals, _info = memo_doc.values_for(cur, show_id)
                        foh = memo_doc.foh_contact(show_date, [r.get("event_name"), name])
                    except Exception as e:  # noqa: BLE001 — fall back to the plain email
                        conn.rollback()
                        print(f"[draft_emails] Memo schedule/contact failed for {name} {show_date}: {e!r}",
                              file=sys.stderr)
                        memo_vals, foh = None, None
                    # the "don't advance with them" note is for part-time crew, not the
                    # advancing contact working the desk that night
                    if memo_vals:
                        email_extra["backline_text"] = ve.memo_backline_text(memo_vals.acts)
                        email_extra["parking_text"] = ve.memo_parking_text(memo_vals.acts)
                        try:
                            email_extra["crew_text"] = ve.memo_crew_text(
                                memo_doc.cost_model_crew(show_date, r.get("event_name") or name))
                        except Exception as e:  # noqa: BLE001
                            print(f"[draft_emails] cost model crew failed for {name}: {e!r}", file=sys.stderr)
                    day_of_contact = foh or ""
                    engineer_contact = bool(foh) and fs.ADVANCING_CONTACT.split(" (")[0] not in foh
                    rows = ve.memo_schedule_rows(memo_vals.event) if memo_vals else []
                    if rows:
                        schedule_block = "\n".join(rows + [ve.MEMO_SCHEDULE_NOTE])
                        schedule_locked = True     # the note above replaces the generic asterisk lines
                        set_line = ""              # the sets are in the schedule

                bill_block = ""
                if len(bill) > 1:
                    lines = ["The bill:"]
                    for a in bill:
                        when = a.get("set_start") or "time TBD"
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
                    set_line_es = ve.set_line(r.get("event_start"), r.get("event_end"),
                                              r.get("set_time"), lang="es")
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

                payload = _prefill_payload(artist_id, venue, show_date, series, r.get("location"),
                                           r.get("contact_name"), r.get("contact_email") or r.get("email"),
                                           show_id=show_id)
                token = _token(payload)
                # 2026-09-21 sweep (MAIL-1): a timed token differs every second, so key
                # the short code on payload + day — one code per row per day, not one
                # new short_links row per row on every package run.
                link_key = ("draft:" + dt.date.today().isoformat() + ":"
                            + json.dumps(payload, sort_keys=True, separators=(",", ":")))
                with conn.cursor() as cur:
                    short_code = db.get_or_create_short_link(cur, token, key=link_key)
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
                    blocks=blocks_en, common_requirements=ve.common_requirements_for(venue),
                    engineer_contact=engineer_contact,
                    personal_note=(f"{personal_note_en}\n\n" if personal_note_en else ""),
                    event_name=r.get("event_name") or "",
                    # 2026-09-21 sweep (MAIL-8): "3rd Party" is an internal class, not a
                    # show name — blank it so show_label falls back to the event name.
                    series=("" if (db.is_third_party(series) or ve.is_standalone_series(series)) else (series or "")),
                    show_date=us_date(show_date),
                    # 2026-09-24 research #14: every band-facing subject ends with this.
                    subject_key=ve.subject_key(name, venue, show_date),
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
                        deadline=deadline_es,
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

                # 2026-09-21 sweep (MAIL-2): venue + show id in the name — one band at two
                # venues on one date (or two same-slug acts) no longer overwrite one file.
                sid = r.get("show_id") or show_id   # the lifecycle's own id first
                fname = (f"{slug(name)}__{show_date.isoformat() if show_date else 'nodate'}"
                         f"__{slug(venue)}__s{sid}__{kind.lower()}.md")
                (out_dir / fname).write_text(body)
                summary.append((kind, name, venue,
                                show_date.isoformat() if show_date else "?",
                                email or "(no email)", fname))
            except Exception as e:  # noqa: BLE001 — one bad row must never sink the whole batch (audit 2026-09-16 #15)
                # 2026-09-21 sweep (MAIL-12): name + date, so the lifecycle can pin
                # this line to the show's "didn't render" reason.
                print(f"[draft_emails] {r.get('name')} {r.get('show_date')}: {e!r}", file=sys.stderr)
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


def _prefill_payload(artist_id, venue, show_date, series=None, location=None,
                     contact_name=None, contact_email=None, show_id=None):
    """contact_name/contact_email are the STAFF-typed booking contact (Brian,
    2026-09-09) — carried into the band's own form as an editable starting
    value at /f/<token>, same as venue/date/location already are. Never
    locked: a band can always correct what staff typed.
    2026-09-21 sweep (IDENT-6): show_id rides along so /f/ re-seeds the show's
    CURRENT venue/date/artist if staff moved it after this link went out."""
    return {"a": artist_id,
            "s": {"venue": venue,
                  "date": show_date.isoformat() if show_date else None,
                  "series": series or None,
                  "location": location or None,
                  "contact_name": (contact_name or "").strip() or None,
                  "contact_email": (contact_email or "").strip() or None,
                  "show_id": show_id}}


def _token(payload):
    # 2026-09-21 sweep (MAIL-1): TIMED signer, same class + salt as app._signer —
    # app.read_prefill_token only accepts timed tokens since d9acd6b, so the old
    # untimed one opened every welcome link on a blank, unaddressed form.
    from itsdangerous import URLSafeTimedSerializer
    secret = os.environ.get("ADVANCE_SECRET", "dev-insecure-secret-change-me")
    signer = URLSafeTimedSerializer(secret, salt="advance-prefill")
    return signer.dumps(payload)


def _q(s):
    from urllib.parse import quote
    return quote(s or "")


if __name__ == "__main__":
    main()
