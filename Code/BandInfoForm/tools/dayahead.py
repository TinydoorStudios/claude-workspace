#!/usr/bin/env python3
"""Day-before confirmation (review 2026-09-14, E5 — Brian's call).

Every responded show playing TOMORROW gets one "see you tomorrow" email at
the 9am lifecycle run: the day schedule as booked, the venue's load-in /
parking paragraph (same text as the welcome), the day-of contact (the
staffing sheet's mix engineer, then the booking Lead), and a short recap of
what's on file. Finalized or not — the thank-you on Mark Finalized stays the
sign-off; this is the reminder. Bilingual for a series in
venue_email.BILINGUAL_SERIES.

Recorded on the show (dayahead_sent_at / dayahead_error). A failure goes
through the same send_failures path as any other send (one alert per
show/kind/day) and is retried by the next run only while the show is still
tomorrow, so nothing ever goes out late as "tomorrow".

    python3 dayahead.py --dry-run --show-id 123     # print, never send
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import fieldspec as fs
import staffing
import venue_email as ve

SCHEDULE_ROWS = [("load_in", "Load-in"), ("soundcheck", "Sound check"),
                 ("event_start", "Start"), ("event_end", "End"), ("curfew", "Curfew")]
SCHEDULE_ROWS_ES = {"load_in": "Carga", "soundcheck": "Prueba de sonido",
                    "event_start": "Inicio", "event_end": "Fin", "curfew": "Hora límite"}


def due_shows(cur):
    cur.execute(
        r"""SELECT DISTINCT ON (s.id)
                   s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                   a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                   b.location, b.lead_name, b.lead_phone, b.contact_name, b.event_name,
                   b.load_in, b.soundcheck, b.event_start, b.event_end, b.curfew
            FROM shows s JOIN artists a ON a.id = s.artist_id
            LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                   AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
            -- audit 2026-09-16 #23: catches today too, not just tomorrow —
            -- a missed 9am run yesterday (the lifecycle didn't fire) used
            -- to mean the day-before for a show now happening TODAY never
            -- goes out at all, since it's never "tomorrow" again once the
            -- date passes.
            WHERE s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 1
              AND s.cancelled_at IS NULL AND s.held_at IS NULL
              AND s.dayahead_sent_at IS NULL
              AND (s.responded_at IS NOT NULL
                   OR EXISTS (SELECT 1 FROM submissions x WHERE x.show_id = s.id))
              AND NOT """ + db.THIRD_PARTY_SILENT_SQL + r"""
            ORDER BY s.id, b.id DESC NULLS LAST""")
    return cur.fetchall()


def _schedule_lines(r, lang="en"):
    locked = ve.crew_schedule_for(r["venue"], r["series"]) if r.get("series") else []
    if locked:
        return [(label, t or "TBD") for label, t in locked]
    out = []
    for key, label in SCHEDULE_ROWS:
        v = (r.get(key) or "").strip()
        if lang == "es":
            label = SCHEDULE_ROWS_ES[key]
            v = v or fs.SCHEDULE_TBD_ES
        else:
            v = v or fs.SCHEDULE_TBD
        out.append((label, v))
    return out


def _day_of_contact(r):
    eng = (staffing.engineer_for(r["venue"], r["show_date"],
                                 series=r.get("series"),
                                 event_name=r.get("event_name"),
                                 artist_name=r.get("artist_name"),
                                 event_start=r.get("event_start"))
           if r["venue"] in ("Fountain Square", "Washington Park") else None)
    if eng:
        return eng, True
    if r.get("lead_name"):
        return r["lead_name"] + (f" ({r['lead_phone']})" if r.get("lead_phone") else ""), False
    return None, False


def _greeting(r, es=False):
    """Same rule as the welcome (draft_emails._greeting_contact_name): first
    name only, and no contact at all when the band name already contains it
    ('Hello Patsy Meyer and Patsy Meyer and Groove Latin' was the dry run)."""
    band = r["artist_name"]
    contact = (r.get("contact_name") or "").strip()
    first = contact.split()[0] if contact else ""
    if not first or contact.lower() in band.lower() or first.lower() in band.lower().split():
        return f"Hola {band}" if es else f"Hello {band}"
    return f"Hola {first} y {band}" if es else f"Hello {first} and {band}"


_FORM_REFS = {
    "en": [r"The load-in process at [^.]*has changed — please review the attached document and acknowledge understanding on the form\.\s*",
           r"\s*Need more validations or large-vehicle parking\? Note it on the form\.", r"\s*Note any large-vehicle needs on the form\."],
    "es": [r"El proceso de carga en [^.]*ha cambiado — por favor revisen el documento adjunto y confirmen que lo entendieron en el formulario\.\s*",
           r"\s*¿Necesitan más validaciones o espacio para vehículos grandes\? Indíquenlo en el formulario\.",
           r"\s*Indiquen en el formulario si necesitan espacio para vehículos grandes\."],
}


def _without_form_refs(text, lang="en"):
    """The day-before email goes to a band that already advanced — drop the
    welcome copy's 'do it on the form' sentences."""
    import re
    for pat in _FORM_REFS[lang]:
        text = re.sub(pat, "", text)
    return text


def _recap_lines(r):
    try:
        from finalize_thankyou import build_recap
        res = build_recap(r["venue"], r["show_date"], r["artist_name"], series=r.get("series"))
    except Exception:  # noqa: BLE001 — recap is a nicety, never a blocker
        return []
    return res[1] if res else []


def build_email(r):
    d = r["show_date"]
    day = d.strftime("%A, %B ") + str(d.day)
    # audit 2026-09-16 #23: due_shows now also catches a show happening
    # TODAY (a missed run yesterday) — "tomorrow" would be wrong in that
    # case, sent the day of the show.
    when_word = "today" if d == dt.date.today() else "tomorrow"
    subject = f"{when_word.title()} at {r['venue']} — {r['artist_name']} ({d.strftime('%-m/%-d')})"
    contact, is_engineer = _day_of_contact(r)
    extra = {}
    if r["venue"] == "Washington Park":
        loc = r.get("location") or ""
        extra = {"location": loc or "confirm with your day-of contact"}
    # audit 2026-09-16 #23: without third_party=, a 3rd-party show's
    # day-before wrongly kept the touring-band garage-QR/validation
    # paragraph even at a venue (FSQ) with a dedicated 3rd-party override.
    third_party = db.is_third_party(r.get("series"))
    blocks = ve.blocks_for(r["venue"], series=r.get("series"), third_party=third_party, **extra)
    if not contact:
        blocks = ve.without_text_on_arrival(blocks, lang="en")
    sched = "\n".join(f"  {t}    {label}" for label, t in _schedule_lines(r))
    recap = _recap_lines(r)
    greeting = _greeting(r)
    body = (f"{greeting},\n\n"
            f"Quick confirmation for {when_word}, {day}, at {r['venue']}"
            f"{(' — ' + blocks['location']) if blocks.get('location') else ''}.\n\n"
            f"Day Schedule:\n{sched}\n\n")
    if contact:
        body += f"Day-of Contact: {contact}\n"
        if is_engineer:
            body += "  Please do not call them before show day; they are part-time staff.\n"
        body += "\n"
    body += f"{_without_form_refs(blocks['load_in'])}\n\n"
    if recap:
        body += "What we have on file for you:\n" + "\n".join(f"  {k}: {v}" for k, v in recap) + "\n\n"
    see_you = "See you today" if when_word == "today" else "See you tomorrow"
    body += ("If anything has changed — headcount, gear, arrival time — reply to this email today "
             f"and we'll update it.\n\n{see_you},\n3CDC Events / Production")
    if r.get("series") and ve.is_bilingual_series(r["series"]):
        blocks_es = ve.blocks_for(r["venue"], series=r.get("series"), lang="es",
                                  third_party=third_party, **extra)
        if not contact:
            blocks_es = ve.without_text_on_arrival(blocks_es, lang="es")
        sched_es = "\n".join(f"  {t}    {label}" for label, t in _schedule_lines(r, lang="es"))
        greeting_es = _greeting(r, es=True)
        when_word_es = "hoy" if when_word == "today" else "mañana"
        see_you_es = "Nos vemos hoy" if when_word == "today" else "Nos vemos mañana"
        body_es = (f"{greeting_es},\n\n"
                   f"Confirmación rápida para {when_word_es}, {d.strftime('%d/%m/%Y')}, en {r['venue']}.\n\n"
                   f"Horario del día:\n{sched_es}\n\n")
        if contact:
            body_es += f"Contacto del día del evento: {contact}\n\n"
        body_es += (f"{_without_form_refs(blocks_es['load_in'], 'es')}\n\n"
                    "Si algo cambió — número de personas, equipo, hora de llegada — respondan a este "
                    f"correo hoy y lo actualizamos.\n\n{see_you_es},\n3CDC Eventos / Producción")
        sep = "─" * 42
        body = f"{body}\n\n{sep}\nESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}"
    return subject, body


def send_due(fail=None):
    """Send every due day-before confirmation. `fail(show_id, kind, error)`
    is the lifecycle's failure recorder. Returns [{artist_name, venue,
    show_date}] for the run summary."""
    import mailer
    sent = []
    with db.get_conn() as conn, conn.cursor() as cur:
        rows = due_shows(cur)
    for r in rows:
        email = (r.get("email") or "").strip()
        if not email:
            if fail and not db.is_third_party(r.get("series")):
                fail(r["show_id"], "dayahead", "no contact email on file")
            continue
        try:
            subject, body = build_email(r)
        except Exception as e:  # noqa: BLE001
            if fail:
                fail(r["show_id"], "dayahead", f"couldn't build the email: {e!r}")
            continue
        # audit 2026-09-16 #17: link the venue's standing docs instead of
        # re-attaching them — only the welcome attaches the real file.
        doc_links = ve.venue_doc_links_text(r["venue"])
        if doc_links:
            body = f"{body}\n\n{doc_links}"
        ok, err = mailer.send(email, subject, body=body)
        with db.get_conn() as conn, conn.cursor() as cur:
            if ok:
                cur.execute("UPDATE shows SET dayahead_sent_at = now(), dayahead_error = NULL WHERE id=%s",
                            (r["show_id"],))
            else:
                cur.execute("UPDATE shows SET dayahead_error = %s WHERE id=%s", (err, r["show_id"]))
            conn.commit()
        if ok:
            sent.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                         "show_date": r["show_date"].strftime("%m/%d/%Y")})
        elif fail:
            fail(r["show_id"], "dayahead", err)
    return sent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-id", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--send-due", action="store_true")
    args = ap.parse_args()
    if args.send_due:
        print(send_due())
        return
    with db.get_conn() as conn, conn.cursor() as cur:
        rows = [r for r in due_shows(cur) if not args.show_id or r["show_id"] == args.show_id]
        if args.show_id and not rows:
            cur.execute(
                r"""SELECT DISTINCT ON (s.id) s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                           a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                           b.location, b.lead_name, b.lead_phone, b.contact_name, b.event_name,
                           b.load_in, b.soundcheck, b.event_start, b.event_end, b.curfew
                    FROM shows s JOIN artists a ON a.id = s.artist_id
                    LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                           AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
                    WHERE s.id = %s ORDER BY s.id, b.id DESC NULLS LAST""", (args.show_id,))
            rows = cur.fetchall()
    for r in rows:
        subject, body = build_email(r)
        print(f"To: {r.get('email')}\nSubject: {subject}\n\n{body}\n{'=' * 60}")


if __name__ == "__main__":
    main()
