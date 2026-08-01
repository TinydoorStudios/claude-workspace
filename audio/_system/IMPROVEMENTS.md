# IMPROVEMENTS — self-improvement log

*Append-only. Dated entries describing structural/workflow changes to the audio project and why. Newest at the bottom.*

---

## 2026-05-30 — Single-project migration

**Context:** Brian moved to an Opus workflow — one project for all venues, a new conversation per show, venue named at the start. The old setup had drifted into 3–5 competing copies of every reference, which produced inconsistent results.

**Direction set this session:**
- `Live Sound KB/` is the single source of truth for all knowledge (venues, consoles, mics, EQ, reverb, pipeline/workflow). Every show conversation pulls its pipeline + specs from the KB.
- The KB grows by reinforcement: when an output lands well, the reusable part gets written back into the KB so the next conversation inherits it.
- Project state lives in `Live Sound KB/Wiki/active-projects.md` (canonical). Cowork auto-memory holds operational preferences/feedback. `about-me/memory.md` keeps session history.
- **Full consolidation approved** (not phased): duplicates move to `_ARCHIVE/`, patchers to `_templates/`, pipeline specs fold into the KB, CLAUDE.md slims to routing + pointers.

**Built this session:**
- `_system/ROUTING.md` — venue → folder · console · base .ses · patcher · PA · Tempest · KB specs to load.
- `_system/NEW-SHOW.md` — deterministic show-conversation flow.
- `_system/IMPROVEMENTS.md` — this log.

**Fixes this session:**
- CLAUDE.md startup path corrected: about-me is at `~/Documents/Claude/audio/about-me/`, not `~/Documents/Claude/about-me/` (the old path never existed, so startup reads were silently failing).
- CLAUDE.md startup block now points at `_system/ROUTING.md` + `NEW-SHOW.md` first.
- about-me/memory.md banner added: project state now canonical in the KB.

**Verified (no change needed):**
- Memo crowd-mic FOH EQ and the Royer AxeMount blend guide are already in KB `venue-memorial-hall`, referenced from `eq-starting-points`. The KB is internally consistent here. The duplicate is the inline copy in CLAUDE.md, which gets removed in the CLAUDE.md slim-down.

**In progress:**
- Memory meld: reconciling `about-me/memory.md`, KB `active-projects.md`, and Cowork auto-memory. Differences surfaced to Brian as questions before merging so nothing is lost.

**Next (consolidation manifest — pending memory-meld answers):**
- Fold the Memo + FSQ "Show Paperwork Pipeline Spec" into KB articles (`show-processing-pipeline` is Memo-centric; add an FSQ variant / generalize). These are the richest pipeline docs and currently live outside the KB.
- `_ARCHIVE/`: `Memo Work/`, `workflow start files/` (≈90% duplicate startup kits), `Fountain Square Knowledge/` (merge into `Fountain Square/` + KB), `Seals and Crofts 2 BACKUP/`, scattered `venue-notes.md` (after diffing against KB venue articles), redundant Seventh Heaven PDFs.
- `_templates/`: `apply_show_TEMPLATE.py`, `apply_show_TEMPLATE_FSQ.py`, `digico_ses_editor.py`, `show-packet-builder-template.py` — then update every path reference in lockstep.
- Strip embedded EQ/console/mic tables from CLAUDE.md once the KB is confirmed complete.

**EQ-table convention — RESOLVED 2026-05-30.** Brian confirmed the Q225 EQ: HPF + LPF + 4 bands; each band Shelf or Bell; any Bell band can be Dynamic; no separate low shelf. Canonical display order locked high→low (`HPF · LPF · Band 4 · Band 3 · Band 2 · Band 1`) with band numbers matching the console (Band 1 = LF, Band 4 = HF). The prior channel-card standard had the numbering backwards (Band 1 = High Shelf) — corrected across `pipeline-spec-memo`, `pipeline-spec-fsq`, CLAUDE.md, and the channel-card auto-memory. Note: the legacy EQ-starting-point data tables in CLAUDE.md still use the old column layout (flagged inline); they get remapped during the CLAUDE.md slim-down.

## 2026-06-12 — SOP routing correction + WP ClearCom SOP

**Mistake surfaced:** Claude created `Memorial Hall/SOP Stuff/` instead of using the canonical `audio/SOP Stuff/` root. Brian caught it. Files moved after gaining access to the audio root folder.

**Rule reinforced:** `SOP Stuff/` is a function folder at `audio/SOP Stuff/<venue>/` — parallel to `N8n/` and `Other/`, not nested inside any venue. Already stated in ROUTING.md "Where things live" and CLAUDE.md FILE STRUCTURE. Added to Cowork auto-memory (feedback_sop_routing.md) so it persists across sessions.

**Deliverable:** `SOP Stuff/WP/WP-SOP-ClearCom-Main-Stage.{md,html,pdf}` — Clear-Com intercom setup, 4-part SOP, 5 extracted photos, weasyprint-rendered PDF. Same .md+.html+.pdf format as FSQ Smaart SOP.

## 2026-06-03 — Reusable web-image-to-PDF workflow
- Web image binaries can't be fetched in-session (web tools return text; screenshots don't persist). Workaround built: a drop-folder + embed helper instead of scraping.
- `Live Sound KB/_tools/embed_refs.py` — scans a drop folder, EXIF-corrects, reads captions.tsv / sidecars, emits a captioned photo grid (standalone contact sheet or injectable flowables). Empty-state shows drop instructions.
- Convention: drop images in `Live Sound KB/_refs/<topic>/`, optional `captions.tsv` (filename TAB caption TAB credit), prefix 01_/02_ for order. Ask to rebuild → photos embed.
- Wired into the C3 deep-dive (`_tools/c3-build/make_c3_pdf.py`, self-locating, regenerates diagrams, writes to Outputs). New "Real-world reference photos" page auto-fills from `_refs/dpa-4099-c3/`.

## 2026-06-16 — ShowBuilder app (guided .ses + paperwork front end)

**Context:** Brian wanted a dashboard to customize Q225 `.ses` files end to end — pick a venue, lay out channels, choose instruments/mics, get genre/venue/mic-aware EQ + comp + Seventh Heaven Pro reverb suggestions, approve, and produce consistent show paperwork + a console-ready `.ses`, with the whole thing self-improving and wiki-synced.

**Built:** `Code/ShowBuilder/` — a Python/aiohttp web wizard that is a **front end to the existing pipeline**, not a reimplementation. It renders the locked `FOH Channel Processing.md` and calls the calibrated `apply_show_TEMPLATE*.py` patchers + `show-packet-builder-template.py`; it never re-derives the `.ses` byte format. Knowledge layer is KB-sourced (`reverb_presets.json` parsed from `reverb-reference-memo` by `build_knowledge.py`; `eq_rules.json` from CLAUDE.md starting points; `mics.json` from `mic-library`). Self-improves via `harvest.py` (new mics → library + KB queue; `learning/` log; KB write-back suggestions).

**Phase boundary in code:** everything except `build.py` runs on both Mac and the future Proxmox instance. Phase 2 = a package-only instance on the n8n VM behind cloudflared + a passcode on the TDS dashboard that emits the `*.spec.json` package; the Mac builds the `.ses` + final paperwork from it. Package format = `ShowSpec.to_dict()`, so phase 2 is wiring/auth/transport only.

**Verified:** Blue Eighty-Eight rebuilds byte-identical from its MD; Memo/FSQ fresh builds PASS at exact sizes (1,543,866 / 2,466,215); engine output sorts bands low→high so MDs satisfy the send-it B1<B4 gate.

**Finding:** the existing Memo MDs (Seals/Brit Pack/Gospel) are pre-2026-05-30 backwards B-numbering — logged in QUESTIONS for conversion.

## 2026-06-23 — eq-advisor skill + wired into the show flow

**Context:** Brian wanted a reusable EQ-decision skill that mirrors how he reasons (instrument → mic → community research → genre → room), usable across workflows, and self-improving.

**Built:** `eq-advisor` skill (installed plugin + source `_skills/eq-advisor/`). Searches the live-sound forums (PSW LAB, Gearspace) first, then cross-checks `eq-starting-points`/`mic-library` so the two verify each other; stops and asks on any uncertainty (Brian's rule: an unsure answer is ~3× worse than a pause). Cuts-first / whole-dB, inline + PDF in the console band layout.

**Wired into the show flow (the "always used" requirement):** `_system/NEW-SHOW.md` Stage 1 + harvest, `showbuilder`, `show-processing-pipeline`, pointer in `eq-starting-points`. The reachable surface is the workflow/KB layer — the ShowBuilder Python app (`Code/ShowBuilder/`) is outside the mounted folder and was **not** modified; app engine + skill both target the KB to stay consistent.

**Self-improving:** logs to `Live Sound KB/_learning/eq-advisor-log.md`, proposes write-backs to `mic-library`/`eq-starting-points` (a Brian override = ground truth), published via wiki-publish.

**Scope:** Q225 (Memo/FSQ) + Wing only by default; CL3/M32 only when Brian explicitly names that desk.

**Open:** KB edits are local — push on the next wiki-publish run. Optional follow-up: feed eq-advisor's output into ShowBuilder's app engine directly (needs Mac-side code access).

---

## 2026-06-24 — Deep research is the EQ standard + EQ Rationale PDF added to the pipeline

**Context:** Brian flagged that show paperwork was coming back instantly — a tell that the "research artist → mic vs instrument → forum check → genre → venue" flow wasn't actually running; it was inheriting KB/CLAUDE.md defaults. Evidence: the 2026-06-26 Izzy spec.json had kick notes referencing a "D6/Beta 91A blend" — there's no D6 in that show; a KB template bled in. Brian: "I'd much rather wait 1–2 minutes while the research is done than have you assume."

**Direction set this session:**
- **Deep research is now the standard EQ method for every show** (no KB-only mode). Artist + genre research **always** runs first; then every source is researched mic × instrument × genre × venue against the KB *floor*, with the searches actually run (visible), stopping to ask on uncertainty. KB is the floor, research is the point.
- **New required Stage-1 deliverable: the EQ Rationale PDF** — per-channel *why* (the notes Brian reads to learn the moves) plus a "what changed from the KB default / prior rev — and why" box.

**Built this session (proof-of-concept, kept as the reference):**
- `Fountain Square/Izzy 2.0 Deep Think/` — full deep-research rebuild of the Izzy Escobar show: `FOH EQ Reasoning.pdf` (the Rationale), `FOH Channel Processing.md`, `Izzy Escobar.ses` (patcher PASS, byte-identical to template), `Input List.xlsx`, `Show Packet.pdf`, `spec.json` (app_version `deep-think-1.0`). One driver script holds the channel data as the single source of truth → emits md/xlsx/spec/packet; patcher builds the .ses.
- Notable reasoned changes vs the KB-default Rev 2.0: vocal static −5@8k → dynamic de-ess + HPF 130→110 (KMS 105 isn't sibilant, protect the soul-vocal air/chest body); acoustic air moved off the 5k piezo-harsh zone to 8k with the 2k quack cut made dynamic; Beta 27 air moved to 9k so it stops doubling the SM57's mids; self-present mics (i5/D2/SM81 OH) eased; Tracks left near-flat (mastered stem).

**Pipeline docs updated:**
- `NEW-SHOW.md` — Stage-1 EQ step rewritten to mandate deep research + artist/genre-first; EQ Rationale PDF added as a required deliverable; don't-forget rule updated.
- `Fountain Square/Q225 SES Patcher SOP/FSQ SES Patcher - Claude Code Handoff.md` — "What you produce, per show" now lists the full packet incl. the Rationale PDF; note added that the patcher's input `.md` must be the deep-research output, not a KB default.

**Next:** turn the deep-research EQ flow into a skill (Brian's next step) so it can be invoked here with web + KB write-back access. Then optionally wire the Rationale + deep-research engine into ShowBuilder (needs Mac-side code access).

---

## 2026-07-01 — Memo template swap: recalibration is now a structural-scan job, not only a save-diff

The new Memo template (`brian memo june 2026.ses`) was calibrated without a console save-diff: the FSQ-format structure (stride-125 surface run carrying the real fader names + contiguous ~0x15A6 channel blocks with ~19 name copies each) is distinctive enough to locate by scan, and the tag semantics carry over between templates. The save-diff remains the gold standard — the first console load of a patched file is still the required proof — but a resave no longer blocks on Brian producing a ZZTOP edit pair first. Recorded in the patcher header + `pipeline-spec-memo`.

Also: both venue templates now live under a consistent `<Venue>/_TEMPLATE/` folder, and both patchers share the same engine, CLI, and tripwire pattern — future fixes should be applied to both or the engine should be factored into one shared module (flagged as a pipeline improvement).

---

## 2026-07-01 (later) — Efficiency pass executed

Brian approved the pipeline improvements list; all six items shipped the same night: (1) shared engine `_shared/q225_ses_engine.py` with both venue patchers as calibration wrappers — regression md5-identical incl. the console-verified Izzy build; (2) send-it KB mirror killed — skill reads the live KB; (3) `new-show` scaffold skill + `_system/scaffold_show.py`; (4) `_shared/md_lint.py` as an automatic hard gate in every patch run; (5) full every-channel readback built into every build + standalone `_shared/readback_verify.py`; (6) CLAUDE.md slim-down done in all three context files (legacy EQ tables + .docx format out, KB pointers + weasyprint rule in).

Engine lesson worth keeping: in scan mode, block bounds MUST be resolved from the pristine template before any renames (the blocks are found by the template names). The first engine draft looked bounds up after `write_name`, which silently skipped every EQ write on FSQ — caught by the new automatic readback, which is exactly the failure class it exists for.

## 2026-07-05 — Deep Think EQ flow: order locked + mic-locker loop

Brian locked the per-input order of importance and process: **instrument → mic → genre → venue**. Written into eq-advisor (SKILL.md + decision-flow.md) and show-deep-build (SKILL.md frontmatter, Step 3, deep-research-workflow.md). Venue stays the last-applied filter and often the biggest dB bend, but ranks last in decision authority — trims and vetoes, never rewrites the instrument+mic foundation.

Two new mechanics in the same pass:
- **Mic locker loop (eq-advisor Step 2b):** every input's specified mic gets checked against `mic-library.md` for an owned alternative with a concrete win (less-EQ voicing, problem peak colliding with genre/room, rejection margin, SPL, kit coherence). One alt max per channel with a one-line why; never on TOUR gear; suggestions batch to the review stop; EQ always targets the specified mic; accepted swap re-enters at Step 2. Alts land in `mic_notes` + `Locker alt —` lines in the spec `changes` so they ride the Rationale PDF — no build_packet.py change needed.
- **Research dedupe:** deep build now collapses N channels into M unique instrument × mic research units, shows the plan table before searching, researches once per unit, fans results back out. Genre once per show; venue constant loaded once.

Open recommendations (Brian's call, not yet implemented): KB-verified cache skip of the web pass for established+dated pairings; single batched stop-and-ask round after the plan pass; post-show "what did you actually move" harvest question; optional per-channel role field.

## 2026-07-05 (later) — Brian's rulings on the open recommendations + artist layer

- **Cross-show research cache: REJECTED.** Web research runs fresh every show — artists never repeat. Written into eq-advisor Step 3. Within-show dedupe (one search per unique instrument × mic unit) stays.
- **Per-channel role field: rejected** — role and any other per-channel context arrive via the free-text `notes`; note-mining table got a "role in the mix" row.
- **Artist layer added to the chain (Brian directive):** the artist_profile from show-deep-build step 2 now feeds every channel's Step 4 in eq-advisor ("Layer the genre + the artist"). Artist-specific evidence outranks the generic genre profile where they differ. Chain per input: instrument → mic → web+KB baseline → genre+artist → venue.
- Batched stop-and-ask round and post-show harvest question: explained to Brian, awaiting his call.

## 2026-07-05 (final) — Batched question round adopted; post-show harvest rejected

Brian's rulings on the last two open items: **batched stop-and-ask ADOPTED** — the deep build's plan pass (dedupe + locker loop + note mining) now collects every stop-and-ask trigger and asks them, together with the locker alternatives, in ONE question round before any EQ commits; mid-build stops remain only for forks the scan missed; standalone (non-show) questions still ask immediately. Written into eq-advisor (Stop-and-ask protocol + Step 2b) and show-deep-build (Step 3 + deep-research-workflow.md). **Post-show harvest question: rejected** — no close-out "what did you move" step.

Deep Think flow spec is now settled: instrument → mic (+ locker loop) → fresh web+KB baseline every show → genre refined by artist_profile → venue as final constraint filter; within-show dedupe; one up-front question round.

## 2026-07-06 — memory-consolidation skill, running daily

**Context:** Brian pointed at a public GitHub skill ("dream-skill") replicating Anthropic's unreleased Claude Code auto-memory-consolidation feature — 4-phase pass over memory, triggered every 24hrs via a Claude Code Stop hook, signal-gathered by grepping local JSONL session transcripts. Neither the Stop hook nor the JSONL files exist in Cowork, so it couldn't be installed as-is; asked to build the equivalent instead.

**Built:** `_skills/memory-consolidation/SKILL.md` — orient → gather signal → consolidate → prune/index, same shape as the reference skill, adapted to this project:
- Gather-signal phase uses Cowork's `list_sessions`/`read_transcript` instead of JSONL grep (best-effort — won't reach every session, treated as a supplement not the source of truth).
- Targets the real two-tier memory here: `active-projects.md` (canonical project state) and `about-me/memory.md` (session history) — not a single flat memory file.
- Ported in from the reference skill: explicit contradiction format (`Updated YYYY-MM-DD, previously: X`), source attribution on merged facts, dry-run-and-confirm on the very first run, never-delete-without-replacement.
- Logs a one-line run summary to `memory.md` Session Notes each time, which doubles as the watermark for the next run's gather-signal phase.

**Trigger:** Cowork scheduled task, once a day (see schedule tool for the exact time — set at build time, adjustable). This replaces the CLI Stop-hook mechanism the reference skill used.

**Relationship to `consolidate-memory`:** that generic Cowork skill still exists for manual/ad-hoc runs. This one is the Brian-specific, scheduled version — it doesn't replace it, it automates it and adds the transcript-scan step.

## 2026-07-06 — Deep Think pipeline audit + hardening (Brian: "cornerstone of my business")

**build_packet.py hardened (regression-verified against the Izzy 2.0 reference — byte-identical .md):**
- Spec validation before anything is written: ribbon + phantom = error; a boost on a VOCALS channel = error unless the band carries `"approved": true` after Brian's explicit OK; duplicate channel numbers = error; band/freq/gain range errors; whole-dB, high-shelf-boost, fader-length, section-grouping warnings. A failed validation writes nothing.
- The written .md is auto-linted with `_shared/md_lint.py` inside the build (errors abort) — the patcher's lint gate now runs twice, once at authoring time.
- Ribbon (`⚠ RIBBON — NO 48V`, red) and new `tour` (`⚑ TOUR — confirm at load-in`) flags auto-prepend to the input list xlsx, the Show Packet rows, and the Rationale channel headers. Previously the spec's `ribbon` field was carried but never surfaced anywhere.
- Input List xlsx now puts the actual `instrument` in the Instrument column (was the fader label — "Kick In" instead of "Kick"); venue restored to the .md header line (matches the reference build).
- New optional spec fields, all rendered: `decisions` (the answered question round → its own box on the Rationale PDF), `monitors` + `reverbs` (xlsx sheets + Rationale header lines; reverb presets verbatim from the KB).
- User text is now escaped for reportlab — an `&` or `<` in a note/eq_summary would previously have crashed or mangled the Rationale PDF.
- Environment fix: `openpyxl` was missing from the Mac's python3 — every future xlsx build would have crashed. Installed `--user` alongside the existing reportlab.

**New evidence channels written into the skill (SKILL.md + deep-research-workflow.md + NEW-SHOW.md + eq-advisor):**
- Step 2 listening pass: recent live videos + setlists over press copy; lineup mismatches vs. the input list go in the question round.
- Prior-verified-show check: same artist / weekly series / twin act at the venue → Brian's own console-verified build is highest-trust evidence BESIDE the fresh research (the fresh-web lock stands; this is not caching). Added to eq-advisor's trust ladder too.
- Tech rider / stage plot: ask for it when one plausibly exists.
- Outdoor shows: pull show-window weather (Open-Meteo / Tempest) into `room_context` — wind, HF air loss, rain contingency.
- Question-round answers now persist in `spec.decisions` and ride the Rationale PDF.

**Respected:** the 2026-07-05 post-show-harvest rejection — no "what did you move" step added. A lower-friction variant (diff a post-show console .ses save against the built .ses via the engine) was re-suggested for Brian's ruling; not implemented.

---

## 2026-07-08 — Show-feedback loop: five FSQ corrections landed as code

First console pass on a shared-engine FSQ build (Hot Magnolias) came back with five corrections; all five are now enforced in the pipeline rather than remembered: deeper outdoor cuts (docs + eq-advisor), FSQ ch 10 / stereo-OH protection (validator + patcher `protected` calibration — a template channel map mistake can no longer reach the console), band-provided stage plots (no generation), the MASTER PDF (pypdf merge in build_packet), and the always-on Seventh Heaven reverb section with settings/plugin-EQ/why/pairing (validator-enforced). Pattern worth keeping: every console-pass correction should land as a validator rule or patcher guard the same day, not as a note.

---

## 2026-07-08 — build_packet.py: plugin cache vs canonical copy (Rev 3 reverb miss)

The hot-mag 3 blind rebuild first shipped WITHOUT the reverb section because the session ran the show-deep-build *plugin cache* copy of `build_packet.py` (stale, predates the same-day reverb/MASTER hardening) instead of the canonical `audio/_skills/show-deep-build/scripts/build_packet.py`. Brian caught it. The canonical script validates reverbs as required, expects `reverb_pairing` (not `reverb_note`), emits the MASTER itself, and adds Monitors/Reverbs xlsx sheets. Standing rule: the `_skills/` copy in the audio folder is the source of truth — check its mtime against the plugin cache before any packet build, and re-install the plugin when the source moves.

---

## 2026-07-09 — ONE skill: eq-advisor merged into show-deep-build; A/B guardrails applied; stale-install fight fixed

Brian asked for an evaluation of eq-advisor + show-deep-build + NEW-SHOW.md ("combine if possible, give me a single skill"). Findings and actions:

**Redundancy removed.** The two SKILL.mds restated each other's locked rules (order, locker loop, batched round, venue filters) — two copies = drift risk, the same failure that killed the CLAUDE.md EQ tables. NEW-SHOW.md step 4 duplicated the whole deep-build flow a third time. Now: `_skills/show-deep-build/` is the single skill (Part I = show pipeline, Part II = the EQ method, formerly eq-advisor — standalone EQ questions run Part II alone); NEW-SHOW.md is a thin router + don't-forgets; eq-advisor archived to `_skills/_ARCHIVE/eq-advisor-retired-2026-07-09/`. Harvest detail moved INTO the skill (step 7) so it's self-contained.

**Fights found.** (1) The Cowork-INSTALLED copies were stale snapshots — eq-advisor plugin from 06-23, show-deep-build skill from 06-25 — missing every July locked rule (order lock, locker loop, batched round, FSQ deeper cuts, required reverbs, MASTER PDF, decisions list). Live sessions were running pre-July behavior while the `_skills/` sources were current. Fresh `show-deep-build.skill` zip built; Brian must delete both installed copies in Cowork and upload the new one. (2) NEW-SHOW.md still claimed the packet ships ".md + .html + PDF via weasyprint" — the locked engine (`build_packet.py`, 2026-07-06) is reportlab and emits no HTML; docs aligned to reality. (3) `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` (hot-mag A/B) was queued but unapplied — all 11 edits folded into the merged skill + NEW-SHOW.md + the KB pipeline article during the merge; acceptance test = the next deep build vs `hot-mag 3`.

Files: `_skills/show-deep-build/SKILL.md` (rewritten, +4 references +1 script from eq-advisor), `_system/NEW-SHOW.md` (rewritten), `show-processing-pipeline.md` (quality-floor section), all three CLAUDE.md files (merged-skill phrasing), auto-memory `deep-think-default`, `active-projects.md`, KB CHANGELOG.

---

## 2026-07-12 — Fable-parity evaluation: discipline merged into the master skill, heavy scaffolding split to an overlay

Brian asked for an evaluation of how Fable 5 executes the deep build vs. the written skill, then a prompt/skill to bring Opus 4.8 (high) to parity. The evaluation found the skill's audio content already hardened (the 07-08 A/B patches), with the real Fable delta being execution discipline: constraint retention over long builds, honest web↔KB reconciliation, genuine self-audit, calibrated question rounds, cross-channel coherence.

Eight mechanics were drafted; Brian chose "discipline only" for the merge. **Into `show-deep-build/SKILL.md` (all models):** the pacing rule (final numbers never in the same message as the research), the constraint card written at build start and re-read before the question round and before spec.json, the one-word AGREE/DISAGREE/THIN reconcile verdict (kills the false-agreement paraphrase), the consolidated 13-line evidence-quoting pre-commit audit (new `references/pre-commit-audit.md`), the zero-questions-is-suspicious heuristic, and the failure-mode catalog (appended to `references/deep-research-workflow.md`). **Kept in the new `_skills/fable-parity/` overlay (non-Fable models only):** per-unit worksheet files in `_worksheets/` + strict one-unit-at-a-time serialization — real overhead, redundant on Fable. Master SKILL.md now points at the overlay for non-Fable sessions.

Both `.skill` zips rebuilt (`show-deep-build.skill`, `fable-parity.skill`); Cowork installs are snapshots — delete the installed show-deep-build copy and upload both fresh.

## 2026-07-14 — Workspace structure cleanup (memory, skills, git, file layout)

Full audit + fix pass on the Claude structure itself. The changes that affect how future sessions behave:

- **`audio/CLAUDE.md` rewritten from scratch.** It was a stale 2026-05-27 fork of the old global file, silently injected into every session under `audio/` — carrying a Neumann U87 that isn't in the kit, Pi-hosted n8n (retired), the dead weasyprint/HTML packet claim, and frozen Active Projects. Now a thin audio-layer file: control-file pointers, canonical-source rules, post-work logging duties. Everything general lives in the main CLAUDE.md.
- **about-me re-unified (the 2026-07-06 fix had silently failed).** `audio/about-me/` held real files again, and the nightly consolidation was writing session notes there while the canonical file went stale — a second fork. Unique entries merged into `~/Documents/Claude/about-me/memory.md`; `audio/about-me/*.md` are now actual symlinks (they weren't before — that's why it re-forked). Pre-merge copies in `audio/about-me/_pre-merge-archive/`.
- **memory.md rolling window.** Session Notes keep ~30 days; 11 pre-2026-06-14 entries rotated to `about-me/memory-archive-2026H1.md` (nothing reads it at startup). Rotation + promote-before-rotate + auto-memory-dedupe rules written into the memory-consolidation skill.
- **CLAUDE.md Active Projects → pointer** to `active-projects.md` (was a frozen duplicate). U87/421-U identity fixes propagated to `show-deep-build/references/decision-flow.md` and `portable-context.md`; ShowBuilder matcher verified already correct; questions.md item closed.
- **Skills:** `audio/_skills/{show-deep-build,fable-parity,memory-consolidation}` symlinked into `.claude/skills/` — Claude Code now always runs the live copy (Cowork uploads remain snapshots, re-upload after edits). Duplicate graphify removed from project skills. New `_system/PIPELINE.md` names the five-stage chain (new-show → show-deep-build → send-it → console verify → wiki push) in one place. `/reflect` rewritten to write auto-memory files instead of appending to `~/.claude/CLAUDE.md` (which is how that file bloated pre-2026-07-13).
- **Git.** `~/Documents/Claude` is now a git repo (baseline commit before any of this, second commit after). `.gitignore` excludes Kims Stuff, SOP Stuff media, the Wiki (own repo), venvs, and the credentials cheat sheet. Retire the `.bak` habit — commit instead.
- **Permissions:** `.claude/settings.local.json` cut from ~40 single-use entries (several against the dead 192.168.0.125) to a short prefix allowlist.
- **Root sweep:** dead June wiki-setup scripts, `_wiki-import`, finished handoffs, the stale "Brian Lloyd - Context.md" export, and the RAM-upgrade spec moved to `_ARCHIVE/`; stray root `Vocal Slap.aup` filed into Echoes T7E Presets (renamed — it differs from the folder copy).

## 2026-07-19 — Workflow evaluation: intake step, show.status.json, unified show-wiki-push

**Context:** Brian asked for an end-to-end evaluation of the DiGiCo/showfile workflow with the goal "upload show info → show-ready PDF packet + console file → wiki." Verdict: the build core (spec.json → build_packet, shared .ses engine, deep-research EQ) is solid; the weak edges were intake, cross-session state, and the publish stage. Venue-keyed template selection already existed via ROUTING.md — confirmed as-is with Brian.

**Shipped (all four approved in one question round):**
- **Intake step (show-deep-build Step 0):** rider/stage-plot PDFs, xlsx/CSV lists, and photos/screenshots are now first-class inputs — every artifact read in full and normalized into brief facts before research; conflicts between artifacts go to the question round; plot/rider filed as `<Show> - Stage Plot.pdf` / `<Show> - Rider.pdf` so the MASTER picks them up.
- **`show.status.json` per show** (`_shared/show_status.py`): scaffolded / packet_built / ses_built / verified / published, with timestamps. scaffold_show.py writes it; build_packet.py and the .ses engine stamp their stages automatically (best-effort — a stamp can never break a build); "verified" and "published" stamped in conversation. Later stages read it instead of newest-folder guessing. Engine regression after the change: hot-mag 3 rebuild md5-identical.
- **show-wiki-push skill** (source `_skills/show-wiki-push/`, symlinked into `.claude/skills/`): venue-aware wiki push for FSQ **and** Memo, driven by the status file, shipping the FULL packet (MASTER / Show Packet / EQ Reasoning / Input List xlsx / .ses / FOH .md / spec.json / band plot+rider) with the copy-list-must-match-links rule. Publishes via `kb-publish.sh`. Fixed stale constants the old skill carried (Wiki.js LAN is 192.168.200.126:3000, not 192.168.0.126). `fsq-wiki-push` rewritten as a deprecated alias that redirects here.
- **Doc sync:** PIPELINE.md (stage table + state-file paragraph), NEW-SHOW.md (intake + scaffold), ROUTING.md (global rule + header date finally bumped off 2026-05-30), send-it (status-file show resolution, verified stamp, wiki-push pointer, and a stale-guardrail fix — it still claimed Mustard dynamics ARE written; corrected to the 2026-07-16 doc-only reality).

**Not done / explicitly scoped out:** ShowBuilder-inbox auto-pull at build start (Brian didn't select it in the intake round); multiple templates per venue and templates for more venues (Brian: covered as-is).

## 2026-07-19 (later) — EQ logic hardened: genre gate, equipment layer, TRACE line

**Context:** Brian dictated his intended EQ-suggestion order (verify genre → research artist → instrument → mic → base EQ influenced by genre/artist/equipment → venue last) and asked for verification against the workflow. Verdict: aligned on artist research, instrument→mic foundation, and venue-last; partial on genre (emerged from artist research instead of being verified first) and equipment (mined from notes but not a named layer no audit could catch under-weighting).

**Shipped (all three options approved):**
- **Genre gate (SKILL.md Step 2a):** genre verified with named evidence before any research; split/hybrid = immediate ask (the one exception to the batched round); verified genre rides the plan table for veto.
- **Equipment in the locked order:** now **instrument (+its notated equipment) → mic → genre → venue**. Notated rig facts (amp/cab model, drum sizes/heads, strings, pickup type) carry the mic-grade research floor — one quantitative fact + named source before bending a value — and are cited in mic_notes/eq_summary wherever they changed a move. Never invent a rig.
- **Per-unit TRACE line:** every unit's research_summary closes with `TRACE: base(…) · equip(…) · genre(…) · artist(…) · venue(…)`, each layer a value or "no change"; pre-commit audit line 14 spot-checks traces against the actual band values.

**Files:** show-deep-build SKILL.md + references (decision-flow, deep-research-workflow, pre-commit-audit line 14 + header), NEW-SHOW.md don't-forgets, project CLAUDE.md locked-order sentence, KB (eq-starting-points, show-processing-pipeline, pipeline-spec-memo, pipeline-spec-fsq — dates bumped), KB CHANGELOG. Constraint card list extended (genre gate · equipment layer · TRACE). `_skills/show-deep-build.skill` zip rebuilt.

## 2026-07-19 (final) — Console-verify gate removed from publishing

**Brian's ruling (verbatim intent):** each show is a one-off — he won't come back to verify a show on the console before it goes to the wiki. His explicit go ("SEND IT" / "push it") is the ONLY publish gate.

**Changed:** show-wiki-push (gate = Brian's go; `verified` stamp informational only, show located by `ses_built`-not-`published`), show-deep-build Step 6 (renamed from "HARD STOP — Brian verifies" to "Hand over — publish on Brian's go"), send-it Step 5, PIPELINE.md stage 4 (now "Console load — NOT a publish gate"), NEW-SHOW.md, ROUTING.md, show_status.py docstring, fsq-wiki-push alias description, KB pipeline-spec-memo + pipeline-spec-fsq hard-stop sentences. Also corrected pipeline-spec-memo's stale "first Memo build still needs console verification" note — the Memo calibration was console-proven 2026-07-16 (Back to Black test load). Auto-memory: `publish-on-go` (feedback). The `verified` stage stays in show.status.json as an optional stamp for when Brian volunteers that a file ran on the desk.

## 2026-07-26 — The locker check became a fork Brian decides

**Brian's ask:** a loop over the show's inputs that checks whether something in the locker beats the specified mic, and when it does, **stop and ask him which he wants** with a three-sentence reason for the recommendation. DI and XLR line-feed inputs don't get the fork.

**What changed:** Step 2b was already sweeping `mic-library.md`, but its output was an FYI — a one-line `Locker alt:` note that batched into the round and, in practice, was easy to read past and default away from. It's now a gate: every eligible input either passes silently (the specified mic is the locker's first call, or nothing concretely beats it) or produces a **LOCKER FORK** card that Brian answers keep/swap. No third state, no silent default.

**The eligibility gate (new):** the fork only runs where there's a capsule to swap. DIs (RNDI, J48, AR133, artist's own box) and XLR line feeds (wireless XLR out, keys/track/playback, console ties) are exempt and pass silently — no fork, no question, nothing in the packet. Also exempt: TOUR/artist-provided mics and the fixed Memo crowd rig (OM1 / Deity S2 / CM4). A source with both a mic and a DI forks on the mic leg only.

**The three sentences are specified, not left to taste:** (1) the concrete win with a number and its source, (2) what it changes for this show — EQ moves saved, or the room/genre problem it solves, (3) the honest cost. If sentence three can't be written straight, the win wasn't real and the fork doesn't get raised. Still one alternative per input, maximum, and the alternative has to be free — not already assigned elsewhere in the show — with its kit source named so Brian knows which case it comes out of.

**Batching kept.** Forks head the single up-front question round rather than interrupting per channel; the 2026-07-05 batched-round rule stands. Standalone EQ questions ask immediately, same card.

**Files:** show-deep-build SKILL.md (Step 2b rewritten, batching paragraph, Part I step 3, constraint card), references/decision-flow.md, references/deep-research-workflow.md (locker loop + batch note + two new failure modes: the swallowed fork, the padded reason), references/spec-schema.md (`decisions` records every fork, swapped or kept), project CLAUDE.md locked-order sentence. `_skills/show-deep-build.skill` zip rebuilt for Cowork.

## 2026-07-26 — House wireless: fixed faders + the mult rule

**Brian's rule:** information on a wireless 1–4 row of the input list lands on fixed faders — **FSQ 33/34/35/36, Memo 41/42/43/44** — unless a band input's mic names the unit (`Wireless 2`, `W58 2`, `WL2`, `W2`), in which case the receiver is **multed**: the named input keeps its own channel *and* the wireless fader stays listed, both patched to the same source port. A bare `W58` with no unit number is a stop-and-ask — never auto-assign a pack.

**Verified against the templates, not taken on faith:** the FSQ patcher's `expected_names` puts 'Wireless 1'–'Wireless 4' at faders 33–36, and the Memo patcher's at 41–44 (45–48 are the matching W1–W4 monitor sends). Brian's numbers and the surface-label tables agree exactly.

**Contradiction fixed:** `pipeline-spec-fsq` said "Channels 1–32 only. Ignore anything above 32" in two places, which would have silently dropped every wireless channel. Now 1–32 for band inputs plus the 33–36 wireless block; skip above 36.

**Enforced as code** in `build_packet.py` (new `WIRELESS_CH` map + `wireless_unit()` parser): a mic naming a wireless with no unit number → error; a wireless fader whose mic names a different unit → error; a named wireless with no fader row in the spec → warning; a non-wireless source parked on a wireless fader → warning. Parser tested against `Wireless 2 / wireless2 / W58 / W58 3 / W58-4 / WL1 / W2 / SM58 / Beta 58A` — `SM58` and `WA-87` correctly don't match, bare `W58` correctly returns "no unit."

**Two defaults I set (Brian to correct if wrong):** on a mult the *named* input carries the deep-built EQ while the wireless fader keeps its template baseline curve and gets no second EQ card; and the shared-socket gain note (two channels off one socket share the Q225 analog gain — ride digital trim on the mult) goes in the channel `notes`.

**Files:** show-deep-build SKILL.md (new wireless block in Part I + validator line + constraint card), references/spec-schema.md (`patch` note), scripts/build_packet.py (map, parser, four checks, docstring), KB pipeline-spec-fsq (channel range ×2 + Input Format gotcha) and pipeline-spec-memo (Input Format block), project CLAUDE.md Patching Conventions, KB CHANGELOG. `.skill` zip rebuilt.

## 2026-07-27 — MASTER quick-links page + the research section made readable

**Two asks from Brian, both about reading the paperwork rather than building it.**

**1. The MASTER opens on a clickable QUICK LINKS page.** Page 1 of `<Show> - MASTER.pdf` is now an index: DOCUMENTS (cover, input list, EQ rationale, what-changed, question round, reverb, research, stage plot/rider when present), then EQ PAGES grouped by section with a chip per channel — "17 Conga 1 · p15" — and the rationale's sections. Every row is a real PDF link, and the same map ships as PDF bookmarks for the reader's sidebar. No more scrolling 45 pages to reach the vocals.

**Page numbers are measured, not guessed.** A zero-height `PageMark` flowable rides the story in both `show-packet-builder-template.py` and the rationale builder and records `canvas.getPageNumber()` where it lands; `build_master_pdf` offsets those marks by the real page counts of every merged part, draws the nav page with a reportlab canvas (so every row's rect is known exactly), and hangs pypdf `Link` annotations off them. The nav length is settled in a loop — adding a second nav page shifts every target, so it re-renders until stable. `build_packet_pdf` / `build_rationale_pdf` now return `(path, marks)` and `build_master_pdf` takes `[(pdf, marks), …]`.

**2. Research is a section, not a paragraph.** The rationale used to render `research_summary` as one 15 kB block of prose — unreadable at the desk. The spec now carries a structured **`research`** object: `genre_verified` / `gig` / `conditions` as three framing boxes, then one table row per researched unit — CH · source/mic · the quantitative finding with its named external source · a colour-chipped AGREE/DISAGREE/THIN verdict · the five TRACE layers each on its own line — closing with the reconciliation and KB write-back boxes. Artist and room context became titled boxes with paragraph breaks at their enumerated turns.

**Legacy specs still build.** A free-text `research_summary` gets chunked on the lead-ins the deep build actually writes (GENRE VERIFIED / THE GIG / WEATHER / CH<n> / RECONCILIATION), the mic pulled into the row head, the verdict chipped, and the TRACE exploded onto its own lines — so the 27 already-built shows read fine without a rewrite. It warns, pointing at the structured form.

**Validator additions (warnings, never blocking):** missing `genre_verified`, a unit with no finding or no named external source, a verdict that isn't one of the three words, any TRACE layer left blank, missing `reconciliation`, and free-text-only research.

**Regenerated 2nd Wind Conclave in place** — `.md` byte-identical to what its `.ses` was built from, so the showfile stays valid; it just gets the new MASTER.

**Files:** `audio/show-packet-builder-template.py` (PageMark + marks through cover/input-list/EQ pages, `build_show_packet` returns the map), `_skills/show-deep-build/scripts/build_packet.py` (research formatting helpers, structured + legacy renderers, `build_nav_pdf`, rewritten `build_master_pdf`, research validation), SKILL.md, references/spec-schema.md (`research` object), references/pre-commit-audit.md (lines 8/9/15 now point at `research.units[]`), references/deep-research-workflow.md, references/decision-flow.md.

## 2026-07-28 — EQ response card on every input page

**Ask:** Brian wanted the preset cards from the FSQ template preset browser — a filled EQ curve with the numbers on it — carried into the show pipeline, one per input.

**What landed.** Every EQ channel page in `<Show> - Show Packet.pdf` now opens with a vector EQ response card, sitting between the channel header and the mic notes. It draws the channel's actual curve — every active band as an RBJ biquad, HPF and LPF folded in — filled with a wash of that section's accent colour so the card reads as part of its section, with the section accent as the stroke. Each active band gets a dot on the curve labelled `B3 -5 @300 Q2`, plus a `D` when the band is dynamic; HPF and LPF get dashed verticals labelled with their corner. Same information as the table below it, read as a shape instead of six rows. It flows into the MASTER unchanged, and page counts don't move — the card fits in the space each channel page already had.

**Numbers come from the spec, never re-parsed.** `build_packet.py` now hands the packet builder a numeric `curve` dict alongside the display rows. `curve_from_rows()` is the fallback for any caller that only has the formatted strings ("2.5 kHz", "+4 dB") — it exists so the packet builder still works standalone, not as the normal path.

**Two honest limits, both stated on the card.** Filters are drawn at 12 dB/oct because the packet spec carries no slope — the corner frequency is exact, the steepness is indicative. And the curve is the EQ section only; Mustard dynamics are paperwork-only and not in it.

**Labels de-collide.** Clustered bands would have stacked their labels on top of each other, so placed labels are tracked and later ones nudged vertically away from the curve until they clear, then clamped inside the plot. Filter labels flip to right-aligned near the plot edge so an LPF at 16k doesn't run off the card.

**Files:** `audio/show-packet-builder-template.py` (biquad helpers, `eq_curve_card`, `curve_from_rows`, card inserted in `build_eq_pages`), `_skills/show-deep-build/scripts/build_packet.py` (numeric `curve` per channel in `build_packet_pdf`).

**Not done:** the standalone `build_eq_pdf.py` (eq-advisor output) and the rationale PDF's compact per-channel blocks don't carry the card — different layouts, and Brian asked for the input pages.

## 2026-07-30 — two builder bugs fixed during the Repertoire FSQ build

**1. `mic_page_gen.py --slug X --wire` was wiping the Locker Gallery.** `main()` filtered the
record list down to the requested slug and then passed that filtered list to `wire_all()`, which
regenerates the entire gallery block between its `MIC-GALLERY` markers. Net effect: every wire
run left the gallery holding exactly one mic — which is why it had contained only the EV N/D 408
since 2026-07-26, and presumably only the previous mic before that. `wire_all()` now always
receives the full record set regardless of `--slug`; the gallery rebuilt from all 55 records
across all seven categories. Follow-on flagged to `questions.md`: 53 of the 55 tiles have no
photo and render as navy placeholders, so either bulk-source product shots (`import_photos.py`
+ `PHOTO-MANIFEST.md`) or filter the gallery to photographed mics.

**2. `show-packet-builder-template.py` was not escaping user prose into reportlab markup.**
Show style, mic notes and engineer notes went straight into `Paragraph()`, so a bare `&` is read
as a malformed entity — "R&B" rendered as "R&B;" on the packet cover and in the engineer notes.
`build_packet.py` already had an `esc()` for the Rationale PDF; the packet builder had none.
Added a shared `_esc()` and applied it to all three call sites. Caught by eyeballing the rendered
MASTER before delivery, which is exactly what that step is for.

Also this session: the **Audix D4** mic-library character row was corrected against Audix's
current published chart (+6 dB @ 5 kHz, rolloff below 70 Hz — not "reaches 35 Hz, less upper-mid
attack"), and the **Shure PG52** was researched and added to the locker via the full
NEW-MIC-WORKFLOW. Both logged in the KB CHANGELOG.
