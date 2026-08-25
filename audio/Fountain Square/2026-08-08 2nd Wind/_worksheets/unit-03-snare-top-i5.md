# Unit 03 — Snare top × Audix i5 · CH 3

INSTRUMENT   Snare, top head. R&B/funk/Motown backbeat plus Top-40 covers — this is the loudest
             single decision in the mix: on a dance set the snare is the two-and-four the crowd
             moves to. Ghost notes and press rolls matter in the funk material. **Two-mic source
             with CH 4 (bottom head).**

MIC          Audix i5. Cardioid dynamic, low sensitivity 1.6 mV/Pa, no phantom. No switches.
             Unchanged from rev 1 — this was Brian's own locker-fork swap on 2026-07-31 (offered
             over the Beta 98H/C, he took the i5), so the fork is NOT re-litigated.

SEARCHES     1. `Audix i5 snare top EQ live sound frequency response 5kHz presence peak funk R&B
                backbeat`
             2. (rev-1 cross-check retained) `AUDIX i5 vs SHURE SM57 snare top` — Gearspace
                shoot-out thread

CAPSULE FACT **+5 dB peak at 150 Hz and +9 dB peak at 5500 Hz**, −3 dB points near 50 Hz and
             16 kHz, with a broader presence boost across 3–8 kHz (RecordingHacks i5 page; Barry
             Rudolph review; Sound On Sound i5 review). Sensitivity is deliberately low at
             1.6 mV/Pa, which SOS notes keeps hi-hat spill down on a snare.

WEB SAYS     The i5's whole selling point is that you don't EQ it the way you EQ a 57 — the 5 kHz
             bump is voiced in, and the 150 Hz lift is where snare body sits. Reviewers describe
             the top end as "open without being brittle" *because* the +9 dB at 5.5 k is
             counterbalanced by that low lift. Gearspace's i5-vs-57 shoot-out has the i5 fuller
             and more open in the mids, where the 57 is more scooped.

KB SAYS      mic-library: "Body lift ~+5 dB @ 150 Hz, presence ~+9 dB @ 5.5 kHz, mids slightly
             scooped vs SM57 — more open, more body. Weakness: that 5.5 k peak can get harsh on a
             cracky snare." Bias: ease off body, crack, snap; tame harsh ~5500 Hz.

VERDICT      **AGREE** — and unusually precisely: the KB row carries the same two numbers the
             external sources publish (+5 @ 150, +9 @ 5.5 k). Nothing to reconcile.

LOCKER       Silent pass — Brian's own recorded decision from rev 1. Re-raising it would be
             re-litigating a fork he already answered, which the skill forbids.

GENRE BEND   Funk/R&B wants the crack to cut and the ghost notes to survive. The genre reflex is
             "boost the crack" — refused here, see gate check, because the capsule already did
             it. Artist layer: rehearsed show band playing to a click, so the snare is consistent
             hit to hit; no wide dynamic range to protect, which means the EQ can be decisive.

VENUE BEND   FSQ outdoor: box cut runs FSQ-deep at −8 @ 400. **Weather layer changes this channel
             from rev 1:** last week ran 50 % RH climbing to 77 %, so the 5.5 k trim was set at
             −4. This week is 38 % RH at downbeat and dry all night — dry air absorbs HF over the
             throw to the back of the plaza, so the trim **lightens to −3**. Same capsule, same
             drum, different air. That is the whole reason this value moved.

DRAFT BANDS  HPF 130 · LPF OFF
             B4  −3 | 5500 | 2.0 | BELL
             B3  −5 |  900 | 2.0 | BELL
             B2  −8 |  400 | 2.0 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.** Both reflexes are reversed:
             - The genre reflex "boost the crack at 5 k" is refused: the capsule bakes **+9 dB at
               5500**. The desk's job there is a trim, and this week a light one.
             - The reflex "boost the body at 150" is refused: the capsule bakes **+5 dB at 150**.
               HPF is set at **130, not 150**, deliberately — filtering at 150 would claw back the
               body lift the capsule provides and that ch 3 owns in the two-mic split.
             - B3 −5 @ 900 is lighter than the FSQ default because the i5's mids are already
               slightly scooped versus a 57 (reverse gate). B2 at 400 is the box and gets full
               FSQ depth — that's a shell/room problem the capsule does nothing about.

TWO-MIC LANES (CH 3 × CH 4 — top and bottom, assigned across the whole spectrum)
             CH 3 (i5, top)     owns **CRACK (5.5 k, baked) + BODY (150, baked)** — i.e. the drum.
             CH 4 (ND408, btm)  owns **WIRE SIZZLE (~9 k)** — the snares themselves, nothing else.
             Shared zones named: 5–6 kHz (ch 3 owns it via the baked peak; ch 4 is trimmed at
             4 k to stay out) · 150–200 Hz body (ch 3 owns it; ch 4 is filtered out at 200) ·
             400–500 Hz box (ch 3 cuts 400, ch 4 cuts 500 — **offset on purpose** so two mics on
             one drum don't dig the identical hole).
             **No boost on both mics in the same zone, top or bottom** — ch 3 has no boosts at
             all, ch 4's only boost is at 9 k where ch 3 is untouched.
             CH 4 is POLARITY INVERTED against ch 3. Non-negotiable, see unit 04.

QUESTIONS    None.

TRACE        base(snare top on a cardioid dynamic — box at 400 is the primary target;
             RecordingHacks/SOS +9 @ 5.5 k and +5 @ 150 mean crack and body are both baked) ·
             equip(no drum size, head or tuning notated — generic snare carries) ·
             genre(funk/R&B backbeat — crack must cut, but the capsule already delivers it, so the
             genre bend is a REFUSED boost rather than an applied one) ·
             artist(rehearsed to a click, consistent hit to hit — EQ can be decisive) ·
             venue(FSQ outdoor: box deepened to −8 @ 400; 38 % RH dry air LIGHTENED the 5.5 k
             trim from rev 1's −4 to −3)
