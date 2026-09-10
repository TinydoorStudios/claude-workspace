#!/usr/bin/env python3
"""Shared DB layer for the Band Advance system.

Everything that touches Postgres goes through here: the Flask form (best-effort
writes on submit), the email-drafting tool, the doc-fill tool, and the search view.
Uses psycopg 3. Connection string comes from ADVANCE_DB_URL, e.g.
    postgresql://advance:<pw>@127.0.0.1:5433/advance
"""
import os
import re
import datetime as dt

import psycopg
from psycopg.rows import dict_row

DB_URL = os.environ.get(
    "ADVANCE_DB_URL", "postgresql://advance:advance@127.0.0.1:5433/advance"
)

# ── helpers ────────────────────────────────────────────────────────────────

def normalize(name: str) -> str:
    """Same rule as the generated match_key column: lower + collapse whitespace."""
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


def to_bool(v):
    """Map the form's Yes/No selects to a real boolean; leave anything else None."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("yes", "y", "true", "1"):
        return True
    if s in ("no", "n", "false", "0"):
        return False
    return None


def to_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def to_date(v):
    if not v:
        return None
    try:
        return dt.date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        return None


def get_conn():
    # timestamps stored as TIMESTAMPTZ (UTC); display them in Cincinnati time
    return psycopg.connect(
        DB_URL, row_factory=dict_row,
        options="-c timezone=America/New_York",
    )


# ── upserts ────────────────────────────────────────────────────────────────

def upsert_artist(cur, name, email=None, phone=None, known_id=None):
    """Insert the band by exact name; on a match_key collision keep the existing
    display name and only fill in newer contact info. Returns artist id.

    known_id (Brian, 2026-09-09): the band's own form no longer locks Band /
    Group Name read-only — it's editable like every other carried-over
    answer. That means a submission from a prefill link now identifies its
    artist two ways: the typed name (fuzzy, via match_key) and, when the
    link came from a known artist, this id (exact). Pass known_id and a
    real rename updates THAT row directly — including its match_key, which
    is generated from name — instead of matching post-edit text and
    creating a duplicate artist that orphans the band's whole history. Only
    when known_id doesn't resolve (a deleted row, a bad id) does this fall
    back to the ordinary name-matching insert below, same as when no id is
    known at all (a brand new artist, or the bare public form)."""
    if known_id:
        cur.execute(
            """
            UPDATE artists SET
                name = %s,
                last_email = COALESCE(%s, last_email),
                last_phone = COALESCE(%s, last_phone)
            WHERE id = %s
            RETURNING id
            """,
            (name, email, phone, known_id),
        )
        row = cur.fetchone()
        if row:
            return row["id"]
    cur.execute(
        """
        INSERT INTO artists (name, last_email, last_phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (match_key) DO UPDATE SET
            last_email = COALESCE(EXCLUDED.last_email, artists.last_email),
            last_phone = COALESCE(EXCLUDED.last_phone, artists.last_phone)
        RETURNING id
        """,
        (name, email, phone),
    )
    return cur.fetchone()["id"]


def upsert_show(cur, artist_id, venue, show_date, series=None):
    """One booking per artist/venue/date. Returns show id."""
    cur.execute(
        """
        INSERT INTO shows (artist_id, venue, show_date, show_series)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (artist_id, venue, show_date) DO UPDATE SET
            show_series = COALESCE(EXCLUDED.show_series, shows.show_series)
        RETURNING id
        """,
        (artist_id, venue, show_date, series),
    )
    return cur.fetchone()["id"]


def stamp_email_sent(cur, show_id):
    """Mark the advance email as sent (first send wins)."""
    cur.execute(
        "UPDATE shows SET email_sent_at = COALESCE(email_sent_at, now()) WHERE id = %s",
        (show_id,),
    )


# ── date-driven advance lifecycle (Brian, 2026-09-03) ───────────────────────
# Initial advance drafts itself 21 days out from the show; the follow-up drafts
# itself if nothing's heard back by 7 days out. Both are DRAFTS — a human still
# sends. See /internal/advance-lifecycle in app.py.

def shows_due_for_initial_advance(cur):
    """Shows that haven't been drafted yet (and haven't already passed) — no
    date-out ceiling. Drafted as soon as a booking is seeded, whenever that
    happens to be; the 21-day mark is now a SEND reminder, not a draft trigger
    (Brian, 2026-09-03: draft at booking time, hold for his send at T-21 —
    see shows_due_for_send_reminder).

    Bug fixed 2026-09-08: this only ever selected `b.location` from the
    bookings LEFT JOIN, so event_name/schedule/lead/slot/set_time/email_note
    — everything a staffer actually types into /booking beyond the bare
    minimum — silently never reached the drafted email on this path (the
    CSV/xlsx batch path draft_emails.py also supports has always carried all
    of it; this immediate/lifecycle path just never pulled it). Caught on
    Brian's first real live booking: the draft came back with a generic day
    schedule and no event name despite real values being on file."""
    cur.execute(
        """SELECT s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  b.location AS location, b.event_name AS event_name,
                  b.lead_name AS lead_name, b.lead_phone AS lead_phone,
                  b.load_in AS load_in, b.soundcheck AS soundcheck,
                  b.event_start AS event_start, b.event_end AS event_end,
                  b.curfew AS curfew, b.slot AS slot, b.set_time AS set_time,
                  b.email_note AS email_note, b.band_count AS band_count,
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NULL
             AND s.show_date IS NOT NULL
             AND s.show_date >= CURRENT_DATE
           ORDER BY s.show_date"""
    )
    return cur.fetchall()


def shows_due_for_send_reminder(cur, days_out=21):
    """Shows already drafted (at booking time) that have now crossed into the
    21-day-out window and haven't been flagged for a send reminder yet — the
    nudge that tells Brian a draft sitting in Gmail is ready to send. Fires
    once per show, whenever the draft happened."""
    cur.execute(
        """SELECT s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date
           FROM shows s JOIN artists a ON a.id = s.artist_id
           WHERE s.advance_draft_created_at IS NOT NULL
             AND s.send_reminder_sent_at IS NULL
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
           ORDER BY s.show_date""",
        (days_out,),
    )
    return cur.fetchall()


# Reminder cadence (Brian, 2026-09-10): 7 days out (the original single
# follow-up), then 3, then 2, then 1 — each fires once, independently, as
# long as the band still hasn't responded. Ordered so the caller can loop
# widest-window-first (a show already inside the 1-day window on the day
# it crosses 7 days is unusual but not impossible with a very late booking;
# firing 7 before 3 before 2 before 1 keeps that order sane either way).
FOLLOWUP_TIERS = (7, 3, 2, 1)


def shows_due_for_followup(cur, days_before=7):
    """Shows within `days_before` days of their date with no response and no
    reminder drafted yet AT THIS TIER (advance_reminders is keyed per
    show+tier, so 7/3/2/1 each gate independently — a show can get all four
    over time, one per crossed threshold). Requires the initial advance to
    have already gone out — a show booked late (already inside every window
    on day one) gets its initial advance first and only qualifies for a
    reminder on a later run."""
    cur.execute(
        """SELECT s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  b.location AS location,
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NOT NULL
             AND s.responded_at IS NULL
             AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
             AND NOT EXISTS (SELECT 1 FROM advance_reminders r
                             WHERE r.show_id = s.id AND r.days_before = %s)
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
           ORDER BY s.show_date""",
        (days_before, days_before),
    )
    return cur.fetchall()


def mark_advance_drafted(cur, show_id):
    cur.execute(
        "UPDATE shows SET advance_draft_created_at = COALESCE(advance_draft_created_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def mark_followup_drafted(cur, show_id, days_before=7):
    """Record that THIS tier's reminder drafted for this show (advance_reminders,
    one row per show+tier — see FOLLOWUP_TIERS), and keep the legacy
    shows.followup_draft_created_at column stamped on whichever tier fires
    FIRST, so status_log.py/status_sheet.py/the advance_status view — all of
    which only ever asked 'has a reminder gone out at all' — need no changes."""
    cur.execute(
        "INSERT INTO advance_reminders (show_id, days_before) VALUES (%s, %s) "
        "ON CONFLICT (show_id, days_before) DO NOTHING", (show_id, days_before),
    )
    cur.execute(
        "UPDATE shows SET followup_draft_created_at = COALESCE(followup_draft_created_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def mark_send_reminder_sent(cur, show_id):
    cur.execute(
        "UPDATE shows SET send_reminder_sent_at = COALESCE(send_reminder_sent_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def bookings_on(cur, event_date):
    """Every booking (one row per band) for a specific date, ordered venue
    then event then slot (opener -> direct_support -> headliner) — the raw
    material for the daily digest's 'shows today' section. Bands sharing a
    bill share event_name/venue/schedule; the caller groups them."""
    cur.execute(
        """SELECT event_name, venue, location, series, artist_name, slot,
                  load_in, soundcheck, event_start, event_end, curfew
           FROM bookings
           WHERE event_date = %s
           ORDER BY venue, event_name,
             CASE slot WHEN 'opener' THEN 1 WHEN 'direct_support' THEN 2
                       WHEN 'headliner' THEN 3 ELSE 4 END""",
        (event_date,),
    )
    return cur.fetchall()


def advances_drafted_since(cur, hours=24):
    """Shows whose initial advance draft was created in the last `hours` —
    the daily digest's outbound half ('new advances we sent out')."""
    cur.execute(
        """SELECT * FROM advance_status
           WHERE advance_draft_created_at >= now() - (%s || ' hours')::interval
           ORDER BY advance_draft_created_at DESC""",
        (hours,),
    )
    return cur.fetchall()


def advances_responded_since(cur, hours=24):
    """Shows a band responded to (completed their advance form) in the last
    `hours` — the daily digest's inbound half ('bands who submitted')."""
    cur.execute(
        """SELECT * FROM advance_status
           WHERE responded_at >= now() - (%s || ' hours')::interval
           ORDER BY responded_at DESC""",
        (hours,),
    )
    return cur.fetchall()


def upcoming_advance_status(cur, days=14):
    """Every show within `days` of today (0 = today), soonest first — the
    daily digest's ranked at-a-glance list."""
    cur.execute(
        """SELECT * FROM advance_status
           WHERE days_until_show BETWEEN 0 AND %s
           ORDER BY days_until_show ASC, band ASC""",
        (days,),
    )
    return cur.fetchall()


def due_for_recap_extraction(cur, grace_days=1, lookback_days=30):
    """Shows that finished at least `grace_days` ago (their advance doc has had
    time to be corrected/finalized) and haven't had their recap extracted yet.
    Default matches extract_advance_recap.py's GRACE_DAYS (1 — next day;
    permanent per Brian 2026-09-10, was 3 originally). `lookback_days` bounds
    the catch-up window so a
    show whose advance was never filed (or filed somewhere the extractor can't
    find) doesn't get retried forever — see tools/extract_advance_recap.py."""
    cur.execute(
        """SELECT s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  s.venue, s.show_date
           FROM shows s JOIN artists a ON a.id = s.artist_id
           WHERE s.show_date IS NOT NULL
             AND s.show_date <= CURRENT_DATE - %s
             AND s.show_date >= CURRENT_DATE - %s
             AND NOT EXISTS (SELECT 1 FROM advance_recaps ar WHERE ar.show_id = s.id)
           ORDER BY s.show_date""",
        (grace_days, grace_days + lookback_days),
    )
    return cur.fetchall()


def record_advance_recap(cur, show_id, artist_id, venue, show_date, source_docx,
                          md_path, pdf_path, recap):
    """Upsert — ON CONFLICT so a re-run (or a later run correcting a failed PDF
    conversion) overwrites cleanly instead of erroring on the UNIQUE(show_id)."""
    import json
    cur.execute(
        """INSERT INTO advance_recaps
               (show_id, artist_id, venue, show_date, source_docx, md_path, pdf_path, recap)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (show_id) DO UPDATE SET
               artist_id=EXCLUDED.artist_id, venue=EXCLUDED.venue,
               show_date=EXCLUDED.show_date, source_docx=EXCLUDED.source_docx,
               md_path=EXCLUDED.md_path, pdf_path=EXCLUDED.pdf_path,
               recap=EXCLUDED.recap, extracted_at=now()""",
        (show_id, artist_id, venue, show_date, source_docx, md_path, pdf_path,
         json.dumps(recap)),
    )


def band_count_for_event(cur, venue, event_date):
    """The declared band count (max across acts, in case of disagreement) for
    any booking at this venue+date — lets daysheet.fill() pick the right N-band
    template even when only some of the bill's acts have real event_acts rows
    yet (bands entered one at a time). None if nobody declared one."""
    cur.execute(
        "SELECT max(band_count) AS n FROM bookings WHERE venue=%s AND event_date=%s "
        "AND band_count IS NOT NULL",
        (venue, event_date),
    )
    row = cur.fetchone()
    return row["n"] if row else None


def get_advance_recap_by_show(cur, show_id):
    cur.execute("SELECT * FROM advance_recaps WHERE show_id=%s", (show_id,))
    return cur.fetchone()


def recaps_for_docx(cur, source_docx, venue):
    """Every act already recorded against this exact filed .docx (a multi-band
    bill shares one file across several shows/artists) — used to rebuild the
    ONE shared recap MD from scratch each time, so it always reflects every
    act recorded so far regardless of which act's extraction run wrote it
    last. `[{'artist_name', 'recap'}, ...]`, in the order acts were recorded."""
    cur.execute(
        """SELECT a.name AS artist_name, ar.recap
           FROM advance_recaps ar JOIN artists a ON a.id = ar.artist_id
           WHERE ar.source_docx = %s AND ar.venue = %s
           ORDER BY ar.id""",
        (source_docx, venue),
    )
    return cur.fetchall()


def insert_submission(cur, artist_id, show_id, data: dict, source="form"):
    """data = the full raw form dict. Promotes the queryable fields into columns
    and keeps the entire payload in JSONB."""
    import json
    cur.execute(
        """
        INSERT INTO submissions (
            artist_id, show_id, contact_name, contact_email, contact_phone,
            venue, show_date, performers, monitors, own_iems, split_snake,
            stage_type, own_engineer, merch, band_tent, large_vehicle, data, source
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (
            artist_id, show_id,
            data.get("contact_name"), data.get("contact_email"), data.get("contact_phone"),
            data.get("venue"), to_date(data.get("show_date")),
            to_int(data.get("performers")), to_int(data.get("monitors")),
            to_bool(data.get("own_iems")), data.get("split_snake"),
            data.get("stage_type"), data.get("own_engineer"),
            to_bool(data.get("merch")), data.get("band_tent"),
            to_bool(data.get("large_vehicle")),
            json.dumps(data), source,
        ),
    )
    return cur.fetchone()["id"]


def insert_file(cur, submission_id, artist_id, filename, stored_name,
                kind="stage_plot", mime=None, size=None, nas_path=None):
    cur.execute(
        """
        INSERT INTO files (submission_id, artist_id, kind, filename, stored_name,
                           mime, size, nas_path)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """,
        (submission_id, artist_id, kind, filename, stored_name, mime, size, nas_path),
    )
    return cur.fetchone()["id"]


def record_submission(form: dict, file_info=None, source="form"):
    """High-level: one transaction that upserts the artist + show, inserts the
    submission, stamps responded_at, and links any uploaded file. Returns
    (artist_id, show_id, submission_id). Raises on failure — caller decides
    whether that's fatal (the form treats it as non-fatal)."""
    name = form.get("band_name") or "(unknown)"
    known_id = form.get("artist_id")
    try:
        known_id = int(known_id) if known_id else None
    except (TypeError, ValueError):
        known_id = None
    with get_conn() as conn:
        with conn.cursor() as cur:
            artist_id = upsert_artist(
                cur, name, email=form.get("contact_email"),
                phone=form.get("contact_phone"), known_id=known_id,
            )
            show_id = upsert_show(
                cur, artist_id, form.get("venue"), to_date(form.get("show_date")),
                series=form.get("show_series"),
            )
            sub_id = insert_submission(cur, artist_id, show_id, form, source=source)
            # advance finished — stamp responded_at (first response wins)
            cur.execute(
                "UPDATE shows SET responded_at = COALESCE(responded_at, now()) WHERE id = %s",
                (show_id,),
            )
            if file_info:
                insert_file(
                    cur, sub_id, artist_id,
                    filename=file_info.get("filename"),
                    stored_name=file_info.get("stored_name"),
                    mime=file_info.get("mime"), size=file_info.get("size"),
                )
        conn.commit()
    return artist_id, show_id, sub_id


# ── queries: prefill, returning-artist logic, search ────────────────────────

def find_artist_by_name(cur, name):
    cur.execute("SELECT * FROM artists WHERE match_key = %s", (normalize(name),))
    return cur.fetchone()


def get_artist(cur, artist_id):
    cur.execute("SELECT * FROM artists WHERE id = %s", (artist_id,))
    return cur.fetchone()


def newest_submission(cur, artist_id):
    cur.execute(
        "SELECT * FROM submissions WHERE artist_id=%s ORDER BY submitted_at DESC LIMIT 1",
        (artist_id,),
    )
    return cur.fetchone()


def played_within(cur, artist_id, ref_date, months=6):
    """Returns the newest prior submission if this band has a submission whose
    show_date is within `months` before ref_date, else None. This is the
    returning-artist test — deliberately cross-venue."""
    sub = newest_submission(cur, artist_id)
    if not sub:
        return None
    last = sub.get("show_date") or (sub.get("submitted_at").date()
                                    if sub.get("submitted_at") else None)
    if not last:
        return None
    if isinstance(ref_date, str):
        ref_date = to_date(ref_date)
    if not ref_date:
        ref_date = dt.date.today()
    delta_days = (ref_date - last).days
    if 0 <= delta_days <= months * 31:
        return sub
    # also treat a very recent past submission (any venue) as returning
    if -31 <= delta_days < 0:
        return sub
    return None


def search_artists(cur, q):
    cur.execute(
        """
        SELECT a.id, a.name, a.last_email, a.last_phone,
               COUNT(DISTINCT s.id)  AS show_count,
               COUNT(DISTINCT sub.id) AS submission_count,
               MAX(sub.submitted_at) AS last_submission
        FROM artists a
        LEFT JOIN shows s ON s.artist_id = a.id
        LEFT JOIN submissions sub ON sub.artist_id = a.id
        WHERE a.match_key LIKE %s
        GROUP BY a.id
        ORDER BY a.name
        LIMIT 100
        """,
        (f"%{normalize(q)}%",),
    )
    return cur.fetchall()


def artist_shows(cur, artist_id):
    cur.execute(
        "SELECT * FROM shows WHERE artist_id=%s ORDER BY show_date DESC NULLS LAST",
        (artist_id,),
    )
    return cur.fetchall()


def artist_submissions(cur, artist_id):
    cur.execute(
        "SELECT * FROM submissions WHERE artist_id=%s ORDER BY submitted_at DESC",
        (artist_id,),
    )
    return cur.fetchall()


def submission_files(cur, submission_id):
    cur.execute("SELECT * FROM files WHERE submission_id=%s", (submission_id,))
    return cur.fetchall()


def get_submission(cur, submission_id):
    cur.execute("SELECT * FROM submissions WHERE id=%s", (submission_id,))
    return cur.fetchone()


# ── events (day-sheet bills) ────────────────────────────────────────────────

SLOT_ORDER = {"opener": 1, "direct_support": 2, "headliner": 3}


def create_event(cur, name, venue, event_date, series=None, notes=None, details=None):
    import json
    cur.execute(
        """INSERT INTO events (name, venue, event_date, series, notes, details)
           VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
        (name, venue, event_date, series, notes, json.dumps(details or {})),
    )
    return cur.fetchone()["id"]


def update_event_details(cur, event_id, details):
    """Merge new detail keys into the event's details JSONB (non-empty win)."""
    import json
    cur.execute("SELECT details FROM events WHERE id=%s", (event_id,))
    row = cur.fetchone()
    cur_details = dict(row["details"] or {}) if row else {}
    for k, v in (details or {}).items():
        if v not in (None, ""):
            cur_details[k] = v
    cur.execute("UPDATE events SET details=%s WHERE id=%s",
                (json.dumps(cur_details), event_id))


def add_act(cur, event_id, slot, artist_id, submission_id=None, slot_order=None,
            set_time=None, sheet_fields=None):
    import json
    if slot_order is None:
        slot_order = SLOT_ORDER.get(slot, 99)
    cur.execute(
        """INSERT INTO event_acts (event_id, slot, slot_order, artist_id,
                                   submission_id, set_time, sheet_fields)
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (event_id, slot) DO UPDATE SET
             artist_id=EXCLUDED.artist_id,
             submission_id=EXCLUDED.submission_id,
             slot_order=EXCLUDED.slot_order,
             set_time=COALESCE(EXCLUDED.set_time, event_acts.set_time),
             sheet_fields=event_acts.sheet_fields || EXCLUDED.sheet_fields
           RETURNING id""",
        (event_id, slot, slot_order, artist_id, submission_id, set_time,
         json.dumps(sheet_fields or {})),
    )
    return cur.fetchone()["id"]


def get_event(cur, event_id):
    cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    return cur.fetchone()


def list_events(cur):
    cur.execute(
        """SELECT e.*, COUNT(a.id) AS acts
           FROM events e LEFT JOIN event_acts a ON a.event_id=e.id
           GROUP BY e.id ORDER BY e.event_date DESC NULLS LAST, e.id DESC"""
    )
    return cur.fetchall()


def event_acts(cur, event_id):
    """Acts in column order, each with its artist + the submission to fill from
    (the linked submission, or the artist's newest)."""
    cur.execute(
        "SELECT * FROM event_acts WHERE event_id=%s ORDER BY slot_order", (event_id,)
    )
    acts = cur.fetchall()
    for a in acts:
        a["artist"] = get_artist(cur, a["artist_id"]) if a.get("artist_id") else None
        if a.get("submission_id"):
            a["submission"] = get_submission(cur, a["submission_id"])
        elif a.get("artist_id"):
            a["submission"] = newest_submission(cur, a["artist_id"])
        else:
            a["submission"] = None
    return acts


# ── staff booking intake ─────────────────────────────────────────────────────
BOOKING_FIELDS = [
    "event_name", "event_date", "venue", "location", "series", "event_type", "paying_band",
    "lead_name", "lead_phone", "load_in", "soundcheck", "event_start",
    "event_end", "curfew", "slot", "set_time", "artist_name", "contact_name", "contact_email",
    "email_note", "entered_by", "band_count",
]


def insert_booking(cur, data: dict):
    """Insert one staff-entered booking. Blank strings stored as NULL."""
    vals = {k: (data.get(k) or None) for k in BOOKING_FIELDS}
    ed = vals.get("event_date")
    if isinstance(ed, str) and ed.strip():
        try:
            vals["event_date"] = dt.date.fromisoformat(ed.strip()[:10])
        except ValueError:
            vals["event_date"] = None
    cols = ", ".join(BOOKING_FIELDS)
    ph = ", ".join(f"%({k})s" for k in BOOKING_FIELDS)
    cur.execute(f"INSERT INTO bookings ({cols}) VALUES ({ph}) RETURNING id", vals)
    return cur.fetchone()["id"]


def series_by_venue(cur):
    """Distinct series names staff have already used, grouped by venue —
    powers the booking form's series dropdown so new bookings build on
    existing naming instead of drifting (e.g. "Live on the Levee" vs
    "live on the levee"). Case-insensitive de-dupe, keeps first spelling seen
    (alphabetical, since the query is ordered)."""
    cur.execute(
        """SELECT DISTINCT venue, series FROM bookings
           WHERE series IS NOT NULL AND series <> ''
           ORDER BY venue, series"""
    )
    out = {}
    for row in cur.fetchall():
        v, s = row["venue"], row["series"]
        bucket = out.setdefault(v, [])
        if not any(existing.lower() == s.lower() for existing in bucket):
            bucket.append(s)
    return out


def browse_venues(cur):
    """Venues with at least one advanced show on record, band + show counts —
    level 1 of the staff browse tree (venue -> series -> band)."""
    cur.execute(
        """
        SELECT venue,
               COUNT(DISTINCT artist_id) AS band_count,
               COUNT(*)                  AS show_count
        FROM shows
        WHERE venue IS NOT NULL AND venue <> ''
        GROUP BY venue
        ORDER BY venue
        """
    )
    return cur.fetchall()


def browse_series(cur, venue):
    """Series for one venue (blank/NULL series collapse into one 'no series /
    one-off' row, series=None) — level 2 of the browse tree."""
    cur.execute(
        """
        SELECT NULLIF(btrim(show_series), '') AS series,
               COUNT(DISTINCT artist_id)       AS band_count,
               COUNT(*)                        AS show_count
        FROM shows
        WHERE venue = %s
        GROUP BY 1
        ORDER BY series NULLS LAST
        """,
        (venue,),
    )
    return cur.fetchall()


def browse_bands(cur, venue, series):
    """Bands advanced at one venue + series (series=None = the no-series
    bucket) — level 3 of the browse tree; each row feeds a link to
    /artist/<id>."""
    if series is None:
        clause, params = "(s.show_series IS NULL OR btrim(s.show_series) = '')", (venue,)
    else:
        clause, params = "s.show_series = %s", (venue, series)
    cur.execute(
        f"""
        SELECT a.id, a.name, a.last_email, a.last_phone,
               COUNT(*)             AS show_count,
               MAX(s.show_date)     AS last_show_date
        FROM shows s
        JOIN artists a ON a.id = s.artist_id
        WHERE s.venue = %s AND {clause}
        GROUP BY a.id
        ORDER BY a.name
        """,
        params,
    )
    return cur.fetchall()


def unseeded_bookings(cur):
    """Bookings not yet appended to the sheet, oldest first."""
    cur.execute("SELECT * FROM bookings WHERE seeded_at IS NULL ORDER BY id")
    return cur.fetchall()


def mark_bookings_seeded(cur, ids):
    if not ids:
        return
    cur.execute("UPDATE bookings SET seeded_at = now() WHERE id = ANY(%s)",
                (list(ids),))


def get_or_create_short_link(cur, token):
    """Deterministic short code for a signed /f/<token> prefill link (same token
    -> same code, so re-drafting a show doesn't pile up rows). /s/<code> 302s to
    the real link — see app.py."""
    import base64
    import hashlib
    digest = hashlib.sha256(token.encode()).digest()
    code = base64.urlsafe_b64encode(digest)[:8].decode()
    cur.execute(
        "INSERT INTO short_links (code, token) VALUES (%s, %s) "
        "ON CONFLICT (code) DO NOTHING", (code, token),
    )
    return code


def resolve_short_link(cur, code):
    cur.execute("SELECT token FROM short_links WHERE code = %s", (code,))
    row = cur.fetchone()
    return row["token"] if row else None
