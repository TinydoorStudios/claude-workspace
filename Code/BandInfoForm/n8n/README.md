# n8n — Advance Follow-up Check (SUPERSEDED 2026-09-03 — deactivated, kept for record)

Old daily workflow (9am) that drove the follow-up loop off days-since-email-sent
(10 days). Replaced by **Advance Lifecycle Check** below, which is date-driven off
the show date instead. Deactivated in n8n (`active=false`), not deleted — the app
endpoint it called (`/internal/run-followups`) and `followup_queue` table are still
in the codebase, just unused by anything live now.

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

# n8n — Advance Lifecycle Check (2026-09-03)

Two date-driven guardrails, Brian's rule verbatim: the **initial advance drafts
itself 21 days out** from the show date (whichever comes first — a normal-lead-time
booking hits the 21-day mark, or a late booking is already inside the window the
first time this runs); the **follow-up drafts itself if nothing's heard back by 7
days out** from the show — asking them to fill out the "performance details," not
tied to when the initial went out. Both are **drafts only** (Gmail, unsent — a human
reviews and sends), plus **one summary email to Brian** listing what's ready,
whenever anything was drafted (silent on a day with nothing due).

The **6-month cross-venue returning-artist check already applies automatically** —
the initial advance reuses `draft_emails.py` wholesale (same NEW/RETURNING logic,
venue blocks, short link, bill grouping), nothing new needed there.

- Workflow: `advance_lifecycle.json` (id `advance-lifecycle`, token placeholdered).
  Daily 9am → `POST /internal/advance-lifecycle` (token-protected) → the app
  queries `advance_db.shows_due_for_initial_advance` /
  `shows_due_for_followup`, batch-renders the initial drafts through
  `draft_emails.py`, builds the follow-up copy inline (reusing the same
  `/s/<code>` short-link mechanism), marks each show's
  `advance_draft_created_at` / `followup_draft_created_at`, and returns
  `{initial: [...], followup: [...]}` as `{to, subject, body}`. n8n loops each
  into a **Gmail draft** (resource `draft`, operation `create` — same
  `3CDCProduction@gmail.com` credential as everything else here), then sends
  **one** "ready to send" summary to `blloyd@3cdc.org`.
- **Guardrail found in testing:** a late-booked show (already inside both the
  21-day and 7-day windows on day one) must NOT get an initial advance and a
  follow-up in the same run — reads as following up on something just sent.
  `shows_due_for_followup` requires `advance_draft_created_at IS NOT NULL`, so a
  late-booked show gets its initial this run and only qualifies for a follow-up
  on a later run. Verified with three synthetic cases (normal, already-advanced
  due for follow-up, late-booked) — each landed in exactly the right bucket.
- **Docker networking gotcha:** the HTTP Request node must call the VM's real LAN
  IP (`http://192.168.200.84:8097/...`), not `localhost:8097` — inside the n8n
  container, `localhost` is the container's own loopback, not the VM host's, so
  `localhost:8097` gets `ECONNREFUSED`. The app is bound `0.0.0.0` so the LAN IP
  reaches it fine; this is unrelated to (and doesn't change) the earlier
  Advance-Notify gotcha, which is the opposite direction (app → n8n) and needed
  `localhost:5678` specifically to dodge Cloudflare's bot protection on the
  public tunnel — same lesson (internal, same-VM traffic should stay off any
  public hostname), opposite fix.
- Schema: `shows.advance_draft_created_at` / `followup_draft_created_at`
  (new columns); `advance_status` view rebuilt (state values now `queued` /
  `awaiting` / `followup_due` / `followup_drafted` / `responded` — replaces the
  old `followup_sent`). `status_sheet.py` / `merge_status.py` updated to match
  ("Email Sent" column renamed "Advance Drafted," sourced from the new column).
- Import: same pattern as above. Tested via a temporary Webhook-trigger swap
  (Schedule Trigger nodes can't be fired externally to test; swap in a Webhook
  node with the same downstream wiring, curl it, swap back) — not something to
  repeat casually, but useful if this workflow needs surgery again.
