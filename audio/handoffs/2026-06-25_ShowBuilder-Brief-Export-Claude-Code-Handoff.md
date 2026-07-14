# ShowBuilder → Brief Export — Claude Code Handoff

*2026-06-25 · for Claude Code working on the ShowBuilder Mac app · author: Brian + Cowork*

## TL;DR

Stop having the app compute EQ. Make ShowBuilder a **data-capture** tool that exports a
**facts-only `<Show>.brief.json`**. All EQ, paperwork, and the `.ses` are produced downstream by
the `show-deep-build` skill, which does real artist + per-source research. The app's job shrinks to:
capture the input list + metadata cleanly, and **round-trip free-text notes verbatim** — because
those notes are the deep build's research hooks.

## Why this change

The app was generating EQ instantly from KB/template defaults. That produced generic — sometimes
wrong — values (a kick channel once carried notes about a "D6/Beta 91A blend" on a show with no D6;
a template bled in). EQ done right needs the artist researched, every source researched mic ×
instrument × genre × venue against the live-sound forums and the KB, with the *why* recorded. That
work lives in the `show-deep-build` skill now, not the app. The app should hand the skill clean
facts and get out of the EQ business.

## New architecture (boundary)

```
ShowBuilder app            show-deep-build skill (Cowork/Claude Code)
---------------            ------------------------------------------
capture input list   -->   read <Show>.brief.json
+ metadata                 research artist + genre (web)
+ free-text notes          research each source (mic×instr×genre×venue) via eq-advisor
                           MINE the notes -> research amps / miking techniques / etc.
export brief.json    -->   write <Show>.spec.json (adds EQ, mic_notes, eq_summary, changes)
                           build_packet.py  -> .md, .xlsx, Show Packet PDF, EQ Rationale PDF
                           venue patcher    -> <Show>.ses
                           (console verify, then wiki-publish)
```

The app **never** writes EQ. The skill **never** re-keys the input list.

## What to BUILD / CHANGE in the app

1. **Remove EQ generation.** Drop the EQ engine output path: no `hpf`/`lpf`/`bands`, no
   `mic_notes`/`eq_summary`, no `comp`/`gate` values, and **stop emitting the FOH Channel Processing
   `.md`** (the skill writes that now, in the patcher's exact format). If the current app writes a
   `spec.json` with EQ, replace it with the brief below.
2. **Add "Export Brief"** → writes `<Show>.brief.json` (schema below) into the show folder
   `<Venue>/YYYY-MM-DD ShowName/` (keep the existing folder/naming convention exactly).
3. **Free-text notes are first-class.** Keep a per-channel `notes` field and add a show-level
   `show_notes` field. **Do not validate, truncate, normalize, or strip them.** Round-trip exactly
   what Brian types — including gear names, miking techniques, and shorthand. These strings are the
   research signals the skill mines (see "Notes are research hooks").
4. **Keep the input vocabulary** already in the app: full mic names (no shorthand), `Local N` patch
   labels (never `L1`), stand vocabulary (Short/Tall/Boom/Bar/Clip/DI/—), ribbon flag, 48V.

## Notes are research hooks (important)

The free-text `notes` / `show_notes` exist so Brian can drop in anything that should "factor into
the grand scheme," and the skill will detect it and **search it**. Examples the skill is built to
catch and research:

- **Amplifiers / cabs** — "Ampeg SVT + 8x10", "Vox AC30 top boost", "Fender Twin", "Helix direct".
- **Miking techniques** — "Fredman", "mid-side", "XY", "ORTF", "spaced pair", "57+121 blend",
  "close + room".
- **Instrument specifics** — "flatwounds", "5-string low B", drum sizes/heads, open tunings.
- **Artist / stage** — tonal requests, "no gate", broadcast feed, RF/TOUR gear, PA, weather.

So the app must not "clean up" notes. A note like `Vox AC30 top boost, 57+Beta 27 blend` must arrive
at the skill byte-for-byte. (App side does **not** need to understand or research these — just
preserve them. The research is the skill's job.)

## `<Show>.brief.json` schema (the contract)

```jsonc
{
  "show_name": "Izzy Escobar",
  "artist": "Izzy Escobar",
  "venue": "fsq",
  "venue_label": "Fountain Square (outdoor)",
  "console_label": "DiGiCo Quantum 225",   // drives the packet/patcher path downstream
  "show_date": "2026-06-26",
  "foh_engineer": "Brian Lloyd",
  "mon_engineer": "Sam Carpender",
  "show_time": "9:00pm",
  "rev": "Rev 1.0",

  "show_notes": "Outdoor, possible wind. Intimate vocal, minimal verb. 75-min set.",  // free text, mined

  "channels": [
    {
      "ch": 13,
      "name": "Guitar 57",          // fader label
      "instrument": "Electric Gtr",
      "mic": "Shure SM57",          // full name, no shorthand
      "section": "GUITAR",          // DRUMS/BASS/RHYTHM/GUITAR/KEYS/PIANO/STRINGS/HORNS/VOCALS/AMBIENT
      "phantom": false,
      "ribbon": false,              // true -> downstream flags NO 48V red
      "stand": "DI",                // Short/Tall/Boom/Bar/Clip/DI/—
      "patch": "Local 13",          // optional; defaults to "Local <ch>"
      "notes": "Vox AC30 top boost, 57 + Beta 27 blend, edge-of-breakup"  // free text, mined verbatim
    }
  ]
}
```

Hard rules: **no EQ fields**; `notes`/`show_notes` are unconstrained text, preserved verbatim;
omit a channel entirely if it's a true spare (don't emit blank EQ).

## Execution — how the brief, skill, and patcher run together

1. **App:** Export Brief → `<Venue>/YYYY-MM-DD ShowName/<Show>.brief.json`.
2. **Cowork:** Brian opens a session and says e.g. *"deep build the Izzy show"* (or points at the
   brief). The `show-deep-build` skill triggers and:
   - researches the artist + genre, then each source (visibly — searches actually run), **mining the
     notes** and researching any amp/technique/etc. it finds;
   - writes `<Show>.spec.json` (deep-research schema: adds `bands`, `mic_notes`, `eq_summary`,
     `artist_profile`, `research_summary`, `room_context`, `changes`);
   - runs the engine:
     ```
     python3 ~/Documents/Claude/audio/_skills/show-deep-build/scripts/build_packet.py \
       --spec "<show folder>/<Show>.spec.json" \
       --out  "<show folder>"
     ```
     → `<Show> - FOH Channel Processing.md`, `<Show> - Input List.xlsx`,
       `<Show> - Show Packet.pdf`, `<Show> - FOH EQ Reasoning.pdf`.
   - builds the `.ses` with the venue patcher (FSQ shown):
     ```
     python3 "~/Documents/Claude/audio/Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py" \
       --src  "~/Documents/Claude/audio/Fountain Square/_TEMPLATE/brian fsq start.ses" \
       --dest "<show folder>/<Show>.ses" \
       --md   "<show folder>/<Show> - FOH Channel Processing.md"
     ```
     Require `bytes changed outside mic'd blocks: 0  PASS` and identical file size.
3. **Console hard stop:** Brian verifies on the Q225. Then `wiki-publish`.

## Acceptance test

Export a brief for the Izzy Escobar show (19 channels, FSQ, Q225) with a couple of notes containing
an amp and a miking technique. Confirm:
- the brief is facts-only (no EQ keys), notes preserved verbatim;
- the skill produces all five paperwork files + a `.ses` that passes the patcher;
- the EQ Rationale PDF's `changes` box reflects the amp/technique notes (proof the mining worked).

Reference build to diff against: `Fountain Square/Izzy 2.0 Deep Think/`.

## Don't break

- The `.ses` patcher and its calibration (see `Fountain Square/Q225 SES Patcher SOP/`). The app
  must not write `.ses` or the channel-processing `.md`.
- Folder/naming convention `<Venue>/YYYY-MM-DD ShowName/`.
- Input vocabulary (full mic names, `Local N`, stand words, ribbon/48V).
- Pipeline docs already updated: `_system/NEW-SHOW.md`, the FSQ SES Patcher SOP, `_system/IMPROVEMENTS.md`.
