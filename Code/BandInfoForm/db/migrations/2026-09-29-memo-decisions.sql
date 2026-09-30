-- Memorial Hall advance (Brian, 2026-09-29): a band answer that differs from
-- what's already on the show is held, not applied, until Brian picks which one
-- remains (Doc Review page + dashboard count, and Nyquist asks in chat).
CREATE TABLE IF NOT EXISTS memo_decisions (
    id            SERIAL PRIMARY KEY,
    show_id       INTEGER NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
    field         TEXT NOT NULL,
    current_value TEXT,
    new_value     TEXT,
    new_raw       JSONB,
    submission_id INTEGER REFERENCES submissions(id) ON DELETE SET NULL,
    source        TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at   TIMESTAMPTZ,
    resolution    TEXT
);
CREATE INDEX IF NOT EXISTS idx_memo_decisions_open ON memo_decisions (show_id) WHERE resolved_at IS NULL;
