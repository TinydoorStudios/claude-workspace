# Context Handoff — 2026-07-01
**Session topic:** Memo .ses template swap + Q225 pipeline overhaul (shared engine, lint, auto-readback, Deep Think default)
**Console / Venue:** DiGiCo Q225 — Memorial Hall + Fountain Square

---

## What We Did
Swapped the Memorial Hall pipeline onto the new template `brian memo june 2026.ses` (37,661,337 bytes, a full console save — the old 1.5 MB strip-layout `brian memo v2.ses` is retired) and rebuilt the Memo patcher on the console-verified FSQ engine. Then ran a pipeline efficiency pass and shipped all six approved improvements: one shared .ses engine for both venues, an automatic MD lint gate, full every-channel readback on every build, a `new-show` scaffold skill, killed the send-it KB mirror idea (skill reads the live KB), and finally did the CLAUDE.md slim-down (EQ tables + old .docx format out of all three context files). Also made Deep Think the standing default for every new show submission.

---

## Current State

- **Done:**
  - New Memo template at `Memorial Hall/_TEMPLATE/brian memo june 2026.ses` (md5 matches the wine original). Calibration: surface table `0x231A48F` (stride 125, 72 faders), scene blocks `0x2324D9C` (stride `0x15A6`), blocks matched to faders **by name** (block order ≠ fader order), dual offset tripwire.
  - Shared engine `audio/_shared/q225_ses_engine.py`; both venue patchers are thin calibration wrappers. Regression: Memo + FSQ calibration builds and the Izzy 2.0 Deep Think show all rebuild **md5-identical** to the pre-engine standalones (archived as `*_pre-engine_standalone.py` in each SOP folder).
  - `_shared/md_lint.py` (auto hard gate, proven: refuses the backwards Brit Pack MD with 96 errors), `_shared/readback_verify.py` (recheck an existing .ses), `_system/scaffold_show.py` + `new-show` skill.
  - Docs synced everywhere: pipeline-spec-memo/fsq, show-processing-pipeline, console-digico-q225, venue-memorial-hall, showbuilder, ROUTING.md, NEW-SHOW.md, send-it SKILL.md, ShowBuilder venues.json, CHANGELOG (2 entries), IMPROVEMENTS, active-projects, both memory.md files, auto-memory (4 entries).
  - ShowBuilder app still functions (brief-only since 2026-06-25; selftest PASS under its venv).
- **In progress:** nothing.
- **Up next:** first real Memo show through the new template → console load → Brian says "verified".

---

## Key Decisions (Locked)

- **Deep Think is the default for every new show** — any submission (channel list, artist + venue, ShowBuilder brief) runs show-deep-build + eq-advisor automatically. No trigger phrase, no KB-only fast path. Written into NEW-SHOW.md, both pipeline specs, and the skills.
- Both venue templates live under `<Venue>/_TEMPLATE/`; the patcher scripts are the **single source of truth** for byte constants (KB articles point at them, don't duplicate them).
- Byte-level fixes go in the shared engine; template recalibrations go in the venue wrapper's `CAL` dict.
- Verification battery every build (all must PASS): name×~20 per fader, 0 stray bytes, do-not-write tags untouched, full readback of every MD channel, exact size (memo 37,661,337 / fsq 3,779,766).
- CLAUDE.md files no longer carry EQ tables — KB `eq-starting-points` is canonical; show docs render HTML→weasyprint (ReportLab only for standalone tool PDFs).
- New Memo template baseline: Wireless 1–4 (faders 41–44) ship a starting vocal curve; channels 1–39 flat; MD-unnamed bands inherit. Crowd mics are faders 57–59 (Above Stage Mics / Floor Crowd / Balcony Crowd).

---

## Open Items

- **Memo console verification** — the Memo calibration was derived by structural scan (not save-diff). Engine semantics are console-proven from FSQ, but the first .ses built from the new Memo template must be loaded on the Q225 and verified by Brian before the pipeline is fully trusted. This is the only open gate.
- Old Memo show MDs (Gospel Awards, S&C 2, Brit Pack) are pre-2026-05-30 backwards band numbering — lint now hard-refuses them; convert before any rebuild.

---

## Corrections / Watch-Outs

- **Engine gotcha (do not reorder):** in scan mode (FSQ), block bounds must be resolved from the pristine template **before** any renames — blocks are located by template names. First engine draft did it after `write_name` and silently skipped all FSQ EQ writes; the automatic readback caught it.
- Never resurrect old constants: memo strips at `0x0b0327` / `HPF_REL 406`, fsq `0xA287A` / `0x1A1000–0x1CC000` — all dead. Tripwires abort on any template mismatch; recalibrate, don't force.
- Lint flagged "Acoustic Guitar" (15 chars) in the shipped Izzy MD — harmless warning, but shows the gate works.

---

## Resume Prompt

> Picking up from a previous session (2026-07-01). The Memo pipeline now runs on `Memorial Hall/_TEMPLATE/brian memo june 2026.ses` with the patcher rebuilt as a wrapper over the shared engine `audio/_shared/q225_ses_engine.py` — lint + full readback run automatically on every build. Deep Think (show-deep-build + eq-advisor) is the standing default for any new show, no trigger phrase needed.
> Next task: run the first real Memo show through the new template. Scaffold with the new-show skill, deep build fills the MD, "send it memo" builds the .ses — then I load it on the Q225 and give the "verified".
> Key context: the Memo calibration is smoke-tested byte-level but NOT yet console-verified — treat the first build's console load as the acceptance test. Full detail: KB `pipeline-spec-memo`, CHANGELOG 2026-07-01, memory `memo-template-recalibration` / `q225-shared-engine` / `deep-think-default`.
