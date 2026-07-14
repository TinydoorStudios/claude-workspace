# memory.md
*Living document — append new entries at the bottom. Update existing entries when directly relevant. Never delete — mark as resolved or archived instead.*

> **Canonical project state moved (2026-05-30):** active project state now lives in `Live Sound KB/Wiki/active-projects.md`. Keep this file for session history and decision notes only — don't add new project state here. Routing: `_system/ROUTING.md`.

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

### Live Dead and Brothers (LDB) — Memorial Hall
*Last updated: May 16, 2026*

- Show document built: `LDB_Show_Document.docx`
- FabFilter Pro-Q 4 settings documented: `LDB_FabFilter_ProQ4_Settings.pdf`
- 21 input channels + 6 Memorial Hall crowd mics
- Royer AxeMount: CH13 SM57 (primary), CH15 R-121 (blend) — SR guitar
- All wireless vocals are TOUR — RF coordination required at load-in
- IEM: Hardwire Mix 7 on drums; MIX 1–5 stage wedges

---

### FSQ Salsa — Fountain Square (Weekly)
*Last updated: May 16, 2026*

- Conversion sheet built: `FSQ_Salsa_Patch_2026.pdf`
- 32-channel show. Standard snake → Salsa-specific input repurposing:
  - CH 25–28: Dante 49–52 (wireless vocals)
  - CH 13–16: Guitar inputs → Keys 1–4
  - CH 17–21: Misc inputs → Timbales/Quinto/Tumba/Bongo
- Weekly repeating — check for personnel or gear changes each week

---

### KSO — Simon & Garfunkel Tribute — Greaves Concert Hall, NKU
*Last updated: May 16, 2026*

- Console: Behringer Wing
- Venue: Greaves Concert Hall, NKU, Highland Heights KY (May 15, 2026)
- 40 channels total: 18 band + 2 DJ + 4 spare + 7 ambient/house
- Piano: 9ft Steinway, short stick lid — DPA 4099 stereo pair (Ch 10 low strings, Ch 11 high strings)
- Strings: 6 violins + 2 cellos — all Countryman B3 clip-on
- Horns: AKG C422 in XY mode (Ch 20–21 = L/R capsule of same mic)
- Vocals 1–4 (Ch 25–28): Wireless — TBD
- Vocals 5–7 (Ch 29–31): Shure SM58 wired
- Ch 22 Flute/Piccolo: mic TBD — CONFIRM before show
- Ch 24 Adam Kit Vocal: mic TBD — CONFIRM before show (sings from kit, also moves front)
- EQ approach: conservative cuts-only (classical rules apply)
- **No show document built yet** — needs to be created

---

### Drowsey Lads 2026 — Memorial Hall (Celtic)
*Last updated: May 16, 2026*

- All-acoustic 5-piece Celtic ensemble
- All XLR = pickup/DI except: Ch 1 Irish Flute (MKH40), Ch 10 Uilleann Pipes (MKH40)
- Ch 5 Bodhran = highest-risk channel at Memo — 200Hz Dynamic EQ most aggressive
- Reverb: 3× Seventh Heaven Pro (Melody / Rhythm / Vocal) + CLA Epic
- **No show document built yet**

---

### Israeli Chamber Project — Memorial Hall (Classical Recording)
*Last updated: May 16, 2026*

- Ensemble: 2 violins, viola, cello, flute, clarinet, piano
- Main array: Schoeps MK5 pair ORTF — wire ~8' downstage, ~9' high
- R88 options: MS or Blumlein from center of ensemble at 5' height — confirm stage plot for player positions before choosing mode
- Pending: Confirm R88 mode, preamp for passive R88, Smaart v9 room mode analysis before recording
- **No show document built yet**

---

## Open Issues

### Wind Alert — TEST TEST TEST prefix
*Opened: prior session*

- n8n Wind Gust Alert Slack messages still prepend "TEST TEST TEST"
- Unresolved as of May 16, 2026

---

### Simon & Garfunkel show document
*Opened: May 16, 2026*

- No show document exists yet
- Needs: patch, monitors, EQ starting points, stage plot page

---

## Resolved / Done

### The Brit Pack — 2026-05-28 @ Memorial Hall [DONE]
- Full show document built: Show Packet + FOH Channel Processing combined into single HTML/PDF (`The Brit Pack - Show Document.html/pdf`)
- Q225 patcher built and verified (`apply_britpack.py` + `The Brit Pack.ses`)
- Reverb section corrected: replaced hallucinated preset names with real Liquidsonics presets (Vocal Plate, Gold Hall, Snare Chamber, Guitar Room, Studio A)
- Pipeline spec updated globally: 2-stage pipeline, combined Show Document as Stage 1 output

---

---

## Seventh Heaven Pro — Key Reference Notes
*Last updated: May 28, 2026*

These are the critical facts to know when working with Seventh Heaven Pro at Memo. Full detail in `/Live Sound KB/Wiki/reverb-reference-memo.md`.

**Early/Late slider behavior (CONFIRMED by Brian, direct experience):**
- Range is −20 dB to Equal Mix only
- Crossing Equal Mix = hard jump to MAX on the opposite side
- Notation: "Early: −15 dB, Late: MAX" or "Equal Mix" — never percentage pairs
- "HF Damp" does not exist in this plugin — rolloff is controlled by Late Rolloff / Early Rolloff in Hz

**Preset names to remember (frequently used at Memo):**
- Lead vocal plate: Vocal Plate (Plates 1, #06) — not "Gold Plate" — VLF −19dB factory (safe)
- Lead vocal hall: Gold Hall (Halls 1, #11) — VLF 0dB factory — always cut at Memo
- British rock snare: Snare Chamber (Chambers 1, #09) — VLF −19dB factory
- Rock guitar: Guitar Room (Rooms 2, #16) — baked-in 300ms slap at −14dB — leave it
- Transparent glue: Studio A (Rooms 1, #01) — Mod 0 (zero modulation) — Mix 3–5% max

**Memo Memo target:** Pull decay 30–40% from factory. VLF always down — room reinforces 60–315Hz.

**Reference PDF:** `~/Documents/Claude/audio/Memo Work/Seventh Heaven Pro Reference.pdf`
**KB article:** `reverb-reference-memo.md`

---

## Session Notes

### June 24, 2026
- Built FSQ Stage Backdrop Insert Panels SOP from 8 photos already in `SOP Stuff/FSQ/Stage Inserts/` — categorized images first (storage / mounting technique / end panels / finished result), then walked the install + teardown steps with Brian.
- Key facts captured: 5 panels numbered 1–5 SL→SR, install/teardown happens every show, U-bolts finger-tight (no slack, not wrenched down), silver support bar required at every inner joint (wind tear-out prevention), panels 1 & 5 have a rope cut-out for the backdrop pipe — single loop only or the panel won't seat, U-bolt hardware stored assembled (support bar + both nuts on).
- Files: `FSQ-SOP-Stage-Inserts.md/.html/.pdf` in `SOP Stuff/FSQ/Stage Inserts/`, alongside the source photos. PDF rendered via weasyprint, 4 pages, verified clean (no clipping).

### May 28, 2026
- The Brit Pack show paperwork completed at Memorial Hall
- Seventh Heaven Pro reverb section in show doc corrected — replaced all hallucinated preset names with verified presets from official Liquidsonics PDFs
- Early/Late slider hard-jump behavior confirmed and documented in KB + memory
- Built standalone Seventh Heaven Pro reference PDF: `Memo Work/Seventh Heaven Pro Reference.pdf`
- KB article `reverb-reference-memo.md` updated: added Gold Hall, Snare Chamber, Studio A presets; Early/Late behavior section updated
- Pipeline spec finalized as 2-stage

### June 12, 2026
- Built WP Clear-Com Production Intercom SOP (Main Stage) from uploaded PDF — extracted 5 photos, produced .md + .html + .pdf via weasyprint
- SOP filed at `audio/SOP Stuff/WP/WP-SOP-ClearCom-Main-Stage.{md,html,pdf}`
- Routing correction: initially created `Memorial Hall/SOP Stuff/` by mistake — files moved to canonical `audio/SOP Stuff/` after Brian pointed it out and provided audio folder access
- Added feedback memory to Cowork auto-memory: SOP Stuff is always at audio root, never inside a venue folder

### May 16, 2026
- Created CLAUDE.md at ~/.claude/CLAUDE.md — global context file covering Brian's full setup, venues, EQ library, show doc format, mic shorthand, and active projects.
- Created about-me.md, writing-rules.md, memory.md in ~/.claude/about-me/
- Updated global instructions to reference all three files on session start.
- Established: default output is PDF, writing tone is warm but direct, never assume — always ask.
- Created `/Documents/Claude/audio/` folder structure with venue subfolders: Memorial Hall, Fountain Square, Washington Park, Elm Street Plaza, Other.
- Created venue-notes.md in each folder — pre-filled from known data.
- Documented PA rigs: Fountain Square (L-Acoustics A15/KS21/X12, Q225 FOH, M32 monitors); Washington Park (JBL SRX915/906/928, M32 FOH, no Tempest).
- Updated CLAUDE.md and about-me.md with PA and console assignments per venue.
- Extracted full session knowledge base from uploaded MD file into CLAUDE.md, memory.md, and about-me.md:
  - Added venue abbreviations (Memo, FSQ, WP, ESP, Greaves) to all files
  - Corrected Memo RT60 to working ~1.6s (previous 2.2s was empty/pre-renovation estimate)
  - Expanded mic shorthand library with Type and Primary Use columns; added B3 numbering and C422 notes
  - Added Celtic Music Engineering section (attack times, gating rules, instrument-specific notes)
  - Added Classical Recording Geometry section (wire array, ORTF, R88, spot mic preferences)
  - Added Frequency Reference tables (problem zones by venue type, instrument fundamental ranges)
  - Added Soundcheck Priority Order and Bus Grouping Standard
  - Updated color palette to full spec (console accent colors, EQ row colors, structure bars)
  - Added Drowsey Lads 2026 and Israeli Chamber Project as new active projects in memory.md
  - Expanded KSO S&G notes with full channel detail
  - Saved show-packet-builder-template.py to /Documents/Claude/audio/

### June 16, 2026 — ShowBuilder app built

- Built **ShowBuilder**, a guided web dashboard at `Code/ShowBuilder/` (Python/aiohttp, `./run.sh` → :8095) that front-ends the existing Q225 pipeline. Wizard: Show → Channels → Review → Build. Collects venue/channels/instruments/mics/genre/artist, suggests EQ+comp and 4–6 Seventh Heaven Pro reverbs, shows a review screen for approval, then renders the locked `FOH Channel Processing.md` and calls the `apply_show_TEMPLATE*.py` patchers + show-packet builder. Outputs MD/HTML/.ses/packet PDF/input-list xlsx + review PDF into the show folder. Does NOT re-derive the .ses byte format.
- Brain is KB-sourced: `reverb_presets.json` parsed from `reverb-reference-memo.md` (236 presets, names verbatim) via `build_knowledge.py`; `eq_rules.json` = CLAUDE.md starting points + genre/venue/mic layering; `mics.json` from `mic-library`. Self-improves: unknown mics → library + KB queue; every build logs to `learning/`.
- Phase 1 = Mac (done). Phase 2 (next session) = package-only instance on the n8n VM behind cloudflared + a passcode on the TDS dashboard; emits `*.spec.json`, Mac builds the .ses + final paperwork.
- Only Memo + FSQ have the calibrated .ses pipeline; other venues are paperwork-only.
- Verified: Blue Eighty-Eight rebuilds byte-identical (md5 match); Memo/FSQ fresh builds PASS at exact sizes (1,543,866 / 2,466,215); packet cover renders clean (no clipping).
- Finding: existing Memo MDs (Seals & Crofts 2, Brit Pack, Gospel Awards) are pre-2026-05-30 backwards B-numbering — logged to QUESTIONS for conversion.

### June 23, 2026 — eq-advisor EQ skill

- Built the **eq-advisor** skill (installed plugin + source `_skills/eq-advisor/`): instrument → mic → live forum research (PSW LAB, Gearspace) cross-checked against `eq-starting-points`/`mic-library` → genre → venue/room. Web and KB verify each other; stops and asks on any uncertainty (Brian's rule: an unsure answer is ~3× worse than a pause). Cuts-first / whole-dB, inline + PDF.
- Per Brian's follow-up: made it a **required EQ step in the show/ShowBuilder flow** (wired into NEW-SHOW, showbuilder, show-processing-pipeline, eq-starting-points); **self-improving** (logs to `_learning/eq-advisor-log.md`, proposes KB write-backs via wiki-publish, a Brian override = ground truth); and **Q225/Wing only** — no CL3/M32 unless explicitly asked.
- ShowBuilder's Python app (`Code/ShowBuilder/`) is outside the mounted folder, so it wasn't modified — wiring is at the workflow/KB layer; both target the KB to stay consistent. KB edits are local; push on next wiki-publish run. Delivered updated `eq-advisor.plugin` (re-install to pick up the changes).

### July 1, 2026 (evening — Memo template swap + pipeline review)
- **Memo .ses template replaced:** Brian supplied `brian memo june 2026.ses` (37,661,337 bytes — a full Q225 console save, vs the old 1.5MB offline-editor `brian memo v2.ses`). Canonical copy placed at `Memorial Hall/_TEMPLATE/` (matching the FSQ convention).
- **Memo patcher rebuilt on the FSQ engine** (`Q225 SES Patcher SOP/apply_show_TEMPLATE.py`; old engine archived as `apply_show_TEMPLATE_v2_OLD_stripformat.py`). Calibration derived by structural scan (no save-diff needed): surface table 0x231A48F stride 125 (72 faders), current-scene blocks 0x2324D9C stride 0x15A6, blocks matched to faders BY NAME (block order ≠ fader order), dual offset tripwire aborts on any mismatch. Smoke test PASS byte-level (names ×20, B1→bidx3 mapping, HPF ×0.8 / LPF ×1.25, DEQ, Wireless 41–44 baseline curve preserved, 0 stray bytes, do-not-write tags clean). **First show build still needs a console load + "verified" from Brian.**
- **Deep Think EQ written into both pipeline specs** (`pipeline-spec-memo`, `pipeline-spec-fsq`, `show-processing-pipeline`): every channel's EQ comes from show-deep-build driving eq-advisor; EQ Rationale PDF required.
- Docs synced: ROUTING.md, console-digico-q225 (patchers now declared source of truth for constants; stale FSQ size fixed), venue-memorial-hall, showbuilder.md, send-it skill + its KB mirror, ShowBuilder venues.json, supersession banners on the three old Memo SOP docs. CHANGELOG + IMPROVEMENTS logged.
- Pipeline efficiency review delivered (5+ improvement candidates: shared patcher engine module, KB-mirror auto-sync for send-it, one-command show scaffold, MD lint gate as pre-flight, batch readback verifier, retire remaining reportlab references). Awaiting Brian's picks.

### July 1, 2026 (late — efficiency pass executed)
- Brian approved all six pipeline improvements; shipped same night: **shared .ses engine** (`audio/_shared/q225_ses_engine.py`; Memo + FSQ patchers are now thin calibration wrappers; regression md5-identical to the standalones incl. the Izzy 2.0 build), **md_lint.py** auto-gate (proven: refuses the backwards Brit Pack MD with 96 errors), **full every-channel readback** on every build + `readback_verify.py` standalone, **new-show scaffold skill** (`_system/scaffold_show.py`), **send-it KB mirror killed** (reads live KB), **CLAUDE.md slim-down done** in all three context files (EQ tables + .docx format → KB pointers; weasyprint rule fixed).
- Engine gotcha for the record: scan-mode block bounds must come from the pristine template BEFORE renames — first draft failed exactly there and the new auto-readback caught it.
- Pre-engine standalones archived as `*_pre-engine_standalone.py` in each SOP folder. Memo console verification of a real show build is still the open gate.

### July 5, 2026
- Deep Think EQ flow evaluated at Brian's request. Locked the per-input order (importance + process): **instrument → mic → genre → venue** — written into eq-advisor and show-deep-build (SKILL.md + references). Venue clarified as last-applied constraint filter, not top authority.
- Added the **mic-locker loop** (eq-advisor Step 2b + show-deep-build Step 3): every input's mic checked against mic-library.md for an owned alternative with a concrete win; one alt max, one-line why, never on TOUR gear, batched to the review stop, EQ still built for the specified mic; alts ride mic_notes + `Locker alt —` changes into the Rationale PDF.
- Added research dedupe to the deep build (N channels → M unique instrument × mic units, plan table shown before searching).
- Pending Brian's call: KB-cache skip of the web pass for established pairings, single batched stop-and-ask round, post-show "what did you move" harvest, per-channel role field.

### July 5, 2026 (later)
- Deep Think rulings finalized: cross-show research cache REJECTED (web pass fresh every show — artists never repeat); per-channel role field rejected (notes carry it); **artist_profile added to the per-input chain** (genre+artist layer, artist beats generic genre); **batched question round ADOPTED** (plan pass collects all stop-and-asks + locker alts → one message before any EQ commits); post-show harvest rejected. All written into eq-advisor + show-deep-build skills; IMPROVEMENTS.md logged.

### July 5, 2026 (final)
- Workflow written into all files: eq-advisor + show-deep-build skills, `_system/NEW-SHOW.md`, KB articles (show-processing-pipeline, pipeline-spec-memo, pipeline-spec-fsq, eq-starting-points header, showbuilder — all Last updated bumped), KB CHANGELOG, all three CLAUDE.md files, and the deep-think-default auto-memory. Canonical statement: per-input order instrument → mic → genre → venue; artist profile refines/outranks generic genre; research fresh every show with within-show dedupe; mic-locker alternative check per input; one up-front question round; venue last as constraint filter. Wiki articles updated locally — not yet pushed to the live wiki (wiki-publish when Brian says).

### July 6, 2026 — memory-consolidation skill built + scheduled daily
- Brian flagged a public GitHub skill ("dream-skill") replicating Anthropic's unreleased auto-memory-consolidation feature for Claude Code. Evaluated it: its 4-phase shape and contradiction/backup habits are portable, but its JSONL-transcript scan and Stop-hook auto-trigger are Claude-Code-CLI-only and don't exist in Cowork.
- Built the equivalent: `_skills/memory-consolidation/SKILL.md` — orient → gather signal (via Cowork's `list_sessions`/`read_transcript`, best-effort) → consolidate (contradiction format `Updated YYYY-MM-DD, previously: X`, absolute dates, source attribution, never-delete-without-replacement) → prune/index. Targets the real memory layout here: `active-projects.md` for project state, this file for history.
- Wired to a Cowork scheduled task running once a day. First run is a dry run (proposes changes, confirms with Brian before writing); after that it applies changes automatically and logs a one-line summary here each time.
- Logged to KB CHANGELOG and `_system/IMPROVEMENTS.md`. Open item in `questions.md`: confirm/adjust the daily run time.
