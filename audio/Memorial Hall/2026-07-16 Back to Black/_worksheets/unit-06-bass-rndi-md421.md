# Unit 06 — Bass × Neve RNDI (ch 9) + Sennheiser MD 421-U (ch 10) — **TWO-MIC**

**INSTRUMENT** — Electric bass through an **Aguilar DB751 head + DB410 (4×10) cab**, plus a DI
split. Role in THIS band: the Motown/Daptone bassline *is* the song — melodic, walking, up front,
round and dark. On the *Frank*-side material it turns into jazz-club upright-ish walking.

**Correction to my own plan-pass assumption, on the record:** I wrote in `plan.md` that the Aguilar
is "modern hi-fi… the *opposite* of the flatwound/Ampeg tone the Amy record is built on." **The
research says otherwise and I'm withdrawing it.** The DB751 is a **hybrid with a tube preamp**, and
TalkBass consensus describes its power section as *"a big, fat, musical slam more similar to the
**SVT** or other all tube amplifiers"* — with everything flat, *"a very thick tone and bottom end."*
The DB410 gives *"punchy, articulate mids."* This rig is **closer to the reference than I assumed**,
so it needs less corrective fighting and more staying-out-of-the-way. Also noted: the head's own EQ
is centered at **800 Hz**, where *"a small cut smooths out the head considerably while a small boost
yields a very aggressive cutting edge"* — 800 Hz is this rig's voicing hinge, and that turns out to
matter below.

---

## The two mics

**MIC A — Neve RNDI (ch 9).** Active transformer DI, class-A discrete FET. Requires 48V. No
switches. Not a ribbon, not TOUR.

**MIC B — Sennheiser MD 421-U (ch 10)** on the DB410. Vintage 1970s **421-U** (native XLR) — *not*
the 421-II. Large-diaphragm dynamic. **Switchable: 5-position inductive bass rolloff.** No phantom.
Not a ribbon, not TOUR.

**SWITCH STATE ASSUMED:** **421-U bass rolloff → "M" (music / full response).**
Rationale: the desk's HPF does the low-end de-stack far more precisely than a 5-position inductive
filter, and "M" keeps the mic's response honest so what I've designed is what arrives. Fallback in
`mic_notes`: if the cab is boomy on stage and the switch gets moved toward "S," the desk's
100 Hz HPF and the 300 Hz cut both come back a step — they'd be stacking on the mic's filter.

**SEARCHES**
1. `Rupert Neve RNDI direct box frequency response transformer bass DI review specs dB`
2. Direct fetch: Sound on Sound — *Rupert Neve Designs RNDI* review
3. `Sennheiser MD 421 bass cabinet mic presence peak 4kHz frequency response bass rolloff switch M S positions dB`
4. `Aguilar DB751 head DB410 cabinet tone character review hi-fi modern vintage frequency response`

**CAPSULE FACT** — two, one per mic, and **together they hand me the lane split for free:**

- **RNDI: ±0.25 dB from 25 Hz – 44 kHz** (±1 dB from 12.5 Hz – 63 kHz; −3 dBu @ 92 kHz) — Rupert
  Neve Designs published spec. Input headroom **+20.5 dBu**. Essentially perfectly flat: it
  delivers the low E (41 Hz) fundamental **untouched**.
- **MD 421: −8 dB at 40 Hz** (rolling off from 80 Hz down), even midrange **80 Hz – 1.5 kHz**, then
  *"slopes up gently to **+4 dB at 2.75 kHz**"* into a substantial **4–5 kHz presence peak** —
  RecordingHacks published frequency plot. Range 30 Hz – 17 kHz.

**Read those two side by side: the DI is flat at the low E; the 421 is 8 dB down there and cannot
deliver a fundamental if you begged it. The mics have already chosen their lanes.**

**WEB SAYS**
- *RNDI* — SOS: *"a subtle, but definite, character to the sound"* that is *"more pronounced at
  higher input signal levels, presumably due to increased levels of harmonic distortion"*; output
  impedance under 40 Ω *"enables the RNDI to drive long cable runs with **minimal loss of
  high-frequencies**."* Reviews elsewhere: *"lows sound more consistent than a lot of other DIs and
  **the highs exhibit slightly more clarity**."* Compared to a transformerless DI, which SOS found
  *"slightly more clinical."*
- *MD 421* — the 4–5 kHz presence peak *"can bring out clarity on toms, and alongside its extended
  low-frequency response, is what has made the 421 the go-to tom mic for generations."* The M/S
  switch: **"S" (speech) attenuates lows, "M" (music) allows full response.**

**KB SAYS**
- *RNDI* — *"Active transformer DI, smooth musical top, gentle harmonic warmth, full lows.
  Bass/gtr/keys direct. **Weakness: very slight HF softening vs a clean DI.**"* EQ tendency:
  **"ease off presence."**
- *MD 421-U* — *"Large-diaphragm dynamic, wide 30Hz-17kHz, extended low end + low-mid girth,
  **voiced presence boost (~4-5kHz)**, 5-position bass rolloff (M=flat…S=-6dB<500Hz). Toms/brass/
  cabs. **Weakness: low-mid bloat 200-400 if close.**"* EQ tendency: *"ease off boom, presence;
  tame mud ~300Hz."*

**VERDICT — split by mic, because they land differently:**

- **RNDI → DISAGREE.** The KB says *"very slight HF softening"* and instructs **"ease off
  presence."** The maker measures **±0.25 dB from 25 Hz to 44 kHz** — there is no HF softening in
  the audio band, or anywhere near it. SOS describes *minimal loss of high frequencies* and no
  rolloff at all; other reviews say the highs have **more** clarity, not less. **The KB's direction
  is inverted.** What the KB is *reaching for* is real — the RNDI does have transformer character —
  but that character is **level-dependent harmonic distortion, not a frequency-response tilt.**
  Following "ease off presence" means cutting top off a measurably flat DI to chase a softness that
  isn't in the response. **→ question round, (a)/(b)/(c).** This touches **four channels**: 9, 14,
  15 (and it is why Unit 09's keys are drafted the way they are).

  **The actionable half of the finding:** if the RNDI's warmth is drive-dependent, then the way to
  get it is **gain** — hit the DI hard rather than EQ warmth back in afterward. Free, period-correct
  color on the exact channel that wants it. That goes in `mic_notes`.

- **MD 421-U → AGREE.** Presence peak ~4–5 kHz, even mids, 5-position rolloff, low-mid bloat
  200–400 — KB and the published plot say the same things. The web adds two numbers the KB lacks
  (**−8 dB @ 40 Hz**, **+4 dB @ 2.75 kHz**), which are worth writing back. Only nuance: the KB's
  *"extended low end"* is fair for a tom/brass mic reaching 30 Hz, but **on a bass cab the
  operative fact is that it's 8 dB down at the low E** — and that is what designs this unit.

**LOCKER** — **No alternative on either channel, and I can name why for both.**
- *ch 9:* the J48 is the locker's other bass DI, but the KB calls it *"clinical (no color)"* — for a
  record built on transformers and tape, the RNDI's harmonic character is the point. Specified mic
  is the better call.
- *ch 10:* the obvious locker swaps are the Beta 52 or D6. Both are **wrong for the lane design** in
  a nameable way: the Beta 52 has *"scooped low-mids"* (KB) and the D6 a **−15 dB scoop at 600 Hz**
  (KB) — but low-mids are precisely the lane this mic is being asked to own. The 421's **even
  80 Hz–1.5 kHz** response is what the job needs. Specified mic stands.

---

## LANE SPLIT — the de-stack design (goes in BOTH channels' `mic_notes`)

Assigned once, across the whole spectrum, per the two-mic rule:

| Zone | Owner | The other mic |
|---|---|---|
| **Bottom (below ~100 Hz)** | **RNDI (9)** — flat ±0.25 dB at the low E | **421 HPF'd at 100 Hz.** It's already −8 dB @ 40 Hz naturally; the HPF finishes it. **No low boost on either.** |
| **Mids (~800 Hz)** | **421 (10)** — boosted **+3** | **RNDI cut −4.** A **handoff, not a stack**: the DI vacates the lane the cab mic fills. |
| **Top** | **421 (10)**, and even it is **trimmed** | **RNDI LPF'd at 5 kHz** so the DI adds no clank over the 421's presence. |
| **Memo 125 Hz node** | **RNDI (9) only — −4 dB** | **Not cut on ch 10.** The node cut belongs to whichever mic owns the low lane. Cutting it on both would be the classic double-dip. |

**GENRE BEND** — Motown/Daptone bass: round, dark, melodic, forward. No modern clank, no slap
sheen. Both LPFs are set by the record, not the room. The one boost in the unit (800 Hz on the
421) exists because in a 1.6 s hall a dark bass stops articulating — the KB's own note applies:
*"upper harmonics give the bass definition on small speakers and for audience members far from the
subs."*

**VENUE BEND** — The KB is explicit and it lands on this unit: **"At Memo: 125 Hz standing wave is
right in the bass fundamental range."** That is *the* collision, and per the lane split it is
treated **once**, on ch 9. The 250–315 node adds to the DB751's already-*"very thick"* flat voicing
on both channels, so each gets its own low-mid cut in its own lane (250 on the DI, 300 on the cab
mic — the latter doubling as the KB's documented 421 bloat fix). Indoor depth.

---

## DRAFT BANDS (Q225 layout, whole dB, cuts first)

### Ch 9 — Bass DI (RNDI) — **owns the BOTTOM**
| Band | Setting | Why |
|---|---|---|
| **HPF** | **35 Hz, 24 dB/oct** | Under the low E (41 Hz) — protects the fundamental this mic exists to deliver. Steep, because ±1 dB to 12.5 Hz means it *will* pass subsonic garbage. |
| **LPF** | **5 kHz, 12 dB/oct** | **De-stack, top.** The DI's job is weight, not clank; clears the top lane for the 421. |
| **Band 4 (HF)** | **OFF** | Nothing to do — and notably **no "ease off presence"**, per the DISAGREE above. |
| **Band 3** | **−4 dB @ 800 Hz, Q 1.5, Bell** | **De-stack, mids.** Vacates the lane the 421 fills. Also the DB751's own voicing hinge, where *"a small cut smooths out the head considerably."* |
| **Band 2** | **−3 dB @ 250 Hz, Q 1.8, Bell** | Memo's 250–315 node meeting the DB751's *"very thick"* flat bottom. |
| **Band 1 (LF)** | **−4 dB @ 125 Hz, Q 2.0, Bell** | **The collision — KB: "125 Hz standing wave is right in the bass fundamental range."** Cut lives here and **nowhere else**. |

**Gain staging (the RNDI finding):** **drive it.** The transformer character is *"more pronounced
at higher input signal levels"* (SOS) — take the color from the gain, not from EQ.

### Ch 10 — Bass Mic (MD 421-U, switch "M") — **owns the MIDS/GROWL**
| Band | Setting | Why |
|---|---|---|
| **HPF** | **100 Hz, 18 dB/oct** | **De-stack, bottom.** Mic is already −8 dB @ 40 Hz; this finishes it so it cannot stack on the DI's lane. Clears Memo's 63 Hz node outright. |
| **LPF** | **6 kHz, 12 dB/oct** | Above the presence peak — kills cab hiss and clank. |
| **Band 4 (HF)** | **−3 dB @ 4 kHz, Q 1.5, Bell** | **Trims the baked peak.** The 421 voices **+4 dB @ 2.75 kHz** rising into a 4–5 kHz presence peak; the Daptone reference doesn't want it. A trim of a documented peak, not a cut of nothing. |
| **Band 3** | **+3 dB @ 800 Hz, Q 1.5, Bell** | **The only boost in this unit** — the lane handoff. Note definition in a 1.6 s room, in the space the DI vacated. |
| **Band 2** | **−4 dB @ 300 Hz, Q 1.8, Bell** | Double-justified: the KB's documented 421 weakness (*"low-mid bloat 200-400 if close"*) **and** Memo's 250–315 node. |
| **Band 1 (LF)** | **OFF** | The 100 Hz HPF owns everything below. **No 125 Hz cut here** — that's ch 9's lane. |

**GATE CHECK** — **One boost in the unit: +3 dB @ 800 Hz on ch 10.**
Permitted: the MD 421's published plot shows an **even midrange from 80 Hz to 1.5 kHz** — flat at
800 Hz, **nothing baked there to stack on**. The peak this mic *does* bake in (+4 dB @ 2.75 kHz)
sits an octave and a half above and is being **cut**, not boosted. Gate passed.
**Lane check:** no zone is boosted on both mics — top and bottom are each owned once, and 800 Hz is
a handoff (−4 on 9, +3 on 10), not a stack.

**DYNAMICS**
- **No gate on either channel** — bass is continuous.
- **Ch 9 comp:** Mustard **Purple (Optical / LA-2A)** — the period-correct bass compressor, and
  gentle by design. **4:1, attack 20 ms, release 200 ms, 4–5 dB GR.** Per the KB: *"gentle
  compression to control peaks and even out note-to-note level variation."*
- **Ch 10 comp:** Mustard **Blue (Neve)**, **3:1, attack 20 ms, release 150 ms, 2–3 dB GR.** Light
  — the DI is doing the leveling; this one is for color.
- **Both:** polarity-check ch 10 against ch 9 in mono before advancing the cab mic — sum must be
  fuller, not thinner. The cab mic also arrives late by the mic's distance from the speaker
  (~1 ms/ft); if the sum stays hollow after the polarity flip, time-align 10 to 9 rather than
  EQ'ing around it. Group both to one VCA; keep the blend constant.

**QUESTIONS** — one, and it is the **RNDI web↔KB DISAGREE**, which reaches ch 9, 14 and 15:
- **(a)** research — the RNDI is flat (±0.25 dB, 25 Hz–44 kHz); no "ease off presence" anywhere,
  and take its warmth from drive (what's drafted);
- **(b)** KB — treat it as HF-softened and ease off presence;
- **(c)** research **and** correct the `mic-library.md` RNDI row: replace *"very slight HF
  softening"* / *"ease off presence"* with the measured flatness plus the level-dependent
  harmonic character.
My read: **(c)**. Maker spec and SOS agree, and they point the opposite way to the KB row.
