# Unit 09 — Bass DI × Whirlwind IMP  (ch 11)

INSTRUMENT   Electric bass, R&B/neo-soul covers. Instrument, strings and rig all unknown (no
             rider). Role: the most important instrument in the band after the vocal — R&B
             lives on the pocket between the kick and the bass, and the bass has to be *round*
             and audible without eating the vocal's chest.
MIC          None — **Whirlwind IMP passive DI. Locker fork EXEMPT.**
SEARCHES     "Whirlwind IMP 2 passive DI bass guitar tone transformer high frequency loss review live"
             → sweetwater.com IMP 2 product + reviews, fullcompass.com IMP2 (TRHL transformer),
               bhphotovideo.com IMP 2, homestudioexpert.com IMP 2 review
CAPSULE FACT No capsule. Device fact: **frequency response 20 Hz–20 kHz ±1 dB, impedance ratio
             133:1, level change −20 dB, Whirlwind TRHL transformer, passive (no power).**
             Source: Whirlwind IMP 2 published specification via Sweetwater / Full Compass.
WEB SAYS     Honest and uncoloured within ±1 dB across the whole band — there is nothing to
             ease off and nothing to compensate for. The practical live notes are the −20 dB
             insertion loss (the Q225 head amp works harder than it would on an active DI) and
             the ground-lift switch, which is the first thing to reach for if the stage hums.
KB SAYS      mic-library DI row: "Passive DI, neutral/honest, reliable. Bass/keys direct.
             Weakness: passive = slight HF/level loss into low-Z." Tendency: "apply template
             as-is (flat/honest)."
VERDICT      **AGREE** — ±1 dB flat from the manufacturer, "neutral/honest" from the KB, and
             both name the same passive level-loss caveat.
LOCKER       Exempt — DI input.
GENRE BEND   R&B/neo-soul bass wants roundness and note definition, not grind. The community
             guidance for the genre is explicit that low-mid warmth is a feature, so the mud cut
             on this channel is a lane-separation move rather than a scrub.
VENUE BEND   FSQ: HPF 45 (the KS21 arch owns everything below), and the 300 Hz cut runs at
             outdoor depth because that is where the DI and the cab mic pile on each other.
DRAFT BANDS  HPF 45 · LPF 12000
             B4  FLAT
             B3  +3 | 800 | 1.8 | BELL
             B2  −7 | 300 | 2   | BELL
             B1  FLAT
GATE CHECK   One boost: **B3 +3 @ 800.** Permitted because the IMP is specified flat to ±1 dB
             across 20 Hz–20 kHz — there is no baked feature anywhere on this signal path to
             stack onto, which is the cleanest possible pass of the capsule gate. 800 Hz is
             where a bass's note actually speaks, and it is the one lane this channel owns.
             **Two-mic (DI + cab) lane split with unit 10 — driven by the PG52's measured curve,
             not by convention.** The PG52 humps at ~80 Hz and dips broadly through 200–800 Hz,
             so the conventional "DI for clean low, mic for mids" split is backwards for this
             pair. Instead: **unit 10 owns the 60–100 Hz cab thump** (its baked hump), and
             **this channel owns the note definition at 800 Hz and everything above.**
             That is why B1 is FLAT here — the DI's fundamental passes through unboosted rather
             than stacking on the PG52's hump — and why unit 10 is cut at 900 Hz, out of this
             channel's lane.
QUESTIONS    Is the IMP taking the instrument directly, or a post-amp DI/line out of the bass
             rig? Build assumes **pre-amp, straight off the instrument**. If it is a post-amp
             send the amp's own voicing is already on it and the +3 @ 800 comes out.
TRACE        base(Whirlwind IMP — passive, 20 Hz–20 kHz ±1 dB, 133:1, −20 dB, Whirlwind spec) ·
             equip(bass, strings and rig unknown, no rider — nothing invented) ·
             genre(R&B/neo-soul — roundness and note definition; the 800 Hz lift is the genre
             move) · artist(no change) ·
             venue(FSQ — HPF 45 because the KS21 arch owns below it; 300 cut at outdoor depth
             where DI and cab stack)
