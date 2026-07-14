---
name: fable-parity
description: >
  Overlay for show-deep-build on non-Fable models (Opus 4.8, Sonnet, etc.) — check the system
  prompt's model line at session start; if it doesn't say Fable, load this alongside
  show-deep-build for every show build and standalone EQ question. Adds the two heavy mechanics
  weaker models need and Fable doesn't: per-unit research worksheets written to disk, and strict
  one-unit-at-a-time serialization. All other Fable-discipline devices (pacing rule, constraint
  card, one-word reconcile verdict, pre-commit audit, failure catalog) live in show-deep-build
  itself as of 2026-07-12 and apply to every model — this skill adds no audio knowledge and
  defers to show-deep-build on any fact.
---

# Fable Parity Overlay — externalize and serialize

show-deep-build carries the full discipline now: the pacing rule, the constraint card with forced
re-reads, the AGREE/DISAGREE/THIN verdict, the 13-line pre-commit audit, and the failure-mode
catalog all run on every model. What Fable does that a smaller model can't is hold a 20-channel
show's research, constraints, and cross-channel structure in its head at once. This overlay
replaces that head-state with disk-state.

## Mechanic 1 — Externalize: per-unit worksheets

Nothing important lives only in your reasoning. Create `_worksheets/` in the show folder (scratch,
not a deliverable — never ships in the packet). The plan pass writes `_worksheets/plan.md` (the
unit table, every mined note with its research question, every carried FLAG, the artist-research
findings). Then each unit gets `_worksheets/unit-NN-<slug>.md` from this template — every field
mandatory, "none" only with a stated reason:

```
# Unit NN — <instrument> × <mic>

INSTRUMENT   what exactly, how played, role in THIS band's mix
MIC          resolved model + KB tendency line; switch state assumed (if switchable);
             ribbon/TOUR/two-mic flags
SEARCHES     the literal queries run (minimum 2 phrasings, site-scoped per forum-research.md)
CAPSULE FACT ≥1 frequency + dB value with the EXTERNAL source named
             ("SOS: i5 bakes +9 dB @ 5.5k"). No fact = unit not researched = stop.
WEB SAYS     concrete settings/character found, weighted by consensus
KB SAYS      mic-library + eq-starting-points read for this pairing
VERDICT      AGREE / DISAGREE / THIN + one line why (per the master's Step 3;
             DISAGREE/THIN → question-round entry with the (a)/(b)/(c) fork)
LOCKER       first-call match / one named alternative + concrete win / none
GENRE BEND   what genre + artist profile change vs. the baseline, and why
VENUE BEND   what the room trims or vetoes, in dB
DRAFT BANDS  console layout, whole dB, cuts first
GATE CHECK   per boost: the baked-in capsule fact that permits it.
             Per two-mic pair: which mic owns which lane, top and bottom.
QUESTIONS    anything for the round, or "none"
```

**spec.json is assembled FROM the worksheets, never from memory.** The question round is built
only from plan.md + the worksheets' QUESTIONS and LOCKER lines. The pre-commit audit's evidence
quotes come from the worksheets. The constraint card the master requires goes in
`_worksheets/constraints.md`.

## Mechanic 2 — Serialize: one unit at a time

One unique instrument × mic unit at a time: Steps 1–5 complete and the worksheet written before
the next unit starts. Never batch-research five units and write them all at once — batching is
where constraints drop and template values bleed in.

## Standalone EQ question mode

One worksheet, shown inline in the reply BEFORE the recommendation (no file needed). Real searches
listed, capsule fact + source, verdict word, gate check on any boost — then the recommendation in
console layout + the PDF. Worksheet-before-numbers is the parity.

## Scope

Process only, no knowledge — show-deep-build wins any conflict. If Brian says "skip the
worksheets" for a quick job, honor it; the master's own rules (research floor, question round,
pre-commit audit) still run regardless.
