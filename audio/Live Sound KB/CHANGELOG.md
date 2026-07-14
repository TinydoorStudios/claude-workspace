## 2026-07-14 — Dante switch plant remediated live (five Cisco switches to standard)

Executed the Dante-on-Cisco runbook live on the work theater plant. Pre- and post-change backups of all five switches in `audio/Network/backups/2026-07-14/` (BigRack SSH/cert key material scrubbed).

- **All five switches now snoop VLAN 200 with one live querier.** Global IGMP snooping + bridge-multicast-filtering on BigRack, FOH, Tech Table, Office, Attic; QoS Basic + trust DSCP + queue map (PTP DSCP 56 → top queue, audio 46 → next, low 8 → q2; 8-queue on the CBS350s, 4-queue on Attic/BigRack); EEE/Green-Ethernet off everywhere. Dante Controller verified stable — one clock leader, no dropouts.
- **Querier is on Tech Table, not BigRack — the SG200-50P core is an Sx200 Smart switch with no IGMP querier capability** (IGMP dialogs expose only query-timing params, no querier enable anywhere). Confirmed actively querying: FOH auto-learned it as a dynamic mrouter across the trunk. This supersedes the runbook's "querier on BigRack" step; KB article `dante-cisco-switch-config.md` corrected (standard + Open Questions).
- Method: the CBS350/SG500 switches (FOH/TT/Office/Attic) driven via CLI over SSH (expect scripts, legacy KEX for the old SG500); BigRack (SG200 — GUI-only, no SSH) driven by hand in the web GUI by Brian, since its row Edit dialogs won't drive under browser automation.
- Resolved: FOH gi10 "missing allow-list" was a bare `switchport mode trunk` = all VLANs, functional (not a stale backup). Snooping confirmed never operational plant-wide before today.
- Deferred to a separate on-site session: BigRack QoS + RSTP-root-priority (GUI by hand); Auto-Smartport → static-trunk conversion on BigRack's five trunks (link-risk, one at a time with console access); pin FOH gi10 to an explicit allow-list; remove FOH's inert staged querier address; NTP (all switch clocks read 2023).

## 2026-07-08 — FSQ show feedback baked into the pipeline (Hot Magnolias console pass)

Brian loaded the first shared-engine FSQ .ses (Hot Magnolias) on the console — file recalled properly. His five corrections, all now code + docs:

- **FSQ cuts run deeper** — −6 to −9 dB typical, up to −10 on mud/box; clarity is the priority outdoors. Written into pipeline-spec-fsq (Outdoor EQ approach), eq-advisor venue layer, NEW-SHOW don't-forgets, and the genre table in all three CLAUDE.md files.
- **FSQ template channel map** — fader 9 "Overheads" is a STEREO channel (both OH mics on one fader); fader 10 "SNARE PL8" is the snare plate reverb return, NOT an input (Hot Magnolias overwrote it). Enforced twice as code: `build_packet.py` RESERVED_CH errors at spec validation, and the FSQ patcher's `protected` calibration hard-aborts any MD carrying Ch 10. Documented in pipeline-spec-fsq + the spec schema.
- **Stage plots are band-provided — never generated.** Ask for theirs, file it as `<Show> - Stage Plot.pdf`; nothing gets drawn. NEW-SHOW, show-document-workflow, project CLAUDE.md packet section order updated.
- **MASTER PDF every show** — `build_packet.py` now emits `<Show> - MASTER.pdf` (Show Packet + EQ Rationale + any band-provided stage plot/rider found in the folder, via pypdf). Individual files still ship.
- **Reverb suggestions required every show, FSQ included** — the old FSQ "minimal to none / don't write speculatively" default is retired. Structure: 3 complementary vocal options + 1–2 instrument (horn-specific when asked) + 1 general when warranted; Seventh Heaven Pro presets verbatim, each with settings + in-plugin EQ + why, plus a "using them together" paragraph. Enforced by the spec validator (`reverbs` + `reverb_pairing`; opt-out only via `no_reverb: true`); richer Reverbs xlsx sheet + a dedicated Rationale-PDF block. pipeline-spec-fsq, pipeline-spec-memo (structure aligned), reverb-reference-memo FSQ section all updated.

Tests: Hot Magnolias' own spec now fails validation with exactly the two intended errors (ch 10 reserved, no reverbs); a corrected spec (stereo OH on ch 9 + reverb block) builds clean incl. MASTER.pdf (24 pp = packet 19 + rationale 4 + stage plot 1); the FSQ patcher refuses the old ch-10 MD. **The shipped 2026-07-11 Hot Magnolias build predates these rules — rebuild before the show.**

## 2026-07-08 — First memory-consolidation run (dry run, then applied)

- First-ever run of the memory-consolidation skill. Dry run reported findings, Brian confirmed same day ("yes do this, do not ask again") — changes applied, future daily runs now proceed automatically without asking.
- **Contradictions resolved:** Wind Alert "TEST TEST TEST" prefix and KSO S&G show-document requirement were both marked `[RESOLVED]`/dismissed in `memory.md` weeks ago (2026-05-22) but still showed as open in `active-projects.md` and `questions.md`. Fixed in both, with `(Updated 2026-07-08, previously: ...)` notes rather than silent deletion.
- **KSO S&G Tribute** moved from Active Shows to Completed Shows in `active-projects.md` — the show (2026-05-15, Greaves) had already happened; no paperwork was built and Brian dismissed the requirement.
- **Deduplication:** `memory.md`'s "Active Projects" section was a verbatim, stale (May 16) copy of the KB's canonical `active-projects.md`. Trimmed to a pointer. SPL Monitor's project-state summary (was living in memory.md, project state, not history) moved into `active-projects.md` Tools & Infrastructure where it belongs.
- **New signal added** (found scanning untracked sessions): Mic Inventory Spreadsheet (Memorial Hall), Audio Archive Sync email report (TrueNAS + Reaper PC), DiGiCo OSC macro for Reaper (paused mid-debug, flagged to resume/shelve), FSQ L-Acoustics Network Manager SOP (published to wiki). All added to `active-projects.md` and/or `memory.md` Session Notes with source dates.
- Flagged, not resolved: LDB show status (frozen since May 16, no date on record), Hog5 lighting programming (new domain, unclear if recurring).
- Full detail: `memory.md` Session Notes "Memory Consolidation — 2026-07-08" entry.

## 2026-07-06 — memory-consolidation skill built + daily auto-run

- New skill `_skills/memory-consolidation/` (4-phase: orient → gather signal → consolidate →
  prune/index). Built after Brian asked to evaluate the public "dream-skill" (Claude Code memory
  consolidation with JSONL scan + Stop-hook auto-trigger) — its transcript-scan idea, contradiction
  format (`Updated YYYY-MM-DD, previously: X`), and dry-run/backup safety habits were ported in;
  the JSONL scan and Stop hook were replaced with Cowork's `list_sessions`/`read_transcript` and a
  real scheduled task, since neither of the originals exist outside Claude Code CLI.
- Targets Brian's actual two-tier memory: `active-projects.md` (canonical project state) and
  `about-me/memory.md` (session history) — not a single generic memory file.
- Wired to run automatically once a day via a Cowork scheduled task. First run is a dry run
  (reports proposed changes, asks before writing); subsequent daily runs apply changes and log a
  one-line summary to `memory.md` under Session Notes.
- Superseded by nothing — `consolidate-memory` (the generic Cowork skill) remains available for
  manual/ad-hoc use; this is the Brian-specific, scheduled version.

## 2026-07-05 — Deep Think flow: order locked, mic-locker loop, batched question round, artist layer

- **Per-input order locked (importance + process): instrument → mic → genre → venue.** The artist profile (from the always-first artist research) refines and outranks the generic genre read; the venue is applied last as the constraint filter — it trims and vetoes, never rewrites the instrument + mic foundation.
- **Mic-locker loop:** every input's specified mic is checked against `mic-library` for an owned alternative with a concrete win (less-EQ voicing, problem peak colliding with genre/room, rejection margin, SPL, kit coherence). One alternative max with a one-line why; never on TOUR gear; EQ is always built for the specified mic; alternatives ride `mic_notes` + `Locker alt —` lines in the spec `changes` into the Rationale PDF.
- **Research is fresh every show** — artists never repeat, no cross-show caching. Within-show dedupe added: channels collapse into unique instrument × mic research units, plan table shown before searching.
- **One up-front question round:** the plan pass collects every stop-and-ask trigger plus the locker alternatives and asks them in a single message before any EQ commits; mid-build stops only for forks the scan missed.
- Rejected by Brian: cross-show research cache, per-channel role field (notes carry it), post-show "what did you move" harvest.
- Updated: eq-advisor + show-deep-build skills (SKILL.md + references), `_system/NEW-SHOW.md`, `show-processing-pipeline`, `pipeline-spec-memo`, `pipeline-spec-fsq`, `eq-starting-points` (header note), `showbuilder`, and all three CLAUDE.md context files.

## 2026-07-01 — Pipeline efficiency pass: shared .ses engine, MD lint gate, auto-readback, show scaffold, KB single-sourcing

- **One .ses engine for both venues:** `audio/_shared/q225_ses_engine.py`. The Memo and FSQ patchers are now thin calibration wrappers (constants + tripwire names only). Regression-proven: Memo CALIBRATION_TEST and FSQ CALIBRATION_TEST + Izzy 2.0 Deep Think all rebuild **md5-identical** to the pre-engine standalones (archived as `*_pre-engine_standalone.py`). A bug fix now lands once, for both venues.
- **MD lint is code:** `_shared/md_lint.py` runs automatically on every patch (and standalone). Hard errors abort the build: backwards band order (proven against the pre-2026-05-30 Brit Pack MD — 96 errors), malformed band lines, missing HPF/LPF, console-limit violations, unparseable DEQ clauses. Warnings (name >12 chars, fractional dB) surface without blocking — it already caught 'Acoustic Guitar' (15 chars) in the shipped Izzy MD.
- **Full readback every build:** the engine re-reads EVERY MD channel from the output .ses (names, bands at mapped bidx, HPF/LPF scaling, DEQ) and PASS/FAILs — the old "spot-check two channels by hand" step is retired. `_shared/readback_verify.py --venue memo|fsq --ses --md` re-checks an existing file without rebuilding.
- **Show scaffold:** `_system/scaffold_show.py` + the `new-show` skill — one command creates the dated show folder, copies the venue patcher as `apply_<short>.py`, and drops the MD stub with venue don't-forgets. No EQ content — that stays with show-deep-build.
- **send-it keeps no KB copies:** skill now reads the live KB (`Live Sound KB/Wiki/`) — single source of truth, no silent staleness.
- **CLAUDE.md slim-down (finally done, flagged since 2026-05-30):** the legacy EQ starting-point tables (old band layout) and the retired landscape-.docx show-doc format were removed from `~/Documents/Claude/CLAUDE.md`, `audio/CLAUDE.md`, and `~/.claude/CLAUDE.md`, replaced with pointers to the KB; the "all PDFs use ReportLab" line corrected to the weasyprint rule everywhere.
- Docs updated: pipeline-spec-memo/fsq (engine + auto lint/readback + verification blocks), ROUTING.md ("where things live" + footnote), NEW-SHOW.md (step 3 scaffold), send-it SKILL.md (automated gates), FSQ handoff (banner).

## 2026-07-01 — Memo template replaced (brian memo june 2026.ses) + patcher rebuilt on the FSQ engine; Deep Think EQ written into both pipeline specs

- **Memo .ses template swapped:** `brian memo june 2026.ses` (37,661,337 bytes, full console save) is now the master, canonical copy at `Memorial Hall/_TEMPLATE/` (offline-editor original in `~/.wine/drive_c/Templates/`). The old `brian memo v2.ses` (1,543,866 bytes, offline strip layout) is retired.
- **Memo patcher rebuilt** on the console-verified FSQ engine: surface table @ 0x231A48F (stride 125, 72 faders), contiguous current-scene blocks @ 0x2324D9C (stride 0x15A6), blocks matched to faders by name, dual offset tripwire (surface + block walk), stray-byte + do-not-write verification, same --src/--dest/--md CLI as FSQ. Old engine archived as `apply_show_TEMPLATE_v2_OLD_stripformat.py`. Smoke-tested byte-level (4-channel calibration MD: names ×20, B-mapping, HPF ×0.8 / LPF ×1.25, DEQ, Wireless baseline preserved, 0 stray bytes). **First show build still needs Brian's console verification.**
- Template baseline noted: Wireless 1–4 (faders 41–44) ship a starting vocal curve; channels 1–39 flat — MD-unnamed bands inherit, same convention as FSQ.
- **Deep Think EQ made explicit in both pipeline specs:** `pipeline-spec-memo` and `pipeline-spec-fsq` now carry the "EQ generation — Deep Think is the standard" section (show-deep-build driving eq-advisor, artist-first research, EQ Rationale PDF required); `show-processing-pipeline` wording aligned.
- Docs updated: pipeline-spec-memo (Step 3 rewritten), console-digico-q225 (patcher-constants section now points at the scripts as source of truth; stale FSQ 2,466,215 size fixed), venue-memorial-hall, ROUTING.md, send-it skill (+ its KB mirror synced), ShowBuilder venues.json, supersession banners on the three old Memo SOP docs.

## 2026-06-23 — eq-advisor EQ skill + wired into the show flow

- Built **eq-advisor** (installed as a plugin; source `_skills/eq-advisor/`): a standalone EQ-decision skill. Pipeline = instrument → mic → live forum research (Pro Sound Web LAB + Gearspace) cross-checked against `eq-starting-points`/`mic-library` (the two verify each other) → genre → venue/room. Cuts-first, whole-dB, stop-on-uncertainty (an unsure answer is treated as ~3× worse than a pause). Output inline + PDF (ReportLab, house palette) in the console band layout.
- **Made it the required EQ step in the show/ShowBuilder workflow:** wired into `_system/NEW-SHOW.md` (Stage 1 EQ + harvest), `showbuilder`, `show-processing-pipeline`, and a pointer in `eq-starting-points`. ShowBuilder's app engine and the skill both target the KB — kept consistent.
- **Self-improving:** logs every recommendation to `Live Sound KB/_learning/eq-advisor-log.md` and proposes KB write-backs (a Brian override = ground truth), published via wiki-publish — the same loop ShowBuilder uses.
- **Console scope:** defaults to Q225 (Memo/FSQ) / Wing (secondary). Does not produce CL3 or M32 layouts unless Brian explicitly names that desk.
- Delivered as `eq-advisor.plugin` (re-install to pick up these edits) + source synced to `_skills/eq-advisor/`. KB edits are local — not yet pushed to the live wiki (pending a wiki-publish run).

## 2026-06-30 — Edge→E40:2 amp power BUILT in Composer (ESP), Rev C

- Over AnyDesk into the ESP Composer 9.0 machine: saved a pre-edit backup (`ESP Spring 2026 temp - BACKUP 2026-06-30 pre-GPIO.symx`), took the design offline, and (Brian driving from click-by-click steps) placed **Local Logic Output #8** + a latching on/off toggle "Amp Power" in the EdgeESP design. NOT pushed — Brian pushes when ESP is safe.
- Final wiring simplified to Brian's requirement: **no relay, no power supply.** Direct open-collector — Logic Out #8 → both amps' GPI sense; Logic GND → both amps' GPI common (parallel). Rev C PDF rebuilt (single page, checked). Polarity + non-isolation caveats noted.
- Confirmed live: ESP runs **Composer 9.0** (KB had 8.5.x from web research) — corrected in `dsp-symetrix-edge`.

## 2026-06-22 — Edge → E 40:2 GPIO sheet Rev B (connector confirmed)

- Front-panel photo confirmed the E 40:2 control interface: a POWER STATE CONTROL/MONITOR block with separate GPI + GPO green Euroblock dry-contact pairs (GPI: short pair = on). Reworked the wiring sheet to Rev B — interposing relay now the lead recommendation (true floating closure, polarity-agnostic, dual-amp isolation; flyback diode noted), direct open-collector kept as the single-amp alternative. Updated active-projects entry. Both PDF pages re-checked, no clipping.

## 2026-06-22 — Edge → E 40:2 GPIO power-control design + wiring sheet

- Designed Edge logic-output → Lab Gruppen E 40:2 GPI on/standby control. E-Series GPI = dry contact closure (closed=on); Edge logic output = open-collector to ground — direct match. One output per amp, optional GPO status feedback, two wiring options (direct / interposing relay), Composer block list + power-on delay.
- Built `Edge_E40-2_GPIO_Power_Control.pdf` (Claude root; script `Code/_scratch/edge_e402_gpio_sheet.py`), visual-checked both pages, no clipping. Logged as active project. Open item: confirm E 40:2 connector pin numbers + amp auto-standby settings before install.

## 2026-06-22 — Added Symetrix Edge + Composer DSP reference

- New article `dsp-symetrix-edge.md` — platform reference for Brian's Edge install DSPs (analog/AES/Dante cards) and Composer software. Covers hardware architecture (4 slots, 400 MHz SHARC, 64×64 Dante, built-in managed Gig switch), the six option cards with model numbers (incl. AES split into 80-0067 in / 80-0068 out), control surface (ARC-WEB, GPIO, RS-232, Lua Intelligent Modules, scheduler), and Composer version notes (current line 8.5.x; 8.0 Lua/Media Manager, 8.4 Brooklyn 3/SSH Lua).
- Web-sourced (symetrix.co + datasheets), Status: emerging. Open items: which venues run Edge + per-frame card population, installed Composer build/firmware, Dante role. Linked from INDEX under Consoles.

## 2026-06-21 — New FSQ template + patcher recalibration

- Brian resaved the FSQ template. New `brian fsq start.ses` is **3,779,766 bytes** (was 2,466,215) — "everything changed": many more snapshots + a baked-in vocal/wireless starting curve. Every absolute offset shifted (file diverges at byte `0x22`); same byte format, only constants moved.
- Recalibrated `apply_show_TEMPLATE_FSQ.py` by a fresh ZZTOP save-diff (`brian fsq start.ses` vs `fsq edited new.ses`, kept in `~/.wine/drive_c/Projects/`). New constants: `SURF_BASE 0xA5571`, `SCAN 0x2D3000–0x33F000` (stride 125, 64 faders). All semantics re-confirmed on the new file: bidx order (b0=high), HPF ×0.8, LPF ×1.25, DEQ/comp tags.
- **Hardened the patcher:** offset tripwire (reads 64 fader names on load, aborts if they don't match `EXPECTED_NAMES` — a future resave/wrong `--src` now fails loudly instead of silently writing to the wrong region) + a block-span guard skipping non-unique names (FX returns, faders 37–44).
- **Vocal/wireless baseline (faders 25–36):** template ships these with a starting curve (HPF 184, B4 −18 dB notch @5k Q20, B2 −6.3 @335). Per Brian's call: keep it — patcher writes only MD-named bands, vocals inherit the baseline. Instrument channels 1–24 are flat.
- **Rolled out everywhere:** new template → both Mac copies (`_TEMPLATE/` + secondary); recalibrated patcher → SOP folder; ShowBuilder `venues.json` `output_bytes` 2,466,215 → 3,779,766 (byte-verify gate); KB `pipeline-spec-fsq` + the handoff SOP doc updated; saved a permanent `CALIBRATION_TEST` MD fixture. Console-verified by Brian (CAL test ch1/13/25) before rollout.

## 2026-06-16 — ShowBuilder app + KB additions

- Built **ShowBuilder** (`Code/ShowBuilder/`): a guided web app that turns a show spec into a Q225 `.ses` + paperwork by front-ending the existing patcher/packet pipeline. New KB article `showbuilder` documents it; `active-projects` gained a Tools & Infrastructure section.
- ShowBuilder derives its reverb library from `reverb-reference-memo` (parsed, names verbatim) and its EQ rules from `eq-starting-points`/CLAUDE.md — the KB stays authoritative; the app self-improves back into it.
- Logged in QUESTIONS: existing Memo show MDs (Seals/Brit Pack/Gospel) are pre-2026-05-30 backwards B-numbering and need conversion before reuse.
- **Wiki publish pipeline verified working — resolves the 2026-06-13 "PAT flagged / needs a live run" open item.** The `com.tinydoor.kb-gitpush` launchd agent auto-commits + pushes to the private `TinydoorStudios/live-sound-kb` repo (last push confirmed today) and publishes pages to Wiki.js via the GraphQL API (`kb-publish-pages.py`, `KB_WIKI_API_KEY` in `~/.claude/kb-secrets.sh`, valid to 2027) — git storage is disabled, so the API is the live path. Verified: GitHub PAT `GET /user` 200 + push perm true; Wiki.js graphql 200; auto-sync log `pages published … failed=0`; new `showbuilder` page renders 200 on the live site. The classic `repo`-scope PAT still works but lives in plaintext in the Mac remote URL and the Wiki.js storage config — rotate to a fine-grained token when convenient (not urgent: private repo, token not in git history). The recurring `line 12` entries in `kb-git-push.err` are stale (current script line 12 is blank).

## 2026-06-13 — Wiki.js rework + on-demand publish skill

- **Reworked all 28 wiki articles for Wiki.js.** Added proper Wiki.js frontmatter (`title`, `description`, `published`, `date`, `editor`, `tags`) to every article while preserving the KB's `Status`/`Last updated`/`Sources`/`Summary` keys (now quoted so colons don't break YAML). Converted all **183 `[[wikilinks]]`** — which Wiki.js renders as literal text — to real root-absolute Markdown links (`[Title](/slug)`). Slugs left flat/kebab-case so no existing URLs break.
- **Rebuilt `index.md`** as a clean grouped home page (Venues / Consoles / Kit & Technique / Workflows / Shows / Meta) with real links. Gave `shows.md` a real description.
- **Standardized show assets** to kebab-case under `assets/shows/<slug>/` (finished the in-flight Blue Eighty-Eight rename) and fixed the show/asset links from `/downloads/` back to `/assets/` (the path nginx actually serves). Cleared the stale `.git/index.lock` is deferred to the publish script (sandbox can't unlink inside `.git`).
- **Built the `wiki-publish` skill** (`_tools/wiki-publish.skill` + scripts in `_tools/`): on "publish to the wiki", it stages content correctly, then runs `kb-publish.sh` **on the Mac** (sandbox can't reach the Tailscale/LAN hosts) to commit + push to GitHub, rsync `assets/` to the n8n VM, force a Wiki.js sync, rebuild the left-nav sidebar from `kb-nav.json`, and verify a download returns 200. Every published file lands under `/assets/` on the server for cross-device download.
- **Open:** GitHub PAT still flagged compromised (rotate + update remote); Wiki.js API key needed in `~/.claude/kb-secrets.sh` to enable the auto sidebar; whole publish pipeline is built faithfully to the 2026-06-11 handoff but needs one live run to confirm (couldn't test against the offsite server from here).

## 2026-06-03 — Reusable image-embed workflow + C3 photo page

- Built `Live Sound KB/_tools/embed_refs.py`: drop real photos into `_refs/<topic>/`, optional `captions.tsv` (filename TAB caption TAB credit) or `<image>.txt` sidecars; the helper EXIF-corrects, crops, captions, and emits a 2-up photo grid (standalone contact sheet via CLI, or injectable flowables). This is the sanctioned alternative to web-scraping images, which the environment blocks (web tools return text only; browser screenshots don't persist to disk).
- Created drop folder `_refs/dpa-4099-c3/` with README + starter captions.tsv.
- Re-passed the C3 deep-dive: new **Real-world reference photos** page auto-fills from the drop folder (clean empty-state placeholder until Brian adds photos). Build is now self-contained at `_tools/c3-build/` (regenerates diagrams, writes to Outputs) — "rebuild" works in any future session.

## 2026-06-03 — DPA 4099 on the Yamaha C3 (deep dive)

- Added a **Yamaha C3 deep-dive section** to `mic-dpa-4099` and a companion PDF `Live Sound KB/Outputs/DPA-4099-on-Yamaha-C3.pdf` (6 pages). Brian's primary 4099 use case: stereo 4099P pair, run at the two lid extremes (full open / fully closed).
- Researched DPA "How to mic a piano" + Sound On Sound "Miking a piano concert with DPA" (real-gig 4099P). Key facts captured: grand exceeds **130 dB near the hammers** (validates Extreme SPL on close piano — the noise floor is a non-issue here); spaced high/low pair with bass mic over C2–G2 ~⅓ down the strings and treble ~oct-and-a-half above middle C; **≥30 cm spacing** (closer combs, too far leaves a hole in the middle); start EQ flat, ~90 Hz low-cut only, expect 250–400 Hz cuts on closed lid.
- Built three C3 diagrams (top-view spaced pair, open-vs-closed lid, tone/distance map). Viewed real DPA + SOS reference photos via the browser to draw the diagrams faithfully; could not embed the actual photo files (fetch tools return text only; screenshots don't persist), so the PDF carries a credited click-through gallery to the genuine photos/videos instead.

## 2026-06-03 — New article: DPA 4099 clip-on reference (Extreme SPL)

- Deep-researched the DPA 4099 CORE+ from DPA's official product page, manual, and "How to mount the 4099 on various instruments" guide, plus CORE+ campaign and SOS review. Wrote new KB article **`mic-dpa-4099`** (established).
- **Variant corrected mid-build:** Brian confirmed he owns 4× **Extreme SPL** (yellow band), not Loud SPL — 2 mV/Pa (−54 dB), 152 dB peak, 28 dB(A) self-noise, 109 dB dynamic range. The whole article is framed around the Extreme SPL reality (ideal on loud sources; needs ~10 dB more gain and shows its floor on quiet classical spots).
- Documented the full clip/mount ecosystem (VC4099, C/BC/GC/STC/P/D/U-CLIP, A-CLIP, CM/MS/CS, goosenecks), per-instrument mounting and placement for the top 20 instruments/applications, and conservative-by-default EQ starting points (whole-dB, subtractive, honoring the mic's built-in +2 dB 10–12 kHz boost).
- Generated companion illustrated PDF mini-wiki at `Live Sound KB/Outputs/DPA-4099-Mini-Wiki.pdf` (palette-matched, with mounting diagrams).
- Registered in INDEX (Kit & Technique), cross-linked from `mic-library`. Logged clip-inventory and wireless-adapter open questions.

## 2026-05-30 — Seventh Heaven Pro: full preset list ingested + article rebuilt

- Pulled the official **Liquidsonics Seventh Heaven Professional Presets List v1.100** (full PDF) and wrote the **complete 236-preset reference into `reverb-reference-memo`** — every bank + in-bank number + Decay/Pre-delay/VLF/Late-Rolloff/Early-Select/Algo. No more `#TBC`: every preset's number is now verified. All 6 previously-known numbers confirmed exact (Sunset Chamber Ch1 #17, Vocal Plate Pl1 #06, Gold Hall H1 #11, Snare Chamber Ch1 #09, Guitar Room R2 #16, Studio A R1 #01).
- Added a "What engineers reach for" section from the Liquidsonics pros article + Gearspace M7 thread (Sunset Chamber, Sun Plate A w/ LPF ~4–5k, Berliner Hall as a live trio; Vocal/Bright Plate for vox; Studio A glue; decay+filters-first advice).
- Added the **3–6 reverb options per show** guidance (2–3 vocal, 1 main instrument, 1–2 extras) to both pipeline specs, pointing at the reverb article.
- Generated a standalone multi-page reference PDF — `SOP Stuff/Memo/Seventh_Heaven_Pro_Preset_Application_Guide.pdf` (cover + Top-10 fast page + by-application picks + full 236-preset library with applications), built via weasyprint and visually verified.
- Rebuilt the entire `reverb-reference-memo` article cleanly in one pass (an earlier in-place splice had duplicated sections and dropped the full table). Verified final: 236 preset rows with correct per-bank counts, all 5 genre tables once each, no duplicate headers, all wikilinks resolve, no contamination. Added the full Controls Reference (incl. Master Filter, Ducker modes) and the engineer-favourites section sourced from the Liquidsonics pros article + community.

## 2026-05-30 — Seventh Heaven Pro reverb reference, corrected + per-venue

- **Early/Late behavior corrected** (Brian, direct): Early sits at MAX; Late is the variable, 0 dB → −20 dB, one notch past −20 = Late OFF. The prior "balance slider, hard-jump at Equal, displayed level on the near side" description was wrong. Recommendation notation locked: "E/L: Early MAX / Late −XdB | Late OFF | Equal" — never positive, never percentage pairs.
- **Always 100% wet** stated as a global rule; dropped the Mix value from the reverb line format. Format now leads with Bank / Name / preset # (when known).
- **Preset numbers:** 5 confirmed in-bank numbers added (Vocal Plate #06, Gold Hall #11, Snare Chamber #09, Guitar Room #16, Studio A #01); all others marked #TBC, to be harvested off the console over time. (Corrected an earlier overstatement of "10 confirmed.")
- **Per-venue scope:** `reverb-reference-memo` broadened to cover Memorial Hall (room-aware), Fountain Square (outdoor — minimal default, Late higher, VLF near factory), and post (factory-intent, no room corrections). Reconciled the FSQ pipeline-spec reverb section. Synced the reverb-format pointer in auto-memory.

## 2026-05-30 — Single-project consolidation

- KB confirmed as single source of truth. Folded the two detailed pipeline specs into the KB: new articles `pipeline-spec-memo` (from the retired Memo Work spec) and `pipeline-spec-fsq` (from the FSQ folder spec). `show-processing-pipeline` is now the linked overview.
- Fixed `venue-fountain-square` (duplicate heading) and `INDEX` (rewritten clean; pre-existing repeated-header corruption removed). Added pipeline articles to INDEX.
- `active-projects` upgraded to canonical project state: added Completed Shows log (Gospel Awards, Seals & Crofts 2, Brit Pack, Verve Pipe) and the Knowledge Harvest close-out loop.
- `venue-memorial-hall` show-folder note updated (Memo Work retired).
- Logged, then resolved, the EQ-table convention question. Brian confirmed the Q225 layout (HPF + LPF + 4 bands; each Shelf/Bell; any Bell can be Dynamic; no separate low shelf). Locked the canonical display order high→low (`HPF · LPF · Band 4 → Band 1`) with console-true band numbers (1 = LF, 4 = HF). Corrected the backwards "Band 1 = High Shelf" card numbering across `pipeline-spec-memo`, `pipeline-spec-fsq`, CLAUDE.md, and auto-memory. Rewrote `pipeline-spec-memo` clean (removed a duplicated section).
- Routing layer added at `_system/` (ROUTING, NEW-SHOW, IMPROVEMENTS, RESUME). Duplicates moved to `_ARCHIVE/` (reversible). Verified Memo crowd-mic EQ + AxeMount already present in KB — no migration needed.

## 2026-05-27 — Reverb reference rewrite (Seventh Heaven Pro accuracy pass)

Brian flagged reverb-reference-memo.md as ~50% inaccurate. Rewrote against official Liquidsonics documentation (Manual v1.5.7, Presets List v1.100).

Corrected:
- VLF: was described ambiguously. Correctly documented as a single level slider controlling the M7's sub-200Hz reverb component. Not an EQ band. At Memo, cut hard (−15 to −20dB or off) due to standing wave buildup in 60–315Hz range.
- Early/Late: was formatted as "XX/XX" implying two separate level values. Correctly documented as a single balance slider. The presets PDF shows the M7 hardware's original Early/Late capture levels, but the plugin control is one slider adjusting relative to that balance.
- HF Damp: does not exist in the plugin. Replaced with correct terminology: Late Rolloff (frequency) and Early Rolloff (frequency) — two separate controls. Late Rolloff is the primary tweak at Memo (4–6kHz classical, 8+ kHz contemporary).
- Pre-delay: clarified that it affects late reverb and VLF only — does NOT move the early reflections (M7 design behavior).
- Added full Controls Reference section documenting all key plugin parameters accurately.
- Added Nonlinear algorithm description.
- Updated reverb line format (locked): now includes VLF, E/L balance, Late Rolloff instead of old HF Damp / Early/Late XX/XX.
- Show Processing Quick Reference also corrected to match.
- All preset names verified against official presets PDF — names were correct, only the control descriptions and line format were wrong.

---

## 2026-05-27 — Source file pass (delta)

Read and applied: about-me.md, memory.md, writing-rules.md, Memorial Hall venue-notes.md, mic-go-tos.md, eq-starting-points.md, console-reference.md, reverb-reference-memo.md, 3CDC venue notes, Fountain Square / Washington Park / Elm Street Plaza venue-notes.md, Input_List_Design_Spec.md, Show Processing Quick Reference, New Show - Start Here, and recent show processing documents.

Auto-fixed:
- venue articles: Memo, FSQ, WP, ESP, CSP, ZP, IA all updated from stub → fully populated with PA system, console assignments, Tempest numbers, site notes
- console articles: Q225 updated with patcher workflow, Mustard rules, do-not-write tags, template path, VCA layout; Wing updated with ESP fixed-install and Greaves context; M32 updated with WP/FSQ role split
- mic-library: fully populated from mic-go-tos.md — all categories (dynamics, SDC, LDC, ribbons, DIs, standard combos)
- eq-starting-points: fully populated from eq-starting-points.md — instrument-by-instrument with genre modifiers
- multitrack-recording-workflow: corrected DAW — REAPER for capture (not Studio One 7); Studio One 7 is production DAW
- active-projects: populated from memory.md — LDB, FSQ Salsa, KSO S&G, Drowsey Lads, Israeli Chamber Project, open issue (n8n wind alert)
- new articles drafted: reverb-reference-memo, show-processing-pipeline, input-list-design-spec, venue-greaves-concert-hall
- INDEX updated: 8 venues, 4 consoles, 3 kit/technique, 5 workflow, 1 living document = 21 articles
- QUESTIONS.md: rebuilt with current gaps, high-priority items flagged

Pending judgement:
- Stage dimensions, FOH throw, power, load-in logistics for all 7 operational venues — not in source files
- MADI/recording interface model at Memo — not documented
- Standard sample rate per context — not documented
- CSP and IA Tempest unit assignments — TBD
- Greaves permanent folder path and house PA — TBD

---

## 2026-05-27 — Initial build

KB created from scratch. Articles seeded from Brian's system prompt context (consoles, venues, DAWs, workflow rules). Mic library and EQ starting points exist as stubs pending Brian's input.

## 2026-07-11 — The Hot Magnolias (FSQ) deep build

Full deep-research packet for The Hot Magnolias (Cincinnati 8-piece NOLA party band) at Fountain Square. Researched lineup (Burkett/Sharkey/Sowash/Cruse/McClellan/Thomas/Kottler/Mitchell), A-T Pro 35 horn behavior, NOLA brass masking, banjo-pickup DI. Built: FOH Channel Processing .md, Q225 .ses (patcher PASS, byte-identical size), styled Input List xlsx (design spec, 32 ch + spares + stage-layout tab), visual Stage Plot PDF, Show Packet PDF, EQ Rationale PDF, spec.json. EQ harvest to eq-starting-points/mic-library HELD pending Brian's console verify. Row added to active-projects. Flags raised: e609-on-hat, Vocal f25/f26 override of FSQ template curve, fader-10 "SNARE PL8"→OH R, keys mono/stereo.

## 2026-07-11 — The Hot Magnolias REV 2 (hot-mag 2) — corrected-pipeline rebuild

Re-ran The Hot Magnolias through the updated deep-build (the five 2026-07-08 console corrections now enforced). New folder `Fountain Square/hot-mag 2/`. Changes vs Rev 1: FSQ cuts re-cut DEEPER (−6 to −9, up to −10 on box/mud); Overheads collapsed to the STEREO pair on fader 9 (fader 10 = reserved SNARE PL8 return, validator-guarded, no longer split 9/10); guitar now a 57/27 blend (Guitar Dyn/CON, complement low-mids backed off, polarity-critical); required Seventh Heaven Pro reverb section shipped (3 vocal + 2 instrument + 1 general, verbatim from the reverb KB, + pairing); MASTER.pdf merge; NO stage plot generated (band-provided). Spec validation PASS 0 warnings, md_lint PASS, patcher PASS (bytes-outside 0, size identical, 17 faders incl. f9/f14, f10 untouched). EQ harvest still HELD pending console verify.

## 2026-07-09 — Skill consolidation: eq-advisor merged into show-deep-build + hot-mag A/B guardrails applied

One skill now runs the whole pipeline: `_skills/show-deep-build/` absorbed eq-advisor as its Part II ("The EQ method" — same 5 steps + locker pass; standalone EQ questions still trigger it). Old eq-advisor archived at `_skills/_ARCHIVE/eq-advisor-retired-2026-07-09/`; learning log keeps its name. `_system/NEW-SHOW.md` slimmed to a router (the duplicated deep-build prose removed — the skill is the single source of truth). All 11 edits from `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` applied into the merged skill: research floor (KB never a research source, quantitative capsule fact + named external source per unit, reconciliation line), capsule-voicing gate, two-mic lane ownership, section slotting in the numbers, three-option web↔KB forks with inline KB-update offers, fetched-never-assumed weather (both humidity cases), factory-anchored reverbs with material-fit selection, carried-flag consumption, numeric dynamics, switchable-hardware state flags. KB article `show-processing-pipeline.md` gained the "Deep-build quality floor" section (Last updated → 2026-07-09). New `show-deep-build.skill` package built for Cowork reinstall — the installed copies were stale snapshots (eq-advisor Jun 23, show-deep-build Jun 25) missing every July rule.

## 2026-07-09 — KB references synced to the merged skill

`eq-starting-points`, `show-processing-pipeline`, `showbuilder`, `pipeline-spec-memo`, `pipeline-spec-fsq`, and the active-projects eq-advisor entry all updated: "eq-advisor" as a standalone skill → "show-deep-build Part II (the EQ method, merged 2026-07-09)". No rule content changed — pointer updates only. Last-updated dates bumped where edited.

## 2026-07-14 — Dante-on-Cisco networking standard (new article + runbook)

Audited the four Cisco switch backups from the theater plant (Tech Table / FOH / BigRack / Attic), then deep-researched Dante switch practice against Audinate's official network-admin PDF, the Yamaha/Audinate SG300 guide, Biamp's Cisco SG guide, and Shure KB extracts. New article `dante-cisco-switch-config.md` (established — 4+ independent sources): DSCP 56/46/8 strict-priority queue map, one-querier-per-VLAN rule (snooping without a querier = the 5-minute Dante death), unregistered-multicast-stays-forwarding (mDNS/control are link-local, never IGMP-joined), sACN VLAN left un-snooped, Auto Smartport = dynamic config that vanishes on link-down. Companion dark-day runbook PDF in Outputs (`Dante-Switch-Runbook-2026-07-14.pdf`) with per-switch paste-in CLI: querier moves Tech Table→BigRack, FOH gi10 trunk allow-list fix, Attic gets snooping + real credentials, QoS normalized to Basic/trust-DSCP on all four, static trunks, RSTP root on BigRack. Open: which venue this plant is, FOH gi10 stale-backup check, VLAN 300 IGMP capability, firmware upgrades.
