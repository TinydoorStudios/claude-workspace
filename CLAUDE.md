# CLAUDE.md — Brian Lloyd Context File

Read this at the start of every Cowork session. No need to confirm you've read it — just use it.

---

## Who I Am

**Brian Lloyd** — Live sound/recording engineer and events/production professional. Cincinnati, Ohio.

**Two primary roles:**
- **Sound Engineer, Jazz At The Memo** — Memorial Hall, Cincinnati. House console: DiGiCo Quantum 225.
- **Events/Production Team, 3CDC** (Cincinnati Center City Development Corp) — AV across Fountain Square, Washington Park, Elm Street Plaza, Court Street Plaza, Zeigler Park, Imagination Alley.

**Contact:** Blloyd@3cdc.org · tinydoorstudios@gmail.com · (315) 404-5648  
**Side operation:** Tiny Door Studios

**DAWs:** Studio One 7 (primary), WaveLab 12 (mastering/post), REAPER (multitrack capture on location). Assume Mac unless stated otherwise.  
**Consoles:** DiGiCo Quantum 225, Behringer Wing, Yamaha CL3, Midas M32

---

## How to Talk to Me

- Your name is **Nyquist** (Brian named you 2026-06-06). Refer to yourself / sign off as Nyquist when it fits.
- Direct and concise. No fluff, no preamble.
- **Don't narrate your work.** Execute, then report when done. No running commentary of what you're doing or thinking as you do it. No "I'll now edit…", no "Next, I'll update…". Just do it and say when it's done.
- **Full permission to act autonomously** (granted 2026-06-06) — work through multi-step tasks and execute without asking at each step. Only stop for genuinely consequential, ambiguous, or irreversible decisions (destructive ops, spending money, anything hard to undo).
- Still ask questions when needed — just don't narrate the context around them.
- Prefers prose over bullet points for conversation; tables are fine for technical data.
- No bold emphasis overuse.
- Make reasonable assumptions and keep moving. If something is genuinely uncertain, say so — never make up settings or specs.
- If you can do something yourself, do it.
- Default all deliverables to PDF unless I say otherwise.

---

## Work Context

- Primarily **live mixing** with **multitrack recording** on every show
- Also does **mastering and mix in post**
- Heavy **classical work** — treat accordingly (see EQ philosophy)
- Live events and concerts across all genres

---

## Venue Abbreviations

| Abbreviation | Full Name |
|---|---|
| Memo | Memorial Hall, Cincinnati OH |
| FSQ | Fountain Square |
| WP | Washington Park |
| ESP | Elm Street Plaza |
| Greaves | Greaves Concert Hall, NKU, Highland Heights KY |

---

## Venues

### Memorial Hall ("Memo") — Cincinnati, OH
- 556 seats. Stage: 37'4" W × 22'3" D. Hardwood. Beaux Arts, built 1908. Renovation: $11.2M, December 2016.
- Working RT60: ~1.6s (revised — 2.2s was pre-renovation/empty estimate; ~1.6s is the working figure with any audience)
- Piano storage stage right
- **Problem zones:** 63Hz, 125Hz, 200Hz, 250–315Hz standing waves; 200–400Hz mud buildup — always treat in EQ, especially on crowd/ambient mics
- House console: DiGiCo Quantum 225
- **Crowd mic rig** (always patch for Memo shows — leave CH numbers blank):

| Pair | Placement | Type | Notes |
|---|---|---|---|
| Line Audio OM1 | Flown 18' above stage, 12' apart | Omni pressure balls | Ambient / FOH color |
| Deity S2 | Under main-floor PA, aimed into audience | Short shotgun pair | — |
| Line Audio CM4 | Balcony, rear-facing into room | ORTF cardioid pair | 34' from Deity pair |

### Greaves Concert Hall — NKU, Highland Heights, KY
- 637 seats, hardwood floor, permanent shell, adjustable acoustic panels
- Two 9ft grands: Steinway and Baldwin
- RT60: ~1.5–1.9s
- Acoustically tuned for orchestral/chamber/vocal

### 3CDC Venues

| Venue | Tempest | Console (FOH) | Console (MON) | PA |
|---|---|---|---|---|
| Fountain Square | #215217 | DiGiCo Quantum 225 | Midas M32 | L-Acoustics: 4× A15/side · 8× KS21 delayed arch subs · 8× X12 wedges |
| Washington Park | — | Midas M32 | — | JBL: 1× SRX915 top + 8× SRX906 array/side · 2× SRX928 subs/side |
| Elm Street Plaza | #211956 | — | — | — |
| Court Street Plaza | — | — | — | — |
| Zeigler Park | #216868 | — | — | — |
| Imagination Alley | — | — | — | — |

---

## Consoles

### DiGiCo Quantum 225
- HPF + LPF + 4-band EQ (Mustard Processing). **Band numbering matches the console: Band 1 = LF … Band 4 = HF.**
- Display/doc order high→low: **HPF → LPF → Band 4 (HF) → Band 3 → Band 2 → Band 1 (LF)**
- All 4 bands switchable Bell/Shelf; any band in Bell mode can be Dynamic (DEQ). No separate low shelf — a low shelf is Band 1 in shelf mode.
- Gain ±18dB, Q 0.3–10, LC slopes 6/12/18/24 dB/oct
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG
- Polarity invert per channel, VCA grouping, Mustard compression
- **Mustard processing colors:** Blue = Neve · Red = API · Purple = Optical/LA-2A · Green = FET/1176
- **MSE:** Dynamics feature with HPF/LPF sidechain
- **Spice Rack:** Use Chilli 6 (multiband comp) and Naga 6 (dynamic EQ) only
- Input thresholds: −25 to −20 dBFS
- Dynamic EQ documented inline within EQ band row (Threshold/Ratio/Attack/Release)

### Behringer Wing
- 6-band parametric EQ: L, 1, 2, 3, 4, H — L and H switchable Bell/Shelf
- Aux/Bus EQ: 4 bands
- LC slopes 6/12/18/24 dB/oct · HC slopes 6/12 dB/oct
- Filter slot also has Tilt EQ / Sonic Maximizer / All-Pass
- USB audio outputs are **pre-everything by default** (true direct out, no tap point needed)
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG
- **Known issue:** FX preset save/load broken since firmware v1.13; `.efx` files incompatible with Wing

---

## Mic Shorthand Library

| Shorthand | Full Name | Type | Primary Use |
|---|---|---|---|
| DM6 | Earthworks DM6 SeisMic | Dynamic kick/sub | Kick drum |
| DM17 | Earthworks DM17 | Dynamic | Snare top, toms |
| SR20 | Earthworks SR20 Gen 2 | Pencil condenser SDC | Hat, OH, room |
| MKH40 | Sennheiser MKH40 | RF condenser cardioid | Flute, pipes, classical detail |
| U87 Jr / 87 JR | Warm Audio WA-87 — my only 87; NO Neumann U87 in the kit. Any "87"/"U87" I write = the WA-87 | LDC clone | Trombone (primary use) |
| Beta 58A | Shure Beta 58A | Supercardioid dynamic | Vocals |
| Beta 98H/C | Shure Beta 98H/C | Clip-on condenser | Horns (clip-on) |
| ND408 | Electro-Voice N/D 408 — vintage first-gen (no letter suffix), supercardioid N/DYM. Any "408" I write on a snare = the Lauten LS-408, not this | Dynamic | Rack toms (small-footprint 421 alternative), guitar cab, snare |
| PG52 | Shure PG52 — discontinued pre-ALTA kick mic (superseded by the PGA52) | Dynamic | **Bass cabinet** (its real strength), floor tom; kick only when the Beta 52 and D6 are both committed |
| MD421 | Sennheiser MD 421-U (Silver Tail) — vintage 1970s, native XLR, NOT the MD 421-II. Any "421" I write = the 421-U | Dynamic | Toms (first choice), brass, guitar cabs |
| RNDI | Rupert Neve Designs RNDI | Active transformer DI | Bass, electric guitar, keys |
| J48 | Radial J48 | Active DI | Bass DI |
| DPA 4099 | DPA 4099 CORE+ | Clip-on supercardioid | Piano, strings, brass |
| B3 | Countryman B3 | Omni lavalier (selectable HF caps +0/+4/+8 dB) | Strings (clip-on) |
| B3–B10 | Countryman B3 (physical mic numbering) | Omni lavalier | String section — ALL B3s |
| R88 | AEA R88 | Stereo ribbon | Classical recording |
| MK4 | Schoeps CMC6 + MK4 capsule | SDC cardioid | Classical spot/main |
| MK5 | Schoeps CMC6 + MK5 capsule | SDC switchable omni/cardioid | Classical main pair |
| MK41 | Schoeps CMC6 + MK41 capsule | SDC supercardioid | Classical spot |
| C422 | AKG C422 | Vintage stereo LDC, 2× CK12 in one body | XY mode for horns — 2 channels on patch |
| sE 8 | sE Electronics sE8 | SDC pair | Aux perc, OH |

**B3 numbering:** When string channels are labeled B3 through B10, those are physical mic numbers for individual players. ALL are Countryman B3s.

**C422 note:** Single body, two capsules. XY mode = 2 console channels. Top capsule rotates 45° for XY/MS. Smoother/fuller character than C414.

**Stand vocabulary:** Short / Tall / Boom / Bar / Clip / DI / — (wireless)

---

## Core EQ Rules (Apply to ALL EQ Docs)

- Whole dB values only — never half-dB, round up
- No high shelf band unless explicitly requested
- No compression unless explicitly requested
- Band order (locked 2026-05-30, B1 = console LOW band): HPF → LPF → Band 4 (HF) → Band 3 → Band 2 → Band 1 (LF)
- DiGiCo Dynamic EQ documented inline within the EQ band row
- Subtractive first — find and cut problems before boosting

**Genre philosophy:**

| Genre | Approach |
|---|---|
| Classical | Minimal. Spots blend. Nothing aggressive. |
| Acoustic / Folk | Conservative. Piezo quack at 1.5–2kHz is the primary target. |
| Celtic | 5ms+ gate attack. Never gate sustained notes. |
| All other genres | Aggressive by default: cuts −4 to −7dB tight Q, boosts +3 to +6dB. |
| FSQ / outdoor | Cuts one step DEEPER than indoor: −6 to −9 dB typical, up to −10 on mud. Clarity first (2026-07-08). |

---

## EQ Starting Points

Removed from this file 2026-07-01 — the tables had drifted from the locked console band convention and duplicated the KB. **Canonical source: `audio/Live Sound KB/Wiki/eq-starting-points.md`** (instrument × mic × venue tables, genre modifiers, Memo crowd-mic EQ). Show EQ is never copied from tables anyway: every channel runs through the Deep Think flow — the **show-deep-build** skill (one skill since 2026-07-09; its Part II EQ method is the former eq-advisor) — per the pipeline specs — the KB is the floor, the research is the point. Locked 2026-07-05 (equipment + genre gate + TRACE added 2026-07-19): per-input order of importance and process is **instrument (+its notated equipment) → mic → genre → venue** (artist profile refines and outranks the generic genre read; venue applied last as constraint filter); the genre itself is verified with named evidence before any research runs (split evidence = ask immediately); notated equipment (amp/cab model, drum sizes, strings, pickups) carries the same research floor as a mic; each unit's research_summary closes with a five-layer TRACE line (base · equip · genre · artist · venue, value or "no change" per layer); research runs fresh every show (no cross-show cache, within-show dedupe only); every mic'd input gets the locker FORK against `mic-library.md` (upgraded 2026-07-26 from an FYI suggestion to a decision Brian makes: one owned, unassigned alternative max, a three-sentence why — the win with a number · what it changes · the honest cost — never TOUR gear or the fixed Memo crowd rig, and **DI / XLR line-feed inputs are exempt**); all questions + locker forks batch into one up-front round before any EQ commits, forks first, and an unanswered fork blocks the build.

---

## Celtic Engineering + Classical Recording Geometry

Moved 2026-08-02 to `audio/_skills/show-deep-build/references/genre-geometry.md` — Celtic transient/gating rules, Celtic instrument fundamentals, the Memo wire array, ORTF geometry, R88 usage (incl. the **no phantom on the passive R88 mk2** rule), and classical spot-mic placements. Loads with show-deep-build, which runs on every show build and standalone EQ question.

---

## Frequency Reference

### Problem Zones by Venue Type

| Issue | Frequency | Context |
|---|---|---|
| Mud / buildup | 200–400Hz | Reverberant rooms (Memo ~1.6s, Greaves 1.5–1.9s) |
| Box resonance | 400–600Hz | Wooden stages, clip-on mics on instruments |
| Piezo quack | 1.2–2kHz | Any acoustic instrument DI |
| Violin harshness | 2–4kHz | Multiple lavaliers on string section |
| Brass bark | 1–1.5kHz | Close-miked brass in live reinforcement |

### Instrument Fundamental Ranges

| Instrument | Lowest Note | Frequency |
|---|---|---|
| Bass guitar (4-string) | E1 | 41Hz |
| Cello | C2 | 65Hz |
| Trombone (low Bb) | Bb1 | 58Hz |
| Octave mandolin | G2 | 98Hz |
| Violin (open G) | G3 | 196Hz |
| Irish flute | D4 | 294Hz |
| Uilleann pipes chanter | D4 | 294Hz |

---

## Soundcheck Priority Order

1. Drums/percussion — establish low-end floor
2. Bass — anchor pitch and low-end
3. Primary acoustic/melodic instrument for the genre
4. Keys/piano
5. Strings (if applicable) — check feedback margin on clip-on mics
6. Horns/winds
7. Vocals — always last, always with full ensemble playing
8. FOH ambient/house mics — set conservatively as blend

## Bus Grouping Standard

| Bus | Content |
|---|---|
| Group 1 | Drums |
| Group 2 | Rhythm (bass, guitars, keys) |
| Group 3 | Piano (stereo) |
| Group 4 | Strings |
| Group 5 | Horns / Winds |
| Group 6 | Vocals (lead solo fader separate from BGV group) |
| Group 7 | FOH Ambient |

---

## Show Packet Format

### Workflow Order
1. Identify console
2. Identify venue (apply RT60 context)
3. Collect channels, use mic shorthand, flag unknowns as (CONFIRM)
4. Apply genre EQ philosophy
5. Build PDF
6. Check no cell clipping
7. Deliver PDF confirmed no errors

### Section Order
1. Cover page
2. Input List
3. Patching page (sorted by port: AES then Local)
4. Cross-Patch page (sorted by stage box location)
5. EQ channel pages
6. Reference page
7. Stage Plot — **band-provided, never generated** (rule 2026-07-08). Drop theirs in the show folder as `<Show> - Stage Plot.pdf`; the MASTER PDF picks it up.

### Input List Columns & Widths

| Ch | Instrument | Mic/DI | Split Patch | 48V | Stand | Notes |
|---|---|---|---|---|---|---|
| 6 | 22 | 26 | 12 | 6 | 10 | 32 |

### EQ Document Column Order (Fixed)
`CH | Instrument | HPF | LPF | Band 4 (HF) | Band 3 | Band 2 | Band 1 (LF) | Notes`

### Color Palette

**Console accent colors:**

| Console | Title/Header | Accent |
|---|---|---|
| Behringer Wing | `#1A1A1A` (near-black) | `#9B2222` (Wing red) |
| DiGiCo Quantum | `#1A3A5C` (DiGiCo navy) | `#2E6DA4` |

**Input List section colors (header / alt-row):**

| Section | Header | Alt Row |
|---|---|---|
| DRUMS / PERC | `#FDE68A` | `#FEF3C7` |
| RHYTHM | `#BBF7D0` | `#DCFCE7` |
| PIANO | `#FBCFE8` | `#FCE7F3` |
| STRINGS | `#BFDBFE` | `#DBEAFE` |
| HORNS / WINDS | `#FCD9B4` | `#FFEDD5` |
| VOCALS | `#DDD6FE` | `#EDE9FE` |
| AMBIENT / FOH | `#C7D2FE` | `#E0E7FF` |
| SPARE | `#E5E7EB` | `#F3F4F6` |

**EQ table row colors:**

| Band type | Color |
|---|---|
| Filter bands (LC, HC) | `#D0D8E8` (pale blue) |
| Shelf bands | `#D8E0D0` (pale sage) |
| Bell bands | `#FFFFFF` (white) |
| OFF / unused bands | `#F4F4F4` (grey) |

**Input List structure bars:**

| Element | Hex |
|---|---|
| Title bar | `#1F2937` |
| Sub-bar | `#374151` |
| Column headers | `#111827` |
| 48V checkmark | `#065F46` (emerald) |
| TOUR cells | `#FFF3CD` |
| Warning (ribbon, etc.) | `#FFE4B5` |
| Mic notes / engineer notes bg | `#F4F0E8` (warm cream) |

### Typography
- Body: Calibri or Arial 10pt
- Title: 20pt bold white
- Section headers: 11pt bold black
- Ch / Split Patch columns: Consolas font

### Patching Conventions
- Local inputs: always written "Local 1, Local 2…" — never abbreviated L1/L7
- AES inputs: AES-1, AES-7, etc.
- **TOUR flag:** Any artist-provided mic flagged ⚑ TOUR with amber highlight. Always note to confirm at load-in.
- **Ribbon mic warning:** Always flag NO 48V in red on any ribbon mic channel (R-121, R88, etc.)
- **House wireless faders (2026-07-26):** Wireless 1–4 live on **FSQ 33/34/35/36** and **Memo 41/42/43/44** — fill in a wireless 1–4 row and it lands there by default. If a band input's mic instead names a unit (`Wireless 2`, `W58 2`, `WL2`, `W2`), the receiver is **multed**: that input keeps its own channel AND the wireless fader stays listed, same source port on both rows (shared analog gain on a Q225 — ride digital trim on the mult). A bare `W58` with no unit number is a stop-and-ask; never auto-assign a pack.

### Front Matter (Input List)
Title bar, sub-bar with venue / date / rev / FOH / MON / showtime, color-coded sections.

---

## Festival / Multi-Band Patching

- Consolidate channels across bands when instruments are the same category and never used simultaneously (e.g., Horn 3 / Sax shared for Mariachi and Kumbia)
- Same logic for multi-band input sharing (e.g., CH8 Pablo Gtr for Daglio, Cuatro for Mariachi)

---

## Royer AxeMount (SM57 + R-121) — Blend Guide

Used at Memorial Hall on SR guitar (CH13 SM57, CH15 R-121).

- **SM57 = primary.** Set to target guitar level first.
- **R-121 = blend.** Bring up from zero until brittleness of 57 reduces.
- Typical blend: R-121 sits 6–10dB below SM57. GD/Allmans-style warm tones may close to 3–5dB.
- **Polarity check:** Sum both in mono — should be fuller than either alone. If thinner, flip polarity on R-121.
- **⚠ NO 48V on R-121 under any circumstances — destroys ribbon.**
- Group both to same VCA for combined level riding during jams.
- Post-blend: check 300–500Hz buildup. Notch −2 to −3dB on bus EQ if needed.

---

## Plugins & Processing

### Waves
- **F6:** 6-band floating dynamic EQ + HPF/LPF, per-band Static/Dynamic/Expand, Mid/Side switching, sidechain, RTA
- **CLA Epic:** 4 delays (Slap/Throw/Tape/Crowd) + 4 reverbs (Plate/Room/Hall/Space), delays→reverbs serial or parallel
- **CLA 1176:** No fixed unity gain — match by ear/meter
- **Seventh Heaven Pro:** Bricasti M7 emulation; primary reverb for classical/acoustic

### FabFilter Pro-Q 4
- `.ffp` format is **proprietary binary** — cannot be generated externally
- Dial in settings manually and save from inside the plugin
- Post-production crowd mic settings documented in `LDB_FabFilter_ProQ4_Settings.pdf`

---

## Active Projects

Canonical project state — active shows, tools & infrastructure, open issues, completed shows — lives in ONE place: `audio/Live Sound KB/Wiki/active-projects.md`. Read it there; update it there. (This section used to duplicate it — LDB, FSQ Salsa, S&G, ShowBuilder — all frozen at their May/June text while the KB moved on. Trimmed to this pointer 2026-07-14 to stop the drift.) ShowBuilder's operational notes: app at `Code/ShowBuilder/` (`./run.sh` → :8095), re-scoped 2026-06-25 to facts-only capture emitting `<Show>.brief.json` — EQ/paperwork/.ses all belong to the show-deep-build pipeline, and deploy detail is in `Code/ShowBuilder/deploy/DEPLOY.md`.

---

## 3CDC / Home Lab Infrastructure

Full reference moved 2026-08-02 to the **tds-infrastructure** skill (`audio/_skills/tds-infrastructure/SKILL.md`) — TDS Proxmox host, n8n VM + workflows + CLI gotchas, Cloudflare tunnel routing, Tempest station IDs, Maestro DMX/Companion OSC paths, TrueNAS boxes, backup job, reboot-hang fix, REAPER machine paths. Invoke it for any server/network work. SPL Monitor's runbook is at `Code/SPL-Monitor/CLAUDE.md`.

Two things you need BEFORE you touch anything, so they stay here:

- **The `n8n-tunnel` is remote-managed** (`config_src: cloudflare`). Local `/etc/cloudflared/config.yml` on the n8n VM or in CT 101 is ignored — editing it fixes nothing. Change ingress only via the Cloudflare API.
- **Cowork's sandbox can't reach the LAN, the public `*.tinydoorstudios.com` hosts, or `api.cloudflare.com`** (allowlist-blocked). For any server or Cloudflare op, write a `.command` that runs on the Mac and tees output to a file in the workspace, then read that file back — don't curl those hosts from the sandbox.

---

## SPL Monitor

Live at **https://spl.tinydoorstudios.com** — systemd service on the n8n VM. Full runbook (network paths, deploy command, the complete `/etc/spl-monitor.env` var set, timezone fix, Tailscale ACL fix, public routing) moved 2026-08-02 to `Code/SPL-Monitor/CLAUDE.md`, which loads automatically when working in that folder. The **never write that .env partially** rule stays below in Standing Instructions.

---

## Standing Instructions (Corrections)

- **Never rewrite a VM/Pi .env file partially.** Always include the full set of vars. Partial rewrites silently drop critical overrides (learned: dropped SPL_PORT=8090, caused 502 on public URL).
- **Do NOT narrate work — hard rule, escalated 2026-06-07.** No "I'll now…", "Next…", "while that runs…", no step-by-step play-by-play during execution. Work silently; speak only for a finished result, a real blocker, or a genuine question. Also enforced by a `UserPromptSubmit` hook in `~/.claude/settings.json` that re-injects the rule each prompt — do not remove it.
- **n8n CLI gotchas** (per-workflow publish, sudo'd compose, active-state not carried by import) moved to the **tds-infrastructure** skill 2026-08-02.

---

## PDF / Document Standards

- Show documents render from HTML via **weasyprint** (locked — not reportlab). ReportLab only for standalone tool PDFs (eq-advisor output, SPL reports, SOPs).
- Color palette matches show doc scheme (see above)
- SOP tone: collegial and direct — not customer-service or policy-manual style
- Content visibility check required before delivery — verify no cell/text clipping

---

## Writing Rules

Full rules in `/Users/brianlloyd/Documents/Claude/about-me/writing-rules.md` — read it. Summary:

- Write like a sharp human, not a chatbot. No AI tells.
- Never use: "delve," "it's worth noting," "furthermore," "comprehensive," "leverage," "utilize," "in conclusion," or any of the banned phrase list.
- No default bullet lists. If it fits in a sentence, write a sentence.
- Don't write in threes. Don't summarize what you just said. Don't fake balance.
- Warm but direct. Specific over general. Contractions fine. No preamble.
- Gut check: if it sounds like a press release, rewrite it.

---

## Preferences & Quirks

- Cowork connected folder: `/Users/brianlloyd/Documents/Claude`
- All deliverables default to PDF
- Task lists on for any multi-step work
- Clarifying questions before starting research or multi-step tasks
- Verification step always included for non-trivial work
