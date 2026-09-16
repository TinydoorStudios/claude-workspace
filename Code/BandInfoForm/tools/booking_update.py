#!/usr/bin/env python3
"""Booking-edit notification (Brian, 2026-09-14).

Editing a logged booking's band-facing fields (date, venue, location, artist
name, set length, load-in/soundcheck/start/end/curfew) queues one
email per booking — the old -> new diff — sent at the NEXT daily lifecycle
run, never immediately, so a same-day string of corrections collapses into
one email instead of several. Only fires while the show is still inside the
21-day window; internal-only fields (contact info, entered_by, email_note,
lead/paying-band, series, event name) never queue anything.
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

FIELD_LABELS = {
    "event_date": "Date", "venue": "Venue", "location": "Location",
    "artist_name": "Artist / Band", "set_time": "Set length",
    "load_in": "Load-in", "soundcheck": "Sound check",
    "event_start": "Start", "event_end": "End", "curfew": "Curfew",
}


def _fmt(field, v):
    if not v:
        return "(not set)"
    if field == "event_date":
        try:
            return dt.date.fromisoformat(v[:10]).strftime("%A, %B %-d")
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

        email = (r.get("contact_email") or "").strip()
        if not email:
            if not db.is_third_party(r.get("series")):
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
        ok, err = mailer.send(email, subject, body=body)
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_booking_edit_sent(cur, r["edit_id"], ok, err)
            conn.commit()
        if ok:
            sent.append({"artist_name": r["artist_name"], "venue": r["venue"] or "",
                         "event_date": r["event_date"].strftime("%m/%d/%Y")})
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
        print(f"To: {r.get('contact_email')}\nSubject: {subject}\n\n{body}\n{'=' * 60}")


if __name__ == "__main__":
    main()
