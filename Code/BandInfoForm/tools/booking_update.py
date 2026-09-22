#!/usr/bin/env python3
"""Booking-edit notification (Brian, 2026-09-14).

Editing a logged booking's band-facing fields (date, venue, location, artist
name, set length, load-in/soundcheck/start/end/curfew) queues one
email per booking — the old -> new diff — sent at the NEXT daily lifecycle
run, never immediately, so a same-day string of corrections collapses into
one email instead of several. 2026-09-21 sweep (MAIL-6): it goes only to a
band that has already been contacted (welcomed, responded, or a manual band
advance), for any show that hasn't passed — not on the 21-day window. Edits
made before the welcome (or held draft) is built ride in it instead and are
resolved as carried. Internal-only fields (contact info, entered_by,
email_note, lead/paying-band, series, event name) never queue anything.
Addressed like every other band email: the artist's current address (the
booking contact as fallback), plus the series CC; bilingual for Salsa.
See advance_db.update_booking / due_booking_edits / BAND_FACING_FIELDS and
app.py's /booking/<id>/edit route.

    python3 booking_update.py --dry-run     # print what's due, never send
    python3 booking_update.py --send-due    # send everything due (lifecycle calls this)
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
import advance_db as db
sys.path.insert(0, str(HERE))
import venue_email as ve

FIELD_LABELS = {
    "event_date": "Date", "venue": "Venue", "location": "Location",
    "artist_name": "Artist / Band", "set_time": "Set length",
    "load_in": "Load-in", "soundcheck": "Sound check",
    "event_start": "Start", "event_end": "End", "curfew": "Curfew",
}
# 2026-09-21 sweep (MAIL-4): Salsa's Spanish half — same words dayahead uses.
FIELD_LABELS_ES = {
    "event_date": "Fecha", "venue": "Lugar", "location": "Ubicación",
    "artist_name": "Artista / Banda", "set_time": ve.SET_LENGTH_LABEL_ES,
    "load_in": "Carga", "soundcheck": "Prueba de sonido",
    "event_start": "Inicio", "event_end": "Fin", "curfew": "Hora límite",
}


def _fmt(field, v, lang="en"):
    if not v:
        return "(sin definir)" if lang == "es" else "(not set)"
    if field == "event_date":
        try:
            d = dt.date.fromisoformat(v[:10])
            return d.strftime("%d/%m/%Y") if lang == "es" else d.strftime("%A, %B %-d")
        except ValueError:
            return v
    return v


# The order a band reads a day in, not whatever order the diff came out of the
# database (Brian, 2026-09-15: the email listed Curfew before Load-in).
FIELD_ORDER = ["event_date", "venue", "location", "artist_name", "load_in",
               "soundcheck", "event_start", "event_end", "curfew", "set_time"]


def build_email(r):
    changes = r["changes"]
    ordered = sorted(changes.items(),
                     key=lambda kv: (FIELD_ORDER.index(kv[0])
                                     if kv[0] in FIELD_ORDER else len(FIELD_ORDER), kv[0]))
    lines = [f"  {FIELD_LABELS.get(f, f)}: {_fmt(f, d['old'])}  ->  {_fmt(f, d['new'])}"
             for f, d in ordered]
    subject = (f"Updated booking details — {r['artist_name']} at {r['venue']} "
               f"({r['event_date'].strftime('%-m/%-d')})")
    body = (f"Hello {r['artist_name']},\n\n"
            f"A couple of details on your booking at {r['venue']} on "
            f"{r['event_date'].strftime('%A, %B %-d')} changed:\n\n"
            + "\n".join(lines) +
            "\n\nEverything else on file for you stays the same. Reply to this email "
            "if anything here doesn't look right.\n\n3CDC Events / Production")
    # 2026-09-21 sweep (MAIL-4): a bilingual series (Salsa) gets the Spanish
    # half under the English one, same shape as its welcome and reminders.
    if r.get("series") and ve.is_bilingual_series(r["series"]):
        lines_es = [f"  {FIELD_LABELS_ES.get(f, FIELD_LABELS.get(f, f))}: "
                    f"{_fmt(f, d['old'], 'es')}  ->  {_fmt(f, d['new'], 'es')}" for f, d in ordered]
        body_es = (f"Hola {r['artist_name']},\n\n"
                   f"Cambiaron algunos detalles de su presentación en {r['venue']} el "
                   f"{r['event_date'].strftime('%d/%m/%Y')}:\n\n"
                   + "\n".join(lines_es) +
                   "\n\nTodo lo demás que tenemos registrado sigue igual. Si algo aquí no se ve "
                   "bien, respondan a este correo.\n\n3CDC Eventos / Producción")
        sep = "─" * 42
        body = f"{body}\n\n{sep}\nESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}"
    return subject, body


def send_due(fail=None):
    """Send every pending booking-edit notification. `fail(booking_id, kind,
    error)` is the lifecycle's failure recorder. Returns a run summary list
    (mirrors dayahead.send_due's shape)."""
    import mailer
    sent = []
    with db.get_conn() as conn, conn.cursor() as cur:
        db.skip_stale_booking_edits(cur)
        conn.commit()
    with db.get_conn() as conn, conn.cursor() as cur:
        rows = db.due_booking_edits(cur)
    for r in rows:
        # audit 2026-09-16 #14: fail() records against shows(id) — passing
        # the booking_id there either violated the FK or, worse, silently
        # recorded the failure against an unrelated show that happened to
        # share that numeric id. Resolve the real show_id once per row;
        # a booking with no show yet (the pipeline hasn't created one) has
        # nothing to record a failure against, so fail() is skipped, not
        # misdirected.
        show_id = None
        with db.get_conn() as conn, conn.cursor() as cur:
            show = db.show_for_booking(cur, r["artist_name"], r["venue"], r["event_date"])
            show_id = show["id"] if show else None

        def _fail(kind, error):
            if fail and show_id:
                fail(show_id, kind, error)

        # 2026-09-21 sweep (MAIL-7): the artist's current address first, same
        # as every other band email; the booking contact only as a fallback.
        email = (r.get("artist_email") or r.get("contact_email") or "").strip()
        if not email:
            # 2026-09-21 sweep (PRIOR-16): due_booking_edits already drops silent
            # 3rd-party bookings, so a 3rd-party row here opted in — say so.
            _fail("booking_update", "no contact email on file")
            with db.get_conn() as conn, conn.cursor() as cur:
                db.mark_booking_edit_sent(cur, r["edit_id"], False, "no contact email on file")
                conn.commit()
            continue
        try:
            subject, body = build_email(r)
        except Exception as e:  # noqa: BLE001
            _fail("booking_update", f"couldn't build the email: {e!r}")
            continue
        # 2026-09-21 sweep (MAIL-4): the Salsa series CC, like every other band email.
        ok, err = mailer.send(ve.with_extra_recipients(email, r.get("series")), subject, body=body)
        # 2026-09-21 sweep (PRIOR-13): a timeout may have delivered — resolve, don't re-send.
        unknown = (not ok) and mailer.outcome_unknown(err)
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_booking_edit_sent(cur, r["edit_id"], ok, err, unknown=unknown)
            conn.commit()
        if ok:
            sent.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                         "event_date": r["event_date"].strftime("%m/%d/%Y")})
        elif unknown:
            _fail("booking_update_unknown", err)
        else:
            _fail("booking_update", err)
    return sent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--send-due", action="store_true")
    args = ap.parse_args()
    if args.send_due:
        print(send_due())
        return
    with db.get_conn() as conn, conn.cursor() as cur:
        rows = db.due_booking_edits(cur)
    for r in rows:
        subject, body = build_email(r)
        to = ve.with_extra_recipients((r.get("artist_email") or r.get("contact_email") or ""), r.get("series"))
        print(f"To: {to}\nSubject: {subject}\n\n{body}\n{'=' * 60}")


if __name__ == "__main__":
    main()
