# Unit 06 — Rack tom 1 (high) × Audix D2 · CH 6

INSTRUMENT   Higher/smaller rack tom. On an R&B/funk/Motown set the toms are fill instruments —
             they appear in transitions and turnarounds, not continuously — so the priority is
             that a fill *lands* clearly through a dance mix rather than that the drum sound
             beautiful in isolation. Part of a three-tom section (ch 6/7/8) with three DIFFERENT
             capsules, which is the dominant fact for this channel.

MIC          Audix D2. Hypercardioid dynamic, VLM diaphragm, **80 Hz–18 kHz**, >144 dB SPL,
             1.2 mV/Pa, no phantom. No switches. Unchanged from rev 1.

SEARCHES     1. `Audix D2 rack tom EQ live frequency response hypercardioid 150Hz body dip 500Hz
                specification`
             2. Audix D2 cutsheet / spec sheet (audixusa.com + RecordingHacks D2 profile)

CAPSULE FACT **Response boost around 150 Hz, a dip between 500 Hz and 1 kHz, and a subtle
             upper-mid presence lift**, over a stated **80 Hz–18 kHz** range (Audix D2 cutsheet
             via RecordingHacks; Thomann and FrontEndAudio spec pages agree). Described as a
             "scooped-mids EQ curve with a larger low-frequency boost than the D4."

WEB SAYS     Audix built the D2 for rack toms specifically, and reviewers are blunt that it
             delivers the expected modern rack-tom sound **without EQ** — "plenty of low end,
             slightly reduced mids, and an assertive attack." The practical consequence for this
             build is that the two moves a tom channel normally gets (boost the body, cut the
             ring) are BOTH already in the capsule.

KB SAYS      mic-library: "Rack-tom hypercardioid: +150 Hz body, dip 500 Hz–1 kHz, subtle
             upper-mid lift. Punchy, articulate. Weakness: leaner deep lows than D4." Bias: ease
             off boom, mud.

VERDICT      **AGREE** — the KB row and the Audix cutsheet carry the identical three features
             (+150, dip 500–1 k, upper-mid lift). Nothing to reconcile.

LOCKER       Silent pass. mic-library: "Audix D2 | Toms — small/mid toms | DP8" — first call for
             this source, and it's the DP8's own rack-tom mic so it comes out of the case already
             assigned to this drum.

GENRE BEND   Funk/R&B fills want attack and pitch, not size. No genre-driven boost survives here
             (see gate check). Artist layer: rehearsed arrangements to a click means fills are
             placed, not improvised — they arrive where the mix expects them, so nothing needs
             over-emphasising to be caught.

VENUE BEND   FSQ outdoor: the box cut gets FSQ depth at −7, but it is placed at **350 Hz, not the
             usual 400–500**, because 500 Hz upward is inside the capsule's own dip — see gate
             check. LPF 12 kHz is cymbal-bleed management, which matters more than usual with
             three cymbal mics plus a stereo OH pair on this kit. HPF 100 sits above the mic's own
             80 Hz floor and above the kick and bass lanes.

DRAFT BANDS  HPF 100 · LPF 12000
             B4  FLAT
             B3  −7 | 350 | 2.0 | BELL
             B2  FLAT
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit, and that is the finding.** This is a
             deliberately light channel because the capsule has already done the work:
             - **No body boost.** Audix bakes a lift at **150 Hz** — exactly where rack-tom body
               sits. Rev 1 carried `B2 +3 | 130` on this channel, which stacks a desk boost onto
               that baked lift. Withdrawn.
             - **No attack boost.** The cutsheet documents a **subtle upper-mid presence lift**,
               and reviewers describe "an assertive attack" out of the box. Rev 1's `B4 +3 | 4000`
               lands inside it. Withdrawn. Dry air (38 % RH) independently says don't trim it
               either — so B4 is FLAT, not cut.
             - **No ring cut in the 500 Hz–1 kHz window.** The capsule already dips there by
               design; cutting into it is the reverse gate's classic double-dip. The box cut is
               therefore moved DOWN to 350 Hz, where the response is not scooped.

TOM SECTION SLOTTING (three toms, three different capsules — the sectional rule in numbers)
             CH 6 Rack 1 · D2 — box cut **350** · body from the baked 150, no boost · B4 flat
             CH 7 Rack 2 · D4 — box cut **450** · weight restored at **110** · 5 k peak TRIMMED
             CH 8 Floor  · D6 — ring cut **300** · note restored at **105** · 4.5 k peak TRIMMED
             No two toms share a cut frequency, no two share a boost frequency, and the reason
             each differs is its own capsule rather than a spread applied for its own sake. The
             template's native tom gate (faders 6/7/8, 130–317 Hz sidechain) handles separation
             *between hits*; this handles it spectrally.

QUESTIONS    None.

TRACE        base(high rack tom on a purpose-built hypercardioid — Audix cutsheet +150 body, dip
             500 Hz–1 kHz, subtle upper-mid lift means body AND attack are both baked) ·
             equip(no tom sizes or heads notated — no rig-driven bend) ·
             genre(funk/R&B fills want attack and pitch over size — but the genre boost is REFUSED
             because the capsule already delivers it) ·
             artist(placed fills in rehearsed arrangements — nothing needs over-emphasis) ·
             venue(FSQ outdoor: box cut at FSQ depth −7 but MOVED to 350 to stay out of the
             capsule's own 500 Hz–1 kHz dip; LPF 12 k for cymbal bleed)
