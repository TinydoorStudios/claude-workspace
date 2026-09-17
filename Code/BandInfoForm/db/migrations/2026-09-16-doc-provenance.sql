-- Root cause B (audit 2026-09-16): doc provenance keyed by artist, not column.
-- columns     {"1": artist_id, "2": ...} the doc was last written with; when
--             the fresh bill's map differs, docmerge moves each artist's cells
--             to their new column before merging.
-- reviewed_at the moment the doc's last open decision was resolved (F11):
--             the resubmission-review check counts from
--             GREATEST(written_at, reviewed_at). Idempotent.
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS columns JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;
