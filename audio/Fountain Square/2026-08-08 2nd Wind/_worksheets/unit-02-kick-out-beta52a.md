# Unit 02 — Kick drum (outside / port) × Shure Beta 52A · CH 2

INSTRUMENT   Same kick drum as unit 01, mic'd at the sound hole / just outside the resonant head.
             Its job in THIS mix is the weight a dance crowd feels on a plaza — the part the PA's
             8× KS21 delayed arch actually reproduces. Not attack; ch 1 has that.
             **Mic changed this week** — rev 1 (2026-07-31) had an Audix D6 here.

MIC          Shure Beta 52A. Supercardioid dynamic, **20 Hz–10 kHz** (deliberately band-limited),
             no phantom. **Two-mic source with CH 1 (Beta 91A).** No switches.

SEARCHES     1. `Shure Beta 52A frequency response chart kick drum EQ live low mid scoop dB
                presence peak 4kHz`
             2. `"Beta 52A" kick outside port mic vs inside two mic kick blend EQ live sound
                forum`

CAPSULE FACT **Presence boost at 4 kHz** with response deliberately limited to **20 Hz–10 kHz**,
             emphasising **50 Hz–4 kHz** (Shure product page + spec sheet; FrontEndAudio and
             DrumHelper both describe the 4 kHz presence peak as voiced-in to make kick and bass
             cut). Gearspace/DFO consensus adds that the midrange attack "can be a little harsh"
             and a typical desk pass is +2 @ 60, −4 @ 500, roll off above 6 k.

WEB SAYS     Shure's own how-to names **this exact pairing**: "the Beta 91A inside the kick drum
             and the Beta 52A near the sound hole… play each microphone to its strength" — the
             52A is optimised for low-frequency punch and captures the weight, the 91A captures
             the attack. That is external confirmation of the lane split, not just a convention I
             chose. The band-limited top (nothing above 10 k by design) means the capsule is
             already a low-pass filter.

KB SAYS      mic-library: "Tailored kick dynamic, scooped low-mids, presence lift ~4 kHz, big
             lows. Click + thump voiced in." Bias: ease off attack, box, mud.

VERDICT      **AGREE.** Web (4 kHz presence lift, 50 Hz–4 kHz emphasis, band-limited to 10 k,
             harsh-ish mid attack) and KB (presence lift ~4 kHz, big lows, scooped low-mids,
             ease off attack/box/mud) say the same thing in the same places. Externally sourced.

LOCKER       First-call match — silent pass. mic-library: "Shure Beta 52 | Kick — body and thump
             layer (inside)" and the Standard Combos section names Beta 52 + Beta 91 as "the
             standard two-mic setup for most shows." This week's list IS that combo. No fork.

GENRE BEND   R&B/funk dance floor: weight is the point, and the 52A's voiced 50–100 Hz is why
             it's here. No genre-driven change to the cuts. Artist layer: programmed low end in
             the Track channel (ch 16) means this kick shares the sub region with playback — so
             the low end is claimed by *gain and capsule*, not by an EQ boost that would fight
             the track.

VENUE BEND   FSQ outdoor: box/cardboard cut deepened to FSQ range (−6 rather than a polite −4).
             The 4 kHz trim is NOT a venue call — see gate check; it's lane discipline. Weather
             (38 % RH, dry): irrelevant up top on a mic that stops at 10 kHz by design.

DRAFT BANDS  HPF 35 · LPF 8000
             B4  −4 | 4000 | 1.5 | BELL
             B3  −5 |  500 | 1.8 | BELL
             B2  −6 |  250 | 1.8 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.**
             - **B1 FLAT is the gate doing its job.** The forum's typical "+2 @ 60" is exactly
               the move to refuse: Shure emphasises 50 Hz–4 kHz on purpose, so a low boost stacks
               on voiced response. The weight comes from gain and placement, not from B1.
             - **B4 −4 @ 4000 is a de-stack, not a tone cut.** The 52A bakes a presence peak at
               4 kHz and the 91A on ch 1 bakes an emphasis from 4–9 kHz. Boosting or even leaving
               both hot puts two voiced peaks on the same drum in the same zone — the classic
               two-mic failure. Ch 1 owns that lane, so ch 2's baked peak gets trimmed out of it.
             - **B3 −5 @ 500 is lighter than the FSQ default on purpose.** The capsule already
               scoops low-mids, so the reverse gate applies: don't deep-cut a zone the mic
               scooped. This is the "back the complement mic's low-mids off so it doesn't stack"
               move, sized to a capsule that has already started the job.
             - **LPF 8000 is housekeeping, not a cab replacement** — the capsule ends at 10 k
               anyway. Its real value is rejecting cymbal bleed, and this kit has THREE cymbal
               mics (hat, ride, OH pair) plus a bottom-snare mic all leaking into it.

TWO-MIC LANES (restated from unit 01, held identical)
             CH 1 (91A, inside)  = ATTACK / TOP. HPF 70, B1 flat, B4 flat.
             CH 2 (52A, port)    = BODY / THUMP / BOTTOM. HPF 35, B1 flat (baked), B4 trimmed.
             Shared zones: 4 kHz presence (ch 1 owns it, ch 2 trimmed out) · 60–100 Hz weight
             (ch 2 owns it, ch 1 filtered out at 70) · 400–500 Hz box (ch 1 cuts 400 hard, ch 2
             backs off 500 lightly — different frequencies, different capsule shapes, no hole).
             **No boost on both mics in the same zone, top or bottom.** Verified: there are no
             boosts on either channel at all.
             Polarity check the pair in mono at soundcheck — sum should be fuller than either
             alone; if thinner, flip ch 2.

QUESTIONS    None.

TRACE        base(kick at the port on a band-limited dynamic — Shure 4 kHz presence peak and
             50 Hz–4 kHz emphasis mean both the weight and the attack are voiced in) ·
             equip(no drum sizes/heads notated — no rig-driven bend) ·
             genre(R&B/funk dance weight — claimed by gain and capsule, not by a B1 boost) ·
             artist(programmed low end in the Track channel — no low boost to fight it) ·
             venue(FSQ outdoor — cardboard cut deepened to −6 @ 250; dry air is a no-change layer
             on a mic that stops at 10 kHz)
