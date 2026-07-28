# Unit 03b — Snare top × Audix i5  (ch 3)  — NEW UNIT, opened by Brian's fork answer

*Brian's call on the round: **i5 on ch 3 only.*** There's one i5 in the DP8, so the main snare
takes it and ch 4 (the aux snare) stays on the Beta 98H/C — a deliberately mixed pair. That
makes ch 3 a new instrument × mic unit and it gets its own research pass. Unit 03 still governs
ch 4; its ch-3 draft is superseded by this file.

INSTRUMENT   Main snare, top head, R&B/gospel show band. Backbeat event that has to read through
             congas, bongos, toys, a programmed track and four vocals.

MIC          Audix i5 — cardioid dynamic, no 48V, Short/boom stand. **From the DP8 — the same
             case the D6 (ch 2), both D2s (ch 6/7) and the D4 (ch 8) come out of**, so nothing
             extra opens for it. KB tendency: "body lift ~+5 dB @ 150 Hz, presence ~+9 dB @
             5.5 kHz, mids slightly scooped vs SM57 — more open, more body. **Weakness: that
             5.5 k peak can get harsh on a cracky snare.** → ease off body, crack, snap; tame
             harsh ~5500 Hz."

SEARCHES     1. `Audix i5 snare frequency response 5.5kHz presence peak 9dB 150Hz body live EQ
                measurement`
             2. Cross-read of the returned RecordingHacks i5 page, the Sound On Sound review,
                Barry Rudolph's review and the Gearspace i5-vs-SM57 snare shootout thread.

CAPSULE FACT **−3 dB points at 50 Hz and 16 kHz, with a +5 dB peak at 150 Hz and a +9 dB peak at
             5500 Hz**, plus a broad presence region running 3–8 kHz (RecordingHacks / SOS).
             That 5.5 kHz figure is the largest single baked peak of any mic on this input list
             and it dominates how this channel gets built.

WEB SAYS     The recurring line in the i5-vs-57 comparisons is that the i5's ~5 kHz peak means
             "you would not have to EQ these recordings as you would using the Shure" — the
             crack is already in the capsule. Reviewers consistently report it as more open and
             fuller than a 57 with slightly scooped mids.

KB SAYS      As above — and the KB's warning is the operative one here: that 5.5 k peak **gets
             harsh on a cracky snare**, which is exactly what a show-band backbeat is.

VERDICT      **AGREE.** Same +5 @ 150 and +9 @ 5.5 k on both sides, same "needs less EQ than a
             57" conclusion, same harshness caveat.

LOCKER       **Resolved — this IS the fork outcome.** Fork raised on unit 03, Brian's answer:
             i5 on ch 3, Beta 98H/C retained on ch 4. Recorded in `changes` as a locker-fork
             swap; unit 03 carries the "Beta 98 kept on ch 4" line so it isn't re-litigated.

GENRE BEND   R&B/funk/gospel backbeat. It needs to land hard and get out of the way, and it has
             to stay clear of the four vocals sitting above it. The crack is placed *high*
             rather than in the 1–3 kHz vocal path.

VENUE BEND   FSQ outdoor: box cut at outdoor depth, HPF high (the i5 reaches to 50 Hz and none of
             that is wanted on a snare next to a kick and a floor tom). Being a dynamic, it also
             solves the reason the fork was raised — far less hat bleed than the condenser it
             replaced, which matters with an open hat mic a couple of feet away on a windy plaza.

DRAFT BANDS  HPF 150 · LPF OFF
             B4  −4 @ 5500  Q 2.0  BELL   the capsule's +9 dB peak — see gate check
             B3  −8 @ 400   Q 2.0  BELL   box — outdoor depth
             B2  −5 @ 900   Q 2.0  BELL   honk, keeps the vocal path clear
             B1  FLAT                     see gate check

GATE CHECK   **The whole channel is the capsule gate working.** Two moves that would be reflexes
             on any other snare mic are forbidden here:
             · **No crack boost.** A snare's crack normally gets +3 around 5–7 kHz. This capsule
               delivers **+9 dB at 5500 Hz** on its own. Boosting there would stack a 9 dB peak
               on a cracky backbeat with no room to soften it — outdoors that reads as an ice
               pick at 60 feet. The move is **−4**, and the crack still arrives.
             · **No body boost.** The i5 already puts **+5 dB at 150 Hz** in. B1 stays flat and
               the HPF at 150 sits right at the shoulder of that lift, keeping the body the
               capsule gives while cutting the kick and floor-tom spill below it.
             **Zero boosts on this channel, and the reason is entirely the mic.** Compare ch 4
             (unit 03), where the Beta 98 *does* get a +3 at 8 k — because that capsule's baked
             lift starts above 8 k, so there's room below it. Same drum pair, same show,
             opposite treatment, capsule-driven.
             **Sectional separation (ch 3 vs ch 4):** ch 3 trims 5500 while ch 4 lifts 8000;
             box at 400 vs 500; mid lane at 900 vs 1200; HPF 150 vs 180. The two snares are
             now *more* differentiated than they were as a matched pair — the mixed pair is an
             improvement on the separation, not a compromise.

QUESTIONS    None — the fork is resolved.
