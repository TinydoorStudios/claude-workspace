-- FSQ parking digest (Brian, 2026-09-15, step 2): replaces the per-
-- submission draft (built and live-tested earlier the same day) with a
-- once-a-day email that only sends when there's something to report. A
-- band's parking numbers land here at /submit time and sit until the next
-- daily digest run picks them up and marks them delivered — see
-- advance_db.queue_fsq_parking / undelivered_fsq_parking /
-- mark_fsq_parking_delivered and app.py's /internal/fsq-parking-digest.
--
-- A full snapshot is stored here rather than joined against shows/
-- submissions at digest time, so a later edit or purge of the show can't
-- change what already went out, or silently drop a pending item.
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
