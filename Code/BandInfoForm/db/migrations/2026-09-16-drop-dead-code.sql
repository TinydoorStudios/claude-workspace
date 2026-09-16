-- Dead-code cleanup (audit 2026-09-16 ops #4): followup_queue was replaced
-- by the live-send lifecycle migration (2026-09-13) — nothing writes to it
-- any more (tools/dump_followups.py, its only reader, is deleted in the
-- same batch). Empty on live; dropping it here instead of leaving a stale
-- unused table around.
DROP TABLE IF EXISTS followup_queue;
