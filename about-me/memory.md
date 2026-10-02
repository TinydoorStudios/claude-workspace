# memory.md
*Last consolidation: 2026-10-02 — log in memory-archive-2026H2.md*

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

### 2026-10-01 — ESP location picker
Booking form (`/booking`) now shows a required Location dropdown for Elm Street Plaza: Pavilion, North Plaza, South Lawn, Other (`forms_config.ESP_LOCATIONS`; sheet column choices in `fieldspec.EVENT_FIELDS`). Label is just "Location", venue-filtered with WP's Main Stage/Porch/Bandstand, cleared on venue switch. ESP locations carry no monitor cap or hidden questions, unlike WP. Committed 67abbbf + a3ce0ba, deployed, checked live. Existing ESP bookings with a blank location must pick one on next edit.

### 2026-10-01 — Advance workflow review (Memo + ESP)
Read-only audit of the band advance pipeline after Memo/ESP builds. VM healthy, no drift (fb26372), no send failures. Breaks found, not fixed: Memo "paused" doesn't gate day-ahead or post-show thank-you (A Man Named Cash would get a day-before with literal {parking_text} on 10/15); Memorial Hall still in the public universal-form venue dropdown; two duplicate Memo welcome Outlook drafts for A Man Named Cash created 21:07 with parking_sheet_sent_at falsely stamped, origin unknown (drafts aren't in mail.log, no access log); ESP work uncommitted + two untracked source snapshots block deploy. Risks: hand-edited Memo doc spawns an "(updated)" copy every run; Memo chases use universal wording; Finalize dead for Memo; Ricky Nye 10/21 "sent" stamp is a pre-live-send draft; n8n history only 1.5 days (prune cap), ZP Pool workflow erroring every minute. Efficiency asks: one venue registry, one paused gate. Then fixed #1/#2 + committed/deployed ESP as ebda1a9 (22:07): _paused_sql() on dayahead.due_shows + shows_due_for_thankyou, blocks_for always blanks unfilled placeholders, Memo off the universal venue pick + /submit refuses it; staging 60/60 memo, 23/23 x-esp, 158/158 core. ESP SPL ack mismatch ignored per Brian. 22:29 deployed: Memo hand-edit now keeps ONE "(updated)" side file (ledger-tracked), Finalize recap reads Memo from DB (memo_doc.values_for); test_memo 65/65, core 158/158 (done on Sonnet 5.5 at Brian's request). Cash drafts: Brian deleted both by hand, nothing sent; parking_sheet_sent_at cleared on 4654 (packet back on the dashboard needs list). Still open: Memo hand-edit copy loop, Memo chase wording, Finalize dead for Memo, snapshot dirs untracked.


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

