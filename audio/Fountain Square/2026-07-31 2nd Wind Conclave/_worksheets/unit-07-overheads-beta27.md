# Unit 07 — Overheads × Shure Beta 27 pair  (fader 9, STEREO)

INSTRUMENT   Drum overheads. The band listed them as OH L / OH R on their ch 9 and 10; on this
             console they are **one stereo channel on fader 9** — both mics, one fader, one EQ.
             Fader 10 is the SNARE PL8 reverb return and takes no input. In an R&B/funk set with
             a programmed track underneath, the overheads are cymbal detail and kit glue, not
             the drum sound — the close mics own that.

MIC          Shure Beta 27 ×2 — large-diaphragm supercardioid FET condensers, 48V, Tall/boom
             stands. **Switchable hardware: −15 dB pad. ASSUMED OUT.** Overheads sit well back
             from the sources and the pad would cost noise floor on an already-noisy plaza.
             Fallback if a pad is found engaged: pull it, or add 15 dB at the head amp and
             expect a worse S/N.

SEARCHES     1. `Shure Beta 27 supercardioid condenser overheads drums frequency response
                5.5kHz 9kHz peak review`
             2. Cross-read of the returned RecordingHacks Beta 27 page and the Studiocare /
                B&H spec listings.

CAPSULE FACT **Nominally flat from ~60 Hz to 3 kHz, with two small HF peaks of +2 dB or less at
             5.5 kHz and 9 kHz; HF −3 dB point above 15 kHz** — RecordingHacks. Plus the
             **switchable −15 dB attenuator** and a supercardioid pattern Shure sells
             specifically for off-axis rejection in live reinforcement.

WEB SAYS     Consensus: a natural, near-linear LDC that is flatter and smoother than the SM27,
             with real low-end weight for a condenser, explicitly marketed for drum and
             percussion overheads among other duties. The +2 dB peaks are the only colour in it
             — this is a mic that reports the kit rather than flattering it.

KB SAYS      mic-library: "Supercardioid LDC, flat 60Hz-3kHz, small peaks +2dB at 5.5k and 9k,
             −15dB pad, flatter than SM57. Open, clean cab/instrument mic. Weakness: slight 9k
             fizz on bright amps. → ease off box, honk; tame harsh ~9000Hz."

VERDICT      **AGREE.** Identical numbers on both sides — 60 Hz–3 kHz flat, +2 dB at 5.5 k and
             9 k, the pad, the supercardioid pattern. Nothing to escalate.

LOCKER       **Considered and not raised.** The obvious alternatives are matched overhead pairs:
             the Earthworks SR20sp Gen 2 (DK-6) or the Audix M1280B pair (DP8 — a case already
             open on this show). Both are more accurate. Both are also *cardioid*, and on an
             open plaza with a 10,000-person conclave crowd, pattern is worth more than
             accuracy — the Beta 27's supercardioid rejection and its −15 dB pad are the reason
             it survives outdoors where a flat SDC pair collects plaza wash. The KB's own note
             on the M1280B ("thin lows, **room-sensitive**") is the argument against it here.
             Tie goes to the specified mic; no fork to Brian.

GENRE BEND   R&B/funk: overheads are glue and hat/ride shimmer, sitting under a mix that already
             has close mics on everything and a programmed kit in the Track channel. They get
             pulled back, not featured — which means this channel is almost entirely subtractive.

VENUE BEND   FSQ outdoor, gusts to 16 mph: overheads on tall booms are the most wind-exposed
             mics on this stage and the ones with the most low-frequency junk to reject. HPF
             goes to 300 — far higher than an indoor overhead would ever run — because nothing
             below the cymbals is wanted from this channel anyway. **Template note:** this fader
             ships double-gated in the FSQ template; that stays as-is.

DRAFT BANDS  HPF 300 · LPF 16000
             B4  −4 @ 9000  Q 2.0  BELL   see gate check
             B3  −7 @ 400   Q 2.0  BELL   kit box / stage-deck wash — outdoor depth
             B2  −5 @ 1200  Q 2.0  BELL   honk, and keeps four vocals' path clear
             B1  FLAT                     HPF at 300 has already done everything down there

GATE CHECK   **No boosts on this channel at all.** The two places an overhead is normally lifted
             — 5.5 k for stick and 9–10 k for air — are exactly where this capsule's two baked
             peaks sit. Boosting either would stack a voiced peak, so the top of this channel is
             a trim (−4 at 9 k, the one the KB flags as fizz) and nothing else. The 5.5 k peak is
             left alone: at +2 dB it's doing useful work on stick definition and doesn't need
             correcting in a mix this dense.
             **Humidity check:** RH climbs 50% → 77% across the set, so HF carries progressively
             better as the night goes on. A channel with no HF boost in it will not get harsh at
             11 pm; one with a +3 air lift would have.

QUESTIONS    None. (The 9/10 → stereo-fader-9 collapse is a mechanical consequence of the FSQ
             template, not a question — but it is called out in the handover so Brian sees it.)
