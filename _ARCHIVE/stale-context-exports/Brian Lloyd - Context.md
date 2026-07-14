---
tags:
  - context
  - about-me
  - profile
aliases:
  - About Brian
  - Who I Am
  - Context
created: 2026-06-26
updated: 2026-06-26
---

# Brian Lloyd — Full Context

> **⚠ Stale-snapshot warning (added 2026-07-06).** This is a portable export from 2026-06-26. Its Q225 EQ band convention ("HPF → L Shelf → Band 1 → … → LPF") and the embedded EQ starting-point tables are the RETIRED pre-2026-05-30 format. The locked convention is **Band 1 = LF … Band 4 = HF, doc order HPF → LPF → B4 → B3 → B2 → B1**, and the canonical EQ tables live in `audio/Live Sound KB/Wiki/eq-starting-points.md`. Don't build paperwork from this file.

This document is the primary context file for any AI system working with Brian Lloyd. Read this before anything else. It covers identity, venues, consoles, mic library, EQ philosophy, active projects, and infrastructure.

---

## Identity

**Brian Lloyd** — Live sound and recording engineer, events and production professional. Cincinnati, Ohio. 20+ years in the industry.

**Email:** tinydoorstudios@gmail.com · Blloyd@3cdc.org  
**Phone:** (315) 404-5648  
**Side operation:** Tiny Door Studios

### Primary Roles

**Sound Engineer — Jazz At The Memo**  
Memorial Hall, Cincinnati. House console: DiGiCo Quantum 225. Regular jazz and classical programming, multitrack recording every show.

**Events/Production Team — 3CDC**  
Cincinnati Center City Development Corp. AV coverage across Fountain Square, Washington Park, Elm Street Plaza, Court Street Plaza, Zeigler Park, and Imagination Alley.

---

## How to Work With Brian

- Direct and concise. No fluff, no preamble.
- Don't narrate work in progress — execute, then report when done.
- If you can do something yourself, do it. Only stop for genuinely consequential or irreversible decisions.
- Ask questions when needed, but don't narrate the context around them.
- Prose over bullet points for conversation. Tables are fine for technical data.
- Whole dB values only in EQ — never half-dB.
- Default all deliverables to PDF unless otherwise specified.
- Make reasonable assumptions and keep moving. If something is genuinely uncertain, say so — never make up settings or specs.
- Talk at a high level. Brian has 20+ years of experience — don't over-explain basics.

---

## DAWs & OS

- **OS:** macOS (assume Mac unless stated otherwise)
- **Primary DAWs:** Studio One 7, WaveLab 12
- **Capture DAW:** REAPER — multitrack capture on location

---

## Consoles

### DiGiCo Quantum 225

House console at Jazz At The Memo (Memorial Hall) and Fountain Square.

- 4-band parametric EQ + HPF/LPF (Mustard Processing)
- **EQ band order:** HPF (LC) → L Shelf → Band 1 → Band 2 → Band 3 → Band 4 → LPF (HC)
- Gain ±18dB, Q 0.3–10, LC slopes 6/12/18/24 dB/oct
- L and H bands switchable Bell/Shelf (default Shelf)
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG
- Mustard processing colors: Blue = Neve · Red = API · Purple = Optical/LA-2A · Green = FET/1176
- Input thresholds: −25 to −20 dBFS
- Polarity invert per channel, VCA grouping, Mustard compression
- Spice Rack: use Chilli 6 (multiband comp) and Naga 6 (dynamic EQ) only

### Behringer Wing

Secondary console, other venues and tribute work.

- 6-band parametric: L, 1, 2, 3, 4, H — L and H switchable Bell/Shelf
- Aux/Bus EQ: 4 bands
- LC slopes 6/12/18/24 dB/oct · HC slopes 6/12 dB/oct
- Filter slot also has Tilt EQ / Sonic Maximizer / All-Pass
- USB audio outputs are pre-everything by default
- **Known issue:** FX preset save/load broken since firmware v1.13 — `.efx` files incompatible with Wing

### Other Consoles in Rotation

- Yamaha CL3
- Midas M32

---

## Venues

### Memorial Hall ("Memo") — Cincinnati, OH

- 556 seats. Stage: 37'4" W × 22'3" D. Hardwood floor, Beaux Arts, built 1908.
- Working RT60: ~1.6s (with any audience present — 2.2s was pre-renovation empty estimate)
- Piano storage stage right
- **Problem zones:** 63Hz, 125Hz, 200Hz, 250–315Hz standing waves; 200–400Hz mud buildup — always treat in EQ, especially crowd/ambient mics
- House console: DiGiCo Quantum 225

**Crowd mic rig** (always patch for Memo shows — leave CH numbers blank):

| Pair | Placement | Type |
|---|---|---|
| Line Audio OM1 | Flown 18' above stage, 12' apart | Omni pressure balls |
| Deity S2 | Under main-floor PA, aimed into audience | Short shotgun pair |
| Line Audio CM4 | Balcony, rear-facing into room, 34' from Deity pair | ORTF cardioid pair |

### Greaves Concert Hall — NKU, Highland Heights, KY

- 637 seats, hardwood floor, permanent shell, adjustable acoustic panels
- Two 9ft grands: Steinway and Baldwin
- RT60: ~1.5–1.9s. Acoustically tuned for orchestral/chamber/vocal

### 3CDC Venues

| Venue | Tempest ID | Notes |
|---|---|---|
| Fountain Square | #215217 | DiGiCo Q225 FOH, Midas M32 monitors |
| Washington Park | — | Midas M32 |
| Elm Street Plaza | #211956 | — |
| Court Street Plaza | — | — |
| Zeigler Park | #216868 | — |
| Imagination Alley | — | — |

---

## Mic Shorthand Library

| Shorthand | Full Name | Type | Primary Use |
|---|---|---|---|
| DM6 | Earthworks DM6 SeisMic | Dynamic | Kick drum |
| DM17 | Earthworks DM17 | Dynamic | Snare top, toms |
| SR20 | Earthworks SR20 Gen 2 | Pencil SDC | Hat, OH, room |
| MKH40 | Sennheiser MKH40 | RF cardioid | Flute, pipes, classical detail |
| U87 | Neumann U87 | LDC | Crowd mic, room |
| U87 Jr | Warm Audio WA-87 | LDC clone | Trombone (primary use) |
| Beta 58A | Shure Beta 58A | Supercardioid dynamic | Vocals |
| Beta 98H/C | Shure Beta 98H/C | Clip-on condenser | Horns |
| MD421 | Sennheiser MD421 | Dynamic | Brass alternative |
| RNDI | Rupert Neve Designs RNDI | Active transformer DI | Bass, guitar, keys |
| J48 | Radial J48 | Active DI | Bass DI |
| DPA 4099 | DPA 4099 CORE+ | Clip-on supercardioid | Piano, strings, brass |
| B3 | Countryman B3 | Omni lavalier | Strings (clip-on) |
| B3–B10 | Countryman B3 (physical mic numbers) | Omni lavalier | String section — ALL B3s |
| R88 | AEA R88 | Stereo ribbon | Classical recording |
| MK4 | Schoeps CMC6 + MK4 | SDC cardioid | Classical spot |
| MK5 | Schoeps CMC6 + MK5 | SDC switchable | Classical main pair |
| MK41 | Schoeps CMC6 + MK41 | SDC supercardioid | Classical spot |
| C422 | AKG C422 | Vintage stereo LDC | XY mode for horns — 2 ch on patch |
| sE 8 | sE Electronics sE8 | SDC pair | Aux perc, OH |

**Notes:**  
B3–B10 labeling means physical mic numbers for individual string players. All are Countryman B3s.  
C422 is a single body, two capsules. XY mode = 2 console channels.  
**⚠ NO 48V on any ribbon mic (R88, Royer R-121) under any circumstances — destroys ribbon.**

---

## Stand Vocabulary

Short / Tall / Boom / Bar / Clip / DI / — (wireless/dash)

---

## EQ Philosophy

- **All genres except classical: aggressive by default.**
- Cuts: −4 to −7dB, tight Q (1.5–2.0). Boosts: +3 to +6dB.
- Whole dB values only. Never half-dB.
- No high shelf band unless specifically requested.
- Subtractive first — find and cut problems before boosting.
- Band order: HPF → L Shelf → Band 1 → Band 2 → Band 3 → Band 4 → LPF

| Genre | Approach |
|---|---|
| Classical | Minimal. Spots blend. Nothing aggressive. |
| Acoustic / Folk | Conservative. Piezo quack at 1.5–2kHz is the primary target. |
| Celtic | 5ms+ gate attack. Never gate sustained notes. |
| All other genres | Aggressive by default. |

---

## EQ Starting Points

### Drums (Aggressive)

| Source | HPF | L Shelf | Band 1 | Band 2 | Band 3 | Band 4 | LPF |
|---|---|---|---|---|---|---|---|
| Kick (DM6) | 40Hz | — | +4dB@80Hz Q1.2 | −6dB@250Hz Q1.8 | −4dB@600Hz Q2.0 | +4dB@3kHz Q1.2 | — |
| Snare Top | 120Hz | — | +3dB@180Hz Q1.2 | −6dB@300Hz Q2.0 | +5dB@1kHz Q1.0 | +4dB@7kHz Q0.8 | — |
| Snare Bottom | 200Hz | — | −6dB@600Hz Q2.0 | +5dB@1.8kHz Q1.2 | +5dB@7kHz Q0.8 | — | — |
| Hi-Hat | 500Hz | — | −5dB@800Hz Q1.5 | −4dB@2kHz Q1.2 | — | — | 16kHz |
| Rack Tom (DM17) | 80Hz | — | +4dB@120Hz Q1.2 | −6dB@400Hz Q1.8 | +4dB@2.5kHz Q1.0 | — | — |
| Floor Tom (DM17) | 60Hz | +5dB@80Hz Shelf | −6dB@450Hz Q1.8 | +4dB@2kHz Q1.0 | — | — | — |
| OH L/R (SR20) | 180Hz | — | −4dB@300Hz Q1.5 | +4dB@5kHz Q0.8 | — | — | — |

### Bass (Aggressive)

| Source | HPF | L Shelf | Band 1 | Band 2 | Band 3 | LPF |
|---|---|---|---|---|---|---|
| Bass DI (J48) | 40Hz | +4dB@80Hz Shelf | −5dB@250Hz Q2.0 | +4dB@600Hz Q1.0 | −4dB@1.5kHz Q1.5 | — |
| Bass Cab (DM6) | 60Hz | +4dB@100Hz Shelf | −6dB@400Hz Q2.0 | +4dB@900Hz Q1.0 | — | 5kHz |

### Guitar (Aggressive)

| Source | HPF | Band 1 | Band 2 | Band 3 | Band 4 |
|---|---|---|---|---|---|
| Elec Gtr (SM57) | 100Hz | −4dB@200Hz Q2.0 | −5dB@450Hz Q2.0 | +4dB@800Hz Q1.2 | +4dB@2.5kHz Q1.0 |
| Royer R-121 | — | +3dB@150Hz Q1.0 | −4dB@350Hz Q2.0 | — | — |
| Acoustic (RNDI) | 100Hz | −5dB@400Hz Q2.0 | −5dB@2kHz Q1.8 | +4dB@200Hz Shelf | +4dB@5kHz |

### Keys

| Source | HPF | Band 1 | Band 2 | Band 3 |
|---|---|---|---|---|
| Keys DI (RNDI) | 60Hz | −4dB@200Hz Q1.5 | +3dB@300Hz Q0.8 | +4dB@2.5kHz Q0.8 |

### Horns / Winds (Aggressive)

| Source | HPF | Band 1 | Band 2 | Band 3 | LPF |
|---|---|---|---|---|---|
| Trumpet | 80Hz | −4dB@300Hz Q2.0 | −4dB@1kHz Q1.8 | +4dB@5kHz Q1.0 | 12kHz |
| Trombone | 60Hz | −4dB@400Hz Q2.0 | −4dB@1.5kHz Q1.8 | +3dB@100Hz Shelf | 10kHz |
| Flute (MKH40) | 200Hz | −4dB@400Hz DEQ | +5dB@4kHz | — | — |
| Sax | 80Hz | −4dB@300Hz Q2.0 | −4dB@800Hz Q1.8 | +4dB@5kHz Q1.0 | 10kHz |

### Vocals

| Source | HPF | Band 1 | Band 2 |
|---|---|---|---|
| Lead/BG wireless | 130Hz | −7dB@230–240Hz Q2.0 | +5dB@3.5kHz Q1.0 |
| Bass player vocal | 130Hz | −7dB@400Hz Q2.0 | +6dB@3.5kHz Q1.0 |
| Drummer vocal | 140Hz | −7dB@350Hz Q2.0 | +6dB@3.5kHz Q1.0 |
| SM58 male (live) | 100Hz | −5dB@200Hz Q2.0 | −4dB@300Hz Q1.8 |
| Beta 58A male (live) | 120Hz | −4dB@230Hz Q2.0 | −3dB@650Hz Q1.8 |

### Piano — DPA 4099 Stereo (Conservative)

| String Range | HPF | L Shelf | Band 1 | Band 2 | Band 3 | LPF |
|---|---|---|---|---|---|---|
| Low strings | 60Hz 18dB/oct | +2dB@100Hz Shelf | −3dB@300Hz Q1.5 | −2dB@800Hz Q1.2 | +2dB@3kHz | 8kHz |
| High strings | 150Hz | — | −2dB@400Hz | +2dB@5kHz | +2dB@10kHz | — |

Do not touch the 10–12kHz DPA high-end boost. Check phase between pair first.

### Memorial Hall Crowd Mics — Live FOH EQ

| Pair | HPF | Band 1 | Band 2 | Band 3 | Band 4 | LPF |
|---|---|---|---|---|---|---|
| OM1 Flown Omni | 80Hz | −5dB@200Hz Q2.0 | −6dB@315Hz Q2.0 | −3dB@800Hz Q1.5 | — | — |
| Deity S2 Under PA | 100Hz | −5dB@200Hz Q2.0 | −5dB@315Hz Q2.0 | −3dB@2.4kHz Q1.8 | — | 16kHz |
| CM4 Balcony ORTF | 120Hz | −5dB@63Hz Q2.5 | −6dB@200Hz Q2.0 | −5dB@315Hz Q2.0 | −4dB@400Hz Q1.5 | 14kHz |

---

## Royer AxeMount — SM57 + R-121 Blend Guide

Used at Memorial Hall on SR guitar (CH13 SM57, CH15 R-121).

SM57 is primary. Set to target guitar level first. R-121 is blend — bring up from zero until the brittleness of the 57 softens. Typical blend: R-121 sits 6–10dB below SM57. GD/Allmans-style warm tones may close to 3–5dB.

**Polarity check:** Sum both in mono — should be fuller than either alone. If thinner, flip polarity on R-121.

**⚠ NO 48V on R-121 under any circumstances.**

Group both to the same VCA for combined level riding. Post-blend: check 300–500Hz buildup, notch −2 to −3dB on bus EQ if needed.

---

## Celtic Music Engineering

Celtic music lives in ornamentation — cuts, rolls, triplets, grace notes that exist entirely in the transient attack of each note. Any processing that compresses, smears, or delays transients destroys the music.

- Compressor attack: 5ms minimum on all melodic instruments — never faster
- Never gate sustained instruments: fiddle, bouzouki, uilleann pipes, accordion
- Bodhran / frame drums: 200Hz Dynamic EQ is the most aggressive move — Memo's modes make this the highest-risk channel
- Uilleann pipes: continuous drone tones — DEQ must use extended release (100–120ms)
- Pickup/DI acoustic instruments suffer thinness — compensate with Lo Bell warmth at 150–200Hz + Mustard Blue (Neve) saturation

---

## Show Document Format

**Sections in order:**
1. Cover page
2. Input List
3. Patching page (sorted by port: AES then Local)
4. Cross-Patch page (sorted by stage box location)
5. EQ channel pages
6. Reference page
7. Stage Plot (5-zone grid, scaled to fit one landscape page — no cropping)

**EQ table column order (fixed):**  
`CH | Instrument | HPF | L Shelf | Band 1 | Band 2 | Band 3 | Band 4 | LPF | Notes`

**Patching conventions:**
- Local inputs: always "Local 1, Local 2…" — never L1/L7
- AES inputs: AES-1, AES-7, etc.
- TOUR flag: any artist-provided mic flagged ⚑ TOUR with amber highlight. Always note to confirm at load-in.
- Ribbon mic warning: always flag NO 48V in red on any ribbon mic channel.

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

---

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

## Plugins & Processing

| Plugin | Notes |
|---|---|
| Waves F6 | 6-band floating dynamic EQ + HPF/LPF, per-band Static/Dynamic/Expand, Mid/Side, sidechain, RTA |
| Waves CLA Epic | 4 delays (Slap/Throw/Tape/Crowd) + 4 reverbs (Plate/Room/Hall/Space), serial or parallel |
| Waves CLA 1176 | No fixed unity gain — match by ear/meter |
| Waves Seventh Heaven Pro | Bricasti M7 emulation — primary reverb for classical/acoustic work |
| FabFilter Pro-Q 4 | `.ffp` format is proprietary binary — cannot be generated externally. Dial in manually, save from the plugin. |

---

## Active Projects

### Live Dead and Brothers (LDB)

GD/Allman Brothers tribute, Memorial Hall.

- Files built: `LDB_Show_Document.docx` (patch + monitors + EQ + stage plot), `LDB_FabFilter_ProQ4_Settings.pdf`
- 21 input channels + 6 crowd mics
- Royer AxeMount on SR guitar: CH13 SM57, CH15 R-121
- All TOUR wireless vocals — confirm RF coordination at load-in
- IEM: Hardwire Mix 7 on drums · MIX 1–5 stage wedges

### FSQ Salsa (Weekly Repeating — Fountain Square)

- Conversion sheet built: `FSQ_Salsa_Patch_2026.pdf`
- 32-channel show: standard snake labels → Salsa-specific inputs
- CH 25–28: Dante 49–52 for wireless vocals
- CH 13–16: Guitar inputs repurposed as Keys 1–4
- CH 17–21: Misc inputs repurposed as Timbales/Quinto/Tumba/Bongo

### Simon & Garfunkel Tribute

- Console: Behringer Wing
- Piano: 9ft Steinway, short stick lid
- Mics: DPA 4099 stereo pair (piano mount clips, magnet mounts on frame)
- EQ: Conservative cuts-only
- No show document built yet

### ShowBuilder — Show Paperwork + .ses Dashboard

Guided web app at `Code/ShowBuilder/` (Python/aiohttp, `./run.sh` → http://localhost:8095).

Front-ends the existing Q225 pipeline. Wizard: Show → Channels → Review → Build. Exports a `<Show>.brief.json` (no EQ); the show-deep-build skill handles EQ/paperwork/.ses. Memo + FSQ get the full .ses pipeline; other venues get paperwork only.

---

## Infrastructure

### Home Lab

| System | Details |
|---|---|
| TDS — Proxmox host | Dell 14G PowerEdge. Proxmox 9.2.3, hostname `pve`. LAN 192.168.0.4, web UI :8006. SSH `ssh tds` (key `~/.ssh/proxmox_tds`). Tailscale machine `tds` = 100.99.198.22. |
| n8n VM (on TDS) | VMID 100, Debian 12, 192.168.200.84. Reach via `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84`. Docker Compose at `/opt/n8n` (n8n + Postgres 16). Needs sudo for compose. |
| Audio NAS (TrueNAS) | 192.168.200.36 |
| Cold Storage (TrueNAS) | 192.168.200.35 · Tailscale 100.126.177.120 |

### n8n Automation Workflows

- Lightning Strike Alert — dual Tempest redundancy, tiered Slack alerts, auto-clear
- Wind Gust Alert — three MPH threshold tiers, 15-min rate limiting
- Rain Forecast Alert — Open-Meteo polling
- Show Reports — Google Sheets trigger → HTML email with conditional Drive photo attachments

**Known issue:** Wind Alert Slack messages still have TEST TEST TEST prefix — unresolved.

### SPL Monitor

Live at https://spl.tinydoorstudios.com. Systemd service `spl-monitor` on the n8n VM at `/opt/spl-monitor`. Source of truth on Mac: `/Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/`.

SMAART data source: `192.24.143.121:26000` (only up during shows). To test with simulated data, set `SPL_SOURCE=simulator` in `/etc/spl-monitor.env`, restart, then restore.

### Tempest Weather Stations

| Venue | Station ID |
|---|---|
| Fountain Square | 215217 |
| Elm Street Plaza | 211956 |
| Zeigler Park | 216868 |

### Cloudflare Tunnel

The `n8n-tunnel` is dashboard/API-managed (`config_src: cloudflare`). Local config files on the VM are ignored — change ingress only via the Cloudflare API. cloudflared runs on the n8n VM alongside a landing nginx (:8088). Wiki.js runs on CT 101 at `192.168.200.126:3000`.

### Maestro DMX / Companion Control

- Maestro DMX: `maestro.local/#/show` (Chrome bookmark "DMX")
- Companion: Generic OSC module, UDP port 7672
- Key OSC paths: `/global/brightness`, `/show/index`, `/show/cue/index`, `/show/stop`, `/show/play_pause`, `/show/cue/next`, `/show/cue/previous`

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

## Document & PDF Standards

- All PDFs use ReportLab in Python
- Default delivery: PDF
- SOP tone: collegial and direct — not customer-service or policy-manual style
- Content visibility check required before delivery — verify no cell/text clipping

---

## Writing Rules (Summary)

Write like a sharp human, not a chatbot. No AI tells.

Never use: "delve," "it's worth noting," "furthermore," "comprehensive," "leverage," "utilize," "in conclusion," "based on the above."

No default bullet lists — if it fits in a sentence, write a sentence. Don't write in threes. Don't summarize what you just said. Warm but direct. Specific over general. Contractions fine. No preamble.

---

*Last updated: 2026-06-26*
