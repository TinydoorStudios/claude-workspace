---
name: show-deep-build
description: >
  Brian's one skill for show EQ and show builds — the deep-research pipeline for a Q225
  (Memo/FSQ) or Wing show, and the standalone EQ brain (absorbed eq-advisor). THE DEFAULT FOR
  EVERY NEW SHOW: whenever Brian submits a new show in any form — a show to build, a
  channel/input list, an artist + venue, a ShowBuilder .md/brief/spec — this skill runs; he
  need not say "deep think". Phrases like "build the show / packet", "deep think this one",
  "run the deep build", "process these channels" all mean this. ALSO use for any standalone EQ
  question: "what EQ for [mic] on [instrument]", "how do I EQ the [source]", "EQ starting point
  for…", "tame the [frequency]", reviewing a mix — runs Part II alone. Always
  researches artist + genre first, then each source in the locked order instrument → mic →
  genre → venue against live-sound forums cross-checked with the KB. Show builds produce the
  packet (FOH .md, .ses patcher, Input List xlsx, Show/EQ/MASTER PDFs). Defaults to
  Q225/Wing; never CL3/M32 unless Brian names that desk.
---

# Show Deep Build — the whole pipeline, one skill

One skill, two ways in:

- **A show build** (Part I → Part II per channel → build). The default for every new show.
- **A standalone EQ question** (Part II alone): one source, inline answer + PDF.

*2026-07-09: this skill absorbed the former **eq-advisor** skill. Part II below IS eq-advisor —
anywhere the KB or old docs say "run eq-advisor", that now means Part II of this skill. The
learning log keeps its name: `Live Sound KB/_learning/eq-advisor-log.md`.*

## The one rule that overrides everything

**An unsure answer is ~3× more damaging than a pause.** Instant output is the tell that research
was skipped. If the artist, a mic, an instrument, the genre, the venue, or any value is uncertain —
**stop and ask Brian.** Never paper a gap with a confident guess. A clean "here's what I know,
here's the fork, which way?" is always the right call.

**In show builds, batch the round (locked 2026-07-05):** the plan pass (dedupe + locker fork loop +
note mining) collects every stop-and-ask trigger and every locker fork into **one question
round** before any EQ is committed. **Locker forks are gate items, not FYIs** (2026-07-26) — they
head the round, each carries its three-sentence reason, and no build passes the round with one
unanswered; see Step 2b. Brian answers once; the build runs straight through. Stop
mid-build only for a genuinely new fork the scan missed. **Carried flags count as questions:**
any open FLAG inherited from a prior rev or run (a mic-choice flag, a mono/stereo question, an
unassigned vocal) goes INTO the round and comes out either as a recorded decision or as an
explicitly renewed flag Brian chose to keep open — a build that ships the same FLAG two revs in a
row without asking is a failed question round. A round with ZERO questions on a multi-channel show
is suspicious — re-check the scan; there's almost always a genuine fork or two. Aim for few, sharp,
genuinely-forked questions with your read attached — not zero (gaps papered over) and not fifteen
trivia items (judgment offloaded to Brian). **Standalone questions ask immediately.**

## Execution discipline (merged from the fable-parity harness, 2026-07-12)

**The pacing rule (hard):** final EQ numbers never appear in the same message as the research that
justifies them. Research lands first (visibly); numbers are drafted in a later step against what
was found. Instant output is the tell that research was skipped — this rule makes it impossible.

**The constraint card:** at the start of every show build, after reading this file in full (no
"I remember this skill"), write the hard rules into a short card in your own words — whole-dB ·
cuts-first · vocals cuts-only · no high shelf unasked · band order/numbering · ribbon = NO 48V ·
TOUR flagged never swapped · locker fork on every mic'd input, DI/XLR exempt, three-sentence
reason, unanswered fork blocks the build · cut/boost ranges incl. the outdoor override · Memo standing waves +
fixed crowd rig · FSQ ch 10 reserved / OH stereo on 9 · wireless faders FSQ 33–36 / Memo 41–44,
multed when a channel names one, bare W58 = ask · research floor · capsule gate · reverbs
anchored to factory · one batched round · genre verified first (split evidence = ask now) ·
equipment rides the instrument layer · per-unit TRACE line. **Re-read the card immediately before the question round
and again before writing spec.json, and say that you did.** Late-context constraint loss (a half-dB
or a vocal boost appearing at channel 24) is the failure this closes.

---

# Part I — The show pipeline

Runs the flow from `_system/NEW-SHOW.md` (which now just points here). Machinery it drives:

- **Part II** (below) — every channel's EQ goes through it. No EQ logic lives anywhere else.
- **`scripts/build_packet.py`** — one deep-research `spec.json` → `.md`, Input List `.xlsx`,
  Show Packet PDF, EQ Rationale PDF, MASTER PDF. One source of truth; outputs can't drift.
- **The venue patcher** (`.ses`): FSQ `Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py`,
  Memo `Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py`. (The standalone `send-it`
  skill wraps the same patchers for rebuild-only runs.)

**What you need:** the input list (channels + mics/DIs) and venue + console. Canonical machine
input is ShowBuilder's `<Show>.brief.json` (facts only, no EQ — `references/brief-schema.md`);
a hand-typed list works. Only an artist name? Ask for the input list. Don't guess a mic from an
instrument. **Ask for the tech rider / stage plot if one exists** — densest research input there
is (real backline, monitor asks, wireless counts, tonal requests). If the list smells secondhand,
ask whether a rider PDF is sitting in an email.

**House wireless — fixed faders, and the mult rule (Brian, 2026-07-26).** Both Q225 templates
reserve four faders for the house wireless receivers, confirmed against the patchers' surface
labels:

| Venue | Wireless 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| **FSQ** | 33 | 34 | 35 | 36 |
| **Memo** | 41 | 42 | 43 | 44 |

Put information on a wireless 1–4 row in the input list and it lands on that fader — that's the
default, no thought required. **The mult:** when another input's mic reads `Wireless 2` (or
`W58 2`, `WL2`, `W2`), that input keeps its own channel *and* the wireless fader stays listed —
same receiver patched to both, so the input list shows the wireless's home channel next to the
named channel it's feeding. The patch column carries the same source port on both rows.
**Practical note for the paperwork:** two channels off one socket share the analog gain on a
Q225 — ride the per-channel digital trim on the mult, not the head amp, and say so in `notes`.

**A bare `W58` / "wireless" with no unit number is a stop-and-ask** — never auto-assign a unit,
never guess which pack. It goes in the question round like any other fork.

Default EQ ownership on a mult: the **named input** gets the deep build (it's the one being
mixed); the reserved wireless fader keeps the template's baseline curve untouched (FSQ faders
25–36 ship a vocal/wireless curve — an MD only overrides the bands it names). Don't write a
second EQ card for the multed fader; do list it on the input list and patch page.

`build_packet.py` enforces the mechanical half: bare-wireless mic → error, a wireless fader whose
mic names a different unit → error, a named wireless with no fader row → warning, a non-wireless
source parked on a wireless fader → warning.

### 0. Intake — normalize whatever arrived (2026-07-19)
Show info rarely arrives as a clean list. Whatever Brian drops or uploads — a rider PDF, a stage
plot, an xlsx/CSV input list, phone photos or screenshots of a printed/handwritten list or an
email thread — **read every artifact before any research starts** (PDFs page by page, images
visually) and normalize it into one set of brief facts: channels + mics/DIs, TOUR gear (with any
spec facts the rider states), monitor/wedge/IEM asks, wireless counts, backline, tonal requests.
File the originals in the show folder: the plot as `<Show> - Stage Plot.pdf`, the rider as
`<Show> - Rider.pdf` (the MASTER PDF picks both up automatically). Where two artifacts disagree
(the rider says 24 channels, the emailed xlsx says 18) or something's unreadable, that's a
question-round item — never silently pick a winner. The normalized facts are the build input;
everything downstream runs unchanged.

### 1. Route + confirm
Read `_system/ROUTING.md` for the venue row (folder, console, base `.ses`, patcher, KB articles —
pull only those). Confirm date + show name + whatever the venue row flags. Scaffold the folder:
`python3 _system/scaffold_show.py --venue <v> --date YYYY-MM-DD --name "Show Name"`.

The scaffold also writes **`show.status.json`** — the per-show state file (2026-07-19,
`_shared/show_status.py`). `build_packet.py` stamps `packet_built` and the .ses engine stamps
`ses_built` automatically; `published` is stamped by the wiki push, `verified` only if Brian
volunteers a desk load (optional — never a gate). Any later session reads
it (`python3 _shared/show_status.py show --folder "<show folder>"`) instead of guessing show
state from folder recency.

### 2. Verify the GENRE, then research the ARTIST — always

**2a. The genre gate (2026-07-19).** Before any other research, verify the genre with named
evidence — the act's own materials, streaming/venue listings, live footage, a prior verified
show. Write one line: `Genre: X — <evidence>`. This is verification, not a guess: if the
evidence is split or the act is hybrid, **stop and ask Brian right then** — the one exception
to the batched round, because the genre shapes every downstream search and can't wait for it.
The verified genre also rides the plan table, so Brian can veto it before any EQ commits.

**2b. Artist research.** Web-search the artist: who they are, sonic references, real
instrumentation, production style, vocal character. Fresh every show — the web pass is never
skipped or cached. Write a short **artist_profile**; it feeds every channel's genre layer in
Part II, and where the artist's actual sound differs from the generic genre profile, **the
artist wins**.

**Listen, don't just read.** Recent live videos (YouTube) and setlists (setlist.fm) over press
copy — the live footage tells you the actual arrangement, stage volume, and whether the input
list matches the band showing up. Lineup mismatches go in the question round.

**Prior-show check.** Search `Live Sound KB/Wiki/active-projects.md` + the shows index for the
same artist, series (FSQ Salsa!), or twin act at this venue. A console-verified past show is
Brian's own ground truth — evidence **beside** the fresh research, never instead of it. If the
verified history and new research disagree, that's a stop-and-ask fork; if paperwork already
exists, say so — the build may be a revision.

### 3. Plan, then research every source
**Dedupe before you search:** collapse N channels into the M unique instrument × mic units (four
Beta 58 vocals = one unit; per-channel differences come from role + notes). Show Brian the plan
table, research once per unit, fan back out.

**Mine the notes — they are deliberate research signals.** Every channel `notes` + the show-level
`show_notes`: amp/cab ("SVT + 8x10"), miking technique ("Fredman", "57+121 blend" — phase/comb
consequences), instrument specifics (flatwounds, 5-string), artist/stage constraints ("no gate",
broadcast → underheads). Research what you find (web + KB); if still unclear, ask — never drop a
note on the floor. What a note changed shows up in `mic_notes`/`eq_summary`, and in `changes` if
it moved you off the KB default. Table of worked examples: `references/deep-research-workflow.md`.

Then run **Part II per unit** — including the **locker fork loop on every mic'd input** (Step 2b;
DI and XLR line feeds are exempt) — and fire the **single batched question round** before
committing any EQ, with the locker forks at the top of it. **Record every answer in the spec's
`decisions` list** — the question round is research output; it rides the Rationale PDF.

### 4. Room context (+ weather outdoors)
Part II Step 5 applies the venue filter per channel. At the show level, record a **room_context**
line. **Outdoor shows: pull the show-time weather — fetched, never assumed.** For FSQ / WP / ESP /
CSP / ZP / IA, fetch the forecast for the actual show window (Open-Meteo; the Tempest stations for
current conditions) and put the numbers in `research.conditions` (temp, RH, wind, rain risk, with
the source named). Seasonal priors are banned — "July = warm and dry" is exactly the assumption
the 2026-07-08 A/B caught being wrong (actual forecast: 74% RH). Apply the real numbers: wind →
windscreen/mic-choice flags and open-mic wash; hot + DRY → extra HF air loss over distance
(protect presence, don't over-cut the top); hot + HUMID → HF carries slightly better (protect
presence, don't over-boost it); rain risk → note the contingency. Fold it into `room_context` so
the why is on paper. Indoor venues skip this. Note every divergence from the KB default and why →
the `changes` list.

### 5. Build everything from one spec
Write **`spec.json`** (`references/spec-schema.md`): metadata, `artist_profile`, **structured
`research`** (`genre_verified` · `gig` · `conditions` · one `units` row per instrument × mic —
finding, named external `sources`, one-word `verdict`, five-layer `trace` object — plus
`reconciliation` and any `kb_writeback`; the Rationale renders it as a per-unit TABLE, so never
dump it as one prose blob — the legacy free-text `research_summary` still builds but warns),
`room_context`, `changes`, `decisions`, optional `monitors`, **required
`reverbs` + `reverb_pairing`** (every show, FSQ included — 3 complementary vocal options, 1–2
instrument (horn-specific when asked), 1 general when warranted; Seventh Heaven Pro preset names
verbatim from the reverb KB, each with `settings`, `plugin_eq`, `why`; every settings value
ANCHORED to the preset's factory value — write "(factory)" when unchanged and "(from X factory)"
when moved, so at the desk it's obvious which knobs to touch; preset SELECTION justified by this
band's material (a second-line band earns a snare splash; a ballad earns the big-moment chamber),
not the generic default trio; opt-out only via `"no_reverb": true` when Brian says so), and
per-channel `bands` + `mic_notes` + `eq_summary` + `tour`/`ribbon` flags.

**Before writing spec.json: re-read the constraint card, then run the pre-commit audit**
(`references/pre-commit-audit.md`) — every line answered in visible output with the evidence
quoted (channel numbers and values, never a bare "verified"). build_packet.py's validator is the
floor, not the audit — it can't check judgment. Only after all lines pass:

```
python3 scripts/build_packet.py --spec "<show folder>/<Show>.spec.json" --out "<show folder>"
```

It validates first (ribbon+48V, vocal boosts, duplicates, ranges, RESERVED faders — FSQ ch 10 is
the SNARE PL8 return; the OH pair is STEREO on fader 9, never split 9/10 — the wireless faders
(FSQ 33–36 / Memo 41–44) and unnumbered `W58` mics; missing `reverbs`;
errors abort with nothing written), auto-lints the `.md` (`audio/_shared/md_lint.py`), and writes
the `.md`, `.xlsx` (+ Monitors/Reverbs sheets), Show Packet PDF, **EQ Rationale PDF**, and
**MASTER PDF** (packet + rationale + any band-provided `<Show> - Stage Plot.pdf` / `- Rider.pdf`
in the folder — stage plots are band-provided, never generated). The MASTER opens on a clickable
**QUICK LINKS** page (2026-07-27) — every document, EQ section and channel is one click away, and
the same map ships as PDF bookmarks; page numbers come from real page marks, so nothing to hand-
maintain. Deps: openpyxl + reportlab
(installed `--user`, 2026-07-06). Then the `.ses`:

```
python3 "<venue patcher>" --src "<venue _TEMPLATE>/<base>.ses" \
  --dest "<show folder>/<Show>.ses" --md "<show folder>/<Show> - FOH Channel Processing.md"
```

Require `bytes changed outside mic'd blocks: 0  PASS`, `readback: PASS`, and an identical file
size. Render a page of each PDF and eyeball for clipping before handing over.

### 6. Hand over — publish on Brian's go (rule changed 2026-07-19)
List which faders/EQ were written and which knobs he still dials by hand. Flag anything that
overrides a template baseline (e.g. FSQ vocal faders ship a wireless curve / feedback notch — a
vocal MD override removes it; call it out). **Shows are one-offs: console verification is NOT a
publish gate.** Brian's explicit go ("SEND IT", "push it") is the only gate for the wiki push —
never ask him to load-test the .ses first. If he volunteers that it ran on the desk, stamp it
(informational): `python3 _shared/show_status.py stamp --folder "<show folder>" --stage verified`.

### 7. Close out + harvest
Shows are one-offs; the lessons aren't. Ask "what will I reuse?" and write it into the KB:
mic-on-instrument that worked → `mic-library`; EQ move that landed → `eq-starting-points` (tag by
genre); reverb that worked → `reverb-reference-memo`; patcher/console gotcha → `console-digico-q225`
or the pipeline spec; new venue fact → that venue article (promote emerging → established). Log the
show's EQ decisions to `_learning/eq-advisor-log.md` and propose KB write-backs (see the
self-improvement loop below). Add the row to `active-projects.md` → Completed Shows; bump touched
articles' `Last updated`; note it in `CHANGELOG.md`. Workflow changes → `_system/IMPROVEMENTS.md`;
open items → `QUESTIONS.md`; preferences → auto-memory. Then the **show-wiki-push** skill on
Brian's go (venue-aware — FSQ and Memo; `fsq-wiki-push` is its legacy alias; other venues/KB
articles → `wiki-publish`). The push stamps `published` in `show.status.json`. (No post-show
"what did you move" solicitation — Brian declined that, 2026-07-05; if he volunteers a live
change, log it.)

---

# Part II — The EQ method (formerly the eq-advisor skill)

The standalone EQ brain: mic-, genre-, and venue-aware EQ for any live or recorded source, using
the web-then-KB verification workflow. Called per-unit by Part I, or alone for any ad-hoc EQ
question. Full detail + worked examples: `references/decision-flow.md`.

**Per-input order of importance AND process (locked 2026-07-05; equipment named as part of the
instrument layer 2026-07-19): instrument (+its notated equipment) → mic → genre → venue.**
Instrument + mic set the foundation and carry the most decision weight; genre — refined
by the artist profile, which outranks the generic genre read where they differ — bends the
targets; the venue is applied last as a constraint filter: it trims amounts and vetoes moves that
fight the room (often the biggest single bend in dB) but never rewrites the foundation.

For a standalone question you can start once you know the **instrument** and the **mic/DI** — ask
for whichever is missing, plus genre/venue/console/live-vs-post as they become relevant.

### Step 1 — Identify the instrument/source + its equipment
Exactly what's being miked: "electric cab, cranked" vs. "acoustic, fingerstyle" — the problems
differ. One mic, a two-mic blend (treat as one signal), or a section?

**Equipment is part of the instrument layer (2026-07-19).** Anything notated about the rig —
amp/cab model, drum sizes and heads, string type (flats/rounds), pickup/piezo type, 4- vs
5-string — is a first-class input to the baseline, with the same research floor as a mic: at
least one quantitative fact with a named source (an SVT 8x10's low-mid emphasis, a Twin
Reverb's bright top, a 26" kick's lower fundamental) before it may bend a value. Any EQ move
the equipment changed must cite it in that channel's `mic_notes`/`eq_summary`. Nothing
notated → the generic instrument carries; never invent a rig.

### Step 2 — Identify the mic/DI
The specific model changes the whole approach (pre-scooped D6 ≈ no EQ; flat DM6 = full shaping).
Resolve Brian's shorthand against `mic-library.md` / the CLAUDE.md mic table. Not in the library →
research item AND a stop-and-ask flag. For a self-present mic (i5, D2, SM81, KMS 105…) note what
the capsule already brings so you don't double it. Flag immediately, before any EQ math:

- **Ribbon mic** (R-121, R88…) → **NO 48V, in red.** Non-negotiable.
- **Two-mic source** (kick in/out, SM57/R-121 AxeMount, 57/27, 57/421, close+room) → treat the
  pair as one signal AND assign each mic ONE lane across the whole spectrum. Name the shared
  frequency zones (both mics' baked peaks and both mics' low ranges), then split ownership: one
  mic owns the attack/top zone, one owns the body/low zone — no boost on both mics in the same
  zone, top or bottom (a +3 low boost on the inside kick mic stacked on a +3 low boost on the
  outside mic is the classic failure). If one mic bakes in a peak the other is being boosted at,
  trim the baked one. Back the complement mic's low-mids (150–800 Hz) off so it doesn't stack;
  plan a mono/polarity check. The de-stack decisions go in both channels' `mic_notes`.
- **Switchable hardware** (contour switches — Beta 91A; pads; selectable HF caps — B3; sensitivity
  switches) → state the assumed switch position, build the EQ for that assumption, and write the
  fallback into `mic_notes` ("contour assumed FLAT — the 400 Hz cut lives on the desk; if the
  switch is engaged, halve the desk cut"). Never leave a switch state implicit.

### Step 2b — The locker fork (every mic'd input; DI/XLR exempt)
*Upgraded 2026-07-26 from an FYI "locker alt" line to a real fork Brian decides. It is a loop:
every eligible input runs it, and every raised fork is a gate — the build does not pass the
question round with one unanswered, and there is no silent default to the specified mic.*

**Eligibility gate — run this first, per input.** The fork only exists where there's a capsule to
swap:

| Input | Fork? |
|---|---|
| Any microphone Brian owns or specified | **Yes** |
| **DI** — RNDI, J48, AR133, artist's own DI, any instrument arriving through a DI | **No** |
| **XLR line feed** — wireless XLR out, keys/track/playback XLR, a console/ambient tie, anything landing at line level with no capsule in front of it | **No** |
| TOUR / artist-provided mic (⚑) | **No** — never suggest replacing artist gear |
| Fixed rigs — the Memo crowd array (OM1 / Deity S2 / CM4) | **No** — locked rig, don't re-derive |
| Mic + DI on one source (bass cab + DI) | **Yes, on the mic leg only** |

Exempt inputs pass silently: no fork, no question, no line in the packet.

**The loop, per eligible input:**

1. Load `mic-library.md` once per session; hold it. Name the source and the specified mic.
2. If the specified mic is already the locker's first call for this source → **silent pass.**
3. Otherwise sweep the locker for candidates and score each on a concrete, nameable win:
   less-EQ voicing · a baked peak colliding with this genre/room · rejection or feedback margin ·
   SPL handling · kit/section coherence · physical fit (clip vs. stand, sightlines, space).
   Marginal or taste-level wins do **not** qualify — a tie goes to the specified mic.
4. **Availability check before raising it:** the alternative must be free — not already assigned
   to another channel in this show, and not a second call on a single-piece mic. Note its kit
   source (DP8, DK-6, V Pack Arena, standalone) so Brian knows what case it comes out of.
5. **One alternative per input, maximum.** Two candidates → pick the stronger and drop the other.
6. Raise the fork in the card format below.

**The fork card — the reason is exactly three sentences:**

```
LOCKER FORK — CH 4 · Snare top
  Specified:  Audix i5          Alt: Earthworks DM17 (DK-6)
  Why: <1 — the concrete win, with a number and its source>
       <2 — what it changes downstream: EQ moves saved, or the room/genre problem it solves>
       <3 — the honest cost: what he gives up, or why it's a close call>
  Call: keep i5  ·  swap to DM17
```

Sentence one is the win with a fact attached, sentence two is the consequence for this show,
sentence three is the tradeoff told straight. Not two sentences, not a paragraph — three. No
recommendation without all three; if you can't fill sentence three honestly, the win wasn't real
and the fork shouldn't be raised.

**Where it lands:**

- **Show build** — forks batch into the single up-front question round (locked 2026-07-05),
  listed first, before the other questions. Brian answers all of them in one pass.
- **Standalone EQ question** — ask immediately, same card.
- **Accepted** → re-enter Step 2 for that channel with the new mic, and carry the swap through the
  Input List (48V, stand, split patch), the patcher, and `changes` (`Locker fork — swapped …`).
- **Declined** → EQ builds for the specified mic; one line in `mic_notes`
  (`Locker fork — DM17 offered, i5 kept`) so the same fork isn't re-litigated next rev.

### Step 3 — Baseline: web first, KB second, reconcile
The web pass runs fresh **every show/question, no exceptions** — no cross-show caching (within-show
dedupe is fine). One source outranks the forums: **Brian's own console-verified past show** on the
same source in the same room — KB-grade evidence, used beside the fresh pass, never instead.

1. **Search the live-sound community**: the LAB at Pro Sound Web (board 9) and Gearspace Live
   Sound; maker frequency-response specs and reputable write-ups are fair game. Query patterns +
   source weighting: `references/forum-research.md`.

   **The research floor (Brian's guardrail, 2026-07-08, from the hot-mag A/B): the KB is for
   longevity, not research.** The KB is where verified knowledge is ARCHIVED so it survives
   between sessions — it is never the research source for a build. No model, on any channel, may
   justify a value with "KB only." Every unique instrument × mic unit gets its own fresh web pass,
   every show — there is no "familiar mic" exemption: an SM57, a Beta 58A, an i5, a D6 all get
   searched. A unit is not researched until the summary can state at least one QUANTITATIVE
   capsule fact for it — a frequency and a dB value (a baked peak, a scoop, a roll-off point) —
   with an EXTERNAL source named. Every `research.units` row in a show spec must name its external
   source ("SOS/Gearspace i5 (+9 dB @ 5.5k baked peak)"), and the block closes with an explicit
   `reconciliation`: either "no web↔KB disagreements" or the list of them.

2. **Cross-check the KB**: `mic-library.md` (mic character + blend logic), `eq-starting-points.md`
   (per-instrument approach). The KB is Brian's verified operational knowledge — authoritative for
   RESOLVING a conflict or confirming a web finding, never a substitute for the web pass itself.
   "The KB already covers this mic" is not a reason to skip the search; it's the reason the
   cross-check will be strong.
3. **Reconcile — and commit to exactly one word per unit: AGREE / DISAGREE / THIN.** The word gets
   written before any numbers do. If you catch yourself writing "the web broadly aligns with the
   KB," stop — that's the false-agreement paraphrase this word exists to kill; name the numbers on
   both sides and pick the word. AGREE → solid, sourced baseline. DISAGREE / THIN / mic unknown →
   **don't average and move on — stop and ask**, showing both sides and your read. A web↔KB fork always carries
   three explicit options: (a) go with the research, (b) go with the KB, (c) go with the research
   AND update the KB entry to match. If Brian picks (a) without (c), note the standing difference
   in `mic_notes` so it resurfaces next time instead of silently persisting. Not only for
   conflicts: when fresh research surfaces something concretely better than the current KB entry
   (a more precise frequency, a baked-peak fact the KB lacks), offer the KB update in the question
   round too. Accepted updates go through the normal staged write-back — never silently to the wiki.

**The capsule-voicing gate (2026-07-08):** before writing ANY boost, state what the capsule
already bakes in at or near that frequency. If the boost lands inside a baked peak, the correct
move is a trim or nothing — never a boost stacked on a voiced peak (the i5 bakes in +9 dB @ 5.5k;
the desk's job there is −3, not +2). Same gate in reverse: don't deep-cut a zone the capsule
already scooped (the D6's −15 dB @ 600 means the desk cut nearby is light or absent). Every boost
in the final spec must survive this gate, and the channel's `mic_notes` must show the baked-in
fact that justified it.

Every move must be traceable to a source — forum consensus or manufacturer spec (the KB verifying
it), never the KB alone.

### Step 4 — Layer the genre + the artist
Bend the baseline toward the genre's sonic signature (`references/genre-profiles.md`; the KB's
Genre Modifiers section is the spine). **The artist profile refines the genre and outranks it
where they differ** — vocal character, tone references, arrangement density, production style.
Standalone questions: ask who the artist is if it would change the call. The big levers: how
aggressive (acoustic-forward = lighter; dense/loud = deeper separation cuts), tonal target, and
the hard rules — classical = cuts-only minimal; celtic = 5 ms+ attack, never gate sustained
notes; acoustic/piezo DI = the 1.5–2 kHz quack is the primary cut. Genre unclear or hybrid → ask.

**Sections get slotted in the numbers, not the prose (2026-07-08).** When a show has a section —
a horn line, multiple backing vocals, twin guitars — and the research says to separate them, the
separation must be visible in the band values: each member's EQ must differ in the lane it owns,
and each channel's `eq_summary` must name that lane ("bone owns ~1k, so its cut sits at 600").
Three near-identical curves under a research note that says "slot the horns" is a failed build.
Before writing the spec, re-read every sectional principle in your own research summary and audit
the numbers against it — if a stated principle isn't traceable in the values, fix the values or
drop the claim.

### Step 5 — Layer the venue + Brian's philosophy
The room is the final, heaviest filter. Pull the show's `venue-*.md`:

- **Memo:** standing waves **63 / 125 / 200 / 250–315 Hz** — boosts there are suspect, cuts
  favored; bodhrán and kick are the highest-risk channels; DEQ where a static cut won't hold;
  RT60 ~1.6 s. The crowd rig (OM1 / Deity S2 / CM4) has **fixed EQ — don't re-derive it.**
- **FSQ / outdoor (WP, ESP, CSP, ZP, IA):** no room gain — **cuts run DEEPER than indoor
  (2026-07-08): −6 to −9 dB typical, up to −10 on mud/box, tight Q.** Clarity is the whole game;
  a polite indoor-depth cut reads as no cut at all. Torn between two depths → take the deeper.
  HPF higher, be decisive.
- **Greaves / classical:** correction-only, conservative, trust placement.

Global philosophy: **cuts before boosts, always. Vocals: cuts only, every genre (feedback
control, not taste). Whole-dB only. No high-shelf band unless Brian asks.** Typical cuts −4 to
−7 dB tight Q (1.5–2.0), boosts +3 to +6 dB on non-vocal sources — with the outdoor override above.

### The per-unit layer trace (2026-07-19)
In show builds, every unit carries a five-layer **TRACE** showing the whole chain, each layer
holding a value or an explicit "no change". In a show spec it's the `trace` object on the unit's
`research.units` row (`base` · `equip` · `genre` · `artist` · `venue`), which the Rationale prints
one layer per line; inline and in standalone answers, the same thing as one line:

`TRACE: base(57 on 4x12 — −5@450, SOS baked-presence fact) · equip(Twin Reverb bright top —
trim 3k, no boost) · genre(blues-rock — keep low-mid) · artist(dark tape tone — no HF lift) ·
venue(Memo — 250 cut deepened to −6)`

"No change" proves the layer was run, not skipped. The pre-commit audit spot-checks TRACE
lines against the actual band values — a trace that doesn't match its channel's numbers is a
failed audit line.

### Standalone output — inline, then PDF, every time
**Inline:** the recommendation in the target console's band layout (default Q225:
`HPF · LPF · Band 4 (HF) → Band 3 → Band 2 → Band 1 (LF)`; band numbers match the console, 1 = LF —
Wing/CL3/M32 layouts in `references/console-bands.md`), whole dB, cuts-first, a short reasoning
paragraph per source written like a colleague, a Sources line, and any red flags. **PDF:**
`python3 scripts/build_eq_pdf.py spec.json "<out>/EQ Recommendation - <source>.pdf"` (schema at
the top of the script); save to the show folder if it's show work, else Desktop/project folder.
(Show builds skip this — the packet's Rationale PDF carries the reasoning.)

---

## Outputs (show build — the full packet, every show)
`<Show> - FOH Channel Processing.md` · `<Show>.ses` · `<Show> - Input List.xlsx` ·
`<Show> - Show Packet.pdf` · `<Show> - FOH EQ Reasoning.pdf` · `<Show> - MASTER.pdf` ·
`<Show>.spec.json` — plus the required reverb section. No generated stage plot, ever.

**EQ response card, every input (2026-07-28).** Each EQ channel page in the Show Packet opens with
a filled response curve drawn from that channel's own numbers — every active band as a biquad, HPF
and LPF folded in, filled and stroked in the section's accent colour, each band dotted and labelled
`B3 -5 @300 Q2` (`D` appended when the band is dynamic). Automatic: `build_packet.py` hands
`show-packet-builder-template.py` a numeric `curve` per channel and `eq_curve_card()` draws it. It
adds no pages and flows into the MASTER. Two limits are printed on the card itself — filters are
drawn at 12 dB/oct because the spec carries no slope (corner exact, steepness indicative), and the
curve is the EQ section only, so the documented Mustard dynamics are not in it. Nothing to do per
show; it is only worth mentioning if Brian asks why a curve and a table disagree.

## Guardrails
- Q225 (Memo/FSQ) or Wing only. **Never CL3/M32 unless Brian names that desk.**
- The research must be **visible** — Brian should see the searches run. Instant output = skipped
  research (`references/deep-research-workflow.md` opens with the failure story).
- Dynamics notes carry numbers, not adjectives: "fast-attack comp" is incomplete — write the
  range and ratio ("10–20 ms, 3:1"). Gate philosophy states what must survive ("ghost notes and
  press rolls must live"), tied to the genre.
- **Those reasoned dynamics get DOCUMENTED, not written to the .ses.** On a Q225 build, every channel
  whose reasoning lands on a compressor or gate still emits `COMP:` / `GATE:` lines in the FOH .md
  alongside its bands — but the patcher no longer patches Mustard into the .ses (console-verified
  2026-07-16, then pulled from the build the same day on Brian's call after hearing the activation
  live; paperwork keeps the lines, the build ignores them). Pick the Mustard colour from the
  reasoning (Blue/Red/Green/Purple/Silver), write a documented starting threshold with the GR target
  in `mic_notes`, and realize a ducker as `Duck` / an expander as a shallow-range `Gate` — this is
  still the correct reasoning to capture, it's just for the desk/paperwork, not the byte-patch.
  Format + rules in `references/console-bands.md`. A channel left flat by the
  reasoning gets no line. (Wing has no Mustard writer yet — dynamics stay in notes there.)
- Per-channel `mic_notes` cite their source inline ("SOS/Gearspace + KB agree: …"), and every
  `eq_summary` connects the moves to the channel's musical role in THIS band, not a generic
  description. Stands and mounts are chosen for the physical mic (an e609 has no clip mount —
  a hat needs a boom; a kick-port or cab mic takes a Short stand).
- Default delivery PDF. Warm, direct, non-corporate writing (`about-me/writing-rules.md`).
- Reference build: `Fountain Square/Izzy 2.0 Deep Think/`.

## Self-improvement loop
After any recommendation — especially a Brian override or a resolved stop-and-ask — capture it:
1. **Log** a dated entry to `Live Sound KB/_learning/eq-advisor-log.md` (source, mic, genre,
   venue, moves, web- vs KB-sourced, disagreements, the resolved truth).
2. **Propose a KB write-back** when durable: mic character → `mic-library.md`; confirmed
   setting/genre note → `eq-starting-points.md`; a resolved web↔KB conflict → fix the KB. **A
   Brian override is ground truth.**
3. **Never write the live wiki silently** — stage it, hand the push to `wiki-publish`.

## Reference files
- `references/decision-flow.md` — the EQ method end-to-end with worked examples.
- `references/forum-research.md` — PSW/Gearspace query patterns + source weighting.
- `references/genre-profiles.md` — genre signatures → EQ influence.
- `references/console-bands.md` — Q225/Wing band layouts (CL3/M32 documented, ask-only).
- `references/deep-research-workflow.md` — visible-research rules, note-mining table, evidence
  channels, two-mic sources, WHY capture.
- `references/pre-commit-audit.md` — the 13-line evidence-quoting audit run before spec.json.
- `references/spec-schema.md` — the deep-research `spec.json` schema (build input).
- `references/brief-schema.md` — ShowBuilder's `<Show>.brief.json` (facts-only input).

**On a non-Fable model** (Opus, Sonnet — check the system prompt's model line), also load the
**fable-parity** overlay skill: it adds the per-unit worksheet files + strict one-unit-at-a-time
serialization that weaker models need to hold this pipeline together. On Fable it's unnecessary.
