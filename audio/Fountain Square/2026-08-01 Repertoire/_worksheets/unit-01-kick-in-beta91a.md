# Unit 01 — Kick In × Shure Beta 91A  (ch 1)

INSTRUMENT   Acoustic kick, R&B/neo-soul covers. Size unknown (no rider). Role: the floor of
             the groove, but NOT the sub — the drum pad on ch 4 is assumed to carry 808-class
             content and the two must split the bottom.
MIC          Shure Beta 91A. Half-cardioid boundary condenser, lies inside on the batter-side
             head. Two-position contour switch — **ASSUMED FLAT**; if it's engaged the desk's
             400 Hz cut halves. KB tendency: "ease off boom; tame box ~400Hz."
SEARCHES     "Shure Beta 91A kick drum frequency response boundary contour switch EQ live sound"
             → shure.com/en-US/products/microphones/beta_91a, recordinghacks.com/microphones/Shure/Beta-91A
             (fetched the RecordingHacks page directly for the contour figure)
CAPSULE FACT **Emphasis from 4 kHz to ~9 kHz for beater attack; the contour switch attenuates
             400 Hz by 7 dB.** Range 50 Hz–15 kHz, sensitivity 3.8 mV/Pa, max SPL 155 dB.
             Source: Shure USA Beta 91A product page + RecordingHacks Beta 91A.
WEB SAYS     Boundary mounting gives solid low end with a pronounced beater click; the 400 Hz
             contour exists because that is how engineers EQ it anyway. Cleaner, smoother top
             than a dynamic kick mic, so it needs less EQ to cut. Picks up shell boxiness
             300–500 Hz from being inside the drum.
KB SAYS      mic-library: "Half-cardioid boundary kick/piano mic. Solid boundary low end +
             pronounced beater click; nominally flat (contour switch cuts 7dB@400 if engaged).
             Weakness: picks up shell boxiness ~300-500." Identical figure, identical weakness.
VERDICT      **AGREE** — the KB's 7 dB @ 400 Hz contour figure and the 300–500 box weakness both
             match Shure's own published copy exactly.
LOCKER       First-call match. mic-library lists the Beta 91 as the attack layer of the standard
             two-mic kick rig ("Beta 52 (body/thump, inside) + Beta 91 (attack/click, on head)").
             No fork.
GENRE BEND   R&B/neo-soul wants a round, deep kick with a defined but unaggressive click — the
             beater should be audible, not rock-spiky. So the 4–5 kHz part of the baked emphasis
             stays untouched and only the 8–9 kHz fizz end comes down.
VENUE BEND   FSQ: no room gain, KS21 arch owns everything under ~45 Hz → HPF 50, and this
             channel takes NO low boost at all (ch 2 owns the bottom). 96% RH means the 8–9 kHz
             bleed arrives intact rather than being eaten by air, so the trim is real, not
             cosmetic. Gusts don't reach inside a kick drum.
DRAFT BANDS  HPF 50 · LPF 9000
             B4  −4 | 8500 | 2   | BELL
             B3  −8 | 400  | 2   | BELL
             B2  −6 | 250  | 1.8 | BELL
             B1  FLAT
GATE CHECK   **No boosts on this channel** — nothing to justify. The 4–9 kHz region is baked in
             by the capsule, so the desk trims (−4 @ 8500) rather than adds; the click at
             4–5 kHz is left alone because the capsule already delivers it.
             Two-mic pair with unit 02: **this mic owns ATTACK/CLICK, top and bottom.** It gets
             no LF boost (B1 FLAT) and keeps its 4–5 kHz emphasis. Unit 02 owns BODY/SUB and
             has its baked 4 kHz beater peak trimmed −5 so the click does not stack.
QUESTIONS    Contour switch position at load-in — build assumes FLAT. Fallback in mic_notes.
TRACE        base(Beta 91A on kick — 4–9k baked attack, 400 box, Shure/RecordingHacks) ·
             equip(no rider, kick size unknown — generic instrument carries, nothing invented) ·
             genre(R&B — keep 4–5k click, trim only the 8–9k fizz) ·
             artist(no change — no artist-specific kick evidence found) ·
             venue(FSQ + 96% RH — HPF 50, B1 FLAT so the KS21 arch owns the bottom; 8500 trim
             is real because saturated air absorbs no HF)
