-- 3CDC Band Advancing — Postgres schema
-- Runs inside the Postgres 16 already on the n8n VM (/opt/n8n docker compose).
-- Create a dedicated database so it never tangles with n8n's own tables:
--
--   sudo docker compose -f /opt/n8n/docker-compose.yml exec -T postgres \
--     psql -U <pguser> -c "CREATE DATABASE advancing;"
--   ... then pipe this file into it:
--   sudo docker compose -f /opt/n8n/docker-compose.yml exec -T postgres \
--     psql -U <pguser> -d advancing < schema.sql
--
-- (The deploy .command in this folder does both for you.)

-- Booked shows = the no-band-gets-missed reference list.
-- Pre-loaded (per booking) so the reminder job knows what SHOULD come back.
CREATE TABLE IF NOT EXISTS shows (
  id           SERIAL PRIMARY KEY,
  act          TEXT NOT NULL,
  venue        TEXT NOT NULL,
  show_date    DATE,
  contact_email TEXT,
  status       TEXT NOT NULL DEFAULT 'Not sent',   -- Not sent | Sent | Received | Complete | Follow-up
  advance_doc  TEXT,                                -- Dropbox link to the generated .docx
  notes        TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Raw form submissions. One row per submit; full payload kept in `raw` for replay.
CREATE TABLE IF NOT EXISTS submissions (
  id            SERIAL PRIMARY KEY,
  show_id       INTEGER REFERENCES shows(id) ON DELETE SET NULL,
  submitted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  email         TEXT,
  venue         TEXT,
  act           TEXT,
  show_date     TEXT,
  contact_name  TEXT,
  dayof_phone   TEXT,
  performers    INTEGER,
  large_vehicle TEXT,
  stageplot_link TEXT,
  monitor_needs TEXT,
  own_engineer  TEXT,
  selling_merch TEXT,
  private_tent  TEXT,
  wristbands    INTEGER,
  escort_rep    TEXT,
  special_guests TEXT,
  notes         TEXT,
  acks          JSONB,          -- {"CONTENT": true, "SOUND": true, ...}
  raw           JSONB,          -- the entire posted payload
  advance_doc   TEXT            -- Dropbox link, filled after the docx service runs
);

CREATE INDEX IF NOT EXISTS idx_submissions_show   ON submissions(show_id);
CREATE INDEX IF NOT EXISTS idx_submissions_email  ON submissions(lower(email));
CREATE INDEX IF NOT EXISTS idx_shows_status       ON shows(status);

-- Convenience view for the tracker dashboard.
CREATE OR REPLACE VIEW tracker AS
SELECT s.id, s.act, s.venue, s.show_date, s.status, s.advance_doc,
       s.contact_email, s.updated_at,
       (SELECT max(sub.submitted_at) FROM submissions sub WHERE sub.show_id = s.id) AS last_submission
FROM shows s
ORDER BY s.show_date NULLS LAST;
