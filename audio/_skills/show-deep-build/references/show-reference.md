# Show Reference — mic shorthand, packet format, palette, blends, plugins

Moved out of the always-loaded project `CLAUDE.md` on 2026-09-14: this only matters inside a show build, an EQ question, a packet render, or a patch sheet. Loads with show-deep-build; send-it, new-show, show-wiki-push and the packet/patch-sheet builders read it here. Standing rules stay in `audio/_system/RULES.md`; this file is reference data, not rules.

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
| 408 / ND408 | Electro-Voice N/D 408 — vintage first-gen (no letter suffix), supercardioid N/DYM. **Any bare "408" I write, on any source including a snare, is THIS mic** (corrected 2026-08-08 — the old rule said a "408" on a snare meant the Lauten; wrong) | Dynamic | Rack toms (small-footprint 421 alternative), guitar cab, snare |
| the Lauten / "snare mic" | Lauten LS-408 — I never call it "408". It's "the Lauten" or just "snare mic" (2026-08-08) | FET LDC, snare-voiced | Snare top. Needs 48V; onboard HPF 80/140, LPF 5/12k — always ask the switch positions |
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
- Body: Calibri (locked 2026-09-11 — default for any document created, not just show packets)
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
