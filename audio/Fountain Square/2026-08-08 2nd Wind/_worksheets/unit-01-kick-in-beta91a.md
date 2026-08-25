# Unit 01 — Kick drum (inside) × Shure Beta 91A · CH 1

INSTRUMENT   Kick drum, inside the shell on the boundary. R&B/funk dance set played to a click —
             steady four-on-the-floor and syncopated funk patterns, foot is consistent and the
             drummer is playing to tracks, so the kick is a metronomic anchor rather than a
             dynamic feature. Role in THIS mix: the floor of a dance-floor low end on a plaza
             with zero room gain. It has to arrive as *attack you can hear at the back* plus
             *weight you feel up front* — and those two jobs are split across two mics.

MIC          Shure Beta 91A. Half-cardioid boundary condenser, 20 Hz–20 kHz, 155 dB max SPL,
             −48.5 dBV/Pa. Requires 48V (already ticked on the band's list — the only cell they
             filled in). **Two-mic source with CH 2 (Beta 52A).**
             SWITCH STATE: the 91A carries a two-step contour switch centred on 400 Hz.
             **Assumed FLAT.** Fallback written into mic_notes: if the low-mid scoop is engaged
             the capsule is already doing −7 dB at 400, so the desk's B3 cut HALVES to −4.

SEARCHES     1. `Shure Beta 91A kick drum inside EQ live sound frequency response boundary
                condenser contour switch 400Hz`
             2. `Beta 91A kick mic review frequency response peak dB presence 3kHz 5kHz
                specification`

CAPSULE FACT **Emphasis from 4 kHz to ~9 kHz with a presence boost around 7 kHz** for attack
             definition, and the **contour switch attenuates 400 Hz by 7 dB** when engaged
             (Shure product page + Gear4Music spec write-up; RecordingHacks confirms the
             response-curve switch figure at ~−7 dB @ 400 Hz). Mix Online's real-world review
             adds that the 91A is tighter in the low end than the original 91 with a more
             pronounced, better-balanced beater snap, and runs ~10 dB hotter.

WEB SAYS     The attack region is BUILT IN — Shure voiced 4–9 k specifically so the beater
             reads without desk help, and the 400 Hz switch exists because that is the cut
             engineers reach for anyway. Live-sound consensus is that the 91A gets a bigger,
             bolder kick through a crowded mix with *less* EQ than a dynamic needs.

KB SAYS      mic-library: "Half-cardioid boundary kick/piano mic. Solid boundary low end +
             pronounced beater click; nominally flat (contour switch cuts 7 dB @ 400 if
             engaged). Weakness: picks up shell boxiness ~300–500." Bias: ease off boom, tame
             box ~400 Hz.

VERDICT      **AGREE.** Both sides name the same two numbers: the 400 Hz problem (web: switch
             attenuates 7 dB there; KB: box 300–500, tame ~400) and the baked high-frequency
             attack (web: 4–9 k emphasis + 7 k presence; KB: pronounced beater click). No
             disagreement to resolve, and the baseline is externally sourced rather than
             KB-only.

LOCKER       First-call match — silent pass. mic-library lists the Beta 91 as "Kick — attack
             layer inside on head; **pair with Beta 52**", which is exactly this week's pairing.
             No fork raised.

GENRE BEND   R&B/funk/soul dance set: the kick is the pulse, so weight and attack both matter
             more than "natural." No change to the box cut (that's a capsule/room issue, not a
             genre one). Artist layer: they play to a click with tracks underneath, so there is
             a *programmed* low end in the Track channel that this kick has to sit beside
             without fighting — which is another reason ch 1 stays out of the sub region and
             lets ch 2 own it deliberately rather than by accident.

VENUE BEND   FSQ outdoor, no room gain. Box/mud cuts run DEEPER than indoor — −8 at 400 rather
             than a polite −5. Weather layer (92.9 °F / 38 % RH at downbeat, dry the whole set):
             dry air absorbs HF over the throw, so the 4–9 k attack the capsule bakes in is
             *needed* at the back of the plaza and must not be trimmed. That combination —
             don't boost it (baked) and don't cut it (air is already eating it) — is why B4
             lands FLAT.

DRAFT BANDS  Q225 layout, whole dB, cuts first:
             HPF 70 · LPF 10000
             B4  FLAT
             B3  −8 | 400 | 2.0 | BELL
             B2  −6 | 200 | 1.8 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.** This is a deliberate change from
             the 2026-07-31 rev, which carried +3 @ 3500. That boost fails the capsule gate: a
             Q1.5 bell at 3500 reaches straight into the 4–9 kHz region Shure already emphasises
             plus the 7 kHz presence peak, so it stacks on voiced response. The correct move
             there is nothing, and the dry-air read independently says don't trim it either.
             B1 FLAT and HPF 70 are the LOW-lane half of the two-mic split.

TWO-MIC LANES (CH 1 × CH 2 — assigned across the whole spectrum, top AND bottom)
             CH 1 (91A, inside)  owns **ATTACK / TOP** — the baked 4–9 k beater snap, delivered
                                 by the capsule with no desk boost. Low end handed off: HPF 70,
                                 B1 flat, no sub boost anywhere.
             CH 2 (52A, outside) owns **BODY / THUMP / BOTTOM** — the low reach and the port
                                 bloom. Its own presence region gets trimmed, not boosted, so it
                                 does not stack on ch 1's baked top.
             Shared zones named: both mics see 400 Hz shell box (only ch 1 cuts it hard — ch 2's
             capsule already scoops there, see unit 02) and both see the 60–100 Hz region (only
             ch 2 carries it). No boost appears on both channels in either zone.
             Polarity: check the pair in mono at soundcheck; an outside mic on the port is a
             different distance from the beater and can arrive out of phase.

QUESTIONS    None. The contour-switch position is an explicit stated assumption with a written
             fallback, not an open question.

TRACE        base(kick inside on a boundary condenser — 400 Hz shell box is the primary target,
             Shure/Gear4Music 4–9 k emphasis + 7 k presence means attack is baked) ·
             equip(no drum sizes or heads notated — generic kick carries; no rig-driven bend) ·
             genre(R&B/funk dance pulse — weight and attack both matter, box cut unchanged) ·
             artist(plays to a click with programmed low end in the Track channel — ch 1 stays
             out of the sub region so it doesn't fight it) ·
             venue(FSQ outdoor + 38 % RH: box cut deepened to −8, and B4 left FLAT because dry
             air is already eating the top the capsule bakes in)
