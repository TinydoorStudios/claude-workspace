# Unit 16 — Pads × DI  (ch 21 Pad 1, ch 22 Pad 2)

INSTRUMENT   **Reading these as an electronic sampling pad's stereo output** — an SPD-SX or
             similar, in the percussionist's or drummer's rig. Two things point that way: their
             position on the input list (between the hand percussion at 17–20 and the keys at
             23–24, i.e. inside the percussion block), and the fact that the SPD-SX's master
             out is exactly a **stereo L/R pair on 1/4" jacks** — which is why they'd arrive on
             two DIs rather than as XLR line like the keys do.
             **CONFIRMED by Brian in the round: sampling pad, run as TWO MONO channels and
             panned** — not treated as a stereo image. That sidesteps the matched-DI problem
             entirely and it also means the two channels no longer have to carry identical EQ,
             though they still do here (same source, same treatment; the separation is pan).

MIC/DI       Two DIs — **BSS AR-133 (ch 21) and Whirlwind IMP (ch 22)**, the remaining locker
             boxes after the RNDI (ch 11) and J48 (ch 12). The locker holds no matched DI pair,
             which would have been a problem for a stereo image; **Brian's call to run these as
             two mono channels and pan them makes the mismatch a non-issue** — an active and a
             passive box on two independently-panned mono sources is fine.
             **Locker fork: EXEMPT.** DI inputs, no capsule.

SEARCHES     1. `SPD-SX electronic drum pad live sound DI EQ stereo output mixing percussion pad
                samples FOH`
             2. Cross-read of the Roland SPD-SX / SPD-SX PRO output documentation (B&H, Sam Ash,
                Roland via Equipboard) for the output topology and onboard processing.

CAPSULE FACT No capsule. The governing fact is topology: the SPD-SX carries **21 master effects
             and 20 kit effects including onboard EQ and compression**, and its samples are
             finished 48 kHz/16-bit audio (Roland spec). So this signal arrives **already
             mixed and already processed** — the drummer has set levels and tone per kit inside
             the unit. Desk EQ on this channel is correction of what the PA does to it, not
             shaping of the source.

WEB SAYS     Standard live practice for sampling pads: take the master L/R stereo out to the
             desk, leave the unit's internal balance alone, and treat the pair as program
             material. The direct outs exist for splitting individual samples out, and the input
             list only shows two channels — so this is the master pair, not split samples.

KB SAYS      Nothing. The KB has no row for sampling pads or electronic percussion. Nearest
             verified guidance is the playback/keys approach: subtractive, minimal, don't fight
             a finished source.

VERDICT      **THIN.** Good manufacturer documentation on the topology, no live-EQ consensus
             worth the name, and no KB row to cross-check. I'm treating it as program material
             on that basis and flagging the gap. → **KB write-back candidate**, plus the
             blocking question about what these actually are.

GENRE BEND   R&B/funk with a click and a Track channel: sampling pads in this context fire
             one-shots — 808s, claps, orchestra hits, risers, vocal stabs — that are *meant* to
             sound like the record. They should not be re-EQ'd toward a live drum aesthetic.
             Artist layer: this band's whole approach is faithful, arrangement-accurate covers,
             so the samples are the record's sounds and want to stay that way.

VENUE BEND   FSQ outdoor: the one real risk is 808/sub one-shots landing on top of the kick and
             bass in a mix that already has three low sources plus the Track channel. HPF at 40
             keeps the sub content the samples were built with (that's the point of them) while
             cutting nothing musical, and the mud cut is moderate rather than deep — this is
             finished audio, not a live source with a room problem.

DRAFT BANDS  *(identical on ch 21 and ch 22 — same source, same treatment; the two channels are
             separated by PAN, not by EQ, per Brian's two-mono answer)*
             HPF 40 · LPF OFF
             B4  FLAT
             B3  −4 @ 300   Q 1.8  BELL   light mud trim for the outdoor stack
             B2  FLAT
             B1  FLAT

GATE CHECK   **Almost nothing written, and that's the finding.** The gate question for a
             finished-audio source is "did someone already make this decision?" — and here the
             answer is yes, twice: the sample was produced, then the drummer EQ'd the kit inside
             the unit. Two boosts and a deep cut on top of that would be the third opinion in
             the chain. The single moderate 300 Hz trim exists because the *plaza* stacks
             low-mids, which is a venue problem the sample's producer couldn't have solved.
             **Against the low-end slot map (unit 09):** no low boost here, deliberately. If the
             pads are firing 808s they'll land at 50–60 Hz on top of the D6 kick's baked peak —
             the fix for that is the fader and the arrangement, not EQ.

QUESTIONS    Resolved. Brian: sampling pad, two mono channels, panned.
             Still open as a staged KB write-back — add a sampling-pad / electronic-percussion
             row to eq-starting-points.
