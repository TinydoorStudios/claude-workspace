---
name: eq-advisor
description: >
  Mic-, genre-, and venue-aware EQ for any live or recorded source, using Brian's web-then-KB
  verification workflow. REQUIRED EQ step in the show-building / ShowBuilder flow — every show's
  EQ runs through it. Use whenever Brian is dialing in or asking about EQ: "what EQ for [mic] on
  [instrument]", "how do I EQ the [source]", "EQ starting point for...", "tame the [frequency]",
  building channel processing, reviewing a mix, or deciding cuts vs boosts. Walks instrument →
  mic → live forum research (Pro Sound Web, Gearspace) cross-checked against the Live Sound KB →
  genre → venue/room, stopping to ask on any uncertainty (an unsure answer is worse than a
  pause). Cuts-first, whole-dB, inline plus a PDF. Defaults to Q225 (Memo/FSQ) or Wing; does not
  produce CL3 or M32 unless Brian names that console.
---

# EQ Advisor

Build an EQ recommendation for a source the way Brian actually reasons about it: start from the
instrument, layer the specific mic, confirm the baseline against the live-sound community **and**
his own KB so the two verify each other, then bend it for the genre and finally for the room.
Cuts before boosts, whole dB, and the room (reverberant, often outdoor) is always the last and
heaviest filter.

This skill is the standalone EQ brain. It pulls knowledge from Brian's Live Sound KB
(`~/Documents/Claude/audio/Live Sound KB/Wiki/`) rather than re-deriving it, and it can be called
from any workflow — an ad-hoc "how should I EQ this" question, the show channel-processing
pipeline, ShowBuilder, or a post mix.

## The one rule that overrides everything

**An unsure answer is roughly 3× more damaging than a pause.** If the web and the KB disagree, if
the mic or instrument or genre is ambiguous, if you're inferring a value you can't source, or if a
move would fight a known room problem — **stop and ask Brian before you commit it.** Never paper
over a gap with a confident-sounding guess. A clean "here's what I know, here's the fork, which way?"
is always the right call. See *Stop-and-ask protocol* below.

## What you need before starting

You can begin once you know the **source/instrument** and the **mic or DI** on it. Everything else
you gather as you go, asking when it isn't obvious:

- **Genre / sub-genre** (drives tonal targets and how aggressive to be)
- **Venue** (drives the room filter — Memo standing waves, FSQ/outdoor, Greaves, etc.)
- **Console** (drives the band layout you output). Default to the venue's primary desk — **Q225**
  (Memo / FSQ) or **Wing** (secondary venues). **Do not produce CL3 or M32 layouts unless Brian
  explicitly names that console** — he isn't using this skill for those desks by default.
- **Live vs. recorded/post** (live = feedback-aware and cut-heavier; post = correction-only)
- Any **inline channel notes** (placement, two-mic blend, broadcast restriction, artist requests)

If the instrument or the mic is missing, ask for it — those two are the spine of the whole thing.
Don't guess the mic from the instrument.

## The pipeline

Run these in order. Each step narrows the last. **Per-input order of importance AND process
(Brian, locked 2026-07-05): instrument → mic → genre → venue.** The instrument and mic set the
foundation and carry the most decision weight; genre — refined by the show's artist profile, which
outranks the generic genre read where they differ — bends the targets; the venue is applied last
as a constraint filter — it trims amounts and vetoes moves that fight the room (and is often the
biggest single bend in dB), but it never rewrites what the instrument + mic established. Read
`references/decision-flow.md` for the full detail and worked examples; the summary is here.

### Step 1 — Identify the instrument/source

Pin down exactly what's being miked: not just "guitar" but "electric guitar cab, cranked" vs.
"acoustic guitar, fingerstyle." The sonic problems differ. Note whether it's one source with one
mic, one source with two mics (a blend — treat as one signal), or a section.

### Step 2 — Identify the mic/DI

Get the specific model. The mic changes the whole approach — a pre-scooped Audix D6 on a kick needs
almost no EQ; a ruler-flat Earthworks DM6 on the same kick takes the full shaping. Resolve Brian's
shorthand against the KB (`mic-library.md` and `CLAUDE.md` mic table — e.g. DM6, U87 Jr, B3, RNDI).
If the mic isn't in the library, that's a research item *and* a stop-and-ask flag (see Step 3).

Flag immediately, before any EQ math:

- **Ribbon mic** (R-121, R-10, R88, etc.) → **NO 48V, in red.** Non-negotiable.
- **Two-mic blend** (SM57/R-121 AxeMount, 57/27, 57/421) → treat the pair as one signal; back the
  complement mic's low-mids (150–800 Hz) off ~half so it doesn't stack; plan a mono/polarity check.

### Step 2b — Mic locker pass (alternative check, every input)

Load `mic-library.md` once per session and hold the locker table in memory — don't re-read it per
channel. Then for every input, after the specified mic is resolved:

1. **First-call check.** Is the specified mic already the locker's first call for this source (the
   "Reach For It When" column, plus the Standard Combos section)? If yes → no suggestion, move on.
2. **Beat-it check.** Does a locker mic beat it *for this show* on a concrete, nameable win:
   a voicing that needs less EQ (pre-scooped vs. flat), a known problem peak that collides with
   the genre or the room (a presence spike into a bright source, proximity build into a Memo
   standing-wave zone), rejection/feedback margin on a loud stage, SPL handling, or kit coherence
   (a kit already deployed on the show covers it — e.g. DK-6 is out, so DM17 over i5)?
3. **Record at most ONE alternative** — the best candidate only — with a one-line why. It is a
   suggestion, not a swap: the EQ is still built for the specified mic.
4. **TOUR / artist-provided gear is exempt.** Never suggest replacing an artist's mic; note its
   character in `mic_notes` instead.
5. **Batch the suggestions.** Present all locker alternatives together in the show build's single
   up-front question round (see *Stop-and-ask protocol*), not channel-by-channel. If Brian accepts
   one, re-run that channel from Step 2 with the new mic.

Marginal or taste-level wins don't qualify — a suggestion with no concrete why is noise. Output:
inline as a `Locker alt:` line under the channel; in show builds it also lands in that channel's
`mic_notes` and as a `Locker alt —` entry in the spec's `changes` list so it rides the Rationale
PDF's "what changed" box.

### Step 3 — Baseline: research the web, then cross-check the KB (they verify each other)

This is the heart of the skill and the order Brian asked for: **web first, KB second, reconcile.**
The web pass runs fresh on **every show, no exceptions** (Brian, 2026-07-05) — the artist context
changes what transfers. The KB cross-check is verification, not a cache; never skip the search
because the same pairing was researched on a prior show. (Deduping *within* one show — researching
a repeated instrument × mic unit once — is still right.)

One source outranks the forums: **Brian's own console-verified past show** on the same source in
the same room (a wiki show page or a verified `.ses`/Rationale in a show folder). That's not a
cache — it's KB-grade evidence. Use it beside the fresh web pass; if the two disagree, that's a
stop-and-ask, same as any web↔KB conflict.

1. **Search the live-sound community first.** Pull real-world settings and the mic's frequency-
   response character for *this mic on this instrument*. Primary sources, in order of trust:
   the LAB at Pro Sound Web (`forums.prosoundweb.com`, board 9 — the Classic Live Audio Board) and
   Gearspace's Live Sound board (`gearspace.com/board/live-sound/`). Manufacturer frequency-response
   specs and reputable engineer write-ups are fair game for the mic's baseline curve.
   `references/forum-research.md` has the exact query patterns, what to extract, and how to weight a
   one-off forum post vs. a consensus.
2. **Then cross-check against the KB.** Compare what you found to `mic-library.md` (per-mic character
   + EQ tendency, two-mic blend logic) and `eq-starting-points.md` (per-instrument approach). The KB
   is Brian's verified operational knowledge — when it speaks to the source, it's authoritative.
3. **Reconcile.** Where web and KB **agree**, you've got a solid, sourced baseline — proceed.
   Where they **disagree**, or the web is thin/contradictory, or the mic isn't in the KB at all —
   **do not average them and move on. Stop and ask Brian**, showing both sides and your read. This
   mutual verification is the point of doing both; a disagreement is a signal, not noise.

Output of this step: a baseline set of moves (HPF, problem cuts, any character) with each move
traceable to a source — KB, a forum consensus, or a manufacturer spec.

### Step 4 — Layer the genre + the artist

Research/confirm the genre's sonic signature and bend the baseline toward it. `references/genre-profiles.md`
has profiles for the genres Brian works (jazz, classical, chamber/orchestral, celtic, folk/acoustic,
blues/soul, gospel & choir, rock, R&B/funk, salsa/latin, bluegrass, singer-songwriter) with the EQ
influence each implies. The KB's Genre Modifiers section in `eq-starting-points.md` is the spine; the
reference file expands it.

**The artist profile refines the genre — and outranks it where they differ** (Brian, 2026-07-05).
In show builds there is always an `artist_profile` from the deep build's artist research; standalone
questions should ask who the artist is if it would change the call. The genre profile is the generic
target; the artist's actual sound is specific evidence about *this* show. Apply it per input: the
vocalist's character (breathy vs. belty → different presence and proximity handling), the guitar
tone references, how dense the arrangements run, the production style (restraint-forward vs.
aggressive). "Pop-soul" says one thing; "pop-soul, but she sings like Amy Winehouse over a sparse
trio" says something more useful — use the second.

The big levers genre pulls:

- **How aggressive.** Acoustic-forward (classical, chamber, celtic, folk) = lighter, smaller cuts,
  let the mic work. Dense/loud (gospel choir, rock, R&B) = deeper cuts for separation.
- **Tonal target.** More thump for blues/soul, more click for rock, natural for jazz/acoustic.
- **Hard genre rules.** Classical = cuts-only, minimal, trust the placement. Celtic = 5 ms+ attack,
  never gate sustained notes. Acoustic/piezo DI = the 1.5–2 kHz quack is the primary cut, always.

If the genre is unclear or a blend ("jazz, but a loud brass-heavy big band"), ask — it flips the
whole aggressiveness scale.

### Step 5 — Layer the venue, the room, and Brian's philosophy

The room is the final and heaviest filter. **Cuts, not boosts. Mostly aggressive. The rooms are
reverberant and frequently outdoor.** This is the default posture unless the source/genre says
otherwise (classical recording being the obvious exception).

Pull the venue file for the show (`venue-*.md`) and apply its specifics:

- **Memorial Hall:** standing waves at **63 / 125 / 200 / 250–315 Hz** — any boost in that range is
  suspect; cuts there are favored. Bodhrán and kick are the highest-risk channels. DEQ where a static
  cut won't hold. Working RT60 ~1.6 s. The crowd rig (OM1 / Deity S2 / CM4) has *fixed* EQ — don't
  re-derive it; see the venue file.
- **Fountain Square / outdoor (WP, ESP, CSP, ZP, IA):** open-air PA, no room gain to lean on —
  **cuts run DEEPER than the indoor default (Brian, 2026-07-08): −6 to −9 dB typical, up to −10
  on mud/box, tight Q.** Clarity is the whole game outdoors — the PA fights street noise and gets
  no help from the room, so a polite indoor-depth cut reads as no cut at all. When torn between
  two depths, take the deeper one. HPF higher, be decisive.
- **Greaves / classical recording:** correction-only, conservative, trust the mic and placement.

Then apply the global philosophy from `CLAUDE.md` / `eq-starting-points.md`:

- **Cuts before boosts — always.** Subtractive first.
- **Vocals: cuts only, no boosts, every genre.** This is feedback control, not taste.
- **Whole-dB values only.** Never half-dB.
- **No high-shelf band unless Brian asks.**
- Typical cuts −4 to −7 dB, tight Q (1.5–2.0); boosts (when justified on non-vocal sources) +3 to +6 dB.

## Stop-and-ask protocol

Stop and ask **before committing** whenever any of these is true. This is the skill's core safety
behavior — Brian would much rather answer a question than get a wrong number.

- Web research and the KB **disagree** on a move (frequency, direction, or amount).
- The **mic or instrument isn't in the KB** and the web is thin or contradictory.
- The **genre is ambiguous** or a hybrid that flips the aggressiveness scale.
- A move would **fight a known room problem** (e.g. boosting into a Memo standing wave).
- You're about to **infer a value you can't source** to either the web or the KB.
- The input list note is **ambiguous** (placement, blend, restriction).
- **Console band structure** doesn't cleanly map the move (e.g. a 4-band idea onto a different layout).

When you stop: state what you know, cite the sources, lay out the fork in one or two sentences, and
give Brian the options. Then wait. Don't pre-build the rest assuming an answer.

**In show builds, batch the round (Brian, 2026-07-05).** Scan the full input list first — the
dedupe plan, the locker pass, the note mining — and collect every stop-and-ask trigger, plus the
locker alternatives, into **one question round** before any EQ is committed. Brian answers once,
then the build runs straight through. Batching is not a license to plow ahead: if a genuinely new
fork appears mid-build that the scan missed, stop then as usual. Standalone single-source
questions (outside a show build) still ask immediately.

## Output — inline, then PDF, every time

Produce both, every run.

**Inline:** the recommendation in the **target console's band layout** (default Q225:
`HPF · LPF · Band 4 (HF) → Band 3 → Band 2 → Band 1 (LF)`; band numbers match the console, 1 = LF,
4 = HF — see `references/console-bands.md` for Wing/CL3/M32). Whole dB, cuts-first. Include a short
**reasoning** paragraph per source written like a knowledgeable colleague (Brian's writing rules —
specific, "cut 6 dB at 250 Hz" not "reduce the low-mids", no AI tells), and a **Sources** line
(forum threads + KB articles used). Surface any red flags (ribbon = no 48V) and note anything that
was confirmed with Brian during the stop-and-ask.

**PDF:** render the same content with `scripts/build_eq_pdf.py`. It takes a JSON spec and writes a
PDF in Brian's house color scheme and the canonical EQ layout. Usage:

```bash
python3 scripts/build_eq_pdf.py spec.json "/output/path/EQ Recommendation - <source>.pdf"
```

The JSON schema and a worked example are documented at the top of the script. Save the PDF to the
right place by Brian's routing rules: the show folder if it's show work, otherwise the Desktop or the
current project folder. Then present the PDF to him.

## Use inside ShowBuilder / the show pipeline

This skill is the EQ authority for show work — it isn't optional. Whenever a show is being built (the
`_system/NEW-SHOW.md` flow, the Show Processing Pipeline, or ShowBuilder), run **every channel's EQ
through this skill** instead of copying raw numbers out of `eq-starting-points.md`. That article is the
starting framework; this skill is how it gets applied to a specific mic, genre, and room.

- **Stay consistent with the app.** ShowBuilder's own engine (`Code/ShowBuilder/` on the Mac) derives
  EQ from the same KB. This skill is the Claude-side path; the two must not drift. When this skill
  learns something, it writes back to the KB (see below) so the app inherits it too.
- **Output the show's canonical layout** so results drop straight into the Show Document and the `.ses`
  pipeline: Q225 `HPF · LPF · Band 4 → Band 1` (full spec: `pipeline-spec-memo.md`).
- **Memo crowd rig** (OM1 / Deity S2 / CM4) keeps its fixed EQ — don't re-derive it.
- **Multi-channel shows:** run the pipeline per channel; batch the web research where the same
  mic/instrument repeats, but still stop-and-ask on any per-channel uncertainty.

## Self-improvement loop

The skill improves by improving its own knowledge source — the KB — so every show makes the next run
smarter. After any recommendation, and **especially when Brian overrides a suggestion or resolves a
stop-and-ask**, capture the lesson:

1. **Log it.** Append a dated entry to `~/Documents/Claude/audio/Live Sound KB/_learning/eq-advisor-log.md`:
   source, mic, genre, venue, the moves, what was web- vs KB-sourced, any web↔KB disagreement, and
   Brian's override/confirmation and the resolved truth.
2. **Propose a write-back** when the lesson is durable: new or corrected mic character →
   `mic-library.md`; a confirmed setting or genre note → `eq-starting-points.md`; a resolved web↔KB
   disagreement → fix the KB so it won't resurface. **A Brian override is the strongest signal — treat
   it as ground truth** and propose the change.
3. **Never write to the live wiki silently.** Stage the change and hand the push to the **wiki-publish**
   skill (Brian triggers it). This mirrors how ShowBuilder self-improves back into the KB.

A mic-on-source or genre call that lands well should become a KB fact the next conversation inherits —
that's the whole point of the loop.

## Reference files

- `references/decision-flow.md` — the full 5-step pipeline, the verification/reconciliation logic,
  and worked examples end to end.
- `references/forum-research.md` — Pro Sound Web + Gearspace search patterns, source weighting, and
  how to reconcile a forum finding with the KB.
- `references/genre-profiles.md` — genre sonic signatures → EQ influence, keyed to Brian's work.
- `references/console-bands.md` — band layouts for Q225 and Wing (the defaults); CL3 and M32 are
  documented but used only when Brian explicitly asks for that desk.

## KB sources this skill leans on

`eq-starting-points.md`, `mic-library.md`, `mic-dpa-4099.md`, the `venue-*.md` file for the show's
venue, `console-*.md` for the desk, and `show-processing-pipeline.md` / `pipeline-spec-memo.md` for
the canonical channel-card layout. The KB is the canonical knowledge source — when it and this skill
ever disagree, the KB wins and the skill gets updated.
