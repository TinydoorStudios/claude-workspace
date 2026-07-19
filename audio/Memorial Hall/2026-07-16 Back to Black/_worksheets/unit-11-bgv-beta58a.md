# Unit 11 — Backing Vocals × Shure Beta 58A (ch 17, 18) — **SECTION**

**INSTRUMENT** — Two backing vocalists. In THIS band they are not decoration: the **60s girl-group
answer-vocal** is a signature of the record (*Back to Black*'s "we only said goodbye with words,"
the *Rehab* "no, no, no"). They also almost certainly cover the **horn lines** — see the note in
Unit 12 and the question round.

**MIC** — Shure Beta 58A ×2. Supercardioid dynamic. No phantom, no switches. Not ribbons, not TOUR.

**SEARCHES** — **Within-show dedupe: the full Beta 58A web pass ran in Unit 10** (three searches
plus two fetch attempts). Same mic, same show — not re-run. Section-specific reasoning below is
grounded in the Unit 10 capsule facts and the artist research in `plan.md`.

**CAPSULE FACT** — Carried from Unit 10, Shure published: **50 Hz – 16 kHz** · **two presence peaks
at 4 kHz and 10 kHz** · **attenuated below 500 Hz** for proximity control · **supercardioid null at
~125° off-axis**, rear lobe at 180°. (Peak amplitudes unpublished — same caveat as Unit 10.)

**WEB SAYS / KB SAYS** — See Unit 10. **VERDICT — AGREE**, same basis.

Additional KB rule that applies specifically here — `eq-starting-points.md`, *Choir/group vocals*:
*"Same cuts-only rule. **Upper-mid nasality from massed voices is usually the first thing to
address.** Gate typically off — the group never goes fully silent the way a solo vocalist does."*

**LOCKER** — **No alternative.** Same reasoning as Unit 10 (supercardioid feedback margin in a 1.6 s
room), and with **two more open mics** on a stage that already has a lead vocal and a wedge, the
gain-before-feedback argument is *stronger* here, not weaker. Specified mics stand.

---

## The section question — and a deliberate decision to NOT slot them

The pipeline's sectional rule says that when a show has a section and **the research says to
separate them**, the separation must be visible in the band values — three near-identical curves
under a "slot the horns" note is a failed build.

**Here the research says the opposite, and that conditional is the whole point.** The artist
profile (`plan.md`) is explicit: Winehouse *"knew that she wanted a '60s girlgroup sound"*; Ronson
and Salaam Remi built a *"synthetic Motown-style backdrop"*; the album's orchestration is
**Phil Spector-influenced**. Spector's entire method — the Wall of Sound — was **massing and
blending sources until they read as one instrument**, not separating them into legible lanes. A
girl-group answer-vocal is supposed to arrive as a single stacked voice.

So **ch 17 and ch 18 get the same curve, deliberately**, and that identity is the sourced decision
rather than an oversight. Both channels' `eq_summary` will name the lane they *share*: **the massed
answer-vocal, blended to read as one voice behind the lead** — and will say that the deliberate
non-separation is Spector, not laziness.

**Where they DO differ from the lead vocal (ch 16) — that separation is real and visible:**

| | Lead (16) | BGV (17, 18) |
|---|---|---|
| **200 Hz** | −4 **DEQ** (thr −18, 3:1) — must track whisper→belt | **−5 static.** They never whisper-narrate; a static cut holds, and goes **deeper** to clear the lead's chest voice. |
| **HPF** | 100 Hz — protects spoken narration | **130 Hz** — no narration to protect; get them out from under the lead. |
| **1.6 kHz** | not cut | **−4** — the KB's massed-voice nasality, which is a group problem the lead doesn't have. |
| **4 kHz** | −4 | **−3** — shallower; they need *some* bite to read as an answer, and they aren't the ones eating the wedge. |
| **Dynamics** | Expander (narration must live) | **None** — KB: the group never goes fully silent. |

**That is the slotting that matters on this show: lead vs. section, not BGV 1 vs. BGV 2.**

**GENRE BEND** — Girl-group blend, per above. Cuts only. The mic's 4 k/10 k peaks carry whatever
brightness the answer-vocals need; the desk subtracts.

**VENUE BEND** — Memo. Two more open supercardioids in a 1.6 s room is the feedback picture, so the
HPF is higher and the box cut is decisive. The **200 Hz** node again, and the **250–315** node
inside the KB's vocal box zone. Indoor depth.

**⚠ Same operational fact as Unit 10:** supercardioid null at **~125°**, rear **lobe** at 180°.
With three Beta 58As live at once, wedge and PA geometry relative to each mic's 125° null is the
gain-before-feedback story for the whole front line.

**DRAFT BANDS** (Q225 layout, whole dB, **cuts only — zero boosts**) — **ch 17 and ch 18 identical**

| Band | Setting | Why |
|---|---|---|
| **HPF** | **130 Hz, 24 dB/oct** | Higher than the lead's 100 Hz — no spoken narration to protect here, and it lifts the section clear of the lead's chest register. |
| **LPF** | **OFF** | The mic already ends at 16 kHz. |
| **Band 4 (HF)** | **−3 dB @ 10 kHz, Q 1.5, Bell** | Trims the documented baked peak; keeps two more open mics from adding strident air to the room. |
| **Band 3** | **−3 dB @ 4 kHz, Q 1.8, Bell** | Trims the other documented peak. **Shallower than the lead's −4** — the answers need enough bite to read, and these mics aren't in front of the Star Wedge. |
| **Band 2** | **−4 dB @ 1.6 kHz, Q 1.5, Bell** | **The section-specific move.** The KB: *"upper-mid nasality from massed voices is usually the first thing to address."* Two voices in thirds honk here in a way neither does alone. The lead does **not** get this cut. |
| **Band 1 (LF)** | **−5 dB @ 200 Hz, Q 2.0, Bell — STATIC** | Memo's node. **Deeper than the lead and static, not dynamic**, for two reasons: they never drop to narration so a static cut holds, and the extra depth clears room for the lead's chest voice to own that register. |

**Note:** the 250–315 box zone is handled by the **130 Hz HPF's slope** plus the 200 Hz cut on this
channel rather than a dedicated band — with four bands and the nasality cut being the higher-value
move on massed voices, that's the trade. The lead keeps its own 315 Hz band.

**GATE CHECK** — **Zero boosts, per the cuts-only rule.** Reverse gate: the 10 kHz and 4 kHz moves
are trims of Shure-documented peaks. The 1.6 kHz cut is not a capsule correction at all — it's the
KB's massed-voice rule, an ensemble phenomenon rather than a mic one. Same unpublished-amplitude
caveat as Unit 10 on the two HF trims.

**DYNAMICS**
- **No gate, no expander.** Straight from the KB: *"gate typically off — the group never goes fully
  silent the way a solo vocalist does."* Two singers trading in and out of a blend will chatter any
  gate, and the one-mic/spill reference argues against chopping anyway.
- **Comp:** Mustard **Purple (Optical / LA-2A)** — **3:1, attack 20 ms, release 200 ms, 3–4 dB GR.**
  **Deliberately not the lead's 1176.** Optical is program-dependent and gentle; it *glues* two
  voices toward one, which is exactly the Spector brief. The FET's grab would articulate them
  apart.

**QUESTIONS** — none as a fork. One item noted for soundcheck rather than the round: **if the two
singers turn out to be in clearly different registers** (say a soprano over an alto), the two HPFs
split at the desk — the upper voice comes up to ~150 Hz. That's an ear call in the room, not a
build blocker, and it doesn't disturb the blend decision. In `mic_notes`.
