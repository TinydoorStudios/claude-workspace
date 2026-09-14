-- Brian, 2026-09-14: a resubmission that would change a filled cell in an
-- advance doc waits for his Keep doc / Use new call instead of being applied
-- silently (pipeline-filled cells) or only reported (hand-typed cells).
-- Every doc_notices row is now a decision. Idempotent.
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS cell_key     TEXT;         -- merge key of the cell/paragraph; NULL on rows from before this
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS resolved_at  TIMESTAMPTZ;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS resolution   TEXT;         -- kept | applied | superseded | moot | dismissed
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS apply_requested_at TIMESTAMPTZ;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS apply_error  TEXT;
CREATE INDEX IF NOT EXISTS idx_doc_notices_open ON doc_notices (venue, event_date) WHERE resolved_at IS NULL;

-- the review page waits on this: set by regen_show.py once it has checked
-- the doc against a submission (whatever the outcome)
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS doc_checked_at TIMESTAMPTZ;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS doc_check      TEXT;
