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

## Draft-early / hold-for-send (2026-09-03, same day)

Brian's follow-up rule: **draft the initial advance the moment staff log the
booking**, not at the 21-day mark — the 21-day mark becomes a **send reminder**
instead (still drafts-only; T-21 was never meant to be an auto-send trigger,
see the "Auto-send scope" decision this session). Staying inside the same
architecture, not a new workflow:

- `advance_db.shows_due_for_initial_advance` **dropped its 21-day ceiling** —
  it now drafts any show with no draft yet, whatever the show date is. A
  `shows` row (and its identity data) already exists as soon as the pipeline
  first runs for a booking (`draft_emails.py`'s `upsert_artist`/`upsert_show`,
  called every `run_now.py` run — see `package_run.py`), so the very next
  daily 9am check after a booking picks it up. `/booking`'s POST handler now
  also fires `_run_pipeline_background()` itself (mirroring `/submit`), so
  that first pipeline run — and the `shows` row it creates — happens right
  away instead of waiting for someone to click "Run advance now."
- New guardrail: **`advance_db.shows_due_for_send_reminder(days_out=21)`** —
  shows already drafted whose date has now crossed into the 21-day window,
  reminder not yet sent. Fires once per show (`mark_send_reminder_sent`),
  independent of *when* the draft itself was made.
- `/internal/advance-lifecycle` response gained a third key:
  `send_reminders: [{artist_name, venue, show_date}]` — no `to`/`subject`/
  `body`, since nothing new is drafted here; it's a nudge that a draft already
  sitting in Gmail is ready to send.
- n8n side — **only two things changed, no rewiring**: `Create Draft` got
  `alwaysOutputData: true` (so `Build Summary` still runs on a day with zero
  new initial/follow-up drafts but a non-empty `send_reminders`); `Build
  Summary`'s code now reads `initial`/`followup`/`send_reminders` straight off
  `$('Fetch Due')` instead of filtering `Build Items`' output, adds a "ready to
  send" section, and returns `[]` (silent) when all three are empty. Verified
  the extracted `jsCode` against five scenarios (all empty, keys missing
  entirely, initial+followup only, reminders-only, all three at once) in a
  local Node REPL before touching the live workflow — reminders-only was the
  case that would've silently gone nowhere without the `alwaysOutputData` fix.
- Schema: `shows.send_reminder_sent_at` (new column); `advance_status` view
  gained a `ready_to_send` state (drafted, inside the 21-day window, not yet
  followup-due) between `awaiting` and `followup_due`. `status_sheet.py` /
  `merge_status.py`'s `STATE_FILL` maps it to a light indigo (`C7D2FE`).
- Import: same pattern as above (`docker cp` the updated
  `advance_lifecycle.json`, `n8n import:workflow`, `n8n publish:workflow
  --id=advance-lifecycle`, restart n8n so the schedule re-registers) — the
  workflow's `id`/node names/connections are unchanged, so this is a safe
  re-import over the existing one, not a new workflow.
- **Not done here (at the time):** true real-time drafting for a normal
  booking — Brian chose the next-daily-9am-run latency (worst case ~24hr)
  over a webhook path for the general case. Superseded a few hours later,
  scoped to late bookings only — see below.

## Late-booking on-demand trigger (2026-09-03, later same day)

The next-daily-9am latency is fine for a normal-lead-time booking — it isn't
for one entered inside the 21-day window already, where every day of delay
actually matters. Brian's rule: **a booking submitted inside the 21-day
window drafts and notifies immediately**, not on the next scheduled check.

- `/booking`'s POST handler now computes days-until-show from the submitted
  `event_date` right at submission time. Outside the window: unchanged,
  `_run_pipeline_background()` fires and the show waits for the next daily
  check like before. Inside the window (`0 <= days_out <= 21`): a background
  thread runs `run_now.py` **synchronously** (so the show is actually seeded
  in Postgres before anything downstream looks for it — a fire-and-forget
  `Popen` would race an on-demand check that runs before seeding finishes),
  then calls `_trigger_immediate_advance()`. The thread means `/booking`'s
  response is never held up by either step.
- New workflow trigger: **`On-Demand Trigger`**, a Webhook node (path
  `advance-lifecycle-now`, `responseMode: onReceived`) added to the *same*
  `advance_lifecycle.json` — not a separate workflow, so there's exactly one
  copy of the drafting/reminder logic regardless of what fired it. A new
  **`Check Token`** code node between the webhook and `Fetch Due` validates
  `X-Advance-Token` and silently returns `[]` on a mismatch — the same idiom
  `advance_notify.json`'s `Format Email` node already uses, not a new IF
  node. `Check Token` → `Fetch Due` is the only new edge; `Daily 9am` →
  `Fetch Due` is untouched, so the schedule keeps working exactly as before
  and both triggers now share one downstream chain.
- `/internal/advance-lifecycle` gained one more piece of logic, live for
  *both* triggers, not just the on-demand one: any show in `due_initial`
  that's **already** inside the 21-day window the moment it's drafted (a
  late booking, or the daily job catching up on a backlog) gets
  `mark_send_reminder_sent` called in the same pass and carries
  `"ready_now": true` in its item. Without this, a late-booked show would
  get drafted today and only get told "ready to send" on a *separate* run
  tomorrow — technically correct, a full day later than it should be.
  `ready_now` shows are excluded from `shows_due_for_send_reminder` on every
  later run (the flag's already set), so there's no duplicate notification.
- `Build Summary` splits `initial` into `ready_now` and not — the former
  renders under its own "drafted — ready to send now" heading (and counts
  toward the subject line as "N ready now") instead of blending into the
  generic "N initial advance(s) drafted" section, which still means
  something different for a normal booking that's genuinely weeks away.
  Verified against six scenarios in a local Node REPL, including the
  ready_now-only case and a mixed run with one of each kind.
- New env var: `ADVANCE_LIFECYCLE_NOW_URL=http://localhost:5678/webhook/advance-lifecycle-now`
  in `/opt/band-advance/advance.env` — same `localhost:5678` pattern as
  `ADVANCE_NOTIFY_URL`, for the same reason (Cloudflare's bot protection
  blocks the public tunnel for server-to-server calls). Best-effort, same
  as `_notify_email` — empty/unset just means this specific fast path is
  skipped and the show falls back to the normal daily-check cadence.
- Import: same pattern, `advance_lifecycle.json`'s `id` is unchanged so this
  is a re-import over the existing workflow. Two placeholder tokens need the
  real `ADVANCE_INTERNAL_TOKEN` substituted before import now — `Fetch Due`'s
  header (as before) and `Check Token`'s `jsCode` (new) — never commit the
  real value to this repo.
