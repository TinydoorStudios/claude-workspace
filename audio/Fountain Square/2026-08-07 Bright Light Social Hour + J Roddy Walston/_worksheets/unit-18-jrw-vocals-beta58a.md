# Unit 18 — Vocals ×4 × Shure Beta 58A (house wireless)  [JRW ch 33/34/35/36]

INSTRUMENT   Four wireless vocals. Sheet's wireless block maps them:
                W1 → fader 33  BGV 1
                W2 → fader 34  Roddy 1   ─┐ same singer, TWO POSITIONS (Brian confirmed)
                W3 → fader 35  Roddy 2   ─┘
                W4 → fader 36  BGV 2
EQUIP FACT   House wireless 1–4 live on FSQ faders 33–36 and carry Beta 58A capsules — confirmed
             against the patcher's surface-label table and the 2nd Wind Conclave build, not just
             assumed. Two mics on one singer means ch 34 and ch 35 are the same VOICE but not the
             same SITUATION: the second position is further from its source and more open, so it
             collects more stage and more mud even with identical capsules.
MIC          Shure Beta 58A ×4, supercardioid dynamic. Not ribbons, not TOUR (house).
SEARCHES     "Shure Beta 58A frequency response presence peaks 4kHz 10kHz supercardioid gain before feedback spec sheet"
             (Shure spec sheet + Music On Stage technical analysis + HigherHz)
CAPSULE FACT Shure spec sheet: 50–16,000 Hz, supercardioid. Music On Stage / HigherHz: "two presence
             peaks at 4 kHz and 10 kHz", with "a pronounced presence peak between 4kHz and 9kHz —
             significantly more aggressive than the SM58's gentler presence lift"; Shure: the true
             supercardioid pattern is maintained "throughout its frequency range, which ensures high
             gain before feedback, maximum isolation from other sound sources, and minimum off-axis
             tone coloration".
WEB SAYS     More bite and more output than a 58; those peaks can get strident on a loud singer.
KB SAYS      mic-library: "Supercardioid vocal dynamic, 50Hz-16kHz, <500Hz attenuated for proximity
             control, TWO presence peaks (~4kHz and ~10kHz)… Weakness: those peaks can get
             strident/sibilant." → ease off presence; tame box ~600 Hz.
VERDICT      AGREE — both peaks confirmed at the same frequencies on both sides.
LOCKER       House wireless capsules — no swap available or sensible. No fork.
GENRE BEND   Roddy is a rock-and-roll shouter in a Zeppelin-meets-'50s band; the voice is raspy and
             loud and lives right on the capsule's 4 kHz peak. That makes 4 kHz the single harshest
             thing in this band's mix and the primary control point.
VENUE BEND   The FSQ template ships faders 25–36 at HPF 184 Hz. *** That is flatly wrong for a male
             rock voice and is overridden on all four channels *** — a male voice's fundamentals run
             well below 184. RH 92 % climbing across the set → all four de-essers DYNAMIC.
DRAFT BANDS  ch 34 Roddy 1: HPF  90 · B4 −3 @  4000 Q2.5 +DEQ · B3 −4 @ 1500 Q1.8 · B2 −6 @ 400 Q2.0 · B1 FLAT
             ch 35 Roddy 2: HPF 100 · B4 −3 @  4000 Q2.5 +DEQ · B3 −4 @ 1500 Q1.8 · B2 −7 @ 400 Q2.0 · B1 FLAT
             ch 33 BGV 1:   HPF 100 · B4 −3 @ 10000 Q2.5 +DEQ · B3 −4 @ 1200 Q1.8 · B2 −6 @ 350 Q2.0 · B1 FLAT
             ch 36 BGV 2:   HPF 105 · B4 −3 @ 10000 Q2.5 +DEQ · B3 −4 @ 2000 Q1.8 · B2 −6 @ 380 Q2.0 · B1 FLAT
             DEQ on all four: thr −18 dB, atk 3 ms, rel 120 ms.
GATE CHECK   ZERO boosts — cuts-only, and both presence peaks are baked, so every B4 is a trim.
             SLOTTING, visible in the numbers:
               · Roddy's PAIR is trimmed at 4000 — the lead lane, where his voice and the capsule
                 peak collide. Same voice, so 34 and 35 share the curve by design.
               · The two BGVs are trimmed at 10000 instead — the OTHER baked peak — so they are
                 controlled without being cut in Roddy's lane, and they sit behind him rather than
                 competing.
               · The BGVs are then separated from EACH OTHER at B3: 1200 vs 2000, two different
                 nasal lanes.
               · ch 35 differs from ch 34 only where the SITUATION differs, not where the voice
                 does: HPF 100 vs 90 and B2 −7 vs −6, because an open second-position mic across
                 the stage collects more low-mid. Identical everywhere else, correctly.
*** TEMPLATE OVERRIDE — MUST RING OUT ***
             Same as unit 16: faders 33–36 ship HPF 184, B4 −18 @ 5024 Q20 feedback notch, B2 −6.3
             @ 335, B1 +0.5 @ 189 (read from the installed template). Every one of these four
             channels overrides the HPF and writes a B4, which REMOVES the notch. Ring out all four.
QUESTIONS    none — Brian confirmed two positions.
