# Unit 10 — Lead Vocal × Shure Beta 58A (ch 16)

**INSTRUMENT** — **Reine Beau**, fronting a produced theatre show. Two distinct jobs on one channel,
and they pull opposite ways:
1. **Singing Amy** — a deep, smoky contralto with heavy chest voice and rasp, swinging from
   intimate jazz phrasing (*Me & Mr Jones*, *Love Is a Losing Game*) to full belt (*Rehab*,
   *Back to Black*).
2. **Talking.** This is Night Owl's **"show-umentary"** format — *"live music interleaved with
   documentary-style storytelling."* There are **long spoken passages between songs**, and they are
   half the product. A five-star review called it *"heartfelt, gutsy."*

**That second job constrains this channel more than the first.** Quiet spoken narration in a 1.6 s
room has to stay warm and intelligible — which rules out the thin, hard-gated, aggressively
HPF'd treatment a belting soul vocal would otherwise invite.

**MIC** — Shure Beta 58A. Supercardioid dynamic. No phantom, no switches. Not a ribbon, not TOUR.

**SEARCHES**
1. `Shure Beta 58A frequency response presence peaks dB supercardioid proximity chart live vocal`
2. Direct fetch: Wikipedia *Shure Beta 58A* · Shure spec sheet PDF (**403 Forbidden** — noted, not
   worked around) · musiconstage technical analysis (**TLS cert failure** — noted)
3. `Shure Beta 58A supercardioid null angle 126 degrees rejection sensitivity specifications`

**CAPSULE FACT** — Shure published:
- **50 Hz – 16 kHz** frequency response — documented roll-off points at both ends.
- **Two presence peaks: 4 kHz and 10 kHz.**
- **Attenuated below 500 Hz** — a deliberate, documented bass roll-off *"to counter the proximity
  effect."*
- **Supercardioid null at ~125° off-axis each side** (not 180°) — corroborated across sources.

**Honest limit, stated:** **no outlet publishes dB values for the two presence peaks.** Shure's own
spec sheet is 403-blocked and every secondary source reproduces the peak *frequencies* without
amplitudes. So I have the frequencies, the roll-off points, and the 500 Hz corner — enough to know
where the mic is voiced and to refuse to add anything there — but not enough to say by how much.
Where that matters, it's said below.

**WEB SAYS** — *"Tailored frequency response specifically shaped for vocals, with brightened
midrange and bass roll off to control proximity effect."* The supercardioid pattern is *"true…
throughout its frequency range,"* giving *"high gain before feedback, maximum isolation from other
sound sources, and minimum off-axis tone coloration."* The peaks *"create a natural brightness which
elevates vocals within a busy mix."* Wikipedia notes the Beta 58A *"has little in common with the
earlier and popular SM58"* — different capsule, different transformer.

**KB SAYS** — *"Shure Beta 58A — Supercardioid vocal dynamic, 50Hz-16kHz, <500Hz attenuated for
proximity control, **TWO presence peaks (~4kHz and ~10kHz)** — brighter/more bite than SM58,
tighter pattern, more gain-before-feedback. **Weakness: those peaks can get strident/sibilant.**"*
EQ tendency: *"ease off presence; tame box ~600Hz."*

**VERDICT — AGREE.**
Point for point, and the KB entry is the better-written of the two: 50 Hz–16 kHz ✓, <500 Hz
attenuated for proximity ✓, two peaks at 4 k and 10 k ✓, supercardioid with more gain before
feedback ✓, peaks can turn strident ✓. Nothing to reconcile. The KB's *"ease off presence"* is
**correct here** — unlike the RNDI's identical tendency line, this mic genuinely has documented
peaks to ease off.

**LOCKER** — **No alternative, and the reasoning is worth recording because the obvious swap is
tempting.** The locker's other lead-vocal call is the **Neumann KMS 105** (*"more detail and
presence than a dynamic"*), and on paper a condenser suits the storytelling. **Rejected on
concrete grounds:** the KB flags the KMS 105 as *"feedback-sensitive"* with *"the 12k air can turn
sibilant/harsh on a loud PA."* This channel is a hard-pushing singer, in a **1.6 s RT60** room,
**with a dedicated wedge** (Mix 6, "Star Wedge") pointed at them. Feedback margin is the binding
constraint, and the Beta 58A's supercardioid is specifically the mic that buys it. Specified mic is
the right call.

**GENRE BEND** — Cuts only, which is the house rule anyway — but here it converges with the capsule
gate: **the mic's 4 kHz and 10 kHz peaks already deliver the brightness that "elevates vocals within
a busy mix."** Amy's voice on record is dark, chesty and midrange-forward; it is not a bright modern
pop vocal. So the desk's job at the top is **subtraction from two documented peaks**, never
addition. A singer chasing Amy's rasp will push hard into exactly those peaks.

**VENUE BEND** — Memo, and the collision is specific: **a contralto's chest voice lands on the
200 Hz node.** The 250–315 node then sits inside the KB's named vocal box zone (300–600 Hz), so
those two justifications converge on one band. The 1.6 s RT60 makes the 4 kHz region wash — which
is also the KB's named feedback zone for handheld dynamics. Indoor depth.

**⚠ THE OPERATIONAL FACT — this is the most useful thing found on this channel:**
**A supercardioid's null is at ~125° off-axis, NOT 180°. At 180° there is a rear LOBE.**
So the **Star Wedge (Mix 6) must sit off to the side-rear at roughly 125°, not straight behind the
mic.** Putting a wedge directly behind a Beta 58A aims it into the mic's rear pickup lobe — the
classic supercardioid mistake, and the fastest way to lose the lead vocal in this room. Goes in
`mic_notes` and on the paperwork.

**DRAFT BANDS** (Q225 layout, whole dB, **cuts only — zero boosts**)

| Band | Setting | Why |
|---|---|---|
| **HPF** | **100 Hz, 24 dB/oct** | **Steep rather than high** — a decisive slope kills handling and proximity without moving the corner up into the chest voice. Deliberately *not* the 120–150 Hz an aggressive vocal HPF would reach for: **the spoken storytelling has to stay warm**, and a contralto's speaking fundamental sits ~165–200 Hz. The mic is already attenuated below 500 Hz, so this is the second stage, not the first. |
| **LPF** | **OFF** | Deliberate. The mic already ends at **16 kHz**; a filter there is theater. |
| **Band 4 (HF)** | **−3 dB @ 10 kHz, Q 1.5, Bell** | **Trims a documented baked peak.** Takes the strident edge off — the KB's named weakness — on a singer pushing hard. |
| **Band 3** | **−4 dB @ 4 kHz, Q 1.8, Bell** | **Trims the other documented baked peak**, and it's triple-justified: the peak is real, 2–4 kHz is the KB's named feedback zone for handheld dynamics (*"cut proactively"*), and a 1.6 s room washes it. |
| **Band 2** | **−4 dB @ 315 Hz, Q 1.8, Bell** | Memo's 250–315 node landing inside the KB's named vocal box zone (300–600 Hz) — *"this is where feedback most often starts building."* Two reasons, one band. |
| **Band 1 (LF)** | **−4 dB @ 200 Hz, Q 2.0, Bell — DYNAMIC (DEQ)** · Thr **−18 dB**, Ratio **3:1**, Atk **10 ms**, Rel **120 ms** | **The move on this channel.** Memo's 200 Hz node sits on a contralto's chest voice — but this singer alternates between whispered narration and full belt, so 200 Hz energy swings enormously. A **static** −4 leaves the storytelling thin; the DEQ acts **only on the belt** and lets the quiet speech through untouched. This is the KB's exact criterion: *"DEQ where a static cut won't hold."* |

**GATE CHECK** — **Zero boosts, per the cuts-only rule.** Gate applied in the direction that
matters: both HF bands are **trims of Shure-documented peaks (4 k, 10 k)**, not cuts of nothing —
and nothing is added at either, because the mic is voiced to deliver brightness there already.
**Caveat recorded:** since Shure publishes the peak *frequencies* but not their *amplitudes*, the
−3/−4 depths are judgment against the KB's *"can get strident"* and the room, not arithmetic
against a measured curve. Verify by ear at soundcheck.

**DYNAMICS**
- **Comp:** Mustard **Green (FET / 1176)** — **4:1, attack 10 ms, release 100 ms, 4–6 dB GR.** The
  aggressive, characterful choice, and it's the artist-referenced one: Tom Elmhirst's vocal
  treatment on this record is famously hard-compressed. It also has to hold a performer whose
  dynamic range runs from spoken whisper to belt in the same minute.
- **Expander — NOT a gate. Threshold −45 dB, range 10 dB only.** **What must survive: the quiet
  spoken storytelling.** The KB's *"gate or expander set to open cleanly on breath and close on
  silence"* is right for a song, and wrong for a show-umentary — a conventional gate will chop the
  front of narration lines. The range is kept very shallow deliberately.

**QUESTIONS** — none as a fork. Two items ride into `mic_notes` rather than the round: the **125°
wedge-placement note** (an instruction, not a question), and the **no-published-dB caveat** on the
two HF trims (a soundcheck check, not a build blocker).
