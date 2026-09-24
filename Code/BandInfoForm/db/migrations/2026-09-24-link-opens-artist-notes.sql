-- 2026-09-24 research #11 + #12 (2026-09-16 audit, section d).
--
-- #11 — open tracking on the emailed short link. A /s/<code> hit is the
-- earliest sign the welcome landed somewhere other than spam, and "sent, never
-- opened" is the row to chase first. Stamped by app.py's /s/<code> route in the
-- SAME statement that resolves the code (advance_db.open_short_link), so the
-- redirect costs no extra round trip and a stamp failure can't break it.
-- show_id is what lets the dashboard / digest say it per advance: the reminder
-- path sets it when the code is minted, the welcome path (tools/draft_emails.py
-- doesn't know it at mint time) gets it backfilled on the first open, which is
-- the only moment it matters. ON DELETE SET NULL — purging a show must not
-- delete a link that still resolves. Nothing about the visitor is stored: no
-- IP, no user agent, no per-hit rows.
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS first_opened_at TIMESTAMPTZ;
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS open_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS show_id INTEGER REFERENCES shows(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_short_links_show ON short_links (show_id);

-- #12 — post-show note on the artist, so the next chase is calibrated by what
-- happened last time ("plot wrong, 3 reminders"). artists.notes already existed
-- and nothing ever wrote it; this claims it as the staff note and adds the 1–5
-- "advance accuracy" pip beside it. Staff-only: both are rendered on the gated
-- /artist page and the internal Needs-you rows, and never in any band-facing
-- email or document.
ALTER TABLE artists ADD COLUMN IF NOT EXISTS advance_rating SMALLINT;
DO $$ BEGIN
    ALTER TABLE artists ADD CONSTRAINT artists_advance_rating_range
        CHECK (advance_rating IS NULL OR advance_rating BETWEEN 1 AND 5);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
