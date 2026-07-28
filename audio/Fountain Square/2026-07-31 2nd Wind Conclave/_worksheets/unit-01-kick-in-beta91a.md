# Unit 01 — Kick in × Shure Beta 91A  (ch 1)

INSTRUMENT   Kick drum, inside the shell on the resonant-head pillow, aimed at the beater.
             R&B / funk dance set played to a click — the kick is the floor of the groove and
             has to punch through a plaza with 10,000 people on it. Half of a two-mic kick
             (ch 2 D6 outside).

MIC          Shure Beta 91A — half-cardioid boundary condenser, 48V required, no stand (lays
             in the drum). KB tendency: "solid boundary low end + pronounced beater click;
             nominally flat; picks up shell boxiness ~300–500 → ease off boom, tame box 400."
             **Switchable hardware — contour switch. ASSUMED FLAT (switch OUT).** The 400 Hz
             cut lives on the desk where I can ride it. Fallback if the switch is found
             engaged: halve the desk's 400 Hz cut, since the mic is already doing −7 there.
             Two-mic source — lane split with ch 2 below.

SEARCHES     1. `Shure Beta 91A kick drum EQ live sound frequency response contour switch
                site:prosoundweb.com`
             2. `Beta 91A frequency response boundary kick mic 3kHz presence peak dB measurement`
             3. Fetched recordinghacks.com/microphones/Shure/Beta-91A and
                mixonline.com Beta91A real-world review for the response detail.

CAPSULE FACT **Contour switch cuts 7 dB at 400 Hz** — Shure spec, quoted independently by
             RecordingHacks and the Mix Online review ("reduces 400 Hz by approximately 7 dB…
             produces a fuller low end and eliminates boxiness"). That is the manufacturer
             telling you where this capsule's problem is: 400 Hz box. Usable band 50 Hz–15 kHz.

WEB SAYS     PSW/Mix consensus: the 91A is the beater-attack mic in a two-mic kick, paired with
             a Beta 52 or D112 outside. vs the original Beta 91 it is "a little tighter in the
             low end, with a more pronounced and a more *balanced* high-end beater snap" —
             balanced, not hyped, which matters for the gate check below. Boundary loading
             gives real low end but also collects shell boxiness.

KB SAYS      mic-library: "Half-cardioid boundary kick/piano mic. Solid boundary low end +
             pronounced beater click; nominally flat (contour switch cuts 7dB@400 if engaged).
             Weakness: picks up shell boxiness ~300-500. → ease off boom; tame box ~400Hz."
             eq-starting-points: two-mic kick = Beta 52 body + Beta 91 attack, EQ'd differently.

VERDICT      **AGREE.** Same 7 dB @ 400 number on both sides, same box-at-400 diagnosis, same
             role in the two-mic pair. Nothing to take to the question round.

LOCKER       **Silent pass.** The Beta 91A is the locker's first call for the inside/attack
             layer of a two-mic kick (mic-library "Standard Combos": Beta 91 = attack/click,
             on head). No fork raised.

GENRE BEND   R&B/funk dance set: the kick wants weight and a defined thud, not a metal click.
             Beater definition is set for intelligibility through a big PA at distance, not for
             aggression — so the top lift stays modest. Artist layer: they play to a click with
             a programmed kick in the Track channel (ch 16), so the live kick has to occupy a
             slightly narrower lane than it would on a bandstand — that argues for owning the
             attack cleanly and letting the D6 and the track share the bottom.

VENUE BEND   FSQ, open plaza, no room gain, gusts to 16 mph. Box and mud cuts go to the outdoor
             depth (−6 to −9), not the indoor −4 to −5. HPF runs high on this mic because it is
             NOT the low-end owner — the D6 is.

DRAFT BANDS  (Q225 order: HPF · LPF · B4 → B3 → B2 → B1)
             HPF 60 · LPF 10000
             B4  +3 @ 3500  Q 1.5  BELL   beater definition
             B3  −8 @ 400   Q 2.0  BELL   shell box — the contour switch's own frequency
             B2  −6 @ 200   Q 1.8  BELL   low-mid de-stack from the D6 + outdoor mud
             B1  FLAT                     HPF owns the bottom limit here

GATE CHECK   **Boost audit — B4 +3 @ 3500.** What does the capsule bake in near 3.5 k? The Mix
             review's word is "balanced" — the 91A's snap is *present but not hyped* (that was
             the explicit improvement over the original 91). A +3 into a balanced region is a
             lift, not a stack. It passes. It stays at +3 rather than +5 precisely because the
             snap is already voiced in.
             **Two-mic lane split (with ch 2, Audix D6):**
             · TOP zone (3–6 k): **the 91A owns it.** It's inside on the head, closest to the
               beater, and it is the un-hyped one of the pair. The D6's baked +5 kHz click gets
               trimmed on ch 2 so the two don't stack.
             · BOTTOM zone (50–90 Hz): **the D6 owns it.** Its 63 Hz peak is baked in and it's
               the outside/port mic. The 91A is HPF'd at 60 and cut at 200 so it doesn't pile on.
             · Neither mic is boosted in the other's zone, top or bottom.
             · Sum in mono at soundcheck; if the pair is thinner than either alone, flip polarity
               on the D6 (the outside mic is the one to flip).

QUESTIONS    None.
