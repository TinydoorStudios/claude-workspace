# Input List / Patch Sheet — Design Spec

A reusable spec for building clean, FOH-readable channel lists in Excel. Drop this file into a Claude.ai Project as a knowledge file, or paste the "Project Instructions" block at the bottom into the project's custom instructions.

---

## Design Principles

1. **Title block, not a buried label.** Show name spans the top in a dark bar. A second sub-bar holds Venue, Date, Rev, FOH engineer, MON engineer, Show Time.
2. **Group by function, color the group.** Channels are grouped into sections (Drums, Rhythm, Piano, Strings, Horns/Winds, Vocals, Ambient/FOH). Each section gets a distinct pastel color used for its header row and as the alternating band color inside that section.
3. **One row per channel, no blanks.** Empty channels are labeled `SPARE`, never left blank.
4. **Freeze the header row.** Column headers stay visible on scroll.
5. **Gridlines off.** Use borders only on the outside of each section block.
6. **Tabular columns are monospaced.** Ch and Split Patch use Consolas so AES-1 / AES-10 / AES-20 line up.
7. **Controlled vocabularies.** Stand and 48V columns use a fixed set of values, not free text.
8. **Stage layout lives on its own tab,** not crammed into a column on the input list.
9. **Print-ready.** Fit-to-width, repeated header rows, narrow margins.

---

## Layout

| Region | Rows | Notes |
|---|---|---|
| Title bar | 1 | Show name, merged A:G, dark slate, 20pt bold white, centered |
| Sub-bar | 2–3 | Venue / Date / Rev on row 2; FOH / MON / Show Time on row 3 |
| Spacer | 4 | blank |
| Column headers | 5 | Bold white on near-black, centered, frozen below |
| Data | 6+ | Section header rows interleaved with channel rows |

**Columns (left to right):** Ch · Instrument · Mic / DI · Split Patch · 48V · Stand · Notes
**Widths:** 6 · 22 · 26 · 12 · 6 · 10 · 32

---

## Color Palette

Hex codes are AARRGGBB-friendly (drop the alpha). Header color is the saturated band, "band" is the lighter alternating row inside the section.

| Section | Header | Alt-row band |
|---|---|---|
| Title bar | `#1F2937` (slate-800) | — |
| Sub-bar | `#374151` (slate-700) | — |
| Column headers | `#111827` | — |
| DRUMS / PERC | `#FDE68A` | `#FEF3C7` |
| RHYTHM | `#BBF7D0` | `#DCFCE7` |
| PIANO | `#FBCFE8` | `#FCE7F3` |
| STRINGS | `#BFDBFE` | `#DBEAFE` |
| HORNS / WINDS | `#FCD9B4` | `#FFEDD5` |
| VOCALS | `#DDD6FE` | `#EDE9FE` |
| AMBIENT / FOH | `#C7D2FE` | `#E0E7FF` |

Borders: thin `#9CA3AF` inside, medium `#111827` on the outside of each section block.

---

## Typography

- Body: Calibri 10
- Title: Calibri 20 bold white
- Sub-bar: Calibri 10 bold white
- Column headers: Calibri 11 bold white, centered
- Section headers: Calibri 11 bold black, left-aligned with indent
- Ch and Split Patch columns: Consolas 10, centered (monospaced for alignment)
- 48V check: Calibri 11 bold, color `#065F46` (emerald-800), centered

---

## Controlled Vocabularies

**48V column:** `✓` for phantom on, blank for off. Never "x" / "X" / "yes".

**Stand column:** one of
- `Short` — kick / floor instruments
- `Tall` — overheads, vocals
- `Boom` — anything off-axis
- `Bar` — Decca / FOH ambient
- `Clip` — DPA, Countryman, snare clip
- `DI` — direct, no stand
- `—` — wireless / handheld

**Mic naming:** Manufacturer + model, no abbreviations. `Shure SM58`, not `58`. If unknown, write `(CONFIRM)` and add `MIC TBD` in Notes.

**Patch naming:** zero-padded or consistent (`AES-1`, `AES-10`, `L1`, `L7`).

---

## Section Order (default)

1. DRUMS / PERC (1–5)
2. RHYTHM (bass, guitars, keys)
3. PIANO
4. STRINGS (violins, then celli)
5. HORNS / WINDS
6. VOCALS (kit vocal first, then wireless leads, then handheld)
7. SPARES (labeled, not blank)
8. AMBIENT / FOH (Decca, crowd, FOH mics)

---

## Stage Plot Tab

A second sheet titled `Stage Plot` with the same title bar styling. Five zones, each a dark bar followed by 2–3 columns of merged item cells:

- DOWNSTAGE (Audience)
- MIDSTAGE LEFT
- MIDSTAGE RIGHT
- UPSTAGE
- FOH / AMBIENT

Items are placed in a 3-column grid under each zone header. Light gray fill `#F3F4F6` on populated cells, white on empty.

---

## Print Setup

- Orientation: Portrait
- Fit to width: 1 page
- Fit to height: unlimited
- Margins: 0.4" sides, 0.5" top/bottom
- Horizontally centered
- Repeat rows 1–5 on every printed page
- Gridlines: off

---

## Project Instructions (paste into a Claude.ai Project)

> When I share an input list, patch sheet, or stage plot for a live show, redesign it using my Input List Design Spec. Apply all of it: title block with show/venue/date/rev/FOH/MON/showtime, frozen column header, color-coded sections (Drums, Rhythm, Piano, Strings, Horns/Winds, Vocals, Ambient/FOH) with alternating bands inside each section, section header rows, monospaced Ch and Split Patch columns, ✓ for 48V, controlled Stand vocabulary (Short / Tall / Boom / Bar / Clip / DI / —), full mic names (never abbreviations like "58"), `SPARE` for empty channels, gridlines off, section-block borders, separate Stage Plot tab with zone grid, and print setup (portrait, fit-to-width, repeat header rows). Flag any missing or ambiguous mic choices with `(CONFIRM)` and `MIC TBD` in Notes — don't guess silently. Stop and ask before deleting channels or changing patch assignments.
