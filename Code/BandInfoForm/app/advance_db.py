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
        # a rename that collides with ANOTHER artist's match_key would violate
        # the unique index and lose the whole submission's DB write — keep
        # the existing name in that case, update contact info only.
        cur.execute("SELECT 1 FROM artists WHERE match_key = %s AND id <> %s",
                    (normalize(name), known_id))
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
                  b.contact_name AS contact_name, b.contact_email AS booking_contact_email
           FROM shows s JOIN artists a ON a.id = s.artist_id
           LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key
           WHERE s.advance_draft_created_at IS NULL
             AND s.cancelled_at IS NULL AND s.held_at IS NULL
             AND s.responded_at IS NULL
             AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
             AND s.show_date IS NOT NULL
             AND s.show_date >= CURRENT_DATE
             AND s.show_date <= CURRENT_DATE + 21
             AND b.skip_welcome_email IS NOT TRUE
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.id, b.id DESC NULLS LAST"""
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


def shows_due_for_send_reminder(cur, days_out=21):
    """RETIRED (Brian, 2026-09-13, live-send migration) — no longer called
    anywhere. Used to nudge Brian that a draft sitting in Gmail/Outlook was
    ready to send at the 21-day mark; now that the initial advance sends
    itself for real at booking time, there's no draft left to nudge about.
    Left in place (unused) rather than deleted in case anything ever needs
    the historical shape back."""
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
FOLLOWUP_TIERS = (7, 3, 1)


def shows_due_for_followup(cur, days_before=7):
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
             AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
             AND NOT EXISTS (SELECT 1 FROM advance_reminders r
                             WHERE r.show_id = s.id AND r.days_before = %s)
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
             AND NOT """ + THIRD_PARTY_SILENT_SQL + """
           ORDER BY s.id, b.id DESC NULLS LAST""",
        (days_before, days_before),
    )
    return sorted(cur.fetchall(), key=lambda r: (r["show_date"], r["show_id"]))


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


def mark_stale_followup_tiers_skipped(cur, show_id, days_out):
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
    # Review 2026-09-14 (M1): a band booked 4 days out used to get the
    # welcome, the 3-day reminder the next morning and the 1-day reminder two
    # days later. No band-facing reminder fires within 48 hours of the
    # welcome: a tier is skipped when its day is less than 2 days after
    # today, i.e. tier > days_out - 2.
    for tier in FOLLOWUP_TIERS:
        if tier > days_out - 2:
            cur.execute(
                "INSERT INTO advance_reminders (show_id, days_before, sent) "
                "VALUES (%s, %s, false) ON CONFLICT (show_id, days_before) DO NOTHING",
                (show_id, tier),
            )


def mark_send_reminder_sent(cur, show_id):
    """RETIRED (Brian, 2026-09-13) — see shows_due_for_send_reminder."""
    cur.execute(
        "UPDATE shows SET send_reminder_sent_at = COALESCE(send_reminder_sent_at, now()) "
        "WHERE id = %s", (show_id,),
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
             AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
             AND s.show_date IS NOT NULL
             AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
             AND (
                  (s.advance_draft_created_at IS NOT NULL
                   AND s.advance_draft_created_at <= now() - interval '24 hours')
               OR (b.skip_welcome_email IS TRUE AND s.advance_draft_created_at IS NULL
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
    text ('7:00pm') — see parse_clock."""
    cur.execute(
        """SELECT id, event_name, venue, location, series, artist_name,
                  load_in, soundcheck, event_start, event_end, curfew
           FROM bookings
           WHERE event_date = %s
           ORDER BY venue, event_name, id""",
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
    daily digest's ranked at-a-glance list."""
    cur.execute(
        """SELECT * FROM advance_status
           WHERE days_until_show BETWEEN 0 AND %s
           ORDER BY days_until_show ASC, band ASC""",
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
        "SELECT COUNT(DISTINCT lower(btrim(regexp_replace(artist_name,'\\s+',' ','g')))) AS n "
        "FROM bookings WHERE venue=%s AND event_date=%s AND COALESCE(btrim(artist_name),'') <> '' "
        "AND (lower(btrim(COALESCE(series,''))) = '3rd party') = %s",
        (venue, event_date, is_third_party(series)),
    )
    row = cur.fetchone()
    return (row["n"] or 0) if row else 0


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
            vehicle_count, large_vehicle_count, data, source
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                      carry_plot=True):
    """One transaction: resolve which artist+show this submission belongs to,
    insert it, stamp responded_at, link any uploaded file. Returns a dict:
    {artist_id, show_id, submission_id, artist_name, match, carried_from}.
    Raises on failure — the form treats that as non-fatal.

    Resolution (2026-09-13 audit #6):
      1. form["artist_id"] — ONLY set by app.py after verifying the signed
         artist token from the band's own link. Same artist record, even if
         they edited the name.
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
    with get_conn() as conn:
        with conn.cursor() as cur:
            artist_id = show_id = None
            if known_id and get_artist(cur, known_id):
                artist_id = upsert_artist(cur, name, email=form.get("contact_email"),
                                          phone=form.get("contact_phone"), known_id=known_id)
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
                artist_id = upsert_artist(cur, name, email=form.get("contact_email"),
                                          phone=form.get("contact_phone"))
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
            "carried_from": carried_from}


# ── queries: prefill, returning-artist logic, search ────────────────────────

def find_artist_by_name(cur, name):
    cur.execute("SELECT * FROM artists WHERE match_key = %s", (normalize(name),))
    return cur.fetchone()


_NAME_STOPWORDS = {"the", "and", "&", "band", "feat", "feat.", "ft", "ft.", "featuring",
                   "trio", "quartet", "quintet", "duo", "group", "orchestra", "dj", "with", "w/"}


def _name_tokens(name):
    return {t for t in re.split(r"[^a-z0-9]+", normalize(name)) if t and t not in _NAME_STOPWORDS}


def names_plausible(typed, booked):
    """Review 2026-09-14 (H5): is `typed` plausibly the same act as `booked`?
    True when one normalized name contains the other, or at least half of
    the meaningful words overlap. Gate on auto-attaching a submission to the
    one unanswered booking — before this, ANY typed name attached to whoever
    hadn't answered yet."""
    a, b = normalize(typed), normalize(booked)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True
    ta, tb = _name_tokens(a), _name_tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb)
    return overlap / min(len(ta), len(tb)) >= 0.5


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
    """Sourced from advance_status (Brian, 2026-09-13), not raw `shows` — the
    template's Status column used to read `s.status`, a column dropped
    2026-09-09; it had been silently rendering blank ever since. The view
    carries every column the template needs (show_date/venue/show_series)
    plus the real computed `state`, the same one the dashboard reads."""
    cur.execute(
        "SELECT * FROM advance_status WHERE artist_id=%s ORDER BY show_date DESC NULLS LAST",
        (artist_id,),
    )
    return cur.fetchall()


def get_show(cur, show_id):
    cur.execute("SELECT * FROM shows WHERE id = %s", (show_id,))
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
    cur.execute("UPDATE events SET details=%s WHERE id=%s",
                (json.dumps(cur_details), event_id))


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
         load_in, soundcheck, json.dumps(sheet_fields or {})),
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
    carrying its artist + the submission to fill from (the linked submission, or
    the artist's newest). Order is computed here, every time, from set start:
    see order_acts. `id` is the tiebreak, so the query orders by it."""
    cur.execute(
        "SELECT * FROM event_acts WHERE event_id=%s ORDER BY id", (event_id,)
    )
    acts = order_acts(cur.fetchall())
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
    cols = ", ".join(BOOKING_FIELDS) + ", skip_welcome_email, band_emails"
    ph = ", ".join(f"%({k})s" for k in BOOKING_FIELDS) + ", %(skip_welcome_email)s, %(band_emails)s"
    # Review 2026-09-14 (H1): one booking row per band/venue/date. A double
    # submit, a refresh that re-POSTs, or a re-entry updates the existing row
    # instead of creating a twin that would make the lifecycle send twice.
    # seeded_at is kept so an already-seeded row isn't appended to the sheet
    # again.
    upd = ", ".join(f"{k} = EXCLUDED.{k}" for k in BOOKING_FIELDS
                    if k not in ("venue", "event_date", "artist_name"))
    cur.execute(
        f"""INSERT INTO bookings ({cols}) VALUES ({ph})
            ON CONFLICT (venue, event_date, (lower(btrim(regexp_replace(artist_name, '\\s+', ' ', 'g')))))
            DO UPDATE SET {upd}, skip_welcome_email = EXCLUDED.skip_welcome_email,
                          band_emails = EXCLUDED.band_emails
            RETURNING id""", vals)
    return cur.fetchone()["id"]


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
    FIELDS change, while the show is still inside the 21-day window, is
    recorded as a booking_edits row — merged into any still-unsent pending
    row for this booking, so several edits before the next daily lifecycle
    run collapse into one email instead of several (uq_booking_edits_pending).

    Returns (changes, notify) — the diff dict just recorded (empty if
    nothing band-facing changed) and whether it queued a notice (False when
    changes is empty, or the show is outside the 21-day notify window)."""
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
    vals["id"] = booking_id
    sets = ", ".join(f"{k} = %({k})s" for k in BOOKING_FIELDS)
    cur.execute(
        f"""UPDATE bookings SET {sets}, skip_welcome_email = %(skip_welcome_email)s,
                                 band_emails = %(band_emails)s
            WHERE id = %(id)s""", vals)

    changes = {}
    for f in BAND_FACING_FIELDS:
        old, new = before.get(f), vals.get(f)
        old_s = old.isoformat() if isinstance(old, dt.date) else (old or "")
        new_s = new.isoformat() if isinstance(new, dt.date) else (new or "")
        if old_s != new_s:
            changes[f] = {"old": old_s, "new": new_s}
    event_date = vals.get("event_date") or before.get("event_date")
    in_window = bool(event_date) and 0 <= (event_date - dt.date.today()).days <= 21
    notify = bool(changes) and in_window
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


def due_booking_edits(cur):
    """Pending booking-edit notifications ready for the next daily lifecycle
    run — still inside the 21-day window (an edit queued while urgent, then
    the window closes some other way before the next run, silently drops
    the notice rather than sending a stale one)."""
    cur.execute(
        """SELECT e.id AS edit_id, e.booking_id, e.changes, e.edited_at,
                  b.artist_name, b.event_date, b.venue, b.contact_email, b.series
           FROM booking_edits e JOIN bookings b ON b.id = e.booking_id
           WHERE e.notify AND e.sent_at IS NULL
             AND b.event_date IS NOT NULL
             AND b.event_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 21
           ORDER BY e.id""")
    return cur.fetchall()


def mark_booking_edit_sent(cur, edit_id, ok, err=None):
    if ok:
        cur.execute("UPDATE booking_edits SET sent_at=now(), error=NULL WHERE id=%s", (edit_id,))
    else:
        cur.execute("UPDATE booking_edits SET error=%s WHERE id=%s", (err, edit_id))


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
                     reg_id=None, keep_written_at=False, cells=None):
    """`cells` (review 2026-09-14, H2): the per-cell provenance map — what
    the pipeline last wrote, keyed by section|column[|paragraph]. None
    leaves the stored map alone."""
    import json
    cells_json = json.dumps(cells) if cells is not None else None
    if reg_id:
        cur.execute(
            """UPDATE filed_docs SET event_key=%s, path=%s, sha256=%s,
                   written_at = CASE WHEN %s THEN written_at ELSE now() END,
                   cells = COALESCE(%s::jsonb, cells)
               WHERE id=%s""",
            (event_key, path, sha256, keep_written_at, cells_json, reg_id))
        return reg_id
    cur.execute(
        """INSERT INTO filed_docs (venue, event_date, event_key, path, sha256, seeded, cells)
           VALUES (%s,%s,%s,%s,%s,%s,COALESCE(%s::jsonb, '{}'::jsonb))
           ON CONFLICT (venue, event_date, event_key) DO UPDATE SET
               path=EXCLUDED.path, sha256=EXCLUDED.sha256, written_at=now(),
               cells = COALESCE(%s::jsonb, filed_docs.cells)
           RETURNING id""",
        (venue, event_date, event_key, path, sha256, seeded, cells_json, cells_json))
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
    sql = ("SELECT * FROM doc_notices WHERE venue=%s AND event_date=%s AND kind='diff' "
           "AND resolved_at IS NULL")
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
                   WHERE id=%s AND resolved_at IS NULL""", (resolution, notice_id))


def keep_doc_value(cur, notice):
    """Brian chose "Keep doc": the decision is closed and the pipeline gives
    up ownership of that cell, so no later pass writes over what the doc says
    (it's treated as hand-typed from here on)."""
    resolve_doc_notice(cur, notice["id"], "kept")
    key = notice.get("cell_key")
    if not key or key.startswith("plot:"):
        return
    cur.execute("""SELECT id, cells FROM filed_docs WHERE venue=%s AND event_date=%s AND event_key=%s""",
                (notice["venue"], notice["event_date"], notice["event_key"]))
    reg = cur.fetchone()
    if not reg:
        return
    cells = {k: v for k, v in (reg["cells"] or {}).items() if k.lower() != key.lower()}
    import json
    cur.execute("UPDATE filed_docs SET cells=%s::jsonb WHERE id=%s", (json.dumps(cells), reg["id"]))


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
    cur.execute("""SELECT n.venue, n.event_date, count(*) AS n, min(n.created_at) AS since,
                          string_agg(n.field, ', ' ORDER BY n.id) AS fields
                   FROM doc_notices n
                   WHERE n.kind = 'diff' AND n.resolved_at IS NULL AND n.event_date >= CURRENT_DATE
                   GROUP BY n.venue, n.event_date ORDER BY n.event_date, n.venue""")
    from urllib.parse import quote
    for n in cur.fetchall():
        out.append({"kind": "doc", "label": "Doc changes to decide",
                    "detail": f"{n['venue']} {n['event_date']:%m/%d} · {n['n']} field(s): {n['fields'][:120]}",
                    "link_path": f"/doc-review?venue={quote(n['venue'])}&date={n['event_date'].isoformat()}",
                    "since": n["since"]})
    cur.execute("""SELECT f.*, a.name, s.venue, s.show_date FROM send_failures f
                   JOIN shows s ON s.id=f.show_id JOIN artists a ON a.id=s.artist_id
                   WHERE f.created_at > now() - interval '3 days' AND s.show_date >= CURRENT_DATE
                   ORDER BY f.id DESC""")
    for f in cur.fetchall():
        out.append({"kind": "send", "label": f"Email not sent ({f['kind']})",
                    "detail": f"{f['name']} — {f['venue']} {f['show_date']:%m/%d}: {f['error']}",
                    "link_path": None, "since": f["created_at"]})
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date FROM shows s
                   JOIN artists a ON a.id=s.artist_id
                   WHERE s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 21
                     AND s.cancelled_at IS NULL AND s.held_at IS NULL AND s.responded_at IS NULL
                     AND COALESCE(a.last_email, '') = ''
                     AND lower(btrim(COALESCE(s.show_series,''))) <> '3rd party' ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "noemail", "label": "No contact email",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}",
                    "link_path": f"/artist/{r['artist_id']}", "since": None})
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date, s.thankyou_error
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.thankyou_error IS NOT NULL AND s.thankyou_sent_at IS NULL
                     AND s.show_date >= CURRENT_DATE ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "thankyou", "label": "Thank-you not sent",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}: {r['thankyou_error']}",
                    "link_path": f"/artist/{r['artist_id']}", "since": None})
    cur.execute("""SELECT s.id, a.id AS artist_id, a.name, s.venue, s.show_date
                   FROM shows s JOIN artists a ON a.id=s.artist_id
                   WHERE s.responded_at IS NULL AND s.cancelled_at IS NULL AND s.held_at IS NULL
                     AND s.show_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 3
                     AND NOT EXISTS (SELECT 1 FROM submissions x WHERE x.show_id = s.id)
                     AND NOT (lower(btrim(COALESCE(s.show_series,''))) = '3rd party' AND COALESCE(a.last_email,'') = '')
                     AND NOT """ + THIRD_PARTY_SILENT_SQL + """
                   ORDER BY s.show_date""")
    for r in cur.fetchall():
        out.append({"kind": "unresponded", "label": "No form, show within 3 days",
                    "detail": f"{r['name']} — {r['venue']} {r['show_date']:%m/%d}",
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
    cur.execute("UPDATE shows SET cancelled_at = NULL, hold_dismissed_at = now() "
                "WHERE id=%s RETURNING id", (show_id,))
    return cur.fetchone() is not None


def queue_fsq_parking(cur, *, artist_id, show_id, band, venue, show_date,
                       contact_name, contact_email, contact_phone,
                       vehicle_count, large_vehicle_count):
    """Hold one Fountain Square band's parking numbers for the next daily
    digest (Brian, 2026-09-15 — step 2: no more per-submission draft,
    everything overnight batches into one email, sent only when non-empty).
    A full snapshot is stored, not just the ids, so a later edit or purge of
    the show can't change what already went out, or silently drop a pending
    item. Returns the new row's id."""
    cur.execute(
        """INSERT INTO fsq_parking_queue
               (artist_id, show_id, band, venue, show_date, contact_name,
                contact_email, contact_phone, vehicle_count, large_vehicle_count)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        (artist_id, show_id, band, venue, show_date, contact_name,
         contact_email, contact_phone, vehicle_count, large_vehicle_count))
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
    event_acts row (and the event itself, plus the filed_docs/doc_notices
    REGISTRY rows, if this was the only act left on that bill) -> the
    matching bookings row -> the shows row (cascades advance_reminders /
    followup_queue / advance_recaps / send_failures automatically, per their
    FKs). Never touches physical files — a filed .docx/.md on Dropbox, or a
    stage-plot upload's copy on the NAS — those are named in the returned
    summary for a human to remove by hand.

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
    # (+ its filed-doc registry rows) if that was the only act left on it —
    # the physical file stays; only the registry pointer to it is cleared.
    filed_paths = []
    cur.execute(
        """SELECT ea.id, ea.event_id FROM event_acts ea
           JOIN events e ON e.id = ea.event_id
           WHERE ea.artist_id=%s AND e.venue=%s AND e.event_date=%s""",
        (artist_id, venue, show_date))
    act_row = cur.fetchone()
    if act_row:
        cur.execute("DELETE FROM event_acts WHERE id=%s", (act_row["id"],))
        cur.execute("SELECT count(*) AS n FROM event_acts WHERE event_id=%s", (act_row["event_id"],))
        if cur.fetchone()["n"] == 0:
            cur.execute("DELETE FROM events WHERE id=%s", (act_row["event_id"],))
            cur.execute("SELECT path FROM filed_docs WHERE venue=%s AND event_date=%s",
                        (venue, show_date))
            filed_paths = [r["path"] for r in cur.fetchall()]
            cur.execute("DELETE FROM filed_docs WHERE venue=%s AND event_date=%s", (venue, show_date))
            cur.execute("DELETE FROM doc_notices WHERE venue=%s AND event_date=%s", (venue, show_date))

    cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))

    return {
        "artist_name": artist_name,
        "venue": venue,
        "show_date": show_date.isoformat() if show_date else None,
        "submissions_deleted": submissions_deleted,
        "files_deleted": files_deleted,
        "booking_deleted": booking_deleted,
        "filed_paths_needing_manual_cleanup": filed_paths,
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


def merge_shows(cur, old_id, new_id):
    """Typo fix: everything recorded against old_id moves to new_id, then the
    old record is deleted. Send history carries over, so the corrected show
    never gets a second welcome or repeat reminders."""
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
    cur.execute("""UPDATE advance_recaps SET show_id=%s WHERE show_id=%s
                   AND NOT EXISTS (SELECT 1 FROM advance_recaps WHERE show_id=%s)""",
                (new_id, old_id, new_id))
    cur.execute("UPDATE submission_matches SET booked_show_id=%s WHERE booked_show_id=%s",
                (new_id, old_id))
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
             held_at = NULL, hold_reason = NULL, hold_dismissed_at = now()
           FROM shows o WHERE n.id=%s AND o.id=%s""", (new_id, old_id))
    cur.execute("DELETE FROM shows WHERE id=%s", (old_id,))
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
        """SELECT s.*, a.name AS artist_name FROM shows s JOIN artists a ON a.id=s.artist_id
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
             AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
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
        cur.execute("""UPDATE shows SET responded_at = NULL WHERE id=%s
                       AND NOT EXISTS (SELECT 1 FROM submissions WHERE show_id=%s)""",
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
        cur.execute("SELECT count(*) AS n FROM submissions WHERE show_id=%s", (show_id,))
        n = cur.fetchone()["n"]
        if row and n == 0:
            if row["advance_draft_created_at"] is None and row["finalized_at"] is None:
                cur.execute("DELETE FROM shows WHERE id=%s", (show_id,))
            else:
                cur.execute("UPDATE shows SET responded_at=NULL WHERE id=%s", (show_id,))
    if artist_id:
        cur.execute("""DELETE FROM artists a WHERE a.id=%s
                       AND NOT EXISTS (SELECT 1 FROM shows WHERE artist_id=a.id)
                       AND NOT EXISTS (SELECT 1 FROM submissions WHERE artist_id=a.id)""", (artist_id,))
