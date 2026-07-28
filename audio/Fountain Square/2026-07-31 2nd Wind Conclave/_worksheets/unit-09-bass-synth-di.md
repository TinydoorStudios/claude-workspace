# Unit 09 — Bass synth × DI  (ch 12)

INSTRUMENT   Synth bass on its own channel, sitting next to a live electric bass. On a modern
             R&B/gospel show-band stage this is usually the keyboard player's left hand or a
             dedicated module, used on the newer material where the record has a synth bass —
             Bruno Mars, contemporary gospel, anything post-2000 in the setlist.
             **Whether it plays simultaneously with ch 11 or swaps song-to-song is not stated
             on the input list, and it changes the low-end strategy.** → question round.
             Draft below assumes the conservative case: they can stack.

MIC/DI       "DI" on the input list. **Specifying the Radial J48** — active phantom DI, 48V.
             KB tendency: "clean/transparent, tight lows, high headroom. Weakness: clinical
             (no colour) → apply template as-is." Clinical is right for a synth: the source is
             already a finished sound and doesn't want a transformer's opinion on top.
             **Locker fork: EXEMPT.** DI input, no capsule.

SEARCHES     1. `synth bass live sound mixing with electric bass same song frequency separation
                octave layering live EQ`
             2. Cross-read of the returned Sound On Sound "Mixing Bass", Waves layering guide,
                iZotope and Mastering The Mix bass articles for the two-bass separation method.

CAPSULE FACT DI-side (J48, KB-verified): transparent active front end, tight lows, high
             headroom — **no baked peak of any kind**, which is why this channel takes the
             template straight. Source-side quantitative anchors from the research: synth-bass
             fundamentals normally sit **60–80 Hz**, and the band that makes a bass read on
             small/distant speakers is a **wide bell at 700 Hz – 1.5 kHz**.

WEB SAYS     The consistent method for two bass sources: treat each channel individually, then
             high-pass the *supporting* layer to around 60–80 Hz so only one source owns the
             fundamental, and separate the two in the midrange rather than fighting over the
             bottom. Sound On Sound's framing is the useful one — the overlap gets solved by
             deciding who owns what, not by cutting both.

KB SAYS      eq-starting-points has no synth-bass row — this is a source the KB doesn't cover.
             The nearest verified guidance is its keys/DI approach (subtractive, let the
             instrument's own voicing stand) plus the J48's "apply template as-is" tendency.

VERDICT      **THIN — and honestly so.** The web method is solid and consistent, but the KB has
             nothing on synth bass to cross-check it against, so there's no reconciliation to
             perform. I'm going with the research and flagging the gap rather than pretending
             the KB confirmed something it doesn't contain. → carried to the round as a **KB
             write-back candidate** (add a synth-bass row to eq-starting-points once this show
             confirms the approach), not as a blocking fork.

GENRE BEND   R&B/funk with a programmed track: the synth bass is a *texture*, and the electric
             is the *instrument*. Artist layer — a band that plays to a click and has a Track
             channel already has programmed low end in the mix, so a third source down there is
             one too many. This channel earns its place in the mids, not the sub.

VENUE BEND   FSQ: no room gain, and the KS21 arch is already carrying more sub than the plaza
             needs. High-passing the supporting bass layer is free here in a way it wouldn't be
             in a club. Mud cut at outdoor depth.

DRAFT BANDS  HPF 55 · LPF 12000
             B4  FLAT
             B3  −7 @ 250   Q 2.0  BELL   mud — outdoor depth
             B2  +3 @ 1200  Q 1.4  BELL   the "reads at distance" band, its own lane
             B1  FLAT                     deliberately — ch 11 owns the fundamental

## The show-wide low-end slot map (drawn here, applied everywhere)

Six sources want the same two octaves. Each one gets a slot and nothing is boosted in
anyone else's:

| Hz | Owner | How |
|---|---|---|
| 60 | **Kick out (D6)** | baked capsule peak — no boost written, none needed |
| 85 | Floor tom | +3, gated transient |
| 100 | **Bass guitar** | +3, the only *sustained* boost down here |
| 110 | Rack tom 2 | +3, gated transient |
| 130 | Rack tom 1 | +3, gated transient |
| — | Bass synth | **HPF 55, no low boost** — supporting layer, stays out |
| — | Congas / bongos | HPF'd above this map entirely (units 13, 14) |

The three toms only appear when struck, and the FSQ template's own tom gate (threshold
−36.2 dB, 130–317 Hz sidechain, faders 6/7/8) is what keeps them out of the way between hits.
That gate is doing real separation work in this show, not just cleanup.

GATE CHECK   **Boost audit — B2 +3 @ 1200.** No capsule, no baked peak, nothing to stack on the
             DI side. Against other sources: the D6 kick is *cutting* −4 at 1200, and ch 11
             bass puts its definition at 800 — so 1.2 kHz is genuinely clear air for this
             channel. That's the point of putting it there rather than at 800 where it would
             have doubled the electric bass.
             **B1 left FLAT is the deliberate move on this channel.** Every instinct says boost
             a synth bass low; the two-source rule says only one layer owns the fundamental and
             ch 11 already does. HPF 55 enforces it.

QUESTIONS    1. Do ch 11 and ch 12 play **at the same time**, or swap song to song? If they
                swap, ch 12's HPF can come down to 40 and it can own its own bottom.
             2. KB write-back candidate — add a synth-bass row to eq-starting-points.
