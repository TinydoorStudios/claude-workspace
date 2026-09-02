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

def upsert_artist(cur, name, email=None, phone=None):
    """Insert the band by exact name; on a match_key collision keep the existing
    display name and only fill in newer contact info. Returns artist id."""
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


def upsert_show(cur, artist_id, venue, show_date, series=None, status=None):
    """One booking per artist/venue/date. Returns show id."""
    cur.execute(
        """
        INSERT INTO shows (artist_id, venue, show_date, show_series, status)
        VALUES (%s, %s, %s, %s, COALESCE(%s, 'not_advanced'))
        ON CONFLICT (artist_id, venue, show_date) DO UPDATE SET
            show_series = COALESCE(EXCLUDED.show_series, shows.show_series),
            status = COALESCE(%s, shows.status)
        RETURNING id
        """,
        (artist_id, venue, show_date, series, status, status),
    )
    return cur.fetchone()["id"]


def stamp_email_sent(cur, show_id):
    """Mark the advance email as sent (first send wins)."""
    cur.execute(
        "UPDATE shows SET email_sent_at = COALESCE(email_sent_at, now()), "
        "status = CASE WHEN status = 'not_advanced' THEN 'email_sent' ELSE status END "
        "WHERE id = %s",
        (show_id,),
    )


def mark_show_status(cur, show_id, status, email_sent=False):
    if email_sent:
        cur.execute(
            "UPDATE shows SET status=%s, email_sent_at=now() WHERE id=%s",
            (status, show_id),
        )
    else:
        cur.execute("UPDATE shows SET status=%s WHERE id=%s", (status, show_id))


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
    submission (status -> responded), and links any uploaded file. Returns
    (artist_id, show_id, submission_id). Raises on failure — caller decides
    whether that's fatal (the form treats it as non-fatal)."""
    name = form.get("band_name") or "(unknown)"
    with get_conn() as conn:
        with conn.cursor() as cur:
            artist_id = upsert_artist(
                cur, name, email=form.get("contact_email"),
                phone=form.get("contact_phone"),
            )
            show_id = upsert_show(
                cur, artist_id, form.get("venue"), to_date(form.get("show_date")),
                series=form.get("show_series"), status="responded",
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
