# Context Handoff — 2026-09-02
**Session topic:** Band Advance pipeline — production restructure (Dropbox venue-tree filing, combined status tab, stage-plot links, venue-correct + personalized emails, staff intake form)
**Console / Venue:** N/A (venue-neutral pipeline; FSQ is the fully-wired venue)

---

## What We Did
Picked up the working advance pipeline (`Code/BandInfoForm/`, branch `advance-system`) and hardened it into a production shape. Replaced the scratch flow with a real cockpit folder, collapsed the status read-back into the input sheet, switched output to a persistent **Venue/Year/Month filing archive**, wired stage-plot download+rename+link, made the advance email **venue-correct + per-artist personalized**, and added a **staff booking intake form** that seeds the sheet. Everything committed + pushed to `advance-system` (through `5064b24`).

---

## Current State
- **Live pilot in Dropbox:** `~/Dropbox/Nyquist/` — self-contained cockpit (`advance-list.xlsx`, `generate.command`, `_bin/`, `_template/`, README). This is a TEMPORARY location; Brian will name the real shared folder later. `generate.command` uses `$HERE`/`ADVANCE_ROOT`, no hardcoded paths, so moving it is trivial.
- **Loop that works, verified end-to-end this session:** staff log a booking → DB → `generate.command` seeds it as a sheet row → fills the advance `.docx`, files the band's stage plot, drafts the venue-correct email → files into `<VenueAbbr>/<Year>/<MM Month>/`, and folds status + band answers back into `advance-list.xlsx`.
- **Test data purged, pilot pristine** (VM DB truncated, uploads/disk cleared, Nyquist reset to a clean 36-col template).
- **Done:** Dropbox pilot, venue-tree filing (overlay/archive, no --delete), combined single-tab status (fill-blanks tinted + STATUS block), stage-plot links in doc + sheet, venue-keyed email engine (FSQ wired), per-artist Email Note, staff `/booking` form.
- **Up next (Brian's likely direction):** other venues' email content; Outlook send step; whatever he refines next.

---

## Key Decisions (Locked)
- **Sheet stays master.** Everything seeds/feeds the spreadsheet; Brian edits/overrides there. Rejected making the DB or an agent the master.
- **No agent.** The pipeline is deterministic plumbing on purpose; an LLM would be less reliable/costlier. (If ever wanted: agent-as-orchestrator over the tools, never doing the file/DB mechanics.)
- **Filing = archive, not mirror.** Each show files into `<VenueAbbr>/<Year>/<MM Month>/<MMDDYY> <Event Name> advance.docx`; email drafts in `Email Drafts/`. `generate` OVERLAYS (rsync, no `--delete`) so past shows/months are never wiped. Venue abbrevs: FSQ/WP/ESP/Court/IA/ZP/Memo; month = "09 September"; filename auto from event name. Scheme lives in `tools/fieldspec.py`.
- **Status is one tab, not two.** Band form answers fill Brian's blank cells (tinted blue); a color-coded STATUS block is appended; a veryHidden `_advance_meta` sheet tracks band-filled cells so Brian's own edits are never clobbered and `sheet.py` never mistakes a band-fill for an override.
- **Stage plots:** downloaded on generate, renamed `MMDDYY <Event> stageplot.<ext>`, filed next to the doc; the Stage Plot cell in BOTH the doc and the sheet is a clickable **relative** hyperlink (doc = same folder; sheet = venue path, URL-encoded). Doc cell reads "See DB — <filename>".
- **Email:** venue-correct body (FSQ garage/95 dB no longer leaks to other venues) via `tools/venue_email.py`; other venues fall back to safe GENERIC blocks. Per-artist **Email Note** column woven into that band's draft.
- **Generate no longer fakes "sent"** — dropped `--mark-sent`. Real sending moves to Outlook; that will start the 10-day follow-up clock.
- **Staff booking = "seed the sheet."** `/booking` gated form → `bookings` table → appended as sheet rows on generate (dedup event+date+venue+artist, stamped `seeded_at`).

---

## Open Items
- **Other venues' email copy** — only Fountain Square is wired in `venue_email.py`. Brian to supply WP / Memorial Hall / ESP / Court / Zeigler / Imagination Alley load-in, technical, hospitality language; until then they get the generic (safe) block.
- **Outlook send step** — the real next feature: drafts → Brian's Outlook drafts folder; the actual send is what should stamp `email_sent_at`. Not built.
- **Real Dropbox path** — Nyquist is a pilot name/location; Brian will give the final shared folder. Moving = relocate the folder + refresh `_bin`.
- **`_bin` drift** — `~/Dropbox/Nyquist/_bin/` holds copies of `merge_status.py`, `fieldspec.py`, `append_bookings.py`. If those change in the repo, re-copy into `_bin`.
- **Staff auth** — `/booking` uses the shared `lockdown` passcode; per-user logins/separate code deferred.
- Parked from earlier: per-act clock windows on the day-sheet; delicate event cells (Event Type/Paying/MC/DJ/Lead) not yet written into the doc; venue address map; tech-pack URLs; embedding vs linking stage plots; Slack/Monday mirror.

---

## Corrections / Watch-Outs
- **`with advance_db.get_conn() as conn` already commits on context exit.** A stray `conn.commit()` *after* the `with` threw on the closed connection and 503'd a booking that actually saved. Put commit INSIDE the `with`. (Applies to any new write handler.)
- **`generate` FILES, it doesn't mirror** — never re-add `--delete` to the venue-tree rsync or you'll wipe the archive.
- **Tinted sheet cells are a live band mirror** — Brian shouldn't hand-edit them; typing over one turns it plain and makes it his (wins from then on).
- **Deploy code with `deploy_app.command`**; DB schema changes go via `docker exec -i advance-db psql < schema.sql`. SSH: `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84` (passwordless sudo).
- Cowork sandbox can't reach the public `advance.tinydoorstudios.com`/LAN — test form POSTs from the VM against `localhost:8097` (gate first: POST `/gate` passcode=lockdown into a cookie jar).

---

## Resume Prompt

> Picking up on the **band advance pipeline** (`Code/BandInfoForm/`, branch `advance-system`, pushed through `5064b24`). It's production-shaped and working end to end. The live PILOT cockpit is **`~/Dropbox/Nyquist/`** — edit `advance-list.xlsx`, double-click `generate.command`; it seeds staff bookings, fills the advance `.docx`, files stage plots, drafts venue-correct + personalized emails into a **`<VenueAbbr>/<Year>/<MM Month>/`** archive (overlay, never deletes), and folds a color-coded status block back into the sheet. The `_bin/` there holds copies of `merge_status.py`/`fieldspec.py`/`append_bookings.py` — re-copy from the repo if they change. Read `Code/BandInfoForm/ARCHITECTURE.md` + the memory file `band-advance-form` first.
>
> Locked: sheet is master; filing (not mirroring); venue-correct emails via `tools/venue_email.py`; staff `/booking` form seeds the sheet; generate never fakes "sent."
>
> Likely next: (1) wire the **Outlook send step** (drafts → Outlook drafts; the send stamps `email_sent_at` and starts the 10-day follow-up); (2) fill in **other venues' email content** in `venue_email.py` (only FSQ is wired); (3) when Brian names it, point the pilot at the **real shared Dropbox folder**. Ask which before diving in.
