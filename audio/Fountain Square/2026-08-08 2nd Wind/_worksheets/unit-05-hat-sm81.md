# Unit 05 — Hi-hat × Shure SM81 · CH 5

INSTRUMENT   Hi-hat. In funk and R&B this is not a garnish — sixteenth-note patterns, open/closed
             accents and the foot pedal are a primary rhythmic voice, and on a Motown/Top-40 dance
             set the hat carries the groove's top layer. Role in THIS mix: crisp, forward, and
             separated from the two other cymbal mics on the same kit.
             **Mic changed this week** — rev 1 had the ND408 here, which changes this channel
             materially (see gate check).

MIC          Shure SM81. Cardioid SDC, 20 Hz–20 kHz, requires 48V. **One of THREE SM81s on this
             kit** (hat 5, ride 14, toys 19) — Brian confirmed 2026-08-08 he owns three; the KB
             row lacked a quantity marker and is being corrected.
             SWITCH STATE: three-position low-cut (flat / 6 dB-oct below 100 Hz / 18 dB-oct below
             80 Hz) plus a lockable −10 dB pad. **Assumed: 18 dB/oct low-cut ENGAGED, pad OUT.**
             The KB's own note is "use the onboard HPF before the desk filter," and on an outdoor
             stage with 15–16 mph gusts that filter is doing real work upstream of the preamp.
             Fallback in mic_notes: if the switch is left flat, the desk HPF carries alone and
             there is more low rumble to ride.

SEARCHES     1. `Shure SM81 hi-hat live sound EQ HPF settings cymbal wash flat response 18dB
                octave`
             2. (placement/slotting cross-check) Signaturesound, *Mic Positioning: Cymbals and
                Overheads*; DrumNinja hi-hat mic round-up

CAPSULE FACT **Flat 20 Hz–20 kHz with no presence peak and no hyped top end** — reviewers state it
             explicitly: "no presence peak, no hyped top-end, no coloration… the brightness you
             get on playback is the brightness of the cymbal, not an artifact of the microphone"
             (SoundRef SM81 review; Shure product page). The switchable low-cut is quantified:
             **flat / −6 dB per octave below 100 Hz / −18 dB per octave below 80 Hz**, plus a
             lockable **−10 dB pad** (Thomann/Shure specs, Gearspace user review).

WEB SAYS     The SM81 is the mic engineers pick for hat and cymbals *because* it adds nothing —
             it captures detailed high end without harshness or brittleness. The corollary, which
             matters for this build: a flat capsule means **the template lands straight**. There is
             no baked peak to trim and no baked scoop to avoid, so every move on this channel is
             mine and every move is load-bearing.

KB SAYS      mic-library: "Ruler-flat SDC, clean detailed highs with no harsh fizz, flat/6/18 dB
             HPF. Accurate on hat/OH/acoustic — takes EQ well. Weakness: needs care on cymbal
             wash, no built-in flattery." Bias: **apply template as-is (flat/honest)**.

VERDICT      **AGREE.** Web ("no presence peak, no hyped top-end") and KB ("ruler-flat… no
             built-in flattery") are the same claim, and both flag the same weakness — cymbal
             wash needs managing because nothing is being politely rolled off for you.

LOCKER       Silent pass. mic-library lists the SM81 for "Overheads, **hi-hat**, acoustic
             instruments" — it is a first-call match for this source. The availability conflict
             that would have forced a fork (three channels, one mic in the KB) was resolved in the
             round: Brian has three, so the M1280BHC alternative is withdrawn and no fork stands.

GENRE BEND   Funk/R&B: the hat needs to sizzle and sit forward, and the 8–12 kHz band is where
             that lives. Because the capsule is flat, this is one of the very few places on this
             show where a genre-driven BOOST survives the gate. Artist layer: rehearsed show band
             to a click — hat patterns are tight and repeatable, so a decisive high lift won't
             turn inconsistent hits into a problem.

VENUE BEND   FSQ outdoor. Box/bleed cut runs FSQ-deep at −7 @ 400 (a hat mic's worst bleed problem
             is the snare sitting 200–400 Hz behind it). HPF runs HIGH at 250 — nothing musical on
             a hat lives below that, and 15–16 mph gusts all evening make a high filter free
             insurance. Weather layer: 38 % RH and dry the whole set means HF genuinely does not
             survive the throw, which is what turns the 10 kHz lift from optional to worth having.
             LPF at 16 kHz is wash management, not tone — this kit has three cymbal mics plus a
             stereo overhead pair all summing.

DRAFT BANDS  HPF 250 · LPF 16000
             B4  +3 | 10000 | 1.5 | BELL
             B3  −6 |  4000 | 2.0 | BELL
             B2  −7 |   400 | 2.0 | BELL
             B1  FLAT

GATE CHECK   **One boost: B4 +3 @ 10000. The fact that permits it —** the SM81 is documented flat
             across 20 Hz–20 kHz with **no presence peak and no hyped top end** (SoundRef, Shure).
             There is no baked peak anywhere near 10 kHz to stack on, which is precisely why the
             KB's bias line for this mic is "apply template as-is." Compare rev 1, where this
             channel was an ND408 whose −6 @ 4500 was load-bearing *because* the 408 has a
             presence rise exactly where hat clank lives — that cut was fixing the capsule. Here
             the −6 @ 4000 is fixing the CYMBAL, not the mic, and it moved to 4000 to slot against
             the other two cymbal channels rather than to chase a capsule artifact.
             - B2 −7 @ 400 is snare bleed and stand rumble; the flat capsule does nothing about it.
             - B1 FLAT: a hat has no low content worth keeping, and the onboard 18 dB/oct filter
               has already removed what the desk HPF doesn't.

CYMBAL SLOTTING (three cymbal mics + a stereo OH pair on ONE kit — the sectional rule applies)
             CH 5  Hat        owns **HIGH SIZZLE ~10 k** (+3) · cuts 4000
             CH 14 Ride       owns **BELL / STICK DEFINITION**, cut placed at 3000, not 4000
             CH 9  Overheads  own **WASH + AIR** as the primary cymbal picture
             No two of the three share a cut frequency, and only the hat carries a high boost —
             three flat-ish condensers all lifted at 10 k would stack into hiss on a plaza.

QUESTIONS    None. Availability resolved in the round; switch state is a stated assumption with a
             written fallback.

TRACE        base(hi-hat on a ruler-flat SDC — template lands straight, no capsule artifact to
             chase; SoundRef/Shure confirm no presence peak, flat 20 Hz–20 kHz) ·
             equip(no cymbal sizes notated; onboard 18 dB/oct low-cut assumed engaged per the KB's
             use-it-before-the-desk note) ·
             genre(funk/R&B sixteenths — hat is a primary rhythmic voice, so the 10 k sizzle lift
             is genre-driven and survives the gate because the capsule is flat) ·
             artist(tight rehearsed patterns to a click — a decisive lift is safe) ·
             venue(FSQ outdoor: bleed cut deepened to −7 @ 400, HPF up at 250 for 15–16 mph gusts,
             LPF 16 k for wash; 38 % RH dry air is what makes the 10 k lift worth having)
