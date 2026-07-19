# Unit 02 — Snare × Lauten LS-408 "Snare Mic" (ch 2)

**INSTRUMENT** — **Unresolved: the backline carries TWO snares** and the list has one snare channel.
- Gretsch USA Custom **Maple 5.5×14**
- Ludwig **Supraphonic Aluminum 5×14**

Role in THIS band: the backbeat of a Motown/Daptone revue — fat, dry, cracking, *not* bright and
not ringing. On the jazz-side material (*Frank* era, *Me & Mr Jones*) it also has to play brushes
and ghost notes at low level.

**MIC** — Lauten Audio LS-408 "Snare Mic." FET condenser, cardioid, purpose-built for snare.
20 Hz–20 kHz, 0.5 mV/Pa, 135 dB dynamic range min, 15 dBA self-noise (SOS).
**Switchable — two 3-position toggles.** Not a ribbon. **⚑ OWNERSHIP FLAG — see QUESTIONS.**

**SWITCH STATE ASSUMED — stated explicitly, per the two-switch rule:**
- **Low Cut → 80 Hz** (of Flat / 80 / 140)
- **High Cut → 12 kHz** (of Flat / 5k / 12k)

**SEARCHES**
1. `Lauten Audio LS-408 snare microphone review frequency response off-axis rejection filters`
2. `Lauten Audio "Snare Mic" LS-408 review Sound on Sound OR Gearspace presence boost dB "5 kHz" OR "6 kHz" frequency response curve`
3. Direct fetches: Sound on Sound review (LS-408 / LS-508) · Mixonline "A Mix Real-World Review" ·
   Vintage King product page (returned nav only — no data)
4. `Ludwig Supraphonic aluminum snare Motown soul records classic sound vs maple snare tone`
   (drum selection, not the mic)

**CAPSULE FACT** (external, quantitative)
- **Filters are 6 dB/octave, low-Q** — Mixonline, verbatim: *"smooth, 6 dB/octave, low-Q filters
  that sound great."* This is the load-bearing number for this channel: the mic's own filters are
  **gentle**, so the desk's steeper filters are complementary rather than redundant.
- **28 dB off-axis rejection** — Lauten official spec, corroborated by Mixonline.
- **135 dB SPL @ 0.5% THD**; gain needed only **5–8 dB** with *"no pad or EQ"* in most cases
  (Mixonline).

**WEB SAYS** — The switches are voicing changes, not plain filters, and Lauten documents each:
- **80 Hz Low Cut** — *"Reduce low-frequency spillover from kick drums and toms while **adding a
  slight presence boost** to the sound of your snare drum."*
- **140 Hz Low Cut** — *"Retain the presence boost … while significantly reducing phase
  incoherence and spillover from kick drums and toms."*
- **12 kHz High Cut** — *"…adds a dip after 7 kHz to help reduce cymbal bleed, followed by a slight
  increase from 12 kHz–15 kHz to help maintain a natural, open snare attack."*
- **5 kHz High Cut** — *"Reduce extreme bleed caused by cymbal or stage volume."*
- **Flat High Cut** — *"open, lifelike top-end air."*

Mixonline: at a 20–30° angle it *"increase[s] crack and top head snap,"* effectively doing what
usually takes two mics.

**The default curve is where the sourcing breaks down.** Sound on Sound is the only outlet
publishing curve shape, and two readings of that same review conflict:
- one rendering: *lift from 1–2 kHz, dips sharply at 3 kHz, rises around 5 kHz to capture the
  stick attack, reduced sensitivity 9–14 kHz to minimise cymbal bleed*
- the other: *"a 1 kHz dip combined with a small peak at around 3 kHz"*

Those describe nearly opposite midrange shapes. **No outlet publishes dB values for the response
curve at all** — not SOS, not Mixonline, not Lauten.

**KB SAYS** — `mic-library.md`, Condensers: *"Lauten LS-408 — FET large-diaphragm condenser voiced
specifically for SNARE — pressure-gradient, ultra-high SPL/dynamic range, onboard HPF (80/140Hz)
and LPF (5/12kHz) switches, tight rejection. Detailed, controlled crack. Weakness:
snare-specialized, not a general vocal/room mic."* EQ tendency: **"ease off body, crack, snap."**

**VERDICT — THIN.**
Not a disagreement — the KB and the web agree on everything either can actually assert (switches,
SPL, purpose-built, controlled crack). The problem is that **neither has a response curve with dB
values**, and the one source with a curve contradicts itself between renderings. So the switch
behavior is well-documented and I'll build on it; the **midrange curve is not knowable from
published sources**, and I have declined to place a band on it. That is the honest consequence of
THIN, and it is why **Band 4 is OFF** rather than filled with an invented 3 kHz move.

**LOCKER** — ⚑ **This is the ownership flag, and it forces the pass.**

`Live Sound KB/_tools/mic_data.json` — the structured record the gallery is generated from —
carries, explicitly:
```json
{"slug": "lauten-ls-408", "name": "Lauten LS-408",
 "owned": false, "status": "Reference — not in locker"}
```
That is deliberate data, not a formatting slip: it sits alongside four other mics flagged the same
way (Beta 56A, AT Pro 35, BSS AR133, Whirlwind IMP), and the C422 in the same file reads
`"owned": true, "status": "Owned — in locker"`.

But **Brian's own `Memorial Hall/mic_inventory.csv`** — the file the show xlsx's Mic Inventory tab
was copied from — lists it plainly among owned gear:
`Lauten Snare Mic, SDC, Cardioid, "Snare drum — purpose-built FET condenser…", Requires 48V, Standalone`

Two of Brian's own files contradict each other on whether the mic exists in the locker.

**One named alternative, if the Lauten is out: the spare Earthworks DM17.** Concrete win — the
DK-6 ships **×4 DM17s and this show uses only three** (ch 4/5/6), so the fourth is already in the
case, already on a rim mount, costs nothing, and the KB lists the DM17 for *"Snare, toms"*
directly. It also keeps all eight drum channels inside one kit (DM6 / DM17 / SR20sp), and its
flat/honest voicing suits the dark reference better than the alternative — the Audix i5's baked
**+9 dB @ 5.5 kHz** (KB) is exactly the modern crack this record does not have.
EQ below is still built for the **specified** Lauten.

**GENRE BEND** — Motown/Daptone backbeat. The crack is *baked into this mic* (Lauten voiced the
5 kHz rise for stick attack; the 80 Hz LC adds presence on top). So the desk adds **nothing** up
there — capsule gate. The 12 kHz High Cut switch is chosen precisely because *Back to Black*'s
snare has no open air on it; Flat's *"lifelike top-end air"* is the wrong record.

**Which snare — a real fork, with a strong read.** Ludwig's own copy calls the Supraphonic *"the
most recorded snare drum in history, with recordings by classic rock greats to **Motown
masters**"*; the aluminum shell is dry, crisp, cutting, with **less sustain**. Maple is warm,
resonant, boosted lows, **long sustain**, less projection. **The Supraphonic is both the artist
answer and the venue answer** — Memo's 1.6 s RT60 and its 200 Hz node will take a resonant maple
shell's sustain and smear it. Still the drummer's call → question round.

**VENUE BEND** — Memo's **200 Hz node lands directly on a 14" snare's shell fundamental.** That is
the collision on this channel, and it is why the deepest cut sits there. The 250–315 node adds the
cardboard-box zone on top. The mic's 6 dB/oct 80 Hz filter is too gentle to stop kick spill riding
Memo's **125 Hz** node into this mic — hence a desk cut there too. Indoor depth throughout.

**DRAFT BANDS** (Q225 layout, whole dB, cuts first) — snare assumed **Supraphonic**

| Band | Setting | Why |
|---|---|---|
| **HPF** | **90 Hz, 18 dB/oct** | The mic's own 80 Hz LC is only **6 dB/oct** — gentle. A steeper desk filter just above it is complementary, not a double-dip. Nothing useful on a 5×14 below 90. |
| **LPF** | **12 kHz, 12 dB/oct** | Complements the mic's 12k High Cut (again 6 dB/oct). Dark reference + hat bleed control. |
| **Band 4 (HF)** | **OFF** | **Deliberate.** The only published curve data for the 1–5 kHz region contradicts itself, and the crack is already baked in. No evidence = no band. |
| **Band 3** | **−3 dB @ 315 Hz, Q 1.8, Bell** | Memo 250–315 node — the cardboard-box zone on a 14" shell. |
| **Band 2** | **−4 dB @ 200 Hz, Q 2.0, Bell** | **The collision.** Memo's 200 Hz node sits on the shell fundamental. Deepest cut on the channel; the room hands it back. |
| **Band 1 (LF)** | **−3 dB @ 125 Hz, Q 2.0, Bell** | Kick spill riding Memo's 125 Hz node, passing straight through the mic's gentle 6 dB/oct 80 Hz filter. |

**Zero boosts.**

**GATE CHECK** — No boosts to justify. Applied in reverse: **no desk boost at 5 kHz** because
Lauten voices a rise there for stick attack (SOS), and the chosen 80 Hz LC *"adds a slight presence
boost"* (Lauten) on top of that — the crack arrives pre-made twice over. Adding desk presence would
stack a third time.

**DYNAMICS**
- **Gate:** threshold −35 dB, **range 15 dB (partial — NOT a mute)**, attack 1 ms, hold 30 ms,
  release 100 ms. **What must survive: ghost notes and brushes.** The Dap-Kings shuffle under
  *Rehab* and the whole *Frank*-era jazz side are built on ghost notes; a conventional gate erases
  them and chatters. Range-limited so the kit stays glued, per the one-mic reference.
- **Comp:** Mustard **Blue (Neve)** — the record tracked through a Neve to tape. 4:1, attack 15 ms
  (crack passes), release 120 ms, 3–4 dB GR.

**QUESTIONS** — three, all real:
1. **Is the Lauten LS-408 actually in the locker?** `mic_data.json` says `owned: false`;
   `mic_inventory.csv` says owned. Fork: **(a)** research/CSV — it's owned, use it as specified;
   **(b)** KB record — it isn't, fall back to the spare DM17; **(c)** it's owned **and** fix the
   `mic_data.json` record. My read: **(c)** — Brian's inventory CSV is the more recently-maintained
   file and the mic is specified on his own input list, which is not something you do with a mic
   you don't own. But I am not guessing on this one, because it decides ch 2's mic.
2. **Which snare — Supraphonic or Gretsch maple?** My read: **Supraphonic**, for both the Motown
   reference and Memo's RT60. If it's the maple, ring/sustain control changes and Band 3 gets
   deeper.
3. **Switch positions** — I've assumed **80 Hz LC / 12 kHz HC** and built to it. Confirm at
   soundcheck; the fallbacks are written into `mic_notes`.
