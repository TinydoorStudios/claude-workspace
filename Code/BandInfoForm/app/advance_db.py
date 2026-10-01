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
from difflib import SequenceMatcher

import psycopg
from psycopg.rows import dict_row

DB_URL = os.environ.get(
    "ADVANCE_DB_URL", "postgresql://advance:advance@127.0.0.1:5433/advance"
)

# ── helpers ────────────────────────────────────────────────────────────────

def normalize(name: str) -> str:
    """Same rule as the generated match_key column: lower + collapse whitespace."""
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


# 2026-09-21 sweep (DBA-3): the lookup key computed IN SQL, identical to the generated
# artists.match_key in db/schema.sql — keep them in step. normalize() folds NBSP/U+202F
# (Python's \s), Postgres doesn't, so a Python key misses those rows.
_SQL_MATCH_KEY = r"lower(btrim(regexp_replace(%s, '\s+', ' ', 'g')))"


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


def is_third_party(series):
    """A booking under the '3rd Party' series is its own event on a date that
    may also carry the internal bill (Brian, 2026-09-14)."""
    return normalize(series) == "3rd party"


# Brian, 2026-09-14: a 3rd-party show sends the band nothing automated
# (welcome, reminders, day-before, thank-you) and raises no "no response"
# nags, unless staff ticked "Send band emails" on its booking. SQL fragment
# for queries that alias shows `s` and artists `a`.
THIRD_PARTY_SILENT_SQL = r"""(lower(btrim(COALESCE(s.show_series,''))) = '3rd party'
      AND NOT EXISTS (SELECT 1 FROM bookings bx
                      WHERE bx.venue = s.venue AND bx.event_date = s.show_date
                        AND lower(btrim(regexp_replace(bx.artist_name, '\s+', ' ', 'g'))) = a.match_key
                        AND bx.band_emails))"""

# 2026-09-21 sweep: "the band has answered", for the reminder ladder and the
# no-response alerts. Staff-typed booking answers (source='staff',
# stamp_responded=False) aren't the band responding (#9(b)) — except on a
# Manual band advance, where staff filling the form IS the advance. Aliases s, a.
BAND_ANSWERED_SQL = r"""EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id
      AND (sub.source <> 'staff'
           OR EXISTS (SELECT 1 FROM bookings mb
                      WHERE mb.venue = s.venue AND mb.event_date = s.show_date
                        AND lower(btrim(regexp_replace(mb.artist_name, '\s+', ' ', 'g'))) = a.match_key
                        AND mb.skip_welcome_email)))"""

# 2026-09-21 sweep (PRIOR-25): a held welcome draft is stale once the band has
# answered (or the show is cancelled). "Answered" mirrors exactly what keeps a show
# out of shows_due_for_initial_advance, so clearing the stamp never releases a send. Aliases s.
_HELD_DRAFT_ANSWERED_SQL = """(s.responded_at IS NOT NULL
      OR EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id AND sub.source <> 'staff'))"""
_HELD_DRAFT_STALE_SQL = "(s.cancelled_at IS NOT NULL OR " + _HELD_DRAFT_ANSWERED_SQL + ")"


def band_emails_on(cur, show_id):
    """False for a 3rd-party show whose booking hasn't opted in to band
    emails; True for every other show."""
    cur.execute("SELECT NOT " + THIRD_PARTY_SILENT_SQL + """ AS on_
                 FROM shows s JOIN artists a ON a.id = s.artist_id WHERE s.id = %s""", (show_id,))
    row = cur.fetchone()
    return bool(row and row["on_"])


def set_band_emails(cur, show_id, on):
    """Flip the opt-in on the booking row(s) behind this show. False if the
    show has no booking row (a sheet-only show) — nothing to flip."""
    cur.execute(r"""UPDATE bookings b SET band_emails = %s
                    FROM shows s JOIN artists a ON a.id = s.artist_id
                    WHERE s.id = %s AND b.venue = s.venue AND b.event_date = s.show_date
                      AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
                    RETURNING b.id""", (bool(on), show_id))
    return bool(cur.fetchall())


def to_date(v):
    if not v:
        return None
    try:
        return dt.date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        return None


def _as_date(v):
    """date | None from a date, a datetime, or an ISO-ish string."""
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return to_date(v)


# Days before the show a venue wants the form back (default a week). Memorial
# Hall asks for two weeks (Brian, 2026-09-29).
DEADLINE_LEAD_DAYS = {"Memorial Hall": 14}


def advance_deadline(show_date, booking_created_at=None, venue=None):
    """2026-09-24 research #2: THE deadline for a band's advance — one date,
    used by the welcome, every reminder tier and every internal surface, so a
    band is never told two different things (Lennd: "give artists one deadline
    for everything"; Stage Portal states it at booking).

    A week before the show (two for Memorial Hall), or two weeks after the booking was logged when
    that lands sooner, then clamped: never after the day before the show, and
    never in the past (a show booked inside the window still gets a real date
    a band can act on, not "by last Tuesday"). The floor wins that clamp, so a
    show booked a day or two out reads "by <show day>" rather than a date
    that's already gone. None when there's no show date."""
    d = _as_date(show_date)
    if not d:
        return None
    deadline = d - dt.timedelta(days=DEADLINE_LEAD_DAYS.get((venue or "").strip(), 7))
    booked = _as_date(booking_created_at)
    if booked:
        deadline = min(deadline, booked + dt.timedelta(days=14))
    deadline = min(deadline, d - dt.timedelta(days=1))
    return max(deadline, dt.date.today() + dt.timedelta(days=1))


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
    known at all (a brand new artist, or the bare public form).
    2026-09-21 sweep: record_submission no longer passes a differing name here."""
    if known_id:
        # a rename that collides with ANOTHER artist's match_key would violate
        # the unique index and lose the whole submission's DB write — keep
        # the existing name in that case, update contact info only.
        cur.execute(f"SELECT 1 FROM artists WHERE match_key = {_SQL_MATCH_KEY} AND id <> %s",
                    (name, known_id))
        if cur.fetchone():
            cur.execute("SELECT name FROM artists WHERE id = %s", (known_id,))
            row = cur.fetchone()
            if row:
                name = row["name"]
        else:
            # a case/spacing-only difference is not a rename (2026-09-14:
            # "Ratboys" typed for "RatBoys" renamed the filed doc and gave
            # Dropbox a case-conflict copy) — keep the staff spelling
            cur.execute("SELECT name FROM artists WHERE id = %s", (known_id,))
            row = cur.fetchone()
            if row and normalize(row["name"]) == normalize(name):
                name = row["name"]
        # 2026-09-18: only write when something actually changes. The UPDATE
        # fires a touch_updated_at trigger, so an unconditional re-write made
        # artists.updated_at a timestamp of "the last lifecycle run" rather
        # than "the last real change" — useless as an audit signal.
        cur.execute(
            """
            UPDATE artists SET
                name = %s,
                last_email = COALESCE(%s, last_email),
                last_phone = COALESCE(%s, last_phone)
            WHERE id = %s
              AND (name IS DISTINCT FROM %s
                   OR last_email IS DISTINCT FROM COALESCE(%s, last_email)
                   OR last_phone IS DISTINCT FROM COALESCE(%s, last_phone))
            RETURNING id
            """,
            (name, email, phone, known_id, name, email, phone),
        )
        if cur.fetchone():
            return known_id
        cur.execute("SELECT 1 FROM artists WHERE id = %s", (known_id,))
        if cur.fetchone():
            return known_id
    cur.execute(
        """
        INSERT INTO artists (name, last_email, last_phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (match_key) DO UPDATE SET
            last_email = COALESCE(EXCLUDED.last_email, artists.last_email),
            last_phone = COALESCE(EXCLUDED.last_phone, artists.last_phone)
        WHERE artists.last_email IS DISTINCT FROM
                  COALESCE(EXCLUDED.last_email, artists.last_email)
           OR artists.last_phone IS DISTINCT FROM
                  COALESCE(EXCLUDED.last_phone, artists.last_phone)
        RETURNING id
        """,
        (name, email, phone),
    )
    row = cur.fetchone()
    if row:
        return row["id"]
    # DO UPDATE ... WHERE that matches nothing returns no row (the conflicting
    # row is unchanged and NOT returned) — fetch its id instead of re-writing.
    cur.execute(f"SELECT id FROM artists WHERE match_key = {_SQL_MATCH_KEY}", (name,))
    return cur.fetchone()["id"]


def upsert_show(cur, artist_id, venue, show_date, series=None):
    """One booking per artist/venue/date. Returns show id."""
    cur.execute(
        """
        INSERT INTO shows (artist_id, venue, show_date, show_series)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (artist_id, venue, show_date) DO UPDATE SET
            show_series = COALESCE(EXCLUDED.show_series, shows.show_series)
        WHERE shows.show_series IS DISTINCT FROM
              COALESCE(EXCLUDED.show_series, shows.show_series)
        RETURNING id
        """,
        (artist_id, venue, show_date, series),
    )
    row = cur.fetchone()
    if row:
        return row["id"]
    # No-op conflict: nothing changed, so DO UPDATE ... WHERE skipped the write
    # and returned nothing. Before 2026-09-18 this updated unconditionally and
    # every lifecycle re-seed bumped updated_at on every show row.
    cur.execute(
        "SELECT id FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s",
        (artist_id, venue, show_date),
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

# slot_for() lived here until 2026-09-15. Its only caller tailored the band's
# own form to its slot — FSQ hid the drum-riser question from openers and direct
# support. The riser question is now asked of every artist, worded "if
# available" (Brian, same day), so nothing needs to know an act's position to
# render its form, and the lookup is gone rather than left dangling.


def shows_due_for_initial_advance(cur):
    """Shows within 21 days of their date that haven't had their initial
    advance sent yet (and haven't already passed).

    INCIDENT (Brian, 2026-09-13, caught same day): this query originally had
    NO date-out ceiling at all — "drafted as soon as a booking is seeded,
    whenever that happens to be" was the 2026-09-03 design, back when
    hitting this path only created a Gmail DRAFT that sat unsent until
    Brian manually sent it at the real T-21 mark (shows_due_for_send_
    reminder). The live-send migration (also 2026-09-13, earlier the same
    day) turned that draft step into a real, immediate Outlook send —
    but kept the "no ceiling" query as-is. Consequence: ANY on-demand
    lifecycle trigger (any single urgent booking within 21 days hits
    _trigger_immediate_advance) swept up and live-sent the welcome for
    EVERY show still sitting in the queue, including ones 3-6 weeks out
    that were never meant to be emailed yet. Three real bands (Dixie Karas
    @ 43 days out, Queen City Cabaret @ 29, Jordan Pollard Trio @ 22) got
    their welcome sent early this way at 2026-09-13 21:04 UTC, triggered by
    an unrelated urgent booking's on-demand call — confirmed via n8n's own
    execution log (mode=webhook) cross-referenced with shows.advance_
    draft_created_at, not just an HTTP status. Fixed by restoring the
    21-day ceiling directly on the send gate itself (previously that
    ceiling only ever lived on the now-retired draft-is-ready-to-send
    REMINDER, never on an actual send condition) — a show booked further
    out than that now simply waits, un-queued, until a lifecycle run
    happens while it's genuinely inside the window, no matter how many
    unrelated on-demand triggers fire in the meantime.

    Bug fixed 2026-09-08: this only ever selected `b.location` from the
    bookings LEFT JOIN, so event_name/schedule/lead/set_time/email_note
    — everything a staffer actually types into /booking beyond the bare
    minimum — silently never reached the drafted email on this path (the
    CSV/xlsx batch path draft_emails.py also supports has always carried all
    of it; this immediate/lifecycle path just never pulled it). Caught on
    Brian's first real live booking: the draft came back with a generic day
    schedule and no event name despite real values being on file.

    Manual-entry bookings (Brian, 2026-09-13) are excluded here via
    `b.skip_welcome_email` — staff is filling in the band's own form by
    hand (they emailed it directly), so the "please fill this out" welcome
    would be pointless and confusing. `b.*` is NULL whenever no matching
    booking row exists at all (a submission-only show), so
    `IS NOT TRUE` — not `= false` — is required: it reads NULL as "no flag
    set, don't exclude" instead of silently dropping every such show."""
    # DISTINCT ON (audit review 2026-09-14, H1): a duplicate booking row for
    # the same band/venue/date used to return the show twice, and the welcome
    # loop sent it twice in one run. One row per show, newest booking wins.
    cur.execute(
        """SELECT DISTINCT ON (s.id)
                  s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  b.location AS location, b.event_name AS event_name,
                  b.lead_name AS lead_name, b.lead_phone AS lead_phone,
                  b.load_in AS load_in, b.soundcheck AS soundcheck,
                  b.event_start AS event_start, b.event_end AS event_end,
                  b.curfew AS curfew, b.set_time AS set_time,
                  b.email_note AS email_note,
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email,
                  COALESCE(b.draft_only, false) AS draft_only,
                  b.id AS booking_id
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NULL
             AND s.cancelled_at IS NULL AND s.held_at IS NULL
             AND s.responded_at IS NULL
             -- audit 2026-09-16 #9: a booking entered WITH the band's answers
             -- already typed in (source='staff') inserts a submission row but
             -- deliberately never stamps responded_at (record_submission
             -- stamp_responded=False) — the welcome/reminder ladder still
             -- needs to run for it, so a staff-sourced submission alone
             -- doesn't count as "already responded" here.
             AND NOT EXISTS (SELECT 1 FROM submissions sub
                             WHERE sub.show_id = s.id AND sub.source <> 'staff')
             AND s.show_date IS NOT NULL
             AND s.show_date >= CURRENT_DATE
             AND s.show_date <= CURRENT_DATE + """ + _welcome_window_sql() + """
             AND """ + _paused_sql() + """
             AND b.skip_welcome_email IS NOT TRUE
             -- a "draft, don't send" welcome that's already sitting in the
             -- drafts folder isn't due again; un-ticking the box clears the
             -- stamp and this picks the show straight back up
             AND s.advance_held_draft_at IS NULL
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.id, b.id DESC NULLS LAST"""
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


# Reminder cadence (Brian, 2026-09-10: 7/3/2/1; trimmed 2026-09-13 to
# 7/3/1 — the 2-day tier is gone — as part of the live-send migration).
# Each fires at most once, independently, as long as the band still
# hasn't responded — EXCEPT a tier already on or before the day a show
# was booked, which is pre-skipped for good right when the welcome sends
# (see mark_stale_followup_tiers_skipped) and never reaches
# shows_due_for_followup at all. Ordered so a caller looping over it
# processes widest-window-first, though with live sends each tier is
# independent and order no longer really matters the way it did when
# multiple tiers could pile up behind one unsent draft.
# 2026-09-24 research #4: the ladder starts at 10 days out, not 7. The old
# escalation was an internal alert to Brian at T-3, by which point the packet is
# already being built and no stage plot arriving then can change it. T-10 is the
# first firm chase, and it rides this same mechanism — advance_reminders
# UNIQUE(show_id, days_before) — so it is idempotent, pre-skipped when the show
# was booked inside the window, and outcome-safe on a timeout, exactly like
# 7/3/1. The T-3 internal alert stays as the last resort.
# HOOK for F1 (research #1, per-tier wording): app.py's follow-up block renders
# ONE generic reminder body for every tier, so today T-10 reads like the T-7
# reminder. The tier number is in scope there as `tier`.
FIRST_CHASE_TIER = 10
FOLLOWUP_TIERS = (FIRST_CHASE_TIER, 7, 3, 1)

# 2026-09-24 research #3: at one week out the venue's message is the CONFIRMED
# SCHEDULE going out (Stage Portal step 3, Ticket Fairy "publish 1-2 weeks
# out"), not a nudge coming back. So tier 7 is no longer a chase — it IS that
# email, it goes to every show at 7 days whether or not the band answered, and
# when they haven't the T-7 chase paragraph rides inside it. One row in
# advance_reminders (UNIQUE(show_id, days_before)) still gates it, so the
# schedule email and the old tier-7 reminder can never both go out.
SCHEDULE_TIER = 7
# The tiers that are still plain chases. app.py merges shows_due_for_schedule
# into the same per-show "closest open tier wins" pick (#21), so a show gets at
# most one of these emails per run no matter how many tiers are open.
CHASE_TIERS = tuple(t for t in FOLLOWUP_TIERS if t != SCHEDULE_TIER)

# Per-venue ladders (Brian, 2026-09-29): Memorial Hall's welcome goes out 30
# days out and chases at 15/10/7/5/3/2/1. Every other venue keeps the default
# above (welcome at 21, chases at 10/7/3/1). Tier 7 stays the confirmed-
# schedule email everywhere. A venue not listed here runs the default.
DEFAULT_WELCOME_DAYS = 21
# "paused": no welcome goes out automatically (and so no chase, schedule or
# day-ahead email either — they all wait on the welcome). Brian, 2026-09-29:
# Memo's welcome copy is on hold; staff send the show's form link by hand.
# Flip it to False (and review venue_email's Memo block) to turn Memo on.
VENUE_LADDERS = {
    "Memorial Hall": {"welcome": 30, "tiers": (15, 10, 7, 5, 3, 2, 1), "paused": True},
}


def welcome_paused(venue):
    return bool(VENUE_LADDERS.get((venue or "").strip(), {}).get("paused"))


def welcome_days(venue):
    return VENUE_LADDERS.get((venue or "").strip(), {}).get("welcome", DEFAULT_WELCOME_DAYS)


def tiers_for(venue):
    return VENUE_LADDERS.get((venue or "").strip(), {}).get("tiers", FOLLOWUP_TIERS)


# every chase tier any venue runs, widest first — app.py's follow-up loop walks this
ALL_CHASE_TIERS = tuple(sorted({t for t in FOLLOWUP_TIERS if t != SCHEDULE_TIER}
                               | {t for v in VENUE_LADDERS.values() for t in v["tiers"]
                                  if t != SCHEDULE_TIER}, reverse=True))


def _welcome_window_sql(col="s.venue"):
    """SQL for 'this show's welcome window in days', per VENUE_LADDERS."""
    whens = " ".join(f"WHEN {col} = '{v}' THEN {c['welcome']}"
                     for v, c in VENUE_LADDERS.items() if "'" not in v)
    return f"(CASE {whens} ELSE {DEFAULT_WELCOME_DAYS} END)" if whens else str(DEFAULT_WELCOME_DAYS)


def _paused_sql(col="s.venue"):
    """SQL: this show's venue isn't on a paused welcome."""
    paused = [v for v, c in VENUE_LADDERS.items() if c.get("paused") and "'" not in v]
    return (f"COALESCE({col}, '') NOT IN (" + ", ".join(f"'{v}'" for v in paused) + ")"
            if paused else "TRUE")


def _tier_venue_sql(tier):
    """(sql, params) limiting a tier's due query to the venues whose ladder has it."""
    custom = list(VENUE_LADDERS)
    having = [v for v, c in VENUE_LADDERS.items() if tier in c["tiers"]]
    default_has = tier in FOLLOWUP_TIERS
    return ("(s.venue = ANY(%s::text[]) OR (%s::boolean AND COALESCE(s.venue, '') <> ALL(%s::text[])))",
            [having, default_has, custom])


def shows_due_for_followup(cur, days_before=7):
    vsql, vparams = _tier_venue_sql(days_before)
    """Shows within `days_before` days of their date with no response and no
    reminder resolved yet AT THIS TIER (advance_reminders is keyed per
    show+tier, so each of FOLLOWUP_TIERS gates independently). 'Resolved'
    covers three cases, all recorded via mark_followup_sent /
    mark_stale_followup_tiers_skipped: actually sent, skipped because the
    band has no email on file, or pre-skipped as already-stale at booking
    time — any of the three permanently closes this tier for this show, so
    this query only ever returns a tier that's genuinely still open.
    Requires the initial advance to have already gone out — a show booked
    late (already inside every window on day one) gets its initial advance
    first; mark_stale_followup_tiers_skipped in that same pass then decides
    which tiers (if any) are even still eligible to show up here later."""
    cur.execute(
        """SELECT DISTINCT ON (s.id)
                  s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  b.location AS location,
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NOT NULL
             AND s.cancelled_at IS NULL AND s.held_at IS NULL
             AND s.responded_at IS NULL
             AND NOT """ + BAND_ANSWERED_SQL + """
             AND NOT EXISTS (SELECT 1 FROM advance_reminders r
                             WHERE r.show_id = s.id AND r.days_before = %s)
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
             AND """ + vsql + """
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.id, b.id DESC NULLS LAST""",
        (days_before, days_before, *vparams),
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


def shows_due_for_schedule(cur, days_before=None):
    """2026-09-24 research #3: shows due the week-out CONFIRMED SCHEDULE email
    — shows_due_for_followup's twin with the response gates removed, because
    this one goes to every show whether the band has answered or not.

    Everything else decides identically to the chase tiers, on purpose: the
    welcome must already have gone out (which is also what keeps a
    manual-advance booking and a welcome still held as a draft out of here),
    never a cancelled or on-hold show, never a 3rd-party show with band emails
    off, and the tier closes on its own advance_reminders row so a second run
    sends nothing. Carries the booking's schedule columns so dayahead can
    render the same block it sends at T-1, and `responded` so the caller knows
    whether the chase paragraph belongs under it."""
    days_before = SCHEDULE_TIER if days_before is None else days_before
    cur.execute(
        r"""SELECT DISTINCT ON (s.id)
                  s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  b.location AS location, b.event_name AS event_name,
                  b.lead_name AS lead_name, b.lead_phone AS lead_phone,
                  b.load_in AS load_in, b.soundcheck AS soundcheck,
                  b.event_start AS event_start, b.event_end AS event_end,
                  b.curfew AS curfew, b.set_time AS set_time,
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email,
                  b.created_at AS booking_created_at,
                  (s.responded_at IS NOT NULL OR """ + BAND_ANSWERED_SQL + r""") AS responded
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NOT NULL
             AND s.cancelled_at IS NULL AND s.held_at IS NULL
             AND NOT EXISTS (SELECT 1 FROM advance_reminders r
                             WHERE r.show_id = s.id AND r.days_before = %s)
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.id, b.id DESC NULLS LAST""",
        (days_before, days_before),
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


def shows_due_for_thankyou(cur):
    """Show ids whose thank-you should go out on its own now (audit
    2026-09-16 #23, Brian's call: automatic, date-driven) — responded, the
    day after the show, not already sent. A short catch-up window (up to a
    week back) tolerates a missed lifecycle run without sending a thank-you
    that reads as comically late. 2026-09-21 sweep (PRIOR-2): the lifecycle
    calls tools/finalize_thankyou.send_for_show(after_show=True), which sends
    the post-show variant and accepts exactly this window; its past-show
    refusal applies only to manual Finalize. It still no-ops a cancelled or
    3rd-party-silent show. finalized_at (the human sign-off) is untouched
    either way — this is independent of it, not a substitute."""
    cur.execute(
        """SELECT s.id AS show_id
           FROM shows s JOIN artists a ON a.id = s.artist_id
           WHERE s.cancelled_at IS NULL AND s.held_at IS NULL
             AND s.thankyou_sent_at IS NULL
             AND (s.responded_at IS NOT NULL
                  OR EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id))
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE - 7 AND CURRENT_DATE - 1
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.show_date""")
    return [r["show_id"] for r in cur.fetchall()]


def mark_advance_drafted(cur, show_id):
    """Name kept from the drafting era — this column (advance_draft_created_at)
    now means 'the initial advance was SENT' as of the 2026-09-13 live-send
    migration. Not renamed: touches too many other readers (advance_status
    view, status_log.py, status_sheet.py, the dashboard) for the size of
    this change to be worth it; the meaning shift is real, just not the name."""
    cur.execute(
        "UPDATE shows SET advance_draft_created_at = COALESCE(advance_draft_created_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def mark_parking_sheet_sent(cur, show_id):
    """The Washington Park garage parking sheet reached the band (on the
    welcome, or from the dashboard's "Parking sheet not sent" item)."""
    cur.execute("UPDATE shows SET parking_sheet_sent_at = COALESCE(parking_sheet_sent_at, now()) "
                "WHERE id = %s", (show_id,))


def memo_parking_sheet_due(cur):
    """Memorial Hall shows whose latest Parking answer is Washington Park and
    whose garage sheet hasn't gone out, with a welcome that won't carry it: the
    welcome already went, or Memo's welcome is paused (staff send the form link
    by hand). Brian, 2026-10-01: the sheet rides the welcome when Parking is set
    by then; otherwise staff send it from the dashboard."""
    paused = bool(VENUE_LADDERS.get("Memorial Hall", {}).get("paused"))
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.venue = 'Memorial Hall' AND s.show_date >= CURRENT_DATE
                     AND s.cancelled_at IS NULL AND s.held_at IS NULL
                     AND s.parking_sheet_sent_at IS NULL
                     AND (s.advance_draft_created_at IS NOT NULL OR %s)
                     AND (SELECT sub.data->>'parking' FROM submissions sub
                           WHERE sub.show_id = s.id AND sub.data->>'_form' = 'memo'
                             AND COALESCE(sub.data->>'parking', '') <> ''
                           ORDER BY sub.submitted_at DESC, sub.id DESC LIMIT 1) = 'Washington Park'
                   ORDER BY s.show_date""", (paused,))
    return cur.fetchall()


def mark_advance_held_as_draft(cur, show_id):
    """The welcome was put in Production@3cdc.org's drafts instead of sent
    (bookings.draft_only — Brian, 2026-09-15). Deliberately does NOT stamp
    advance_draft_created_at: that column means the band has been contacted,
    and nobody has been. This stamp only stops the lifecycle from building the
    same draft again tomorrow morning."""
    cur.execute(
        "UPDATE shows SET advance_held_draft_at = COALESCE(advance_held_draft_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def mark_advance_sent_by_hand(cur, show_id, days_out=None):
    """Brian sent the held draft himself out of Outlook (Brian, 2026-09-15).

    This is the other half of "draft, don't send": clearing the checkbox tells
    the system to SEND the welcome, which is wrong once a human already has.
    This says the band has been contacted without sending anything — the show
    leaves 'queued', and the 7/3/2/1-day reminder ladder starts working again,
    which it can't while the system believes nobody has written to them."""
    mark_advance_drafted(cur, show_id)
    cur.execute("UPDATE shows SET advance_held_draft_at = NULL WHERE id = %s", (show_id,))
    if days_out is not None:
        mark_stale_followup_tiers_skipped(cur, show_id, days_out)


def clear_advance_held_draft(cur, show_id):
    """Un-ticking "draft, don't send" puts the show back in the normal queue —
    the next lifecycle run sends the welcome for real. 2026-09-21 sweep
    (PRIOR-25): not once the band has answered — the stamp stays, so the stale
    draft surfaces in Needs you instead of vanishing from view."""
    cur.execute("UPDATE shows s SET advance_held_draft_at = NULL WHERE s.id = %s AND NOT "
                + _HELD_DRAFT_ANSWERED_SQL, (show_id,))


def discard_held_draft(cur, show_id):
    """Staff deleted a stale held welcome from Production@3cdc.org drafts
    (2026-09-21 sweep, PRIOR-25). Guarded to answered/cancelled shows, so it
    can never release an unanswered show into the welcome send queue."""
    cur.execute("UPDATE shows s SET advance_held_draft_at = NULL "
                "WHERE s.id = %s AND s.advance_draft_created_at IS NULL AND "
                + _HELD_DRAFT_STALE_SQL + " RETURNING s.id", (show_id,))
    return cur.fetchone() is not None


def mark_followup_sent(cur, show_id, days_before=7, sent=True):
    """Record that THIS tier is resolved for this show — sent=True for an
    actual send, sent=False when there was nothing to send (no email on
    file) or when mark_stale_followup_tiers_skipped pre-skipped it as
    already stale at booking time. Either way, shows_due_for_followup's
    NOT EXISTS check closes this tier for good the moment ANY row exists
    here, real send or not — `sent` only matters for telling the two
    apart later if that's ever needed for reporting. Also keeps the
    legacy shows.followup_draft_created_at column stamped on whichever
    tier resolves FIRST (renamed in meaning, not in name, same reasoning
    as mark_advance_drafted) so status_log.py/status_sheet.py/the
    advance_status view need no changes. Named mark_followup_drafted
    before the live-send migration (2026-09-13)."""
    cur.execute(
        "INSERT INTO advance_reminders (show_id, days_before, sent) VALUES (%s, %s, %s) "
        "ON CONFLICT (show_id, days_before) DO NOTHING", (show_id, days_before, sent),
    )
    cur.execute(
        "UPDATE shows SET followup_draft_created_at = COALESCE(followup_draft_created_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def mark_schedule_sent(cur, show_id, sent=True, chased=False):
    """Close the week-out tier (2026-09-24 research #3). Deliberately the SAME
    advance_reminders row mark_followup_sent would have written for tier 7 —
    reusing that UNIQUE(show_id, days_before) is what makes "one email at seven
    days, never two" true without a parallel table to keep in step.

    `chased` stamps the legacy shows.followup_draft_created_at only when the
    chase paragraph actually rode along: a show that already answered got a
    schedule, not a follow-up, and the status views read that column."""
    cur.execute(
        "INSERT INTO advance_reminders (show_id, days_before, sent) VALUES (%s, %s, %s) "
        "ON CONFLICT (show_id, days_before) DO NOTHING", (show_id, SCHEDULE_TIER, sent),
    )
    if chased:
        cur.execute(
            "UPDATE shows SET followup_draft_created_at = COALESCE(followup_draft_created_at, now()) "
            "WHERE id = %s", (show_id,),
        )


def mark_stale_followup_tiers_skipped(cur, show_id, days_out, venue=None):
    """Live-send migration (Brian, 2026-09-13): right after a show's welcome
    sends, pre-skip — for good, never reconsidered — any FOLLOWUP_TIERS
    mark that's already on or before TODAY relative to `days_out` (the
    show's days-out at the moment the welcome sent). A tier coinciding
    with the SAME day as the welcome counts as already-passed too (a
    reminder should never fire the same day as the welcome it's supposedly
    following up on) — hence `>=`, not `>`. Only tiers strictly ahead of
    today are left open, to fire normally later via shows_due_for_followup
    as their own date arrives. No-ops if days_out is None (no show_date)."""
    if days_out is None:
        return
    if venue is None:
        cur.execute("SELECT venue FROM shows WHERE id=%s", (show_id,))
        row = cur.fetchone()
        venue = row["venue"] if row else None
    # Review 2026-09-14 (M1): a band booked 4 days out used to get the
    # welcome, the 3-day reminder the next morning and the 1-day reminder two
    # days later. No band-facing reminder fires within 48 hours of the
    # welcome: a tier is skipped when its day is less than 2 days after
    # today, i.e. tier > days_out - 2.
    for tier in tiers_for(venue):
        if tier > days_out - 2:
            cur.execute(
                "INSERT INTO advance_reminders (show_id, days_before, sent) "
                "VALUES (%s, %s, false) ON CONFLICT (show_id, days_before) DO NOTHING",
                (show_id, tier),
            )


def shows_due_for_unresponded_alert(cur, days_before=3):
    """Shows within `days_before` days of their date with no response and no
    internal alert sent yet — Brian's manual-follow-up flag (2026-09-13).
    Fires once per show, whether or not the band has an email on file.

    Audit 2026-09-13:
      #12 — manual-entry shows (bookings.skip_welcome_email, no welcome ever
            sent) are included, flagged `manual`, so a form staff never
            filled in still gets caught.
      #21 — never within 24h of the show's welcome (or, for a manual show,
            of its booking) so a late booking doesn't trip the alert minutes
            after its own welcome went out.
      #4  — cancelled and on-hold shows never alert."""
    cur.execute(
        r"""SELECT DISTINCT ON (s.id)
                  s.id AS show_id, a.id AS artist_id, a.name AS artist_name,
                  a.last_email AS email, s.venue, s.show_series AS series, s.show_date,
                  COALESCE(b.skip_welcome_email, false) AS manual
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.responded_at IS NULL
             AND s.unresponded_alert_sent_at IS NULL
             AND s.cancelled_at IS NULL AND s.held_at IS NULL
             AND NOT (lower(btrim(COALESCE(s.show_series,''))) = '3rd party' AND COALESCE(a.last_email,'') = '')
             AND NOT """ + THIRD_PARTY_SILENT_SQL + r"""
             AND NOT """ + BAND_ANSWERED_SQL + r"""
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
             AND (
                  (s.advance_draft_created_at IS NOT NULL
                   AND s.advance_draft_created_at <= now() - interval '24 hours')
               -- a paused-welcome venue (Memo) is staff-sent like a manual show
               OR ((b.skip_welcome_email IS TRUE OR NOT """ + _paused_sql() + r""")
                   AND s.advance_draft_created_at IS NULL
                   AND COALESCE(b.created_at, s.created_at) <= now() - interval '24 hours')
             )
           ORDER BY s.id, b.id DESC NULLS LAST""",
        (days_before,),
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


def mark_unresponded_alert_sent(cur, show_id):
    cur.execute(
        "UPDATE shows SET unresponded_alert_sent_at = COALESCE(unresponded_alert_sent_at, now()) "
        "WHERE id = %s", (show_id,),
    )


def bookings_on(cur, event_date):
    """Every booking (one row per artist) for a specific date — the raw material
    for the daily digest's 'shows today' section. Artists sharing a bill share
    event_name/venue; the caller groups them. Ordered by set start within each
    bill (Artist 1 first), which is sorted in Python because event_start is free
    text ('7:00pm') — see parse_clock. 2026-09-21 sweep (IDENT-9): each row
    carries `cancelled` (its show is soft-cancelled) so the digest can drop it."""
    cur.execute(
        """SELECT b.id, b.event_name, b.venue, b.location, b.series, b.artist_name,
                  b.load_in, b.soundcheck, b.event_start, b.event_end, b.curfew,
                  (s.cancelled_at IS NOT NULL) AS cancelled
           FROM bookings b""" + _BOOKING_EDIT_SHOW_JOIN + """
           WHERE b.event_date = %s
           ORDER BY b.venue, b.event_name, b.id""",
        (event_date,),
    )
    rows = cur.fetchall()
    return sorted(rows, key=lambda r: (
        r.get("venue") or "", r.get("event_name") or "",
        act_sort_key({"set_start": r.get("event_start"), "id": r.get("id")}),
    ))


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
    daily digest's ranked at-a-glance list.
    2026-09-24 research #11: link_opened_at rides along (when the band first
    opened the emailed /s/ link) so a row still waiting on a form can say
    whether the welcome was ever read — see welcome_open_phrase. Left out of
    the view itself; only this one caller wants it."""
    cur.execute(
        """SELECT v.*,
                  (SELECT max(sl.first_opened_at) FROM short_links sl
                    WHERE sl.show_id = v.show_id) AS link_opened_at
           FROM advance_status v
           WHERE v.days_until_show BETWEEN 0 AND %s
           ORDER BY v.days_until_show ASC, v.band ASC""",
        (days,),
    )
    return cur.fetchall()


def dashboard_status(cur):
    """Every show from today forward, no upper bound — the live dashboard's
    feed (Brian, 2026-09-12: 'nothing that has passed'). Unlike
    upcoming_advance_status this never caps how far out it looks; the
    dashboard groups/sorts client-side."""
    cur.execute(
        """SELECT * FROM advance_status
           WHERE days_until_show >= 0
           ORDER BY show_date ASC, venue ASC, band ASC"""
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


def artist_count_for_event(cur, venue, event_date, series=None):
    """How many artists are actually booked on this bill at venue+date — the
    internal bill, or (series '3rd Party') the 3rd-party event, never mixed
    (Brian, 2026-09-14). Counted, not declared: the booking form stopped asking
    "Bands on the Bill" on 2026-09-15, because the answer was already sitting in
    the bookings table and a typed one could disagree with it. 0 if none."""
    cur.execute(
        r"""SELECT COUNT(DISTINCT lower(btrim(regexp_replace(b.artist_name,'\s+',' ','g')))) AS n
            FROM bookings b
            LEFT JOIN artists a ON a.match_key = lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g')))
            LEFT JOIN shows s ON s.artist_id = a.id AND s.venue = b.venue AND s.show_date = b.event_date
            WHERE b.venue=%s AND b.event_date=%s AND COALESCE(btrim(b.artist_name),'') <> ''
              AND (lower(btrim(COALESCE(b.series,''))) = '3rd party') = %s
              AND s.cancelled_at IS NULL""",
        (venue, event_date, is_third_party(series)),
    )
    row = cur.fetchone()
    return (row["n"] or 0) if row else 0


def acts_for_event(cur, venue, event_date, series=None, event_name=None):
    """2026-09-21 sweep (FLOW-15): who's on this bill, from bookings — the welcome's
    'The bill:' block, which used to list only acts in the same lifecycle batch.
    Same grouping as artist_count_for_event; cancelled AND held shows excluded (a
    band-facing list never names an act that isn't playing or isn't confirmed).
    A 3rd-party bill is its own event: pass event_name. [{name, set_start, set_time}]."""
    mk = r"lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g')))"
    sql = (r"""SELECT DISTINCT ON (""" + mk + r""")
                  COALESCE(a.name, btrim(b.artist_name)) AS name,
                  COALESCE(b.event_start, '') AS set_start,
                  COALESCE(b.set_time, '') AS set_time
            FROM bookings b
            LEFT JOIN artists a ON a.match_key = """ + mk + r"""
            LEFT JOIN shows s ON s.artist_id = a.id AND s.venue = b.venue AND s.show_date = b.event_date
            WHERE b.venue=%s AND b.event_date=%s AND COALESCE(btrim(b.artist_name),'') <> ''
              AND (lower(btrim(COALESCE(b.series,''))) = '3rd party') = %s
              AND s.cancelled_at IS NULL AND s.held_at IS NULL""")
    params = [venue, event_date, is_third_party(series)]
    if is_third_party(series):
        sql += r" AND lower(btrim(COALESCE(b.event_name,''))) = lower(btrim(%s))"
        params.append(event_name or "")
    sql += " ORDER BY " + mk + ", b.id DESC"
    cur.execute(sql, params)
    return cur.fetchall()


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
            stage_type, own_engineer, merch, band_tent, large_vehicle,
            vehicle_count, large_vehicle_count, trailer, crew_count, data, source
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
            # large_vehicle (boolean) is retired going forward (2026-09-13) —
            # the form now asks large_vehicle_count instead; this stays None
            # for every new submission and only ever has a value on old rows.
            to_bool(data.get("large_vehicle")), to_int(data.get("vehicle_count")),
            to_int(data.get("large_vehicle_count")),
            # 2026-09-24 research #(b): trailer is the flag a vehicle COUNT can't
            # carry (van + trailer = one vehicle, and it can't use the FSQ garage);
            # crew_count is additive to performers, which keeps its own meaning.
            to_bool(data.get("trailer")), to_int(data.get("crew_count")),
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


def record_submission(form: dict, file_info=None, source="form", resolve_booking=True,
                      carry_plot=True, stamp_responded=True):
    """One transaction: resolve which artist+show this submission belongs to,
    insert it, stamp responded_at, link any uploaded file. Returns a dict:
    {artist_id, show_id, submission_id, artist_name, match, carried_from, name_kept}.
    Raises on failure — the form treats that as non-fatal.

    Resolution (2026-09-13 audit #6):
      1. form["artist_id"] — ONLY set by app.py after verifying the signed
         artist token from the band's own link. Same artist record, even if
         they edited the name — the edit is NOT applied (2026-09-21 sweep), it
         comes back as name_kept for Brian to decide.
      2. the typed name matches an artist who is booked at this venue+date.
      3. otherwise, if exactly ONE unresponded booking exists at this
         venue+date, attach to it (match status 'attached_auto'; Brian gets a
         Confirm / Detach email).
      4. otherwise a new artist/show from the typed name, match status
         'pending_pick' (Brian picks the booking from an email).
    Carry-forward (audit #8): a submission with no stage plot upload reuses
    the artist's most recent stored plot, recorded as stage_plot_carried_from."""
    import json
    name = (form.get("band_name") or "(unknown)").strip()
    known_id = form.get("artist_id")
    try:
        known_id = int(known_id) if known_id else None
    except (TypeError, ValueError):
        known_id = None
    venue = form.get("venue")
    show_date = to_date(form.get("show_date"))
    series = (form.get("show_series") or "").strip() or None
    if series and series.lower() == "default":
        series = None
    match = None
    name_kept = None
    with get_conn() as conn:
        with conn.cursor() as cur:
            artist_id = show_id = None
            stored = get_artist(cur, known_id) if known_id else None
            if stored:
                # 2026-09-21 sweep (DBA-2): never rename the artists row from a form. Bookings and
                # the sheet kept the old name, so the next run re-minted it as a ghost show that got
                # welcomed while the real one sat held. Brian decides; Edit Show carries a rename.
                if normalize(name) != normalize(stored["name"]):
                    name_kept = name
                artist_id = upsert_artist(cur, stored["name"], email=form.get("contact_email") or None,
                                          phone=form.get("contact_phone") or None, known_id=known_id)
            elif resolve_booking and venue and show_date:
                by_name = find_artist_by_name(cur, name)
                booked = show_for_artist_at(cur, by_name["id"], venue, show_date) if by_name else None
                if booked:
                    artist_id = by_name["id"]
                else:
                    cands = unresponded_shows_at(cur, venue, show_date)
                    if len(cands) == 1 and names_plausible(name, cands[0]["artist_name"]):
                        artist_id, show_id = cands[0]["artist_id"], cands[0]["show_id"]
                        cur.execute("""UPDATE artists SET last_email = COALESCE(%s, last_email),
                                       last_phone = COALESCE(%s, last_phone) WHERE id=%s""",
                                    (form.get("contact_email") or None,
                                     form.get("contact_phone") or None, artist_id))
                        match = {"status": "attached_auto", "booked_show_id": show_id,
                                 "booked_name": cands[0]["artist_name"], "candidates": []}
                    else:
                        match = {"status": "pending_pick", "booked_show_id": None,
                                 "candidates": [{"show_id": c["show_id"], "artist_name": c["artist_name"]}
                                                for c in cands]}
            if artist_id is None:
                # 2026-09-21 sweep (DBA-6): blank means keep — '' through COALESCE wiped last_email/last_phone.
                artist_id = upsert_artist(cur, name, email=form.get("contact_email") or None,
                                          phone=form.get("contact_phone") or None)
            if show_id is None:
                show_id = upsert_show(cur, artist_id, venue, show_date, series=series)

            carried_from = None
            if carry_plot and not form.get("stage_plot_file"):
                cur.execute(
                    """SELECT sub.data->>'stage_plot_file' AS stored, sub.submitted_at,
                              f.filename, f.mime, f.size
                       FROM submissions sub
                       LEFT JOIN files f ON f.submission_id = sub.id
                            AND f.stored_name = sub.data->>'stage_plot_file'
                       WHERE sub.artist_id=%s AND COALESCE(sub.data->>'stage_plot_file','') <> ''
                       ORDER BY sub.submitted_at DESC LIMIT 1""", (artist_id,))
                prior = cur.fetchone()
                if prior:
                    carried_from = prior["submitted_at"].date().isoformat()
                    form["stage_plot_file"] = prior["stored"]
                    form["stage_plot_carried_from"] = carried_from
                    file_info = {"filename": prior["filename"] or prior["stored"],
                                 "stored_name": prior["stored"], "mime": prior["mime"],
                                 "size": prior["size"]}

            sub_id = insert_submission(cur, artist_id, show_id, form, source=source)
            if stamp_responded:
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
            if match:
                cur.execute(
                    """INSERT INTO submission_matches (submission_id, booked_show_id, typed_name,
                           venue, show_date, status, candidates)
                       VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (sub_id, match["booked_show_id"], name, venue, show_date, match["status"],
                     json.dumps(match["candidates"])))
                match["id"] = cur.fetchone()["id"]
            artist = get_artist(cur, artist_id)
        conn.commit()
    return {"artist_id": artist_id, "show_id": show_id, "submission_id": sub_id,
            "artist_name": artist["name"] if artist else name, "match": match,
            "carried_from": carried_from, "name_kept": name_kept}


# ── queries: prefill, returning-artist logic, search ────────────────────────

def find_artist_by_name(cur, name):
    cur.execute(f"SELECT * FROM artists WHERE match_key = {_SQL_MATCH_KEY}", (name,))
    return cur.fetchone()


_NAME_STOPWORDS = {"the", "and", "&", "band", "feat", "feat.", "ft", "ft.", "featuring",
                   "trio", "quartet", "quintet", "duo", "group", "orchestra", "dj", "with", "w/"}


def _name_tokens(name):
    return {t for t in re.split(r"[^a-z0-9]+", normalize(name)) if t and t not in _NAME_STOPWORDS}


def names_plausible(typed, booked):
    """Review 2026-09-14 (H5): is `typed` plausibly the same act as `booked`?
    True when one normalized name contains the other, at least half of the
    meaningful words overlap with at least two meaningful words in common (one,
    when either name is a single word), or the two spellings are a close edit-distance
    match (a typo like "LimeLght" for "LimeLight", Brian FSQ 9/18, shares no
    whole token so the overlap test alone misses it). Gate on auto-attaching a
    submission to the one unanswered booking — before this, ANY typed name
    attached to whoever hadn't answered yet. Only ever consulted when there is
    exactly one unanswered booking at the venue+date (see record_submission),
    so a high full-string similarity there is a safe bet on the same act."""
    a, b = normalize(typed), normalize(booked)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True
    ta, tb = _name_tokens(a), _name_tokens(b)
    if ta and tb:
        # 2026-09-21 sweep (PRIOR-24): one shared word ("Square One" vs "Jazz on the
        # Square Trio") was half of a two-word name and auto-attached to the wrong band.
        shared, small = len(ta & tb), min(len(ta), len(tb))
        if shared >= (1 if small == 1 else 2) and shared / small >= 0.5:
            return True
    return SequenceMatcher(None, a, b).ratio() >= 0.85


def get_artist(cur, artist_id):
    cur.execute("SELECT * FROM artists WHERE id = %s", (artist_id,))
    return cur.fetchone()


def set_artist_note(cur, artist_id, notes, rating):
    """The staff post-show note + 1–5 advance-accuracy pip (2026-09-24 research
    #12). Blank note or no pip clears that half. Rating is clamped here as well
    as in the column's CHECK so a hand-posted 9 is a no-op, not a 500. Returns
    True if the artist exists. Staff-only: nothing band-facing ever reads these."""
    notes = (notes or "").strip() or None
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        rating = None
    if rating is not None and not 1 <= rating <= 5:
        rating = None
    cur.execute("UPDATE artists SET notes=%s, advance_rating=%s WHERE id=%s RETURNING id",
                (notes, rating, artist_id))
    return cur.fetchone() is not None


def newest_submission(cur, artist_id):
    cur.execute(
        "SELECT * FROM submissions WHERE artist_id=%s ORDER BY submitted_at DESC LIMIT 1",
        (artist_id,),
    )
    return cur.fetchone()


def submission_for_show(cur, artist_id, venue, show_date):
    """What a show's paperwork fills from: this show's own newest submission,
    else (returning-band pre-fill, H2) the artist's newest from any show.
    2026-09-21 sweep: newest-across-all-shows used to win outright, so a band's
    later booking overwrote an earlier show's doc/sheet with its answers."""
    if artist_id and venue and show_date:
        cur.execute(
            """SELECT sub.* FROM submissions sub JOIN shows s ON s.id = sub.show_id
               WHERE s.artist_id=%s AND s.venue=%s AND s.show_date=%s
               ORDER BY sub.submitted_at DESC LIMIT 1""",
            (artist_id, venue, show_date),
        )
        row = cur.fetchone()
        if row:
            return row
    return newest_submission(cur, artist_id) if artist_id else None


def played_within(cur, artist_id, ref_date, months=6, exclude_show_id=None):
    """Returns the newest PRIOR submission if this band has one whose show_date
    is within `months` before ref_date, else None. This is the returning-artist
    test — deliberately cross-venue.

    exclude_show_id (Brian, 2026-09-16): the show being welcomed right now, so a
    submission recorded for THIS SAME SHOW doesn't count as "their last show".
    That situation didn't used to exist — a submission only ever showed up
    before a welcome sent if staff filled the band's own form in by hand via
    the old separate link — but the booking form's own "band's own answers"
    section (2026-09-16) creates one at BOOKING time, before any welcome has
    gone out. First case that hit it: Jet Jurgensmeyer, booked with their
    answers typed in directly, got called "returning" with "their last show"
    recap being the same show being welcomed — worse, cross-contaminated with
    a bill-mate's data via the unrelated column-reassignment bug (see
    docmerge's per-column diff, which is position- not artist-keyed)."""
    if isinstance(ref_date, str):
        ref_date = to_date(ref_date)
    if not ref_date:
        ref_date = dt.date.today()
    # 2026-09-21 sweep (DBA-7): only shows on/before ref_date are candidates — a
    # newer submission for a LATER booking (staff-typed at booking time) used to
    # win the LIMIT 1, go negative below, and hide the real prior show.
    cur.execute(
        """SELECT * FROM submissions WHERE artist_id=%s AND show_id IS DISTINCT FROM %s
             AND COALESCE(show_date, submitted_at::date) <= %s
           ORDER BY COALESCE(show_date, submitted_at::date) DESC, submitted_at DESC LIMIT 1""",
        (artist_id, exclude_show_id, ref_date),
    )
    sub = cur.fetchone()
    if not sub:
        return None
    last = sub.get("show_date") or (sub.get("submitted_at").date()
                                    if sub.get("submitted_at") else None)
    if not last:
        return None
    delta_days = (ref_date - last).days
    if 0 <= delta_days <= months * 31:
        return sub
    # audit 2026-09-16 #23: the branch that used to sit here treated a
    # submission for a show up to 31 days in the FUTURE as "their last
    # show" too (delta_days < 0 means `last` is after ref_date) — a second,
    # different upcoming booking close by got called returning with a
    # recap of a show that hasn't happened yet, the same class of bug
    # exclude_show_id fixes for the identical-show case, just not caught
    # by it since these are two different shows.
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
    """Sourced from advance_status (Brian, 2026-09-13), not raw `shows` — the
    template's Status column used to read `s.status`, a column dropped
    2026-09-09; it had been silently rendering blank ever since. The view
    carries every column the template needs (show_date/venue/show_series)
    plus the real computed `state`, the same one the dashboard reads."""
    # advance_held_draft_at is joined from `shows` rather than added to the view
    # (2026-09-15): the view is recreated wholesale by migration and adding a
    # column to it for one button on one page isn't worth that churn. It drives
    # the artist page's "I sent it" action — see app.show_advance_sent.
    cur.execute(
        """SELECT v.*, s.advance_held_draft_at,
                  """ + _HELD_DRAFT_STALE_SQL + """ AS held_draft_stale
           FROM advance_status v JOIN shows s ON s.id = v.show_id
           WHERE v.artist_id=%s ORDER BY v.show_date DESC NULLS LAST""",
        (artist_id,),
    )
    return cur.fetchall()


def get_show(cur, show_id):
    cur.execute("SELECT * FROM shows WHERE id = %s", (show_id,))
    return cur.fetchone()


def show_for_booking(cur, artist_name, venue, show_date):
    r"""The show row a booking belongs to — artist matched on the same
    normalization every other booking/show join in this file uses (match_key),
    so a stray capital or double space can't miss it. None if the pipeline
    hasn't created the show yet."""
    if not (artist_name and venue and show_date):
        return None
    cur.execute(
        r"""SELECT s.* FROM shows s JOIN artists a ON a.id = s.artist_id
            WHERE a.match_key = lower(btrim(regexp_replace(%s, '\s+', ' ', 'g')))
              AND s.venue = %s AND s.show_date = %s
            ORDER BY s.id DESC LIMIT 1""",
        (artist_name, venue, show_date),
    )
    return cur.fetchone()


def get_booking_for_show(cur, show):
    r"""The bookings row for this show (same match_key/venue/date join every
    other booking/show lookup here uses), or None if staff never logged one —
    a show can exist purely from a real band submission. `show` is a shows-
    with-artist row (needs venue, show_date, match_key)."""
    if not (show.get("venue") and show.get("show_date") and show.get("match_key")):
        return None
    cur.execute(
        r"""SELECT * FROM bookings
            WHERE venue=%s AND event_date=%s
              AND lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g'))) = %s
            ORDER BY id DESC LIMIT 1""",
        (show["venue"], show["show_date"], show["match_key"]),
    )
    return cur.fetchone()


def find_booking(cur, venue, event_date, artist_name):
    """Same identity key as uq_bookings_ident (venue, event_date, normalized
    artist_name) — used by /booking to detect a re-POST for a band already
    booked that night before deciding insert vs. update (audit 2026-09-16
    #11)."""
    if not (venue and event_date and artist_name):
        return None
    cur.execute(
        r"""SELECT * FROM bookings
            WHERE venue=%s AND event_date=%s
              AND lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g')))
                = lower(btrim(regexp_replace(%s, '\s+', ' ', 'g')))
            ORDER BY id DESC LIMIT 1""",
        (venue, event_date, artist_name),
    )
    return cur.fetchone()


def show_state(cur, show_id):
    """This show's current computed state from advance_status, or None if the
    id doesn't exist. Used by the finalize endpoint to re-check server-side
    that a response is actually on file before allowing sign-off — never
    trust that the button was only ever shown when it should have been."""
    cur.execute("SELECT state FROM advance_status WHERE show_id = %s", (show_id,))
    row = cur.fetchone()
    return row["state"] if row else None


def finalize_show(cur, show_id):
    """Sign off a show's advance as fully complete (Brian, 2026-09-13) — the
    point after a band has responded where a human has reviewed everything.
    `WHERE finalized_at IS NULL` makes this atomically idempotent: a 0-row
    result means it was already finalized (double-click, two staff at once,
    a retried request), so the caller knows never to send a second thank-you
    email for it. Returns the show's id + artist_id + contact email when this
    call was the genuine first transition, or None when it was a no-op."""
    cur.execute(
        """UPDATE shows SET finalized_at = now()
           WHERE id = %s AND finalized_at IS NULL
           RETURNING id, artist_id""",
        (show_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    cur.execute("SELECT last_email FROM artists WHERE id = %s", (row["artist_id"],))
    artist = cur.fetchone()
    return {"show_id": row["id"], "artist_id": row["artist_id"],
            "email": (artist or {}).get("last_email")}


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

# Artist order (Brian, 2026-09-15). Slots — opener / direct support / headliner
# — are retired. An act's position on the bill is ARTIST 1 / 2 / 3, derived from
# its set start time: earliest is Artist 1, latest is Artist 3. Nothing declares
# it and nothing stores it, so a band booked later with an earlier start time
# renumbers the whole bill by itself — no copying a band's answers into the next
# slot down, nothing to migrate, nothing that can be half-moved.
#
# "Band" is deliberately not the word: plenty of these are solo artists.

# A set starting before this hour belongs to the night before — a 12:30a set
# sorts AFTER a 10:00p one, not seven hours before it.
NIGHT_ROLLOVER_MIN = 4 * 60

_CLOCK_RE = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m?\.?\s*$", re.I)


def parse_clock(s):
    """'7:00pm' / '7pm' / '7:00 p.m.' / '19:00' -> minutes past midnight.
    None when there's nothing parseable — the caller decides what that means.
    Times before 4:00am roll to the next day (see NIGHT_ROLLOVER_MIN)."""
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    m = _CLOCK_RE.match(s)
    if m:
        hour, minute, half = int(m.group(1)), int(m.group(2) or 0), m.group(3).lower()
        if not (1 <= hour <= 12) or minute > 59:
            return None
        hour = hour % 12 + (12 if half == "p" else 0)
    else:
        m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*$", s)   # 24-hour, as the form posts it
        if not m:
            return None
        hour, minute = int(m.group(1)), int(m.group(2))
        if hour > 23 or minute > 59:
            return None
        # audit 2026-09-16 #20 (root cause C): a bare hour 1-6 with no am/pm
        # is read literally as 1am-6am here, but a human typing a show time
        # with no am/pm essentially never means the middle of the night —
        # Rob Keenan's FSQ 9/23 "5:00" (meant 5pm) sorted him at 05:00 and
        # was emailed to the band as "6:30pm -> 5:00". Legacy/loose data
        # only (a sheet cell, an old row) — _validate_booking_data rejects
        # a bare H:MM outright at entry now, so new data can't create this.
        if 1 <= hour <= 6:
            hour += 12
    mins = hour * 60 + minute
    return mins + 1440 if mins < NIGHT_ROLLOVER_MIN else mins


def act_sort_key(act):
    """Earliest set start first; an act with no start time yet sorts last, in
    the order it was entered, so a half-filled bill still renders stably."""
    mins = parse_clock((act or {}).get("set_start"))
    seq = (act or {}).get("id") or 0
    return (0, mins, seq) if mins is not None else (1, 0, seq)


def order_acts(acts):
    """Acts sorted by set start, each stamped `artist_order` 1..N. This is the
    only thing that decides who is Artist 1 — call it on every read."""
    ordered = sorted(acts or [], key=act_sort_key)
    for i, a in enumerate(ordered, 1):
        a["artist_order"] = i
    return ordered


def artist_label(n):
    """'Artist 1' — the label on the paperwork and in every internal list."""
    return f"Artist {n}" if n else ""


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
    # 2026-09-21 sweep (PRIOR-10): default=str — a stray time/date cell must not crash the import
    cur.execute("UPDATE events SET details=%s WHERE id=%s",
                (json.dumps(cur_details, default=str), event_id))


def add_act(cur, event_id, artist_id, submission_id=None, set_time=None,
            set_start=None, set_end=None, load_in=None, soundcheck=None,
            sheet_fields=None):
    """Put an artist on a bill. The act is keyed by its ARTIST — there is no
    slot to collide over, so re-running an import just updates the same row.
    `set_time` is the set LENGTH ('45'); `set_start` is what orders the bill."""
    import json
    cur.execute(
        """INSERT INTO event_acts (event_id, artist_id, submission_id, set_time,
                                   set_start, set_end, load_in, soundcheck,
                                   sheet_fields)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (event_id, artist_id) DO UPDATE SET
             submission_id=EXCLUDED.submission_id,
             set_time=COALESCE(EXCLUDED.set_time, event_acts.set_time),
             set_start=COALESCE(EXCLUDED.set_start, event_acts.set_start),
             set_end=COALESCE(EXCLUDED.set_end, event_acts.set_end),
             load_in=COALESCE(EXCLUDED.load_in, event_acts.load_in),
             soundcheck=COALESCE(EXCLUDED.soundcheck, event_acts.soundcheck),
             sheet_fields=event_acts.sheet_fields || EXCLUDED.sheet_fields
           RETURNING id""",
        (event_id, artist_id, submission_id, set_time, set_start, set_end,
         load_in, soundcheck, json.dumps(sheet_fields or {}, default=str)),   # 2026-09-21 sweep (PRIOR-10)
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
    """Acts in column order — Artist 1 first — each stamped `artist_order` and
    carrying its artist + the submission to fill from (the linked submission,
    else this show's own newest, else the artist's newest from any show — see
    submission_for_show). Order is computed here, every time, from set start:
    see order_acts. `id` is the tiebreak, so the query orders by it."""
    ev = get_event(cur, event_id) or {}
    cur.execute(
        "SELECT * FROM event_acts WHERE event_id=%s ORDER BY id", (event_id,)
    )
    acts = order_acts(cur.fetchall())
    for a in acts:
        a["artist"] = get_artist(cur, a["artist_id"]) if a.get("artist_id") else None
        if a.get("submission_id"):
            a["submission"] = get_submission(cur, a["submission_id"])
        elif a.get("artist_id"):
            a["submission"] = submission_for_show(cur, a["artist_id"], ev.get("venue"),
                                                  ev.get("event_date"))
        else:
            a["submission"] = None
    return acts


# ── staff booking intake ─────────────────────────────────────────────────────
BOOKING_FIELDS = [
    "event_name", "event_date", "venue", "location", "series", "event_type", "paying_band",
    "lead_name", "lead_phone", "load_in", "soundcheck", "event_start",
    "event_end", "curfew", "set_time", "artist_name", "contact_name", "contact_email",
    "email_note", "entered_by",
]
# `slot` and `band_count` came off this list 2026-09-15 — the form stopped
# asking (position is derived from set start, and the bill counts itself).
# The columns stay in the table as history on rows already written.


def insert_booking(cur, data: dict):
    """Insert one staff-entered booking. Blank strings stored as NULL.

    skip_welcome_email is handled outside the BOOKING_FIELDS loop above —
    that loop's "blank -> NULL" rule is for optional text fields; this is a
    NOT NULL boolean (default false), so it needs a real True/False, never
    None. See shows_due_for_initial_advance for what it gates."""
    vals = {k: (data.get(k) or None) for k in BOOKING_FIELDS}
    ed = vals.get("event_date")
    if isinstance(ed, str) and ed.strip():
        try:
            vals["event_date"] = dt.date.fromisoformat(ed.strip()[:10])
        except ValueError:
            vals["event_date"] = None
    vals["skip_welcome_email"] = bool(data.get("skip_welcome_email"))
    vals["band_emails"] = bool(data.get("band_emails"))
    vals["draft_only"] = bool(data.get("draft_only"))
    cols = ", ".join(BOOKING_FIELDS) + ", skip_welcome_email, band_emails, draft_only"
    ph = (", ".join(f"%({k})s" for k in BOOKING_FIELDS)
          + ", %(skip_welcome_email)s, %(band_emails)s, %(draft_only)s")
    # Review 2026-09-14 (H1): one booking row per band/venue/date. A double
    # submit, a refresh that re-POSTs, or a re-entry updates the existing row
    # instead of creating a twin that would make the lifecycle send twice.
    # seeded_at is kept so an already-seeded row isn't appended to the sheet
    # again.
    upd = ", ".join(f"{k} = EXCLUDED.{k}" for k in BOOKING_FIELDS
                    if k not in ("venue", "event_date", "artist_name"))
    clear_sheet_removals(cur, vals.get("venue"), vals.get("event_date"), vals.get("artist_name"))
    cur.execute(
        f"""INSERT INTO bookings ({cols}) VALUES ({ph})
            ON CONFLICT (venue, event_date, (lower(btrim(regexp_replace(artist_name, '\\s+', ' ', 'g')))))
            DO UPDATE SET {upd}, skip_welcome_email = EXCLUDED.skip_welcome_email,
                          band_emails = EXCLUDED.band_emails,
                          draft_only = EXCLUDED.draft_only
            RETURNING id""", vals)
    return cur.fetchone()["id"]


# What a booking contributes to advance-list.xlsx — everything the sheet has a
# column for that the booking form owns. Band-detail columns (Monitors, Stage
# Type, ...) are deliberately absent: those are the band's answers or Brian's
# own sheet overrides, and the booking has no opinion on them.
SHEET_OWNED_FIELDS = [
    "event_name", "event_date", "venue", "location", "series", "event_type",
    "paying_band", "lead_name", "lead_phone", "load_in", "soundcheck",
    "event_start", "event_end", "curfew", "set_time", "artist_name",
    "contact_email", "email_note",
]

# The band's OWN answers, addable straight from the booking form (Brian,
# 2026-09-16: "I should be able to enter all of the same information as if...
# from the band's side"). Same field names /submit expects from a real band
# submission, so a value typed here goes through record_submission exactly
# the way the band's own form would — same table, same daysheet/doc path, no
# second system to keep in sync. contact_name/contact_email are the booking's
# own fields already; contact_phone is band-only, added here.
BOOKING_BAND_ANSWER_FIELDS = [
    "contact_phone", "performers", "crew_count", "stage_type", "monitors", "uses_iems",
    "iem_count", "own_iems", "split_snake", "own_engineer", "merch",
    "band_tent", "vehicle_count", "large_vehicle_count", "trailer", "backline",
    "scenic", "lighting", "stage_plot_desc", "additional",
    "stage_escort_name", "stage_escort_cell",
    # the three acknowledgment checkboxes a real submission carries — optional
    # here (this is staff transcription, not the band affirming for
    # themselves), but worth recording if the band confirmed some other way
    # (phone, email) so a completed advance doesn't read as unacknowledged.
    "ack_loadin", "ack_95db", "ack_reqs",
]

# Fields a band actually sees/relies on, vs. staff-facing bookkeeping
# (contact info, entered_by, email_note, lead/paying-band, series, event
# name, band_count). Changing one of these on an already-logged booking is
# what queues the "info changed" notice — see update_booking below and
# tools/booking_update.py (Brian, 2026-09-14).
BAND_FACING_FIELDS = [
    "event_date", "venue", "location", "artist_name", "set_time",
    "load_in", "soundcheck", "event_start", "event_end", "curfew",
]


def get_booking(cur, booking_id):
    cur.execute("SELECT * FROM bookings WHERE id=%s", (booking_id,))
    return cur.fetchone()


def update_booking(cur, booking_id, data: dict):
    """Update an existing staff-entered booking in place (the edit-booking
    form, distinct from show_edit's band-submission editor). Any BAND_FACING_
    FIELDS change is recorded as a booking_edits row — merged into any
    still-unsent pending row for this booking, so several edits before the
    next daily lifecycle run collapse into one email instead of several
    (uq_booking_edits_pending). It queues a notice (notify) when the old or
    new date is inside the 21-day window, or the band was already contacted
    (welcomed, responded, or a manual band advance); due_booking_edits only
    sends it once the band has been contacted (2026-09-21 sweep).

    Returns (changes, notify) — the diff dict just recorded (empty if
    nothing band-facing changed) and whether it queued a notice (False when
    changes is empty, the show has passed, or it's an uncontacted band with
    neither date inside the 21-day window)."""
    import json as _json
    before = get_booking(cur, booking_id)
    if not before:
        raise ValueError(f"no booking {booking_id}")
    vals = {k: (data.get(k) or None) for k in BOOKING_FIELDS}
    ed = vals.get("event_date")
    if isinstance(ed, str) and ed.strip():
        try:
            vals["event_date"] = dt.date.fromisoformat(ed.strip()[:10])
        except ValueError:
            vals["event_date"] = None
    vals["skip_welcome_email"] = bool(data.get("skip_welcome_email"))
    vals["band_emails"] = bool(data.get("band_emails"))
    vals["draft_only"] = bool(data.get("draft_only"))
    vals["id"] = booking_id
    sets = ", ".join(f"{k} = %({k})s" for k in BOOKING_FIELDS)
    cur.execute(
        f"""UPDATE bookings SET {sets}, skip_welcome_email = %(skip_welcome_email)s,
                                 band_emails = %(band_emails)s,
                                 draft_only = %(draft_only)s
            WHERE id = %(id)s""", vals)
    if vals.get("artist_name") and vals.get("venue") and vals.get("event_date"):
        carry_show_with_booking(cur, before, vals)

    def _as_text(v):
        return v.isoformat() if isinstance(v, dt.date) else (v or "")

    # audit 2026-09-16 #20: "8:00pm" -> "8:00p" (or any other spelling of
    # the same time) isn't a real change — compare these five as clock
    # minutes, not text, so re-typing a time in a different format doesn't
    # queue a pointless "info changed" email to the band.
    _CLOCK_FIELDS = {"load_in", "soundcheck", "event_start", "event_end", "curfew"}

    changes = {}
    for f in BAND_FACING_FIELDS:
        old_s, new_s = _as_text(before.get(f)), _as_text(vals.get(f))
        if f in _CLOCK_FIELDS and old_s and new_s:
            old_m, new_m = parse_clock(old_s), parse_clock(new_s)
            if old_m is not None and old_m == new_m:
                continue
        if old_s != new_s:
            changes[f] = {"old": old_s, "new": new_s}

    # Anything the SHEET carries for this booking that just changed has to be
    # pushed back into advance-list.xlsx, or the next pipeline run rebuilds the
    # bill from the old row and undoes the edit (2026-09-15). Wider than
    # BAND_FACING_FIELDS: the series or the event name never reaches a band,
    # but it does reach the sheet.
    # 2026-09-21 sweep (FLOW-12): record WHICH fields — the sync writes only those, so
    # a value Brian typed into the sheet survives an unrelated app edit. A dirty row
    # with no list is a pending whole-row write (pre-migration) and stays one.
    sheet_changed = [f for f in SHEET_OWNED_FIELDS if _as_text(before.get(f)) != _as_text(vals.get(f))]
    if sheet_changed:
        cur.execute(
            """UPDATE bookings SET sheet_dirty = true,
                   sheet_dirty_fields = CASE WHEN sheet_dirty AND cardinality(sheet_dirty_fields) = 0
                       THEN sheet_dirty_fields
                       ELSE ARRAY(SELECT DISTINCT unnest(sheet_dirty_fields || %s::text[])) END
               WHERE id = %s AND seeded_at IS NOT NULL""",
            (sheet_changed, booking_id))
    # 2026-09-21 sweep (MAIL-6): notify when the OLD or NEW date is in the
    # 21-day window, or the band was already contacted — a welcomed show moved
    # 10 -> 45 days out still hears about it. due_booking_edits gates the send.
    today = dt.date.today()
    new_d, old_d = vals.get("event_date") or before.get("event_date"), before.get("event_date")

    def _win(d):
        return bool(d) and 0 <= (d - today).days <= welcome_days(vals.get("venue") or before.get("venue"))
    cur_show = (show_for_booking(cur, vals.get("artist_name"), vals.get("venue"), new_d)
                or show_for_booking(cur, before.get("artist_name"), before.get("venue"), old_d))
    contacted = bool(vals.get("skip_welcome_email")) or bool(
        cur_show and (cur_show.get("advance_draft_created_at") or cur_show.get("responded_at")))
    notify = bool(changes) and bool(new_d) and new_d >= today and (_win(new_d) or _win(old_d) or contacted)
    edited_by = data.get("entered_by") or before.get("entered_by")
    if changes:
        cur.execute(
            """SELECT id, changes FROM booking_edits
               WHERE booking_id=%s AND notify AND sent_at IS NULL""", (booking_id,))
        pending = cur.fetchone()
        if pending:
            merged = pending["changes"]
            for f, d in changes.items():
                # keep the earliest "old" so the eventual email reflects the
                # whole span of edits since it was last sent, not just the last one
                merged[f] = {"old": merged[f]["old"], "new": d["new"]} if f in merged else d
            # A field edited back to where it started is not a change (Brian,
            # 2026-09-15: "Set length: 120 -> 120 min" was about to go to a band
            # as news). Dropping it here rather than at send time keeps the
            # stored diff honest too — what's queued is what the band will read.
            # 2026-09-21 sweep (DBB-8): clock fields compare as minutes here too,
            # so 8p -> 9:00pm -> 8:00pm isn't queued as "Start: 8p -> 8:00pm".
            def _no_change(f, d):
                if d["old"] == d["new"]:
                    return True
                if f in _CLOCK_FIELDS and d["old"] and d["new"]:
                    o = parse_clock(d["old"])
                    return o is not None and o == parse_clock(d["new"])
                return False
            merged = {f: d for f, d in merged.items() if not _no_change(f, d)}
            if not merged:
                cur.execute("DELETE FROM booking_edits WHERE id=%s", (pending["id"],))
                return changes, False
            cur.execute(
                """UPDATE booking_edits SET changes=%s::jsonb, edited_by=%s, edited_at=now(),
                                             notify=%s WHERE id=%s""",
                (_json.dumps(merged), edited_by, notify, pending["id"]))
        else:
            cur.execute(
                """INSERT INTO booking_edits (booking_id, changes, edited_by, notify)
                   VALUES (%s, %s::jsonb, %s, %s)""",
                (booking_id, _json.dumps(changes), edited_by, notify))
    return changes, notify


def carry_show_with_booking(cur, before, after):
    """A booking renamed or moved after its show exists takes the show with it
    (root cause A / F8, audit 2026-09-16). Without this only the bookings row
    changed: the next run upserted a second artist + show under the new
    identity with blank stamps and welcomed the band again, while holds.py
    later parked the original as an orphan.

    Rename: the artists row is renamed in place when this show is its only
    one (match_key regenerates, every stamp stays on the show). When the
    artist has other shows, or the new name already belongs to another artist
    row (the match_key collision upsert_artist(known_id=) also guards), this
    show moves to that artist instead — renaming a shared row would detach
    the band's other bookings. Venue/date: the show row moves, and its filed
    doc follows when nothing else is left on the old bill (or is retired
    SUPERSEDED when the new date already has its own doc). If the target
    artist already has a show on the new venue+date (a band submission got
    there first), the two are merged. Returns the surviving show id or None."""
    old_name, old_venue, old_date = before.get("artist_name"), before.get("venue"), before.get("event_date")
    new_name, new_venue = after.get("artist_name"), after.get("venue")
    new_date = to_date(after.get("event_date"))
    renamed = normalize(old_name) != normalize(new_name)
    moved = (old_venue, old_date) != (new_venue, new_date)
    if not (renamed or moved) or not new_date:
        return None
    show = show_for_booking(cur, old_name, old_venue, old_date)
    if not show:
        return None
    old_artist = show["artist_id"]
    target_artist = old_artist
    if renamed:
        cur.execute(f"SELECT id FROM artists WHERE match_key = {_SQL_MATCH_KEY}", (new_name,))
        hit = cur.fetchone()
        if hit:
            target_artist = hit["id"]
        else:
            cur.execute("SELECT count(*) AS n FROM shows WHERE artist_id=%s AND id<>%s",
                        (old_artist, show["id"]))
            if cur.fetchone()["n"] == 0:
                cur.execute("UPDATE artists SET name=%s WHERE id=%s", (new_name.strip(), old_artist))
            else:
                target_artist = upsert_artist(cur, new_name.strip(), email=after.get("contact_email"))
    there = show_for_artist_at(cur, target_artist, new_venue, new_date)
    if there and there["id"] != show["id"]:
        merge_shows(cur, show["id"], there["id"], tombstone=False)
        if moved:   # 2026-09-21 sweep (IDENT-13): merge left the old doc registered
            _retire_left_behind_doc(cur, old_venue, to_date(old_date), new_venue, new_date, old_name)
        return there["id"]
    cur.execute("UPDATE shows SET artist_id=%s, venue=%s, show_date=%s WHERE id=%s",
                (target_artist, new_venue, new_date, show["id"]))
    if target_artist != old_artist:
        cur.execute("UPDATE submissions SET artist_id=%s WHERE show_id=%s", (target_artist, show["id"]))
        cur.execute("""UPDATE files SET artist_id=%s WHERE submission_id IN
                       (SELECT id FROM submissions WHERE show_id=%s)""", (target_artist, show["id"]))
        # 2026-09-21 sweep (DBB-7): or the artist DELETE below cascades the moved show's recap away
        cur.execute("UPDATE advance_recaps SET artist_id=%s WHERE show_id=%s", (target_artist, show["id"]))
        cur.execute("""DELETE FROM artists a WHERE a.id=%s
                       AND NOT EXISTS (SELECT 1 FROM shows WHERE artist_id=a.id)
                       AND NOT EXISTS (SELECT 1 FROM submissions WHERE artist_id=a.id)""",
                    (old_artist,))
    if moved:
        # 2026-09-21 sweep (IDENT-13): retire=True — a doc left behind at the old date is retired
        _retire_left_behind_doc(cur, old_venue, to_date(old_date), new_venue, new_date, old_name)
    if target_artist != old_artist:
        # 2026-09-21 sweep: after the re-register, so a doc that followed the show is re-keyed too
        remap_doc_artist(cur, new_venue, new_date, old_artist, target_artist)
    return show["id"]


_BOOKING_EDIT_SHOW_JOIN = r"""
           LEFT JOIN artists a ON a.match_key = lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g')))
           LEFT JOIN shows s ON s.artist_id = a.id AND s.venue = b.venue AND s.show_date = b.event_date"""
_BOOKING_EDIT_SILENT_SQL = (
    "(lower(btrim(COALESCE(b.series,''))) = '3rd party' AND NOT COALESCE(b.band_emails, false))")


def due_booking_edits(cur):
    """Pending booking-edit notifications ready for the next daily lifecycle
    run — the show hasn't passed and the band has already been contacted
    (welcomed, responded, or a manual band advance). 2026-09-21 sweep
    (MAIL-6): gated on contact, not the 21-day window — a notice for a band
    whose welcome hasn't gone out (or sits as a held draft) stays pending;
    the welcome resolves it as carried (resolve_booking_edits_carried), or
    "I sent it" releases it. Excludes a show that's since gone
    cancelled/held, or is 3rd-party without band_emails opted in (audit
    2026-09-16 #13) — see skip_stale_booking_edits, which resolves those
    instead of leaving them pending forever."""
    cur.execute(
        """SELECT e.id AS edit_id, e.booking_id, e.changes, e.edited_at,
                  b.artist_name, b.event_date, b.venue, b.contact_email, b.series,
                  a.last_email AS artist_email
           FROM booking_edits e JOIN bookings b ON b.id = e.booking_id"""
        + _BOOKING_EDIT_SHOW_JOIN + """
           WHERE e.notify AND e.sent_at IS NULL
             AND b.event_date IS NOT NULL
             AND b.event_date >= CURRENT_DATE
             AND (COALESCE(b.skip_welcome_email, false)
                  OR s.advance_draft_created_at IS NOT NULL OR s.responded_at IS NOT NULL)
             AND (s.id IS NULL OR (s.cancelled_at IS NULL AND s.held_at IS NULL))
             AND NOT """ + _BOOKING_EDIT_SILENT_SQL + """
           ORDER BY e.id""")
    return cur.fetchall()


def skip_stale_booking_edits(cur):
    """A pending booking-edit notice whose show has since gone cancelled,
    held, or turned 3rd-party-silent is done, not failed and not stuck
    retrying forever — resolve it the same way a stale followup tier gets
    pre-skipped (audit 2026-09-16 #13). 2026-09-21 sweep: a past show too, so
    a notice for a never-contacted band can't sit pending forever and absorb
    later edits through uq_booking_edits_pending."""
    cur.execute(
        """SELECT e.id AS edit_id, s.cancelled_at, s.held_at,
                  COALESCE(b.event_date < CURRENT_DATE, false) AS passed,
                  """ + _BOOKING_EDIT_SILENT_SQL + """ AS silent
           FROM booking_edits e JOIN bookings b ON b.id = e.booking_id"""
        + _BOOKING_EDIT_SHOW_JOIN + """
           WHERE e.notify AND e.sent_at IS NULL
             AND (s.cancelled_at IS NOT NULL OR s.held_at IS NOT NULL
                  OR b.event_date < CURRENT_DATE OR """
        + _BOOKING_EDIT_SILENT_SQL + ")")
    for r in cur.fetchall():
        reason = ("skipped: cancelled" if r["cancelled_at"] else
                  "skipped: held" if r["held_at"] else
                  "skipped: show passed" if r["passed"] else
                  "skipped: 3rd-party silent")
        cur.execute("UPDATE booking_edits SET sent_at=now(), error=%s WHERE id=%s",
                    (reason, r["edit_id"]))


def mark_booking_edit_sent(cur, edit_id, ok, err=None, unknown=False):
    # 2026-09-21 sweep: unknown = the send timed out (mailer.outcome_unknown) —
    # resolve it with the error kept, so the next run never re-sends a maybe-delivered notice.
    if unknown:
        cur.execute("UPDATE booking_edits SET sent_at=now(), error=%s WHERE id=%s", (err, edit_id))
    elif ok:
        cur.execute("UPDATE booking_edits SET sent_at=now(), error=NULL WHERE id=%s", (edit_id,))
    else:
        cur.execute("UPDATE booking_edits SET error=%s WHERE id=%s", (err, edit_id))


def resolve_booking_edits_carried(cur, booking_id, asof, reason):
    """2026-09-21 sweep (MAIL-6): the welcome (or held draft) just built from
    the booking's current values carries every edit made up to `asof` — resolve
    those pending notices instead of sending "X -> Y" for an X the band never saw."""
    if booking_id is None:
        return
    cur.execute(
        """UPDATE booking_edits SET sent_at=now(), error=%s
           WHERE booking_id=%s AND notify AND sent_at IS NULL AND edited_at <= %s""",
        (reason, booking_id, asof))


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


def future_bookings(cur):
    """Every booking for a show that hasn't happened yet, seeded or not —
    used to reconcile against the sheet (audit 2026-09-16 #19): a seeded
    booking whose sheet row later vanishes (a hand edit, a bad merge) is
    invisible to unseeded_bookings (seeded_at is already set), so it just
    falls off the sheet for good and holds.py orphans it — and Restore
    doesn't put it back either. run_now.one_pass re-appends anything whose
    ident isn't found in a fresh sheet read, regardless of seeded_at.
    2026-09-21 sweep (IDENT-9): a cancelled show's row is never re-added (if
    someone deleted it, that was on purpose; Undo cancel brings it back), nor a
    dirty one — step 1b owns it, and re-adding it under its new ident duplicates it."""
    cur.execute("""SELECT b.* FROM bookings b""" + _BOOKING_EDIT_SHOW_JOIN + """
                   WHERE b.event_date IS NOT NULL AND b.event_date >= CURRENT_DATE
                     AND NOT b.sheet_dirty
                     AND (s.id IS NULL OR s.cancelled_at IS NULL)
                   ORDER BY b.id""")
    return cur.fetchall()


def edited_bookings(cur):
    """Bookings already in the sheet whose details have been edited since —
    each with `_old_ident`, the (artist, venue, date) the sheet row was written
    under, so a renamed band or a moved date can still be found there instead of
    leaving an orphan row behind.

    audit 2026-09-16 (db P2): this used to read only the NEWEST booking_edits
    row, so a rename followed by a load-in edit before the next sync lost the
    old name and the sheet row couldn't be found. Now every edit since the row
    last matched the sheet (`synced_at`, else `seeded_at`) counts, earliest
    `old` per field. 2026-09-21 sweep (IDENT-3): `sheet_ident`, when stamped,
    replaces that reconstruction — it's only the fallback for older rows."""
    # 2026-09-21 sweep (PRIOR-7): _cancelled — step 1b now re-appends a dirty booking
    # whose row is gone (1c skips dirty ones), except for a cancelled show.
    cur.execute("""SELECT b.*, COALESCE(e.all_changes, '[]'::jsonb) AS _changes,
                          (s.cancelled_at IS NOT NULL) AS _cancelled FROM bookings b"""
                + _BOOKING_EDIT_SHOW_JOIN + """
                   LEFT JOIN LATERAL (
                       SELECT jsonb_agg(changes ORDER BY id) AS all_changes FROM booking_edits
                       WHERE booking_id = b.id
                         AND edited_at > COALESCE(b.synced_at, b.seeded_at, '-infinity'::timestamptz)
                   ) e ON true
                   WHERE b.sheet_dirty AND b.seeded_at IS NOT NULL
                   ORDER BY b.id""")
    rows = cur.fetchall()
    for r in rows:
        # 2026-09-21 sweep (IDENT-3): the ident the row was last WRITTEN under wins
        # — rebuilding it from edit history lost the row after a 2nd rename/revert.
        si = r.pop("sheet_ident", None)
        changes = r.pop("_changes", None) or []
        if si:
            r["_old_ident"] = {f: si.get(f) or _sheet_txt(r.get(f))
                               for f in ("artist_name", "venue", "event_date")}
            continue
        earliest = {}
        for ch in changes:
            for f in ("artist_name", "venue", "event_date"):
                if f in (ch or {}) and f not in earliest and (ch[f] or {}).get("old"):
                    earliest[f] = ch[f]["old"]
        date = r.get("event_date")
        r["_old_ident"] = {
            "artist_name": earliest.get("artist_name") or r.get("artist_name"),
            "venue": earliest.get("venue") or r.get("venue"),
            "event_date": earliest.get("event_date") or (date.isoformat() if date else ""),
        }
    return rows


def _sheet_txt(v):
    return v.isoformat() if isinstance(v, dt.date) else ("" if v is None else str(v))


def _sheet_ident_of(row):
    return {"artist_name": row.get("artist_name") or "", "venue": row.get("venue") or "",
            "event_date": _sheet_txt(row.get("event_date"))[:10]}


_SHEET_IDENT_SQL = ("jsonb_build_object('artist_name', artist_name, 'venue', venue, "
                    "'event_date', to_char(event_date, 'YYYY-MM-DD'))")


def _stamp_from_snapshot(cur, ids, snapshot, stamp_col, dirty_expr, keep_first=False,
                         reset_fields=False):
    """2026-09-21 sweep (IDENT-3): stamp sheet_ident from the rows the run actually
    WROTE (its JSON snapshot); an edit that landed mid-run stays sheet_dirty.
    Returns the ids that had no snapshot row. keep_first: never move a set stamp.
    reset_fields (FLOW-12): sheet_dirty_fields = just the fields edited mid-run."""
    import json
    stamp = f"COALESCE({stamp_col}, now())" if keep_first else "now()"
    rest = []
    for i in ids:
        snap = (snapshot or {}).get(int(i))
        if snap is None:
            rest.append(i)
            continue
        cur.execute("SELECT * FROM bookings WHERE id=%s FOR UPDATE", (i,))
        now_row = cur.fetchone()
        if not now_row:
            continue
        changed_fields = [f for f in SHEET_OWNED_FIELDS
                          if _sheet_txt(now_row.get(f)) != _sheet_txt(snap.get(f))]
        changed = bool(changed_fields)
        cur.execute(f"UPDATE bookings SET {stamp_col} = {stamp}, sheet_ident = %s::jsonb, "
                    f"sheet_dirty = {dirty_expr} WHERE id = %s",
                    (json.dumps(_sheet_ident_of(snap)), changed, i))
        if reset_fields:
            cur.execute("UPDATE bookings SET sheet_dirty_fields = %s::text[] WHERE id = %s",
                        (changed_fields, i))
    return rest


def mark_bookings_synced(cur, ids, snapshot=None):
    """Their sheet row now matches the booking. `snapshot` ({id: row} as written
    to the sheet) keeps a mid-run edit dirty and records sheet_ident."""
    if not ids:
        return
    rest = _stamp_from_snapshot(cur, ids, snapshot, "synced_at", "%s", reset_fields=True)
    if rest:
        cur.execute(f"UPDATE bookings SET sheet_dirty = false, sheet_dirty_fields = '{{}}', "
                    f"synced_at = now(), "
                    f"sheet_ident = {_SHEET_IDENT_SQL} WHERE id = ANY(%s)", (list(rest),))


def mark_bookings_seeded(cur, ids, snapshot=None):
    if not ids:
        return
    # 2026-09-21 sweep (PRIOR-7): seeded_at = when the row FIRST reached the sheet;
    # run_now 1c re-stamps every future booking each pass and must not move it.
    rest = _stamp_from_snapshot(cur, ids, snapshot, "seeded_at", "(sheet_dirty OR %s)",
                                keep_first=True)
    if rest:
        cur.execute(f"UPDATE bookings SET seeded_at = COALESCE(seeded_at, now()), "
                    f"sheet_ident = {_SHEET_IDENT_SQL} WHERE id = ANY(%s)", (list(rest),))


def adopt_sheet_row(cur, booking_id, old_ident):
    """2026-09-21 sweep (IDENT-2): a booking just created for a sheet-typed show
    (no bookings row before) takes over that show's hand-typed row, found under
    `old_ident` — run_now step 1b rewrites it in place (a rename/move included)
    instead of appending a twin and leaving the old row to re-mint the old show.
    No such row (a submission-only show): 1b appends it (2026-09-21 sweep, PRIOR-7).
    2026-09-21 sweep: identity fields only — the booking-less form never showed the row's
    schedule, so its Set-Start defaults must not overwrite the hand-typed Load-In/Start."""
    d = old_ident.get("event_date")
    d = d.isoformat() if isinstance(d, dt.date) else str(d or "")[:10]
    cur.execute(
        """UPDATE bookings SET seeded_at = COALESCE(seeded_at, now()), sheet_dirty = true,
                  sheet_dirty_fields = ARRAY['artist_name', 'venue', 'event_date']::text[],
                  sheet_ident = jsonb_build_object('artist_name', %s::text, 'venue', %s::text,
                                                   'event_date', %s::text)
           WHERE id = %s""",
        (old_ident.get("artist_name"), old_ident.get("venue"), d, booking_id))


# ── sheet removals (root cause A, audit 2026-09-16) ─────────────────────────
# A purged or merged-away show has to leave advance-list.xlsx too, or the next
# run imports the row again and the show comes back with blank stamps. The
# tombstone is applied by run_now.one_pass before the rebuild reads the sheet;
# until it is, import_sheet.py and draft_emails.py skip that ident.

def removal_ident(name, venue, event_date):
    """(match_key, venue lowercased, YYYY-MM-DD) — the same shape holds._ident
    and append_bookings.py compare sheet rows on."""
    d = event_date.isoformat() if isinstance(event_date, dt.date) else str(event_date or "")[:10]
    return (normalize(name), (venue or "").strip().lower(), d)


def add_sheet_removal(cur, venue, event_date, match_key, artist_name=None, reason="purge",
                      doc_path=None):
    cur.execute(
        """INSERT INTO sheet_removals (venue, event_date, match_key, artist_name, reason, doc_path)
           VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
        (venue, event_date, match_key, artist_name, reason, doc_path))
    return cur.fetchone()["id"]


def pending_sheet_removals(cur):
    cur.execute("SELECT * FROM sheet_removals WHERE applied_at IS NULL ORDER BY id")
    return cur.fetchall()


def pending_removal_idents(cur):
    return {removal_ident(r["match_key"], r["venue"], r["event_date"])
            for r in pending_sheet_removals(cur)}


def mark_sheet_removals_applied(cur, ids):
    """Stamp these applied and return their rows (doc_path/reason for the
    caller that retires the filed doc)."""
    if not ids:
        return []
    cur.execute("""UPDATE sheet_removals SET applied_at = now()
                   WHERE id = ANY(%s) AND applied_at IS NULL RETURNING *""", (list(ids),))
    return cur.fetchall()


def clear_sheet_removals(cur, venue, event_date, artist_name):
    """A band re-booked on the same venue+date after a purge is a real booking:
    a still-pending removal would otherwise delete its fresh sheet row."""
    d = to_date(event_date) if not isinstance(event_date, dt.date) else event_date
    if not (venue and d and artist_name):
        return
    cur.execute("""DELETE FROM sheet_removals WHERE applied_at IS NULL
                   AND venue=%s AND event_date=%s AND match_key=%s""",
                (venue, d, normalize(artist_name)))


def _registry_row_for_event(cur, venue, event_date, event_key, n_events_same_day):
    """Same rule as docmerge.locate: exact key, else the only doc that day when
    that day has only one event."""
    row = get_filed_doc(cur, venue, event_date, event_key)
    if row:
        return row
    rows = filed_docs_for(cur, venue, event_date)
    return rows[0] if len(rows) == 1 and n_events_same_day <= 1 else None


def reregister_docs_for_move(cur, old_venue, old_date, new_venue, new_date, retire=True):
    """A show moved to another venue/date (F8, audit 2026-09-16). When that
    leaves the old venue+date with no show at all, its one filed doc belongs
    to the moved show: re-point the registry row (and its notices) at the new
    venue+date — docmerge's next pass for that event finds it through
    `locate` and renames it into the new month folder, hand edits intact.
    When the new venue+date already has its own doc, the old one is retired
    instead (registry row dropped, path returned for the caller to rename);
    `retire=False` leaves it registered where it was. Returns the retired
    path or None."""
    if not (old_date and new_date) or (old_venue, old_date) == (new_venue, new_date):
        return None
    cur.execute("SELECT count(*) AS n FROM shows WHERE venue=%s AND show_date=%s",
                (old_venue, old_date))
    if cur.fetchone()["n"]:
        return None     # other acts are still on that bill; the doc stays theirs
    rows = filed_docs_for(cur, old_venue, old_date)
    if len(rows) != 1:
        return None
    reg = rows[0]
    if not filed_docs_for(cur, new_venue, new_date):
        cur.execute("UPDATE doc_notices SET venue=%s, event_date=%s "
                    "WHERE venue=%s AND event_date=%s AND event_key=%s",
                    (new_venue, new_date, old_venue, old_date, reg["event_key"]))
        cur.execute("UPDATE filed_docs SET venue=%s, event_date=%s WHERE id=%s",
                    (new_venue, new_date, reg["id"]))
        return None
    if not retire:
        return None
    _drop_registry_row(cur, reg)
    return reg["path"]


def _retire_left_behind_doc(cur, old_venue, old_date, new_venue, new_date, artist_name):
    """2026-09-21 sweep (IDENT-13): a show moved onto a date that already has its own
    doc leaves the old one registered at the old date for a later booking to inherit.
    Retire it: a doc-only sheet_removals row (match_key '' matches no sheet row) so
    run_now step 0 renames it SUPERSEDED. Returns the retired path or None."""
    path = reregister_docs_for_move(cur, old_venue, old_date, new_venue, new_date, retire=True)
    if path:
        add_sheet_removal(cur, old_venue, old_date, "", artist_name,
                          reason="doc_retire", doc_path=path)
    return path


def remap_doc_artist(cur, venue, event_date, old_id, new_id):
    """A show changed artist_id (rename onto another artist row, or a merge).
    2026-09-21 sweep: re-key every filed doc at venue+date so docmerge sees an
    unchanged column map instead of blanking that column back to the template.
    Skipped when the new artist already has its own column (two can't merge)."""
    import json
    if not (venue and event_date) or old_id is None or new_id is None or old_id == new_id:
        return
    old_id, new_id = int(old_id), int(new_id)
    pat = re.compile(r"\|a%d(?=\||$)" % old_id)
    rep = "|a%d" % new_id

    def _i(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    for reg in filed_docs_for(cur, venue, event_date):
        cols = reg.get("columns") or {}
        ids = {_i(v) for v in cols.values()}
        if old_id not in ids or new_id in ids:
            continue
        new_cols = {k: (new_id if _i(v) == old_id else v) for k, v in cols.items()}
        cells = reg.get("cells")
        cells_json = (json.dumps({pat.sub(rep, k): v for k, v in cells.items()})
                      if cells is not None else None)
        cur.execute("UPDATE filed_docs SET columns=%s::jsonb, cells=COALESCE(%s::jsonb, cells) "
                    "WHERE id=%s", (json.dumps(new_cols), cells_json, reg["id"]))
        cur.execute("SELECT id, cell_key FROM doc_notices WHERE venue=%s AND event_date=%s "
                    "AND event_key=%s AND cell_key IS NOT NULL",
                    (reg["venue"], reg["event_date"], reg["event_key"]))
        for n in cur.fetchall():
            nk = pat.sub(rep, n["cell_key"])
            if nk != n["cell_key"]:
                cur.execute("UPDATE doc_notices SET cell_key=%s WHERE id=%s", (nk, n["id"]))


def _drop_registry_row(cur, reg):
    cur.execute("DELETE FROM doc_notices WHERE venue=%s AND event_date=%s AND event_key=%s",
                (reg["venue"], reg["event_date"], reg["event_key"]))
    cur.execute("DELETE FROM filed_docs WHERE id=%s", (reg["id"],))


def rekey_filed_doc(cur, reg, new_key):
    """2026-09-21 sweep (IDENT-11): the event behind a filed doc was renamed, so
    its registry row and its notices move together — or Keep doc and Use new
    lose the doc. An old-key notice whose twin already exists under the new key
    is dropped first (the notice UNIQUE tuple)."""
    old, v, d = reg["event_key"], reg["venue"], reg["event_date"]
    if old == new_key:
        return
    cur.execute("""DELETE FROM doc_notices o
                   WHERE o.venue=%s AND o.event_date=%s AND o.event_key=%s
                     AND EXISTS (SELECT 1 FROM doc_notices n
                                 WHERE n.venue=o.venue AND n.event_date=o.event_date
                                   AND n.event_key=%s AND n.kind=o.kind
                                   AND n.field=o.field AND n.new_value=o.new_value)""",
                (v, d, old, new_key))
    cur.execute("UPDATE doc_notices SET event_key=%s WHERE venue=%s AND event_date=%s AND event_key=%s",
                (new_key, v, d, old))
    cur.execute("UPDATE filed_docs SET event_key=%s WHERE id=%s", (new_key, reg["id"]))


def get_or_create_short_link(cur, token, key=None, show_id=None):
    """Deterministic short code for a signed /f/<token> prefill link (same token
    -> same code, so re-drafting a show doesn't pile up rows). /s/<code> 302s to
    the real link — see app.py.
    2026-09-21 sweep (MAIL-1): `key` (optional) replaces the token as the code's
    hash input — timed tokens differ per call; the first token for a key wins.
    2026-09-24 research #11: `show_id` (optional) ties the code to its advance so
    the dashboard and digest can report the open. Callers that don't know it at
    mint time leave it out — open_short_link backfills it from the token on the
    first hit, the only moment the link matters."""
    import base64
    import hashlib
    digest = hashlib.sha256((key or token).encode()).digest()
    code = base64.urlsafe_b64encode(digest)[:8].decode()
    cur.execute(
        "INSERT INTO short_links (code, token, show_id) VALUES (%s, %s, %s) "
        "ON CONFLICT (code) DO NOTHING", (code, token, show_id),
    )
    if show_id:
        cur.execute("UPDATE short_links SET show_id=%s WHERE code=%s AND show_id IS NULL",
                    (show_id, code))
    return code


SUBMIT_RATE_PER_IP = 5
SUBMIT_RATE_SITEWIDE = 60
SUBMIT_RATE_WINDOW_MIN = 60


def submit_rate_limited(cur, ip):
    """True if this IP (or the site overall) has already hit the /submit
    rate limit in the last hour (audit 2026-09-16 security #7) — every bot
    POST to the bare public form does real work (artist+show+submission,
    notify email, FSQ parking queue, a regen_show.py spawn), not a cheap
    no-op, so this isn't just noise prevention."""
    cur.execute(
        """SELECT count(*) AS n FROM submit_attempts
           WHERE ip=%s AND attempted_at > now() - (%s || ' minutes')::interval""",
        (ip, SUBMIT_RATE_WINDOW_MIN))
    if cur.fetchone()["n"] >= SUBMIT_RATE_PER_IP:
        return True
    cur.execute(
        """SELECT count(*) AS n FROM submit_attempts
           WHERE attempted_at > now() - (%s || ' minutes')::interval""",
        (SUBMIT_RATE_WINDOW_MIN,))
    return cur.fetchone()["n"] >= SUBMIT_RATE_SITEWIDE


def record_submit_attempt(cur, ip):
    cur.execute("INSERT INTO submit_attempts (ip) VALUES (%s)", (ip,))


def prune_short_links_and_gate_attempts(cur):
    """Nothing else ever prunes either table (audit 2026-09-16 security
    #9) — short_links grows one row per artist ever drafted, forever;
    gate_attempts/gate_lockouts log every passcode attempt, forever. A
    short_links row past a year is already useless on its own (the signed
    token it points at now carries its own 180-day expiry — see
    PREFILL_TOKEN_MAX_AGE in app.py), so this is storage hygiene, not a
    security boundary by itself."""
    cur.execute("DELETE FROM short_links WHERE created_at < now() - interval '1 year'")
    cur.execute("DELETE FROM gate_attempts WHERE attempted_at < now() - interval '90 days'")
    cur.execute("DELETE FROM gate_lockouts WHERE locked_at < now() - interval '90 days'")
    cur.execute("DELETE FROM submit_attempts WHERE attempted_at < now() - interval '7 days'")


def resolve_short_link(cur, code):
    cur.execute("SELECT token FROM short_links WHERE code = %s", (code,))
    row = cur.fetchone()
    return row["token"] if row else None


def open_short_link(cur, code):
    """Resolve an emailed /s/<code> AND record the open in one statement
    (2026-09-24 research #11) — first hit sets first_opened_at, every hit bumps
    open_count. Deliberately the same UPDATE ... RETURNING that does the lookup,
    so tracking costs the redirect no extra round trip and no second
    transaction; app.py falls back to resolve_short_link if this raises, because
    a stamp that fails must never cost the band their link. Returns the row
    (token, show_id, first_opened_at, open_count) or None for an unknown code.
    Nothing about the visitor is recorded — no IP, no user agent, no per-hit
    rows; open_count is the whole history."""
    cur.execute(
        """UPDATE short_links
              SET open_count = open_count + 1,
                  first_opened_at = COALESCE(first_opened_at, now())
            WHERE code = %s
        RETURNING token, show_id, first_opened_at, open_count""",
        (code,),
    )
    return cur.fetchone()


def attach_short_link_show(cur, code, show_id):
    """Point an already-minted code at its show (2026-09-24 research #11). The
    welcome link is minted by tools/draft_emails.py, which doesn't pass a
    show_id; app.py's /s/ route reads it out of the signed token and backfills
    it here on the first open. Only ever fills a NULL — a code is never
    re-pointed at a different show."""
    if not show_id:
        return
    cur.execute("UPDATE short_links SET show_id=%s WHERE code=%s AND show_id IS NULL",
                (show_id, code))


# ── filed advance docs registry (2026-09-13 audit #1/#2) ─────────────────────

def get_filed_doc(cur, venue, event_date, event_key):
    cur.execute("SELECT * FROM filed_docs WHERE venue=%s AND event_date=%s AND event_key=%s",
                (venue, event_date, event_key))
    return cur.fetchone()


def filed_docs_for(cur, venue, event_date):
    cur.execute("SELECT * FROM filed_docs WHERE venue=%s AND event_date=%s "
                "ORDER BY written_at DESC, id DESC", (venue, event_date))
    return cur.fetchall()


def upsert_filed_doc(cur, venue, event_date, event_key, path, sha256, seeded=False,
                     reg_id=None, keep_written_at=False, cells=None, columns=None):
    """`cells` (review 2026-09-14, H2): the per-cell provenance map — what
    the pipeline last wrote, keyed by section|a<artist_id>[|paragraph].
    `columns` (root cause B, 2026-09-16): {column: artist_id} the doc was
    written with. None leaves either stored map alone."""
    import json
    cells_json = json.dumps(cells) if cells is not None else None
    cols_json = json.dumps({str(k): v for k, v in columns.items()}) if columns is not None else None
    if reg_id:
        cur.execute(
            """UPDATE filed_docs SET event_key=%s, path=%s, sha256=%s,
                   written_at = CASE WHEN %s THEN written_at ELSE now() END,
                   cells = COALESCE(%s::jsonb, cells),
                   columns = COALESCE(%s::jsonb, columns)
               WHERE id=%s""",
            (event_key, path, sha256, keep_written_at, cells_json, cols_json, reg_id))
        return reg_id
    cur.execute(
        """INSERT INTO filed_docs (venue, event_date, event_key, path, sha256, seeded, cells, columns)
           VALUES (%s,%s,%s,%s,%s,%s,COALESCE(%s::jsonb, '{}'::jsonb),COALESCE(%s::jsonb, '{}'::jsonb))
           ON CONFLICT (venue, event_date, event_key) DO UPDATE SET
               path=EXCLUDED.path, sha256=EXCLUDED.sha256, written_at=now(),
               cells = COALESCE(%s::jsonb, filed_docs.cells),
               columns = COALESCE(%s::jsonb, filed_docs.columns)
           RETURNING id""",
        (venue, event_date, event_key, path, sha256, seeded, cells_json, cols_json,
         cells_json, cols_json))
    return cur.fetchone()["id"]


def insert_doc_notice(cur, venue, event_date, event_key, kind, field, new_value,
                      doc_value=None, detail=None, cell_key=None):
    """Returns the new id, or None if this exact notice was already recorded
    (open or already decided — a value Brian kept is not asked about again).
    A new value for a cell supersedes that cell's older open decision
    (2026-09-14 doc review)."""
    cur.execute(
        """INSERT INTO doc_notices (venue, event_date, event_key, kind, field, new_value,
                                    doc_value, detail, cell_key)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (venue, event_date, event_key, kind, field, new_value) DO NOTHING
           RETURNING id""",
        (venue or "", event_date, event_key or "", kind, field or "", new_value or "",
         doc_value, detail, cell_key))
    row = cur.fetchone()
    if row and cell_key:
        cur.execute(
            """UPDATE doc_notices SET resolved_at=now(), resolution='superseded'
               WHERE venue=%s AND event_date IS NOT DISTINCT FROM %s AND event_key=%s
                 AND lower(cell_key)=lower(%s) AND id<>%s AND resolved_at IS NULL""",
            (venue or "", event_date, event_key or "", cell_key, row["id"]))
    return row["id"] if row else None


def open_doc_notices(cur, venue, event_date, event_key=None):
    """Undecided doc changes for a show (event_key None = every event that
    venue+date)."""
    # 'artist_name' joins 'diff' here (2026-09-19): it is a real decision for
    # Brian — which spelling of the band is right — just one that resolves by
    # renaming everywhere instead of by writing a single cell.
    sql = ("SELECT * FROM doc_notices WHERE venue=%s AND event_date=%s "
           "AND kind IN ('diff','artist_name') AND resolved_at IS NULL")
    params = [venue or "", event_date]
    if event_key is not None:
        sql += " AND event_key=%s"
        params.append(event_key)
    cur.execute(sql + " ORDER BY id", params)
    return cur.fetchall()


def get_doc_notice(cur, notice_id):
    cur.execute("SELECT * FROM doc_notices WHERE id=%s", (notice_id,))
    return cur.fetchone()


def resolve_doc_notice(cur, notice_id, resolution):
    cur.execute("""UPDATE doc_notices SET resolved_at=now(), resolution=%s, apply_error=NULL
                   WHERE id=%s AND resolved_at IS NULL
                   RETURNING venue, event_date, event_key, kind""", (resolution, notice_id))
    row = cur.fetchone()
    if row and row["kind"] in ("diff", "artist_name"):
        # F11 (audit 2026-09-16): the last open decision on a doc closes its
        # review — docmerge's resubmission check counts from here, not from the
        # last pipeline write, or review mode never switches off again
        cur.execute(
            """UPDATE filed_docs f SET reviewed_at = now()
               WHERE f.venue=%s AND f.event_date=%s AND f.event_key=%s
                 AND NOT EXISTS (SELECT 1 FROM doc_notices n
                                 WHERE n.venue=f.venue AND n.event_date=f.event_date
                                   AND n.event_key=f.event_key
                                   AND n.kind IN ('diff','artist_name')
                                   AND n.resolved_at IS NULL)""",
            (row["venue"], row["event_date"], row["event_key"]))


def keep_doc_value(cur, notice):
    """Brian chose "Keep doc": the decision is closed and the pipeline gives
    up ownership of that cell, so no later pass writes over what the doc says
    (it's treated as hand-typed from here on)."""
    # 2026-09-21 sweep (DOC-3): lock the registry row BEFORE resolving — same order
    # as docmerge's final write (filed_docs, then doc_notices), so a merge running
    # right now either sees this 'kept' or has its cells re-read here after it commits.
    cur.execute("""SELECT id, cells, columns FROM filed_docs WHERE venue=%s AND event_date=%s AND event_key=%s
                   FOR UPDATE""",
                (notice["venue"], notice["event_date"], notice["event_key"]))
    reg = cur.fetchone()
    resolve_doc_notice(cur, notice["id"], "kept")
    key = notice.get("cell_key")
    if not key or key.startswith("plot:") or not reg:
        return
    import json
    cells = _apply_keep(reg["cells"], key, notice.get("doc_value"), reg.get("columns"))
    cur.execute("UPDATE filed_docs SET cells=%s::jsonb WHERE id=%s", (json.dumps(cells), reg["id"]))


def _kept_drop_keys(key, columns):
    """The provenance keys a "Keep doc" on `key` gives up (lowercased)."""
    drop = {key.lower()}
    # a notice recorded under a pre-2026-09-16 column key gives up the
    # artist-keyed cell too — ownership moved to `Section|a<id>` since
    cols = {str(k): v for k, v in (columns or {}).items()}
    m = re.match(r"^(.*)\|col(\d)(\|\d+)?$", key)
    if m and cols.get(m.group(2)):
        drop.add(f"{m.group(1)}|a{cols[m.group(2)]}{m.group(3) or ''}".lower())
    return drop


def _apply_keep(cells, key, doc_value, columns):
    """`cells` with the pipeline's ownership of `key` given up (a new dict)."""
    drop = _kept_drop_keys(key, columns)
    out = {k: v for k, v in (cells or {}).items() if k.lower() not in drop}
    if doc_value == "(cleared by hand)":
        # docmerge F10: keeping a hand-cleared cell keeps it EMPTY — ownership
        # stays recorded (as a marker, never the template text) so the next
        # pass still reads it as cleared on purpose instead of refilling it
        out[key] = "\u2205 kept blank"
    return out


def reapply_kept_decisions(cur, notice_ids, cells, columns):
    """2026-09-21 sweep (DOC-3): docmerge's final write re-applies any "Keep doc"
    Brian clicked on these notices while its pass was running. Otherwise the
    pass re-owns the cell and a later pass writes the value he rejected."""
    if not notice_ids:
        return cells
    cur.execute("SELECT cell_key, doc_value FROM doc_notices WHERE id = ANY(%s) AND resolution='kept'",
                (list(notice_ids),))
    for n in cur.fetchall():
        key = n.get("cell_key")
        if key and not key.startswith("plot:"):
            cells = _apply_keep(cells, key, n.get("doc_value"), columns)
    return cells


def resubmitted_since(cur, venue, event_date, artist_ids, since):
    """True when one of these acts' shows got a submission after the doc's
    last pipeline write that is a SECOND submission for that show, or a
    staff edit — the case whose changes wait for Brian (2026-09-14)."""
    if not artist_ids or not since:
        return False
    cur.execute(
        """SELECT 1 FROM shows s
           JOIN submissions x ON x.show_id = s.id
           WHERE s.venue=%s AND s.show_date=%s AND s.artist_id = ANY(%s)
             AND x.submitted_at > %s
             AND (x.source = 'staff'
                  OR EXISTS (SELECT 1 FROM submissions p WHERE p.show_id = s.id
                             AND p.submitted_at < x.submitted_at))
           LIMIT 1""",
        (venue, event_date, list(artist_ids), since))
    return cur.fetchone() is not None


def stamp_doc_check(cur, submission_id, result):
    cur.execute("UPDATE submissions SET doc_checked_at=now(), doc_check=%s WHERE id=%s",
                ((result or "")[:500], submission_id))


def unnotified_doc_notices(cur):
    cur.execute("SELECT * FROM doc_notices WHERE notified_at IS NULL "
                "AND (event_date IS NULL OR event_date >= CURRENT_DATE) ORDER BY event_date, id")
    return cur.fetchall()


def mark_doc_notices_notified(cur, ids):
    if ids:
        cur.execute("UPDATE doc_notices SET notified_at=now() WHERE id = ANY(%s)", (list(ids),))


# ── send failures (audit #3) ─────────────────────────────────────────────────

def record_send_failure(cur, show_id, kind, error):
    """One row per show/kind/day. Returns True if this is new today."""
    cur.execute(
        """INSERT INTO send_failures (show_id, kind, error) VALUES (%s,%s,%s)
           ON CONFLICT (show_id, kind, day) DO UPDATE SET error=EXCLUDED.error
           RETURNING (xmax = 0) AS inserted""",
        (show_id, kind, (error or "")[:1000]))
    return cur.fetchone()["inserted"]


def unnotified_send_failures(cur):
    """Failures to email Brian about now. Review 2026-09-14 (M6): the same
    show / kind / error that was already emailed in the last 7 days is
    suppressed (marked notified + suppressed, no email) so a standing data
    gap nags once a week, not every morning. A new error text for the same
    show is still reported right away."""
    cur.execute(
        """UPDATE send_failures f SET notified_at = now(), suppressed = true
           WHERE f.notified_at IS NULL
             AND EXISTS (SELECT 1 FROM send_failures p
                         WHERE p.show_id = f.show_id AND p.kind = f.kind
                           AND p.error IS NOT DISTINCT FROM f.error
                           AND p.notified_at IS NOT NULL AND NOT p.suppressed
                           AND p.notified_at > now() - interval '7 days')""")
    cur.execute(
        """SELECT f.*, a.name AS artist_name, s.venue, s.show_date
           FROM send_failures f JOIN shows s ON s.id = f.show_id
           JOIN artists a ON a.id = s.artist_id
           WHERE f.notified_at IS NULL ORDER BY s.show_date, f.id""")
    return cur.fetchall()


def mark_send_failures_notified(cur, ids):
    if ids:
        cur.execute("UPDATE send_failures SET notified_at=now() WHERE id = ANY(%s)", (list(ids),))


# ── digest queue + "needs you" feed (review 2026-09-14, E1) ─────────────────

def queue_digest_item(cur, kind, subject, html, link=None):
    """Something Brian should see, folded into the next 7am digest instead
    of its own email (doc notices, submission matches, set-time clashes, the
    3-day unresponded list, thank-you / day-before failures)."""
    cur.execute("INSERT INTO digest_items (kind, subject, html, link) VALUES (%s,%s,%s,%s) RETURNING id",
                (kind, subject, html, link))
    return cur.fetchone()["id"]


def undelivered_digest_items(cur):
    cur.execute("SELECT * FROM digest_items WHERE delivered_at IS NULL ORDER BY id")
    return cur.fetchall()


def mark_digest_items_delivered(cur, ids):
    if ids:
        cur.execute("UPDATE digest_items SET delivered_at = now() WHERE id = ANY(%s)", (list(ids),))


def welcome_open_phrase(sent_at, opened_at):
    """"welcome sent 09/02 · opened 09/03" / "welcome sent 09/02 · never opened"
    (2026-09-24 research #11). A link hit is the earliest sign the mail didn't
    land in spam, so "never opened" is the row to work by hand first. Reads
    "no welcome sent yet" for a manual-entry booking that skipped the welcome."""
    if not sent_at:
        return "no welcome sent yet"
    sent = f"welcome sent {sent_at:%m/%d}"
    return f"{sent} · opened {opened_at:%m/%d}" if opened_at else f"{sent} · never opened"


def artist_note_phrase(notes, rating, limit=70):
    """"last time: plot wrong, 3 reminders · 3/5" (2026-09-24 research #12) —
    the staff note + advance-accuracy pip on a returning band, so the next chase
    starts calibrated. Blank for a band with neither. First line only, clipped:
    these ride inside a one-line Needs-you row, and the full note lives on
    /artist. Staff-only — never goes anywhere a band can see."""
    bits = []
    first = ((notes or "").strip().splitlines() or [""])[0].strip()
    if first:
        bits.append(first if len(first) <= limit else first[:limit - 1].rstrip() + "…")
    if rating:
        bits.append(f"{rating}/5")
    return ("last time: " + " · ".join(bits)) if bits else ""


def needs_attention(cur):
    """Open decisions and problems, live, for the dashboard panel and the
    digest. Each entry: {kind, label, detail, link_path, since}."""
    out = []
    cur.execute("""SELECT m.id, m.typed_name, m.venue, m.show_date, m.status, m.created_at
                   FROM submission_matches m WHERE m.resolved_at IS NULL ORDER BY m.id""")
    for m in cur.fetchall():
        out.append({"kind": "match", "label": "Submission needs a booking",
                    "detail": f"“{m['typed_name']}” — {m['venue']} {m['show_date']:%m/%d} "
                              + ("(auto-attached, confirm or detach)" if m["status"] == "attached_auto" else "(pick the booking)"),
                    "link_path": f"/submission-match/{m['id']}", "since": m["created_at"]})
    cur.execute("""SELECT s.id, a.name, s.venue, s.show_date, s.hold_reason, s.held_at
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.held_at IS NOT NULL AND s.cancelled_at IS NULL ORDER BY s.show_date""")
    for h in cur.fetchall():
        out.append({"kind": "hold", "label": "Show on hold",
                    "detail": f"{h['name']} — {h['venue']} {h['show_date']:%m/%d}: {h['hold_reason']}",
                    "link_path": f"/show/{h['id']}/hold", "since": h["held_at"]})
    # 2026-09-19: grouped by KIND as well, so a band-name clash gets its own
    # line at the top of the dashboard instead of being counted as one more
    # "field" among the ordinary cell diffs — it is a different decision
    # (which spelling is the band) with a different consequence (a rename
    # everywhere), and Brian needs to see which one is waiting on him.
    cur.execute("""SELECT n.venue, n.event_date, n.kind, count(*) AS n,
                          min(n.created_at) AS since,
                          string_agg(n.field, ', ' ORDER BY n.id) AS fields,
                          string_agg(DISTINCT n.doc_value, ' / ') AS doc_values
                   FROM doc_notices n
                   WHERE n.kind IN ('diff','artist_name') AND n.resolved_at IS NULL
                     AND n.event_date >= CURRENT_DATE
                   GROUP BY n.venue, n.event_date, n.kind
                   ORDER BY n.kind DESC, n.event_date, n.venue""")
    from urllib.parse import quote
    for n in cur.fetchall():
        link = f"/doc-review?venue={quote(n['venue'])}&date={n['event_date'].isoformat()}"
        if n["kind"] == "artist_name":
            bands = ", ".join(sorted({f.split("—", 1)[-1].strip()
                                      for f in (n["fields"] or "").split(", ") if f}))
            out.append({"kind": "artist_name",
                        "label": "Band name needs deciding",
                        "detail": f"{n['venue']} {n['event_date']:%m/%d} · the doc and the booking "
                                  f"disagree on the name ({bands or n['n']}) — picking renames "
                                  "the band everywhere",
                        "link_path": link, "since": n["since"]})
            continue
        out.append({"kind": "doc", "label": "Doc changes to decide",
                    "detail": f"{n['venue']} {n['event_date']:%m/%d} · {n['n']} field(s): {n['fields'][:120]}",
                    "link_path": link, "since": n["since"]})
    # Welcomes held as a draft (bookings.draft_only — Brian, 2026-09-15). This
    # panel is the only thing that surfaces them: a held show is deliberately
    # silent, no reminders fire, so without a line here a draft nobody sent
    # would just sit in Outlook until the show arrived.
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date,
                          s.advance_held_draft_at
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.advance_held_draft_at IS NOT NULL
                     AND s.advance_draft_created_at IS NULL
                     AND s.cancelled_at IS NULL AND s.held_at IS NULL
                     AND NOT """ + _HELD_DRAFT_ANSWERED_SQL + """
                     AND s.show_date >= CURRENT_DATE
                   ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "heldraft", "label": "Advance drafted, not sent",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}: "
                              f"waiting in Production@3cdc.org drafts",
                    "link_path": f"/artist/{r['artist_id']}", "since": r["advance_held_draft_at"]})
    # 2026-09-21 sweep (PRIOR-25): the band answered (or the show was cancelled)
    # while its welcome sat in drafts — someone could still send that stale nag.
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date,
                          s.advance_held_draft_at, s.cancelled_at
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.advance_held_draft_at IS NOT NULL
                     AND s.advance_draft_created_at IS NULL
                     AND s.show_date >= CURRENT_DATE
                     AND """ + _HELD_DRAFT_STALE_SQL + """
                   ORDER BY s.show_date""")
    for r in cur.fetchall():
        why = "show cancelled" if r["cancelled_at"] else "band already answered"
        out.append({"kind": "heldraft_stale", "label": "Held welcome is stale",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}: {why} — delete "
                              f"the unsent welcome from Production@3cdc.org drafts",
                    "link_path": f"/artist/{r['artist_id']}", "since": r["advance_held_draft_at"]})
    for r in memo_parking_sheet_due(cur):
        out.append({"kind": "parking_sheet", "label": "Parking sheet not sent",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}: parking is the "
                              "Washington Park garage; the band hasn't been sent the sheet",
                    "link_path": f"/show/{r['id']}/parking-sheet", "since": None})
    cur.execute("""SELECT f.*, a.name, s.venue, s.show_date FROM send_failures f
                   JOIN shows s ON s.id=f.show_id JOIN artists a ON a.id=s.artist_id
                   WHERE f.created_at > now() - interval '3 days' AND s.show_date >= CURRENT_DATE
                   ORDER BY f.id DESC""")
    for f in cur.fetchall():
        # 2026-09-21 sweep: a timed-out send is stamped sent, not retried — say so.
        label = ("Send outcome unknown — check Sent Items, won't retry"
                 if f["kind"].endswith("_unknown") else f"Email not sent ({f['kind']})")
        out.append({"kind": "send", "label": label,
                    "detail": f"{f['name']} — {f['venue']} {f['show_date']:%m/%d}: {f['error']}",
                    "link_path": None, "since": f["created_at"]})
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date FROM shows s
                   JOIN artists a ON a.id=s.artist_id
                   WHERE s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + """ + _welcome_window_sql() + """
                     AND s.cancelled_at IS NULL AND s.held_at IS NULL AND s.responded_at IS NULL
                     AND COALESCE(a.last_email, '') = ''
                     -- 2026-09-21 sweep (PRIOR-16): a 3rd-party show that opted in
                     -- to band emails is listed too; only silent ones stay hidden
                     AND NOT """ + THIRD_PARTY_SILENT_SQL + """ ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "noemail", "label": "No contact email",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}",
                    "link_path": f"/artist/{r['artist_id']}", "since": None})
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date, s.thankyou_error
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.thankyou_error IS NOT NULL AND s.thankyou_sent_at IS NULL
                     -- 2026-09-21 sweep (PRIOR-2): the automatic thank-you runs on past
                     -- shows, so its failures show for the catch-up week; skips never do
                     AND s.show_date >= CURRENT_DATE - 7
                     AND s.thankyou_error NOT LIKE 'skipped:%' ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "thankyou", "label": "Thank-you not sent",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}: {r['thankyou_error']}",
                    "link_path": f"/artist/{r['artist_id']}", "since": None})
    # 2026-09-24 research #4: the 10-days-out row. The first firm chase is the
    # T-10 reminder tier (FIRST_CHASE_TIER) — this reports what happened to it,
    # so a band that is still silent is visible a week before the 3-day row
    # below exists and there is still time to build the packet off a real plot.
    # Listed only once that tier has resolved for the show, so it never nags
    # about a welcome that went out yesterday. The link is the staff answers
    # page, for when a band replies with the details by email instead of filling
    # the form in — no phone number anywhere: everything reaches the band
    # through Production@3cdc.org (Brian, 2026-09-24).
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date,
                          a.last_email AS email, a.notes, a.advance_rating,
                          s.advance_draft_created_at,
                          (SELECT max(sl.first_opened_at) FROM short_links sl
                            WHERE sl.show_id = s.id) AS link_opened_at,
                          (SELECT r.drafted_at FROM advance_reminders r
                            WHERE r.show_id = s.id AND r.days_before = %s AND r.sent) AS nudge_sent_at
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.responded_at IS NULL AND s.cancelled_at IS NULL AND s.held_at IS NULL
                     AND s.show_date BETWEEN CURRENT_DATE + 4 AND CURRENT_DATE + %s
                     AND EXISTS (SELECT 1 FROM advance_reminders r
                                 WHERE r.show_id = s.id AND r.days_before = %s)
                     AND NOT """ + BAND_ANSWERED_SQL + """
                     AND NOT (lower(btrim(COALESCE(s.show_series,''))) = '3rd party' AND COALESCE(a.last_email,'') = '')
                     AND NOT """ + THIRD_PARTY_SILENT_SQL + """
                   ORDER BY s.show_date""",
                (FIRST_CHASE_TIER, FIRST_CHASE_TIER, FIRST_CHASE_TIER))
    for r in cur.fetchall():
        nudge = (f"{FIRST_CHASE_TIER}-day nudge sent {r['nudge_sent_at']:%m/%d}"
                 if r["nudge_sent_at"] else f"{FIRST_CHASE_TIER}-day nudge skipped")
        bits = [f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}",
                r["email"] or "no email on file", nudge,
                welcome_open_phrase(r["advance_draft_created_at"], r["link_opened_at"])]
        note = artist_note_phrase(r["notes"], r["advance_rating"])
        if note:
            bits.append(note)
        out.append({"kind": "chase10", "label": f"No advance, {FIRST_CHASE_TIER} days out",
                    "detail": " · ".join(bits),
                    "link_path": f"/show/{r['id']}/edit",
                    "link_label": "type their answers →", "since": None})
    # 2026-09-24 research #11 + #12: the last-resort row carries the same open
    # state (a welcome never opened is a different problem from one read and
    # ignored) and last time's staff note.
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date,
                          a.notes, a.advance_rating, s.advance_draft_created_at,
                          (SELECT max(sl.first_opened_at) FROM short_links sl
                            WHERE sl.show_id = s.id) AS link_opened_at
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.responded_at IS NULL AND s.cancelled_at IS NULL AND s.held_at IS NULL
                     AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 3
                     AND NOT """ + BAND_ANSWERED_SQL + """
                     AND NOT (lower(btrim(COALESCE(s.show_series,''))) = '3rd party' AND COALESCE(a.last_email,'') = '')
                     AND NOT """ + THIRD_PARTY_SILENT_SQL + """
                   ORDER BY s.show_date""")
    for r in cur.fetchall():
        bits = [f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}",
                welcome_open_phrase(r["advance_draft_created_at"], r["link_opened_at"])]
        note = artist_note_phrase(r["notes"], r["advance_rating"])
        if note:
            bits.append(note)
        out.append({"kind": "unresponded", "label": "No form, show within 3 days",
                    "detail": " · ".join(bits),
                    "link_path": f"/artist/{r['artist_id']}", "since": None})
    return out


# ── job runs (audit #21) ─────────────────────────────────────────────────────

def record_job_run(cur, job, source):
    cur.execute("INSERT INTO job_runs (job, source) VALUES (%s,%s)", (job, source))


def job_ran_since(cur, job, source, since):
    cur.execute("SELECT 1 FROM job_runs WHERE job=%s AND source=%s AND ran_at >= %s LIMIT 1",
                (job, source, since))
    return cur.fetchone() is not None


# ── cancel / hold / merge (audit #4) ─────────────────────────────────────────

def cancel_show(cur, show_id):
    cur.execute("UPDATE shows SET cancelled_at = COALESCE(cancelled_at, now()), held_at = NULL "
                "WHERE id=%s RETURNING id", (show_id,))
    return cur.fetchone() is not None


def uncancel_show(cur, show_id):
    # audit 2026-09-16 #19: hold_dismissed_at is restore_show's flag (a
    # HELD show, released for good) — stamping it here too, on a plain
    # un-cancel, permanently exempted this show from ever being auto-held
    # again for an unrelated reason (its sheet row later vanishing, say),
    # which was never the intent of reversing a cancellation.
    cur.execute("UPDATE shows SET cancelled_at = NULL WHERE id=%s RETURNING id", (show_id,))
    return cur.fetchone() is not None


def queue_fsq_parking(cur, *, artist_id, show_id, band, venue, show_date,
                       contact_name, contact_email, contact_phone,
                       vehicle_count, large_vehicle_count, trailer=None):
    """Hold one Fountain Square band's parking numbers for the next daily
    digest (Brian, 2026-09-15 — step 2: no more per-submission draft,
    everything overnight batches into one email, sent only when non-empty).
    A full snapshot is stored, not just the ids, so a later edit or purge of
    the show can't change what already went out, or silently drop a pending
    item. Returns the new row's id."""
    if show_id:
        # 2026-09-21 sweep (FLOW-10): newest numbers replace an undelivered row, so the
        # digest never lists a band twice; delivered rows stay, so a later change still goes out
        cur.execute("DELETE FROM fsq_parking_queue WHERE show_id=%s AND digested_at IS NULL",
                    (show_id,))
    cur.execute(
        # 2026-09-24 research #(b): trailer rides along in the snapshot — a
        # towed trailer can't use the 6'8" garage, and the counts alone never
        # said so (van + trailer is one vehicle).
        """INSERT INTO fsq_parking_queue
               (artist_id, show_id, band, venue, show_date, contact_name,
                contact_email, contact_phone, vehicle_count, large_vehicle_count,
                trailer)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        (artist_id, show_id, band, venue, show_date, contact_name,
         contact_email, contact_phone, vehicle_count, large_vehicle_count,
         trailer))
    return cur.fetchone()["id"]


def undelivered_fsq_parking(cur):
    """Every queued FSQ parking item not yet folded into a digest, oldest
    first — carries forward untouched across any number of empty days
    (Brian: 'if no new submissions have come in, do not send') until a run
    finally has something to report, so nothing is ever silently dropped."""
    cur.execute("SELECT * FROM fsq_parking_queue WHERE digested_at IS NULL ORDER BY created_at")
    return cur.fetchall()


def mark_fsq_parking_delivered(cur, ids):
    if ids:
        cur.execute("UPDATE fsq_parking_queue SET digested_at = now() WHERE id = ANY(%s)", (list(ids),))


def purge_show(cur, show_id):
    """Irreversibly delete every DATABASE trace of ONE show (Brian,
    2026-09-15 — the 'complete removal' option on the dashboard's cancel
    dialog, scoped to just this show: the artist row and any other booking
    they have elsewhere, other venues/dates, is untouched).

    Deletes, in order: this show's uploaded files -> its submissions -> its
    event_acts row (and the event itself, plus that event's filed_docs /
    doc_notices REGISTRY row, if this was the only act left on that bill) ->
    the matching bookings row -> the shows row (cascades advance_reminders /
    advance_recaps / send_failures automatically, per their FKs). Then writes
    a sheet_removals tombstone: the next run_now pass deletes the sheet row
    and renames an orphaned filed doc "PURGED - …" (root cause A, audit
    2026-09-16). Never deletes a physical file.

    Returns a summary dict, or None if the show doesn't exist."""
    show = get_show(cur, show_id)
    if not show:
        return None
    artist_id, venue, show_date = show["artist_id"], show["venue"], show["show_date"]

    cur.execute("SELECT name FROM artists WHERE id=%s", (artist_id,))
    artist_row = cur.fetchone()
    artist_name = artist_row["name"] if artist_row else None

    cur.execute("SELECT id FROM submissions WHERE show_id=%s", (show_id,))
    sub_ids = [r["id"] for r in cur.fetchall()]
    files_deleted = 0
    if sub_ids:
        cur.execute("DELETE FROM files WHERE submission_id = ANY(%s) RETURNING id", (sub_ids,))
        files_deleted = len(cur.fetchall())
    cur.execute("DELETE FROM submissions WHERE show_id=%s RETURNING id", (show_id,))
    submissions_deleted = len(cur.fetchall())

    # the matching bookings row — same match_key join every other query in
    # this file uses to tie a booking to a show.
    cur.execute(
        """DELETE FROM bookings b USING artists a
           WHERE a.id=%s AND b.venue=%s AND b.event_date=%s
             AND lower(btrim(regexp_replace(b.artist_name, '\\s+', ' ', 'g'))) = a.match_key
           RETURNING b.id""",
        (artist_id, venue, show_date))
    booking_deleted = cur.fetchone() is not None

    # this act on the event's day-sheet bill, and the event itself
    # (+ its filed-doc registry row) if that was the only act left on it.
    # audit 2026-09-16 (root cause A): the registry row is matched on the
    # event's own key, not venue+date — a same-date 3rd-party event's doc
    # used to go with it. The doc itself is renamed "PURGED - …" in its own
    # folder when the sheet removal is applied (never deleted).
    retired_path = None
    # set when the event survived the purge because another show still sits on
    # that venue+date — the caller/log should say so rather than imply the
    # bill was cleaned up.
    event_kept = None
    cur.execute(
        """SELECT ea.id, ea.event_id, e.name, e.series FROM event_acts ea
           JOIN events e ON e.id = ea.event_id
           WHERE ea.artist_id=%s AND e.venue=%s AND e.event_date=%s""",
        (artist_id, venue, show_date))
    act_row = cur.fetchone()
    if act_row:
        cur.execute("DELETE FROM event_acts WHERE id=%s", (act_row["id"],))
        cur.execute("SELECT count(*) AS n FROM event_acts WHERE event_id=%s", (act_row["event_id"],))
        acts_left = cur.fetchone()["n"]
        # 2026-09-18: "no acts left" is NOT the same as "nothing left on this
        # date". A show only gets an event_acts row when the sheet import puts
        # it on a bill — a real booking that never got one is invisible here.
        # That collision bit on 2026-09-17: a ghost "MANY" act was the only
        # event_acts row on the real FSQ 9/26 Moon Festival, whose actual
        # booking (show 1415) had no act row, so purging the ghost would have
        # deleted the real event and retired its filed doc. Any OTHER show at
        # this venue+date keeps the event and the registry row; an empty event
        # left behind is harmless, a deleted real one is not.
        cur.execute("SELECT count(*) AS n FROM shows WHERE venue=%s AND show_date=%s AND id<>%s",
                    (venue, show_date, show_id))
        shows_left = cur.fetchone()["n"]
        if acts_left == 0 and shows_left == 0:
            cur.execute("DELETE FROM events WHERE id=%s", (act_row["event_id"],))
            cur.execute("SELECT count(*) AS n FROM events WHERE venue=%s AND event_date=%s",
                        (venue, show_date))
            others = cur.fetchone()["n"]
            reg = _registry_row_for_event(cur, venue, show_date,
                                          normalize(act_row["name"] or act_row["series"] or ""),
                                          others + 1)
            if reg:
                retired_path = reg["path"]
                _drop_registry_row(cur, reg)
        elif acts_left == 0:
            event_kept = act_row["event_id"]

    # 2026-09-21 sweep (PIPE-4): a purged orphan releases its 'possible correction'
    # candidates, same as Cancel/Restore/Merge — else they stay held on a dead id.
    release_candidate_holds(cur, show_id)
    cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))

    if artist_row and show_date:
        cur.execute("SELECT match_key FROM artists WHERE id=%s", (artist_id,))
        add_sheet_removal(cur, venue, show_date, cur.fetchone()["match_key"], artist_name,
                          reason="purge", doc_path=retired_path)

    return {
        "artist_name": artist_name,
        "venue": venue,
        "show_date": show_date.isoformat() if show_date else None,
        "submissions_deleted": submissions_deleted,
        "files_deleted": files_deleted,
        "booking_deleted": booking_deleted,
        "filed_doc_retired": retired_path,
        "event_kept": event_kept,
    }


def hold_show(cur, show_id, reason):
    cur.execute("""UPDATE shows SET held_at = now(), hold_reason = %s
                   WHERE id=%s AND held_at IS NULL AND cancelled_at IS NULL
                     AND hold_dismissed_at IS NULL RETURNING id""", (reason, show_id))
    return cur.fetchone() is not None


def restore_show(cur, show_id):
    """Release a hold for good — this show is never auto-held again."""
    cur.execute("UPDATE shows SET held_at = NULL, hold_reason = NULL, hold_dismissed_at = now() "
                "WHERE id=%s RETURNING id", (show_id,))
    return cur.fetchone() is not None


def release_candidate_holds(cur, orphan_show_id):
    """Shows held only as a 'possible correction' of this orphan go back to
    normal (they are real bookings in their own right)."""
    cur.execute("""UPDATE shows SET held_at = NULL, hold_reason = NULL, hold_dismissed_at = now()
                   WHERE hold_reason = %s AND cancelled_at IS NULL""",
                (f"possible correction of show {orphan_show_id}",))


def release_stale_candidate_holds(cur):
    """'possible correction of show N' holds whose orphan N is gone or no longer
    held (2026-09-21 sweep, PIPE-4: any path that drops an orphan without
    releasing its candidates — holds.run sweeps these up nightly)."""
    cur.execute("""UPDATE shows c SET held_at = NULL, hold_reason = NULL, hold_dismissed_at = now()
                   WHERE c.held_at IS NOT NULL AND c.cancelled_at IS NULL
                     AND c.hold_reason ~ '^possible correction of show [0-9]+$'
                     AND NOT EXISTS (SELECT 1 FROM shows o
                                     WHERE o.id = substring(c.hold_reason from '([0-9]+)$')::int
                                       AND o.held_at IS NOT NULL AND o.cancelled_at IS NULL)
                   RETURNING c.id""")
    return [r["id"] for r in cur.fetchall()]


def merge_shows(cur, old_id, new_id, tombstone=True):
    """Typo fix: everything recorded against old_id moves to new_id, then the
    old record is deleted. Send history carries over, so the corrected show
    never gets a second welcome or repeat reminders.

    Root cause A (audit 2026-09-16): the typo'd side's sheet row is tombstoned
    (sheet_removals) so it can't resurrect the old show on the next run, and
    when the old venue+date is left with no show at all its filed doc follows
    the show — re-registered under the new venue+date if that date has no doc
    yet (the next filing pass renames it into the new month folder, hand
    edits intact), else renamed "SUPERSEDED - …" in place. `tombstone=False`
    is for update_booking's rename-in-place, where the sheet row is being
    rewritten, not removed."""
    cur.execute("SELECT * FROM shows WHERE id=%s", (old_id,))
    old = cur.fetchone()
    cur.execute("SELECT * FROM shows WHERE id=%s", (new_id,))
    new = cur.fetchone()
    if not old or not new or old_id == new_id:
        raise ValueError("both shows must exist and differ")
    cur.execute("UPDATE submissions SET show_id=%s WHERE show_id=%s", (new_id, old_id))
    if old["artist_id"] != new["artist_id"]:
        cur.execute("UPDATE submissions SET artist_id=%s WHERE show_id=%s AND artist_id=%s",
                    (new["artist_id"], new_id, old["artist_id"]))
        cur.execute("""UPDATE files SET artist_id=%s WHERE submission_id IN
                       (SELECT id FROM submissions WHERE show_id=%s)""", (new["artist_id"], new_id))
    cur.execute("""INSERT INTO advance_reminders (show_id, days_before, drafted_at, sent)
                   SELECT %s, days_before, drafted_at, sent FROM advance_reminders WHERE show_id=%s
                   ON CONFLICT (show_id, days_before) DO NOTHING""", (new_id, old_id))
    # 2026-09-21 sweep (DBB-7): artist_id moves too — its ON DELETE CASCADE
    # would drop the recap when the old artist row is deleted below.
    cur.execute("""UPDATE advance_recaps SET show_id=%s, artist_id=%s WHERE show_id=%s
                   AND NOT EXISTS (SELECT 1 FROM advance_recaps WHERE show_id=%s)""",
                (new_id, new["artist_id"], old_id, new_id))
    cur.execute("UPDATE submission_matches SET booked_show_id=%s WHERE booked_show_id=%s",
                (new_id, old_id))
    # 2026-09-24 research #11: the open history follows the show — a typo fix
    # would otherwise reset the corrected show to "never opened" when the old
    # row's ON DELETE SET NULL cut its links loose.
    cur.execute("UPDATE short_links SET show_id=%s WHERE show_id=%s", (new_id, old_id))
    cur.execute(
        """UPDATE shows n SET
             email_sent_at = COALESCE(n.email_sent_at, o.email_sent_at),
             responded_at = COALESCE(n.responded_at, o.responded_at),
             followup_sent_at = COALESCE(n.followup_sent_at, o.followup_sent_at),
             advance_draft_created_at = COALESCE(n.advance_draft_created_at, o.advance_draft_created_at),
             followup_draft_created_at = COALESCE(n.followup_draft_created_at, o.followup_draft_created_at),
             send_reminder_sent_at = COALESCE(n.send_reminder_sent_at, o.send_reminder_sent_at),
             unresponded_alert_sent_at = COALESCE(n.unresponded_alert_sent_at, o.unresponded_alert_sent_at),
             finalized_at = COALESCE(n.finalized_at, o.finalized_at),
             thankyou_sent_at = COALESCE(n.thankyou_sent_at, o.thankyou_sent_at),
             -- audit 2026-09-16 #23: these two were missing — losing
             -- advance_held_draft_at un-held a deliberately-withheld draft
             -- and fired a fresh send; losing dayahead_sent_at let the
             -- corrected show's day-before go out a second time.
             advance_held_draft_at = COALESCE(n.advance_held_draft_at, o.advance_held_draft_at),
             dayahead_sent_at = COALESCE(n.dayahead_sent_at, o.dayahead_sent_at),
             cancelled_at = COALESCE(n.cancelled_at, o.cancelled_at),
             held_at = NULL, hold_reason = NULL, hold_dismissed_at = now()
           FROM shows o WHERE n.id=%s AND o.id=%s""", (new_id, old_id))
    # audit 2026-09-16 #23: the old show's own bookings row (if staff had
    # logged one under the pre-correction venue/date/name) otherwise
    # becomes an orphan nothing else cleans up — and the run_now.py #19
    # reconcile step would eventually re-append it to the sheet, recreating
    # exactly what this merge just corrected away.
    old_artist = get_artist(cur, old["artist_id"])
    if old_artist:
        cur.execute(
            """DELETE FROM bookings b
               WHERE b.venue=%s AND b.event_date=%s
                 AND lower(btrim(regexp_replace(b.artist_name, '\\s+', ' ', 'g'))) = %s""",
            (old["venue"], old["show_date"], old_artist["match_key"]))
    cur.execute("DELETE FROM shows WHERE id=%s", (old_id,))
    release_candidate_holds(cur, old_id)  # 2026-09-21 sweep (PIPE-4): carry's merge path skipped it
    retired = reregister_docs_for_move(cur, old["venue"], old["show_date"],
                                       new["venue"], new["show_date"], retire=tombstone)
    if old["artist_id"] != new["artist_id"]:
        # 2026-09-21 sweep: keep the doc's column + hand edits with the show's new artist id
        remap_doc_artist(cur, new["venue"], new["show_date"], old["artist_id"], new["artist_id"])
    if tombstone and old_artist and old["show_date"]:
        add_sheet_removal(cur, old["venue"], old["show_date"], old_artist["match_key"],
                          old_artist["name"], reason="merge", doc_path=retired)
    if old["artist_id"] != new["artist_id"]:
        cur.execute("""DELETE FROM artists a WHERE a.id=%s
                       AND NOT EXISTS (SELECT 1 FROM shows WHERE artist_id=a.id)
                       AND NOT EXISTS (SELECT 1 FROM submissions WHERE artist_id=a.id)""",
                    (old["artist_id"],))


def active_future_shows(cur):
    cur.execute("""SELECT s.*, a.name AS artist_name, a.match_key
                   FROM shows s JOIN artists a ON a.id = s.artist_id
                   WHERE s.show_date >= CURRENT_DATE AND s.cancelled_at IS NULL""")
    return cur.fetchall()


def show_with_artist(cur, show_id):
    cur.execute("""SELECT s.*, a.name AS artist_name, a.last_email, a.match_key
                   FROM shows s JOIN artists a ON a.id=s.artist_id WHERE s.id=%s""", (show_id,))
    return cur.fetchone()


def merge_candidates(cur, show_id):
    """Shows that could be the corrected version of this one: same band on a
    different date/venue, or the same venue+date under a different band name."""
    s = show_with_artist(cur, show_id)
    if not s:
        return []
    cur.execute(
        """SELECT s.*, a.name AS artist_name, a.match_key
           FROM shows s JOIN artists a ON a.id=s.artist_id
           WHERE s.id <> %s AND s.cancelled_at IS NULL AND s.show_date >= CURRENT_DATE - 1
             AND ( s.artist_id = %s
                   OR (s.venue = %s AND s.show_date = %s) )
           ORDER BY s.created_at DESC LIMIT 10""",
        (show_id, s["artist_id"], s["venue"], s["show_date"]))
    return cur.fetchall()


# ── submission → booking matching (audit #6) ─────────────────────────────────

def unresponded_shows_at(cur, venue, show_date):
    cur.execute(
        """SELECT s.id AS show_id, s.artist_id, a.name AS artist_name, s.show_series
           FROM shows s JOIN artists a ON a.id = s.artist_id
           WHERE s.venue=%s AND s.show_date=%s AND s.cancelled_at IS NULL
             AND s.responded_at IS NULL
             -- 2026-09-21 sweep: staff-typed booking answers never stop the
             -- real band submission attaching to its booked show
             AND NOT EXISTS (SELECT 1 FROM submissions sub
                             WHERE sub.show_id = s.id AND sub.source <> 'staff')
           ORDER BY s.id""", (venue, show_date))
    return cur.fetchall()


def show_for_artist_at(cur, artist_id, venue, show_date):
    cur.execute("SELECT * FROM shows WHERE artist_id=%s AND venue=%s AND show_date=%s",
                (artist_id, venue, show_date))
    return cur.fetchone()


def get_match(cur, match_id):
    cur.execute("SELECT * FROM submission_matches WHERE id=%s", (match_id,))
    return cur.fetchone()


def reattach_submission(cur, submission_id, target_show_id, delete_empty_source=True):
    """Move a submission (and its files) onto another show + that show's
    artist, stamp that show responded, and clean up whatever the submission
    left behind (a show/artist it alone created)."""
    cur.execute("SELECT * FROM submissions WHERE id=%s", (submission_id,))
    sub = cur.fetchone()
    cur.execute("SELECT * FROM shows WHERE id=%s", (target_show_id,))
    tgt = cur.fetchone()
    if not sub or not tgt:
        raise ValueError("submission or target show missing")
    old_show, old_artist = sub["show_id"], sub["artist_id"]
    cur.execute("UPDATE submissions SET show_id=%s, artist_id=%s WHERE id=%s",
                (target_show_id, tgt["artist_id"], submission_id))
    cur.execute("UPDATE files SET artist_id=%s WHERE submission_id=%s", (tgt["artist_id"], submission_id))
    cur.execute("UPDATE shows SET responded_at = COALESCE(responded_at, now()) WHERE id=%s",
                (target_show_id,))
    if delete_empty_source:
        _release_show_if_empty(cur, old_show, old_artist)
    else:
        # 2026-09-21 sweep: staff-typed booking answers never stamp responded_at, so a
        # show left with only those goes back to unresponded (its reminders resume)
        cur.execute("""UPDATE shows SET responded_at = NULL WHERE id=%s
                       AND NOT EXISTS (SELECT 1 FROM submissions
                                       WHERE show_id=%s AND source <> 'staff')""",
                    (old_show, old_show))


def detach_submission(cur, submission_id, typed_name, venue, show_date, series=None):
    """'Wrong band' — the submission goes to its own artist/show under the name
    the band typed; the booked show goes back to unresponded."""
    artist_id = upsert_artist(cur, typed_name)
    show_id = upsert_show(cur, artist_id, venue, show_date, series=series)
    reattach_submission(cur, submission_id, show_id, delete_empty_source=False)
    return show_id


def _release_show_if_empty(cur, show_id, artist_id):
    if show_id:
        cur.execute("""SELECT advance_draft_created_at, finalized_at FROM shows WHERE id=%s""", (show_id,))
        row = cur.fetchone()
        # 2026-09-21 sweep: delete only with no submissions at all, but reset responded_at
        # whenever no band answer remains (staff-typed rows never stamp it)
        cur.execute("""SELECT count(*) AS n, count(*) FILTER (WHERE source <> 'staff') AS band_n
                       FROM submissions WHERE show_id=%s""", (show_id,))
        counts = cur.fetchone()
        n = counts["n"]
        if (row and n == 0 and row["advance_draft_created_at"] is None
                and row["finalized_at"] is None):
            cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))
        elif row and counts["band_n"] == 0:
            cur.execute("UPDATE shows SET responded_at=NULL WHERE id=%s", (show_id,))
    if artist_id:
        cur.execute("""DELETE FROM artists a WHERE a.id=%s
                       AND NOT EXISTS (SELECT 1 FROM shows WHERE artist_id=a.id)
                       AND NOT EXISTS (SELECT 1 FROM submissions WHERE artist_id=a.id)""", (artist_id,))


# ── Memorial Hall: held band changes (2026-09-29) ───────────────────────────
def memo_state(cur, show_id):
    """Merged Memo answers for one show (oldest -> newest, blank never erases)."""
    import memo_fields
    cur.execute("""SELECT data FROM submissions WHERE show_id=%s AND data->>'_form' = %s
                   ORDER BY submitted_at, id""", (show_id, memo_fields.FORM_KEY))
    return memo_fields.merge([r["data"] for r in cur.fetchall()])


def add_memo_decisions(cur, show_id, current, held, submission_id, source):
    import json
    import memo_fields
    for k, v in held.items():
        cur.execute("""INSERT INTO memo_decisions (show_id, field, current_value, new_value,
                           new_raw, submission_id, source)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (show_id, k, memo_fields.display(current.get(k)), memo_fields.display(v),
                     json.dumps(v), submission_id, source))


def open_memo_decisions(cur, venue=None, event_date=None, show_id=None):
    """Undecided held changes, with the band and the field's label."""
    import memo_fields
    sql = """SELECT d.*, s.venue, s.show_date, a.name AS artist_name
             FROM memo_decisions d JOIN shows s ON s.id = d.show_id
             JOIN artists a ON a.id = s.artist_id
             WHERE d.resolved_at IS NULL"""
    params = []
    if show_id is not None:
        sql += " AND d.show_id = %s"
        params.append(show_id)
    if venue is not None:
        sql += " AND s.venue = %s AND s.show_date = %s"
        params += [venue, event_date]
    cur.execute(sql + " ORDER BY d.show_id, d.id", params)
    rows = cur.fetchall()
    for r in rows:
        r["label"] = (memo_fields.FIELDS.get(r["field"]) or {}).get("label", r["field"])
    return rows


def resolve_memo_decision(cur, decision_id, use_new):
    """Keep the current answer, or apply the held one as a staff save.
    Returns the show id, or None if it was already decided."""
    import datetime as _dt
    import memo_fields
    cur.execute("""UPDATE memo_decisions SET resolved_at = now(), resolution = %s
                   WHERE id = %s AND resolved_at IS NULL RETURNING *""",
                ("applied" if use_new else "kept", decision_id))
    d = cur.fetchone()
    if not d:
        return None
    if use_new:
        s = show_with_artist(cur, d["show_id"])
        data = {d["field"]: d["new_raw"], "_form": memo_fields.FORM_KEY, "_staff_edit": True,
                "band_name": s["artist_name"], "venue": s["venue"],
                "show_date": s["show_date"].isoformat(),
                "_submitted_at": _dt.datetime.now().isoformat(timespec="seconds"),
                "_source_note": f"memo decision {decision_id}: used the band's new answer"}
        insert_submission(cur, s["artist_id"], d["show_id"], data, source="staff")
    return d["show_id"]
