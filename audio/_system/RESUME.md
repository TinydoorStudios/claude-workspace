# RESUME — consolidation checkpoint

*If a session ended mid-migration (usage limit, etc.), read this to pick up exactly where it left off. Read `ROUTING.md` + `NEW-SHOW.md` for normal show work.*
*Last updated: 2026-05-30*

---

## What this migration is

Brian moved to one project for all venues (a new conversation per show, venue named at the start), on Opus. Goal: kill the drift from having 3–5 competing copies of every reference. The KB (`Live Sound KB/Wiki/`) is now the single source of truth; `_system/` routes; the KB grows by harvesting reusable lessons from each show.

## DONE (2026-05-30)

- **Access:** full `~/Documents/Claude/audio/` project mounted. (about-me confirmed at `audio/about-me/` — the old `~/.claude/` and `~/Documents/Claude/about-me/` paths were both wrong.)
- **Routing layer built:** `_system/ROUTING.md` (venue → folder · console · base .ses · patcher · PA · Tempest · KB specs), `_system/NEW-SHOW.md` (show flow + harvest), `_system/IMPROVEMENTS.md` (self-improvement log), this file.
- **CLAUDE.md** startup block rewritten to point at `_system/` + `audio/about-me/` + KB; about-me path bug fixed.
- **Pipeline specs folded into KB:** `pipeline-spec-memo` (from Memo Work spec) + `pipeline-spec-fsq` (from FSQ spec). `show-processing-pipeline` is now the linked overview. INDEX updated + rewritten clean (had pre-existing repeated-header corruption).
- **active-projects.md** = canonical project state: added Completed Shows log + Knowledge Harvest loop.
- **Fixed:** `venue-fountain-square` duplicate heading; `venue-memorial-hall` stale "two Memo folders" note.
- **Archived (reversible, → `_ARCHIVE/`):** `Memo Work/`, `workflow start files/`, `Fountain Square Knowledge/` (xlsx relocated to `Fountain Square/`), `Seals and Crofts 2 BACKUP/`, scattered `venue-notes.md`, folded pipeline-spec copies + redirect stub. See `_ARCHIVE/MANIFEST.md`.
- **Auto-memory:** added KB-canonical pointers to the channel-card, deliverables, and Q225-tags rules; wrote `project-single-project-migration` memory.
- **CHANGELOG.md** entry written.

## DONE (2026-05-30, later same session) — Seventh Heaven Pro reverb pass
- Corrected Early/Late model in KB `reverb-reference-memo` (Brian, direct): Early sits at MAX; Late is the variable 0→−20 dB; one notch past −20 = Late OFF. Notation locked "E/L: Early MAX / Late −XdB | Late OFF | Equal."
- Locked always-100%-wet (dropped Mix from the line format); format now leads with Bank / Name / preset # (#TBC when unknown).
- Filled 5 confirmed preset numbers (Vocal Plate #06, Gold Hall #11, Snare Chamber #09, Guitar Room #16, Studio A #01); rest #TBC, harvest off the console.
- Made the article per-venue: Memorial Hall (room-aware), Fountain Square (outdoor — minimal default, Late higher, VLF near factory), post (factory-intent). Reconciled FSQ pipeline-spec reverb section. Synced auto-memory + CHANGELOG.
- Source of truth for factory specs: the verified `Seventh Heaven Pro - Preset Reference.pdf` (project root) — matches the official Liquidsonics Manual v1.5.7 + Presets List v1.100.
- **Full 236-preset list ingested + article rebuilt (2026-05-30):** pulled the official Liquidsonics v1.100 presets PDF; KB `reverb-reference-memo` now holds the complete bank/number/spec table (every preset number verified, no #TBC). Article was rebuilt cleanly in one Write after an in-place splice corrupted it — final verified: 236 rows, correct per-bank counts, 5 genre tables, no dup headers, links resolve, no contamination. Engineer-favourites section added from web research (Sunset Chamber, Sun Plate A, Berliner/Boston Hall, Vocal/Dark Plate, Large Wooden, Snare Plate, Studio A).

## NEXT (not yet done — pick up here)

1. **CLAUDE.md slim-down (deferred on purpose).** CLAUDE.md still embeds full EQ/console/mic/show-doc tables that now duplicate the KB. Once Brian confirms the KB is complete, strip those tables and leave CLAUDE.md as routing + pointers only. *Not done yet because the embedded tables are a useful safety net until the KB is battle-tested.*
2. **EQ-table convention — DONE (2026-05-30).** Brian confirmed: HPF + LPF + 4 bands; each Shelf/Bell; any Bell can be Dynamic; no separate low shelf. Canonical display order high→low `HPF · LPF · Band 4 → Band 1`, band numbers match console (1 = LF, 4 = HF). Applied to both pipeline specs, CLAUDE.md, and auto-memory. Remaining sub-task folded into the slim-down: remap the legacy EQ-starting-point data tables in CLAUDE.md to the new columns.
3. **Optional: `_templates/` folder.** Could centralize `apply_show_TEMPLATE.py`, `apply_show_TEMPLATE_FSQ.py`, `digico_ses_editor.py`, `show-packet-builder-template.py`. *Deferred — relocating active patchers breaks path refs in ROUTING/pipeline specs; only do it as a focused batch with lockstep ref updates. Patchers currently stay in their venue `Q225 SES Patcher SOP/` folders, which ROUTING points to.*
4. **First live test:** run a real new-show start for Memo and for FSQ; confirm routing pulls the right folder + KB specs cleanly. Fix anything that snags.
5. **Schedule** the `knowledge-base-health-check` skill (optional) to auto-audit the KB for drift between sessions.

## Guardrails
- Destructive ops (delete, overwrite, move out of place): stop, warn, wait for Brian's OK.
- Never invent specs for emerging venues (CSP, ZP, IA, ESP, Greaves) — ask, then write the answer into the KB.
- KB wins over CLAUDE.md / ROUTING when facts disagree; fix the loser.
