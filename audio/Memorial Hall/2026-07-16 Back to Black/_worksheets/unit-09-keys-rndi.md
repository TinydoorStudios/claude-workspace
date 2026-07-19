# Unit 09 — Keys × Neve RNDI ×2 (ch 14, 15 — stereo pair)

**INSTRUMENT** — ⚑ **NOT KNOWN, and the backline quote is why.** Under *Keyboard*, Event
Enterprises supplies:
- Single Tier X Stand
- Keyboard Bench
- **Keyboard Total: $0.00**

**A stand and a bench. No keyboard.** The player brings their own, and nothing on the input list,
the quote, or the web says what it is. Instrument is the first and heaviest layer in the
instrument → mic → genre → venue order, so this is a genuine stop-and-ask. **→ question round.**

**What the material demands is knowable, though, and that carries the provisional.** From the
album credits (Wikipedia / album liner notes): **John Adams played Rhodes and organ**; **Victor
Axelrod played Wurlitzer** (and *"Wurlitzer and claps on 'Rehab'"*), plus **piano on "Wake Up
Alone."** Ronson used *"synthesisers and vintage keyboards… including the Wurlitzer electric
piano."* The *Frank*-side material adds straight **jazz piano** (*Me & Mr Jones*).

So the confirmed setlist needs **four keyboard voices: acoustic piano, Rhodes, Wurlitzer, and
organ.** One player, one stand, one tier. **That is a Nord-class stage keyboard** (Electro / Stage,
or a Yamaha CP / Roland RD) running patches — nothing else covers that repertoire on a single X
stand. High confidence on the *category*; zero on the *model*.

**And the category is what actually sets the EQ**, which is why a provisional is honest here:
**one EQ curve has to serve piano AND Rhodes AND Wurli AND organ.** That single fact forces
conservatism. Anything shaped tightly around a Rhodes bell will wreck the piano two songs later.
So the restraint below isn't hedging — it's the correct answer to a four-voice channel, and it
would survive most answers to the question.

**MIC** — Neve RNDI ×2 (stereo). Active transformer DI, 48 V. No switches. Not a ribbon, not TOUR.

**SEARCHES**
1. `Amy Winehouse "Back to Black" album keyboards piano Rhodes Wurlitzer Hammond organ Dap-Kings instrumentation`
2. RNDI research: **within-show dedupe — the full web pass ran in Unit 06** (`Rupert Neve RNDI
   direct box frequency response…` + the SOS review fetch). Same mic, same show; not re-run.

**CAPSULE FACT** — **RNDI: ±0.25 dB from 25 Hz – 44 kHz** (±1 dB, 12.5 Hz – 63 kHz) — Rupert Neve
Designs published spec. Input headroom **+20.5 dBu**. Carried from Unit 06.

**WEB SAYS** — See Unit 06 in full. The short version: measurably flat across and well beyond the
audio band; SOS finds *"a subtle, but definite, character"* that is **level-dependent harmonic
distortion**, not a response tilt; output impedance under 40 Ω gives *"minimal loss of high
frequencies."*

**KB SAYS** — *"Neve RNDI — Active transformer DI, smooth musical top, gentle harmonic warmth, full
lows… **Weakness: very slight HF softening vs a clean DI.**"* EQ tendency: **"ease off presence."**

**VERDICT — DISAGREE.** Same conflict as Unit 06, carried here because it lands on two more
channels. The KB's *"ease off presence"* is contradicted by ±0.25 dB flatness to 44 kHz. **This is
why Band 4 is OFF below rather than carrying a reflex presence cut** — and on a keyboard channel
that matters more than on the bass, because a Rhodes and a piano both live in the top octaves the
KB would have had me trim for no measured reason. Folded into the single round-round fork in
Unit 06 (touching ch 9, 14, 15 together).

**LOCKER** — **First-call match, no alternative.** The KB lists both the RNDI (*"Hi-Z instrument —
electric bass, guitar direct, synth"*) and the J48 (*"keys"*) for this job. The RNDI is the better
call and I can name why: on a **digital** board — sampled patches, clean converters — the
transformer's harmonic character is the one thing in the chain that sounds like the record's
transformer-and-tape lineage. The J48 is *"clinical (no color)"* (KB), which is the last thing a
Nord needs. Specified DI stands.

**GENRE BEND** — The keys carry the *"synthetic Motown backdrop"* — they are the harmonic bed under
the vocal, not a solo voice, for most of the set. Dark, warm, sat back. But the *Frank* material
turns the piano into a foreground jazz instrument, so the curve cannot be so shaped that it can't
step forward. **Four voices, two roles, one curve → conservative.**

**VENUE BEND** — Memo, and the HPF earns its corner here: set at **60 Hz** it sits directly on the
room's **63 Hz node**, so the filter does that node's work and no bell band is spent on it (same
trick as the hat's 300 Hz HPF against the 250–315 node). The **125 Hz** node then collides with a
piano patch's left hand — treated. The **250–315** node is the most crowded real estate on this
whole stage: bass cab at 300, guitar box at 400, snare at 315, keys mud here too. Indoor depth.

**DRAFT BANDS** (Q225 layout, whole dB, cuts first) — **linked stereo pair, identical both sides**

| Band | Setting | Why |
|---|---|---|
| **HPF** | **60 Hz, 18 dB/oct** | Protects a piano patch's real bottom while killing DI rumble — and lands the corner on Memo's **63 Hz node**, so the filter handles it instead of a band. |
| **LPF** | **14 kHz, 12 dB/oct** | The tape ceiling, consistent with the hat and overheads. Gentle — the Rhodes bell lives at 2–6 kHz and is untouched by this. |
| **Band 4 (HF)** | **OFF** | **Deliberate, and this is the DISAGREE landing.** The KB's *"ease off presence"* would trim the top off a DI measured at **±0.25 dB to 44 kHz** — a correction for a softness that isn't in the response. Nothing to correct, so nothing here. |
| **Band 3** | **−3 dB @ 2.5 kHz, Q 1.5, Bell** | **Carving, not correcting** — the KB's own rule for DI keys: *"the EQ work is mostly about carving space in the mix, not correcting a mic."* This is where sampled Rhodes/Wurli patches turn glassy **and** where the keys would otherwise sit on top of the lead vocal's intelligibility. Light, because it has to be safe for the piano too. |
| **Band 2** | **−4 dB @ 315 Hz, Q 1.5, Bell** | Memo's node meeting keyboard low-mid mud, in the most contested zone on the stage. Deepest cut on the channel. |
| **Band 1 (LF)** | **−3 dB @ 125 Hz, Q 2.0, Bell** | Memo's node, where a piano patch's left hand collides with the bass guitar. (Not a stack with ch 9's 125 cut — different instruments, different channels; the two-mic rule is about two mics on *one* source.) |

**Zero boosts.**

**GATE CHECK** — No boosts to justify. Reverse gate: **Band 4 is OFF because the RNDI bakes in
nothing** — ±0.25 dB across 25 Hz–44 kHz means there is no capsule feature to correct at either
end, and the KB's tendency line pointed at one that measurement says isn't there.

**DYNAMICS**
- **No gate.** Pads and organ are continuous; a gate would chop sustained chords.
- **Comp:** Mustard **Purple (Optical / LA-2A)**, **3:1, attack 20 ms, release 200 ms, 2–3 dB GR.**
  Light and program-dependent — it has to be transparent across four voices with wildly different
  envelopes (piano transient vs. organ's flat sustain).
- **Gain staging:** as with ch 9, take the RNDI's warmth from **drive** rather than EQ — the
  character is *"more pronounced at higher input signal levels"* (SOS).

**QUESTIONS** — one, and it's a real blocker to full commitment:
**What keyboard is the player bringing?** The backline supplies a stand and a bench and nothing
else. My read: a **Nord-class stage keyboard on piano / Rhodes / Wurli / organ patches**, because
that's what the confirmed setlist requires from one player on one tier — and the curve above is
built to be safe across all four voices. **What would change it:**
- **A real Hammond + Leslie** (mic'd, not DI'd) — this unit is void; ch 14/15 become a different
  build entirely.
- **A vintage Rhodes or Wurli** (a real one, not a patch) — Band 3's 2.5 kHz cut comes off; real
  electromechanical bark isn't glassy the way a sample is, and the noise floor changes the
  gain plan.
- **Piano-only, no other voices** — the curve can stop compromising and open up.
- **A synth/workstation with onboard effects** — check what reverb it's already sending; it will
  fight the plate.
