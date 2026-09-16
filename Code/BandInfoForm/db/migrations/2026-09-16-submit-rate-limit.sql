-- Rate limit on the public /submit endpoint (audit 2026-09-16 security #7):
-- no throttle existed at all beyond MAX_CONTENT_LENGTH. Every bot POST to
-- the bare public form creates an artist+show+submission, fires Slack + n8n
-- notify email, queues an FSQ parking row, and spawns regen_show.py — real
-- work, not a cheap no-op. Same shape as gate_attempts, a separate table
-- since it's a different endpoint with different limits (5/IP/hour,
-- 60 site-wide/hour vs the gate's 5/IP/15min).
CREATE TABLE IF NOT EXISTS submit_attempts (
    id           SERIAL PRIMARY KEY,
    ip           TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_submit_attempts_ip ON submit_attempts (ip, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_submit_attempts_time ON submit_attempts (attempted_at DESC);
