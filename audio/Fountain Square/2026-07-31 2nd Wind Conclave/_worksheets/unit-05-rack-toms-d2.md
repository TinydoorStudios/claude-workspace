# Unit 05 — Rack toms × Audix D2  (ch 6 Rack 1, ch 7 Rack 2)

INSTRUMENT   Two rack toms on a show-band kit. In R&B/funk they're fill instruments, not a
             constant presence — they need to arrive with weight and get out of the way.
             Equipment note: no drum sizes given on the input list, so the generic rack-tom
             baseline carries; nothing invented.

MIC          Audix D2 — hypercardioid dynamic, no 48V, clip/Short stand. KB tendency: "+150 Hz
             body, dip 500 Hz–1 kHz, subtle upper-mid lift. Punchy, articulate. Weakness: leaner
             deep lows than D4. → ease off boom, mud."

SEARCHES     1. `Audix D2 rack tom frequency response 150Hz boost 500Hz dip hypercardioid
                specification live EQ`
             2. Cross-read of the returned Audix AX-D2 spec sheet, the RecordingHacks D2
                cutsheet and the Gearspace D2 user review.

CAPSULE FACT **68 Hz–18 kHz, with a boost around 150 Hz, a dip between 500 Hz and 1 kHz, and a
             subtle upper-mid presence lift** — Audix spec sheet / RecordingHacks cutsheet.
             Pattern: hypercardioid with **over 30 dB of off-axis rejection**.

WEB SAYS     The D2 is deliberately pre-shaped for rack toms — the 150 Hz bump is the body and
             the 500 Hz–1 k dip is the mud already removed, which is why the consensus is that
             it needs "minimal corrective EQ." The >30 dB off-axis figure is the other half of
             the pitch: on a crowded kit it keeps hat and snare out of the tom channels.

KB SAYS      mic-library: "Rack-tom hypercardioid: +150Hz body, dip 500Hz-1kHz, subtle upper-mid
             lift. Punchy, articulate. Weakness: leaner deep lows than D4. → ease off boom, mud."

VERDICT      **AGREE.** Same three features, same numbers, same conclusion.

LOCKER       **Silent pass.** The D2 is the locker's first call for rack toms (mic-library:
             "Audix D2 | Toms — small/mid toms"). No fork.

GENRE BEND   R&B/funk fills want a round, quick tom — attack enough to be heard over a dense
             mix, decay short enough not to smear the next bar. Artist layer: with programmed
             percussion already in the Track channel, the live toms are accents; they get a
             touch of stick definition rather than a big low boost.

VENUE BEND   FSQ outdoor: the 400–600 Hz cardboard/box zone gets the deeper outdoor treatment,
             and the HPF sits above the tom's fundamental region only as far as the mic's own
             68 Hz limit makes sensible — 90 for rack toms.
             **Template note:** the new FSQ template (installed 2026-07-26) ships faders 6/7/8
             with the native gate already enabled — threshold −36.2 dB, release 227 ms, with a
             130–317 Hz sidechain band. That's Brian's own tom gate and it stays; the paperwork
             documents it rather than re-deriving it.

DRAFT BANDS  **ch 6 Rack 1**
             HPF 90 · LPF 12000
             B4  +3 @ 4000  Q 1.5  BELL   stick definition
             B3  −7 @ 450   Q 2.0  BELL   box/cardboard — outdoor depth
             B2  FLAT                     500 Hz–1 k is already dipped in the capsule
             B1  +3 @ 130   Q 1.2  BELL   see gate check

             **ch 7 Rack 2**
             HPF 80 · LPF 12000
             B4  +3 @ 3500  Q 1.5  BELL   definition, a step below rack 1
             B3  −7 @ 400   Q 2.0  BELL   box
             B2  FLAT
             B1  +3 @ 110   Q 1.2  BELL   the lower drum's body, below rack 1's

GATE CHECK   **Boost audit — B1 +3 @ 130 / 110.** The capsule's baked body bump is at **150 Hz**.
             Both boosts sit deliberately *below* it (130 and 110), so they extend the low body
             rather than stacking the peak — and they stay at +3, not +5, because the capsule is
             already contributing above them. A boost written at 150 Hz would have been the
             stack, and that's the move this gate exists to catch.
             **Boost audit — B4 +3 @ 4000 / 3500.** The D2's upper-mid lift is described as
             "subtle" in both sources, so a modest +3 for stick definition is a lift on gentle
             ground. Not taken higher for that reason.
             **Gate in reverse — B2 stays FLAT on both.** The 500 Hz–1 kHz region is *already*
             dipped by the capsule. Even with the FSQ override pushing cuts deeper, there's
             nothing left to cut there — the box cut is placed at 400–450, below the dip.
             **Sectional separation (ch 6 vs ch 7):** body at 130 vs 110, definition at 4 k vs
             3.5 k, box at 450 vs 400, HPF 90 vs 80 — the two toms are voiced as two drums
             descending in pitch, not one curve copied twice.

QUESTIONS    None.
