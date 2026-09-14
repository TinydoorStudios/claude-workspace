---
name: show-deep-build
description: >
  Brian's one skill for show EQ and show builds — the deep-research pipeline for a Q225
  (Memo/FSQ) or Wing show, and the standalone EQ brain (absorbed eq-advisor). THE DEFAULT FOR
  EVERY NEW SHOW: whenever Brian submits a new show in any form — a show to build, a
  channel/input list, an artist + venue, a rider, a brief — this skill runs; he need not say
  "deep think". Phrases like "build the show / packet", "deep think this one", "run the deep
  build", "process these channels" all mean this. ALSO use for any standalone EQ question:
  "what EQ for [mic] on [instrument]", "how do I EQ the [source]", "EQ starting point for…",
  "tame the [frequency]", reviewing a mix — runs Part II alone. Always researches artist +
  genre first, then each source in the locked order instrument → mic → genre → venue against
  live-sound forums cross-checked with the KB. Show builds produce the packet (FOH .md, .ses,
  Input List xlsx, Show/EQ/MASTER PDFs, phone patch sheet). Defaults to Q225/Wing; never
  CL3/M32 unless Brian names that desk.
---

# Show Deep Build

Two ways in: a **show build** (Part I, which calls Part II per unit) or a **standalone EQ
question** (Part II alone, inline answer + PDF). The hard rules are numbered in
`audio/_system/RULES.md` — **read it in full at the start of every run**; this file is the
procedure and cites rules by number instead of restating them.

## Before anything: the branch, the queue, the card

1. `git -C ~/Documents/Claude branch --show-current` must print `main` (R47). Otherwise stop.
2. Open `Live Sound KB/_learning/PENDING.md`. For each unchecked item, ask Brian ONE AT A TIME
   (AskUserQuestion, recommended option first): approve → write it into the named KB article now
   and tick it; skip → tick with "skipped <date>"; later → leave it. Staged KB edits go out with
   the next `wiki-publish`. Ten items max per run; say how many remain. (R44)
3. Write the **constraint card**: RULES.md in your own words, one line per rule that touches
   this show. Re-read it before the question round and before writing `spec.json`, and say so.
   (R40)
4. The **pacing rule** (R27): research lands visibly first; numbers come in a later message.
   Instant output is the tell that research was skipped.

# Part I — the show build

**Inputs.** Venue + console, and the input list (channels + mics/DIs). Ask for the tech rider
and stage plot; they are the densest research input. Only an artist name → ask for the list.
Never guess a mic from an instrument (R38). `brief.json` (`references/brief-schema.md`) is still
a valid machine input.

### 0. Intake
Read every artifact Brian dropped — rider PDF page by page, stage plot, xlsx/CSV, photos of a
handwritten list — and normalize to one set of facts: channels + mics, TOUR gear, monitor/IEM
asks, wireless counts, backline, tonal requests. File originals as `<Show> - Stage Plot.pdf` /
`<Show> - Rider.pdf` in the show folder. Two artifacts that disagree = a question, never a
silent winner.

### 1. Route + scaffold
First `python3 _shared/advance_bridge.py` — it pulls upcoming shows from the band advance
database, scaffolds any missing show folder, stamps the canonical `show_key`, drops the band's
stage plot / input-list uploads into the folder and writes a `<Show>.brief.json` skeleton whose
`show_notes` carries their monitor, backline and input answers. If the folder already exists,
start from what is in it. Then `_system/ROUTING.md` gives the venue row (folder, console, template, patcher, which KB
articles to pull — only those). Confirm date + name. Then
`python3 _system/scaffold_show.py --venue <v> --date YYYY-MM-DD --name "Show Name"`,
which creates the folder, the `.md` stub and `show.status.json` (R43). If a folder already
exists, read its status file: this may be a revision.

### 2. Genre gate, then artist
**2a.** Verify the genre with named evidence (the act's own material, listings, live footage, a
prior verified show) and write `Genre: X — <evidence>`. Split or hybrid evidence = ask Brian
right now (R20).
**2b.** Web-search the artist fresh (R21): who they are, real instrumentation, production style,
vocal character. Live video and setlists over press copy. Write a short `artist_profile`; it
refines and outranks the generic genre read. Check `active-projects.md` and the shows index for
a prior verified show of the same act or series — evidence beside the fresh pass, never instead.

### 3. Plan, mine, research
Dedupe channels into unique instrument × mic **units** and show Brian the plan table. Mine every
channel `notes` line and `show_notes` for research signals (amp/cab, miking technique, strings,
"no gate", broadcast) and research each; never drop a note (R28, table in
`references/deep-research-workflow.md`). Run **Part II per unit**, including the locker fork on
every mic'd input (R32). Then the **question round, one prompt at a time, locker forks first**
(R39): every fork, every stop-and-ask, every carried FLAG from a prior rev. Record each answer in
the spec's `decisions` list.

### 4. Room context
Part II Step 5 applies the venue per channel; at show level write one `room_context` line.
Outdoor venues: **fetch** the show-window weather (Open-Meteo; Tempest for current) and put the
numbers with source in `research.conditions` (R26). Note every divergence from the KB default in
`changes`.

### 5. Build from the spec
Write `<Show>.spec.json` per `references/spec-schema.md`: metadata, `artist_profile`, the
structured `research` object (one `units` row per unit with finding, external `sources`, one-word
`verdict`, five-layer `trace`; plus `reconciliation` and `kb_writeback`), `room_context`,
`changes`, `decisions`, optional `monitors`, required `reverbs` + `reverb_pairing` (R19), and
per-channel `bands` + `mic_notes` + `eq_summary` + `tour`/`ribbon`.

Re-read the constraint card, run `references/pre-commit-audit.md` with evidence quoted (channel
numbers and values, never "verified"), then:

```
python3 scripts/build_packet.py --spec "<show folder>/<Show>.spec.json" --out "<show folder>"
```

It validates (errors abort with nothing written), writes the `.md`, xlsx, Show Packet PDF, EQ
Rationale PDF and MASTER (quick-links page, bookmarks, band-provided plot/rider folded in),
lints the `.md`, and stamps `packet_built` with `rev` and hashes. **If the `.md` on disk was
edited since the last build it stops with a conflict table (R5)**: ask Brian per channel, one at
a time, write `{"<ch>": "md"|"spec"}` to a file and re-run with `--resolve <file>`.

Then the `.ses`, running the venue patcher **in place** (never copy it, R41):

```
python3 "<venue patcher>" --src "<venue _TEMPLATE>/<template>.ses" \
  --dest "<show folder>/<Show>.ses" --md "<show folder>/<Show> - FOH Channel Processing.md"
```

Require `bytes changed outside mic'd blocks: 0 PASS`, `do-not-write tags modified: 0 PASS`,
`readback: PASS`, name×20 on every fader, identical size. Then the phone sheet:
`python3 _shared/make_mobile_patch_sheet.py --spec "<show folder>/<Show>.spec.json"`.
Open one page of each PDF and check for clipping.

### 6. Hand over
List what was written and what Brian still dials by hand (HPF/LPF slopes, all dynamics — R18),
and any template baseline the build overrode (FSQ vocal faders ship a wireless curve). Console
verification is not a gate (R42). Publishing waits for his explicit go and is the
**show-wiki-push** skill (one command: `Live Sound KB/_tools/publish_show.py`), which also
appends this show's `kb_writeback` and `reconciliation` lines to PENDING.md and stamps
`published`.

### 7. Close out
Add the row to `active-projects.md` → Completed Shows (publish_show.py drafts it) and log the
show's decisions to `_learning/eq-advisor-log.md`. The harvest itself happens through PENDING.md
at the start of the next build; stamp `harvested` when that show's items are all decided.

# Part II — the EQ method

Order of importance and of process (R22): **instrument (+ notated equipment) → mic → genre →
venue.** Full detail and two worked examples: `references/decision-flow.md`.

**Step 1 — Instrument + equipment.** Exactly what is miked and how it is played; one mic, a
two-mic blend, or a section. Notated gear (amp/cab, drum sizes, strings, pickups) carries the
mic-grade research floor before it may bend a value; nothing notated → the generic instrument.

**Step 2 — Mic/DI.** Resolve shorthand against `mic-library.md` (R31). Not in the library →
research item AND a stop-and-ask. Flag before any math: ribbon → NO 48V red (R29); two-mic source
→ lane ownership (R16); switchable hardware (contour, pads, B3 caps) → state the assumed position
and the fallback in `mic_notes`.

**Step 2b — Locker fork (R32).** Exempt: DI, XLR line feed, TOUR, the Memo crowd rig; mic + DI
forks on the mic leg only. Load `mic-library.md` once per session. Specified mic is the locker's
first call → silent pass. Otherwise one owned, unassigned alternative with a concrete, nameable
win (less-EQ voicing · baked peak vs this genre/room · rejection margin · SPL · kit coherence ·
physical fit); ties go to the specified mic. Card, exactly three sentences:

```
LOCKER FORK — CH 4 · Snare top
  Specified:  Audix i5          Alt: Earthworks DM17 (DK-6)
  Why: <1 the win, with a number and its source>
       <2 what it changes for this show>
       <3 the honest cost>
  Call: keep i5  ·  swap to DM17
```

Accepted → re-enter Step 2 with the new mic and carry it through input list, patch, `changes`.
Declined → one line in `mic_notes` so it is not re-litigated next rev.

**Step 3 — Baseline: web first, KB second, reconcile (R23, R24).** Search the LAB (PSW) and
Gearspace Live Sound plus the maker's response curve (`references/forum-research.md`), fresh
every unit every show. Not researched until you can state one quantitative capsule fact with a
named external source. Cross-check `mic-library.md` and `eq-starting-points.md`. Write exactly one
word per unit — AGREE / DISAGREE / THIN — before any numbers; DISAGREE or THIN is a question with
three options (research / KB / research + update the KB). The capsule-voicing gate (R15) clears
every boost and every deep cut.

**Step 4 — Genre + artist.** Bend toward the genre (`references/genre-profiles.md`; the KB's
Genre Modifiers are the spine), then let the artist profile refine it (R13, R21). Sections are
slotted in the numbers with each lane named (R17).

**Step 5 — Venue.** The heaviest filter, applied last: Memo standing waves (R14), outdoor depth
(R12), classical restraint (R13). Then the global philosophy: cuts first, vocals cuts-only, whole
dB, no high shelf unasked (R8–R11).

**TRACE (R25).** Every unit closes with `base · equip · genre · artist · venue`, each a value or
"no change", as the `trace` object on its `research.units` row (one line inline for standalone).

**Standalone output.** Inline in the console's layout (Q225 `HPF · LPF · B4 → B1`; Wing/CL3/M32
in `references/console-bands.md`), whole dB, cuts first, a colleague's reasoning paragraph, a
Sources line, red flags. Then the PDF:
`python3 scripts/build_eq_pdf.py spec.json "<out>/EQ Recommendation - <source>.pdf"`.

## Dynamics
Reasoned with numbers, documented as `COMP:` / `GATE:` lines in the `.md`, never patched (R18).
Format: `references/console-bands.md`. A channel the reasoning leaves flat gets no line.

## Outputs
`<Show> - FOH Channel Processing.md` · `<Show>.ses` · `<Show> - Input List.xlsx` ·
`<Show> - Show Packet.pdf` (EQ response card on every input page) · `<Show> - FOH EQ Reasoning.pdf`
· `<Show> - MASTER.pdf` · `<Show> - Patch Sheet (Phone).pdf/.html` · `<Show>.spec.json`. No
generated stage plot, ever (R7).

## References
- `references/decision-flow.md` — the method end to end, worked examples.
- `references/deep-research-workflow.md` — visible research, note mining, failure catalog.
- `references/forum-research.md` — where to search, query patterns, source weighting.
- `references/genre-profiles.md`, `references/genre-geometry.md` — genre signatures; Celtic and
  classical geometry (incl. no phantom on the passive R88).
- `references/console-bands.md` — band layouts, Mustard paperwork format.
- `references/pre-commit-audit.md` — the audit lines, evidence quoted.
- `references/spec-schema.md`, `references/brief-schema.md` — the spec and the brief.

On a non-Fable model (check the system prompt's model line) also load **fable-parity**, which
adds per-unit worksheet files and strict one-unit-at-a-time serialization.
