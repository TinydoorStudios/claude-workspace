# Unit 13 — Congas × Audio-Technica PRO 35  (ch 17 Conga 1, ch 18 Conga 2)

INSTRUMENT   Two congas, clip-miked. This band carries a full percussion chair (congas, bongos,
             toys) on top of a drum kit — in R&B/funk that percussion is the top-end movement
             that makes the groove feel live rather than programmed. Two drums of different
             pitch: conga 1 is the higher (quinto/conga), conga 2 the lower (tumba). No sizes
             notated; the generic two-drum baseline carries.

MIC          Audio-Technica PRO 35 ×2 — clip-on cardioid condenser, 48V, clip mount (no stands).
             KB tendency: "50 Hz–15 kHz (limited top), voiced presence lift, clamp mount.
             Weakness: rolled-off extreme top, thin lows, plasticky upper-mid if close. → ease
             off presence."
             **Switchable hardware: the AT8538 in-line power module carries a flat / 80 Hz
             roll-off switch. ASSUMED FLAT.** The desk owns the low end so it can be ridden.
             Fallback if the switches are found in the roll-off position: the mic is already
             doing 18 dB/oct from 80 Hz, so drop the desk HPF to ~90 or the drums will get thin.

SEARCHES     1. `Audio-Technica PRO 35 conga percussion live EQ frequency response clip-on
                cardioid presence peak dB`
             2. `Audio-Technica PRO 35 frequency response curve presence peak 8kHz 10kHz dB
                rise AT8538 80Hz rolloff switch`
             3. `conga bongo live sound EQ high pass 120Hz slap 5kHz ring 400Hz percussion
                mixing live band`
             4. Fetched the RecordingHacks PRO 35 page; the AT spec PDF returned 403 so the
                numbers below come from AT's own product copy as quoted by RecordingHacks,
                Thomann and Equipboard.

CAPSULE FACT **50 Hz – 15 kHz**, cardioid, **145 dB max SPL** (115 dB dynamic range), and a
             switchable **80 Hz roll-off at 18 dB/octave** in the AT8538 power module (AT spec,
             via RecordingHacks/Thomann). The 15 kHz ceiling is the number that matters: this
             capsule is *done* above 15 k, so there is no air to reach for on this channel.

WEB SAYS     Live conga consensus: fundamental/resonance sits **200–260 Hz**, with harmonics at
             **400 Hz and 700 Hz**; slap and presence live **2–4 kHz**, with the sharpest slap
             attack up at **5 kHz**. Standard live treatment is a high-pass around 120 Hz plus
             gating/compression to bring the slap forward. The 400 Hz harmonic is the ring that
             makes congas boxy in a dense mix.

KB SAYS      mic-library (PRO 35): voiced presence lift, thin lows, "plasticky upper-mid if
             close" → ease off presence. eq-starting-points percussion: conservative, let the
             instrument speak, cut the ring rather than boost the attack.

VERDICT      **AGREE.** Both sides say the same thing from opposite directions — the web says
             congas ring at 400 and slap at 2–5 k; the KB says this capsule *adds* upper-mid and
             gets plasticky close in. Together they point at one answer: cut the ring, and do
             not boost the slap region this capsule is already lifting.

LOCKER       **Silent pass.** The PRO 35 is the locker's clip-on for percussion and brass
             (mic-library: "Drums/brass", clamp mount) and it's the only clip-on pair free —
             the DPA 4099s are the alternative but they're the string/piano/brass call and would
             be a lateral move on congas at best. No fork.

GENRE BEND   R&B/funk: percussion is the sparkle and the syncopation. It needs slap definition
             and *no* low weight — the kick, bass and floor tom already own everything below
             150 Hz and the congas adding to it is exactly how an outdoor mix turns to soup.
             Artist layer: with programmed percussion in the Track channel, the live congas need
             to read as human hands, which means the slap transient matters more than the tone.

VENUE BEND   FSQ outdoor, gusts to 16 mph: clip-on condensers on drum shells are less
             wind-exposed than boom-mounted mics, but the HPF still runs above the researched
             120 — at 140 for conga 1 and 120 for conga 2 — because on a plaza the low-mid
             region is pure liability on a percussion channel.

DRAFT BANDS  **ch 17 Conga 1 (higher drum)**
             HPF 140 · LPF 15000
             B4  FLAT                     nothing above 15 k to reach for — see gate check
             B3  −7 @ 400   Q 2.0  BELL   the ring harmonic — outdoor depth
             B2  −4 @ 2500  Q 2.0  BELL   the capsule's own presence lift — see gate check
             B1  +3 @ 240   Q 1.5  BELL   resonance/tone, top of the researched band

             **ch 18 Conga 2 (lower drum)**
             HPF 120 · LPF 15000
             B4  FLAT
             B3  −7 @ 350   Q 2.0  BELL   ring, its own lane below conga 1's
             B2  −4 @ 2000  Q 2.0  BELL   presence lift tamed, a step below conga 1's
             B1  +3 @ 200   Q 1.5  BELL   resonance, bottom of the researched band

GATE CHECK   **B4 stays FLAT on both — deliberately.** The instinct on percussion is to reach
             for air. This capsule stops at 15 kHz, so there is nothing up there to lift: a
             high boost would just amplify the capsule's own rolloff shoulder and the plaza's
             noise floor. The LPF is set at 15 k to match the mic rather than pretend otherwise.
             **Gate in reverse — B2 −4 at 2500 / 2000.** The research says slap lives 2–4 kHz
             and every generic percussion chart says boost it. This capsule already has a voiced
             presence lift there and the KB's specific warning is "plasticky upper-mid if
             close" — clip-on means close. So the correct move is a **trim, not a boost**, and
             the slap comes from the transient rather than from EQ. This is the single clearest
             capsule-gate reversal in the show.
             **Boost audit — B1 +3 @ 240 / 200.** The 200–260 Hz resonance band is the
             instrument's own fundamental, not a capsule peak, and the PRO 35's documented
             weakness is *thin lows* — so a modest lift there is filling a real hole. Held to +3
             because everything below 150 belongs to other channels.
             **Sectional separation (ch 17 vs ch 18):** tone at 240 vs 200, ring at 400 vs 350,
             presence trim at 2.5 k vs 2 k, HPF 140 vs 120. The two drums descend together
             across all four moves, so a conga pattern reads as two pitches.

QUESTIONS    None.
