# Unit 14 — Bongos × Shure SM57  (ch 19)

INSTRUMENT   Bongos — the highest-pitched drums on the stage, played as syncopated accents over
             the congas. In R&B/funk they're a sparkle instrument: they need to be heard through
             a dense mix and a big crowd without turning into a stab.

MIC          Shure SM57 — cardioid dynamic, no 48V, Short/boom stand between the two drums.
             KB tendency: "mid-forward workhorse, presence 3–5 kHz, proximity-prone. On
             cabs/snare builds box/honk 300–500 Hz. Weakness: thin lows, can be honky/harsh in
             upper mids → tame box ~400 Hz."

SEARCHES     1. `SM57 bongos live percussion EQ presence 3-5kHz proximity 400Hz box shure spec`
             2. `conga bongo live sound EQ high pass 120Hz slap 5kHz ring 400Hz percussion
                mixing live band` (shared with unit 13)
             3. Fetched and read the **Shure SM57 user guide, version 3.6 (2025-A)** — the
                official frequency-response curve and the proximity-effect section.

CAPSULE FACT Straight off Shure's own published curve: **40 – 15,000 Hz**, essentially flat from
             200 Hz to about 1 kHz, rising to a **presence peak of roughly +5 to +6 dB centred
             around 6–7 kHz**, then dipping and rolling off hard above ~10 kHz. The low end is
             **about −10 dB at 40 Hz**. Shure's own proximity note: a cardioid at 6 mm boosts
             **bass by 6 to 10 dB below 100 Hz**.

WEB SAYS     Shure's own application guidance puts the 57 on higher-pitched percussion for its
             transient handling and SPL capability. The live percussion consensus (shared with
             unit 13): resonance 200–260 Hz, presence/slap 2–4 kHz, sharp slap at 5 kHz, ring
             harmonics at 400 and 700 Hz.

KB SAYS      mic-library: presence 3–5 kHz, box/honk builds at 300–500 Hz, thin lows,
             proximity-prone → tame box ~400 Hz.

VERDICT      **DISAGREE — on where the presence peak sits.** The KB says 3–5 kHz; Shure's
             published curve peaks at **6–7 kHz** and is only up ~+2 dB by 3 kHz. Both describe
             the same rising slope, but they'd send you to different frequencies with a trim.
             I'm going with the manufacturer's measured curve — it's the primary source and this
             is a measurement question, not a judgment one. → **question round** with the three
             options: (a) take the 6–7 k figure, (b) keep the KB's 3–5 k, or (c) take the 6–7 k
             figure **and update the mic-library SM57 row**, which is my recommendation. This
             one is worth resolving because the SM57 is the most-used mic in the locker — the
             row is wrong on 21 channels' worth of past specs.

LOCKER       **Silent pass.** The SM57 is the locker's stated utility/percussion workhorse
             ("Snare (primary), guitar cab (primary), **utility anywhere**") and Shure's own
             guide names higher-pitched percussion as a use case. The nearest alternative, the
             AT PRO 6L, is a smoother-mid 57 substitute — and smoother mids is not what a bongo
             accent needs. No fork.

GENRE BEND   R&B/funk: bongos punctuate. They want attack and pitch, no body, and they must not
             compete with the four vocals sitting above them or the congas sitting below them.
             Artist layer: programmed percussion is already in the Track channel, so the live
             bongos exist to be *heard as hands* — transient, not tone.

VENUE BEND   FSQ outdoor: nothing below the drums' own pitch is wanted, and a 57 close-miked on
             a bongo stand will be collecting stage thump through the floor. HPF at 200, well
             above the researched 120 floor for hand percussion, and the box cut at outdoor
             depth.

DRAFT BANDS  HPF 200 · LPF 15000
             B4  −4 @ 6000  Q 2.0  BELL   the capsule's own presence peak — see gate check
             B3  −7 @ 450   Q 2.0  BELL   box/ring — the 57's known build-up, outdoor depth
             B2  +3 @ 300   Q 1.5  BELL   bongo tone, its own slot above the congas
             B1  FLAT                     HPF owns it; the capsule is −10 dB at 40 anyway

GATE CHECK   **Gate in reverse — B4 −4 @ 6000.** Every percussion EQ chart says boost 5 kHz for
             slap. This capsule already delivers **+5 to +6 dB at 6–7 kHz** by Shure's own
             measurement, and a bongo is the brightest source on the stage. Boosting there would
             be stacking a documented peak on an already-piercing instrument in a venue with no
             room to soften it. So the move is a **trim**, and the slap comes from the transient.
             This is the trim the KB's 3–5 kHz figure would have put in the wrong place — which
             is exactly why the disagreement above is worth resolving.
             **Boost audit — B2 +3 @ 300.** The 57 is flat from 200 Hz to 1 kHz, so there's no
             peak here to stack. It's a genuine lift into a flat region, filling the tone the
             HPF at 200 takes off the bottom.
             **Sectional separation (percussion trio):** conga 2 at 200, conga 1 at 240, bongos
             at 300 — three pitches, three slots, ascending. Ring cuts at 350 / 400 / 450 do the
             same. Nothing is a copy of anything.

QUESTIONS    1. SM57 presence-peak fork — 6–7 kHz (Shure's curve) vs the KB's 3–5 kHz, and
                whether to update the mic-library row. Recommend (c).
