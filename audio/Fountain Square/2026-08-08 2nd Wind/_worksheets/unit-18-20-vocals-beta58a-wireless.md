# Units 18–20 — Four handheld vocals × Shure Beta 58A (house wireless) · CH 33/34/35/36

INSTRUMENT   Four featured vocalists who front the show and work the crowd — **Aretha** (also MCs),
             **Heather**, **Vince**, and **Brandon** (NEW this week, replacing Markay). On an
             R&B/funk/Motown set the vocal IS the show: leads trade, harmonies stack, and all four
             mics are live most of the night on an open plaza. **Gain-before-feedback is the
             governing constraint of this entire build.**
             Three units by voice type: 18 = female lead (33, 34) · 19 = male bass-range (35) ·
             20 = male, range TBD (36).

MIC          Shure Beta 58A × 4, house wireless handhelds on the FSQ template's reserved faders
             **33/34/35/36 = Wireless 1/2/3/4**. Supercardioid dynamic, 50 Hz–16 kHz, no phantom.
             **EXEMPT from the locker fork** — fixed house rig, not a per-show mic choice.
             No mults: no band input on this list names a wireless unit.
             Capsule identity is a carried assumption Brian renewed in the round.

SEARCHES     1. `Shure Beta 58A frequency response chart presence peak dB supercardioid proximity
                effect live vocal EQ`
             2. Shure Beta 58A specification sheet (content-files.shure.com) + SoundRef Beta 58A
                review + MusicOnStage technical analysis

CAPSULE FACT **Two high-frequency presence peaks — one at 4 kHz and one at 10 kHz — with a
             pronounced presence region between 4 kHz and 9 kHz, significantly more aggressive than
             an SM58's**, over a **50 Hz–16 kHz** response, and **frequencies attenuated below
             500 Hz to counter the proximity effect** with a rolloff steeper than the SM58's
             (Shure spec sheet; MusicOnStage technical analysis; SoundRef review). The consequence
             reviewers name explicitly: "the presence peak enhances consonants and sibilance…
             singers with naturally bright or thin voices may find the presence peak emphasises
             sibilance excessively."

WEB SAYS     Three things that set every value below. (1) The **10 kHz peak is why the de-essers
             exist** — it is a capsule artifact sitting exactly where sibilance lives. (2) The
             **4 kHz peak is why no vocal on this show gets a presence boost** — beyond the
             cuts-only rule, there is nothing to add. (3) The **sub-500 Hz attenuation** means the
             capsule has already begun the low-mid work, so the box cuts are placed with a TIGHT Q
             rather than broadened — see gate check.

KB SAYS      `eq-starting-points` and the root CLAUDE.md: **vocals are cuts-only in every genre**,
             feedback control rather than taste. FSQ-specific: the template's wireless faders
             25–36 ship a baseline vocal/wireless curve — HPF 184, a −18 @ 5 k Q20 feedback notch,
             and a −6.3 @ 335 — and a vocal MD override **replaces all of it**. Auto-memory
             (`vocal-slotting-by-voice-type`): slot multi-vocal shows **by voice type, not
             hierarchy**, and the template's HPF 184 was flatly wrong for Vince, whose fundamentals
             reach ~82 Hz.

VERDICT      **AGREE.** Web (4 k and 10 k peaks, sub-500 attenuation, sibilance warning) and KB
             (cuts-only, de-ess the 10 k region dynamically, don't trust the template's 184) point
             the same way and reinforce each other.

LOCKER       **Exempt** ×4 — fixed house wireless rig. No forks, no packet lines.

GENRE BEND   R&B/funk/soul/Motown: the vocal must be forward and intelligible over a loud dance
             band, and gospel-adjacent material means big sustained notes and runs. The genre wants
             presence — and cannot have it as a boost, so it is bought by *clearing the masking
             band on every other channel* instead. That is why the keys are cut at 300, the guitar
             at 300 and 800, the bass at 250, and why the sampling pads and Track get room-making
             cuts: five instrument channels are cleared so four vocals can sit forward without a
             single dB of vocal boost. Artist layer: they back Kirk Whalum, The Whispers, Fantasia,
             Charlie Wilson and the Clark Sisters — a lineage where the vocal is unambiguously the
             feature.

VENUE BEND   FSQ outdoor, four open handhelds, no room gain, and the tightest gain-before-feedback
             margin on the show. Box cuts run at FSQ depth. **RING OUT AT SOUNDCHECK** — the MD
             removes the template's 5 kHz feedback notch, so that protection is gone and has to be
             re-earned by hand. Weather layer: 38 % RH and dry all evening. On a static band that
             would argue for lightening the HF trim; here the HF work is on **dynamic** bands, which
             only act when sibilance actually arrives, so the dry-air argument is much weaker and
             the de-essers stay at −3. Gusts 15–16 mph: **windscreens on all four**, and the
             high HPFs help.

DRAFT BANDS  All four cuts-only. All four de-essers **DYNAMIC**, not static.

             **CH 33 — Aretha** (female lead + MC)
             HPF 130 · LPF 16000
             B4 −3 | 10000 | 2.0 | BELL | DEQ thr −18 atk 3 ms rel 80 ms
             B3 −2 |  1600 | 1.8 | BELL
             B2 −6 |   600 | 2.0 | BELL
             B1 FLAT

             **CH 34 — Heather** (female)
             HPF 140 · LPF 16000
             B4 −3 |  9500 | 2.0 | BELL | DEQ thr −18 atk 3 ms rel 80 ms
             B3 −3 |  1800 | 1.8 | BELL
             B2 −6 |   550 | 2.0 | BELL
             B1 FLAT

             **CH 35 — Vince** (male, bass-range)
             HPF 90 · LPF 16000
             B4 −2 |  8500 | 2.0 | BELL | DEQ thr −18 atk 3 ms rel 80 ms
             B3 −4 |   700 | 2.0 | BELL
             B2 −7 |   350 | 2.0 | BELL
             B1 FLAT

             **CH 36 — Brandon** (male, range UNKNOWN — ⚑ LOAD-IN FLAG)
             HPF 105 · LPF 16000
             B4 −3 |  9000 | 2.0 | BELL | DEQ thr −18 atk 3 ms rel 80 ms
             B3 −3 |  1100 | 1.8 | BELL
             B2 −6 |   450 | 2.0 | BELL
             B1 FLAT
             **Printed alternates on his EQ page — a 20-second change once he's heard:**
             · if BARITONE / bass-baritone (like Vince): HPF **95** · B3 −4 @ **750** · B2 −7 @ **400**
             · if TENOR / upper-range (like Markay): HPF **120** · B3 −3 @ **1400** · B2 −6 @ **500**

GATE CHECK   **Zero boosts across all four channels.** Two independent reasons, and both must hold:
             - **The rule:** vocals are cuts-only in every genre, for feedback control. Non-
               negotiable, and with four open handhelds on a plaza it is the whole ballgame.
             - **The capsule:** the Beta 58A bakes presence peaks at **4 kHz and 10 kHz** with a
               pronounced 4–9 kHz region. Even if the rule permitted a boost, there is nothing to
               add — the capsule is already more aggressive up there than an SM58.
             - **The de-essers are trims on a measured capsule artifact,** not taste. The 10 kHz
               peak only misbehaves on sibilants, which is exactly why all four bands are DYNAMIC
               rather than static: a static value set at 7 pm in 38 % RH would be wrong by 10 pm at
               60 %, and a dynamic band tracks that on its own.
             - **B2 box cuts use a tight Q 2.0 deliberately.** The capsule already attenuates below
               500 Hz to fight proximity effect, so a broad low-mid cut would double-dip that
               rolloff. FSQ depth is kept (a plaza needs it) but the bandwidth is narrow so it
               removes box without hollowing the chest voice.
             - **B1 FLAT on all four** — nothing to add at the bottom of a handheld, ever.

VOCAL SLOTTING — by voice type, not hierarchy (no two channels share a value in any band)
             | | Vince (35) | Brandon (36) | Aretha (33) | Heather (34) |
             |---|---|---|---|---|
             | HPF | **90** | **105** | **130** | **140** |
             | Box (B2) | **350** | **450** | **600** | **550** |
             | Upper-mid (B3) | **700** | **1100** | **1600** | **1800** |
             | De-ess (B4) | **8500** | **9000** | **10000** | **9500** |
             **Vince's upper-mid cut sits at 700 Hz — BELOW his presence region — on purpose.** For
             a bass voice, cutting inside 1.2–1.8 kHz removes the intelligibility he depends on; the
             other three are cut inside that nasal window because their presence regions sit higher.
             **Brandon is placed BETWEEN Vince and the women** rather than on top of either: HPF 105
             and box 450 sit in the gap, so whichever way his voice turns out, he is not colliding
             with an already-slotted channel — and the alternates move him without displacing anyone.
             **Nobody gets HPF 184.** The template's baseline is removed on all four.

QUESTIONS    None open. Q5 (Brandon's range) was answered "don't know — he's new", which is why this
             channel ships with a flag and printed alternates rather than a guess dressed up as a
             value.

TRACE        base(four handheld vocals on a supercardioid dynamic — Shure/MusicOnStage: presence
             peaks at 4 k and 10 k, sub-500 Hz attenuation for proximity. Cuts-only, de-ess the
             10 k artifact dynamically, tight-Q box cuts) ·
             equip(house wireless on reserved faders 33–36, no mults; windscreens for 15–16 mph
             gusts) ·
             genre(R&B/funk/Motown wants the vocal forward — bought by clearing FIVE instrument
             channels' masking bands rather than by any vocal boost) ·
             artist(four featured vocalists who trade leads; Whalum/Whispers/Fantasia/Clark Sisters
             backing lineage = vocal is the feature; Brandon is NEW, so ch 36 ships flagged with
             both alternate slots printed) ·
             venue(FSQ outdoor, tightest feedback margin on the show: FSQ-depth box cuts at tight Q,
             template HPF 184 + 5 k notch + 335 cut all REMOVED, RING OUT AT SOUNDCHECK; 38 % RH dry
             air did NOT lighten the de-essers because they are dynamic and self-regulating)
