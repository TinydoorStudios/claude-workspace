# Unit 12 — Electric guitar × Marshall emulated line out ("Rec Out") · CH 13

INSTRUMENT   Electric guitar, one channel. In an R&B/funk/Motown show band the guitar is mostly
             clean-to-crunchy comping — chank, sixteenth-note skank, wah figures, occasional
             solo — sitting in the 800 Hz–3 kHz window between the bass and the keys. Role in THIS
             mix: rhythmic articulation that reads on a plaza without eating the vocal's presence
             region, with four live vocals to protect.
             **Source changed this week** — rev 1's list said a modeler with cab sim on; this week
             the band wrote "Rec Out of Marshall."

MIC          Not a mic — **the Marshall's emulated line out.** Confirmed by Brian in the round,
             2026-08-08: DSL/JVM class, speaker-emulated. **EXEMPT from the locker fork** (XLR line
             feed, no capsule).

SEARCHES     1. `Marshall DSL emulated line out FOH live EQ Softube cabinet emulation harsh 800Hz
                honk low pass`
             2. `Marshall amp "emulated line out" vs raw line out DI recording out speaker
                emulation which models DSL JVM MG Origin`

CAPSULE FACT (equipment fact) **The DSL's emulated output is a frequency-compensated line-level
             out running Softube-designed cabinet emulation of Marshall's 1960 4×12** — Marshall
             and Softube replicated the 1960-series 4×12 following their CODE-series partnership,
             and both the headphone and line outputs carry it (Marshall Amp Forum DSL/Softube
             threads; Sweetwater DSL20HR product copy; Cream City Music's 2018 DSL update
             write-up). On the JVM, the Marshall forum's own consensus is that the emulated line
             out is a genuinely usable FOH source — one thread's summary is that it beats a mic'd
             speaker outright.

WEB SAYS     The decisive point is that this is a **frequency-compensated** output — it is not a
             raw preamp tap. The Softube emulation supplies the 4×12's own response: the
             characteristic Marshall midrange honk in the 800 Hz–1 kHz region, the presence shelf
             around 2–3 kHz, and the speaker's HF roll-off above roughly 5–6 kHz. All three of
             those are already in the signal before the desk sees it.

KB SAYS      `eq-starting-points` has no row for a modeller or emulated amp direct feed — the same
             gap as unit 10's post-EQ bass DI, and one of the four rows in the write-back Brian
             approved today. What the KB *does* supply is the governing principle, established on
             this show's own rev 1 and now in auto-memory: **a cab-sim'd direct feed is a mic'd cab
             for gate purposes — don't boost into the IR's presence shaping.**

VERDICT      **AGREE.** The web pass establishes that the Marshall emulation is frequency
             compensated and identifies the specific cab modelled; the KB principle says how to
             treat a compensated feed. They point the same way, and the fresh pass adds the
             concrete detail rev 1 lacked — rev 1 knew only "cab sim ON", this build knows it is a
             1960 4×12 emulation, which is what moves the honk cut to 800 Hz.

LOCKER       **Exempt** — line-level feed with no capsule. No fork, no packet line.

GENRE BEND   Funk/R&B comping wants tight, dry midrange articulation, not size. The genre reflex
             would be a presence lift to make the chank cut — refused (gate check). Instead the
             articulation comes from clearing the mud below it. Artist layer: no horn channels on
             this list, so the keys and pads carry the horn lines in the 1–2 kHz window; the guitar
             is deliberately cut at 800 and left alone above it so it interlocks with those parts
             rather than masking them.

VENUE BEND   FSQ outdoor: box/mud cut at full FSQ depth, −8 @ 300 — this is one of the channels
             where a plaza is unforgiving, because guitar mud stacks directly onto bass and keys
             mud in the same octave. HPF **150**: nothing musical on this source lives below it and
             everything below it competes with the bass lane. Weather layer: **no change** — the
             emulation has already rolled the top off around 5–6 kHz, so there is no HF up there
             for dry air to take, and nothing to protect.

DRAFT BANDS  HPF 150 · LPF 8000
             B4  FLAT
             B3  −5 |  800 | 2.0 | BELL
             B2  −8 |  300 | 2.0 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.**
             - **No presence boost, and this is the load-bearing decision.** The Softube 1960 4×12
               emulation already supplies the cab's presence shaping around 2–3 kHz. Rev 1 drafted
               `+3 @ 3000` here and **withdrew it** once cab sim was confirmed; the same withdrawal
               applies with more force now that the emulated cab is identified by model. B4 stays
               FLAT.
             - **B3 −5 @ 800 rather than the generic 900.** The move is aimed at the 1960 4×12's own
               midrange honk, which the emulation reproduces around 800 Hz–1 kHz. Rev 1 cut 900
               against a generic cab sim; naming the cab moves the target.
             - **LPF 8000 is housekeeping, not a cab replacement.** The emulation has already
               rolled off above ~5–6 kHz — this is the distinction that would have inverted if the
               answer to Q3 had been "raw", where the LPF would have had to come down to 5–6 kHz and
               *be* the cab.
             - B1 FLAT and HPF 150: the bass lane is protected, and a guitar contributes nothing
               below 150 in a dense dance mix.

QUESTIONS    None. Q3 answered in the round.

TRACE        base(electric guitar, rhythm comping — 300 Hz mud and 800 Hz honk are the targets) ·
             equip(Marshall emulated line out, Softube 1960 4×12 emulation, frequency-compensated —
             this layer REFUSED the presence boost outright and MOVED the honk cut from 900 to 800
             by naming the cab) ·
             genre(funk/R&B chank wants dry tight articulation — achieved by clearing mud, not by
             lifting presence) ·
             artist(no horn channels; keys and pads own the 1–2 kHz window, so the guitar is cut at
             800 and left alone above it to interlock rather than mask) ·
             venue(FSQ outdoor: mud cut deepened to −8 @ 300, HPF 150 to protect the bass lane; dry
             air = no change, the emulation already rolled the top off)
