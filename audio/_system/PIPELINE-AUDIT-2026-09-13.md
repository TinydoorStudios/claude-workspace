# Show Pipeline Audit — 2026-09-13

*Nyquist. Read end to end: the five skills, `_system/`, `_shared/`, both venue patchers and templates, `build_packet.py`, the KB pipeline articles, every show folder and its status file, the wiki push tooling, the advance pipeline, and the repo's branch state. Findings ranked by how much they cost you per show, then the recommendations as a short program of work.*

---

## The short version

The core machinery is sound. One spec drives every output, the .ses engine verifies byte-for-byte and reads back, the status file tells later sessions where a show sits, and the question round is now one fork at a time. Where the pipeline bleeds time is everything around that core: the workspace lives on three git branches that the desktop app swaps between sessions, the same rule is written in ten places and has drifted in several, show facts are captured by four disconnected tools, and the harvest loop that is supposed to make each build cheaper than the last almost never runs. Fixing those four things is a week of work and would remove most of the bookkeeping tax that every session currently pays.

---

## 1. The workspace itself is unreliable: three branches, three stashes

This session started with `show-pipeline-2026-07-26` checked out. On that branch the show-deep-build skill still says "batch the question round", the six August show folders do not exist, `memory.md` ends on 2026-08-03, and `Code/BandInfoForm/` contains one subfolder. Partway through, the tree switched to `main`, and everything reappeared. The three stash entries named `epitaxy: pre-switch from …` are the tool parking uncommitted work at each switch.

Branch state today:

| Branch | Last commit | Holds |
|---|---|---|
| `advance-system` | 2026-09-13 | All September advance-form work AND all six August shows. This is the real head. |
| `main` | 2026-08-30 | August shows, no September work. |
| `show-pipeline-2026-07-26` | 2026-08-03 | Six weeks stale. Old skill text, no August shows. |

Consequences already on record: the 2026-08-06 IMPROVEMENTS entry is titled "I built this show on `main`, which is 10 commits behind" and the double bill had to be rebuilt on reconciled tooling. The 2026-08-25 self-audit committed two weeks of stranded work but left the branch model in place, so the same failure is armed again. A deep build that starts on the wrong branch runs a six-week-old skill and never knows.

**Fix.** Merge `advance-system` into `main`, delete the other two branches, pop and resolve the three stashes, and treat this repo as single-branch from now on. It is a workspace, not a codebase with parallel feature work. Add one line to the session-start block in `CLAUDE.md`: if `git branch --show-current` is not `main`, stop and say so before touching a show.

## 2. Skills live in two homes and one is already stale

`show-deep-build`, `show-wiki-push`, `fable-parity`, `memory-consolidation` and `tds-infrastructure` are in `audio/_skills/`, versioned, symlinked into `.claude/skills/`, and rebuilt into `.skill` zips by the pre-commit hook. `new-show`, `send-it` and `fsq-wiki-push` are plain folders in `~/.claude/skills/`, outside the repo, unversioned, uncovered by the packaging guard. `PIPELINE.md` says all skill sources live in `audio/_skills/`, which is not true.

`send-it` is already wrong in two places: it quotes the FSQ template as 39,910,618 bytes (it has been 39,910,700 since the 2026-08-01 drop, and the patcher enforces the new size), and it tells you to copy the patcher into the show folder while show-deep-build tells you to run the venue patcher directly.

**Fix.** Move the three into `audio/_skills/`, symlink, add them to `build-packages.sh`. Delete `fsq-wiki-push` outright; its only content is "go run show-wiki-push".

## 3. Every rule is written ten times, and they have drifted

The same hard rules (vocals cuts-only, whole dB, band numbering, FSQ deeper cuts, ch 10 reserved, wireless faders, ribbon no 48V, reverbs required, one question at a time) appear in the global `CLAUDE.md`, the project `CLAUDE.md`, `NEW-SHOW.md`, `ROUTING.md`, `SKILL.md` (three times: the rule, the constraint card, the guardrails), `decision-flow.md`, `pre-commit-audit.md`, the scaffold skeleton, `build_packet.py` comments, and three KB articles. A rule change is a ten-file edit, and it misses. Contradictions found today:

- **PDF engine.** Project `CLAUDE.md` says "weasyprint (locked, not reportlab)". `ROUTING.md`, `pipeline-spec-fsq`, `pipeline-spec-memo` and `show-processing-pipeline` all say the .md ships with an .html and a weasyprint PDF. No HTML is produced anywhere; `build_packet.py`, `show-packet-builder-template.py` and `make_mobile_patch_sheet.py` are all reportlab. The weasyprint rule is dead and should be deleted, not "fixed".
- **Stages.** `show-processing-pipeline` says the packet PDF "is always a separate request, not generated automatically after Stage 2". `build_packet.py` writes it on every run. `ROUTING.md` says the pipeline is two-stage; `PIPELINE.md` says five.
- **Question round.** `main`'s skill says one at a time (2026-08-08). `pipeline-spec-fsq` line 48 and `show-processing-pipeline` still say "batch into ONE up-front round".
- **Console verification.** The 2026-07-19 rule says it is never a gate. `build_packet.py` ends with "then verify on the console" and the engine ends with "load on the Q225 and verify before the file is trusted". The ShowBuilder README says "Console verify, then wiki-publish."
- **ShowBuilder article.** Last updated 2026-07-09, still describes the pre-06-25 app that computed EQ, had an approve-and-build gate and produced the .ses. The README on disk says facts-only. The wiki page is telling any reader the wrong thing.
- **Active Shows.** LDB, FSQ Salsa, Drowsey Lads and Israeli Chamber Project sit under "Active" frozen at May 16. `questions.md` itself asks whether LDB ever happened.

The skill also carries its own history inline: "(locked 2026-07-05)", "(upgraded 2026-07-26 from …)", "(rule changed 2026-07-19)". That makes the instructions read like a changelog. Between `CLAUDE.md`, `memory.md`, `ROUTING`/`NEW-SHOW`, the skill and its references, and the KB articles the FSQ routing row names, an FSQ build loads about 300 KB of text before the first search. Most of that is restatement.

**Fix.** One `audio/_system/RULES.md`, numbered, dated only in a footer. Everything else points at it by number and stops restating. Cut `SKILL.md` to the procedure and checklists (target under 12 KB), move the dated history to `IMPROVEMENTS.md` where it belongs, and delete the constraint-card list from the skill body since it becomes "write RULES.md in your own words". Retire the ShowBuilder article or rewrite it as three paragraphs.

## 4. Source of truth is ambiguous and the state file is incomplete

The skill says "one spec, outputs can't drift". `active-projects.md` says "the FOH .md is authoritative, not the spec" because Nasty Nati and Back to Black were revised in the .md after the spec was written, and re-running `build_packet.py` silently overwrote the good .md. Both are now standing practice, and they contradict each other. The wiki push still copies `spec.json` "for reproducibility" even when it is the stale one.

`show.status.json` has no `rev` field and no hashes, so nothing can detect this. Pre-07-19 shows have no status file. Back to Black has only `published` stamped. Nothing records whether a show was harvested.

**Fix.** Decide: the spec is the source. A late revision edits the spec, bumps `rev`, and regenerates everything, including the .ses. Enforce it in code: `build_packet.py` records the md5 of the .md it wrote in the status file; on the next run it refuses to overwrite an .md whose hash differs unless `rev` was bumped. The engine records the md5 of the .md it consumed alongside `ses_built`. Add a `harvested` stage. Backfill status files for the four pre-July shows in one pass.

## 5. The harvest loop is write-mostly

This is the step that is supposed to make each build cheaper than the last, and it is the step most often skipped.

- Repertoire, The Shades, Ric Sexton (all 2026-08-01/02) and 2nd Wind (2026-08-08) sit at `ses_built`, never published, never harvested. Their "pending harvest" columns in `active-projects.md` are six weeks old.
- Buffalo Wabs was published 08-24 and not harvested.
- `_learning/eq-advisor-log.md` has five entries for roughly fifteen builds.
- `_learning/STAGED-2026-07-16-back-to-black.md` sat unactioned; the SM57 finding in it was rediscovered ten days later.
- The Audix D6 row has been flagged wrong in three consecutive log entries and is still wrong in `mic-library.md`. The build then pays for a web search that disagrees with the KB every time.
- `questions.md` carries thirty-odd items, several from May, plus a "KB Write-Backs Awaiting Brian" pile that only grows.

Because the KB never absorbs what the research found, every unit on every show pays the full research price, and the cross-check against the KB is weaker than it should be. Your rule that the KB is for longevity, not research, is right. The half that is missing is the longevity.

**Fix.** Make harvest part of publish, not a separate close-out nobody triggers: `show-wiki-push` ends by writing the build's `kb_writeback` and `reconciliation` lines into `_learning/PENDING.md`. The next deep build opens by clearing that queue one item at a time ("Change the D6 row to 700–750 Hz, −17 dB? y/n"), same interactive prompt as the locker forks. A weekly scheduled task lists shows past their date that are not published or harvested. That turns a growing pile into a two-minute prompt at the start of each build.

## 6. Six bookkeeping targets per session

After meaningful work the instructions require updates to `active-projects.md`, KB `CHANGELOG.md`, `IMPROVEMENTS.md`, `questions.md`, `memory.md`, and auto-memory. The consolidation passes then spend their runs reconciling them: the 2026-08-04 entry documents a two-week watermark gap in two of the six, the CHANGELOG is landing entries out of order, `IMPROVEMENTS.md` is missing the 08-08 process change, and `questions.md` has grown a meta-section about the state of the other logs. That is the tax showing up as work.

**Fix.** Three targets, each with one job: git history (what changed, with the commit message as the changelog), `active-projects.md` (current state), auto-memory (durable preferences). Keep `memory.md` as the lean journal you already chose. Retire `IMPROVEMENTS.md` (its content is commit messages) and generate the KB `CHANGELOG.md` from the Wiki repo's git log, which is already auto-committed. `questions.md` stays but gets split into "needs Brian" and "queued write-backs", the second of which is the PENDING queue above.

## 7. Four intake tools, none connected

Show facts arrive through ShowBuilder (`brief.json`, port 8095), Patchbay (patch sheets, port 8096), the band advance form (Postgres: stage plot, backline, monitors, IEMs, wireless, contact), and hand-typed lists or rider PDFs in chat. None hands off to the next:

- The advance pipeline files the band's stage plot under `Advancing/FSQ/2026/09 September/…`; the deep build expects it at `audio/Fountain Square/YYYY-MM-DD Show/<Show> - Stage Plot.pdf` and asks you for it again.
- Artist identity differs per system: the advance DB keeps "Buffalo Wabs" and "Buffalo Wabs and the Price Hill Hustle" as two artists; the show folder uses the long name; the wiki slug a third form.
- `Show Status Log.xlsx` tracks advance state and knows nothing about paperwork; `show.status.json` tracks paperwork and knows nothing about the advance.
- ShowBuilder's README still ends with "Console verify, then wiki-publish."

**Fix.** A canonical show key, `<venue>-<date>-<slug>`, shared by the advance DB, the show folder name, `show.status.json` and the wiki page. When staff books or a band submits, `run_now.py` calls `scaffold_show.py`, drops the stage plot in the right place with the right name, and writes a `brief.json` skeleton from whatever the form captured. The Show Status Log gains Packet / .ses / Published columns read from the status files. Then ShowBuilder can retire (its wizard is the advance staff hub's job) and Patchbay becomes a renderer that reads the spec.

## 8. Publish is eight steps of server surgery

`show-wiki-push` SSHes into Proxmox, runs psql against the Wiki.js database, optionally restarts the container, and if the render column is stale, patches it with SQL. That is operations inside a skill, on every push. `make_show_page.py` and `kb-publish.sh` already exist. One `publish_show.py` that writes the page, copies the assets, runs `kb-publish.sh`, stamps `published`, and verifies with an HTTP 200 on the page and one asset URL would make the push a single command. Escalate to the database only when the HTTP check fails. Note also that `make_show_page.py`'s docstring says it reads `spec.json` while `active-projects.md` says pages are built from the .md; one of them is wrong.

## 9. Code-level findings

None of these has bitten yet; all are cheap.

- `build_packet.py`: a channel with no `hpf` silently gets 20 Hz written to the .md and the .ses (`ch.get("hpf", 20)`). Should be an error.
- Q range is validated at 0.3–20 in both the spec validator and `md_lint.py`; the console is 0.3–10 per `CLAUDE.md`. A Q of 15 passes lint and gets patched.
- The engine's `!! fader N: only n name fields written` warning does not fail the build, and `ses_built` still stamps.
- Both scripts end with "NEXT: verify on the console" (see section 3).
- Per-show patcher copies: every show folder gets a 40-line `apply_<short>.py` that only imports the shared engine. After the 2026-08-01 recalibration the copies in older folders carry stale constants (Repertoire's is 4,862 bytes against the current 5,381). The tripwire will abort a rebuild from one, which is good, but the copy has no purpose. Stop copying; call the venue patcher.
- Stray retired templates at venue roots: `Fountain Square/brian fsq start.ses` (3,779,766 bytes, the retired June file, same filename as the live one in `_TEMPLATE/`) and `Memorial Hall/brian memo v2.ses`. Move both to `_TEMPLATE/_retired/`.
- `rename_fsq.py` still calibrated to the retired template (known since 08-01).
- Show-folder clutter under Fountain Square: three Izzy Escobar folders plus "Izzy 2.0 Deep Think", `hot-mag 2`, `hot-mag 3`, `hot-mag A-B eval`, "(Brief Test)". Archive to `_ARCHIVE/`.
- No automated regression test. The engine's "md5-identical" regression was done by hand once. A `_shared/selftest.py` that patches `CALIBRATION_TEST - FOH Channel Processing.md` against each template and compares to a golden md5, builds a fixture spec through `build_packet.py`, and lints, wired into the pre-commit hook, is the one test that pays for itself: the output goes onto a console.
- `.ses` files in git: about 40 MB per show. The 08-25 note already flagged it. Exclude `*.ses` (regenerable from .md + template) or use git-lfs before the repo becomes painful to clone.
- `memory.md` on disk says weasyprint was fixed 09-11 and needs `DYLD_LIBRARY_PATH`; nothing in the pipeline uses it. Delete the rule rather than maintain the fix.

## 10. One tension worth naming

The `UserPromptSubmit` hook injects "do not narrate, work silently" on every prompt. The skill demands visible searches, a visible constraint card, and a fifteen-line audit answered "in visible output with the evidence quoted". Both are your rules and they collide on every build. Add one sentence to the hook: research output, the question round, and the pre-commit audit are deliverables, not narration.

---

## What is working

The shared engine with the offset tripwire, stray-byte check and full readback. One spec driving md, xlsx, both PDFs, the MASTER with real page links, and the phone patch sheet. The status file. One question at a time with the recommendation first. The packaging guard on commit. The advance pipeline's disk-first writes and weekly self-restoring backup. Those are the parts to build on; nothing above proposes touching them.

---

## Recommended order of work

1. **Today, an hour.** Merge to one branch, resolve the stashes, move the three orphan skills into the repo, fix the `send-it` template size, delete the weasyprint rule and the two "verify on the console" lines, move the two stray templates.
2. **This week, a day.** `RULES.md` plus the SKILL.md diet. Rewrite or retire the ShowBuilder article. Backfill the four missing status files, add `rev`, hashes and `harvested`, and put the overwrite guard in `build_packet.py`. Publish or explicitly close the four unpublished August shows.
3. **Next, two days.** `PENDING.md` harvest queue consumed at build start; `publish_show.py`; `selftest.py` in the pre-commit hook; collapse the six logs to three.
4. **Then.** The show key and the advance-to-scaffold bridge, Show Status Log packet columns, retire ShowBuilder.

*Report and PDF: `audio/_system/PIPELINE-AUDIT-2026-09-13.{md,pdf}`.*
