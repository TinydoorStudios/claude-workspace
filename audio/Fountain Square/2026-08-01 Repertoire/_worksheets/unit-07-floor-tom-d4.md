# Unit 07 — Floor tom × Audix D4  (ch 8)

INSTRUMENT   Floor tom. Size unknown (no rider). Role: the bottom of the fills and the
             occasional tribal groove figure R&B covers reach for.
MIC          Audix D4 (DP8). Hypercardioid dynamic, VLM diaphragm, no switches, 144 dB SPL.
             KB tendency: "ease off boom, mud."
SEARCHES     "Audix D2 D4 tom mic frequency response hypercardioid peak dB live EQ specification"
             → recordinghacks.com/microphones/Audix/D4, audixusa.com/products/d4,
               bhphotovideo.com D4 listing, homerecording.com "Differnece between Audix D2 and D4"
CAPSULE FACT **+6 dB at 5 kHz with a secondary peak above 10 kHz, and a low-frequency rolloff
             below 70 Hz.** Range 38 Hz–19 kHz, max SPL 144 dB.
             Source: RecordingHacks Audix D4, reading Audix's *current* published chart.
WEB SAYS     Marketed and used as the low-source Audix — more low-end extension than the D2.
             The current chart, though, shows the presence peak is real and sits at 5 kHz, and
             that the mic rolls off below 70 Hz rather than reaching flat into the 30s.
KB SAYS      mic-library: "Floor-tom/low source: flat to ~63Hz, rise ~80Hz, **reaches 35Hz**,
             smooth 800Hz-1kHz (not scooped). Deep, resonant. Weakness: **less upper-mid attack
             — may need a touch of click.**"
VERDICT      **DISAGREE** — and on both ends of the spectrum at once. The KB says the D4 reaches
             35 Hz and lacks upper-mid attack, inviting a click boost. RecordingHacks' reading of
             Audix's current chart says it rolls off below 70 Hz and already has +6 dB at 5 kHz,
             which forbids one. These cannot both be true. Carried to the question round with
             the (a)/(b)/(c) fork; **this draft follows the research**, because the published
             range (38 Hz–19 kHz) and a current manufacturer chart outrank a character line, and
             because the failure mode of being wrong the other way — a click boost stacked on a
             +6 dB baked peak, outdoors, at 96% RH — is the worse one.
LOCKER       Silent pass. mic-library: "Floor tom — more low-end extension than D2." First call,
             and it is the DP8's floor-tom mic. The MD 421-U would be the alternative but its
             own KB row makes it the *rack* tom first choice and it brings a 200–400 Hz bloat
             this outdoor build does not want.
GENRE BEND   R&B floor tom is weight — a low, round thud under a fill. No attack boost, which is
             the same conclusion the research reaches by a different route.
VENUE BEND   FSQ: HPF 60, box cut at FSQ depth (−7 @ 300). No room gain to supply floor-tom
             weight, and the capsule rolls off below 70 — which is what makes the one boost on
             this channel legitimate rather than a stack.
DRAFT BANDS  HPF 60 · LPF 10000
             B4  −3 | 5000 | 2   | BELL
             B3  −5 | 700  | 2   | BELL
             B2  −7 | 300  | 2   | BELL
             B1  +3 | 80   | 1.2 | BELL
GATE CHECK   One boost: **B1 +3 @ 80.** Permitted because the capsule *rolls off* below 70 Hz
             (RecordingHacks / Audix current chart) — this is restoring weight the mic does not
             deliver, not adding to something it does. It is also the only place FSQ can get
             floor-tom body, since an open plaza supplies no room reinforcement.
             B4 is a **trim, not a boost**, and this is the whole point of the DISAGREE above:
             the KB's "may need a touch of click" would have produced a +3 @ 5000 landing
             directly on a +6 dB baked peak. Under the research reading it becomes −3.
QUESTIONS    Web↔KB fork on the D4 row — see the question round, options (a) research /
             (b) KB / (c) research + fix the KB row.
TRACE        base(D4 — +6 dB @ 5 kHz baked, rolloff below 70 Hz, RecordingHacks/Audix chart) ·
             equip(floor tom size unknown, no rider — generic carries) ·
             genre(R&B — weight not attack, which agrees with the research reading) ·
             artist(no change) ·
             venue(FSQ — HPF 60, box −7 at outdoor depth, and the +3 @ 80 exists because an
             open plaza gives back nothing)
