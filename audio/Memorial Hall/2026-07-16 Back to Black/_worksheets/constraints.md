# Constraint Card — Back to Black, Memo, 2026-07-16

Written after reading show-deep-build in full. Re-read before the question round and again
before spec.json.

## Numbers
- **Whole dB only.** No half-dB. Ever. Round up.
- **Cuts before boosts, always.** Find the problem, subtract it, before reaching for a boost.
- Typical cuts: **−4 to −7 dB, tight Q (1.5–2.0)**. Typical boosts: **+3 to +6 dB** on non-vocal.
- **Memo is INDOOR** — the FSQ/outdoor override (−6 to −9, up to −10) does NOT apply here.
  Indoor depth. Do not import FSQ aggression into this room.

## Vocals
- **Cuts only. Every genre. No exceptions.** This is feedback control, not taste.
  A vocal boost anywhere in this spec = failed build. Applies to Lead (16), BGV 1 (17), BGV 2 (18).
- Let the Beta 58A's own two presence peaks (~4k, ~10k) carry the top. Subtract, never add.

## Bands
- **No high shelf unless Brian asks.** He did not ask.
- Band order in all docs, high→low: **HPF → LPF → Band 4 (HF) → Band 3 → Band 2 → Band 1 (LF)**.
- **Band numbering matches the console: Band 1 = LF, Band 4 = HF.** Not the reverse.
- Q225: all 4 bands switchable Bell/Shelf; any Bell band can be Dynamic (DEQ). DEQ documented
  inline in the band row with Threshold/Ratio/Attack/Release.

## Safety
- **Royer R-121 on ch 12 = RIBBON. NO 48V. Flag in RED.** Non-negotiable. Destroys the ribbon.
- **TOUR / artist-provided gear is flagged ⚑ amber and NEVER swapped.** No locker suggestion
  against artist gear. Confirm at load-in.

## Memo (venue — final, heaviest filter)
- **Standing waves: 63 / 125 / 200 / 250–315 Hz.** Boosts in those zones are suspect;
  cuts favored. 125 Hz sits in the bass fundamental. Kick is the highest-risk channel here.
- RT60 ~1.6 s working. The room is already doing reverb work → pull factory decay 30–40%.
- **Crowd rig is FIXED (OM1 / Deity S2 / CM4) with LOCKED EQ — do not re-derive it.**
  → This show's list shows C422 pairs instead. That is a fork, not a licence to invent. ASK.

## Research
- **The KB is for longevity, not research.** No channel may be justified "KB only."
- Every unique instrument × mic unit gets a **fresh web pass, every show.** No familiar-mic
  exemption — SM57, Beta 58A, RNDI all get searched.
- A unit is not researched until I can state **≥1 quantitative capsule fact** (a frequency AND
  a dB value) with an **external source named**.
- **One-word verdict per unit: AGREE / DISAGREE / THIN.** Written before any numbers.
  No "broadly aligns" paraphrase. DISAGREE/THIN → question round with the (a)/(b)/(c) fork.

## Capsule gate
- Before ANY boost: state what the capsule already bakes in at/near that frequency.
  Boost inside a baked peak → the move is a trim or nothing.
- Reverse: don't deep-cut a zone the capsule already scooped.

## Two-mic sources (this show has TWO)
- **Bass: RNDI (9) + MD 421-U (10).** **Guitar: SM57 (11) + R-121 (12).**
- Treat each pair as ONE signal. Assign each mic ONE lane across the whole spectrum.
  **No boost on both mics in the same zone, top or bottom.** Back the complement's
  150–800 Hz off. Mono/polarity check planned. De-stack decisions in BOTH channels' mic_notes.

## Sections
- BGV 1 + BGV 2 are a section. If research says separate them, **the separation must be visible
  in the band values** — each owns a different lane, each eq_summary names its lane.
  Near-identical curves under a "slot them" note = failed build.

## Reverbs
- **Required.** 3 complementary vocal options + 1–2 instrument + 1 general when warranted.
- Seventh Heaven Pro preset names **verbatim** from the reverb KB.
- **Every settings value ANCHORED to factory:** "(factory)" when unchanged,
  "(from X factory)" when moved. Selection justified by THIS band's material.

## Pacing
- **Numbers never appear in the same message as the research that justifies them.**
  Research lands first, visibly. Numbers come later, drafted against what was found.

## Process
- **ONE batched question round** before any EQ commits. Carried flags go IN the round.
- Zero questions on a 20+ channel show = suspicious. Aim for few, sharp, genuinely-forked.
- Serialize: one unit at a time, worksheet written, before the next starts.
- Pre-commit audit with **evidence quoted** (channel numbers + values, never "verified").
