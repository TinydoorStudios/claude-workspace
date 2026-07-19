# Unit 01 — Kick × Earthworks DM6 (ch 1)

**INSTRUMENT** — Gretsch USA Custom kick, **18" deep × 22" diameter, maple**. Shallow-ish 22", so
punchy and quick rather than cavernous. Single Yamaha FP9500C pedal (no double kick). Role in THIS
band: the Daptone reference kick — short, dark, felt, *midrangey*, no modern sub or click sheen.
It is the pulse under a 5-piece, not a rock anchor.

**MIC** — Earthworks DM6 SeisMic. Supercardioid condenser, 20 Hz–20 kHz, 150 dB SPL, from the
DK-6 kit (same kit as the DM17s and SR20sps — kit coherence). No switches. Not a ribbon, not TOUR.

**SEARCHES**
1. `Earthworks DM6 SeisMic kick drum mic frequency response review EQ live sound`
2. Direct fetch: TapeOp review #160 — "DM6 SeisMic Kick Drum Mic"
3. Cross-read: Sweetwater / FOH Magazine / B&H product + review copy

**CAPSULE FACT** (external, quantitative — three of them)
- **+9 dB @ 20 Hz** — TapeOp review #160, verbatim: *"a boosted low end (+9 dB at 20 Hz)"*
- **+8 dB @ 11–12 kHz** — TapeOp, verbatim: *"rising from 1 kHz to a +8 dB bump at around the
  11 to 12 kHz range"*
- **≈ −8 dB dip @ ~400 Hz** — Sweetwater product copy / response curve; TapeOp corroborates as
  *"gently dipping to a low-mid scoop"*

**WEB SAYS** — The DM6 is **voiced, not flat.** It is a smiley curve: big LF lift peaking low, a
low-mid scoop, and a pronounced HF bump for beater articulation. TapeOp: *"a generally natural,
but dare I say, pre-mixed/EQ'd tone"* with *"a modern, electrified feel"* relative to other
Earthworks mics, and the reviewer *"was never immediately compelled to reach for an EQ."* FOH /
user consensus echoes it — one report of four different kicks in one room, no EQ on any of them.
Earthworks' own copy admits the tailoring: response *enhanced* in the low range for round tone,
*"a slight high-end peak accentuates the beater impact."*

**KB SAYS** — `mic-library.md`, Condensers table: *"Earthworks DM6 — SeisMic **flat**/extended-LF
kick condenser. Honest, uncolored, huge sub reach — **takes full shaping.** Weakness: needs EQ to
get a 'modern' kick."* EQ tendency column: **"apply template as-is (flat/honest)."**

**VERDICT — DISAGREE.**
Not a nuance; the two sources say opposite things. The KB says *flat, uncolored, needs EQ to get a
modern kick, apply the template as-is.* The web says *pre-EQ'd smiley, already modern-sounding,
never reached for an EQ.* Both cannot be true. The KB has the DM6 filed with the other Earthworks
mics (SR25, SR20sp, DM17 — genuinely flat) and I think the DM6's tailoring was inherited from that
family assumption rather than measured. **→ question round, (a)/(b)/(c) fork.**

**Why this one is not academic:** the KB's instruction is *"takes full shaping"* on a channel whose
capsule is already **+9 dB @ 20 Hz** — pointed into a room whose worst node is **63 Hz**. Following
the KB literally means boosting low end into a baked capsule boost *and* a room resonance
simultaneously. That is precisely the stack the capsule gate exists to catch.

**LOCKER** — **No alternative.** The locker's nominal first call for kick is the two-mic
Beta 52 + Beta 91 rig ("standard two-mic setup for most shows"), but there is **one** kick channel
on this list, and for this material a single dark mono kick *is* the brief — the record's kick was
one mic in a room. The DM6 also keeps the kit all-DK-6 (DM6 / DM17 / SR20sp), which is a real
coherence win across eight channels. Specified mic stands.

**GENRE BEND** — Soul/Motown via the Dap-Kings, *not* modern R&B. The generic "dense genre" read
would want click and separation; the artist reference explicitly wants neither. **The 11–12 kHz
capsule bump is working against the record** — that sheen does not exist on *Back to Black*. It
gets removed, and that is the single most artist-specific move on this channel. Felt beater on
maple: beater definition lives at 2–5 kHz, not 11 kHz.

**VENUE BEND** — Memo is the heaviest filter here and this is the room's **highest-risk channel**
(KB: *"the 200 Hz node is particularly aggressive on low-frequency instruments"*; *"any boost in
that range needs to be weighed against the room"*). Nodes at 63 / 125 / 250–315 all sit inside the
kick's range. Indoor depth — **the FSQ −6 to −9 override does not apply.** Node cuts do not thin
the kick: the room hands that energy back.

**DRAFT BANDS** (Q225 layout, whole dB, cuts first)

| Band | Setting | Why |
|---|---|---|
| **HPF** | **45 Hz, 24 dB/oct** | Kills the tail of the capsule's baked **+9 @ 20 Hz** before it excites the room and eats headroom. Sits under the 22" fundamental (~60–70 Hz), so thump survives. Decisive slope. |
| **LPF** | **9 kHz, 12 dB/oct** | Removes the capsule's baked **+8 @ 11–12 kHz** sheen. This is the Daptone move. Keeps beater definition (2–5 kHz) intact. |
| **Band 4 (HF)** | **OFF** | The LPF already owns the 11–12 kHz job. A bell trim on top would double-dip the same baked peak. |
| **Band 3** | **−3 dB @ 250 Hz, Q 2.0, Bell** | Memo node. Deliberately placed **below** the capsule's ~400 Hz scoop so the desk cut is not stacked on a scoop the mic already dug (capsule gate, in reverse). |
| **Band 2** | **−3 dB @ 125 Hz, Q 2.0, Bell** | Memo node, sitting in the kick's body. Light on purpose — the room returns it. |
| **Band 1 (LF)** | **−4 dB @ 63 Hz, Q 2.0, Bell** | Memo's most aggressive low node, plus the upper tail of the capsule's +9 @ 20 Hz. |

**Zero boosts on this channel.** Every move is a subtraction from either a baked capsule peak or a
room node.

**GATE CHECK** — No boosts to justify. Reverse gate applied: the capsule's **~400 Hz scoop** is why
there is **no box/mud cut at 300–500 Hz** — the mic already dug that hole, and a desk cut there
would be a second scoop on top of the first.

**DYNAMICS**
- **Gate:** threshold −30 dB, **range 20 dB (partial — NOT a full mute)**, attack 2 ms, hold 40 ms,
  release 120 ms. Range-limited because the reference record is glued by bleed; a hard gate chops
  the kit apart and will chatter on the quiet jazz-side material. What must survive: soft
  passages and the kit reading as one instrument.
- **Comp:** Mustard **Blue (Neve)** — the record ran through a Neve into tape. 4:1, attack 20 ms
  (beater passes), release 150 ms, 3–4 dB GR.

**QUESTIONS** — One, and it is the DM6 web↔KB DISAGREE above. Fork for the round:
- **(a)** go with the research — treat the DM6 as pre-voiced, trim the baked peaks (what's drafted);
- **(b)** go with the KB — treat it as flat and shape it fully;
- **(c)** go with the research **and** correct the `mic-library.md` DM6 row + EQ-tendency column.
My read: **(c)**. TapeOp is a measured, named, quotable source with two hard numbers, and the KB
row reads like the DM6 was grouped with its flat Earthworks siblings by association.
