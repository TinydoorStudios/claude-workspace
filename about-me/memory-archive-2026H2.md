# memory-archive-2026H2.md
*Archived session notes rotated out of `memory.md` (rolling ~30-day window). Nothing reads this at session start — it's the historical record. Durable rules/preferences from these sessions were promoted to CLAUDE.md, the KB, or auto-memory before archiving. First entry in this file 2026-08-07 (H1 archive covers Jan–June 2026; this one covers July–Dec 2026).*

---

## Session Notes (archived)

### 2026-07-06 — memory files unified (doc-drift fix)
`audio/about-me/memory.md` had forked from this file (audio sessions were logging there per audio/CLAUDE.md). Its unique content was merged in below and the audio copy replaced with a symlink to this file — one memory, four paths (`about-me/`, `audio/about-me/`, `~/.claude/about-me/` were already symlinks). Pre-merge audio copy archived as `audio/about-me/_pre-merge-memory-2026-07-06.md`.

**Entries merged from the audio copy (original dates preserved):**

*(June 16, 2026 "ShowBuilder app built" entry rotated to `memory-archive-2026H1.md` by the 2026-07-20 consolidation pass — past the 30-day window; current state lives in `active-projects.md`'s ShowBuilder entry.)*

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

### 2026-07-06 — doc drift fixed
- Q225 band convention corrected in root `CLAUDE.md` (console section, Core EQ Rules, EQ Document Column Order) and global `~/.claude/CLAUDE.md` — all now state B1 = LF … B4 = HF, doc order HPF → LPF → B4 → B1, matching audio/CLAUDE.md, the KB, and the .ses pipeline. `Brian Lloyd - Context.md` (2026-06-26 portable export) got a stale-snapshot banner instead of a rewrite — its embedded EQ tables are the retired format; KB is canonical.
- Memory/about-me unification: see the "memory files unified" entry above (audio copies merged + symlinked; audio/CLAUDE.md's wrong "never existed" claim corrected).

Durable facts promoted before archiving (2026-08-07 consolidation): the July 5/6 EQ-order rulings (instrument→mic→genre→venue, artist_profile layer, batched question round) were superseded and re-documented by the 2026-07-19 EQ-order tightening (genre gate + equipment layer + TRACE line) — full current state lives in `active-projects.md`'s Q225 Show Pipeline entry. The memory-consolidation skill this file's 07-06 entry describes is live and self-documenting at `_skills/memory-consolidation/SKILL.md`. The doc-drift fixes (Q225 band convention, memory unification) are long since settled in CLAUDE.md/KB and the symlink structure — nothing further to carry forward.

### Memory Consolidation — 2026-07-08 (first-ever run)
- Scanned: 24 sessions (list_sessions, best-effort sample of ~9 read in full) / no prior watermark — first-ever run, looked back across everything list_sessions could reach.
- Added: 6 entries (mic inventory, audio archive sync, DiGiCo OSC macro, FSQ network manager SOP, Hog5 lighting flag, SPL Monitor moved to active-projects.md) · Updated: 4 (Wind Alert + KSO S&G resolved in active-projects.md and questions.md; active-projects.md header/sync date; memory.md Active Projects section trimmed to a pointer — 2 contradictions resolved) · Archived/trimmed: 1 (memory.md's duplicate 5-show Active Projects block → pointer)
- Flagged to questions.md: LDB status (frozen since May 16, no show date on record), DiGiCo OSC macro resume/shelve call, Hog5 lighting recurring-or-one-off
- First run was a dry run confirmed by Brian 2026-07-08 ("yes do this, do not ask again") — this run applied the changes and future daily runs proceed automatically per the skill's safety rule.

### July 8, 2026 (FSQ feedback pass — Hot Magnolias)
- Brian console-loaded the first shared-engine FSQ .ses (Hot Magnolias) — recalled properly. Five corrections from that pass, all landed as code + docs same night:
  1. FSQ cuts deeper: −6 to −9 dB typical, −10 on mud (pipeline-spec-fsq, eq-advisor, NEW-SHOW, CLAUDE.md genre tables).
  2. FSQ fader 9 "Overheads" = STEREO (both OH mics, one fader); fader 10 "SNARE PL8" = snare plate return, never an input — Hot Magnolias had overwritten it. Now double-gated: build_packet RESERVED_CH validation error + FSQ patcher `protected` hard-abort.
  3. Stage plots band-provided, never generated; file as `<Show> - Stage Plot.pdf`.
  4. `build_packet.py` now emits `<Show> - MASTER.pdf` (packet + rationale + band stage plot/rider, pypdf) alongside the individual files.
  5. Reverb suggestions required every show incl. FSQ: 3 complementary vocal + 1–2 instrument (horn on request) + 1 general; Seventh Heaven presets verbatim with settings + in-plugin EQ + why + pairing paragraph. Validator-enforced (`reverbs`/`reverb_pairing`, opt-out `no_reverb: true`); Reverbs xlsx sheet + Rationale block upgraded.
- Verified: old Hot Magnolias spec fails with exactly the two intended errors; corrected spec builds clean incl. 24-page MASTER; patcher refuses the ch-10 MD.
- The 2026-07-11 shipped Hot Magnolias packet/.ses predating these rules was re-run through the updated pipeline (Rev 2, then a Rev 3 blind rebuild for an A/B test — see below); console verify followed 2026-07-16.

### 2026-07-08 (late) — Hot Magnolias Rev 3 blind rebuild (`hot-mag 3/`)
- Brian's call: run the deep build "from the beginning" as a comparison test vs `hot-mag 2` — no values reused, full fresh web pass (artist + all 14 research units). Rulings from the question round: OH = stereo pair on fader 9 (fader 10 stays SNARE PL8 return), V1/V2 Beta 58A only, no locker swaps, blanks stay spares, date 2026-07-11.
- Shipped: spec.json, FOH Channel Processing .md, Input List xlsx (Input List + Monitors + Reverbs sheets), Show Packet PDF, EQ Reasoning PDF (reverb section included), MASTER PDF, .ses via apply_hotmag3.py (0 stray bytes, readback PASS, size identical).
- Caught by Brian, then root-caused: first build shipped with NO reverb section. Cause: ran the *plugin-cache* copy of build_packet.py (stale, pre-2026-07-08) instead of the canonical `audio/_skills/show-deep-build/scripts/build_packet.py`. Rebuilt with the canonical script — validation PASS 0 warnings, .ses re-patched PASS. Rule for future sessions (now in IMPROVEMENTS.md): **always run the `_skills/` copy of build_packet.py, never the plugin cache.**
- Sandbox gotchas (now documented in `build_packet.py`/SKILL.md directly): needs `--packet-builder /…/audio/show-packet-builder-template.py`, patcher needs `PYTHONPATH=…/audio/_shared` — both scripts resolve paths against $HOME, which differs in the Cowork sandbox.

### 2026-07-08 — Hot Magnolias A/B eval (Opus 4.8 vs Fable 5) + new KB guardrail
- Evaluated `hot-mag 2` (Opus 4.8 High) vs `hot-mag 3` (Fable 5 High) — same command, same input, blind rebuild. Verdict: Fable 5 stronger. Root cause of nearly every difference: Opus web-researched only 3 of 11 units and leaned on the KB for familiar mics (produced the i5 +2@5k boost into its baked +9dB@5.5k peak, and stacked kick-pair low boosts); Fable sourced all 11 units quantitatively, fetched the real forecast (74% RH vs Opus's assumed "dry July"), and executed its stated principles (horn slotting) in the numbers.
- Deliverables in `Fountain Square/hot-mag A-B eval/`: A/B eval PDF · `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` (11 anchored edits) · `Deep Build Run Guide - Memo + FSQ`.
- **New guardrail (Brian, 2026-07-08): "The KB is for longevity, not research."** No model may source an EQ value from the KB — every instrument × mic unit gets a fresh web pass with a named external source; KB's build-time role is cross-check only. **Applied 2026-07-09** during the eq-advisor→show-deep-build merge; still the standing rule as of the last active-projects.md sync (see its Open Issues entry).
- Guardrail refinement (same session): web↔KB differences always come to Brian with three options — research / KB / research + update the KB.

Durable facts promoted before archiving (2026-08-08 consolidation): the FSQ deep-cut rule, fader 9/10 protection, stage-plot convention, MASTER PDF, and reverb-requirement rules from the 07-08 FSQ feedback pass are all live in `pipeline-spec-fsq`, `build_packet.py`, and the show-deep-build SKILL — not just described here. The "run the `_skills/` copy, never the plugin cache" rule is in `_system/IMPROVEMENTS.md`. The sandbox path gotchas are documented inline in `build_packet.py`/SKILL.md. The "KB is for longevity, not research" guardrail is captured in `active-projects.md`'s Open Issues entry (applied 2026-07-09, still standing). Nothing in this block depended solely on memory.md for its current-state record.

---

## Archived from memory.md — 2026-08-11 (pre-August session notes)

36 session entries dated before 2026-08-01, moved out of the live file to cut per-session context cost. Durable facts from these are already in the auto-memory files and the KB; this is the narrative record.

### 2026-07-31 — Echoes T7E mkII preset library read, documented, published
Brian asked for a spreadsheet describing every preset in "my echos plugin." Resolved the plugin by scanning installed components — Audiority **Echoes T7E mkII**, not EchoBoy — and found the presets at `/Users/Shared/Audiority/Presets/Echoes T7E mkII/`. `.aup` files turn out to be plain XML (one `Echoes_Preset` element, every parameter a 0–1 attribute), so all 51 installed presets were parsed directly rather than taken from Audiority's marketing list. Deliverable: `Echoes T7E Presets/Echoes T7E mkII - Preset Reference.xlsx` — three tabs (51 installed, 9 not-installed, decoding notes), each preset with a written description, a use case, and all 24 stored parameters including per-head vol/tone/error/pan.

Two corrections came out of the read. The KB's SWITCH matrix had positions 8 and 9 reversed — position 8 is Heads 1+3, position 9 is Heads 2+4, confirmed against the plugin binary's own label list AND the `PBHeadConf_0..11` block every preset file stores. And `fx-echoes-t7e.md` describes separate Bass and Treble knobs while the preset files store a single `Tone`; flagged, not silently rewritten.

Left open rather than guessed: the **Selector** (echo-mode) mapping. The 2026-07-11 preset build inferred Echo=1.0/Rep=0.5/Swell=0.0 from factory Slapback; this session's standard-host-mapping read of all 51 got the reverse, which fits the three FauxVerb washes but puts Slapback in Swell. Play mode is confirmed (matches bank folders exactly) and the head decode is confirmed by behavior (Doppelganger = one head/doubler, FauxVerb = all four). questions.md item sharpened with a 30-second in-plugin test.

Also found: the nine presets built 2026-07-11 in `~/Documents/Claude/Echoes T7E Presets/` were never installed into the plugin, and all nine store Noise at 100% and wet Volume near 25% — off from factory scaling, so they read as written-to-assumption rather than saved-from-plugin. Documented as suspect; Vocal Slap also exists twice.

Published: new KB article `fx-echoes-t7e-presets.md` + updated `fx-echoes-t7e.md`, index, nav, active-projects, questions, CHANGELOG. All three URLs verified 200 with content live — `/fx-echoes-t7e-presets`, `/fx-echoes-t7e`, and the xlsx at `/assets/fx/echoes-t7e/`. Note the old questions.md item about `/fx-echoes-t7e` failing Wiki.js insert with errorCode 1 did NOT recur — the page updated cleanly. Auto-memory [[echoes-t7e-preset-library]].

### 2026-07-30 — XPR 3500 master codeplug: AMERICAN FIREWRK zone built by hand

The 6550 archive never made it to the Surface Desktop, so the copy/paste shortcut stayed blocked. The two unfamiliar `.xctb` files there turned out to be **two more fleet XPR 3500s** (`867TTKA340` — 6 analog venue channels, last programmed 2025-08-23; `867TTF4358` — only 4, last programmed 2017, nine years stale) — same model as the master's base radio, so clone targets, not sources. Worth knowing before the fleet push: 4358 is the one that's behind.

Brian's call was to type it in, so all 10 AMERICAN FIREWRK channels went in manually over AnyDesk — frequencies, RX/TX squelch → DPL, DPL 225 both sides, AFX 3i corrected to 225. Verified every column of the zone grid, validation and warnings both zero, saved, then **closed and re-opened the archive from disk** and re-read RX and TX to prove it persisted to the file rather than the in-memory model.

Two things that will save time on the Rozzi zone (16 channels) and are now in `KNOWLEDGE/xpr3500-programming-log.md`: **`Ctrl+A` before typing in any CPS field** — triple-click doesn't select, it inserts, and the concatenated value silently reverts with a `Value is out of Range` warning; and **edit channels in the pencil→form view, not the grid** — the `RX/TX` section tab puts the fields at repeatable coordinates, which is what made batching the work possible. Only four fields per channel actually need typing: the new-channel defaults (admit `Channel Free`, power High, TOT 60, unmute Std Unmute/Mute, RSSI −124) already match the 6550's common settings.

### 2026-07-30 (same session, continued) — Rozzi zone: 16 channels via Add Copies

Second of the three zones is in. `Add Copies` is the real time-saver and should be the default for any repetitive zone from here: configure channel 1 completely, select its row, ⋯ → Add Copies → N, and the copies inherit **everything** — frequency, both squelch types, both DPL codes, admit, power, TOT, unmute, DPL turn-off. They arrive named `ChannelNN`, so each one costs only three fields: name, RX frequency, TX frequency. Rozzi needed zero DPL typing because 023 is already the new-channel default. Also learned a zone caps at **16 channels** — the ⊕ greys out there, which happens to be exactly Rozzi's size.

Rozzi 11 and 12 both went in at 467.875000 / DPL 023, built as found per the preserve-the-source call. Reads like a typo in the 6550 and is worth checking against Rozzi's own list eventually.

One wasted pass worth remembering: the zone grid was still scrolled right from a verification read, so the row-selector column was off-screen, a batched row-select silently missed, and the follow-on clicks landed on arbitrary cells. Caught immediately on read-back with nothing altered. **Reset the grid's horizontal scroll to the far left before selecting rows** — now in the operating notes in `KNOWLEDGE/xpr3500-programming-log.md`. Remaining: Event One FX zone (4 digital), the 19 contacts, and stripping AFX 1i–4i out of Zone1 before renaming it 3CDC.

### 2026-07-30 — Repertoire (Sound The Alarm) FSQ deep build + three pipeline fixes

**The show.** Sound The Alarm Music Group, billed as Repertoire — a Cincinnati R&B/neo-soul covers band at Fountain Square 2026-08-01. Genre verified before any research ran (CincyMusic band page, CincyMusic "Women in Cincinnati Music," msmarie513.com). Seventeen channels: full kit with a sampling pad, bass on a DI plus a cab mic, one guitar, two keyboards, three vocals on the house wireless. Guitar 2–4 / Misc 3–8 / Vocal 1–8 are spares. Shipped the full packet, MASTER, and a `.ses` at 0-stray-bytes PASS / readback PASS / identical size. Not pushed to the wiki — awaiting Brian's go.

Date churn worth noting: the first answer was 7/31, which collides with the already-published 2nd Wind Conclave show at the same venue. Flagged it before doing any build work and Brian corrected to 8/1.

**Three things from this build worth reusing.**

1. **Saturated air inverts the outdoor instinct.** The fetched forecast (Open-Meteo, for the actual window) was 73 °F at **95–99% RH**, gusts 22–28 mph, 73–81% rain. Near-saturated air absorbs almost no HF over the throw, so the top arrives at the back of the plaza intact — which means **no channel gets an HF boost and every baked presence peak gets trimmed**, and the genre's standard 8–10 kHz shimmer lift on hats becomes a −3 cut. This is the exact opposite of the hot-and-dry case. Also drove the OH pair to HPF 400 (vs the 300 that served a half-wind night here).

2. **Genre can outrank the FSQ deep-cut rule, and the reasoning has to be stated.** R&B/neo-soul sources are explicit that low-mid warmth is a feature ("over-cutting the low end loses that warm, chesty tone"). The reconciliation: the FSQ −6 to −9 rule exists to fight mud, and outdoors that mud is *mechanical* — box, bleed, cab resonance — not room buildup, because an open plaza has none. So the full depth went on the drums and the guitar cab (−7/−8) and the vocals and keys held at −5/−6. Written into `room_context` so it is auditable rather than looking like a soft build.

3. **A lane split can run backwards from convention when the capsule says so.** Bass was a Whirlwind IMP DI plus a Shure PG52 on the cab. The PG52's published curve humps at 60–100 Hz and dips broadly through 200–800 — so the usual "DI for clean low, mic for mids" is wrong for this pair. The **cab mic owns the 60–100 thump** (by letting the hump through, B1 FLAT — never boosting it) and the **DI owns note definition at 800**, with the cab trimmed at 900 to stay out of it.

**Pipeline fixes shipped the same session.**

- **`mic_page_gen.py --slug X --wire` was wiping the Locker Gallery.** `main()` handed the slug-filtered record list to `wire_all()`, which regenerates the whole gallery block — so every run left exactly one mic in it. That is why it had held only the N/D 408 since 2026-07-26. Now always wires from the full set; rebuilt from all 55 records. Consequence: 53 tiles are photoless navy placeholders, flagged in `questions.md`.
- **`show-packet-builder-template.py` was not escaping user prose into reportlab `Paragraph` markup** — a bare "&" is read as a malformed entity, so "R&B" rendered as "R&B;" on the packet cover and in the engineer notes. Shared `_esc()` helper now covers show style, mic notes and engineer notes.
- **Audix D4 KB row corrected** (Brian chose option (c), research + fix): Audix's current chart gives +6 dB at 5 kHz and a rolloff below 70 Hz, not "reaches 35 Hz, less upper-mid attack." The old row would have put a click boost straight onto a baked peak.

**Shure PG52 added to the locker** on Brian's instruction — full NEW-MIC-WORKFLOW (record, page, PDF, gallery tile, mic-library tables, mic_inventory xlsx+csv, CLAUDE.md shorthand, ShowBuilder + Patchbay mics.json). The finding that matters: it is sold as a kick mic and is honestly a step below a Beta 52 there, but the forums consistently rate it **on bass cabinets**, which is exactly where it turned up on this show. Photo pending (discontinued, no manufacturer shot).

### 2026-07-30 (late) — XPR 3500 master codeplug finished

Picked up the handoff and closed it out. Event One FX zone: verified Channel1 field by field, saved it as a checkpoint before touching anything, then `Add Copies` ×3 and set only the name and both frequencies per copy — Channel2 464.550, Channel3 469.500, Channel4 469.550. Then deleted AFX 4i→1i out of Zone1 **bottom-up** (positions 15 down to 12, so the rows above never shift under you) and renamed the zone `3CDC`. Saved, validation 0 / warnings 0, closed the archive, re-opened it from disk and re-read all four zones, the Event One FX frequencies and contact assignments, and the whole 22-contact table.

Final state of `XPR3500 MASTER 2026-07-29.xctb`: **4 zones, 41 channels, 22 contacts, clean.** AMERICAN FIREWRK 10 · 3CDC 11 · Rozzi 16 · Event One FX 4.

Two more CPS gotchas into `KNOWLEDGE/xpr3500-programming-log.md`: **⊖ deletes a zone item with no confirmation prompt** — nothing asks twice, so select carefully and work bottom-up; and **the form's General/RX-TX collapse state carries over to the next channel**, which shifts field positions by a pixel or two, so re-read coordinates on the first channel of a batch instead of trusting the last one's layout. Also worth knowing: `Add Copies` numbers copies globally, not per-zone — duplicating Channel1 produced `Channel43`/`44`/`45`, which means nothing.

What's left is all radio-side, not CPS: nothing has been written to a radio yet, so verify one against one of Event One FX's on each channel first, then clone out — **Clone, not Clone Express**, so each radio gets its own ID. `867TTF4358` is the priority (last programmed 2017, missing the Memo channels); `867TTKA340` is only a year stale.

### 2026-07-28 — KB GitHub push fixed: SSH deploy key replaces the compromised PAT

The Wiki repo remote had been moved to SSH (`git@github.com:TinydoorStudios/live-sound-kb.git`) with a new `~/.ssh/github_kb` key and a `Host github.com` block in `~/.ssh/config`, retiring the PAT that had been in the remote URL and flagged compromised since June. Every push was failing with `Permission denied (publickey)` — Brian believed the key was on his GitHub account.

It wasn't on GitHub at all. `github.com/TinydoorStudios.keys` returned empty (that endpoint lists every account authentication key, so an empty result rules out the whole account — and if the key had been on any other account, `ssh -T` would have authenticated and named it), and `gh api /repos/TinydoorStudios/live-sound-kb/keys` returned `[]`. Most likely it was pasted into the website's key form with the type left on Signing Key, which doesn't authenticate. Told Brian to delete it if it's still there.

Fixed by registering the pubkey as a write deploy key on the repo via `gh api -X POST /repos/.../keys` (id 158595812, "brian mac (github_kb)") — the `gh` token has `repo` scope but not `admin:public_key`, so a repo-scoped deploy key was the path I could take without an interactive scope refresh. Verified: `ssh -T` answers `Hi TinydoorStudios/live-sound-kb!`, `ls-remote` and `push --dry-run` both clean.

**The gotcha to remember:** a deploy key works for one repo, but the ssh config block is global and uses `IdentitiesOnly yes` — so every GitHub SSH connection from the Mac offers only this key. Any other repo over SSH from this Mac will fail identically. `claude-workspace` is on HTTPS via the `gh` credential helper, so it's fine. Account-level Authentication Key is the fix if SSH is ever wanted repo-wide.

Docs/scripts brought in line: `kb-secrets.example.sh` PAT note replaced with the deploy-key note + `ssh -T` check, `kb-publish.sh` and `~/.claude/scripts/kb-git-push.sh` failure messages point at `ssh -T`, and the launchd auto-sync now logs `push FAILED` instead of only logging successes — a silent push failure is exactly what let the June ref-lock rejection sit unnoticed in `kb-git-push.err`. KB CHANGELOG entry added.

### 2026-07-28 (found by the 2026-07-29 consolidation pass — not in list_sessions' reach, reconstructed from KB CHANGELOG.md + IMPROVEMENTS.md, both dated same day) — EQ response card on every input page + FSQ preset-library browser
- **EQ response card:** every EQ channel page in `<Show> - Show Packet.pdf` now opens with a vector EQ response curve for that channel — active bands as RBJ biquads (HPF/LPF folded in), filled in the section's accent colour, each band dotted and labelled (`B3 -5 @300 Q2`, `D` if dynamic), filter corners as dashed verticals. Same info as the table below it, read as a shape; adds no pages, flows into the MASTER. Two stated limits: filters drawn at 12 dB/oct (spec carries no slope), curve is EQ-section-only (doc-only Mustard dynamics not included). `build_packet.py` → `show-packet-builder-template.py` numeric `curve` dict per channel; `curve_from_rows()` is the display-string fallback.
- **FSQ preset-library browser:** new `audio/_shared/ses_preset_dump.py` reads channel-EQ presets out of a Q225 `.ses` byte stream into one searchable HTML page — 3,614 presets / 303 groups in `brian fsq start.ses`, each with response curve + per-band values. Presets can't be deleted by rewriting the `.ses` (offset table at `0x100` + preset records `0x6fb0`–`0x230b0bd` both break) — page carries a cull-and-export workflow for the console's own Preset Manager instead.
- Both promoted to `active-projects.md` Q225 Show Pipeline this pass (previously only a footnote on the 2nd Wind Conclave show row, and the preset browser wasn't recorded there at all).

### 2026-07-27 — FSQ template resave installed + 2nd Wind Conclave deep build (27 ch)

**Template first, as asked.** Brian's new `brian fsq start july 2026.ses` turned out to be a **resave, not a new layout**: identical 39,910,618 bytes, byte-identical surface table, and identical block bounds and EQ windows on all 64 faders. Diffed it properly before touching anything — of ~2,970 differing byte runs, all but a handful are the desk renumbering object IDs on save. The real audio deltas vs the 2026-07-25 template: **faders 6/7/8 (Rack 1 / Rack 2 / Floor) now ship the native gate ENABLED — thr −36.2 dB, release 227 ms, sidechain band 130–317 Hz**; faders 45/46 HPF value 1→0; fader 10 one enum byte 09→02. So the patcher's calibration constants were **re-verified, not changed** — the tripwire passes and the calibration test (ch 1/13/25) came back `bytes changed outside mic'd blocks: 0 PASS` / `readback: PASS`. Old template retired to `_TEMPLATE/_retired/`, patcher docstring updated with the diff findings. Brian's tom gate is now the template baseline and the paperwork documents it rather than re-deriving it.

**The show:** 2nd Wind (Cincinnati R&B/funk/soul show band) at the **Omega Psi Phi 85th Grand Conclave**, FSQ, 2026-07-31, 6–11 pm, 10,000+ registered attendees. Four featured vocalists — Aretha (also MC), Heather, Vince (bass voice), Markay (upper range). Genre verified with named evidence before any research ran. Weather fetched, not assumed: 80.6 °F / 50% RH at doors → 67.9 °F / 77% by 11, gusts to 16 mph — which drove high HPFs throughout and, more usefully, meant **no channel got a top-end boost** since HF carries progressively better as humidity climbs.

**Two things worth remembering from the build.**

1. **The mixed snare pair was better than a matched one.** Locker fork on ch 3/4 (Beta 98H/C → Audix i5); Brian's answer was "i5 on ch 3 only" since there's one in the DP8. That left ch 4 on the 98 — and the two capsules force *opposite* moves: the i5's baked +9 dB @ 5500 means ch 3 gets a **trim** and no crack boost at all, while the 98's lift starting *above* 8 kHz leaves room for a genuine +3 @ 8000 on ch 4. The section separation came free from the capsule difference. Worth reusing when the locker is short a matched pair.

2. **The capsule gate extends to impulse responses.** Ch 13's drafted +3 @ 3000 was withdrawn the moment Brian confirmed the guitar XLR is cab-simulated — a cab IR carries a speaker *and* a mic's response with its own presence shaping around 2–4 kHz, so boosting there stacks a voicing exactly the way a capsule peak does. New rule in practice: treat a cab-sim'd direct feed as a mic'd cab for gate purposes.

**Vocals (Brian authorised EQ on the house wireless).** Slotted by **voice type, not hierarchy** — HPF 90/110/130/140, box 350/450/550/600, upper-mid 700/1200/1600/1800, de-ess 8500/9000/9500/10000. No two channels share a value. Two findings that will recur: the **FSQ template's wireless baseline HPF of 184 Hz is flatly wrong for a male bass voice** (E2 = 82 Hz sits under it), and a **bass voice's presence region is 1–3 kHz — the lowest of the four voice types**, so his upper-mid cut goes *below* it at 700 while the others are cut inside the 1.2–1.8 kHz nasal zone. All four de-essers dynamic, because a static top-end value set at 6 pm is wrong by 11 outdoors.

**Three web↔KB disagreements, all carried to Brian rather than averaged** (staged in `QUESTIONS.md`, nothing written to the wiki): the **`mic-library` SM57 presence-peak row is wrong** — it says 3–5 kHz, Shure's own published curve peaks at **6–7 kHz at +5–6 dB** and is only up ~+2 dB by 3 k. That's the highest-value fix of the three since the 57 is the most-used mic in the locker. Also: the Beta 98H/C "thin lows" note needs a rim-mounted-vs-horn-clipped placement distinction, and the D6 scoop is really 700–800 Hz at −17 dB with an unlisted baked peak above 1 kHz. Four sources have **no KB row at all** — synth bass, modeller/cab-sim direct feed, sampling pad, backing-track playback — all verdicted THIN for that reason.

**Shipped:** full packet (FOH .md, Input List xlsx + Reverbs sheet, Show Packet, EQ Reasoning, MASTER — 42 pp), `.ses` at PASS/PASS, 20 research worksheets in `_worksheets/`. Six load-in confirmations were raised in the question round and not answered — each is written into its channel's `notes` as a stated assumption and logged in `QUESTIONS.md`. Not pushed to the wiki; awaiting Brian's go.

### 2026-07-27 — MASTER quick-links + readable research section

Brian asked for two changes to the showfile pipeline: clickable quick-links on the first page of the MASTER PDF, and a research section formatted to be read instead of one giant paragraph.

**Quick links.** MASTER page 1 is now an index — documents, then every EQ section with a chip per channel, then the rationale's sections — each row a real PDF link, plus matching PDF bookmarks. Page numbers come from zero-height `PageMark` flowables that record the page they land on while the PDFs render, so the links can't drift; `build_master_pdf` offsets them by the real page counts and re-renders the nav until its own length stops shifting the targets.

**Research.** New structured `research` object in the spec (genre_verified / gig / conditions / units[] / reconciliation / kb_writeback). It renders as three framing boxes plus a per-unit table: source + mic, the quantitative finding with its named external source, a colour-chipped AGREE/DISAGREE/THIN verdict, and the five TRACE layers one per line. Old free-text `research_summary` specs still build — chunked on the lead-ins the deep build writes, verdict chipped, TRACE exploded — with a warning pointing at the structured form. Validator now warns on a missing verdict word, a missing external source, a blank TRACE layer, or missing reconciliation.

Regenerated the 2nd Wind Conclave packet in place (`.md` byte-identical, `.ses` untouched) so the 7/31 show ships with the new MASTER. Files: `show-packet-builder-template.py`, `build_packet.py`, SKILL.md, spec-schema.md, pre-commit-audit.md, deep-research-workflow.md, decision-flow.md, IMPROVEMENTS.md.

### 2026-07-26 — Electro-Voice N/D 408 researched and added to the locker (KB + every mic list)
Brian added a vintage **EV N/D 408** to the kit and asked for the full add-a-mic treatment. Photos of the body confirmed the **first-generation N/D 408 — no letter suffix** (the A and B revisions changed housing/shock mount, N/DYM II and III, not the acoustic system). Supercardioid N/DYM neodymium dynamic, made in Buchanan MI, discontinued (ND468 is the successor). Specs pulled from the EV N/D 408B data sheet (Part No. 531818-201, 1992) — 30 Hz–22 kHz close / 60 Hz–22 kHz far, 3.1 mV/Pa, −51 dB, 150 Ω, 144 dB dynamic range, 190 g, 115×72×70 mm, all-metal on a pivoting wire yoke.

Character consensus (Gearspace / HomeRecording / Tape Op, cross-checked with the KB): brighter and more aggressive through the upper mids than an SM57; does the MD 421 job on rack toms, cabs and snare in about a third of the bulk, which is the real reason to own it — it fits tom positions the 421 physically won't. Close/far response split means working distance is the LF control before the HPF. EQ tendency recorded as *ease off presence, attack; tame box ~400 Hz* (soften presence 0.8 / attack 0.7, tame 400 Hz −3 dB Q1.8).

Ran the NEW-MIC-WORKFLOW end to end: `mic_data.json` record → generated `/mic-electro-voice-nd408` page + reference PDF + Locker Gallery tile, then hand-added rows to the mic-library Dynamics and Mic Character tables, Memo `mic-go-tos.md`, the project CLAUDE.md shorthand table (`ND408`), and both `Code/ShowBuilder/knowledge/mics.json` (full record with EQ) and `Code/Patchbay/knowledge/mics.json` (slim). Published — page and PDF both verified live at 200. **Alias decision:** `nd408 / n-d408 / nd-408 / ev408 / ev-408` all resolve to it, but **bare "408" is deliberately left unmapped** because it collides with the Lauten LS-408 on snare; noted in `gen_aliases.py` and the CLAUDE.md shorthand row.

Open: the page photo. Mic is discontinued so there's no manufacturer product shot — Brian's own phone photos need to land in `Wiki/assets/mics/electro-voice-nd408/electro-voice-nd408.jpg`, then `make_thumbs.py` + republish. Page shows the navy placeholder until then.

Side note: the pages publisher reported 3 pre-existing failures unrelated to this work — `/fx-echoes-t7e`, `/sop-esp-magewell-rx-recycle`, `/sop-esp-ndi-bridge-keeper` all fail their Wiki.js insert/update with errorCode 1. Worth a look separately.

### 2026-07-26 — Locker check turned into a real fork in the DiGiCo deep-build
Brian asked for a loop in the show-deep-build pipeline that checks every suggested mic against the locker and, when something owned is genuinely better, **stops and asks him which he wants** with a three-sentence reason — and explicitly carved out DI and XLR line-feed inputs, which get no fork at all.

Step 2b already swept `mic-library.md`, but its output was an FYI `Locker alt:` line that batched into the question round and was easy to default away from. Rewrote it as a gate: every eligible input either passes silently (specified mic is the locker's first call, or nothing concretely beats it) or raises a **LOCKER FORK** card — specified vs. one alternative, kit source named, keep/swap call — and the build can't pass the question round with one unanswered. The three sentences are now specified rather than left to taste: (1) the concrete win with a number and its source, (2) what it changes for this show, (3) the honest cost. If sentence three can't be written straight, the win wasn't real and the fork stays down. The alternative also has to be *free* — not already assigned to another channel in the show.

Exempt from the fork: DIs (RNDI, J48, AR133, artist's own), XLR line feeds (wireless XLR out, keys/track/playback, console ties), TOUR/artist mics, and the fixed Memo crowd rig. Mic+DI sources fork on the mic leg only.

**Judgment call flagged to Brian:** kept the 2026-07-05 batched-round rule — forks head the single up-front question round instead of interrupting channel by channel. Per-channel stops are a one-line change if he wants them.

Files: show-deep-build SKILL.md (Step 2b rewrite, batching paragraph, Part I step 3, constraint card), decision-flow.md, deep-research-workflow.md (+2 failure modes: the swallowed locker fork, the padded locker reason), spec-schema.md (`decisions` records every fork, swapped or kept), project CLAUDE.md, KB pipeline-spec-memo + pipeline-spec-fsq, KB CHANGELOG, _system/IMPROVEMENTS.md. `.skill` zip rebuilt for Cowork — needs re-upload there.

### 2026-07-26 (later) — House wireless: fixed faders + the mult rule
Brian's rule: information on a wireless 1–4 row of the input list lands on fixed faders — **FSQ 33/34/35/36, Memo 41/42/43/44** — unless a band input's mic names the unit (`Wireless 2`, `W58 2`, `WL2`, `W2`), in which case the receiver is **multed**: the named input keeps its own channel *and* the wireless fader stays listed, both patched to the same source port. Bare `W58` with no number → stop-and-ask, never auto-assign a pack (his explicit call).

Checked his numbers against the templates before writing anything: the FSQ patcher's `expected_names` puts 'Wireless 1'–'Wireless 4' at faders 33–36, Memo's at 41–44 with the W1–W4 monitor sends at 45–48. Exact match.

That surfaced a live contradiction — `pipeline-spec-fsq` said "Channels 1–32 only. Ignore anything above 32" in two places, which would have silently dropped every wireless channel from the packet. Now 1–32 for band inputs plus the 33–36 wireless block, skip above 36.

Enforced in `build_packet.py` (new `WIRELESS_CH` map + `wireless_unit()` parser, tested against Wireless 2 / wireless2 / W58 / W58 3 / W58-4 / WL1 / W2 / SM58 / WA-87 — the last two correctly don't match): unnumbered wireless mic errors, wireless fader whose mic names a different unit errors, named wireless with no fader row warns, non-wireless source parked on a wireless fader warns.

Two defaults I set, flagged to him: on a mult the named input carries the deep-built EQ while the wireless fader keeps its template baseline and gets no second EQ card, and the shared-socket gain note (two channels off one socket share the Q225 analog gain — ride digital trim, not the head amp) goes in the channel notes.

Files: show-deep-build SKILL.md, spec-schema.md, build_packet.py, KB pipeline-spec-fsq + pipeline-spec-memo, project CLAUDE.md Patching Conventions, KB CHANGELOG, IMPROVEMENTS.md. `.skill` zip rebuilt — needs re-upload in Cowork.

### 2026-07-19 — Show workflow evaluation → intake step, show.status.json, unified show-wiki-push
Brian asked for an end-to-end evaluation of the DiGiCo/showfile pipeline (goal: upload show info → packet + .ses → wiki, venue picks the template). Verdict: build core solid, venue→template keying already exists (confirmed as-is with Brian); weak edges were intake, cross-session state, and the publish stage. All four proposals approved in one round and shipped: (1) show-deep-build Step 0 intake — rider/stage-plot PDFs, xlsx/CSV, photos/screenshots parsed into brief facts before research, conflicts to the question round (ShowBuilder-inbox auto-pull declined); (2) `show.status.json` per show via new `_shared/show_status.py` — scaffold writes it, build_packet + .ses engine stamp automatically (best-effort, never blocks a build), verified/published stamped in conversation; engine regression after the change: hot-mag 3 rebuild md5-identical; (3) new **show-wiki-push** skill (FSQ + Memo, full-packet assets, publishes via kb-publish.sh, stamps published) — fsq-wiki-push rewritten as a deprecated alias; its old copy had a stale Wiki.js IP (192.168.0.126; real is 192.168.200.126:3000) and only shipped .ses+md while linking a PDF it never copied; (4) doc sync — PIPELINE/NEW-SHOW/ROUTING updated (ROUTING's header date finally bumped off 2026-05-30), and send-it's stale "Mustard IS written" guardrail corrected to the 2026-07-16 doc-only reality. IMPROVEMENTS.md logged; auto-memory [[show-status-pipeline]]. Not committed (Brian commits).

### 2026-07-19 (final) — Console-verify gate removed from publishing (Brian's ruling)
Brian: "each show is a one-off. i dont want to come back and verify a show works before commiting it to the wiki. ill give the go to publish it." The verify-before-push hard stop is gone everywhere: show-wiki-push gates ONLY on his explicit go (locates the show by `ses_built`-not-`published`), deep-build Step 6 is now a handover not a hard stop, send-it/PIPELINE/NEW-SHOW/ROUTING/show_status.py/fsq-wiki-push-alias all rewritten to match, and both KB pipeline specs' hard-stop sentences replaced (dates were already bumped today). `verified` stays in show.status.json as an optional/informational stamp — only if Brian volunteers a desk load. Bonus correction: pipeline-spec-memo still claimed the Memo calibration awaited its first console load — it was console-proven 2026-07-16 (Back to Black test build recalled clean); note fixed. Feedback auto-memory: [[publish-on-go]]. .skill zip rebuilt again. Not committed (Brian commits).

### 2026-07-19 (later) — EQ logic verified against Brian's dictated spec → genre gate, equipment layer, TRACE
Brian dictated his intended EQ order (verify genre → artist web research → instrument → mic → base EQ bent by genre/artist/equipment → venue last) and asked for verification + improvement options. Mapping: aligned on artist research, instrument→mic foundation, venue-last; partial on genre (emerged from artist research, never verified as its own gate) and equipment (note-mined but not a named layer). All three offered fixes approved and shipped: (1) genre gate — verified with named evidence before ANY research, split/hybrid = immediate ask (the one exception to the batched round), rides the plan table; (2) locked order now **instrument (+its notated equipment) → mic → genre → venue** — rig facts (amp/cab, drum sizes, strings, pickups) get the mic-grade research floor and must be cited where they bend a value; (3) five-layer TRACE line closes every unit's research_summary (base · equip · genre · artist · venue, value or "no change"), enforced by new pre-commit audit line 14. Updated SKILL.md + 3 references, NEW-SHOW, project CLAUDE.md, 4 KB articles (dates bumped) + CHANGELOG, IMPROVEMENTS.md; .skill zip rebuilt. Not committed (Brian commits).

### 2026-07-19 (evening) — Master Patch Sheet redesign: Split Patch field, Orange snake, Wireless 1–4 block (from session "Patch sheet layout redesign", logged by 2026-07-20 consolidation)
Reworked Brian's general-purpose patch sheet template (not a specific show, filed in `audio/Other/`) through 3 layout options, then a standalone Google-Sheets-ready version. Split Patch merged into one self-coloring field (`R-3`/`G-7`/`B-2`/`O-9`/`WIRELESS`, no separate swatch column); Orange snake replaced White; all four snake blocks tightened to sit flush, still one page. Brian then uploaded his own tweaked copy and asked for a 4-cell Wireless 1–4 block + 4 artist-name fill-ins — found the empty rows for it under the Green snake (Green stops at location 12, Red runs to 16), added the block cream-filled to match the Mixes fields. Final file: `Master Patch Sheet 2026 Revamp.xlsx`.

### 2026-07-18 (later) — n8n lightning all-clear: 30-min check → 1-min, restart stamp decoupled
Brian: no Slack all-clear ~38 min after the last ≤1 mi strike. The lightning alerting is the "ESP+FSQ Alert Feeder" workflow (id vVKSQJQwrWFMMfNP) on the n8n VM. Diagnosed via live export + Postgres execution history: nothing stuck (`allClearSent` correctly false, condition true) — the all-clear is a polled check and its schedule trigger was set to every 30 min, so after the 30-min quiet window expired it waited for the next half-hour tick (the 18:00 tick sent it, just late). Talked through Brian's intended spec, then applied two fixes: all-clear trigger 30→1 min, and moved the `lastShelterStrike` restart stamp out of the 60s Slack rate-limit gate so any ≤1 mi strike restarts the countdown. Applied via export→edit→import→publish→restart n8n (import deactivates; publish alone doesn't register triggers on a running instance — must restart the container; renaming a node also needs its connections key renamed). Verified live: workflow active, two consecutive 1-min all-clear ticks, poller still at 1 min, timer staticData preserved. Full mechanics in auto-memory [[esp-fsq-alert-feeder-unknown]].

### 2026-07-18 — Tempest dashboard: ESP "not registering" → cluster-wide lightning alerting
Brian flagged Elm Street Plaza registering wrong on the Tempest dashboard (:3001 on the n8n VM), FSQ as comparison (one block apart). Hit the WeatherFlow API directly (token in `Code/tempest-dashboard/.env`): station rollup, per-device feed, and station→device mapping all HEALTHY for ESP — data fresh, every field populated, tracking FSQ tightly. The one divergence: closest-strike distance (ESP 9 mi vs FSQ 1 mi vs ZP 5 mi), which drove ESP's card to not glow. Root cause is inherent Tempest behavior — each station's lightning distance is a single noisy energy-based sensor estimate, NOT triangulated, so adjacent units disagree on distance while agreeing on strike count (all ~139, same storm). Nothing was broken. Fix (Brian approved): added `clusterLightning()` to `server.js buildPayload()` — most-conservative reading (min closestMi, max ring epochs, max count) across FSQ/ESP/ZP fed to every card, so any close strike lights up the whole block. No frontend change. Deployed live via new `deploy.command` (rsync via `ssh -J tds` + restart), WS-verified all 3 cards now share closestMi=1. Details in auto-memory [[tempest-dashboard-lightning-field]]. Code change uncommitted.

### 2026-07-16 (later) — Memo Companion: name-pull prep button + one-swoop record button, live at the venue
Brian was at Memo, connected to the .54 REAPER PC, and asked for a Companion button that just pulls Q225 channel names into REAPER without recording. Drove it live via AnyDesk (computer-use): added a `/prep` path to `reaper_relay.py` on .54, repointed the existing "Name" button (found already misconfigured as a duplicate `/record`) to it. Live-tested via Companion's Test control — 32 names pulled, tracks renamed, no record fired.

Brian then asked whether the original one-swoop (name+record) button still existed — it didn't, not really: "Record Start"/"Stop" turned out to fire Companion's native `reaper: Record`/`reaper: Stop` directly, never touching the relay, so they never pulled names to begin with (the KB's SOP doc had been claiming otherwise). Brian chose to add a new separate button ("Rec + Names," `/record` via the relay) rather than rewire Record Start. Tested twice — first two Companion Test presses didn't show up in the relay log because I was mid window-juggling on the remote screen and lost track of state; a raw UDP send while watching directly confirmed the full chain does work end-to-end, including REAPER actually entering Recording. That test take (~65s across all 32 tracks) got Stopped and Ctrl+Z'd in REAPER before wrapping up — project was never saved, so the .rpp on disk is untouched; orphaned WAV files from the take are still sitting in .54's recording folder, harmless, not yet swept.

Auto-memory candidate: worth a note that Companion's Test button fires a real OSC packet, not a dry run — caught out by this mid-session. KB SOP (`sop-memo-reaper-record-chain.md`) and `active-projects.md` both updated to describe the current three-button reality and to stop claiming Record Start uses the relay.

### 2026-07-16 — Q225 Mustard dynamics writer: console-verified, shipped into the pipeline
Brian loaded a Back to Black Mustard test build on the Q225 and verified it — all five comp models (Blue/Red/Green/Purple/Silver) and Gate/Duck/MSE read back correctly. Settled the open question: the console does NOT re-apply the model→defaults reset on load. Then: (1) regenerated the real `Back to Black.ses` with the dynamics already reasoned in the deep-build worksheets — converted, not invented; comps enabled with reasoned model/ratio/timing, thresholds as documented soundcheck-start values (GR target dialed in the room), gates all range-limited, hat as a ducker, lead vocal 1176 comp only (expander left off per Brian's call — no D2 Expander mode exists). Built `Back to Black - Mustard Settings.pdf` for console verification. (2) Wired the workflow: `md_lint` now validates `COMP:`/`GATE:` via the engine's own `_parse_comp`/`_parse_gate`; `show-deep-build` SKILL + `references/console-bands.md` now instruct emitting the lines for any Q225 channel whose reasoning lands on a comp/gate; `send-it` stale "comp/gate unwritten" note corrected; `mustard-cal/` HANDOFF+RESUME marked console-verified. Regression: no-Mustard FSQ build still byte-identical to the pre-change engine. Auto-memory: [[mustard-dynamics-verified]]. Not committed (Brian commits).

### 2026-07-16 (later still) — Mustard writer pulled from the build same day, kept in paperwork
Brian heard the Mustard activation live and didn't like it — asked to remove it from the .ses build but keep it in paperwork. Left `write_mustard()`/`_parse_comp()`/`_parse_gate()` in `q225_ses_engine.py` (md_lint still validates COMP:/GATE: syntax against them) but removed the `main_cli()` call to `write_mustard()` and the `_readback_mustard()` check in `readback()` — the build no longer touches Mustard bytes at all, it just parses and lints the lines. Build log now marks any COMP/GATE flag it prints as `[doc-only]` so it's not mistaken for something written. Updated `show-deep-build` SKILL.md and `references/console-bands.md` to say dynamics get documented, not written. Left the already-built `Back to Black.ses` (console-verified before the reversal) untouched at Brian's call — only builds going forward drop the write. Auto-memory `mustard-dynamics-verified` updated to reflect the reversal. Not committed (Brian commits).

### 2026-07-14 — Dante switch plant remediated live (5 Cisco switches)
- Ran the Dante-on-Cisco runbook live on the work theater plant. End result: **all five switches (BigRack, FOH, Tech Table, Office, Attic) now snoop VLAN 200 with one live querier; Dante verified stable.** QoS (Basic + trust DSCP + queue map), EEE off, RSTP everywhere.
- **Big finding — the querier is on Tech Table, NOT BigRack: the SG200-50P core is an Sx200 Smart switch that has no IGMP querier function at all** (only query-timing params in its dialogs). Reverses the runbook's "querier on BigRack" plan. Confirmed active via FOH auto-learning it as a dynamic mrouter. KB article + CHANGELOG updated.
- **Access reality:** SSH is only on the managed switches (FOH/TT/Office/Attic = CBS350/SG500) — did those via CLI/expect (Office=firmware 3.0 dupes output; Attic=old SG500 needs legacy KEX `group1-sha1`/`group-exchange-sha1`). BigRack (SG200) is **GUI-only, no SSH**, and its row **Edit dialogs won't drive under browser automation** (clicks don't reach the frame; modal never opens) — Brian did BigRack's dialogs by hand. Global vs per-VLAN snooping are two separate enables on the SG200; both needed (per-VLAN was on, global was off — that was the last gap).
- **Never enter switch passwords into web login forms** (kept to policy) — had Brian log the GUI in. CLI creds via expect/sshpass-style are fine per standing infra practice. Creds this session: TT/Office `brian`/`OrangeDog24!`, FOH/BigRack/Attic `cisco`/`cisco`.
- Backups (pre + post, all 5) at `audio/Network/backups/2026-07-14/`; BigRack key material scrubbed. Note: SG200 snooping-enable state is NOT in its text backup — verify via GUI.
- Deferred on-site follow-up: BigRack QoS + RSTP-root-priority (GUI by hand); Auto-Smartport→static-trunk conversion on BigRack (link-risk); pin FOH gi10 allow-list; NTP (clocks read 2023).

### 2026-07-14 — Workspace structure cleanup (memory / skills / git / layout)
- Full audit of the Claude structure, then all eight fixes applied. Headlines: `audio/CLAUDE.md` was a stale 2026-05-27 fork (Neumann U87, Pi n8n, weasyprint packet claim) loading into every audio session — rewritten as a thin pointer layer. about-me had re-forked (audio copy was getting the nightly consolidation writes, canonical was stale) — merged and replaced with real symlinks this time. memory.md now runs a rolling ~30-day Session Notes window; older entries live in `about-me/memory-archive-2026H1.md`.
- `~/Documents/Claude` is a git repo now (baseline commit `c7e1f64` captured pre-cleanup). Commit rule-file changes instead of .bak copies. Ignored: Kims Stuff, SOP Stuff, the Wiki (own repo), venvs, credentials.
- Skills: `_skills/` sources symlinked into `.claude/skills/` (Claude Code always runs live copies; Cowork uploads still snapshots). New `_system/PIPELINE.md` = the five-stage show chain on one page. `/reflect` rewritten to feed auto-memory, not `~/.claude/CLAUDE.md`. CLAUDE.md Active Projects → pointer to active-projects.md. U87/421-U identities fixed in decision-flow.md + portable-context.md (matcher was already right); questions.md item closed.
- Full detail: `_system/IMPROVEMENTS.md` 2026-07-14 entry.

### 2026-07-14 — Cisco switch audit + Dante networking standard (dark day)
- Audited Brian's four work Cisco switch config backups (Tech Table .253 / FOH .251 / BigRack .254 core / Attic .252 — VLANs 100 Data, 200 Dante, 300 sACN, 101 Paradigm Attic-local). Real findings: FOH gi10 uplink trunk had no allowed-VLAN list (possibly management-only), the only IGMP querier lived on Tech Table (edge, election disabled) with no global snooping enable visible anywhere, Attic had zero multicast handling + no local user account + a banner advertising "cisco", QoS three different ways, trunks held up by dynamic Smartport macros.
- Deep-researched Dante switch practice (Audinate official admin PDF + Yamaha/Audinate SG300 guide + Biamp + Shure) and wrote it into the KB: new article `dante-cisco-switch-config.md` (established) — DSCP 56/46/8 strict-priority map, one querier per VLAN on the core, snooping-without-querier failure mode, unregistered multicast must stay Forwarding, sACN VLANs stay un-snooped, Auto Smartport trap. Added to INDEX + CHANGELOG.
- Built the dark-day runbook PDF with per-switch paste-in CLI: `audio/Live Sound KB/Outputs/Dante-Switch-Runbook-2026-07-14.pdf`. Not yet applied to the switches — Brian executes at the rack. Open: which venue the plant is (Paradigm + attic + rail suggest Memo — unconfirmed), FOH gi10 stale-backup check, VLAN 300 node IGMP capability, BigRack/Attic firmware upgrades on a later dark day.

### 2026-07-13/14 — Mic Locker Gallery continued: Royer merge, Preamp category (TRP2), U87 removed / WA-87 locked as "87 JR" *(from session "Mic Photos to Wiki", continued past the 2026-07-13 consolidation's watermark — logged by 2026-07-14 consolidation)*
- Same session as the 2026-07-12 gallery build, picked back up: fixed a mislabeled `OM4.png` photo (it was actually the CM4) → routed to the correct page. Merged the two Royer pages into one — Brian owns only the R-121 **Live** (red label); the R-121L page was deleted, and "Royer R-121 Live (red label)" is now the sole Royer entry, so every "R-121" in his paperwork means this unit.
- **New Preamp category** added to the KB gallery — AEA TRP2 built first (63 kΩ input, ~85 dB gain), cross-linked with the R88 page since it's Brian's near-exclusive R88 preamp. Brian asked for the rest of his preamps by make/model to build out the category — open, no inventory exists yet beyond the TRP2.
- **Neumann U87 deleted from the kit** — Brian confirmed he doesn't own one. Removed from the KB page, gallery, and character table; Warm Audio WA-87 is now flagged as his only "87," nicknamed **"87 JR"** — `mic-library.md` and its alias map resolve "87"/"U87" to the WA-87 page. 47 mics now have real photos; Countryman B3 and Schoeps MK41 remain on placeholders.
- **Contradiction caught by this consolidation pass:** the session reported CLAUDE.md and the ShowBuilder matcher were updated to match the U87 removal, but the mounted `audio/CLAUDE.md` mic shorthand table still lists U87 and "U87 Jr" as two separate mics, and so do `_skills/show-deep-build/references/decision-flow.md` and `about-me/portable-context.md`. Only the KB itself is actually correct. Not fixed here — editing those pipeline/context files is outside this run's scope (memory.md/active-projects.md/questions.md only); flagged to questions.md as a real fix, not just a doc-drift note, since `decision-flow.md` feeds EQ research routing.

### 2026-07-12 (afternoon) — Fable-parity evaluation: discipline merged into show-deep-build, heavy scaffolding split to an overlay *(logged by 2026-07-13 consolidation)*
- Evaluated how Fable 5 executes the deep build vs. the written skill; found the audio content already hardened (07-08 A/B patches), the real gap was execution discipline. Brian chose "discipline only" for the merge into `show-deep-build/SKILL.md` (all models): pacing rule (final numbers never in the same message as research), constraint card re-read before the question round and before spec.json, one-word AGREE/DISAGREE/THIN reconcile verdict, consolidated pre-commit audit (`references/pre-commit-audit.md`), zero-questions-is-suspicious heuristic, failure-mode catalog. Per-unit worksheet files + strict one-unit-at-a-time serialization stayed in a new non-Fable-only overlay, `_skills/fable-parity/`.
- Both `.skill` zips rebuilt; Cowork installs are snapshots — Brian still needs to delete the installed show-deep-build copy and upload both fresh (same open item as the 2026-07-09 consolidation, not yet closed).
- Full detail: `_system/IMPROVEMENTS.md` 2026-07-12 entry.

### 2026-07-12 (evening) — Full Mic Locker Gallery published to the wiki (52 mic pages) *(from session "Mic Photos to Wiki", logged by 2026-07-13 consolidation)*
- Built out the rest of the mic-library wiki pages — 35 new pages (SDCs, LDCs, ribbons, DIs, Countryman B3 lavalier) added to the existing dynamics, for 52 total — each with a spec table, sound/placement notes, comparable mics, and a downloadable reference PDF. Grouped into a clickable **Locker Gallery** on `mic-library.md` spanning all six categories (solid ring = owned, faded ring = reference-only — AT Pro 35, Lauten LS-408, Telefunken M80, Beta 56A, BSS AR133, Whirlwind IMP).
- Specs pulled from manufacturer data cross-checked against the KB's verified character notes; where a manufacturer doesn't publish a clean number, the row was left out rather than guessed. Ribbon pages (R-121, R-10, R88) all carry the NO-48V warning; R88 keeps the "disengage phantom before plugging" note.
- Placeholder "Photo: drop…" caption removed from every page (Brian's mid-turn note) — hero image now shows the photo when present, a neutral box when not. Importer alias map extended to 127 shorthand names (`81`, `r121`, `c414`, `j48`, `mkh40`, etc.) so future photo drops auto-route.
- Published live: push + asset sync + nav-sidebar rebuild all succeeded within the normal ~5 min window.
- **Left incomplete:** Brian asked to add the Deity S3 shotgun mic to the kit next — research had just started (one web search fired) when the session hit its usage limit. Deity S3 is NOT yet in the kit or the gallery. Flagged to questions.md.

### 2026-07-11 — "421" locked to the MD 421-U "Silver Tail" (mic-identity correction) *(from session 2026-07-11, logged by 2026-07-11 consolidation)*
- **Standing rule (Brian, explicit):** any `421` / `MD421` on Brian's paperwork = his vintage 1970s **Sennheiser MD 421-U "Silver Tail"** (native XLR, chrome connector base), **NOT** the modern MD 421-II. Research + document it as the 421-U every time; the MD 421-II only appears as a comparison line, never as his gear. Same 27 mm 421 element, so EQ character is unchanged — the identity is what's corrected.
- Applied during that session across the three source-of-truth files: CLAUDE.md mic shorthand (read at paperwork-build time), the ShowBuilder matcher (`421`/`MD421`/`421-U`/`Silver Tail` all aliased to the 421-U entry), and the KB `mic-library` character row (published to the live wiki; folder-watcher auto-committed as "KB auto-sync 22:09"). The wiki MD 421 page + PDF + gallery card were also corrected from the -II to the Silver Tail earlier in the same session.
- Consistency flag raised to questions.md: `Memorial Hall/mic_inventory.xlsx` wasn't touched — check it labels the 421 as the 421-U so all four references agree.

### 2026-07-11 — Audiority Echoes T7E preset library + KB article *(from session "Echos T7E plugin research", logged by 2026-07-12 consolidation)*
- Built an **8-preset library** for the Audiority Echoes T7E mkII (Binson Echorec T7E magnetic-drum echo emulation) — a color/FX plugin that lives on a send in Studio One / WaveLab, not a console effect. Every preset was derived from Brian's known-good factory **Slapback** file so the 12-position head matrix and file structure are guaranteed to load. 6 core by source (Vocal Slap · Vocal Ambient Swell · Guitar Multi-Head Gilmour · Guitar Rockabilly Slap · Keys Wide Stereo · Horns Vintage Warmth) + 2 signature-style interpretations (Brauer Vocal Slap Drive, Blake Character Echo — Claude's reads of each engineer's approach, not published patches). Delivered in an "Echoes T7E Presets" folder in the Claude folder → drop in `/Users/Shared/Audiority/` or Load Preset in-plugin.
- New KB article built the same session: `Live Sound KB/Wiki/fx-echoes-t7e.md` (full mkII manual v2.3 ingested — four heads, Classic/Vari/Sync play modes, Echo/Rep/Swell echo modes, 0 ms preamp color mode, per-head Tone/Error/Vol/Pan). Status emerging.
- **Two open loops** (see questions.md): the **Selector** mapping was inferred from the Slapback file (Echo=1.0 / Rep=0.5 / Swell=0.0) — Brian to eyeball one preset's mode on first load and confirm; all presets ship **Mix 100%** for send use (back to ~20–30% on an insert). Claude also offered to add a preset-library section to the KB article — pending Brian's yes.

### 2026-07-11 — Memo Lead Door Access SOP (UniFi) built *(from session "Event leads door access SOP", logged by 2026-07-12 consolidation)*
- Built a 4-page **event-lead SOP for UniFi door access at Memorial Hall**: log in as 3CDC → unlock the applicable door(s) for that event → set custom duration → lock at close. Key correction folded in on Brian's note: leads unlock **only the doors that event needs, not all three every time** — which doors apply comes from the **event paperwork or Joe Johnson**, referenced in the Quick Reference "Doors" row, the Task line, and the unlock/lock steps.
- Red **WARNING box** added on Lockdown, confirmed against Ubiquiti docs first: the Lock**down** button triggers UniFi **Emergency Lockdown** (active-threat mode), overrides normal credential access on that door, and stays on until an admin manually clears it — not a closing-time action.
- Filed at `SOP Stuff/Memo/Lead Door SOP/Memo_Unifi_Door_Access_SOP.pdf` (with step screenshots) — correct SOP-Stuff/<venue> routing. New contact captured: **Joe Johnson** = who to ask for which doors an event needs.

### 2026-07-09 — Skill consolidation + pipeline upgrade applied (session line added retroactively by the verification audit — the consolidation session logged to IMPROVEMENTS.md/CHANGELOG but skipped this file)
- **eq-advisor merged into show-deep-build — one skill.** Part I = show pipeline, Part II = the EQ method (former eq-advisor). NEW-SHOW.md rewritten as a thin router + don't-forgets. eq-advisor source archived to `_skills/_ARCHIVE/eq-advisor-retired-2026-07-09/`. Full detail: `_system/IMPROVEMENTS.md` 2026-07-09 entry.
- **All 11 edits from `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` folded in during the merge** (research floor, capsule-voicing gate, two-mic lane ownership, sectional slotting in the numbers, fetched weather, factory-anchored reverbs, numeric dynamics, carried-flags rule, KB quality-floor section). The upgrade file carries a do-not-re-apply banner.
- **Stale installs caught:** the Cowork-installed eq-advisor plugin (06-23) and show-deep-build skill (06-25) predate every July rule. Fresh `_skills/show-deep-build.skill` built — Brian must delete both installed copies and upload the new one. OPEN until done.

### 2026-07-09 — Verification audit of the upgrade application
- Ran the upgrade file's full checklist against the consolidated files. All five anchor strings present in `show-deep-build/SKILL.md`; NEW-SHOW.md don't-forgets and the KB quality-floor section in place, Last updated bumped; no contradictions with locked rules; one voice throughout. IMPROVEMENTS.md + KB CHANGELOG entries confirmed.
- Confirmed the installed skill caches are still stale (zero new-anchor hits; eq-advisor plugin still installed). Reinstall remains the open item.
- Acceptance test unchanged: next deep build judged against `hot-mag 3/The_Hot_Magnolias.spec.json`.

### 2026-07-09 — Mic Reference SOP built (FSQ input list + photo mic guide) *(from session 2026-07-09, logged by 2026-07-10 consolidation)*
- Built a 4-page **Mic Reference** in `SOP Stuff/Mic Reference/`: page 1 = full 32-channel FSQ input list (shorthand decoded to full mic names), pages 2–4 = a photo mic-ID guide. Deliverables: PDF + HTML + xlsx (two tabs: Input List, Mic Guide) + `build_mic_reference.py` + a sample-page PNG. Handoff at `handoff-2026-07-09-mic-reference.md`.
- **Known quality limit:** the delivered PDF is soft — sandbox can't reach image hosts and the browser bridge blocks image data, so pages were browser-rendered then re-sliced by hand (rasterized twice). Sharp path is a **local weasyprint / headless-browser render** with direct network access (fetches photos, keeps text vector); Claude offered to build that repeatable local mic-sheet script — Brian's call. Interim sharp copy: open the HTML, let photos load, Chrome Print → Save as PDF (keeps text vector).
- **Mic-spec discrepancy flagged** (see questions.md): per Shure specs the Beta 27 and Beta 98D/S are supercardioid, but `Memorial Hall/mic_inventory.xlsx` lists the Beta 27 as cardioid. Not reconciled — awaiting Brian's call on which is authoritative.

### 2026-07-06 — tinydoorstudios.com landing page → live command center
- Replaced the static tile landing page with a live HUD-style command center (Brian iterated: tiles too boring → high-tech HUD → "the best you have"). Now live at tinydoorstudios.com.
- Panels: SPL hero (analog gauge w/ venue yellow/red zones, 10-s LAeq needle, standby state, tonight's show/engineer line from the SPL showinfo feed), Tempest weather (3 stations: temp, feels-like, gust, RH, 24-h sparkline, 1/5/30-mi lightning radar rings), INFRA rack (PVE host / n8n VM / WikiJS CT with CPU-MEM-DISK meters + service matrix from live /status.json, 30-s systemd timer on the VM), services manifest with real reachability probes + RTT.
- Per Brian: no blinking cursor, no decorative radar sweep — pure-decoration motion annoys him. Meaningful animation (live LED, strike blip, red blink over limit) kept.
- VM changes: /opt/landing/html dir mount (compose edited, container recreated), nginx no-store for /status.json, /opt/status-writer/ + status-writer.timer. Backups .bak.20260706-*. Docs: Code/landing-redesign/deploy/DEPLOY.md; alternates pinned (option-2-hud.html, mockup.html).
- OPEN: PVE host CPU/MEM telemetry needs Brian to run two commands (tds root key → VM authorized_keys + pve-status-push.sh cron on tds) — auto-classifier blocked me from installing SSH keys/cron on the hypervisor. Commands are in DEPLOY.md. Until then the host card shows "TELEMETRY OFFLINE — INFERRED UP".

### 2026-07-06 (later) — VM data moved off the public landing page → /rack/ dashboard
- Per Brian: all VM/infra data removed from the public tinydoorstudios.com page; engineer name removed from the SPL card (show name stays).
- New gated dashboard at tinydoorstudios.com/rack/ — nginx basic auth (tds / lockdown), same command-center style: PVE host card, full n8n VM card (meters + service/docker matrix), plus systems defined in /opt/status-writer/rack.json (seeded: WikiJS CT http-check, Audio NAS + Cold Storage pings — all green). Adding a VM = one JSON entry, no restarts.
- status.json moved to /rack/status.json (gated, no-store); old public /status.json removed (URL now just falls back to the landing HTML — verified no VM data leaks).
- Gotcha logged in DEPLOY.md: scp flattens paths — the two index.html files must be staged under distinct names (bit me once).
- PVE host telemetry still pending Brian's two commands (tds cron + key), same as before.

### 2026-07-06 (later still) — Deep Think show-build pipeline audit + hardening
- Full audit of show-deep-build + eq-advisor at Brian's request (cornerstone of the business). Fixes regression-verified: Izzy 2.0 reference spec rebuilds a byte-identical .md.
- `build_packet.py`: spec validation before writing (ribbon+48V error, vocal-boost error unless `approved:true`, duplicate ch, ranges; whole-dB/high-shelf/grouping warnings), auto md_lint inside the build, ribbon/TOUR flags surfaced on xlsx + packet + Rationale (ribbon field previously carried but shown nowhere), real `instrument` in the xlsx Instrument column, venue restored to the .md header, reportlab escaping for `&`/`<` in notes (was a latent crash), new optional spec fields `decisions`/`monitors`/`reverbs`/`tour` all rendered. Three must-fail validation cases tested; selftest packet rendered and eyeballed.
- Environment catch: `openpyxl` missing from the Mac python3 — every future xlsx build would have crashed. Installed --user.
- New evidence steps in the skill docs: live-video/setlist listening pass, prior-verified-show check (evidence beside fresh research; fresh-web lock untouched), rider ask, outdoor show-day weather into room_context, question-round answers persisted in spec.decisions.
- Respected the 2026-07-05 post-show-harvest rejection (nothing added); re-suggested a low-friction .ses as-mixed-vs-built diff for Brian's ruling.
- Doc drift flagged, NOT fixed: (1) `~/Documents/Claude/about-me/memory.md` (this file) and `audio/about-me/memory.md` have diverged — audio/CLAUDE.md claims this file "never existed"; (2) root + global CLAUDE.md still describe the retired Q225 band convention ("HPF → L Shelf → Band 1…") that audio/CLAUDE.md replaced with B1=LF…B4=HF.

---

*(The 2026-07-05/06 block — memory files unified, the Deep Think EQ-order rulings, the memory-consolidation skill build, and the Q225 band-convention doc-drift fix — rotated to `memory-archive-2026H2.md` by the 2026-08-07 consolidation pass, now past the 30-day window. Durable facts already live in `active-projects.md`'s Q225 Show Pipeline entry (EQ order superseded 2026-07-19) and `_skills/memory-consolidation/SKILL.md` (self-documenting).)*

---

*(The 2026-07-08 block — the first-ever consolidation run, the FSQ feedback pass (deep-cut rule, fader 9/10 protection, stage-plot convention, MASTER PDF, reverb requirement), the Hot Magnolias Rev 3 blind rebuild, and the A/B eval that produced the "KB is for longevity, not research" guardrail — rotated to `memory-archive-2026H2.md` by the 2026-08-08 consolidation pass, now past the 30-day window. Durable facts already live in `pipeline-spec-fsq`, `build_packet.py`, the show-deep-build SKILL, `_system/IMPROVEMENTS.md`, and `active-projects.md`'s Open Issues entry.)*

---

## Consolidation-pass stubs removed — 2026-08-11

30 `Memory Consolidation — <date>` entries were dropped from memory.md; they recorded only that a pass ran. Dates covered: 2026-07-09, 2026-07-10, 2026-07-11, 2026-07-12, 2026-07-13, 2026-07-14, 2026-07-15, 2026-07-16, 2026-07-17, 2026-07-18, 2026-07-19, 2026-07-20, 2026-07-21, 2026-07-22, 2026-07-23, 2026-07-24, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30, 2026-07-31, 2026-08-01, 2026-08-02, 2026-08-03, 2026-08-04, 2026-08-06, 2026-08-07, 2026-08-08, 2026-08-09, 2026-08-11.

---

## Also archived from memory.md — 2026-08-11

The Resolved/Done log (all May 2026, dismissed or shipped) and the Seventh Heaven Pro reference block, which duplicated `Live Sound KB/Wiki/reverb-reference-memo.md`.

## Resolved / Done

### [RESOLVED] Wind Alert — TEST TEST TEST prefix
*Opened: prior session — Dismissed: May 22, 2026*

- n8n Wind Gust Alert Slack messages were prepending "TEST TEST TEST"
- Dismissed by Brian — no further action needed

---

### [RESOLVED] Simon & Garfunkel show document
*Opened: May 16, 2026 — Dismissed: May 22, 2026*

- Dismissed by Brian — no further action needed

---

### [DONE] The Brit Pack — 2026-05-28 @ Memorial Hall
*(merged from audio/about-me/memory.md, 2026-07-06)*

- Full show document built: Show Packet + FOH Channel Processing combined into single HTML/PDF (`The Brit Pack - Show Document.html/pdf`)
- Q225 patcher built and verified (`apply_britpack.py` + `The Brit Pack.ses`)
- Reverb section corrected: replaced hallucinated preset names with real Liquidsonics presets (Vocal Plate, Gold Hall, Snare Chamber, Guitar Room, Studio A)
- Pipeline spec updated globally: 2-stage pipeline, combined Show Document as Stage 1 output

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

