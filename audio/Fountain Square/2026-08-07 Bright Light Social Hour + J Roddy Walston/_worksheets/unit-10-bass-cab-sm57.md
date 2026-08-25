# Unit 10 — Bass cab × Shure SM57  [ch 12, both bands]

INSTRUMENT   Ampeg SVT-410HLF (and/or SVT 15e) driven by an SVT-CL. Mic'd for grind and character,
             not for weight.
EQUIP FACT   The 410HLF is ported and horn-loaded: reaches "down to 28Hz" and its 1" compression
             driver runs "up to 4kHz" with an L-Pad (Ampeg / Yamaha London / SamAsh spec). Two
             consequences: (1) the cab's real low end is far below anything a 57 can hear, so the
             mic cannot serve as the low source no matter where it is placed; (2) the horn puts
             genuine 4 kHz energy in front of the mic, landing near the 57's own peak — so the top
             of this channel needs trimming, not adding.
MIC          Shure SM57. Not a ribbon, not TOUR. *** LOCKER FORK L1 RAISED (see plan.md) — built as
             specified pending Brian's keep/swap call. ***
SEARCHES     "SM57 on bass cabinet live sound thin low end 40Hz -10dB blend with DI forum"
             (TalkBass, HomeRecording, PSW thread "How to EQ Bass DI + Bass Cabinet SM57 Mic Combination")
CAPSULE FACT Shure's published curve (user guide v3.6, 2025-A) as carried into the KB after the
             2026-07-26 correction: presence peak at 6–7 kHz, +5 to +7 dB — NOT 3–5 kHz — reached by
             an upward ramp from ~2 kHz (only about +2 dB by 3 kHz), then a dip and a hard rolloff
             above ~10 kHz; about −10 dB at 40 Hz; proximity +6 to +10 dB below 100 Hz at 6 mm; and
             a small dip at 300–600 Hz.
WEB SAYS     Forum consensus is unusually consistent: "The SM57 has a low-end roll-off at about
             200hz so you'll lose some of those real low tones"; "if you're blending the mic'ed
             track with a DI track, then a 57 works great for that. If you're just mic'ing, then use
             something else"; blend it against a low-passed DI to fill the bottom back in.
KB SAYS      mic-library: "Mid-forward workhorse… thin lows, and that 6-7k peak stabs on bright
             transient sources outdoors… box ~400Hz but lighter than reflex."
VERDICT      AGREE — Shure's curve and the forums describe the same mic, and both independently say
             this is a blend mic on bass. The KB's "lighter than reflex" instruction is the direct
             consequence of the measured 300–600 Hz dip.
LOCKER       FORK L1 — SM57 vs Shure PG52. Raised to Brian, three-sentence reason in the round.
             Building to the specified SM57 unless he swaps.
GENRE BEND   BLSH: grind supports a syncopated groove — moderate. JRW: Zepp bass barks in the
             midrange; one more dB of growl.
VENUE BEND   FSQ: the 400 Hz box cut would normally go −7/−8 outdoors, but it is held at −4 because
             the capsule ALREADY dips 300–600 — cutting deep there is the capsule gate in reverse.
             This is a case where the venue rule is deliberately overridden and the reason is on paper.
DRAFT BANDS  BLSH: HPF 150 · LPF OFF · B4 −4 @ 6500 Q2.0 · B3 +3 @ 1600 Q1.4 · B2 −4 @ 400 Q1.8 · B1 FLAT
             JRW:  HPF 140 · LPF OFF · B4 −4 @ 6500 Q2.0 · B3 +4 @ 1600 Q1.4 · B2 −4 @ 400 Q1.8 · B1 FLAT
GATE CHECK   The B4 move is a TRIM sitting exactly on the measured 6–7 kHz peak — with the cab's
             horn feeding 4 kHz into it and 92 % RH delivering all of it, a boost here would be
             indefensible.
             The +3/+4 @ 1600 PASSES: 1.6 kHz is on the flat part of the ramp below the peak (only
             ~+2 dB by 3 kHz per the curve), so it is not stacking a voiced region — and it is below
             the HF band the humidity rule governs.
             Two-source lane split with ch 11: HPF 150/140 is the hard boundary. The DI owns the
             bottom; the 57 owns 1–3 kHz grind. Neither is boosted in the other's lane, and the low
             end is not doubled. Mono/polarity check against the DI at soundcheck — in notes.
QUESTIONS    Which cab is actually mic'd, the 410HLF or the 15e? Changes nothing in the bands (the
             57 is high-passed above both) but belongs on the patch sheet. In notes.
