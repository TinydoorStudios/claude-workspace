-- Gear Tickets — ledger of record
-- Runs in the Postgres that already lives in the n8n compose stack on 192.168.200.84.
-- Monday is the working queue; THIS is the permanent record. Nothing here is ever deleted.

CREATE DATABASE tickets;
\c tickets

CREATE TABLE IF NOT EXISTS tickets (
    id              BIGSERIAL PRIMARY KEY,
    ticket_id       TEXT UNIQUE NOT NULL,        -- TDS-0001, human-facing key
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- what the submitter actually typed
    raw_description TEXT NOT NULL,
    raw_venue       TEXT,                        -- from the QR param, before normalising
    submitter_name  TEXT,
    submitter_phone TEXT,
    submitter_email TEXT,

    -- what the agent decided
    title           TEXT,                        -- cleaned-up one-liner used as the Monday item name
    venue           TEXT,                        -- normalised: Fountain Square, Washington Park, ...
    category        TEXT,                        -- Damaged Gear | Missing Gear | Showfile Issue | Venue / Facility | Vehicle | Supplies / Restock | Other
    severity        TEXT,                        -- Show-stopper | Fix before next use | Annoying but working | Note for the record
    gear_item       TEXT,                        -- best guess at the specific piece of gear
    troubleshooting TEXT,                        -- what the reporter already tried, so nobody starts from scratch
    duplicate_of    TEXT REFERENCES tickets(ticket_id),
    triage_notes    TEXT,
    triaged_at      TIMESTAMPTZ,
    triage_model    TEXT,                        -- which model made the call, for when it gets one wrong

    -- workflow state
    status          TEXT NOT NULL DEFAULT 'new', -- new | open | blocked | resolved
    resolved_at     TIMESTAMPTZ,
    resolution      TEXT,

    -- link out
    monday_item_id  TEXT,
    monday_synced_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS tickets_status_idx   ON tickets(status);
CREATE INDEX IF NOT EXISTS tickets_venue_idx    ON tickets(venue);
CREATE INDEX IF NOT EXISTS tickets_created_idx  ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS tickets_monday_idx   ON tickets(monday_item_id);


-- Every photo. Originals stay on the VM forever; Monday only ever gets a link
-- or a compressed copy, so the 500MB Monday storage cap never becomes a problem.
CREATE TABLE IF NOT EXISTS ticket_photos (
    id            BIGSERIAL PRIMARY KEY,
    ticket_id     TEXT NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    seq           INT NOT NULL,                  -- 1, 2, 3... order they were uploaded
    filename      TEXT NOT NULL,
    stored_path   TEXT NOT NULL,                 -- /opt/gear-tickets/photos/TDS-0001/1.jpg
    public_url    TEXT,
    mime_type     TEXT,
    bytes         BIGINT,
    width         INT,
    height        INT,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (ticket_id, seq)
);

CREATE INDEX IF NOT EXISTS photos_ticket_idx ON ticket_photos(ticket_id);


-- Append-only audit log. Every state change, every agent decision, every sync.
-- This is what the nightly reconcile compares Monday against.
CREATE TABLE IF NOT EXISTS ticket_events (
    id          BIGSERIAL PRIMARY KEY,
    ticket_id   TEXT NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor       TEXT NOT NULL,                   -- 'form' | 'agent' | 'monday' | 'brian' | 'reconcile'
    event       TEXT NOT NULL,                   -- submitted | triaged | pushed_to_monday | status_changed | photo_added | nudged | resolved | reconciled
    detail      JSONB
);

CREATE INDEX IF NOT EXISTS events_ticket_idx ON ticket_events(ticket_id, at DESC);
CREATE INDEX IF NOT EXISTS events_at_idx     ON ticket_events(at DESC);


-- Sequence for the human-facing ticket key.
CREATE SEQUENCE IF NOT EXISTS ticket_seq START 1;

CREATE OR REPLACE FUNCTION next_ticket_id() RETURNS TEXT AS $$
    SELECT 'TDS-' || LPAD(nextval('ticket_seq')::TEXT, 4, '0');
$$ LANGUAGE SQL;


-- Keep updated_at honest.
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tickets_touch ON tickets;
CREATE TRIGGER tickets_touch BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();


-- What's actually in front of Brian right now.
CREATE OR REPLACE VIEW open_tickets AS
SELECT t.ticket_id,
       t.title,
       t.venue,
       t.category,
       t.severity,
       t.submitter_name,
       t.created_at,
       date_part('day', now() - t.created_at)::INT AS age_days,
       (SELECT count(*) FROM ticket_photos p WHERE p.ticket_id = t.ticket_id) AS photo_count,
       t.monday_item_id
FROM tickets t
WHERE t.status IN ('new', 'open', 'blocked')
  AND t.duplicate_of IS NULL
ORDER BY CASE t.severity
             WHEN 'Show-stopper'         THEN 1
             WHEN 'Fix before next use'  THEN 2
             WHEN 'Annoying but working' THEN 3
             ELSE 4
         END,
         t.created_at;


-- Anything the nightly job should chase: open, untouched, and old enough to matter.
CREATE OR REPLACE VIEW stale_tickets AS
SELECT * FROM open_tickets
WHERE (severity = 'Show-stopper'        AND age_days >= 1)
   OR (severity = 'Fix before next use' AND age_days >= 7)
   OR (severity NOT IN ('Show-stopper', 'Fix before next use') AND age_days >= 30);
