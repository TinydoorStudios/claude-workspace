-- Root cause A (audit 2026-09-16): purge / merge / rename never reached
-- advance-list.xlsx, so the next run re-imported the sheet row and the
-- deleted show came back with blank stamps and got welcomed again.
--
-- sheet_removals is the tombstone purge_show / merge_shows write. run_now
-- deletes the matching sheet row BEFORE the rebuild reads the sheet and then
-- stamps applied_at; until then import_sheet.py and draft_emails.py refuse
-- to create an act or a show for that ident. doc_path is the filed doc that
-- lost its last act (renamed "PURGED - …" / "SUPERSEDED - …" in the same
-- folder when the removal is applied — never deleted). Idempotent.
CREATE TABLE IF NOT EXISTS sheet_removals (
    id           SERIAL PRIMARY KEY,
    venue        TEXT NOT NULL,
    event_date   DATE NOT NULL,
    match_key    TEXT NOT NULL,             -- artists.match_key of the removed act
    artist_name  TEXT,                      -- display name, for logs only
    reason       TEXT NOT NULL DEFAULT 'purge',   -- purge | merge
    doc_path     TEXT,                      -- relative to the Dropbox root
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_sheet_removals_pending
    ON sheet_removals (venue, event_date, match_key) WHERE applied_at IS NULL;

-- edited_bookings._old_ident needs every edit since the row last matched the
-- sheet, not just the newest one (audit db P2).
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS synced_at TIMESTAMPTZ;
