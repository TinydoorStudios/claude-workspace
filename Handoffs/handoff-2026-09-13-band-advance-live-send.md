# Context Handoff — 2026-09-13
**Session topic:** Band Advance system — Spanish-language support, live-send migration, and a real production incident
**System:** Code/BandInfoForm/, branch `advance-system`, n8n VM (192.168.200.84), advance.tinydoorstudios.com

---

## What We Did

Very long session, several major chunks, all finished, deployed, and pushed:

1. **Spanish-language band form + translation-on-submit.** `?lang=es` on every form route (`app/i18n.py`, one bilingual strings table — form.html/thanks.html pull from it, never carry literal copy). Field names and stored option values stay English regardless of language, so the DB/docfill/daysheet pipeline never has to know which language a band used. Free-text answers get machine-translated to English on submit (`app/es_translate.py`, Groq `openai/gpt-oss-120b`, free tier — GROQ_API_KEY is set in advance.env). Original Spanish kept alongside as `<field>_es_original`, never dropped.
2. **Salsa On The Square is 3CDC's one bilingual series.** Its advance email sends English-then-Spanish in one message with two form links (`venue_email.BILINGUAL_SERIES`, `draft_emails.py`'s `is_bilingual` branch). Its form drops the backline and scenic-elements questions in both languages (a house-band situation, no backline-sharing concept). Series content override files can carry "## Section (Español)" headers alongside English ones.
3. **Welcome-email greeting tweaks:** uses only the contact's first name plus the band name ("Hello Dali and The Amador Sisters,"), and collapses to just one name when the contact name exactly matches the band name — a solo act booked under their own name gets "Hello Dali Amador," not "Hello Dali and Dali Amador,".
4. **Fixed a real lifecycle bug:** a late booking already inside its own follow-up window at booking time could never get that follow-up in the same run — it silently waited for tomorrow's cron. Queries reordered to run fresh after the initial-advance commit.
5. **New: unresponded-at-3-days alert** — one real email to blloyd@3cdc.org the first time a show crosses 3 days out with no submission, independent of the band-facing follow-up, not skipped for a band with no email on file.
6. **Live-send migration.** The initial advance and every follow-up (cadence trimmed 7/3/2/1 → 7/3/1) now SEND for real via Outlook — no more draft-and-review step. A reminder tier already on/before the day a show was booked is permanently pre-skipped (never fires backdated). The old 21-day "your draft is ready" nudge is retired.
7. **A real incident during that migration, root-caused and fixed:** an n8n workflow edit looked completely successful (SQL ran, workflow showed active, every test returned 200/202) but silently never took effect — this n8n instance versions workflows separately (`workflow_history` + `activeVersionId`) from the row that looks like the live definition (`workflow_entity.nodes`). Two real bands got a welcome email with an empty body before it was caught by actually reading a test send's content back via Gmail instead of trusting the HTTP response. Fixed properly via the project's own `./deploy_n8n_workflows.command` (import + publish + restart against the checked-in JSON — the tool that should have been used the first time). Built a hard guard against recurrence: both n8n's Send via Graph node and Flask's `_send_outlook_email` now refuse to send blank/whitespace-only content to a real recipient, redirecting to Brian with an explanation instead. Fully documented in `n8n/README.md` ("Live-send migration + a real incident" section) with the hard rule: **never edit an n8n workflow via raw SQL again.**
8. **Booking form:** picking an existing series now auto-matches its venue (`SERIES_VENUE` map built from the same data the series dropdown's optgroups already use).
9. **Diagnosed (not yet acted on)** why the Ricky Nye WP show (Oct 21) shows "Awaiting Window" while three other WP shows just entered today show "Queued" — not a bug, just timing: Ricky Nye already hit a lifecycle run and got its welcome sent; the other three were entered moments ago and, being more than 21 days out, won't get an immediate on-demand send — they'll wait for tomorrow's 9am cron. See Open Items.

---

## Current State

Everything above is done, deployed to the VM, and verified live (real Gmail read-backs, not just HTTP status codes) — nothing half-finished.

- **Done:** all 9 items above.
- **In progress:** nothing.
- **Up next:** waiting on Brian's answer to the open question below.

Five commits this session, all pushed to `advance-system` (not merged to `main`):
- `band-advance: Spanish-language form, on-submit translation, bilingual Salsa email`
- `band-advance: live-send migration, lifecycle ordering fix, unresponded-at-3-days alert`
- `band-advance: empty-body send guard + n8n workflow-versioning writeup`
- `band-advance: booking form auto-matches venue to an existing series`
- `band-advance: welcome greeting collapses when contact name IS the band name`

---

## Key Decisions (Locked)

- **Live-send, no review step.** Initial advance + every follow-up (7/3/1 days out) send for real via Outlook the moment they're due. This is the new normal going forward, not a pilot.
- **Stale-tier skip is permanent, not just for the migration window.** Any reminder tier on/before the day a show was booked never fires for that show, ever — not just during the cutover.
- **n8n workflow edits: `./deploy_n8n_workflows.command` only, never raw SQL against `workflow_entity`/`workflow_history`.** This is now a hard rule with a real incident behind it (see `n8n/README.md`).
- **Empty-body guard stays in place permanently** on both sides of the Flask/n8n boundary — not a one-time patch.
- **Salsa On The Square is bilingual; every other series is English-only** through the same templates, unaffected.
- **The Love Handles incident: left alone, no follow-up sent** — Brian's explicit call after I clarified they were never actually sent a broken email (I'd misattributed an unrelated notification as evidence of one).
- **Chaya Jones did get a corrected resend** — she was the one real, confirmed case of the empty-body bug.
- **GROQ_API_KEY is Brian's own key, already live in advance.env** — separate from GearTickets' own Groq credential (that one lives inside n8n's encrypted credential store, not reusable here).

---

## Open Items

- **Unanswered question to Brian:** should the on-demand lifecycle trigger fire for every new booking regardless of days-out (not just ones already inside 21 days), so a far-future booking's welcome goes out within seconds instead of waiting for the next 9am cron? This is exactly why Ricky Nye and the three just-entered WP shows show different states right now. Ask this first if Brian doesn't bring it up himself.
- **Background task still pending** (spawned this session, not yet resolved): investigate why n8n workflow `XUNicTtAu6GhT6Ca` ("Advance Follow-up Check") shows as active when `n8n/README.md` documents it as superseded/deactivated since 2026-09-03 — possible duplicate/legacy follow-up mechanism still running silently.
- **Worth knowing, not yet acted on:** the `advance_status` SQL view's state model (`queued` / `awaiting` / `ready_to_send` / `followup_due` / `followup_drafted` / `responded`) predates the live-send migration. `ready_to_send` in particular is now essentially unreachable in practice (nothing sits "ready to send" anymore — it either hasn't sent yet or already has). Not broken, just a little stale conceptually; could use a pass if the dashboard/status report ever gets revisited.
- `internal_create_outlook_draft` n8n workflow is left active but dormant — nothing calls it since the live-send migration. Not deleted, in case a draft-based path is ever wanted again.

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|--------------|
| fsq_sample_es.md | md | Early sample render of the Spanish Fountain Square advance email (superseded in spirit by the later Salsa bilingual work, but was the first proof-of-concept) |

---

## Corrections / Watch-Outs

- **Never trust an HTTP 200/202 as proof a workflow edit took effect.** After any change to a workflow that sends or drafts real email, send a real test through the actual webhook and read the actual content back (Gmail search/get_message, or the Graph response body for a draft call). A success status only proves Graph accepted the request — it proves nothing about what was in it.
- **This n8n instance has a versioned publish model** (`workflow_history` table, `workflow_entity.activeVersionId`) that most people don't expect. Editing `workflow_entity.nodes` directly does nothing to what's actually running.
- Misdiagnosed The Love Handles as a second empty-body victim by treating a nearby `internal-send-outlook` execution as evidence — it was actually an unrelated "new booking" notification to Brian himself. Caught it before sending anything further, but already fired one unnecessary "correcting a glitch" email to a band that never had a problem. Lesson: cross-check timestamps against actual deploy/commit times before attributing an incident, not just proximity in an execution log.

---

## Resume Prompt

> Picking up from the 2026-09-13 session on the Band Advance system (`Code/BandInfoForm/`, branch `advance-system`). That session shipped Spanish-language form support with on-submit translation (Groq), made Salsa On The Square a bilingual series, and migrated the whole system from draft-and-review to live-send for the initial advance and every follow-up (cadence now 7/3/1 days out). A real incident happened mid-migration — an n8n workflow edit silently never took effect due to n8n's versioned-publish model, and two real bands got an empty-body welcome email before it was caught. That's fully fixed now with a hard guard on both the n8n and Flask side, plus a documented rule in `n8n/README.md`: never edit an n8n workflow via raw SQL, always `./deploy_n8n_workflows.command`. Five commits pushed to `advance-system`, not yet merged to `main`.
>
> The last thing in that session was Brian asking why the Ricky Nye WP show (Oct 21) shows "Awaiting Window" while three other WP shows entered minutes earlier show "Queued." I explained it's just timing (Ricky Nye already hit a lifecycle run; the other three are more than 21 days out so they wait for tomorrow's 9am cron rather than triggering immediately), and asked whether he wants the on-demand trigger to fire for every new booking regardless of days-out so far-future welcomes go out within seconds instead of waiting on the cron. **That question is unanswered — ask it again if he doesn't bring it up.**
>
> Also open: a background task was spawned to investigate why n8n workflow `XUNicTtAu6GhT6Ca` ("Advance Follow-up Check") shows active despite being documented as deactivated/superseded since 2026-09-03 — check whether it resolved anything before redoing that work.
>
> Key context not necessarily in standing memory yet: the n8n versioned-publish gotcha and the "always use deploy_n8n_workflows.command" rule (both in `n8n/README.md`'s new section), the empty-body send guard now in `internal_send_outlook.json` and `app.py`'s `_send_outlook_email`, the FOLLOWUP_TIERS = (7,3,1) cadence with permanent stale-tier pre-skipping, and that GROQ_API_KEY is already live in advance.env.

