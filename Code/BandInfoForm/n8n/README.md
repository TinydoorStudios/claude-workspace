# n8n — Advance Follow-up Check

Daily workflow (9am) that drives the follow-up loop. It POSTs to the advance app's
token-protected `/internal/run-followups`, which finds advances that are follow-up
due (emailed, no response, past 10 days) and queues a reminder draft per band into
`followup_queue`. Nothing sends — Brian reviews and sends.

- Workflow: `advance_followup_check.json` (token shown as a placeholder; the live
  copy in n8n carries the real `ADVANCE_INTERNAL_TOKEN`).
- Import: `docker cp` into the n8n container, then `n8n import:workflow`,
  `n8n publish:workflow --id=<id>`, and restart n8n so the schedule registers.
- Connectivity: `advance-db` is attached to the `n8n_default` docker network
  (see db/docker-compose.yml) so n8n reaches Postgres/the app.
- Queued drafts surface on the Mac via `generate.command` -> output/emails/followups/.
