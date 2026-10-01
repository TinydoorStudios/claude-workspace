# memory.md
*Last consolidation: 2026-10-01 — log in memory-archive-2026H2.md*

*Living document — newest entries at the top of Session Notes. Never delete — archive instead.*
*SIZE RULE: this file loads in full at every session start. Session Notes keep a trailing ~2 weeks and the file stays under 18KB; older notes roll into `memory-archive-YYYYHn.md`. Consolidation passes log to the archive, never here. (Updated 2026-09-14, previously: ~30KB / current calendar month — tightened 2026-08-25.)*

---

## How This File Works

This file is the persistent memory system for Brian Lloyd's sessions. It tracks:
- Active projects and their current state
- Decisions made and why
- Unresolved issues and open questions
- Things to remember for next time

**Rules for updating:**
- Append new entries under the relevant project or create a new section if it's a new topic.
- If updating an existing entry, edit in place and update the date.
- Mark completed items `[DONE]` and resolved issues `[RESOLVED]`.
- Never rewrite history — if something changed, add a note below the original entry.

---

## Active Projects

Canonical project state (active shows, tools & infrastructure, open issues, completed shows) lives in the KB: `Live Sound KB/Wiki/active-projects.md`. This section used to duplicate it verbatim (both frozen at "Last updated May 16, 2026" since the original entry) — trimmed to this pointer 2026-07-08 to stop the drift. SPL Monitor's project-state summary (features, next steps) was also moved there the same day; its build history stays below in Session Notes, which is where it belongs.

---

## Open Issues

*(none)*

---

## Resolved / Done

Archived 2026-08-11 to `memory-archive-2026H2.md` — everything in it was May 2026, dismissed or shipped.

---

## Seventh Heaven Pro

Reference notes moved to the KB 2026-08-11 — canonical source is `Live Sound KB/Wiki/reverb-reference-memo.md` (Early/Late behavior, the Memo preset list, VLF rule). The old copy here is in `memory-archive-2026H2.md`.

---

## Session Notes

### 2026-09-29 — Memorial Hall advance: form, doc, filing (live)
Memo now has its own advance. The two old Memo docs became one branded, one-page Prod Adv. It has a one-artist and a two-artist layout; the two-artist version is used when a second act is booked under the same Event Name. Memo also has its own form. All questions are Yes/No, and the IEM and engineer follow-ups work like FSQ's. Staff-only sections are hidden from the band. The form has seven multi-file upload boxes, and every save adds to the same record. Docs and uploads are filed into the team's per-show folder (`<MM.YYYY> MEMO/<MM.DD.YY> <Event>/`). Uploads are renamed by date + act + type. Crew comes from the staffing sheet's Memorial Hall block. Memo's welcome goes out at 30 days, with chases at 15/10/7/5/3/2/1. The welcome is PAUSED until Brian approves the copy. Staging passed 158/158, 620/620 and 42/42; deployed as 92ec8a2. Later that night: band changes to settled answers are held for Brian (5e6009d), staff-only Internal notes, and the first real show, A Man Named Cash (10/16/26), booked with no emails. Scripts, sample fills and superseded drafts now live in `Code/BandInfoForm/tools/memo_shows/` and `_superseded/memo-drafts-2026-09-29/` (moved out of Handoffs). Auto-memory `[[memo-advance-doc]]`; system notes in ARCHITECTURE.md.

### 2026-09-29 — Memorial Hall tech specs, Version 1
Rebuilt Memo's production specs from Brian's "2026 edit" .docx into a branded 10-page spec sheet: page 1 is contacts + an At a Glance table, then Stage, Load-in/Power, Audio, Lighting, Video, Backline, Dressing Rooms, Terms, with all 23 source photos kept and captioned. Avenir Next, Memo purple/gray, Memo wordmark header, 3CDC footer. Files + generator in `audio/Memorial Hall/Tech Specs/` (`build_v1.py` → .docx, Word exports the PDF). Brian chose the SPL wording "95 dBA LAeq (6-minute), balcony center" for Memo. Not yet folded into techpack.py / memorial-hall.json.

### 2026-09-29 — Snidely Whiplash (FSQ 09-30) deep build
Rev 1.0 packet + .ses built and committed (17845f4); all PASS. All five vocals hold the FSQ template curve (Brian) — written as FLAT bands + HPF 184.4 so the template passes through byte-exact. Dry-air posture (27–43% RH). Carole King PENDING items (8) approved and written to KB articles. Not yet published — waits for Brian's go.

### 2026-09-29 — Opus/Sonnet model routing made permanent
show-deep-build runs on Opus 5.5 medium (frontmatter + a get_session model gate at step 1); new-show, send-it and show-wiki-push run on Sonnet 5.5 medium via frontmatter. Global ~/.claude/settings.json now has effortLevel medium alongside model opus. Guideline in audio/_system/PIPELINE.md. Reddit research requested but reddit.com is blocked in both Chrome and the built-in browser ("safety restrictions"); Brian can paste threads instead.

### 2026-09-29 — 3CDC brand rollout started (advancing first)
Decided against branches for keeping advancing separate from show work. The plan instead: give the advance pipeline its own repo and move venues into a registry, with Memo as the first venue built on its own profile (content still owed). Read the 3CDC Brand Guidelines PDF and drafted a six-phase plan to put every advancing output on brand: emails via mailer.py first, then the form, the Prod Adv .docx, tech packs, and optionally internal tools. Brian: Avenir Next everywhere, show packets included, replacing the Calibri rule (auto-memory `[[calibri-body-default]]`). Phase 0+1 done: 24 logos cropped at 600 dpi from the guide's vector art (Brian: final for now) plus `Code/BandInfoForm/brand/brand.json` (tokens, per-venue palettes, addresses). Two errors in the guide were corrected there: Memo gray is #A7A8AA, not the printed #A9AB36, and the PMS 646 RGB is a typo. Open: the guide spells it Ziegler but the code key is "Zeigler Park" (alias only for now, key migration is its own job); Elm Street Plaza isn't in the guide; build_packet.py still uses Calibri. Afternoon: phases 2–4 shipped. That covers the branded HTML band emails (mailer.py `venue=`, plain text rides along), the restyled Prod Adv template (now one page, venue logo stamped in daysheet.build) and the light venue-themed form + thanks page, plus public /brand/ and /techpack/ routes. Staging passed 158/158 and 620/620, and it was deployed as 7fbc87c. The deploy first required committing an uncommitted 09-27 VM hotfix to tools/missing_reports.py. The tech pack generator (tools/techpack.py) is built, but its content is parked for Brian's specs-redo project (auto-memory `[[tech-specs-redo-next]]`).

### 2026-09-27 — Tool scouting + shows board
Skipped DeepSeek Harness, AnyDoc, OmniRoute. From Chase AI's "Claude OS" TikTok, took one idea: the dashboard should show skill outputs. Built the shows pipeline board on tinydoorstudios.com/rack/ (export_shows.py + push-shows.command, commit dbcf863). The launchd timer was blocked, so the feed now auto-pushes on every show_status stamp instead (`62ee86b`). (Updated 2026-09-28, previously: "Feed isn't scheduled yet because the launchd agent was blocked.") Afternoon, same day (from git log, consolidated 2026-09-28): /rack/ gained the band-advance panel (`/internal/board` → status_writer, `b8cdbf0`/`75ce2e6`), an open-issues panel (gear tickets + PENDING.md, `17e46d8`), and action buttons for digest / crew report / missing-reports through an nginx allowlist with X-Advance-Token, with the Report Reminder webhook now token-checked (`b7fd26b`/`9b7516d`); dark palette pass `92529dc`. Both Q225 templates got a second preset-library trim and Memo ch 1-39 went back to June (`bdb2b06`). Detail in auto-memory `[[landing-command-center]]`, `[[memo-template-recalibration]]`, `[[fsq-template-current]]`.

### 2026-09-26 (afternoon/evening) — Advance tweaks, 1313 hard-coded, Smaart IP moved, CK/JT published (from git log, consolidated 2026-09-27)
Band Advance: `9560c02` hard-codes `1313` into `VALID_GATE_PASSES` so it always opens the gate whatever advance.env says (the env value was never set on the VM); `55a6115` flattens a typed stage plot before it lands in the doc cell; `7b73760`/`8f1c5c9` relabel Edit buttons "View/Edit". SPL Monitor: FSQ Smaart host moved to `192.24.143.107` (Altafiber dynamic, was .121), runbook updated in `4b63646`; dashboard guide PDF gained Section 5 on the 90/95 switch (`4f1d916`). CK/JT: published to the wiki (`41ac488`), piano rig PDF folded into MASTER, CLA Epic loadable presets + 7th Heaven chart, mixes renamed from the input list; show-deep-build now runs the renamer every build (`9417e6a`).

### 2026-09-26 — Carole King & James Taylor Story (Memo 09-28/30)
Piano rig locked (DPA 4099 Hi/Lo PA, SM57 plate hole H2 wedges, MK4 ORTF record; all condensers on Millennia HV-3D-8). C3 placement diagram drawn from a real C3 plate photo. Full deep build Rev 1.0: packet + .ses PASS, commit 5cc3e63. New standing rule: Memo reverbs = 7th Heaven + CLA Epic only. KB write-backs pending (SM57 plate hole, stomp box DI, piano pair group EQ, CLA Epic section, HV-3 page).

### 2026-09-26 — SPL Monitor limit-mode toggle shipped
FSQ dashboard now has a passcode-gated (1682, both directions) switch between 90 dB LAeq 10s and 95 dBA Slow. 95 mode: light/headroom/violations off SPL A Slow, yellow 90, 3 s sustain. Mode persists across restarts within a report day, snaps back to 90 at 05:00. CSV `limit_mode` column; nightly email/PDF list the rule(s) in force. Config `limitModes` in Code/SPL-Monitor/config.json (Memo instance has none, so no toggle there). Deployed to the n8n VM and live. Plan: Handoffs/plan-2026-09-25-spl-limit-mode-toggle.md.

*Newest first. Older entries live in `memory-archive-2026H2.md`.*

### 2026-09-25 (evening) — Band Advance: drink tickets fixed, 3rd-party shows lose the perks (from git log, consolidated 2026-09-26)
Three commits closed the drink-ticket gap the 09-24 note left open. `07270b9`: tickets = (performers + crew) × 2 in the day sheet, form, fieldspec and schema. `bb01219` + `776c011`: 3rd-party FSQ/WP shows no longer get parking validations or drink tickets — dropped from the venue email, thank-you, day sheet and the form help text (i18n). Deploy not recorded in git. Same day, a plan was written for an FSQ SPL dashboard limit-mode toggle (90 LAeq 10s ⇄ 95 dBA-Slow, passcode-gated, reuses the reset code): `Handoffs/plan-2026-09-25-spl-limit-mode-toggle.md`, not yet built.

### 2026-09-24 — Band Advance: the research improvements shipped, and the phone came out of the ladder (Opus)
Second batch on top of the 09-23 sweep. Four work packages from the 2026-09-16 research pass (`report-research.md` (d)), committed `ea47c71`, staged 158/158 + 620/620, deployed, `advance_lifecycle.json` redeployed with it. The ladder is now welcome → T-10 → T-7 → T-3 → T-1, each rung with its own voice and naming what that show is actually missing; one deadline everywhere (`min(show−7d, booking+14d)`); **T-7 stopped being a nudge and became the confirmed schedule to every show**, chase folded in underneath when they haven't answered (one email, one `advance_reminders` row); set length in every band email; every subject ends `— Band · Venue · M/D`; open-tracking on the short link; staff note + accuracy pip on the artist. Form got two of the four gap fields — an optional trailer question (only shown once large-vehicle count > 0) and a crew count beside performers. **Three corrections from Brian worth keeping: research #4's phone escalation is out entirely ("everything needs to be my email as much as possible") and became an email tier; the "not needed here" guest-list/credentials line was pulled back out of the hospitality blocks; and the research findings should have been SHOWN before anything was built from them** — "nowhere did you show research findings and suggestions. i asked for that." Open and unresolved: splitting crew out of `performers` means a band with crew now gets fewer drink tickets (code says `performers × 2`, the form still promises tickets for both) — he dismissed the question. (Updated 2026-09-25: resolved — drink tix are now `(performers + crew) × 2` everywhere, `07270b9`.) Next piece is research #8, the send outbox. Handoff: `Handoffs/handoff-2026-09-24-band-advance-sweep-and-research.md`.

### 2026-09-23 — Band Advance: the 122-fix sweep is staged, tested and LIVE (Opus)
Picked up the 9/22 sweep where the usage limit dropped it — the fix lanes had never run, so `b0e4d3a` existed only as a plan. Re-ran the workflow with the fix stage restructured into six parallel lanes (hub files `app.py`/`advance_db.py` shared, Edit-tool-only so concurrent lanes can't lose an update); the 14 finders and 60-odd verifiers replayed from cache, so only the fixes were paid for twice. 122 of 124 confirmed fixes landed, 10 regressions in the new code were caught by the diff reviewers and repaired. Staging on the VM from a repo rsync (`~/advsrc` → `setup.sh advsrc`): first run 158/158 + 477/484. **All seven failures were fixture collisions with real cloned bookings, not regressions** — the clone carries live data, and a real Salsa act held 7:00p on x-l's hardcoded date (the set-start guard refused the fixture, correctly) while a third live act shifted x-m's columns. Added `free_date()` (`67e02ca`), which also steps over every `timedelta(days=n)` the suite hardcodes — the first cut of it stole x-h's day. Fresh clone, both suites: **158/158 + 483/483**, then teardown, deploy (`67e02ca`, drift check clean, both new migrations applied), and the three changed n8n workflows re-imported + republished (lifecycle, notify, backup report — all active after the restart). Live checks: form 200, healthz ok, every deployed .py parses under the VM's 3.11. Answers `questions.md`: the sweep is deployed. Standing lesson for this suite: **a staging test that asserts "these are the only acts on the bill" must pick its own free date** — the clone is live data, and October fills up.

### 2026-09-23 — Band Advance: Latin Beat Project (FSQ Salsa 9/24) follow-up check
Brian asked whether the unresponded band got its follow-ups. DB showed 7-day (9/17) and 3-day (9/21) reminders sent to jaimemrls@aol.com, no send_failures; no day-ahead because that email only goes to responded shows. At his go, fired `/internal/advance-lifecycle` by hand at 8:46 ET: sent Latin Beat's 1-day reminder plus the 9/30 7-day reminders (Love Handles, Snidely Whiplash) and thank-yous for shows 397/918, 0 failures. The "missed" overnight run was not a bug: that run was 11:05pm ET on 9/22, and the app's DB connections run in America/New_York, so the show was still 2 days out. My earlier "should have fired" came from psql, which runs in UTC. Always check date logic in the app's timezone. At 8:50am the VM was still running the 9/19 code. The parallel Opus session (entry above) deployed the sweep as `67e02ca` at 10:38am, verified 9/24: `.deployed_commit` = 67e02ca, form 200. Booking row 38 still has no times or lead.

### 2026-09-22 — Band Advance: 122-fix sweep across the whole pipeline (Opus, "Advancing workflow optimization")
(from session 2026-09-22, backfilled by consolidation 2026-09-23 from commit `b0e4d3a` — the session ended without a note.) Fourteen reviewers read all of `Code/BandInfoForm/` (app, tools, db, n8n, ops, backup, staging); 184 raw findings deduped to 127, 124 confirmed and fixed, then a diff re-review caught and repaired 10 regressions. The P0: every welcome link had opened a blank, un-prefilled form since the token signer went timed on 09-16, because `draft_emails` still signed untimed — links already in inboxes are now honoured read-only until their show date. P1s included the public `/stage-plot/` route serving any file in the venue folder (the internal advance doc too), Edit Show on a booking-less show clobbering an existing booking and re-welcoming the band, and RiffPay re-import wiping staff flags. New staging checks were added to `run_tests_extra.py` but **not run** (the staging clone needed a permission that session lacked), and the commit doesn't say whether it was deployed — flagged in `questions.md`.

