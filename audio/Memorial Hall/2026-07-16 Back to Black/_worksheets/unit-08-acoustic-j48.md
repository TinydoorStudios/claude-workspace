# Unit 08 — Acoustic Guitar × Radial J48 (ch 13)

**INSTRUMENT** — Acoustic guitar, DI only (no mic on the list). Almost certainly a piezo/undersaddle
pickup — that is what a DI'd acoustic on a theatre input list means. Role in THIS band: **texture,
not feature.** The *Frank*-side material and the ballads (*Love Is a Losing Game*) are where it
lives; it is never the front of the mix.

**MIC** — Radial J48. Active DI, 48 V. **Switchable — two: an 80 Hz high-pass and a −15 dB pad.**
Not a ribbon, not TOUR.

**SWITCH STATE ASSUMED — both OUT:**
- **80 Hz HPF → OUT (flat).** The desk's HPF is steeper and tunable; the J48's is a fixed corner of
  unpublished slope, and it would stack on the DI's *inherent* low removal (below) plus the desk
  filter — three low-end reductions on one channel is over-determined. **Fallback in `mic_notes`:**
  if the guitar howls on its body resonance and the desk HPF can't catch it, engage the switch and
  back the desk HPF down a step.
- **−15 dB pad → OUT.** An onboard acoustic preamp isn't hot enough to trouble the J48's 9 V rails.
  **Fallback:** engage if it clips at the DI.

**SEARCHES**
1. `Radial J48 active DI frequency response specs dB THD headroom acoustic guitar piezo review`
2. Cross-read: Radial Engineering J48 specifications page · Sweetwater · Music On Stage

**CAPSULE FACT** — **"the J48's dynamic handling is increased by a full 3 dB by gently removing
unnecessary lows"** — Radial Engineering, verbatim. A dB value tied to a documented response
behavior, and the operative one here. Supporting: **20 Hz–20 kHz** (HF exceeding 40 kHz on the
bench) · THD **0.002% @ −5 dBu** · dynamic range **109 dB** · input impedance **220 kΩ**, which
Radial specs as *"high enough to avoid loading down any instrument pickup, including finicky piezo
transducers."*

**WEB SAYS** — Clean, transparent, very low distortion, high headroom from the switching supply
that raises the internal rail to 9 V. The 220 kΩ input is explicitly a piezo-loading spec. Radial's
own framing of the low-end behavior is *"gently removing unnecessary lows"* to buy dynamic range —
i.e. the tight bottom is deliberate, not a limitation.

**KB SAYS** — `mic-library.md`: *"Radial J48 — Active phantom DI, clean/transparent, **tight lows**,
high headroom. Bass DI. Weakness: clinical (no color)."* EQ tendency: **"apply template as-is
(flat/honest)."**

**VERDICT — AGREE.**
And pleasingly so: the KB's **"tight lows"** turns out to be Radial's **"gently removing
unnecessary lows… a full 3 dB"** — the KB's shorthand is the maker's spec, independently arrived
at. Clean/transparent/high-headroom matches on both sides. Solid sourced baseline.

**LOCKER** — **No alternative.** The RNDI is the obvious thought — its transformer harmonics would
warm a thin, clinical piezo, and it's period-correct for a transformer-and-tape record. **I'm not
suggesting it, for two concrete reasons:** (1) it wouldn't fix the one real problem on this channel
— the 1.5–2 kHz quack is in the *pickup*, and no DI removes it, so this is a colour preference,
which the locker rule says doesn't qualify; (2) all three RNDIs are already committed (ch 9, 14,
15). The J48 is the KB's listed acoustic DI and its 220 kΩ input is specced for exactly this
source. Specified DI stands.

**GENRE BEND** — This channel takes the **acoustic-forward** rules, not the show's soul-revue
rules, because that's what it is musically: *"Conservative. Piezo quack at 1.5–2 kHz is the primary
target"* (CLAUDE.md), and the KB's *"acoustic-forward genres want natural character preserved —
cuts only, conservative."* So: **two bands used, two OFF.** The restraint is the point — a texture
instrument doesn't need six moves.

**VENUE BEND** — Memo's **250–315** node meets acoustic body boom; treated once, lightly. The
63/125 nodes sit below the HPF. The 1.6 s RT60 is the reason the HPF is decisive rather than
polite — a DI'd acoustic with its low end intact turns to porridge in this room. Indoor depth.

**DRAFT BANDS** (Q225 layout, whole dB, cuts first)

| Band | Setting | Why |
|---|---|---|
| **HPF** | **80 Hz, 18 dB/oct** | Sits **right at the low E (82 Hz)** — preserves the fundamental, drops everything under it. Conservative by design, per the acoustic-forward rule; the bass owns the register below this anyway. |
| **LPF** | **12 kHz, 12 dB/oct** | Piezo fizz and DI hash. Gentle. |
| **Band 4 (HF)** | **OFF** | Deliberate. The top is what makes it read as *acoustic* in a soul band — cutting it would leave a dull, useless channel. The LPF already has the fizz. |
| **Band 3** | **−5 dB @ 1.8 kHz, Q 2.0, Bell** | **The quack — CLAUDE.md's named primary target for any piezo DI.** Deepest cut on the channel, and the one move that matters. |
| **Band 2** | **−3 dB @ 250 Hz, Q 1.8, Bell** | Memo's node meeting acoustic body boom. Light — conservative genre. |
| **Band 1 (LF)** | **OFF** | The 80 Hz HPF owns everything below, and the J48 has already *"gently removed"* 3 dB of it upstream. Adding a band here would be the third low-end reduction on one channel. |

**Zero boosts.**

**GATE CHECK** — No boosts to justify. Reverse gate, and it's load-bearing here: **Band 1 is OFF
specifically because the J48 already removes low end by design (3 dB, Radial)** — a desk LF cut
would stack on the DI's own removal *and* the HPF. That's the same failure as double-scooping a D6,
just at the other end of the spectrum.

**DYNAMICS**
- **No gate** — acoustic-forward; the KB's rule against chopping attacks applies, and this part
  is sparse enough that a gate would only ever chatter.
- **Comp:** Mustard **Purple (Optical / LA-2A)** — gentle and program-dependent, the right character
  for a texture instrument. **3:1, attack 20 ms, release 200 ms, 2–3 dB GR.** Light: the KB's
  acoustic rule is *"slow and gentle… the attack is part of the articulation."*

**QUESTIONS** — none as a fork. One assumption worth a line in the round only if Brian wants to
correct it: **I've assumed a piezo/undersaddle pickup**, which is what drives the 1.8 kHz cut. If
the guitar has a magnetic soundhole pickup or an onboard mic/blend system, the quack largely isn't
there and Band 3 comes off. It's a soundcheck-visible thing, not a build blocker — noted in
`mic_notes`.
