-- DigiBot schema. Applied idempotently by the service on startup.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS pages (
  id          SERIAL PRIMARY KEY,
  source      TEXT NOT NULL,            -- 'digico' | 'kb'
  path        TEXT NOT NULL,
  title       TEXT NOT NULL,
  url         TEXT NOT NULL,
  tier        SMALLINT NOT NULL DEFAULT 1,
  content     TEXT NOT NULL,
  content_sha TEXT NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source, path)
);

CREATE TABLE IF NOT EXISTS chunks (
  id         SERIAL PRIMARY KEY,
  page_id    INTEGER REFERENCES pages(id) ON DELETE CASCADE,
  teaching_id INTEGER,                  -- set instead of page_id for teachings
  ord        INTEGER NOT NULL DEFAULT 0,
  section    TEXT NOT NULL DEFAULT '',
  text       TEXT NOT NULL,
  tier       SMALLINT NOT NULL DEFAULT 1,
  figures    TEXT[] NOT NULL DEFAULT '{}',
  embedding  vector(384),
  tsv        tsvector GENERATED ALWAYS AS (to_tsvector('english', section || ' ' || text)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS chunks_page_idx ON chunks (page_id);
CREATE INDEX IF NOT EXISTS chunks_emb_idx ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS teachings (
  id          SERIAL PRIMARY KEY,
  text        TEXT NOT NULL,
  question    TEXT,                     -- the thread's root question, if any
  taught_by   TEXT NOT NULL,            -- slack user id
  slack_link  TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  folded      BOOLEAN NOT NULL DEFAULT false   -- true once Brian moved it into a real wiki page
);

CREATE TABLE IF NOT EXISTS gaps (
  id          SERIAL PRIMARY KEY,
  question    TEXT NOT NULL,
  reason      TEXT,
  asked_by    TEXT,
  channel     TEXT,
  ts          TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  reported    BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS qa_log (
  id          SERIAL PRIMARY KEY,
  channel     TEXT,
  ts          TEXT,                     -- the asker's message ts
  reply_ts    TEXT,                     -- the bot's reply ts (set by n8n after posting)
  asked_by    TEXT,
  question    TEXT NOT NULL,
  answer      TEXT,
  model       TEXT,
  chunk_ids   INTEGER[] NOT NULL DEFAULT '{}',
  tool_calls  JSONB NOT NULL DEFAULT '[]',
  tokens_in   INTEGER,
  tokens_out  INTEGER,
  latency_ms  INTEGER,
  feedback    TEXT,                     -- 'up' | 'down'
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (channel, ts)
);

CREATE TABLE IF NOT EXISTS seen_events (
  key         TEXT PRIMARY KEY,         -- channel:ts or reaction key
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
