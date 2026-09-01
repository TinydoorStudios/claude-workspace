-- 3CDC Band Advance — database schema
-- Source of truth for the advance pipeline. Four linked tables:
--   artists  → one row per band, ever (identity anchor)
--   shows    → one row per booking (same band, many venues = many rows)
--   submissions → one row per advance-form response
--   files    → one row per uploaded asset (stage plot / input list)
--
-- Identity rule (locked with Brian 2026-08-31):
--   name      = exact, verbatim — drives every email + document, never altered
--   match_key = normalized (lowercased, whitespace-collapsed) — matching ONLY, hidden.
--               Generated automatically so a stray capital or space can never split a band
--               and defeat the 6-month lookback.

CREATE TABLE IF NOT EXISTS artists (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,                     -- exact, verbatim (display everywhere)
    match_key   TEXT GENERATED ALWAYS AS
                  (lower(btrim(regexp_replace(name, '\s+', ' ', 'g')))) STORED,
    last_email  TEXT,                              -- last-known contact email (from advance list)
    last_phone  TEXT,                              -- last-known day-of phone (from form)
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_artists_match_key ON artists (match_key);

CREATE TABLE IF NOT EXISTS shows (
    id            SERIAL PRIMARY KEY,
    artist_id     INTEGER NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    venue         TEXT,
    show_series   TEXT,
    show_date     DATE,
    -- pipeline state: not_advanced -> email_sent -> responded -> built -> complete
    status        TEXT NOT NULL DEFAULT 'not_advanced',
    email_sent_at TIMESTAMPTZ,
    doc_path      TEXT,                            -- filled DOC generated for this show
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- one booking per artist / venue / date
CREATE UNIQUE INDEX IF NOT EXISTS uq_shows_booking ON shows (artist_id, venue, show_date);
CREATE INDEX IF NOT EXISTS idx_shows_artist ON shows (artist_id);
CREATE INDEX IF NOT EXISTS idx_shows_date   ON shows (show_date);

CREATE TABLE IF NOT EXISTS submissions (
    id            SERIAL PRIMARY KEY,
    artist_id     INTEGER NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    show_id       INTEGER REFERENCES shows(id) ON DELETE SET NULL,
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- promoted fields (queried / prefilled / dropped into the DOC)
    contact_name  TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    venue         TEXT,                            -- as submitted (snapshot)
    show_date     DATE,
    performers    INTEGER,
    monitors      INTEGER,
    own_iems      BOOLEAN,
    split_snake   TEXT,
    stage_type    TEXT,
    own_engineer  TEXT,
    merch         BOOLEAN,
    band_tent     TEXT,
    large_vehicle BOOLEAN,
    -- the complete raw form response — nothing is ever lost, new questions land here
    data          JSONB NOT NULL DEFAULT '{}'::jsonb,
    source        TEXT NOT NULL DEFAULT 'form',    -- form | manual
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- "newest submission by this band" — the prefill + returning-artist query
CREATE INDEX IF NOT EXISTS idx_submissions_artist ON submissions (artist_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_show   ON submissions (show_id);

CREATE TABLE IF NOT EXISTS files (
    id            SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    artist_id     INTEGER REFERENCES artists(id) ON DELETE CASCADE,
    kind          TEXT,                            -- stage_plot | input_list | other
    filename      TEXT,                            -- original name, verbatim
    stored_name   TEXT,                            -- on-disk name
    nas_path      TEXT,                            -- where it lives on the NAS (once synced)
    mime          TEXT,
    size          INTEGER,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_files_submission ON files (submission_id);
CREATE INDEX IF NOT EXISTS idx_files_artist     ON files (artist_id);

-- events: a bill/day-sheet grouping up to 3 acts (opener / direct support / headliner).
-- The advance form is per-band; the day-sheet DOC is per-event. An event ties
-- band submissions to act slots so doc-fill can populate the three columns.
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    name        TEXT,                              -- e.g. "513 Airwaves w/ Inhailer Radio"
    venue       TEXT,
    event_date  DATE,
    series      TEXT,
    notes       TEXT,
    -- event-level fields from the spreadsheet: event_type, paying_band, mc, dj,
    -- lead_name, lead_phone (and future schedule)
    details     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_events_date ON events (event_date);
ALTER TABLE events ADD COLUMN IF NOT EXISTS details JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS event_acts (
    id            SERIAL PRIMARY KEY,
    event_id      INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    slot          TEXT NOT NULL,                   -- opener | direct_support | headliner
    slot_order    INTEGER NOT NULL,                -- 1,2,3 -> column order in the day-sheet
    artist_id     INTEGER REFERENCES artists(id) ON DELETE SET NULL,
    -- specific submission to fill from; NULL = use the artist's newest
    submission_id INTEGER REFERENCES submissions(id) ON DELETE SET NULL,
    set_time      TEXT,                            -- e.g. "9:00p-10:00p" (from the advance sheet)
    -- band-detail overrides typed into the spreadsheet; win over the form submission
    sheet_fields  JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_event_acts_slot ON event_acts (event_id, slot);
-- for DBs created before these columns existed:
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_time TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS sheet_fields JSONB NOT NULL DEFAULT '{}'::jsonb;

-- keep updated_at honest
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_artists_touch ON artists;
CREATE TRIGGER trg_artists_touch BEFORE UPDATE ON artists
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
DROP TRIGGER IF EXISTS trg_shows_touch ON shows;
CREATE TRIGGER trg_shows_touch BEFORE UPDATE ON shows
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
