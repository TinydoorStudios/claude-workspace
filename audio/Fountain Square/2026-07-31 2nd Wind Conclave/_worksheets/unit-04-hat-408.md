# Unit 04 — Hi-hat × "408"  (ch 5)  ⚠ MIC AMBIGUOUS — BLOCKS THIS CHANNEL

INSTRUMENT   Hi-hat on a full kit that also carries two snares, three toms, an overhead pair,
             congas, bongos and toys. In an R&B/funk dance set the hat is the timekeeper and
             the thing that gets a mic mostly so it can be *controlled*, not featured — and
             outdoors with the hat sitting next to two condenser snare mics, bleed management
             matters more than tone.

MIC          **"408" is ambiguous and I am not guessing it.** Brian's own shorthand rule
             (CLAUDE.md, mic table) reads: *"ND408 = Electro-Voice N/D 408 … Any '408' I write
             on a snare = the Lauten LS-408, not this."* That rule disambiguates 408-on-a-snare.
             This one is written on a **hat**, which the rule doesn't cover, and neither
             candidate is a hat mic in the KB — the locker's hat calls are the SM81, the Audix
             M1280BHC and the Earthworks SR25. Working assumption for the draft below: **EV
             N/D 408** (the LS-408 is snare-specialised per the KB, so a hat is the less likely
             of the two). **The answer gates this channel.**
             Interlock: if the answer is the LS-408, that single mic is then unavailable as the
             ch 3 snare alternative, which changes the unit-03 fork.

SEARCHES     1. `Electro-Voice N/D 408 supercardioid frequency response presence peak dB
                proximity toms review`
             2. `Audix M1280BHC hi-hat microphone frequency response hypercardioid
                specification dB` (the alternative)
             3. Fetched and read the **EV N/D 408B Engineering Data Sheet** (part 531818-201,
                ©1992) response curve and spec panel directly.

CAPSULE FACT From the EV data sheet: **close response 30 Hz–22 kHz, far response 60 Hz–22 kHz**
             — i.e. the low end is a *placement* variable, and the printed close curve runs on
             the order of **10 dB above the far curve through 100–300 Hz**. EV's own text:
             "the low-frequency response is tailored to provide bass boost without the
             booziness of many directional microphones," and closer working distances are the
             documented way to get it. The response carries a **broad presence rise centred
             ~4–5 kHz**, a few dB above the 1 kHz level, then a gentle top out to 22 k. The
             N/DYM magnet gives **6 dB more output sensitivity** than conventional designs, and
             the supercardioid pattern is unusually uniform with frequency (EV's stated reason
             for its gain-before-feedback advantage).
             Alternative for the fork: **Audix M1280BHC — 40 Hz–20 kHz hypercardioid**,
             integrated preamp, RF-immune (Audix spec).

WEB SAYS     Gearspace/TC Furlong/dealer consensus: the 408 is a percussion, guitar-cab and
             horn mic — snare, toms, cabs. Nobody puts one on a hi-hat. Its selling points
             (proximity bass boost on a pivoting yoke, supercardioid rejection, 144 dB dynamic
             range) are all aimed at loud, close, low-ish sources.

KB SAYS      mic-library on the ND408: "brighter and more aggressive upper mids than an SM57,
             deliberate proximity lift, high SPL, tiny pivoting head that fits where a 421
             won't. **Weakness: that upper-mid bite gets spiky on bright sources**; close
             working distance piles low-mids." A hi-hat is the definition of a bright source.
             KB hat calls: SM81 ("ruler-flat… accurate on hat/OH"), M1280BHC ("Hi-hat —
             ultra-compact condenser", "tight isolation"), SR25.

VERDICT      **THIN — resolved by Brian in the round.** There is no body of live-sound evidence
             for a 408 on a hi-hat because essentially nobody does it — the sources are all
             about cabs, toms and snare. I can characterise the capsule confidently; I cannot
             cite anyone using it this way. Taken to Brian rather than papered over.
             **Answer: it's the EV N/D 408, and it stays.** The draft below is now the build.

LOCKER       **FORK RAISED and DECLINED.** Alternative offered: Audix M1280BHC (DP8) — the hat
             mic in a case already open on this show (its D6, both D2s and the D4 are on the
             list), hypercardioid, the KB's own hi-hat call. **Brian kept the 408.**
             One line goes in `mic_notes` so this isn't re-litigated next rev:
             *"Locker fork — M1280BHC offered, ND408 kept."*
             Consequence carried forward: the −6 @ 4500 stays and is load-bearing, because the
             capsule's presence rise is exactly where hat clank lives. That band is the price of
             keeping this mic and it should not be dialled out at soundcheck without listening
             for what comes back.

GENRE BEND   R&B/funk: the hat carries the 16ths that make the groove move, so it needs
             articulation up top and nothing at all below the snare. It is never a featured
             channel — it exists to be dialled in and left. Artist layer: with a programmed
             track under the band, the live hat mostly adds human feel on top of the
             programmed one; it should be crisp and narrow, not big.

VENUE BEND   FSQ: gusts to 16 mph and an open plaza mean every open mic on the kit is also a
             wind and wash collector — the HPF goes high (250) with no hesitation. No room gain
             means nothing below the hat's own fundamental is doing any work up there anyway.

DRAFT BANDS  *(CONFIRMED — Brian: EV N/D 408, fork declined)*
             HPF 250 · LPF OFF
             B4  +3 @ 10000 Q 1.5  BELL   stick articulation / shimmer
             B3  −7 @ 400   Q 2.0  BELL   the proximity low-mid pile the data sheet documents
             B2  −6 @ 4500  Q 2.0  BELL   the capsule's own presence rise — see gate check
             B1  FLAT

GATE CHECK   **Boost audit — B4 +3 @ 10 k.** The 408's printed curve is gently rising and flat
             out to 22 kHz with no baked peak at 10 k (its peak is down at 4–5 k), so a lift
             there is a genuine one, not a stack. It stays modest at +3 because humidity climbs
             from 50% to 77% across the set and the top will get *more* present, not less, as
             the night goes on.
             **Gate in reverse — B2 −6 @ 4500.** This is the one move the capsule *forces*.
             The presence rise is centred exactly where a hi-hat's most obnoxious clank lives,
             and the KB's warning is explicit ("that upper-mid bite gets spiky on bright
             sources"). So the correct move there is a cut, at outdoor depth. That single band
             is most of the argument for the locker fork: the alternative mic doesn't need it.

QUESTIONS    1. **Which 408 is on the hat** — EV N/D 408 or Lauten LS-408? Blocking.
             2. Locker fork — M1280BHC instead?
