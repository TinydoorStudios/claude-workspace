# Unit 06 — Toms × Audix D2  [ch 6 + ch 7, both bands]

INSTRUMENT   *** BACKLINE / INPUT-SHEET MISMATCH — the most consequential find in the intake. ***
             The input sheets say "Rack 1 / Rack 2 / Floor". The backline quote ships ONE rack tom
             (10"D × 13"W on a DW9900 mount) and TWO floor toms (14"D × 16"W and 16"D × 18"W, each
             on three DW floor-tom legs). So the real map is:
                ch 6 "Rack 1" = 13" RACK tom      → D2 (correct mic for the job)
                ch 7 "Rack 2" = 16" FLOOR tom     → D2 (a small/mid-tom mic on a floor tom)
                ch 8 "Floor"  = 18" FLOOR tom     → D4  (unit 07)
             ch 7 is the problem child and is built as a floor tom, not as a second rack.
EQUIP FACT   A 16" floor tom's fundamental sits around 90–110 Hz — below the D2's own low bump,
             which is what makes the pairing thin. A 13" rack sits nearer 150–170 Hz, right on it.
MIC          Audix D2, hypercardioid dynamic. Not a ribbon, not TOUR.
SEARCHES     "Audix D2 frequency response peaks dips polar pattern max SPL" → RecordingHacks D2 (fetched)
CAPSULE FACT RecordingHacks: 44–18,000 Hz, hypercardioid, 144 dB max SPL, 2.5 mV/Pa, and the curve
             is described as "a scooped-mids EQ curve, with a larger low-frequency boost than the D4".
WEB SAYS     Punchy and articulate on small/mid toms; the mid scoop does the separation work for you.
KB SAYS      mic-library: "Rack-tom hypercardioid: +150Hz body, dip 500Hz-1kHz, subtle upper-mid
             lift. Punchy, articulate. Weakness: leaner deep lows than D4." → ease off boom, mud.
VERDICT      AGREE — "larger LF boost than the D4" and "leaner deep lows than D4" are the same fact
             seen from two ends: the bump is higher up (≈150 Hz), so the DEEP low is where it runs
             out. That is precisely why ch 7 needs help and ch 6 does not.
LOCKER       First call for the 13" rack ("Audix D2 — Toms, small/mid toms"). For ch 7 the honest
             better mic is the D4 — but the D4 is committed to the 18" floor and there is only one,
             so no free alternative exists. No fork raised; the shortfall is handled in EQ and named
             in `changes`.
GENRE BEND   BLSH: toms are melodic/groove figures inside a dense mix — cut mud harder for clarity.
             JRW: Zepp toms are the point — big, resonant, allowed to bloom. Cut LESS mud on both
             tom channels and give ch 7 a bigger low placement.
VENUE BEND   FSQ: mud cuts deep. BUT the 500 Hz–1 kHz zone is already SCOOPED by the capsule, so the
             cut there is held to −5/−6 rather than the −8 the venue rule would otherwise ask for —
             capsule gate in reverse.
DRAFT BANDS  ch 6 (13" rack)
               BLSH: HPF 90 · LPF OFF · B4 FLAT · B3 −6 @ 500 Q1.8 · B2 −5 @ 300 Q1.8 · B1 FLAT
               JRW:  HPF 80 · LPF OFF · B4 FLAT · B3 −5 @ 500 Q1.8 · B2 −4 @ 300 Q1.8 · B1 FLAT
             ch 7 (16" floor on a D2)
               BLSH: HPF 65 · LPF OFF · B4 FLAT · B3 −6 @ 500 Q1.8 · B2 −6 @ 300 Q1.8 · B1 +3 @ 100 Q1.2
               JRW:  HPF 60 · LPF OFF · B4 FLAT · B3 −5 @ 500 Q1.8 · B2 −4 @ 300 Q1.8 · B1 +4 @ 100 Q1.2
GATE CHECK   ch 6 — no boosts. A low bell at ~150 was drafted and REMOVED: that is exactly where the
             D2's own low bump lives, so it would have been a boost stacked on a voiced region.
             ch 7 — the +3/+4 @ 100 PASSES the gate, and here is why: the capsule's bump is at
             ≈150 Hz and its deep low is the documented weakness, so 100 Hz is below the voiced
             region, on the falling side of the curve. This is placing weight where the mic runs
             out, not reinforcing what it already does. B4 stays FLAT on both toms — the D2's
             "subtle upper-mid lift" plus 92 % RH means any attack boost would stack.
QUESTIONS    none — the mismatch is a build note + `changes` entry, not a fork.
