# memory.md
*Last consolidation: 2026-09-14 — log in memory-archive-2026H2.md*

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

*Newest first. Older entries live in `memory-archive-2026H2.md`.*

### 2026-09-14 — DigiBot: Q225 staff help bot for Slack (plan only)
Brian asked for an n8n-hosted chatbot his crew can reach from Slack that answers Quantum 225 questions from the DiGiCo wiki (digico.tinydoorstudios.com, 122 pages, ~170K tokens) plus the official manual, and that can be "taught" the venue-specific workflow. Inventoried the wiki repo (`Code/DigicoWiki/`), the n8n VM (2.36.8, 2 vCPU / 3.8 GB — no room for a local model, no pgvector in the n8n Postgres), and existing Slack/LLM plumbing (Gear Tickets user token, Groq only). Wrote the plan, nothing built: `Code/DigicoBot/PLAN.md` + `PLAN.pdf`. Design: Slack Events → n8n Slack Trigger → Claude agent with `search_wiki` (hybrid pgvector + Postgres FTS over heading-chunked pages, tiered teachings › venue › how-to › manual), `read_page`, `log_gap`; thread = memory; teach loop via `@DigiBot teach:` / 📌 into a bot-maintained `/venue/teachings-inbox` page; weekly gaps digest; ~10 venue pages under `content/venue/` as the "training" layer. Five decisions are Brian's (model Opus 5 vs Sonnet 5, embeddings vendor, bot name/channel, scope, who can teach) — ask one at a time on go.

### 2026-09-14 (morning) — Band Advance review pass BUILT + DEPLOYED
Brian answered the review's questions one at a time and chose "build and deploy tonight". Built on `advance-system` in its own worktree (`.worktrees/advance-system`), staging-tested with a new scripted harness (`tools/staging/`, 70/70), deployed 23:26/23:27 on 9/13 (app + migrations + timers; n8n send + lifecycle workflows), day-before greeting fix redeployed 09:01 on 9/14. Live: per-cell doc provenance (`filed_docs.cells`), booking unique index + DISTINCT ON, token hard-fail, name-plausibility gate + honeypot, 48h reminder gap (Amador tier-3 pre-skipped), TBD schedule times, CANCELLED doc rename + header, bilingual reminders, day-before confirmation (`dayahead.py`), Needs-you dashboard panel + digest queue (`digest_items`), nightly 06:30 full run, deploy branch guards, multi-attachment support (tech pack = `_attachment-2 …` in the venue's Series Email Templates folder). First morning: nightly 06:30 ran clean, digest 07:00 sent, 9am lifecycle ran, zero band emails (correct). Not done: `git push` (denied by the auto-mode classifier — Brian runs it), ff-merge of `main` (two dirty files in the shared checkout: about-me/memory.md, Code/landing-redesign/deploy/index.html), tech-pack content (drafts in `Handoffs/tech-packs/`), ZP Pool n8n workflow erroring every minute (unrelated, reported only).
(Updated 2026-09-14: the ff-merge happened — `advance-system` merged into `main` as 3ca555c during pipeline-fix. Previously listed as not done.)

### 2026-09-13 — Claude Code efficiency audit (report only, no fixes applied)
Full audit of settings, hooks, skills, memory tiers, launchd jobs, git state and 30 days of transcripts. Four silent breaks: (1) no scheduled task exists anywhere for memory-consolidation — last run 2026-08-16, this file is over its 18KB cap with nothing logged after 08-25; (2) the Cowork skills plugin still serves the July-12 show-deep-build, which shows up in Code sessions as a second `anthropic-skills:show-deep-build`; (3) `advance-system` is 144 commits ahead of main and unmerged, main is 2 ahead of origin, and stash@{2} holds ~838 lines of Buffalo Wabs spec/build work committed nowhere; (4) 1,142 screenshots in 30 days, five sessions over 85 each. Fixed per-session load is ~90KB (~22K tokens); about 13KB of CLAUDE.md is show-build-only and about-me.md is mostly duplicate. Contradictions: /scope wants 5 batched questions vs one-at-a-time; CLAUDE.md says weasyprint for show docs but the packet builder doesn't use it; settings.local.json allows a dead tool name. Fix list delivered in chat, awaiting go.
(Updated 2026-09-14: the memory-consolidation scheduled task now exists (`~/.claude/scheduled-tasks/memory-consolidation/`, created 09:21) and ran the same morning; `advance-system` was merged into `main` (3ca555c) and the Buffalo Wabs stash recovered (9111f31). Previously: no task, branch unmerged, stash uncommitted.)

### 2026-09-13 (late) — Band Advance: Fable review pass (read-only)
Reviewed the whole `advance-system` branch + live VM + advance DB after the 23-fix deploy. Changed nothing, sent nothing. Report: `Handoffs/band-advance-review-2026-09-13.{md,pdf}` (9 pp). Six HIGH items: duplicate booking rows double-send the welcome (no unique index, no DISTINCT); returning-band docs pre-fill from the PRIOR show's submission and never-overwrite then blocks the new answers (design fork: this-show-only vs per-cell provenance); Check Token returning [] reads as "sent"; holds only run inside a package run (needs a nightly full run); auto-attach can hijack another band's booking; and the repo working tree is shared across Claude sessions — another session switched the checkout to `main` at 22:49 mid-review (advance-system is 144 commits ahead, ff-mergeable). Verified n8n active versions carry Confirm Sent + Mark Cron; tomorrow's 9am sends one email (Amador Sisters tier-3). Research: tech pack up front, T-1 confirmation, SMS channel, single source of truth are the borrowable ideas; no off-the-shelf tool does the Word-doc-in-Dropbox filing. Questions queued one at a time starting with the doc-fill design fork.
(Updated 2026-09-14: the branch-switch hazard is defused by the single-branch merge; the shared working tree itself still applies — see [[shared-worktree-branch-hazard]].)

### 2026-09-13 — Show pipeline audit (fine-tooth read of the whole chain)
Brian asked for a full evaluation of the show pipeline. Read every skill, `_system/`, `_shared/`, both patchers/templates, `build_packet.py`, the KB pipeline articles, all show folders + status files, the wiki push tooling, the advance pipeline and the repo's branch state. Report: `audio/_system/PIPELINE-AUDIT-2026-09-13.{md,pdf}` (6 pp). Headline findings: (1) the workspace sits on three branches (`advance-system` is the real head at 09-13; `main` 08-30; `show-pipeline-2026-07-26` 08-03) and the desktop app swaps between them per session with "epitaxy: pre-switch" stashes — this session started on the July branch with the old batch-the-round skill, no August show folders and a 08-03 memory.md, then switched to main mid-run; (2) `new-show`/`send-it`/`fsq-wiki-push` live only in `~/.claude/skills/`, unversioned, and `send-it` quotes the retired FSQ template size; (3) the hard rules are restated in ~10 files and have drifted (weasyprint rule is dead — everything is reportlab; "packet PDF is a separate request"; "batch the round" still in the KB specs; "verify on the console" still printed by both builders); (4) spec-vs-.md authority contradiction + no rev/hash in `show.status.json`; (5) harvest loop is write-mostly — Repertoire/Shades/Sexton/2nd Wind 08-08 never published or harvested, D6 row flagged 3× and still wrong, eq-advisor-log has 5 entries for ~15 builds; (6) six bookkeeping targets per session; (7) four disconnected intake tools (ShowBuilder, Patchbay, advance form, chat); (8) publish skill does DB surgery on every push; plus code nits (HPF defaults to 20 silently, Q validated to 20 not 10, `!!` name warning doesn't fail the build, per-show patcher copies go stale, retired templates left at venue roots, no regression test, .ses in git). Recommended a four-step program: single branch + orphan skills into the repo today; RULES.md + SKILL diet + status-file rev/hash/harvested this week; PENDING harvest queue consumed at build start + `publish_show.py` + `selftest.py` next; then a canonical show key bridging the advance DB to the show scaffold. No files changed besides the report and this entry.
(Updated 2026-09-14: pipeline-fix Phase A committed as 4d5a56f — one long-lived branch (`main`), `new-show`/`send-it` moved into `audio/_skills/` and symlinked, ShowBuilder + eval folders archived to `_ARCHIVE/2026-09-pipeline-fix/`. Later phases were still in flight in another session at consolidation time. Previously: three branches, orphan skills.)

### 2026-09-13 (latest) — Band Advance QC audit: 23 fixes decided, built, tested, deployed live
Full read-only audit of Code/BandInfoForm + the live VM, then Brian decided all 23 items one question at a time (spec: `Handoffs/band-advance-audit-decisions-2026-09-13.md`) and said "run it all". Built, tested on the VM against a cloned DB + copied Dropbox folders + a local mail stub (70/70 checks), preflighted against an untouched clone of real data (0 holds, nothing to send, only blank Event Type / Salsa Flat cells filled), then deployed to live. Brian's standing rule for the session: **nothing I run may send an email** — all live one-off steps ran with the new `ADVANCE_MAIL_DISABLED=1` kill switch, n8n's new Confirm Sent node was verified with a throwaway mock workflow (202 -> 200, 4xx -> 500, unreadable status -> 200 so a real send is never re-sent), and the one doc-change notice my run produced (Wishy monitors: doc 5, pipeline 3 — Brian's own 18:27 edit) was marked notified and reported in chat instead of emailed. Key changes: filed docs never overwritten (tools/docmerge.py + filed_docs registry, 18 live docs renamed in place to headliner names), sends stamp only on confirmed Graph 202 with retry + one alert per show/kind/day, advisory-locked lifecycle, closest-tier-only reminders, cancel/hold/merge (tools/holds.py, /show/<id>/hold), name-mismatch auto-attach with Confirm/Detach, signed artist token, stage plot carry-forward, booking rules (email/series/slot clash; Event Type removed, "Stand-Alone Internal"/"3rd Party"), vehicle counts everywhere, day-of contact = mix engineer + part-time-staff line, Salsa copy (Nick Radina parking, escort rep field, no riser), shared status labels + sheet STATUS cleanup, Status Log never overwritten when unreadable, nightly DB dump to both NAS (02:40, verified), 10:15 9am-check watchdog, gunicorn gthread 4x4 120s, dropbox_exclude.sh no longer deletes (VM copy replaced), delete/create-draft n8n workflows unpublished, token-bearing temp files and 124 app.py.bak files removed. Pre-audit backups: `/var/backups/band-advance/pre-audit/` (DB) and `~/advance-audit-backups/` on the VM (sheet, Status Log, Salsa copy, exclude script). Commits f5e21e2 + 02a1a15 on advance-system (not pushed). Gotchas: a `pgrep -f` pattern inside an `ssh "..."` string matches its own bash process — use the `[r]un_now` bracket trick; a global string replace turned `_internal_auth()` into infinite recursion (caught in staging). Not done: Graph client-secret expiry (not readable with Mail.Send-only perms), KB wiki article update, git push.

### 2026-09-09 — Cold Storage rotates at 8; the backup completion email became its own n8n workflow
Two follow-ups to the backup system built the same day. (1) **Retention is now per-target** — `TARGETS` lines are `name|host|dir|keep|monthly`. Cold Storage is a **flat rotating 8** (Brian: it's the box he opens, 8 weeks is what he wants there); the Audio NAS keeps the deeper tail, 12 weekly + 24 first-of-month, so nothing older is truly gone. Tested rather than assumed: seeded 11 archives onto Cold Storage, ran once, 8 left, newest kept. (2) **New n8n workflow "Band Advance — Backup Report (Cold Storage)"** (`band-advance-backup-report`) now owns the completion email — the script POSTs facts, the workflow formats and sends as Production@3cdc.org via the same Graph credential. Subject is blunt: *complete* or *FAILED on Cold Storage*, and **complete requires the sha256 to have been re-verified ON the NAS**, not merely that a copy arrived. Body: archive + size, verified y/n, how many of the 8 held (newest/oldest labelled), what rotated off, row counts, failures. First real send = Graph 202, execution 497168. **Two gotchas cost cycles:** zsh (the TrueNAS login shell) does NOT word-split an unquoted variable, so a doomed-file list has to go through a file and be read line by line — see [[truenas-zsh-glob-abort]]; and **n8n only mounts a newly imported webhook route on restart** — a published, active, perfectly good workflow 404s its first POST until then, and the route lags `/healthz` by another 10-20s after the restart — see [[n8n-webhook-needs-restart]]. `install_backup.command` step 4b now deploys the workflow and restarts n8n itself. Still open and offered but not built: a watchdog for the case where the VM or n8n is down at 03:15, which today means silence rather than an alarm.
