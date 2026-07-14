# ShowBuilder

A guided web tool for **capturing a show's input list** — venue, channels,
instruments, mics, stands, 48V, and free-text notes — and exporting a facts-only
`<Show>.brief.json`.

ShowBuilder is a **data-capture tool only**. It does **not** compute EQ, write a
`.ses`, or write the FOH Channel Processing `.md`. All of that is produced
downstream by the `show-deep-build` skill, which reads the brief, researches the
artist and every source, and renders the EQ, the paperwork packet, and the `.ses`
(via the calibrated venue patcher). The app's whole job is to hand the skill clean
facts — and to round-trip the notes **verbatim**, because those notes are the deep
build's research hooks.

See `docs/HANDOFF.md` for the full boundary and the brief schema.

## Run (Mac)

```bash
cd ~/Documents/Claude/Code/ShowBuilder
./run.sh                 # serves http://localhost:8095
```

Walk the wizard: **Show → Channels → Export brief**. Every show starts at
**32 channels** (the crowd rig is appended on top of that, not counted). The
export writes `<Show>.brief.json` into the show folder
(`audio/<Venue>/YYYY-MM-DD ShowName/`); if the file already exists you're asked
before it's overwritten. Then, in Cowork, run the deep build against it:

> "deep build the Izzy show"

The `show-deep-build` skill produces the FOH Channel Processing `.md`, the Input
List xlsx, the Show Packet PDF, the EQ Rationale PDF, and the `.ses`. Console
verify, then `wiki-publish`.

## The brief (the contract)

Facts only — no EQ keys ever. Notes and `show_notes` are unconstrained free text,
preserved byte-for-byte. A true spare channel is omitted, not emitted blank.

```jsonc
{
  "show_name": "...", "artist": "...", "genre": "rock",
  "venue": "fsq", "venue_label": "...", "console_label": "DiGiCo Quantum 225",
  "show_date": "2026-06-26", "foh_engineer": "...", "mon_engineer": "...",
  "show_time": "...", "rev": "Rev 1.0",
  "show_notes": "free text, mined",
  "channels": [
    { "ch": 13, "name": "Guitar 57", "instrument": "Electric Gtr",
      "mic": "Shure SM57", "section": "GUITAR", "phantom": false, "ribbon": false,
      "stand": "DI", "patch": "Local 13",
      "notes": "Vox AC30 top boost, 57 + Beta 27 blend — mined verbatim" }
  ]
}
```

The app fills only no-EQ facts the engineer didn't type: `section` from the
instrument, `ribbon`/`phantom` from the mic library, the Memo crowd rig as
facts-only `AMBIENT` channels, and a default `patch` of `Local <ch>` (a Patch
column in the wizard takes explicit overrides like `Dante 49`).

## Wizard conveniences

- **Autosave** — everything typed is drafted to localStorage; a refresh or crash
  offers a Restore/Discard banner. The draft clears on a successful export.
- **Import brief…** (step 1) — load an existing `.brief.json` to clone or revise
  a show; crowd rows and implicit `Local <ch>` patches are stripped on the way in,
  and the table is padded back to the 32-channel baseline.
- **Guards** — switching venues or regenerating rows asks before wiping typed
  channels; the review flags duplicate/missing CH numbers.

## Architecture

```
backend/
  brief.py         Brief + BriefChannel — the facts-only export model
  app.py           aiohttp server: wizard + /api/bootstrap + /api/brief
  knowledge.py     loads knowledge/*.json (venues, mics, instruments, genres)
  mic_library.py   mic-name normalization helpers
  _deprecated/     FROZEN pre-2026-06-25 EQ/build pipeline (eq_engine, reverb_engine,
                   build, engine, spec, harvest, …) — kept for reference, not imported
knowledge/         venues / mics / instruments+genres / reverb_presets (reference data)
web/               vanilla-JS wizard (Show → Channels → Export brief)
```

**Package instance (n8n VM — live at https://showbuilder.tinydoorstudios.com):**
with `SHOWBUILDER_ROLE=package` and no `audio_root`, `/api/brief` returns the
brief as a download AND keeps a copy in `/opt/showbuilder/inbox/` — the wizard's
export step lists recent briefs so nothing is stranded on a phone. `GET /health`
is unauthenticated for uptime checks. Redeploy with
`deploy/deploy_showbuilder.command`.

## Venues

Memo and FSQ have the calibrated `.ses` pipeline downstream (in the skill). Other
venues are paperwork-only. The brief is venue-agnostic — it just carries facts and
the `console_label` that picks the downstream packet/patcher path.

## Verification

```bash
.venv/bin/python backend/selftest_brief.py   # exports a 19ch FSQ Izzy brief,
                                             # asserts no EQ keys + notes verbatim
```
