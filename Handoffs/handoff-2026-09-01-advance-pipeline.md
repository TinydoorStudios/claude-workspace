# Context Handoff — 2026-09-01
**Session topic:** Band Advance pipeline — built the full spreadsheet→email→form→day-sheet system with status tracking + n8n follow-ups
**Console / Venue:** N/A (venue-neutral; day-sheet modeled on the 513 Airwaves / Fifth & Vine FSQ template)

---

## What We Did
Turned the standalone band-advance Flask form into a full **advance pipeline** on the n8n VM. The spreadsheet is now the master source: it generates the advance email and the day-sheet document, and the band's form fills whatever the sheet leaves blank. Added a dedicated Postgres, event/day-sheet doc-fill against the real 513 Airwaves template, pre-addressed form links, status tracking, and an n8n daily follow-up loop. Everything lives in `Code/BandInfoForm/`, branch **`advance-system`** (~20 commits, NOT pushed).

---

## Current State
- **Live:** public form at **advance.tinydoorstudios.com** (Cloudflare tunnel + DNS + dashboard tile). Flask app systemd `band-advance` :8097. Dedicated **`advance-db`** Postgres container (127.0.0.1:5433, isolated from n8n, also attached to `n8n_default` net).
- **DB tables:** artists, shows, submissions, files, events, event_acts, followup_queue + the **`advance_status`** view. Disk-first: form saves to disk then DB best-effort.
- **The loop works end to end:** put band(s) in `tools/lists/advance_list_template.xlsx` → run **`generate.command`** → drops into `output/`: a day-sheet per event, a pre-addressed advance email per band, follow-up drafts, and **`advance_status.xlsx`** (status read-back). Nothing auto-sends.
- **Brian tested it live** with "Headiner Band" (513 Airwaves w/ Inhailer Radio, 2026-09-11, FSQ) — filled the form via the pre-addressed link; it flowed to the day-sheet + status sheet correctly.
- **n8n:** workflow "Advance Follow-up Check" (id `XUNicTtAu6GhT6Ca`) active, daily 9am → POST `/internal/run-followups` (token-protected) → queues reminder drafts (drafts-you-approve).
- **Up next (Brian's likely direction):** review the day-sheet cell mapping for the remaining "missing/misplaced" cells; decide multi-act per-act clock windows; wire the actual Gmail send step; maybe manual "completed" override.

---

## Key Decisions (Locked)
- **Spreadsheet is the master source.** It creates the email + day-sheet; the form fills blanks; **sheet value wins, form fills gaps.** Single source of truth = `tools/fieldspec.py` (35 columns, 3 groups: EVENT / ACT / BAND DETAILS).
- **DB = dedicated `advance-db` Postgres container**, isolated from n8n's PG (reuses pg16-alpine image).
- **Send path: Gmail now, Outlook in production. Drafts-you-approve — NOTHING auto-sends** (initial or follow-up). Generating with `generate.command` stamps `email_sent_at` (treats generate = the send step).
- **Follow-up: 10 days, ONE, DRAFTED not sent.** n8n owns the recurring check. Completed = band submitted the form (auto); follow-up date shows only while not completed.
- **Status view = generated companion `advance_status.xlsx`** (Email Sent / Follow-up Due / Completed + all form answers), refreshed each run. NOT a live dashboard, NOT written back into Brian's input file.
- **Outputs land in the workspace** `Code/BandInfoForm/output/` (day-sheets/, emails/, emails/followups/, advance_status.xlsx).
- **Pre-addressed form links:** every advance email carries `/f/<token>` seeded from the sheet row (band/venue/date/series pre-filled); ties the submission to the exact show.
- **Set Time → Set Length** (duration; key kept as `set_time` internally). Shows in email ("Set length: 60 min") + status sheet; day-sheet AUDIO row uses the event **clock window (Start–End)**, not the length.
- **Email rebuilt off Brian's real Fifth & Vine email** (`tools/email_templates/advance.md.j2`): keeps all policy/informational content, drops the highlighted questions (form covers them), merges sheet data (schedule, bill, set length, contacts, deadline).
- Form gained **contact name + email**, a returning-only "what changed?" box, a per-venue tech-pack link hook. Search view is passcode-gated (`lockdown`).

---

## Open Items
- **Multi-act per-act clock windows on the day-sheet** — AUDIO row now shows the whole-show window (Start–End), exact for single-act; a multi-act bill shows the same window on every act. Would need per-act clock fields or computing from start + set lengths. (Brian flagged, deferred.)
- **Delicate day-sheet event cells** — Event Type / Paying? checkboxes, MC/DJ, Lead are stored in `events.details` but NOT yet written into the doc (checkbox-glyph / separate-table cells). Next pass.
- **Venue location/address map** — only Fountain Square's full address is mapped (`fieldspec.VENUE_LOCATION`); other venues show just the name until Brian gives addresses.
- **Email attachments** — the email references the load-in doc + 5 parking QR codes, but the system can't attach files to a draft. Brian adds at send, or we host copies + link.
- **Remaining "missing/misplaced" day-sheet cells** — Brian gave SCENIC (fixed: riser + scenic notes); may have more. Mapping lives in `daysheet.py::act_cells` + `fieldspec.py`.
- **Manual "completed" override** and **separating "mark sent" from generate** — offered, not built.
- **Tech-pack URLs per venue** (`forms_config.TECH_PACKS`) — TBD from Brian.
- **Slack / Monday mirror** — deferred ("later").
- **n8n:** can only test-run the workflow via the UI (CLI `execute` collides on port 5679 with the running instance). PG16 "compatibility only" warning persists.
- **Credentials cheat sheet** (`TDS_Credentials_CheatSheet.md`) has the advance-db creds + gate passcode; not committed (private).

---

## Files Delivered This Session
| File | Format | Description |
|------|--------|-------------|
| advance_list_template.xlsx | xlsx | The master input sheet (35 cols incl. Set Length + schedule columns; venue/slot dropdowns; How-to tab) |
| advance_status.xlsx | xlsx | Status read-back: Email Sent / Follow-up Due / Completed + all form answers |
| 513_Airwaves..._2026-09-11__daysheet.docx | docx | Day-sheet for the Headiner Band test (AUDIO row = clock window fix) |
| sample_advance_email / headiner-band...new.md | md | Advance email rebuilt off the Fifth & Vine template |

(Many earlier iterations were also delivered; the above are the current versions.)

---

## Corrections / Watch-Outs
- **Day-sheet AUDIO row** was showing the set length (60); FIXED to pull the event clock window (Start–End, e.g. "HEADLINER: 9pm-10pm").
- **"Lily" contamination** was bad demo data (site lead ≠ band contact). System keeps band contact (from form) separate from the Lead field (site lead, internal).
- **Template example rows** imported as a real event; removed example DATA rows (worked example now on the How-to tab). Sheet reader also skips EXAMPLE-prefixed rows.
- **Sheet reader reads by column LABEL, not position** — Brian can reorder/delete columns freely; renaming a header needs a `fieldspec.py` alias.
- **Regenerating the template wipes data rows** — preserve by reading rows first and re-adding (dropdowns survive an openpyxl round-trip; the x14 validation warning is harmless).
- **n8n:** workflow JSON needs a top-level `id` or import fails; activate via `n8n publish:workflow --id=<id>` (NOT update:workflow) THEN restart n8n. Deploy code with `deploy_app.command`; the DB compose/env/systemd are one-time.
- **generate.command** clears `output/` before pulling so it mirrors the current sheet.
- SSH to VM: `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84` (passwordless sudo).

---

## Resume Prompt

> Picking up from a previous session on the **band advance pipeline** (`Code/BandInfoForm/`, branch `advance-system`, not pushed). It's built and working end to end: the spreadsheet (`tools/lists/advance_list_template.xlsx`) is the master source → `generate.command` produces a day-sheet, a pre-addressed advance email, follow-up drafts, and `advance_status.xlsx` into `output/`. The form fills blanks (sheet value wins). Dedicated `advance-db` Postgres on the n8n VM; app at advance.tinydoorstudios.com (systemd band-advance :8097). n8n "Advance Follow-up Check" runs daily. Nothing auto-sends — drafts-you-approve, Gmail now / Outlook in production. Read `Code/BandInfoForm/ARCHITECTURE.md` first.
>
> Locked rules: spreadsheet is source of truth (single spec in `tools/fieldspec.py`); follow-up = 10 days / one / drafted; Set Length (not Set Time); day-sheet AUDIO row = event Start–End clock window.
>
> Likely next tasks: (1) finish the delicate day-sheet event cells (Event Type/Paying checkboxes, MC/DJ, Lead — stored in events.details, not yet written to the doc); (2) multi-act per-act clock windows on the day-sheet; (3) wire the real Gmail send step; (4) review any remaining day-sheet cell mapping Brian flags. Ask which before diving in.
