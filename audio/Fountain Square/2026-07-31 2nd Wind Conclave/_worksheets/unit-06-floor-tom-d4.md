# Unit 06 — Floor tom × Audix D4  (ch 8)

INSTRUMENT   Floor tom, bottom of the tom run. In an R&B/funk set it's the weight in a fill and
             the drum that shares the low-mid region with the kick, the bass and the congas —
             the crowded end of this show. No drum size given; generic baseline carries.

MIC          Audix D4 — hypercardioid dynamic, no 48V, clip/Short stand. KB tendency: "flat to
             ~63 Hz, rise ~80 Hz, reaches 35 Hz, smooth 800 Hz–1 kHz (not scooped). Deep,
             resonant. Weakness: less upper-mid attack — may need a touch of click."

SEARCHES     1. `Audix D4 floor tom frequency response 80Hz rise 35Hz reach 800Hz 1kHz smooth
                specification`
             2. Fetched and read the **Audix D-4 "Sub Impulse" spec sheet** (recordinghacks
                mirror, 2001) directly for the published numbers.

CAPSULE FACT From the Audix spec sheet: **40 Hz – 18 kHz**, hypercardioid, **off-axis rejection
             > 30 dB**, **max SPL > 144 dB**, VLM Type D capsule, transformerless. Audix's own
             framing: "a perfect choice for instruments requiring precise low frequency
             reproduction." The number that matters for this build is the comparison with its
             own sibling — the D4 reaches **40 Hz where the D2 stops at 68 Hz**, a 28 Hz
             difference that is the entire reason the two mics are on different drums here.

WEB SAYS     Dealer/spec consensus is consistent: the D4 is the low-source member of the D-series
             (floor tom, djembe, kick, low brass), chosen for LF extension rather than attack.
             Nothing in the published material claims a presence peak, which lines up with the
             KB's note that it can need a touch of click added.

KB SAYS      mic-library: "Floor-tom/low source: flat to ~63Hz, rise ~80Hz, reaches 35Hz, smooth
             800Hz-1kHz (**not scooped**). Deep, resonant. Weakness: less upper-mid attack —
             may need a touch of click. → ease off boom, mud."

VERDICT      **AGREE.** The spec sheet's 40 Hz and the KB's "reaches 35 Hz" are the same claim
             at the edge of the curve, and neither source claims a presence peak. The KB adds
             one thing the manufacturer sheet doesn't: that the 800 Hz–1 kHz region is **smooth,
             not scooped** — the opposite of the D2. That distinction drives the EQ below and is
             Brian's own verified knowledge doing exactly the job the cross-check is for.

LOCKER       **Silent pass.** The D4 is the locker's first call for floor tom (mic-library:
             "Audix D4 | Floor tom — more low-end extension than D2"). No fork.

GENRE BEND   R&B/funk: the floor tom is a punctuation mark. It wants depth and a defined stick,
             and — because this band runs congas, bongos and a bass guitar in the same octave —
             it wants to be narrow about where it lives.

VENUE BEND   FSQ outdoor: the plaza's KS21 sub arch handles the deep end of the PA, so the floor
             tom doesn't need to reach for 40 Hz; the HPF at 60 buys stage rumble and gust
             immunity and costs nothing musically. The mud cut goes to outdoor depth.

DRAFT BANDS  HPF 60 · LPF 10000
             B4  +4 @ 3000  Q 1.5  BELL   stick attack — the one thing this capsule doesn't give
             B3  −7 @ 350   Q 2.0  BELL   mud/box — outdoor depth
             B2  −6 @ 900   Q 2.0  BELL   see gate check
             B1  +3 @ 85    Q 1.2  BELL   body, just above the capsule's own rise
                                          (moved 90 → 85 when the show-wide low-end slot map
                                          was drawn in unit 09 — clears the bass at 100)

GATE CHECK   **Boost audit — B4 +4 @ 3000.** Neither the Audix sheet nor the KB claims any
             presence peak in this capsule; the KB explicitly says it's short on upper-mid
             attack. So this is a lift into an empty region, not a stack — and it's the one
             boost on this channel allowed to go to +4 rather than +3.
             **Boost audit — B1 +3 @ 90.** The capsule's own rise is at ~80 Hz. The boost is
             placed at 90, just above it, and held to +3 so it extends the body rather than
             piling onto the rise. A +5 written at 80 would have been the stack.
             **B2 −6 @ 900 is the D2/D4 difference made audible.** On ch 6/7 the 500 Hz–1 kHz
             band is left flat because the D2 already dips it. The D4 does **not** — it's smooth
             through there — so on this channel the honk is real and gets cut at outdoor depth.
             Same kit, same show, opposite move, and the capsule is the reason.
             **Sectional separation:** body at 90 (vs rack toms at 130 and 110), attack at 3 k
             (vs 4 k and 3.5 k) — the three toms descend in both body and attack, so a fill
             reads as three drums.

QUESTIONS    None.
