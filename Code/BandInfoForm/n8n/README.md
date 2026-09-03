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

# n8n — Advance Notify (2026-09-03)

Fires a quick-glance summary email whenever a staff booking is logged (`/booking`)
or a band completes the advance form (`/submit`). The Flask app POSTs the event to
this workflow's webhook (best-effort, never blocks the request it came from); the
workflow checks a shared-secret header, formats a short HTML summary, and sends it
via Gmail — reusing the existing `3CDCProduction@gmail.com` OAuth2 credential (the
same one the SPL Nightly Summary Email workflow already uses). Recipient is
`blloyd@3cdc.org`, hardcoded in the Gmail node — change there if that should move.

- Workflow: `advance_notify.json` (id `advance-notify`, token placeholdered same as
  above — the live copy carries the real `ADVANCE_INTERNAL_TOKEN`).
- Webhook path: `advance-notify`, POST only. **Called from `localhost:5678`, not
  the public `n8n.tinydoorstudios.com` tunnel** — Cloudflare's bot protection 403s
  server-to-server calls through the tunnel (Python's default User-Agent reads as
  a bot). `ADVANCE_NOTIFY_URL` in `advance.env` is
  `http://localhost:5678/webhook/advance-notify`, since the Flask app and n8n run
  on the same VM.
- Import: same as above — `docker cp` into the container, `n8n import:workflow`,
  `n8n publish:workflow --id=advance-notify`, restart n8n.
- App-side wiring: `app/app.py` — `_notify_email(event_type, fields)`, called from
  `/booking` (event_type "booking") and `/submit` (event_type "submission").
  `ADVANCE_NOTIFY_URL` env var; empty/unset = notify silently skipped (same
  best-effort pattern as the existing Slack stub).
