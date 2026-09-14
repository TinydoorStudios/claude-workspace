---
name: pipeline-fix
description: Executes the 2026-09-13 show-pipeline audit as one run. Trigger when Brian says "fix the pipeline", "run the pipeline fix", "do the audit fixes", or "/pipeline-fix". Reads audio/_system/PIPELINE-AUDIT-2026-09-13.md, asks the six decisions that are his to make (one at a time, recommendation first), then works the four phases in order with a git commit after each, and reports at the end. Nothing is deleted without a git commit before it.
---

# Pipeline Fix — the audit, executed

Source of truth for what to do: `audio/_system/PIPELINE-AUDIT-2026-09-13.md`. Read it in full
first. This skill is the runbook; the audit holds the reasoning.

## Step 0 — Preconditions (stop on any failure)
- `git status` clean or only files you are about to commit. If dirty with unrelated work, commit it
  first as "pre-fix snapshot".
- `git fetch --all`. Note the heads of `main`, `advance-system`, `show-pipeline-2026-07-26`.
- `git stash list` — note the three `epitaxy: pre-switch` stashes.

## Step 1 — Decisions (AskUserQuestion, ONE at a time, recommended option first)
1. **Branch merge.** Merge `advance-system` into `main`, then delete `advance-system` and
   `show-pipeline-2026-07-26` (local + origin)? (Recommended: yes.)
2. **Stashes.** Pop each `epitaxy` stash onto main, resolve, commit; or drop them after showing
   `git stash show --stat` for each? (Recommended: pop and inspect; drop only if empty/duplicate.)
3. **Source of truth.** spec.json is authoritative; late revisions edit the spec, bump `rev`,
   regenerate everything incl. the .ses. (Recommended: yes.)
4. **Four unpublished shows** (Repertoire, The Shades, Ric Sexton, 2nd Wind 08-08): publish now
   via show-wiki-push, or stamp `published` as "closed unpublished" and harvest only? (Recommended: publish.)
5. **Logs.** Retire `_system/IMPROVEMENTS.md` (git history takes over) and generate KB CHANGELOG
   from the Wiki repo git log? (Recommended: yes.)
6. **ShowBuilder + .ses in git.** Retire ShowBuilder (archive `Code/ShowBuilder`) and exclude
   `*.ses` from git going forward (keep history)? (Recommended: yes to both.)

Record the answers at the top of the run report. Anything answered "no" is skipped, not improvised.

## Step 2 — Phase A (an hour): the workspace
- Merge per decision 1; resolve stashes per decision 2. Commit. Push.
- Move `~/.claude/skills/new-show` and `send-it` into `audio/_skills/`, symlink back into
  `.claude/skills/`. Delete `fsq-wiki-push` (both copies). Brian builds shows in Claude Code, not
  Cowork (confirmed 2026-09-13): retire the `.skill` zips, `build-packages.sh` and the pre-commit
  packaging hook (`git config --unset core.hooksPath` once selftest.py replaces it in Phase C), and
  delete every "re-upload in Cowork" / "Cowork installs are snapshots" line in CLAUDE.md,
  PIPELINE.md, questions.md and active-projects.md. Fix `send-it`: template size 39,910,700; "run the venue patcher directly, never
  copy it".
- Delete the weasyprint rule from project `CLAUDE.md`, `ROUTING.md`, `pipeline-spec-fsq`,
  `pipeline-spec-memo`, `show-processing-pipeline`. Replace with "all show PDFs are reportlab".
- Remove the two "verify on the console" NEXT lines (`build_packet.py` main, `q225_ses_engine.py`
  main_cli). Replace with "NEXT: publish on Brian's go (show-wiki-push)".
- Move `Fountain Square/brian fsq start.ses` (3,779,766 B) and `Memorial Hall/brian memo v2.ses`
  to their venue `_TEMPLATE/_retired/`. Archive the Izzy/hot-mag/Brief Test folders to
  `audio/_ARCHIVE/2026-09-pipeline-fix/`.
- Session-start guard: add to the session-start block of `~/.claude/CLAUDE.md`: "run
  `git -C ~/Documents/Claude branch --show-current`; if not `main`, stop and tell Brian before
  any show work."
- Commit: "pipeline-fix A: one branch, skills in repo, dead rules removed".

## Step 3 — Phase B (a day): rules, state, code guards
- Write `audio/_system/RULES.md`: every hard rule from the constraint card, NEW-SHOW
  don't-forgets, ROUTING global rules and the KB specs, numbered, deduplicated, dated only in a
  footer. Then make each of those places a pointer ("Rules: `_system/RULES.md` R1–R24").
- SKILL.md diet: keep procedure + checklists + Step 2b card format + spec/build commands; move
  every dated "(locked/upgraded/changed YYYY-MM-DD …)" clause to `IMPROVEMENTS.md` (or the commit
  message if decision 5 = yes). Target ≤ 12 KB. Rebuild the .skill zip (hook does it).
- KB `pipeline-spec-fsq` / `pipeline-spec-memo` / `show-processing-pipeline`: batch-the-round →
  one at a time; "Stage 3 separate request" → built every run. Rewrite `showbuilder.md` to three
  paragraphs (facts-only capture, retired if decision 6 = yes). Move the four May "Active Shows"
  to a "Stale / confirm with Brian" list.
- `show_status.py`: add `rev`, `md_md5`, `ses_md5`, `spec_md5` fields and a `harvested` stage.
  `build_packet.py`: stamp md5s; refuse to overwrite an .md whose md5 differs from the stamped one
  unless `--rev` is higher than the stamped rev. Engine: stamp `md_md5` at `ses_built`.
  `make_show_page.py`: read the .md (per decision 3 the spec, so regenerate the .md first).
- Backfill `show.status.json` for Verve Pipe, Blue Eighty-Eight, Izzy 2026-06-26, Hot Magnolias,
  Gospel Awards, Seals & Crofts 2, Brit Pack, Back to Black (retroactive stamps from file mtimes,
  note "backfilled 2026-09-13").
- Code nits: missing `hpf` → validator error; Q range 0.3–10 in validator + `md_lint.py`; `!!`
  name-count warning → `ok = False`; scaffold no longer copies the patcher (prints the direct
  command instead); recalibrate or retire `rename_fsq.py`.
- Publish / close the four shows per decision 4, harvesting each (Step 4 queue).
- Commit: "pipeline-fix B: RULES.md, skill diet, status hashes, validator guards".

## Step 4 — Phase C (two days): the loops
- `_learning/PENDING.md` queue: `show-wiki-push` appends each build's `kb_writeback` +
  `reconciliation` lines on publish. `show-deep-build` Step 1 gains: "open PENDING.md; for each
  item AskUserQuestion approve/skip; approved items are written to the KB article and staged for
  wiki-publish; the item is removed." Seed it now with the D6 row (700–750 Hz, −17 dB; +17 dB @
  10–12 kHz), the Beta 98H/C placement note, the four missing eq-starting-points rows, and every
  "pending harvest" cell in `active-projects.md`.
- `Live Sound KB/_tools/publish_show.py`: page + assets (via make_show_page) → kb-publish.sh →
  HTTP 200 check on the page and one asset → stamp `published` → append PENDING. DB patching
  only on HTTP failure. `show-wiki-push` becomes: confirm "SEND IT?", run it, report.
- `_shared/selftest.py`: patch `CALIBRATION_TEST - FOH Channel Processing.md` against both
  templates, compare md5 to goldens stored in `_shared/goldens.json`; build a fixture spec through
  `build_packet.py`; lint. Wire into `audio/_skills/git-hooks/pre-commit`.
- Logs per decision 5. Split `questions.md` into "Needs Brian" and a pointer to PENDING.md.
- Weekly scheduled task (`/schedule`): list shows past date not `published`/`harvested`.
- Hook text: append "Research output, the question round and the pre-commit audit are
  deliverables, not narration." to the UserPromptSubmit hook in `~/.claude/settings.json`.
- Commit: "pipeline-fix C: harvest queue, one-command publish, selftest, hook carve-out".

## Step 5 — Phase D (later, separate go): the advance bridge
Canonical show key `<venue>-<date>-<slug>` in the advance DB (`shows.show_key`), the scaffold,
`show.status.json` and the wiki slug. `run_now.py` calls `scaffold_show.py` on booking/submission,
files the stage plot as `<Show> - Stage Plot.pdf`, writes a `brief.json` skeleton. Show Status Log
gains Packet / .ses / Published columns. Ask before starting this phase; it touches the live VM.

## Step 6 — Report
One message: decisions taken, commits made (hashes), what was skipped and why. No manual step
remains — Claude Code runs the live skill copies directly.
