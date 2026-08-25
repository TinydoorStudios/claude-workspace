# Unit 09 — Drum overheads × Shure Beta 27 pair · CH 9 (STEREO fader)

INSTRUMENT   Drum overhead pair. On this show the overheads are the **primary cymbal picture** —
             the ride and hat mics reinforce them rather than replace them (externally supported;
             see unit 13). They also carry the kit's glue: the sense that a drummer is playing one
             instrument rather than eight channels. Role in THIS mix on a plaza: air and cymbal
             wash, with everything below the cymbals filtered away.

MIC          Shure Beta 27 × 2. Side-address supercardioid LDC, requires 48V, **on the STEREO
             fader 9** — both mics, one fader. **Never split across 9/10; fader 10 is the SNARE
             PL8 reverb return and is hard-protected by the patcher.** The band's list had OH L on
             9 and OH R on 10, which is the collapse this reconciliation handles.
             SWITCH STATE: −15 dB attenuator and a 3-position low-frequency filter.
             **Assumed: pad OUT, LF filter ENGAGED.** Overheads sit ~1 m off the cymbals rather
             than inside a drum, so the SPL doesn't demand the pad, and a Q225 wants −25 to
             −20 dBFS at the input — padding 15 dB off would cost gain structure. The LF filter is
             engaged because kick and tom bleed from below is this position's main problem.
             Fallback in mic_notes: if the pad is found engaged, expect ~15 dB more preamp and
             re-check gain before ringing out.

SEARCHES     1. `Shure Beta 27 drum overheads pair live EQ supercardioid flat 60Hz-3kHz +2dB
                5.5kHz 9kHz pad`
             2. Shure Beta 27 product page + user guide (switch complement, stated applications)

CAPSULE FACT **Nominally flat from ~60 Hz to 3 kHz with two small HF peaks of +2 dB or less at
             5500 Hz and 9 kHz**, plus a **−15 dB switchable attenuator** and a 3-position
             low-frequency filter (RecordingHacks Beta 27 profile; Shure product page and user
             guide). Shure explicitly names **"drum and percussion overheads"** as an optimal
             application for it.

WEB SAYS     The supercardioid pattern and off-axis rejection are the selling points for live
             reinforcement, which is what makes this a defensible overhead choice outdoors where a
             wide pattern would just collect plaza noise and PA wash. The response is genuinely
             flat where it matters and the HF peaks are SMALL — +2 dB, not the +6 to +9 dB peaks
             the dynamics on this kit carry. That single number changes this channel from rev 1.

KB SAYS      mic-library: "Supercardioid LDC, flat 60 Hz–3 kHz, small peaks +2 dB at 5.5 k and 9 k,
             −15 dB pad, flatter than SM57. Open, clean cab/instrument mic. Weakness: slight 9 k
             fizz on bright amps." Bias: ease off box, honk; tame harsh ~9000 Hz.

VERDICT      **AGREE.** Web and KB carry the identical numbers — flat 60 Hz–3 kHz, +2 dB peaks at
             5.5 k and 9 k, −15 dB pad. No conflict.

LOCKER       Silent pass. The Beta 27 pair shipped on this exact channel in rev 1 without
             objection, and Shure names drum overheads as an intended application. Sweeping the
             locker does turn up dedicated matched OH pairs (Earthworks SR20sp, Audix M1280B,
             sE8), but "a different matched pair exists" is a taste-level difference, not a
             concrete nameable win — and a tie goes to the specified mic. No fork raised.

GENRE BEND   R&B/funk/Motown: the overheads want to sound like a record — cymbals present and
             airy, kit glued, no crashiness. Because the capsule is nearly flat, the shaping is
             mine. Artist layer: a tight rehearsed show band means the overheads are not carrying
             dynamic drama, they're carrying sheen; and with four vocals live on an open plaza,
             every open condenser on stage is a gain-before-feedback cost, so the overheads get
             filtered aggressively at the bottom and are not asked to do anything below the
             cymbals.

VENUE BEND   FSQ outdoor. HPF runs HIGH at **300** — nothing below the cymbals is wanted here, and
             15–16 mph gusts all evening make an open pair the most wind-exposed mics on the
             stage. Bleed cut at −7 @ 400 gets FSQ depth. **Weather layer moved two values off
             rev 1:** (1) LPF opens from 16 kHz to **18 kHz** — with 38 % RH dry air eating HF over
             the throw, closing the overheads down at 16 k removes air the plaza is already
             removing; (2) the 9 kHz trim **lightens from −4 to −2**, because the documented peak
             is only **+2 dB** and a −4 was over-trimming a small peak in air that is itself
             attenuating that region. This is the humidity inversion applied literally.

DRAFT BANDS  HPF 300 · LPF 18000
             B4  −2 | 9000 | 2.0 | BELL
             B3  −5 | 1200 | 2.0 | BELL
             B2  −7 |  400 | 2.0 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.**
             - **B4 −2 @ 9000 is sized to the measured peak.** The capsule's 9 kHz peak is **+2 dB
               or less**. Trimming −4 (rev 1's value) removes more than the capsule added, which on
               a nearly-flat mic means cutting real cymbal air rather than a capsule artifact —
               and doing it in dry air that is already attenuating up there. −2 nets the response
               to roughly flat, which is the honest target for a flat mic.
             - **No air boost.** The temptation with dry air is to lift 10–12 kHz on the
               overheads. Refused: three cymbal mics feed this kit and the hat (ch 5) already
               carries the show's only high lift at 10 kHz. Two condensers lifted in the same
               region stack into hiss and cymbal wash on a plaza, and the sectional rule says only
               one member of the cymbal group owns that lane.
             - B3 −5 @ 1200 is cymbal clang/honk, offset from the hat's 4000 and the ride's 3000.
             - B2 −7 @ 400 is kick/tom/snare bleed arriving from below; B1 FLAT and HPF 300 finish
               that job. The capsule's flat 60 Hz–3 kHz means none of this is fighting a voicing.

CYMBAL SLOTTING  (three cymbal mics — the sectional rule in numbers)
             CH 9  Overheads  mid cut **1200** · HF **−2 @ 9000** · no boost — the primary picture
             CH 5  Hat        mid cut **4000** · HF **+3 @ 10000** — owns the high sizzle
             CH 14 Ride       mid cut **3000** · owns bell/stick definition (see unit 13)
             No shared cut frequency, exactly one high boost across the three channels.

TEMPLATE NOTE  Fader 9 ships as a stereo channel in the FSQ template and is named "Overheads"
             natively. Fader 10 ("SNARE PL8") is untouched — the patcher hard-protects it and
             build_packet.py errors if a channel is written there.

QUESTIONS    None.

TRACE        base(drum overheads on a near-flat supercardioid LDC — RecordingHacks/Shure flat
             60 Hz–3 kHz with only +2 dB peaks at 5.5 k and 9 k, so the shaping is mine and the
             trims must be sized to small peaks) ·
             equip(no cymbal sizes notated; pad assumed OUT and LF filter ENGAGED, with a gain
             re-check fallback written in) ·
             genre(R&B/Motown wants record-like sheen and glue, not crash — flat capsule means the
             genre bend is applied directly in the numbers) ·
             artist(four live vocals on an open plaza make every open condenser a
             gain-before-feedback cost — overheads filtered hard at the bottom, asked to do one
             job) ·
             venue(FSQ outdoor: HPF 300 for gusts, bleed −7 @ 400 at FSQ depth; 38 % RH dry air
             OPENED the LPF from rev 1's 16 k to 18 k and LIGHTENED the 9 k trim from −4 to −2)
