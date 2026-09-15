-- Booking edit tracking + "info changed" notification to the band
-- (Brian, 2026-09-14): staff can now edit a logged booking's core fields
-- after the fact. An edit that touches a band-facing field (date, venue,
-- location, artist name, slot, set time, load-in/soundcheck/start/end/
-- curfew), on a show still inside the 21-day window, queues one email —
-- sent by the NEXT daily lifecycle run, never immediately. Several edits
-- before that run collapse into the same pending row instead of separate
-- emails. See advance_db.update_booking / due_booking_edits and
-- tools/booking_update.py.
CREATE TABLE IF NOT EXISTS booking_edits (
    id           SERIAL PRIMARY KEY,
    booking_id   INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    changes      JSONB NOT NULL,          -- {field: {"old": ..., "new": ...}}
    edited_by    TEXT,
    edited_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    notify       BOOLEAN NOT NULL DEFAULT false,
    sent_at      TIMESTAMPTZ,
    error        TEXT
);
-- one pending (unsent, notify) row per booking at a time — a later edit
-- merges into it (advance_db.update_booking) instead of queuing a second email
CREATE UNIQUE INDEX IF NOT EXISTS uq_booking_edits_pending
    ON booking_edits (booking_id) WHERE notify AND sent_at IS NULL;

-- advance_status view gains booking_id so the dashboard can link each act to
-- its bookings row for the new "Edit booking" button. DROP first — CREATE OR
-- REPLACE can't insert a column ahead of existing ones, only append.
--
-- BUG (found 2026-09-15, live dashboard): this rewrite dropped
-- cancelled_at/held_at/thankyou_sent_at/thankyou_error and, with them, the
-- 'cancelled'/'held' WHEN branches #4/#17 in schema.sql had added. So
-- cancelling a show from the dashboard set shows.cancelled_at, but the
-- view's state CASE never looked at that column, fell through to whatever
-- state the show was already in, and the card kept showing exactly as
-- before — no strikethrough, no Cancelled pill, Cancel button still there.
-- Restored below, keeping this migration's booking_id column.
DROP VIEW IF EXISTS advance_status;
CREATE VIEW advance_status AS
SELECT
    s.id            AS show_id,
    a.id            AS artist_id,
    a.name          AS band,
    s.venue,
    s.show_series,
    s.show_date,
    s.email_sent_at,
    s.responded_at,
    s.followup_sent_at,
    s.advance_draft_created_at,
    s.followup_draft_created_at,
    s.send_reminder_sent_at,
    s.finalized_at,
    s.cancelled_at,
    s.held_at,
    s.thankyou_sent_at,
    s.thankyou_error,
    b.id            AS booking_id,
    (SELECT max(sub.submitted_at) FROM submissions sub WHERE sub.show_id = s.id)
                    AS last_submission,
    CASE
        WHEN s.cancelled_at IS NOT NULL THEN 'cancelled'
        WHEN s.finalized_at IS NOT NULL THEN 'finalized'
        WHEN s.held_at IS NOT NULL THEN 'held'
        WHEN s.responded_at IS NOT NULL
             OR EXISTS (SELECT 1 FROM submissions sub WHERE sub.show_id = s.id)
            THEN 'responded'
        WHEN s.followup_draft_created_at IS NOT NULL THEN 'followup_drafted'
        WHEN s.advance_draft_created_at IS NOT NULL
             AND s.show_date IS NOT NULL
             AND s.show_date <= CURRENT_DATE + 7
            THEN 'followup_due'
        WHEN s.advance_draft_created_at IS NOT NULL
             AND s.show_date IS NOT NULL
             AND s.show_date <= CURRENT_DATE + 21
            THEN 'ready_to_send'
        WHEN s.advance_draft_created_at IS NOT NULL  THEN 'awaiting'
        ELSE 'queued'
    END             AS state,
    CASE WHEN s.show_date IS NOT NULL
         THEN (s.show_date - CURRENT_DATE) END
                    AS days_until_show,
    a.last_email    AS contact_email
FROM shows s
JOIN artists a ON a.id = s.artist_id
LEFT JOIN bookings b ON b.venue = s.venue AND b.event_date = s.show_date
       AND lower(btrim(regexp_replace(b.artist_name, '\s+', ' ', 'g'))) = a.match_key;
