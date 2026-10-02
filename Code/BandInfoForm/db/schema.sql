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
--
-- Every migration in db/migrations/ is also folded in here in the same commit, so this
-- file alone bootstraps a working DB. deploy_app.command still runs every migration on
-- each deploy; both paths must stay idempotent. (2026-09-21 sweep: DBB-10)

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
-- 2026-09-24 research #12: staff-only post-show note. artists.notes above was
-- already there and unwritten — it becomes the free-text note; advance_rating is
-- the 1–5 "advance accuracy" pip beside it. Both render on the gated /artist page
-- and the internal Needs-you rows only, never in anything a band receives.
ALTER TABLE artists ADD COLUMN IF NOT EXISTS advance_rating SMALLINT;
DO $$ BEGIN
    ALTER TABLE artists ADD CONSTRAINT artists_advance_rating_range
        CHECK (advance_rating IS NULL OR advance_rating BETWEEN 1 AND 5);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS shows (
    id            SERIAL PRIMARY KEY,
    artist_id     INTEGER NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    venue         TEXT,
    show_series   TEXT,
    show_date     DATE,
    -- pipeline state lives in the advance_status view (below), computed live
    -- from these timestamps + whether a submission exists — removed 2026-09-09,
    -- was a static column nothing kept in sync (stuck at its insert-time
    -- default forever; the real state was never actually read from here)
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
    name        TEXT,                              -- e.g. "513 Airwaves w/ Inhaler Radio"
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
    slot          TEXT,                            -- legacy (opener | direct_support | headliner); nothing writes it since 2026-09-15 (artist-order)
    slot_order    INTEGER,                         -- legacy (1,2,3); nothing writes it since 2026-09-15 (artist-order)
    artist_id     INTEGER REFERENCES artists(id) ON DELETE SET NULL,
    -- specific submission to fill from; NULL = use the artist's newest
    submission_id INTEGER REFERENCES submissions(id) ON DELETE SET NULL,
    set_time      TEXT,                            -- e.g. "9:00p-10:00p" (from the advance sheet)
    -- band-detail overrides typed into the spreadsheet; win over the form submission
    sheet_fields  JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 2026-09-15 (artist-order): an act is identified by its artist, not a slot name.
DROP INDEX IF EXISTS uq_event_acts_slot;
CREATE UNIQUE INDEX IF NOT EXISTS uq_event_acts_artist ON event_acts (event_id, artist_id);
-- for DBs created before these columns existed:
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_time TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS sheet_fields JSONB NOT NULL DEFAULT '{}'::jsonb;
-- 2026-09-15 (artist-order): per-act schedule; slot/slot_order kept as history only.
-- DROP NOT NULL is a no-op on an already-nullable column. The backfill UPDATE
-- stays in db/migrations/2026-09-15-artist-order.sql only.
ALTER TABLE event_acts ALTER COLUMN slot       DROP NOT NULL;
ALTER TABLE event_acts ALTER COLUMN slot_order DROP NOT NULL;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_start  TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS set_end    TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS load_in    TEXT;
ALTER TABLE event_acts ADD COLUMN IF NOT EXISTS soundcheck TEXT;

-- advance lifecycle timestamps (email_sent_at already exists above)
ALTER TABLE shows ADD COLUMN IF NOT EXISTS responded_at   TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS followup_sent_at TIMESTAMPTZ;

-- Date-driven lifecycle (Brian, 2026-09-03): the initial advance drafts itself
-- 3 weeks (21 days) out from the show; the follow-up drafts itself if nothing's
-- heard back by 7 days out from the show. Both are DRAFTS (Gmail), never auto-
-- sent — email_sent_at/followup_sent_at stay for whenever real send-tracking
-- (Outlook) gets built; these new columns track the draft step, which is what
-- actually happens today.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS advance_draft_created_at  TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS followup_draft_created_at TIMESTAMPTZ;

-- Draft-early / hold-for-send (Brian, 2026-09-03): the initial advance now
-- drafts itself as soon as a booking is seeded (no date ceiling — see
-- shows_due_for_initial_advance) instead of waiting for the 21-day mark. The
-- 21-day mark becomes a SEND reminder to Brian that a draft already sitting
-- in Gmail is ready to go out — still never auto-sent. Fires once per show.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS send_reminder_sent_at TIMESTAMPTZ;

-- Multi-tier reminder cadence (Brian, 2026-09-10): the single follow-up at
-- 7 days out became four — 7/3/2/1 days before the show, each firing once,
-- independently, as long as the band still hasn't responded. One row per
-- (show, tier) fired, so each tier gates itself instead of the old single
-- followup_draft_created_at column (kept below for backward compat — it
-- still gets stamped on whichever tier fires FIRST, so status_log.py /
-- status_sheet.py / the advance_status view need no changes at all).
CREATE TABLE IF NOT EXISTS advance_reminders (
    id           SERIAL PRIMARY KEY,
    show_id      INTEGER NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
    days_before  INTEGER NOT NULL,
    drafted_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(show_id, days_before)
);

-- Live-send migration (Brian, 2026-09-13): cadence trimmed 7/3/2/1 -> 7/3/1
-- (see advance_db.FOLLOWUP_TIERS), and a row here no longer always means
-- "actually sent" — `sent` distinguishes a genuine send from a tier
-- resolved with nothing to do: no email on file, or pre-skipped as
-- already-stale relative to when the show was booked
-- (mark_stale_followup_tiers_skipped). Historical rows all default true —
-- they really were drafted/sent under the pre-migration system.
ALTER TABLE advance_reminders ADD COLUMN IF NOT EXISTS sent BOOLEAN NOT NULL DEFAULT true;
-- 2026-09-24 research #3/#4: the ladder is 10/7/3/1, and days_before = 7 no
-- longer means a reminder — it means the week-out CONFIRMED SCHEDULE email,
-- which goes to every show at seven days whether or not the band answered
-- (advance_db.SCHEDULE_TIER / mark_schedule_sent). Deliberately no new table
-- and no `kind` column: reusing this row's UNIQUE(show_id, days_before) is
-- what guarantees the schedule and the old tier-7 chase can never both go
-- out. `sent` keeps its meaning, and a show that had already answered gets a
-- row here without shows.followup_draft_created_at being stamped.

-- Dead column removed (Brian, 2026-09-09): nothing kept it in sync with
-- reality (stamp_email_sent/mark_show_status, the only writers, were either
-- unused or gated behind a --mark-sent flag nothing passes anymore), and
-- nothing downstream ever read it back — the advance_status view below
-- computes the real live state from timestamps + submissions instead.
ALTER TABLE shows DROP COLUMN IF EXISTS status;

-- Finalized sign-off (Brian, 2026-09-13): the point after a band has responded
-- where a human reviews everything and confirms the advance is fully done.
-- Distinct from responded_at — a show can sit "responded" (now labeled
-- "Advancing In Progress") for a while before anyone signs off. See
-- advance_status below (checked ahead of 'responded' — finalized only ever
-- follows a response) and app.py's POST /artist/<id>/finalize/<show_id>.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS finalized_at TIMESTAMPTZ;

-- One row per advance (band + show) with its computed state, for n8n's daily
-- checks and the status report. DROP first — CREATE OR REPLACE can't insert a
-- column ahead of existing ones, only append at the end.
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
    (SELECT max(sub.submitted_at) FROM submissions sub WHERE sub.show_id = s.id)
                    AS last_submission,
    CASE
        WHEN s.finalized_at IS NOT NULL THEN 'finalized'
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
JOIN artists a ON a.id = s.artist_id;

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

-- staff booking intake (short gated form). Seeds the master spreadsheet on the
-- next generate: unseeded rows are appended as sheet rows, then stamped seeded.
-- Mirrors the sheet's EVENT + ACT columns; band-detail fields stay the band's job.
CREATE TABLE IF NOT EXISTS bookings (
    id            SERIAL PRIMARY KEY,
    event_name    TEXT,
    event_date    DATE,
    venue         TEXT,
    -- WP-only sub-venue (Main Stage | Porch | Bandstand) — see forms_config.WP_LOCATIONS.
    -- Blank for every other venue.
    location      TEXT,
    series        TEXT,
    event_type    TEXT,
    paying_band   TEXT,
    lead_name     TEXT,
    lead_phone    TEXT,
    load_in       TEXT,
    soundcheck    TEXT,
    event_start   TEXT,
    event_end     TEXT,
    curfew        TEXT,
    slot          TEXT,
    set_time      TEXT,
    artist_name   TEXT,
    contact_name  TEXT,
    contact_email TEXT,
    email_note    TEXT,
    entered_by    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    seeded_at     TIMESTAMPTZ
);
-- for DBs created before this column existed:
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS location TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS foh_console TEXT;  -- FSQ: DiGiCo Quantum 225 | iPad
-- staff-entered contact name (Brian, 2026-09-09): carries into the band's own
-- advance form as an editable starting value — see /f/<token> prefill in
-- app.py and _token() in draft_emails.py. contact_email already existed.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS contact_name TEXT;

-- Manual-entry bookings (Brian, 2026-09-13): a band that emailed its info
-- directly instead of using the form. Staff checks this at /booking time so
-- the automated welcome/initial-advance email never goes out for this show
-- (pointless — staff is about to fill in the band's own form by hand with
-- what was emailed) while the rest of the pipeline (sheet seed, docfill,
-- dashboard) still runs normally. Read by shows_due_for_initial_advance via
-- its existing bookings LEFT JOIN — permanent for this booking, not a
-- one-time suppression that could be raced by the immediate on-booking
-- trigger. See app.py's /booking route and the "Manual band entry" note in
-- ARCHITECTURE.md.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS skip_welcome_email BOOLEAN NOT NULL DEFAULT false;

-- Bands on the bill (Brian, 2026-09-08): declared explicitly per booking so a
-- multi-band bill entered one act at a time (band 1 today, band 2 next week)
-- still knows it's multi-band on day one, instead of inferring from however
-- many booking rows happen to exist yet. Drives (1) dropping "please take set
-- breaks as needed" from the email for anything >1, (2) the day-sheet
-- template's act-count. NULL = not specified, falls back to the old inferred
-- behavior (see draft_emails.py / daysheet.py).
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS band_count INTEGER;

-- 2026-09-21 sweep (IDENT-3): {artist_name, venue, event_date} the booking's
-- sheet row was last written under — edited_bookings finds the row by it.
-- Backfill lives in db/migrations/2026-09-21-bookings-sheet-ident.sql.
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS sheet_ident JSONB;

-- Advance recap extraction (Brian, 2026-09-07): 3 days after a show, an n8n
-- job (2am daily) converts the filed advance .docx to PDF + MD (saved next to
-- the .docx in the Dropbox venue tree) and stores the parsed recap here, so
-- the 6-month returning-artist email can pull final show info without
-- re-parsing a Word document at draft time — and without depending on
-- events/event_acts, which package_run.py truncates + rebuilds from the live
-- sheet on every run (a working model, not a history; this table IS the
-- durable one). UNIQUE(show_id) makes the nightly sweep idempotent.
CREATE TABLE IF NOT EXISTS advance_recaps (
    id           SERIAL PRIMARY KEY,
    show_id      INTEGER UNIQUE REFERENCES shows(id) ON DELETE CASCADE,
    artist_id    INTEGER REFERENCES artists(id) ON DELETE CASCADE,
    venue        TEXT,
    show_date    DATE,
    source_docx  TEXT,                        -- filename of the advance this was extracted from
    md_path      TEXT,                        -- relative to the Dropbox Nyquist/ root
    pdf_path     TEXT,                        -- relative to the Dropbox Nyquist/ root; NULL if conversion failed
    recap        JSONB NOT NULL DEFAULT '[]'::jsonb,  -- [[label, value], ...] — same shape daysheet.read_filed_advance returns
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_advance_recaps_artist ON advance_recaps (artist_id);

-- short redirect for the /f/<signed-token> prefill link — the signed token is
-- long (venue name + date + series + HMAC signature); emails carry /s/<code>
-- instead, which 302s to the real /f/<token> link. Deterministic per token
-- (hash of the token itself) so re-drafting the same show reuses the same code.
CREATE TABLE IF NOT EXISTS short_links (
    code       TEXT PRIMARY KEY,
    token      TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 2026-09-24 research #11: open tracking. /s/<code> stamps these in the same
-- statement that resolves the code (advance_db.open_short_link) — first hit sets
-- first_opened_at, every hit bumps open_count. show_id is set when the reminder
-- path mints the code and backfilled on first open for the welcome link (whose
-- minter doesn't know it), so the dashboard / digest can say "welcome sent 9/02 ·
-- never opened" per advance. Nothing about the visitor is kept: no IP, no UA,
-- no per-hit rows. SET NULL, not CASCADE — purging a show must not delete a
-- link that still resolves.
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS first_opened_at TIMESTAMPTZ;
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS open_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE short_links ADD COLUMN IF NOT EXISTS show_id INTEGER REFERENCES shows(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_short_links_show ON short_links (show_id);

-- Internal "hasn't responded" alert to Brian (2026-09-13): a manual-
-- follow-up flag, separate from the band-facing tier reminders in
-- advance_reminders. Fires once per show, the first time it's inside 3
-- days of its date with no response — deliberately NOT gated on the band
-- having an email on file the way the band-facing tier-3 follow-up is
-- (shows_due_for_followup skips those since there's nowhere to send it;
-- this alert is for Brian, so a band with no email qualifies too — if
-- anything he needs to know about those MORE, since automated follow-up
-- can't even reach them). See advance_db.shows_due_for_unresponded_alert.
ALTER TABLE shows ADD COLUMN IF NOT EXISTS unresponded_alert_sent_at TIMESTAMPTZ;

-- Vehicle count (Brian, 2026-09-13): paired with the existing large_vehicle
-- yes/no question so a headcount-of-vehicles drives how many parking garage
-- validations to prep per band, instead of that only ever showing up as a
-- free-text note. See form.html's large_vehicle block, fieldspec.BAND_FIELDS,
-- and daysheet.act_row_values' "parking" row.
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS vehicle_count INTEGER;

-- large_vehicle (boolean) replaced by a count, same day (Brian, 2026-09-13):
-- a bill's vehicles aren't all-or-nothing — 1 large + 1 standard is a real
-- case a Yes/No can't represent. large_vehicle stays on old submissions for
-- history; nothing new writes it going forward, only large_vehicle_count.
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS large_vehicle_count INTEGER;

-- 2026-09-24 research #(b): trailer + crew_count (db/migrations/2026-09-24-
-- trailer-crew-count.sql). A van towing a trailer is ONE vehicle in the counts
-- above, so the count alone never said it can't use the 6 ft 8 in FSQ garage.
-- crew_count is ADDITIVE to performers, not a subset — performers stays the
-- on-stage count; the day sheet's drink tix = (performers + crew) x 2.
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS trailer BOOLEAN;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS crew_count INTEGER;

-- ═════════════════════════════════════════════════════════════════════════
-- 2026-09-13 QC audit fixes (see Handoffs/band-advance-audit-decisions-2026-09-13.md)
-- ═════════════════════════════════════════════════════════════════════════

-- #1/#2: registry of every filed advance doc the pipeline created or adopted.
-- Docs are never overwritten; lookups go through here, not filename sort order.
CREATE TABLE IF NOT EXISTS filed_docs (
    id          SERIAL PRIMARY KEY,
    venue       TEXT NOT NULL,
    event_date  DATE NOT NULL,
    event_key   TEXT NOT NULL,            -- normalized event name (or series)
    path        TEXT NOT NULL,            -- relative to the Dropbox root
    sha256      TEXT,                     -- hash of what the PIPELINE last wrote
    written_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    seeded      BOOLEAN NOT NULL DEFAULT false,  -- adopted an existing file, not written by us
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (venue, event_date, event_key)
);

-- #1: "doc says X, new info says Y" notices — stored once, emailed once.
CREATE TABLE IF NOT EXISTS doc_notices (
    id          SERIAL PRIMARY KEY,
    venue       TEXT NOT NULL DEFAULT '',
    event_date  DATE,
    event_key   TEXT NOT NULL DEFAULT '',
    kind        TEXT NOT NULL DEFAULT 'diff',
    field       TEXT NOT NULL DEFAULT '',
    new_value   TEXT NOT NULL DEFAULT '',
    doc_value   TEXT,
    detail      TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at TIMESTAMPTZ,
    UNIQUE (venue, event_date, event_key, kind, field, new_value)
);

-- #4: cancel / hold / merge; #14: thank-you record
ALTER TABLE shows ADD COLUMN IF NOT EXISTS cancelled_at      TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS held_at           TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS hold_reason       TEXT;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS hold_notified_at  TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS hold_dismissed_at TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS thankyou_sent_at  TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS thankyou_error    TEXT;

-- #3: a failed/blocked send, alerted to Brian at most once per show per kind per day
CREATE TABLE IF NOT EXISTS send_failures (
    id          SERIAL PRIMARY KEY,
    show_id     INTEGER REFERENCES shows(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL,            -- welcome | followup_<n> | thankyou | ...
    error       TEXT,
    day         DATE NOT NULL DEFAULT CURRENT_DATE,
    notified_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (show_id, kind, day)
);

-- #21: when did the scheduled 9am lifecycle check actually run
CREATE TABLE IF NOT EXISTS job_runs (
    id      SERIAL PRIMARY KEY,
    job     TEXT NOT NULL,
    source  TEXT,
    ran_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_job_runs_job ON job_runs (job, ran_at DESC);

-- #13: staff gate attempts (rate limit shared across every worker)
CREATE TABLE IF NOT EXISTS gate_attempts (
    id           SERIAL PRIMARY KEY,
    ip           TEXT NOT NULL,
    ok           BOOLEAN NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_gate_attempts_ip ON gate_attempts (ip, attempted_at DESC);
CREATE TABLE IF NOT EXISTS gate_lockouts (
    ip          TEXT PRIMARY KEY,
    locked_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at TIMESTAMPTZ
);

-- #6: a submission whose band name didn't match its booking
CREATE TABLE IF NOT EXISTS submission_matches (
    id              SERIAL PRIMARY KEY,
    submission_id   INTEGER REFERENCES submissions(id) ON DELETE CASCADE,
    booked_show_id  INTEGER REFERENCES shows(id) ON DELETE SET NULL,
    typed_name      TEXT,
    venue           TEXT,
    show_date       DATE,
    status          TEXT NOT NULL,        -- attached_auto | pending_pick | confirmed | detached | attached_manual
    candidates      JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    notified_at     TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ
);

-- #4/#17: status view with cancelled + on-hold states
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
JOIN artists a ON a.id = s.artist_id;

-- ═════════════════════════════════════════════════════════════════════════
-- 2026-09-14 review pass (Handoffs/band-advance-review-2026-09-13.md)
-- ═════════════════════════════════════════════════════════════════════════

-- H1: one booking row per band/venue/date (a twin row made the lifecycle send twice)
CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_ident
    ON bookings (venue, event_date, (lower(btrim(regexp_replace(artist_name, '\s+', ' ', 'g')))));

-- H2: per-cell provenance — what the pipeline last wrote into each doc cell.
-- A cell still equal to this is the pipeline's to update; anything else is a
-- hand edit and is never touched.
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS cells JSONB NOT NULL DEFAULT '{}'::jsonb;

-- M6: a failure already emailed in the last 7 days is suppressed, not re-sent daily
ALTER TABLE send_failures ADD COLUMN IF NOT EXISTS suppressed BOOLEAN NOT NULL DEFAULT false;

-- E5: automatic day-before confirmation to every responded show
ALTER TABLE shows ADD COLUMN IF NOT EXISTS dayahead_sent_at TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS dayahead_error   TEXT;

-- E1: things for Brian that ride the 7am digest instead of their own email
CREATE TABLE IF NOT EXISTS digest_items (
    id           SERIAL PRIMARY KEY,
    kind         TEXT NOT NULL,
    subject      TEXT NOT NULL,
    html         TEXT NOT NULL,
    link         TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    delivered_at TIMESTAMPTZ
);

-- Booking edit tracking + "info changed" notification to the band (Brian,
-- 2026-09-14): an edit to a logged booking's band-facing fields (date,
-- venue, location, artist name, slot, set time, load-in/soundcheck/start/
-- end/curfew), on a show still inside the 21-day window, queues one email —
-- sent at the NEXT daily lifecycle run, never immediately. Several edits
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
CREATE UNIQUE INDEX IF NOT EXISTS uq_booking_edits_pending
    ON booking_edits (booking_id) WHERE notify AND sent_at IS NULL;

-- advance_status view gains booking_id so the dashboard can link each act to
-- its bookings row for the new "Edit booking" button. DROP first — CREATE OR
-- REPLACE can't insert a column ahead of existing ones, only append.
--
-- BUG (found 2026-09-15, live dashboard; re-found stale in schema.sql itself
-- 2026-09-16 audit db-P1): this rewrite had dropped cancelled_at/held_at/
-- thankyou_sent_at/thankyou_error and, with them, the 'cancelled'/'held'
-- WHEN branches #4/#17 above had added — a full schema.sql apply (e.g. the
-- now-retired deploy_recap_extraction.command) would have reinstated this
-- regressed view on live. Restored from db/migrations/2026-09-14-booking-edits.sql,
-- keeping this migration's booking_id column.
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

-- ── folded in from db/migrations/ 2026-09-14-doc-review .. 2026-09-16-submit-rate-limit (2026-09-22)
-- 2026-09-21 sweep (DBB-10): this file had drifted ten migrations behind, so a bootstrap
-- from it alone broke add_act/insert_booking. DDL only, verbatim; each migration file
-- keeps its own comments and any data backfill. drop-dead-code needs nothing here.

-- 2026-09-14-doc-review
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS cell_key     TEXT;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS resolved_at  TIMESTAMPTZ;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS resolution   TEXT;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS apply_requested_at TIMESTAMPTZ;
ALTER TABLE doc_notices ADD COLUMN IF NOT EXISTS apply_error  TEXT;
CREATE INDEX IF NOT EXISTS idx_doc_notices_open ON doc_notices (venue, event_date) WHERE resolved_at IS NULL;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS doc_checked_at TIMESTAMPTZ;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS doc_check      TEXT;

-- 2026-09-14-third-party-emails
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS band_emails BOOLEAN NOT NULL DEFAULT false;

-- 2026-09-15-artist-order: folded into the event_acts block near the top of this file.

-- 2026-09-15-draft-only
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS draft_only BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS advance_held_draft_at TIMESTAMPTZ;
ALTER TABLE shows ADD COLUMN IF NOT EXISTS parking_sheet_sent_at TIMESTAMPTZ;

-- 2026-09-15-fsq-parking-queue
CREATE TABLE IF NOT EXISTS fsq_parking_queue (
    id                   SERIAL PRIMARY KEY,
    artist_id            INTEGER REFERENCES artists(id) ON DELETE SET NULL,
    show_id              INTEGER REFERENCES shows(id) ON DELETE SET NULL,
    band                 TEXT NOT NULL,
    venue                TEXT NOT NULL,
    show_date            DATE,
    contact_name         TEXT,
    contact_email        TEXT,
    contact_phone        TEXT,
    vehicle_count        INTEGER,
    large_vehicle_count  INTEGER,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    digested_at          TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_fsq_parking_queue_pending
    ON fsq_parking_queue (digested_at) WHERE digested_at IS NULL;
-- 2026-09-24 research #(b): the queue is a stored SNAPSHOT, not a live join, so
-- the trailer flag has to be captured with the counts to reach Mtully's digest.
ALTER TABLE fsq_parking_queue ADD COLUMN IF NOT EXISTS trailer BOOLEAN;

-- 2026-09-15-sheet-writeback
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS sheet_dirty BOOLEAN NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS idx_bookings_sheet_dirty ON bookings (sheet_dirty)
    WHERE sheet_dirty;
-- 2026-09-21-sheet-dirty-fields: only these are written back (empty = whole row)
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS sheet_dirty_fields TEXT[] NOT NULL DEFAULT '{}';

-- 2026-09-16-doc-provenance
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS columns JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE filed_docs ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;

-- 2026-09-16-sheet-removals
CREATE TABLE IF NOT EXISTS sheet_removals (
    id           SERIAL PRIMARY KEY,
    venue        TEXT NOT NULL,
    event_date   DATE NOT NULL,
    match_key    TEXT NOT NULL,             -- artists.match_key of the removed act
    artist_name  TEXT,                      -- display name, for logs only
    reason       TEXT NOT NULL DEFAULT 'purge',   -- purge | merge | doc_retire (match_key '', doc only)
    doc_path     TEXT,                      -- relative to the Dropbox root
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_sheet_removals_pending
    ON sheet_removals (venue, event_date, match_key) WHERE applied_at IS NULL;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS synced_at TIMESTAMPTZ;

-- 2026-09-16-submit-rate-limit
CREATE TABLE IF NOT EXISTS submit_attempts (
    id           SERIAL PRIMARY KEY,
    ip           TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_submit_attempts_ip ON submit_attempts (ip, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_submit_attempts_time ON submit_attempts (attempted_at DESC);
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
