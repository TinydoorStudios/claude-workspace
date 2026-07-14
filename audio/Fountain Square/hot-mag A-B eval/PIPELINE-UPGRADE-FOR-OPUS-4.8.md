# PIPELINE UPGRADE — process this file with Opus 4.8

> **STATUS: APPLIED 2026-07-09.** All 11 edits were folded into the pipeline during the same-day
> skill consolidation (eq-advisor merged into show-deep-build — one skill; the anchors below now
> live in `_skills/show-deep-build/SKILL.md` Part II, `_system/NEW-SHOW.md`, and the KB
> `show-processing-pipeline.md` "Deep-build quality floor" section). Do NOT re-apply this file —
> the anchor lines it names no longer exist. Kept for the context section and the acceptance test:
> the next deep build is the live test, judged against `hot-mag 3/The_Hot_Magnolias.spec.json`.


You are updating Brian Lloyd's show-build pipeline so that every future deep build behaves the way the Fable 5 reference run did (`Fountain Square/hot-mag 3/`). This file contains exact edits. Make them precisely, then run the verification checklist at the end. Do not improvise beyond what's written here — if an anchor line can't be found, stop and tell Brian instead of guessing.

## Context — why these edits exist

An A/B test (2026-07-08, The Hot Magnolias, FSQ) ran the identical deep build twice: Opus 4.8 High (`hot-mag 2`) and Fable 5 High (`hot-mag 3`). Full analysis: `Fountain Square/hot-mag A-B eval/Hot Magnolias A-B Eval - Opus 4.8 vs Fable 5.pdf`. The Fable run was stronger in five specific, enforceable behaviors:

1. It web-researched EVERY instrument × mic unit with a named source and a quantitative capsule fact — including "familiar" mics. The Opus run researched 3 of 11 units and leaned on the KB for the rest, which produced a +2 @ 5k boost on an Audix i5 that already bakes in +9 dB @ 5.5k.
2. It checked what each capsule already bakes in before boosting, and de-stacked two-mic sources (trimmed the D6's baked 5k click so it couldn't stack on the 91A's attack boost; no doubled low boost across the kick pair).
3. It executed the principles its research stated. The Opus run's research said "frequency-slot the three horns," then wrote three nearly identical horn EQs. The Fable run assigned each horn a lane and the band values actually differ.
4. It fetched the real show-day forecast instead of assuming seasonal weather. The Opus run assumed "warm/dry July air" when the actual forecast was 74% RH — the opposite HF conclusion.
5. It anchored outputs to verifiable references: reverb values tied to factory presets, the 91A contour-switch state flagged with a fallback, compressor notes with numbers instead of adjectives.

Each edit below converts one of those behaviors into pipeline text so the behavior no longer depends on which model runs it.

## Files you will edit

| # | File | Role |
|---|---|---|
| 1 | `~/Documents/Claude/audio/_skills/eq-advisor/SKILL.md` | The EQ brain — most edits land here |
| 2 | `~/Documents/Claude/audio/_skills/show-deep-build/SKILL.md` | The show orchestrator |
| 3 | `~/Documents/Claude/audio/_system/NEW-SHOW.md` | The deterministic show flow |
| 4 | `~/Documents/Claude/audio/Live Sound KB/Wiki/show-processing-pipeline.md` | KB pipeline article |

Note: `_skills/` holds the editable source of both skills. If the installed plugin copies (eq-advisor / show-deep-build plugins) are built from these files, remind Brian at the end to reinstall/refresh the plugins so live sessions pick up the changes — installed skill caches are read-only and do not update themselves.

---

## EDIT 1 — eq-advisor: the research floor (KB is NEVER a research source)

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** the numbered item in Step 3 that begins `1. **Search the live-sound community first.**`
**Action:** immediately after that numbered item's paragraph (before item `2. **Then cross-check against the KB.**`), insert:

```
   **The research floor (Brian's guardrail, 2026-07-08, from the hot-mag A/B): the KB is for
   longevity, not research.** The KB is where verified knowledge is ARCHIVED so it survives
   between sessions — it is never the research source for a build. No model, on any channel, may
   justify a value with "KB only." Every unique instrument × mic unit gets its own fresh web pass,
   every show — there is no "familiar mic" exemption. An SM57, a Beta 58A, an i5, a D6 all get
   searched. A unit is not researched until the summary can state at least one QUANTITATIVE
   capsule fact for it — a frequency and a dB value (a baked peak, a scoop, a roll-off point) —
   with an EXTERNAL source named. The KB's role in a build is exactly two things: (1) the
   cross-check that verifies the web findings, with any disagreement a stop-and-ask, and (2) the
   destination for the post-show harvest. The research_summary in a show spec must name the
   external source per unit, the way the hot-mag 3 reference does ("SOS/Gearspace i5 (+9 dB @
   5.5k baked peak)"), and must close with an explicit reconciliation line: either "no web↔KB
   disagreements" or the list of them.
```

## EDIT 1b — eq-advisor: close the "KB is authoritative" loophole

This is the specific sentence that let the Opus run skip research on familiar mics.

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** in Step 3, numbered item 2, the sentence: `The KB is Brian's verified operational knowledge — when it speaks to the source, it's authoritative.`
**Action:** replace that sentence with:

```
The KB is Brian's verified operational knowledge — authoritative for RESOLVING a conflict or
confirming a web finding, never a substitute for the web pass itself. "The KB already covers this
mic" is not a reason to skip the search; it's the reason the cross-check will be strong.
```

**Also in the same file:** find the description-block phrase and the Step 3 heading language `web-then-KB verification workflow` / `web first, KB second, reconcile` — leave those (they're correct), but scan the whole file for any other sentence that could be read as "KB is sufficient" and tighten it to match the guardrail. Report each instance you change.

## EDIT 1c — eq-advisor: surface KB differences to Brian, with the update offered inline

Brian's rule (2026-07-08): keep checking with him whenever the research differs from what the KB
says, and give him the option to update the KB right there — not just a log entry after the fact.

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** in the `## Stop-and-ask protocol` section, the paragraph beginning `When you stop: state what you know, cite the sources, lay out the fork...`
**Action:** append to that paragraph:

```
When the fork is a web↔KB difference, the question always carries three explicit options: (a) go
with the research, (b) go with the KB, (c) go with the research AND update the KB entry to match.
If Brian picks (a) without (c), note the standing difference in the channel's mic_notes so it
resurfaces next time instead of silently persisting. And this isn't only for conflicts: when the
fresh research surfaces something concretely better than the current KB entry — a more precise
frequency, a baked-peak fact the KB doesn't have, a technique note — say so in the question round
and offer the KB update as an option there too. Brian's answer is ground truth either way; an
accepted update goes through the normal staged write-back (never silently to the live wiki).
```

## EDIT 2 — eq-advisor: the capsule-voicing gate (trim baked peaks, don't boost over them)

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** in Step 3, the sentence `Output of this step: a baseline set of moves...`
**Action:** insert immediately BEFORE that sentence:

```
**The capsule-voicing gate (added 2026-07-08):** before writing ANY boost, state what the capsule
already bakes in at or near that frequency. If the boost lands inside a baked peak, the correct
move is a trim or nothing — never a boost stacked on a voiced peak (the i5 bakes in +9 dB @ 5.5k;
the desk's job there is −3, not +2). The same gate applies in reverse: don't deep-cut a zone the
capsule already scooped (the D6's −15 dB @ 600 means the desk cut nearby is light or absent).
Every boost in the final spec must survive this gate, and the channel's mic_notes must show the
baked-in fact that justified it.
```

## EDIT 3 — eq-advisor: two-mic de-stacking (full-spectrum, not just low-mids)

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** in Step 2, the bullet that begins `- **Two-mic blend** (SM57/R-121 AxeMount, 57/27, 57/421)`
**Action:** replace that entire bullet with:

```
- **Two-mic source** (kick in/out, SM57/R-121 AxeMount, 57/27, 57/421, close+room) → treat the
  pair as one signal AND assign each mic ONE lane across the whole spectrum. Name the shared
  frequency zones (both mics' baked peaks and both mics' low ranges), then split ownership: one
  mic owns the attack/top zone, one owns the body/low zone — no boost on both mics in the same
  zone, top or bottom (a +3 low boost on the inside kick mic stacked on a +3 low boost on the
  outside mic is the classic failure). If one mic bakes in a peak the other mic is being boosted
  at, trim the baked one. Back the complement mic's low-mids (150–800 Hz) off so it doesn't stack;
  plan a mono/polarity check. The de-stack decisions go in both channels' mic_notes.
```

## EDIT 4 — eq-advisor: section slotting must be executed, not stated

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** end of Step 4 (after the paragraph ending `...it flips the whole aggressiveness scale.`)
**Action:** append as a new paragraph in Step 4:

```
**Sections get slotted in the numbers, not the prose (added 2026-07-08).** When a show has a
section — a horn line, multiple backing vocals, twin guitars — and the research says to separate
them, the separation must be visible in the band values: each member's EQ must differ in the lane
it owns, and each channel's eq_summary must name that lane ("bone owns ~1k, so its cut sits at
600"). Three near-identical curves under a research note that says "slot the horns" is a failed
build. Before writing the spec, re-read every sectional principle in your own research summary
and audit the numbers against it — if a stated principle isn't traceable in the values, fix the
values or drop the claim.
```

## EDIT 5 — eq-advisor: hardware-state flags

**File:** `_skills/eq-advisor/SKILL.md`
**Anchor:** in Step 2, after the ribbon-mic bullet (`- **Ribbon mic** ... Non-negotiable.`) and after the two-mic bullet replaced in EDIT 3.
**Action:** add a third bullet:

```
- **Switchable hardware** (contour switches — Beta 91A; pads; selectable HF caps — B3; sensitivity
  switches) → state the assumed switch position, build the EQ for that assumption, and write the
  fallback into mic_notes ("contour assumed FLAT — the 400 Hz cut lives on the desk; if the switch
  is engaged, halve the desk cut"). Never leave a switch state implicit.
```

## EDIT 6 — show-deep-build: weather is fetched, never assumed (and both humidity cases)

**File:** `_skills/show-deep-build/SKILL.md`
**Anchor:** the Step 4 paragraph beginning `**Outdoor shows: pull the show-time weather.**`
**Action:** replace that entire paragraph with:

```
**Outdoor shows: pull the show-time weather — fetched, never assumed.** For FSQ / WP / ESP / CSP /
ZP / IA, fetch the forecast for the actual show window (Open-Meteo; the Tempest stations for
current conditions) and put the numbers in the research_summary (temp, RH, wind, rain risk, with
the source named). Seasonal priors are banned — "July = warm and dry" is exactly the assumption
the 2026-07-08 A/B caught being wrong (actual forecast: 74% RH). Apply the real numbers: wind →
windscreen/mic-choice flags and open-mic wash; hot + DRY → extra HF air loss over distance
(protect presence, don't over-cut the top); hot + HUMID → HF carries slightly better (protect
presence, don't over-boost it); rain risk → note the contingency. Fold it into `room_context` so
the why is on paper. Indoor venues skip this.
```

## EDIT 7 — show-deep-build: reverb factory anchoring + genre-fit selection

**File:** `_skills/show-deep-build/SKILL.md`
**Anchor:** in Step 5, inside the parenthetical describing the required `reverbs` list — after the phrase `Seventh Heaven Pro presets verbatim from the reverb KB, each with `settings`, `plugin_eq` (the in-plugin moves), and `why`;`
**Action:** extend that requirement so the sentence continues:

```
every settings value ANCHORED to the preset's factory value — write "(factory)" when unchanged
and "(from X factory)" when moved, so at the desk it's obvious which knobs to touch; and preset
SELECTION justified by this band's material (a second-line band earns a snare splash; a ballad
earns the big-moment chamber) rather than the generic default trio;
```

## EDIT 8 — show-deep-build: the question round resolves carried flags

**File:** `_skills/show-deep-build/SKILL.md`
**Anchor:** the Step 3 paragraph beginning `**One question round (Brian, 2026-07-05).**`
**Action:** append to the end of that paragraph:

```
Carried flags count as questions: any open FLAG inherited from a prior rev or run (a mic-choice
flag, a mono/stereo question, an unassigned vocal) goes INTO the round and comes out either as a
recorded decision or as an explicitly renewed flag Brian chose to keep open. A build that ships
the same FLAG two revs in a row without asking is a failed question round.
```

## EDIT 9 — show-deep-build: numeric dynamics and sourced notes

**File:** `_skills/show-deep-build/SKILL.md`
**Anchor:** the `## Defaults / guardrails` section, after the line `- Whole-dB, cuts-first, no high-shelf band unless asked. ...`
**Action:** add two guardrail bullets:

```
- Dynamics notes carry numbers, not adjectives: "fast-attack comp" is incomplete — write the
  range and ratio ("10–20 ms, 3:1"). Gate philosophy states what must survive ("ghost notes and
  press rolls must live"), tied to the genre.
- Per-channel mic_notes cite their source inline ("SOS/Gearspace + KB agree: ..."), and every
  eq_summary connects the moves to the channel's musical role in THIS band, not a generic
  description. Stands and mounts are chosen for the physical mic (an e609 has no clip mount —
  a hat needs a boom; a kick-port or cab mic takes a Short stand).
```

## EDIT 10 — NEW-SHOW.md: sync the don't-forget rules

**File:** `_system/NEW-SHOW.md`
**Anchor:** the `## Don't-forget rules` section.
**Action:** add these rules to the list:

```
- THE KB IS FOR LONGEVITY, NOT RESEARCH (Brian, 2026-07-08). No model may source an EQ value from
  the KB — every instrument × mic unit gets a fresh web pass with a named external source and a
  quantitative capsule fact, no familiar-mic exemption. The KB's only build-time job is the
  cross-check (disagreement = stop-and-ask); its other job is receiving the post-show harvest.
- Capsule-voicing gate: never boost into a baked peak; trim it. Two-mic sources get full-spectrum
  lane ownership (no stacked boosts top or bottom).
- Sections (horns, BVs, twin guitars) are slotted in the band values, with each channel's lane
  named — a stated principle must be traceable in the numbers.
- Outdoor weather is FETCHED for the show window and quoted with numbers — seasonal assumptions
  are banned. Humid ≠ dry: hot+dry = protect presence from air loss; hot+humid = HF carries
  slightly better, don't over-boost it.
- Reverb settings anchor to factory values ("(factory)" / "(from X factory)"); presets picked for
  this band's material. Switchable hardware (contour, pads, caps) gets an assumed state + fallback.
- The question round consumes carried flags — a FLAG that survives two revs unasked is a failure.
```

**Also:** in the same file, Step 4 item 3 (the long EQ paragraph), after the sentence `Outdoor venues: pull the show-window weather into the room context.` append: `— fetched with real numbers, never assumed from the season.`

## EDIT 11 — KB article: show-processing-pipeline.md

**File:** `Live Sound KB/Wiki/show-processing-pipeline.md`
**Action:** add a short dated section (match the article's existing heading style) titled `Deep-build quality floor (2026-07-08, from the hot-mag A/B)` summarizing the five behaviors in one line each: per-unit sourced research with quantitative capsule facts; capsule-voicing gate on boosts; full-spectrum de-stacking on two-mic sources; sectional slotting executed in the values; fetched weather, factory-anchored reverbs, numeric dynamics, resolved flags. Cross-reference the eval: `Fountain Square/hot-mag A-B eval/`. Bump the article's `Last updated` date. Do NOT rewrite the rest of the article.

---

## After the edits — verification checklist (run all of it)

1. Re-read each edited section in full and confirm the inserted text reads as one voice with the surrounding file (Brian's writing rules: direct, specific, no corporate filler, no banned phrases).
2. Confirm no edit contradicts a locked rule: instrument → mic → genre → venue order (2026-07-05), one batched question round (2026-07-05), FSQ deeper cuts (2026-07-08), fresh web pass every show (2026-07-05), whole-dB, cuts-first, no high shelf, vocals cuts-only, stage plots band-provided, reverbs required every show.
3. Grep both SKILL.md files for the strings `research floor`, `capsule-voicing gate`, `lane`, `factory`, `carried flags` and confirm each appears where the edits placed it.
4. Update `_system/IMPROVEMENTS.md` with a dated entry: what changed, why (hot-mag A/B), files touched.
5. Update `Live Sound KB/CHANGELOG.md` for the KB article edit.
6. Append a session-history line to `about-me/memory.md`.
7. Tell Brian: (a) which files changed, (b) that installed plugin copies of eq-advisor / show-deep-build need a reinstall/refresh if they're built from `_skills/`, and (c) that the next show build is the live test — compare its research_summary against `hot-mag 3/The_Hot_Magnolias.spec.json` as the reference standard.

## The acceptance test

The upgrade worked if the next Opus-run deep build produces, without being prompted per-item: a research_summary naming an EXTERNAL source per unit with at least one frequency+dB fact each and a reconciliation line — zero units justified by "KB only"; zero boosts inside baked capsule peaks; lane-owned two-mic pairs; sectional EQs that actually differ per the stated slotting; a quoted forecast with numbers on any outdoor show; factory-anchored reverb settings; numeric comp/gate notes; and a decisions list with no unconsumed carried flags. That is exactly the checklist `hot-mag 3` passes and `hot-mag 2` fails.
