# Unit 07 — Electric Guitar × SM57 (ch 11) + Royer R-121 (ch 12) — **TWO-MIC** ⚠ RIBBON

**INSTRUMENT** — **Fender Blues Deluxe, 40 W, 1×12 tube combo.** Bright, chimey Fender clean with
tube breakup when pushed. Role in THIS band: the Daptone guitar part — clean, warm, chunky, sitting
*back*. The *Rehab* chank, the *Back to Black* arpeggios. Dark and round. Never bright, never spiky.

**Note the channel numbers.** Memo's KB documents the house AxeMount rig on **CH 13/15**; this show
puts it on **11/12**. The input list wins — the venue article's channel numbers are a description of
the usual patch, not a rule. Flagged so nobody patches from memory.

---

## The two mics

**MIC A — Shure SM57 (ch 11).** Cardioid dynamic. **Primary.** No phantom. Not a ribbon, not TOUR.

**MIC B — Royer R-121 (ch 12).** Figure-8 **RIBBON**. **Complement.** ⚠⚠ **NO 48V — IN RED.**
Not TOUR.

**SEARCHES**
1. `Royer R-121 frequency response figure-8 ribbon dB proximity SM57 blend guitar cab Fender Blues Deluxe`
2. Direct fetch: ZenPro Audio — Royer Labs R-121 specification page
3. `Shure SM57 frequency response chart presence peak dB "6 kHz" proximity effect guitar cab 300-500Hz honk`

**CAPSULE FACT** — one per mic, and the pair of them *is* the design brief:

- **SM57: +7 dB @ 6 kHz.** RecordingHacks / Shure response data — *"an upward ramp in sensitivity
  from 2 kHz to about 6 kHz, where the mic becomes **7 dB more sensitive**,"* with a slight peak
  around 5 kHz. Also: **proximity boost of 6–10 dB below 100 Hz** at close range (Shure);
  **small dip between ~300–600 Hz**; 40 Hz–15 kHz with a sharp roll-off from 12 kHz.
- **R-121: 30–15,000 Hz ±3 dB.** Royer published spec (via ZenPro). Figure-8. **>135 dB SPL @
  20 Hz.** Sensitivity −50 dBv.

**Put them together and the problem states itself: a bright Fender clean, into a mic that adds
+7 dB exactly where a Fender is already spiky.** That is the thing to fix, and the ribbon is the
other half of the fix.

**WEB SAYS**
- *R-121* — *"flat and well balanced,"* low end *"deep and full"* while avoiding boominess, midrange
  *"well defined and realistic,"* top end *"sweet and natural sounding, **never edgy or
  sibilant**."* At **3 ft and closer the rear side reads slightly brighter than the front.**
- *The blend* — near-universal consensus: *"nothing beats the combination of an SM57 capturing the
  mid attack of a cab blended with a ribbon mic to smooth the sound and round out the bottom end"*;
  the R-121 *"pairs brilliantly with the Shure SM57, combining the warmth of the ribbon with the
  SM57's focused bite."* The AxeMount/SM-21 clip points the 57 where the dome meets the paper and
  the ribbon more at the dome — *"a tried-and-true, phase-coherent configuration."*
- *SM57* — the 300–600 Hz dip *"helps reduce muddiness in the low mids"*; the presence rise is the
  thing *"sometimes less charitably known as midrange honk."*

**KB SAYS**
- *SM57* — *"Mid-forward workhorse, presence 3-5kHz, proximity-prone. On cabs/snare builds
  box/honk 300-500Hz. Weakness: thin lows, can be honky/harsh in upper mids."* → *"tame box ~400Hz."*
- *R-121* — *"Figure-8 ribbon, flat 30Hz-15kHz, deep full (not boomy) low, defined mids, sweet
  natural top (never edgy/sibilant) rolling off above ~15k, proximity. Rear side records brighter.
  NO 48V. Weakness: soft top vs condensers, low output, proximity bloom."* → *"ease off air,
  presence, top; tame proximity ~200Hz."*
- *The rig* — CLAUDE.md + venue article: 57 primary, set level first; ribbon up from zero until the
  57's brittleness reduces; **typically 6–10 dB under, closing to 3–5 dB for warm GD/Allmans-style
  tones**; polarity-check in mono; watch 300–500 Hz on the bus post-blend; one VCA; **no phantom.**

**VERDICT — AGREE**, on both mics, with one refinement worth writing back.
The R-121 is textbook: 30–15k ±3 dB, deep-not-boomy low, sweet un-edgy top, rear brighter close in
— the KB and Royer say the same thing in nearly the same words. The SM57 matches too, and the web
supplies the number the KB lacks (**+7 dB @ 6 kHz** vs the KB's looser *"presence 3-5kHz"*).

**The refinement:** the KB says the 57 *"builds box/honk 300-500Hz"* on cabs, while the published
curve shows a **small dip** at 300–600 Hz. Both are true and they aren't in conflict — the curve is
free-field, the KB is describing what actually happens when you jam it against a loud 1×12 and
proximity piles in. But it means **the 400 Hz cut should be lighter than reflex**, because the
capsule already dips there. That's the gate working in reverse, and it's why Band 3 on ch 11 is
−3 and not −5.

**LOCKER** — **First-call match, no alternative, on both.** This *is* the locker's documented
AxeMount rig — the KB lists it under Standard Combos as the Memo guitar-cab pair. Nothing to
suggest.

---

## LANE SPLIT — the de-stack design (goes in BOTH channels' `mic_notes`)

The mechanism is worth being precise about, because "the ribbon adds top" is the wrong mental
model. The R-121 doesn't *add* top — it adds **content that has no 6 kHz spike**, which averages
the 57's peak down. That's what "tames brittleness" means physically.

| Zone | Owner | The other mic |
|---|---|---|
| **Bottom (below ~120 Hz)** | **SM57 (11)** — HPF 90 Hz | **R-121 HPF'd higher, at 120 Hz**, so the ribbon cannot stack on the primary's bottom, and its documented ~200 Hz proximity bloom stays out. |
| **Midrange grit / pick attack** | **SM57 (11)** — the primary, untouched in its own lane | **R-121 cut −4 @ 400 Hz** — the KB blend rule: the complement's 150–800 comes down so it doesn't stack on the primary's midrange. |
| **Top** | **R-121 (12)** — left **completely alone** | **SM57 trimmed −4 @ 6 kHz** (its baked peak) **and LPF'd at 10 kHz.** |
| **Memo 250 Hz node** | **SM57 (11) only — −3 dB** | Not cut on ch 12; the ribbon's 120 Hz HPF plus its 200 Hz cut already own that region on its side. |

**Blend level — a deliberate departure, traceable to the KB's own text: R-121 sits 3–5 dB under the
SM57, not the usual 6–10.** The KB says the blend closes to *"3–5 dB for warm GD/Allmans-style
tones."* A clean, dark, round Daptone guitar tone is that case exactly — we want *more* ribbon in
this blend than a rock show would take, because the ribbon is doing the work that makes it 1966.

**GENRE BEND** — Everything above. The single most artist-specific move on this unit is the
**−4 dB @ 6 kHz on the 57**: a bright Fender + a mic with +7 dB there = the opposite of this record.

**VENUE BEND** — Memo's **250–315 node** meets a 1×12's cab boom → handled once, on the primary.
The 63/125 nodes sit below both HPFs and need no bands. Indoor depth — this is a clean guitar in a
556-seat room, not an outdoor rock stage.

---

## DRAFT BANDS (Q225 layout, whole dB, cuts first)

### Ch 11 — Guitar Mic 57 (SM57) — **primary; owns mids + bottom**
| Band | Setting | Why |
|---|---|---|
| **HPF** | **90 Hz, 18 dB/oct** | Controls the documented **6–10 dB proximity boost below 100 Hz**. A 1×12 has nothing useful down there. |
| **LPF** | **10 kHz, 12 dB/oct** | Dark reference. Set at 10k rather than 12k so it actually does something — the mic already self-rolls sharply from 12 kHz. |
| **Band 4 (HF)** | **−4 dB @ 6 kHz, Q 1.5, Bell** | **The move on this channel.** Trims the baked **+7 dB @ 6 kHz** off a cab that's already bright. A trim of a documented peak, not a cut of nothing. |
| **Band 3** | **−3 dB @ 400 Hz, Q 1.5, Bell** | The KB's *"tame box ~400Hz."* **−3 not −5** — the capsule already dips at 300–600, so a reflex-depth cut would be a second scoop on the first. |
| **Band 2** | **−3 dB @ 250 Hz, Q 1.8, Bell** | Memo's node meeting 1×12 cab boom. |
| **Band 1 (LF)** | **OFF** | HPF owns it. |

### Ch 12 — Guitar Mic 121 (Royer R-121) — **complement; owns the top** ⚠ **NO 48V**
| Band | Setting | Why |
|---|---|---|
| **HPF** | **120 Hz, 18 dB/oct** | **De-stack, bottom** — set *above* the 57's so the ribbon stays out of the primary's low lane. Also catches the KB's documented ribbon proximity bloom. |
| **LPF** | **OFF** | **Deliberate.** The ribbon self-limits at **15 kHz ±3 dB**. An LPF here would be theater. |
| **Band 4 (HF)** | **OFF** | **A considered departure from the KB's "ease off air, presence, top" tendency line.** This mic is patched *specifically* to contribute its sweet, un-peaky top as the antidote to the 57's +7 dB @ 6 kHz. Cutting its top defeats the only reason it's here. Noted in `mic_notes` so it doesn't read as an oversight. |
| **Band 3** | **−4 dB @ 400 Hz, Q 1.5, Bell** | **De-stack, mids** — the KB blend rule; keeps the ribbon out of the 57's midrange. |
| **Band 2** | **−3 dB @ 200 Hz, Q 1.8, Bell** | The KB's documented R-121 *"proximity bloom ~200 Hz."* |
| **Band 1 (LF)** | **OFF** | HPF owns it. |

**Zero boosts in this entire unit.**

**GATE CHECK** — **No boosts anywhere, so the gate is satisfied trivially.** Both reverse checks
recorded: (1) the SM57's 400 Hz cut is held to **−3** because of the capsule's own 300–600 dip;
(2) the R-121's top is **not** cut despite the KB's tendency line, because its un-peaky top is the
functional payload of the blend.
**Lane check:** no zone is boosted on both mics — there are no boosts at all. Bottom is owned once
(57, with the ribbon HPF'd above it), top is owned once (ribbon, with the 57 trimmed and LPF'd).

**DYNAMICS**
- **No gate** — a clean guitar part is continuous, and the one-mic reference says don't chop.
- **Comp (ch 11):** Mustard **Blue (Neve)**, **3:1, attack 20 ms, release 150 ms, 2–3 dB GR.** Light.
- **Comp (ch 12):** none — the ribbon rides the blend.
- **⚠ CH 12 PHANTOM OFF. Verify before the mic is plugged, and verify again after any patch
  change.** 48 V on a passive ribbon destroys it. Red on every document.
- **Polarity-check ch 12 against ch 11 in mono before advancing the ribbon** — the sum must be
  **fuller**, not thinner. If thinner, flip polarity on ch 12.
- **Both to one VCA**; keep the blend constant once set.
- **Post-blend:** check 300–500 Hz on the bus; notch −2 to −3 dB there if it piles up (KB).

**QUESTIONS** — none. Both mics resolved, both verdicts AGREE, no locker fork, no switches. The
only carried item is the **ch 11/12 vs. CH 13/15 patch difference**, which is a note, not a fork.
