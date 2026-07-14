# Brian Lloyd — Claude Global Context

*Last updated: 2026-05-27*

---

## Session Start Instructions

At the start of every session, read these files before doing anything else:

- `~/Documents/Claude/audio/_system/ROUTING.md` — venue → folder · console · specs map (the control center for show work)
- `~/Documents/Claude/audio/_system/NEW-SHOW.md` — the deterministic flow for any show conversation
- `~/Documents/Claude/audio/about-me/about-me.md` — who Brian is, his tools and venues
- `~/Documents/Claude/audio/about-me/writing-rules.md` — how to write without sounding like an AI
- `~/Documents/Claude/audio/about-me/memory.md` — session history (project state lives in the KB, see below)
- `~/Documents/Claude/audio/Live Sound KB/Wiki/INDEX.md` — KB article map; pull specific articles as the task requires — do not read all articles at startup

**about-me is ONE set of files (unified 2026-07-06).** Canonical location: `~/Documents/Claude/about-me/`. Both `~/Documents/Claude/audio/about-me/` and `~/.claude/about-me/` are symlinks to it, so the paths above work in every session type and always hit the same files. The audio copy had forked (session notes were splitting between two memory.md files); its unique content was merged into the canonical file and the pre-merge copies archived as `audio/about-me/_pre-merge-*-2026-07-06.md`.

**Canonical sources:** Knowledge → `Live Sound KB/Wiki/`. Project state → `Live Sound KB/Wiki/active-projects.md`. The EQ/console/mic tables embedded below mirror the KB during the migration; when they disagree, the KB wins. (The old `Memo Work/` and `workflow start files/` duplicate kits were archived to `_ARCHIVE/` on 2026-05-30.)

After completing meaningful work: update `Live Sound KB/Wiki/active-projects.md` + `CHANGELOG.md`, log workflow/structure changes to `_system/IMPROVEMENTS.md`, open items to `Live Sound KB/Wiki/QUESTIONS.md`, and append session history to `about-me/memory.md`.

---

## Who You're Working With

**Brian Lloyd** — Live sound/recording engineer and events/production professional, Cincinnati, Ohio. 20+ years in the industry.

**Primary roles:**
- Sound Engineer, Jazz At The Memo — Memorial Hall, Cincinnati. House console: DiGiCo Quantum 225.
- Events/Production Team, 3CDC (Cincinnati Center City Development Corp) — AV across Fountain Square, Washington Park, Elm Street Plaza, Court Street Plaza, Zeigler Park, Imagination Alley.

**Contact:** Blloyd@3cdc.org · (315) 404-5648 · tinydoorstudios@gmail.com

**Side operation:** Tiny Door Studios

---

## How To Work With Brian

- **Direct and concise. No fluff, no preamble.**
- **Step-by-step when troubleshooting** — stop and confirm before moving on. Do not get ahead.
- **Never assume. Always verify.** If something is unclear, stop and ask. Brian would rather answer a question than have you guess wrong.
- **Ask questions as you go.** This is preferred over making assumptions.
- **If you can do something yourself, do it** — don't ask for permission to act when the task is clear.
- Talk at a high level — Brian has 20+ years of experience. Do not over-explain basics.
- Prose over bullet points for conversation. Tables are fine for technical data. Minimal bold/header use.
- **Default output format: PDF** unless otherwise specified.
- **Writing tone:** When asked to write anything — emails, SOPs, show docs, communications — use a warm tone that is clear and direct. Not corporate, not stiff. Collegial.

---

## DAWs & OS

- **Primary DAWs:** Studio One 7, WaveLab 12
- **Capture DAW:** REAPER — multitrack capture on location
- **OS:** macOS — assume Mac unless Brian states otherwise

---

## Consoles

### DiGiCo Quantum 225 (Jazz At The Memo / Memorial Hall)
- HPF + LPF + 4-band EQ (Mustard Processing); each band Shelf/Bell, any Bell band can be Dynamic
- EQ: HPF + LPF + 4 bands. Display order high→low: HPF → LPF → Band 4 (highest) → Band 3 → Band 2 → Band 1 (lowest). Band numbering matches the console: Band 1 = LF, Band 4 = HF.
- Gain ±18dB, Q 0.3–10, LC slopes 6/12/18/24 dB/oct
- All 4 bands switchable Bell/Shelf; any band in Bell mode can be Dynamic (DEQ). No separate low shelf — a low shelf is Band 1 in shelf mode.
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG
- Polarity invert per channel, VCA grouping, Mustard compression

### Behringer Wing (secondary/other venues)
- 6-band parametric: L, 1, 2, 3, 4, H — L and H switchable Bell/Shelf
- Aux/Bus EQ: 4 bands
- LC slopes 6/12/18/24 dB/oct, HC slopes 6/12 dB/oct
- Filter slot also has Tilt EQ / Sonic Maximizer / All-Pass
- USB audio outputs are pre-everything by default
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG
- **Known issue:** FX preset save/load broken since firmware v1.13; `.efx` files incompatible with Wing

### Other consoles in rotation
- Yamaha CL3
- Midas M32

---

## Work Context

- Primarily **live mixing** with **multitrack recording** on every show
- Also does **mastering and mix in post**
- Heavy **classical work** — treat accordingly (see EQ philosophy)
- Live events and concerts across all genres

---

## Mic Shorthand Library

| Shorthand | Full Name |
|---|---|
| DM6 | Earthworks DM6 SeisMic kick mic |
| DM17 | Earthworks DM17 snare/tom |
| SR20 | Earthworks SR20 Gen 2 pencil condenser |
| MKH40 | Sennheiser MKH40 RF cardioid |
| U87 | Neumann U87 |
| U87 Jr | Warm Audio WA-87 (used on trombone) |
| Beta 58A | Shure Beta 58A vocals |
| Beta 98H/C | Shure Beta 98H/C clip-on horn mic |
| MD421 | Sennheiser MD421 dynamic |
| RNDI | Rupert Neve Designs active transformer DI (bass/gtr/keys) |
| J48 | Radial J48 active DI |
| DPA 4099 | DPA 4099 CORE+ clip-on supercardioid (piano/strings/brass) |
| B3 | Countryman B3 omni lavalier (selectable HF caps +0/+4/+8 dB) |
| B3–B10 | String channels — ALL are Countryman B3s (physical mic numbering) |
| R88 | AEA R88 stereo ribbon — classical recording |
| MK4/MK5/MK41 | Schoeps CMC6 + capsule |
| C422 | AKG C422 vintage stereo LDC (2× CK12, XY mode for horns, 2 channels on patch) |
| sE 8 | sE Electronics sE8 SDC |

---

## Venues

### Memorial Hall (Jazz At The Memo) — Cincinnati, OH
- 556 seats
- Stage: 37'4" W × 22'3" D
- RT60: ~1.6s working (2.2s was pre-renovation/empty estimate — use 1.6s for all processing decisions)
- Piano storage stage right
- **Standing wave problem zones: 63Hz, 125Hz, 200Hz, 250–315Hz** — always treat in EQ, especially crowd/ambient mics
- House console: DiGiCo Quantum 225
- Crowd mic rig (always patch for Memo shows — leave CH numbers blank):
  - Line Audio OM1 pair — flown 18' above stage, 12' apart, pressure balls, omni
  - Deity S2 pair — short shotgun, under main-floor PA, aimed into audience
  - Line Audio CM4 pair — ORTF, balcony, rear-facing into room, 34' from Deity pair

### Greaves Concert Hall (NKU, Highland Heights KY)
- 637 seats, hardwood floor, permanent shell, adjustable acoustic panels
- Two 9ft grands: Steinway and Baldwin
- RT60: ~1.5–1.9s
- Acoustically tuned for orchestral/chamber/vocal

### 3CDC Venues
- Fountain Square (Tempest station #215217)
- Washington Park
- Elm Street Plaza (Tempest station #211956)
- Court Street Plaza
- Zeigler Park (Tempest station #216868)
- Imagination Alley

---

## Show Document Format

Locked format lives in the KB: `pipeline-spec-memo` / `pipeline-spec-fsq` (channel cards, section order) and `input-list-design-spec` (colors, columns, typography). Deliverables: MD + HTML + PDF, the PDF rendered from the HTML via **weasyprint** (the old landscape-.docx/docx-npm format is retired). Default delivery: PDF.

---

## EQ Philosophy

**All genres except classical: aggressive EQ by default.**
- Cuts: -4 to -7 dB, tight Q (1.5–2.0)
- Boosts: +3 to +6 dB
- Whole dB values only — never half-dB
- No high shelf band unless specifically requested
- Subtractive first

| Genre | Approach |
|---|---|
| Classical | Minimal. Spots blend. Nothing aggressive. |
| Acoustic/Folk | Conservative. Piezo quack at 1.5–2kHz is the primary problem. |
| Celtic | 5ms+ attack, never gate sustained notes. |
| Everything else | Aggressive by default. |
| FSQ / outdoor | Cuts one step DEEPER than indoor: −6 to −9 dB typical, up to −10 on mud. Clarity first (2026-07-08). |

---

## EQ Starting Points

Removed from this file 2026-07-01 — the tables had drifted from the locked console band convention and duplicated the KB. **Canonical source: `audio/Live Sound KB/Wiki/eq-starting-points.md`** (instrument × mic × venue tables, genre modifiers, Memo crowd-mic EQ). Show EQ is never copied from tables anyway: every channel runs through the Deep Think flow — the **show-deep-build** skill (one skill since 2026-07-09; its Part II EQ method is the former eq-advisor) — per the pipeline specs — the KB is the floor, the research is the point. Locked 2026-07-05: per-input order of importance and process is **instrument → mic → genre → venue** (artist profile refines and outranks the generic genre read; venue applied last as constraint filter); research runs fresh every show (no cross-show cache, within-show dedupe only); every mic gets the locker check against `mic-library.md` (one owned alternative max, never TOUR gear); all questions + locker alts batch into one up-front round before any EQ commits.

---

## Royer AxeMount (SM57 + R-121) Blend Guide

Used at Memorial Hall on SR guitar (CH13 SM57, CH15 R-121).

- SM57 = primary. Set to target guitar level first.
- R-121 = blend. Bring up from zero until brittleness of 57 reduces.
- Typical blend: R-121 sits 6–10dB below SM57. GD/Allmans-style warm tones may close to 3–5dB.
- Polarity check: Sum both in mono — should be fuller than either alone. If thinner, flip polarity on R-121.
- ⚠ NO 48V on R-121 under any circumstances — destroys ribbon.
- Group both to same VCA for combined level riding during jams.
- Post-blend: check 300–500Hz buildup. Notch -2 to -3dB on bus EQ if needed.

---

## Active Projects / Ongoing Shows

### Live Dead and Brothers (LDB)
- GD/Allman Brothers tribute — Memorial Hall
- Files built: `LDB_Show_Document.docx`, `LDB_FabFilter_ProQ4_Settings.pdf`
- 21 input channels + 6 crowd mics
- Royer AxeMount on SR guitar (CH13 SM57, CH15 R-121)
- All TOUR wireless vocals — confirm RF coordination at load-in
- IEM: Hardwire Mix 7 on drums; MIX 1–5 stage wedges

### FSQ Salsa (Weekly Repeating — Fountain Square)
- Conversion sheet built: `FSQ_Salsa_Patch_2026.pdf`
- 32-channel show: Standard snake labels → Salsa-specific inputs
- CH 25–28: Dante 49–52 for wireless vocals
- CH 13–16: Guitar inputs repurposed as Keys 1–4
- CH 17–21: Misc inputs repurposed as Timbales/Quinto/Tumba/Bongo

### Simon & Garfunkel Tribute
- Console: Behringer Wing
- Piano: 9ft Steinway, short stick lid
- Mics: DPA 4099 stereo pair (piano mount clips, magnet mounts on frame)
- EQ: Conservative cuts-only (see Classical section above)
- No show document built yet

---

## 3CDC Automation / Infrastructure

### n8n Workflows (Raspberry Pi — n8n.tinydoorstudios.com via Cloudflare tunnel)
- Lightning Strike Alert — dual Tempest redundancy, tiered Slack alerts, auto-clear
- Wind Gust Alert — three MPH threshold tiers, 15-min rate limiting
- Rain Forecast Alert — Open-Meteo polling
- Show Reports — Google Sheets trigger → HTML email with conditional Drive photo attachments
- **Known issue:** Wind Alert Slack messages still have TEST TEST TEST prefix — unresolved

### Tempest Weather Stations

| Station | ID |
|---|---|
| Fountain Square | 215217 |
| Elm Street Plaza | 211956 |
| Zeigler Park | 216868 |

Workflows use scheduled REST API polling (not webhook push).

### Maestro DMX / Companion Control
- Maestro DMX: `maestro.local/#/show` (Chrome bookmark "DMX")
- Companion: Generic OSC module, UDP port 7672
- Key OSC paths: `/global/brightness`, `/show/index`, `/show/cue/index`, `/show/stop`, `/show/play_pause`, `/show/cue/next`, `/show/cue/previous`

---

## Home Lab / Self-Hosted Infrastructure

| System | Details |
|---|---|
| n8n | Raspberry Pi, n8n.tinydoorstudios.com, Cloudflare tunnel |
| Audio NAS (TrueNAS) | 192.168.200.36 |
| Cold Storage (TrueNAS) | 192.168.200.35 · Tailscale 100.126.177.120 |
| Backup script | `/mnt/AudioNas/scripts/backup-to-coldstorage.sh` · cron 2AM |
| Cold Storage SMB ACL | Must stay nfsv4 |

**REAPER:**
- 7th-Heaven machine: primary `A:\2026\$project`, secondary `Z:\FSQ\2026\$project`
- Memo-Fourwinds machine: template at `C:\Users\Memo-Fourwinds\AppData\Roaming\REAPER\ProjectTemplates\memo show.rpp`

---

## Document & PDF Standards

- Default output format: **PDF**
- Show documents render from HTML via **weasyprint** (locked). ReportLab only for standalone tool PDFs.
- Color palette matches show doc scheme (see above)
- SOP tone: collegial and direct — not customer-service or policy-manual style
- Content visibility check required before delivery — verify no cell/text clipping

## FabFilter Pro-Q 4 Notes
- `.ffp` format is proprietary binary — cannot be generated externally
- Dial in settings manually and save from inside the plugin
- Post-production crowd mic settings documented in `LDB_FabFilter_ProQ4_Settings.pdf`

---

*End of CLAUDE.md. Last updated: 2026-07-01 (EQ tables + show-doc format moved to the KB — KB is canonical).*
