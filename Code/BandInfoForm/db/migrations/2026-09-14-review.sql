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
-- 2026-09-21 sweep: the two one-time data fixes that shipped here on 9/14
-- now live in db/oneoff/2026-09-14-review-data.sql. Deploy re-runs every
-- migration in the container's UTC psql session, so re-running the M1
-- pre-skip permanently skipped live reminder tiers for welcomes sent after
-- 8pm ET. The M1 rule itself lives in advance_db.mark_stale_followup_tiers_skipped.
