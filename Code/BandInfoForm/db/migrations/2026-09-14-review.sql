-- Applied to live 2026-09-14 with the review-pass deploy. Idempotent.
CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_ident
    ON bookings (venue, event_date, (lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g')))));
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS cells JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE send_failures ADD COLUMN IF NOT EXISTS suppressed BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS dayahead_sent_at TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS dayahead_error   TEXT;
CREATE TABLE IF NOT EXISTS digest_items (
    id           SERIAL PRIMARY KEY,
    kind         TEXT NOT NULL,
    subject      TEXT NOT NULL,
    html         TEXT NOT NULL,
    link         TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    delivered_at TIMESTAMPTZ
);
-- record fix: tier-7 pre-skips written before the `sent` column existed
UPDATE advance_reminders r SET sent = false
  FROM shows s WHERE s.id = r.show_id AND r.days_before = 7
   AND s.advance_draft_created_at IS NOT NULL
   AND (s.show_date - s.advance_draft_created_at::date) <= 7 AND r.sent;
-- M1 applied to in-flight shows: pre-skip any tier that would fire within
-- 48h of a welcome sent in the last 2 days (Amador Sisters tier 3 on 9/14)
INSERT INTO advance_reminders (show_id, days_before, sent)
SELECT s.id, t.tier, false
  FROM shows s CROSS JOIN (VALUES (7),(3),(1)) AS t(tier)
 WHERE s.advance_draft_created_at > now() - interval '2 days'
   AND s.responded_at IS NULL AND s.cancelled_at IS NULL
   AND t.tier > (s.show_date - s.advance_draft_created_at::date) - 2
ON CONFLICT (show_id, days_before) DO NOTHING;
