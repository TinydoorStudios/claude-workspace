# Band Advancing — Google Form → n8n → self-hosted DB → Dropbox

Replaces the reply-all advancing email. Google's only job is the form. Everything of
record — the data, the generated Word doc, the no-band-gets-missed tracker — lives on your
own infrastructure (the n8n VM, its Postgres 16, and Dropbox).

```
Google Form ──onSubmit POST──▶ n8n Webhook
                                  │
                                  ├─▶ docx service (renders your .docx → Dropbox)
                                  ├─▶ Postgres  (advancing DB: submissions + shows)
                                  └─▶ Slack ping
Daily n8n schedule: "upcoming shows not advanced?" ──▶ Slack nudge
```

## Pieces

| Path | What it is |
|---|---|
| `AdvanceForm.gs` | Apps Script that builds the generic WP/FSQ/ESP Google Form and POSTs each submission to the n8n webhook. |
| `db/schema.sql` | Postgres tables: `shows` (booked = the tracker) + `submissions` (form data), and a `tracker` view. |
| `docx-service/app.py` | Flask service on the VM. Fills the venue's tagged advance-sheet template and uploads it to Dropbox. `TEMPLATES` maps venue → template file. |
| `docx-service/templates/advance_fsq_salsa.docx` | Your **blank Salsa master**, tagged. Only the band-provided cells are tagged; the schedule, PA, consoles, crew (Sam/Joe), emcee, and "Salsa on the Square" stay baked exactly as your master. |
| `n8n/advancing_intake.json` | Import into n8n: webhook → render docx → insert → flip the show to Received → Slack. |
| `n8n/normalize.js` | Paste into the intake workflow's "Normalize" Code node (JSON export mangles inline JS). |
| `n8n/advancing_reminder.json` | Daily "who hasn't advanced?" nudge. |
| `deploy/deploy-docx-service.command` | Run on the Mac: creates the DB, loads schema, installs the service + systemd unit. |

## What I need from you to finish

1. **The real advance doc, available offline.** In Dropbox, right-click
   `082726 Salsa Prod Adv Dayton Salsa project.docx` → Make Available Offline (it's a 0-byte
   placeholder right now). Once it syncs, I'll turn a copy into `docx-service/templates/advance_template.docx`
   with `{{ }}` tags so the output matches your layout exactly. Until then the service uses the fallback layout.
2. **A Dropbox app + token.** dropbox.com/developers → Create app → Scoped access → App folder →
   name it (e.g. `3cdc-advancing`). Under Permissions enable `files.content.write` and
   `sharing.write`; generate an access token. Tell me the folder path you want docs in
   (default `/3CDC Advancing/<Venue>/`). Token goes in `/etc/advance-docx.env`, never in git.
3. **Confirm the Postgres user** in `/opt/n8n/.env` (the deploy script assumes `n8n` — override with
   `PGUSER=… bash deploy-docx-service.command` if different).
4. **WP / ESP blank masters.** Each venue/series uses its own tagged blank master (its schedule,
   PA, consoles, crew, and defaults are baked in — not coded). I've tagged the FSQ Salsa one from
   the blank you gave me. Drop the blank master `.docx` for Washington Park and Elm Street Plaza in
   `_inbox` and I'll tag each the same way and register it in `TEMPLATES`. Until then those venues
   fall back to a plain data doc.

## Stand-up order

1. **Deploy the DB + service:** run `deploy/deploy-docx-service.command` on the Mac. It tees to
   `deploy/deploy.log` — send me that if anything errors. Create `/etc/advance-docx.env` from
   `docx-service/advance.env.example` (with the Dropbox token + a shared secret), then the script starts the service.
2. **n8n:** import both workflow JSONs. Attach an "Advancing Postgres" credential (host `postgres`,
   db `advancing`) to the Postgres nodes and your Slack cred to the Slack nodes. Paste `normalize.js`
   into the Normalize node. Set the Slack channel. Copy the intake **Webhook Production URL**.
   Publish per-workflow: `cd /opt/n8n && sudo docker compose exec -T n8n n8n publish:workflow --id=<id>`.
3. **Google Form:** paste `AdvanceForm.gs` into a new script.googleapps project, set
   `CONFIG.n8nWebhookUrl` (the webhook URL), `CONFIG.webhookSecret` (matching the service +
   workflow), and `CONFIG.uploadEmail`. Run `setup()`. Grab the form URL from the logs.
4. **Test:** submit the form once. Confirm a row in `submissions`, a `.docx` in Dropbox, and a Slack ping.
5. **Load the tracker:** insert one `shows` row per booked show (act, venue, date, contact_email,
   status='Not sent'). The reminder job nags on anything inside 10 days still not Received; submissions
   auto-flip the matching row to Received.

## Stage plots

The form tells bands to email stage plots/input lists to `CONFIG.uploadEmail` (your dedicated
Gmail), with an optional "paste a link" field. Google Forms native file upload is deliberately not
used — it forces every band to sign into a Google account. If you later move intake off Google (a
self-hosted form), direct upload becomes possible and the Gmail can retire.

## Monday (phase two)

The `submissions`/`shows` tables are the seam. When you want the board of record in Monday, add a
Monday node to the intake workflow (create/update an item per submission) — same pattern as Gear
Tickets — and mirror the `status` column. Nothing else changes.
