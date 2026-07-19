# Unit 12 — Playback × XLR line (ch 20)

**INSTRUMENT** — ⚑ **Unknown content, and it's load-bearing.** The list says only
`20 | Playback | XLR`. One channel, line level, no mic.

**What the research says it probably is.** Night Owl Shows' format is their trademark
**"show-umentary"** — *"live music interleaved with documentary-style storytelling about Amy's
career and rise to stardom"* (nightowlshows.com), and the venue page confirms *"storytelling
alongside interpretations of Winehouse's catalog."* That is a produced theatre show with narration
segments. **A single mono XLR labeled "Playback" in that context most likely carries the
documentary narration bed** — mono speech, pre-produced.

**But there's a second, competing reading, and it comes from a hole in the input list.**

The confirmed setlist is *Back to Black*, *Valerie*, *Rehab*, *Me & Mr Jones*, *Love Is a Losing
Game*, *Monkey Man*. **Every one of the up-tempo numbers there is horn-forward** — Ronson cut *"a
trio of horn players to create the '60s-sounding metallics"* (Wikipedia / Billboard), and the
Dap-Kings horn section is a signature of the record. **There is not one horn channel on this input
list.** So the horns are getting there somehow:
- **(a) on playback tracks** — which would make ch 20 a full-range music channel and one of the
  most important inputs in the show;
- **(b) played by the keys** — which changes Unit 09's patch expectations;
- **(c) sung by the BGVs** (ch 17/18) — common in small-combo soul tributes, and it would change
  Unit 11's arrangement read;
- **(d) dropped.**

**Ch 20 and the missing horns are the same question**, which is why it's asked once.

**MIC** — None. Line-level XLR into the desk. No capsule, no phantom, no ribbon risk, no TOUR flag.

**SEARCHES**
1. `"Back to Black" Amy Winehouse tribute band Cincinnati Memorial Hall 2026` (venue page fetch)
2. `Reine Beau "Back to Black" Night Owl Shows Amy Winehouse tribute band lineup musicians`
3. Direct fetches: memorialhallotr.com show page · nightowlshows.com show page
4. `Amy Winehouse "Back to Black" Mark Ronson production Dap-Kings recording sound 60s girl group Motown mono`

**Result of the lineup searches, stated plainly: Night Owl does not publish its band lineup or any
technical detail.** Four searches and two direct fetches of their own pages returned Reine Beau, the
format, the awards, and the setlist — and nothing about instrumentation, band size, horns, or
tracks. This is not a gap I can close from the web; it needs the band or a rider.

**CAPSULE FACT** — **Not applicable, and that's a real answer rather than a dodge.** A line-level
playback input has no capsule, no polar pattern and no frequency response of its own — there is
nothing to research about the "mic" because there isn't one. The research floor's purpose (know
what the transducer bakes in before you touch a band) has no object here. **What the channel
actually needs is the content answer**, which is in the question round.

**WEB SAYS / KB SAYS / VERDICT — N/A.** No mic, no web↔KB reconciliation to perform. The KB's
nearest applicable line is `mic-library.md`'s J48 entry — *"General-purpose active DI — keys, bass,
acoustic, **playback**"* — which is about a DI, not this XLR feed.

**LOCKER** — **N/A.** Nothing to substitute; there is no mic on this input.

**GENRE BEND / VENUE BEND** — Both depend entirely on the fork, which is the point:
- **If narration:** the whole job is **intelligibility in a 1.6 s RT60 room**, and the enemy is the
  250–315 node smearing consonants. Treatment is minimal — pre-produced narration is already
  mixed; the desk's job is to not wreck it and to clear the room's mud.
- **If music/horn tracks:** it becomes a full-range channel that must sit in the **horn lane**
  (KB: *"Brass/Horns — harshness in the upper mids, low-mid buildup… compression with a fast
  attack"*), and the HPF below is flatly wrong — it would gut the tracks' own kick and bass.

**⚠ A boost is permissible on this channel, and I want that said out loud rather than done
quietly.** The house rule is *"Vocals: cuts only, every genre"* — and its stated rationale is
**feedback control, not taste**. A playback XLR has **no microphone and therefore no feedback
loop**, so the rule's mechanism doesn't exist here. If the answer comes back "narration" and the
narration reads muddy in the room, a presence lift is on the table in a way it never is on ch 16.
I have not used one below, because pre-produced narration usually arrives finished and I'm not
going to boost a source I haven't heard.

**DRAFT BANDS** (Q225 layout, whole dB) — **provisional: assumes MONO PRE-PRODUCED NARRATION**

| Band | Setting | Why |
|---|---|---|
| **HPF** | **80 Hz, 18 dB/oct** | Clears rumble and room from a speech bed. **⚠ Wrong if this is music** — drop to 30–40 Hz, or the tracks lose their bottom. |
| **LPF** | **OFF** | Nothing to do to a finished source. |
| **Band 4 (HF)** | **OFF** | Pre-produced narration arrives mixed. Don't touch what you haven't heard. |
| **Band 3** | **OFF** | As above. |
| **Band 2** | **−3 dB @ 315 Hz, Q 1.5, Bell** | The one move I'll commit to blind: Memo's 250–315 node is what smears spoken consonants in a 1.6 s hall. Helps intelligibility regardless of source. |
| **Band 1 (LF)** | **OFF** | HPF owns it. |

**Deliberately near-empty.** Four bands off on an unknown source is the honest build; the answer
fills them in, not guesswork.

**GATE CHECK** — No boosts drafted, so nothing to justify. The permission analysis above is
recorded rather than exercised.

**DYNAMICS**
- **No gate.**
- **Comp:** Mustard **Purple (Optical / LA-2A)**, **3:1, attack 20 ms, release 200 ms, 3–4 dB GR** —
  gentle level-holding on narration so quiet passages carry to the balcony.
- **If it turns out to be horn tracks:** switch to **Blue (Neve), fast attack**, per the KB's brass
  rule — *"brass transients are aggressive and will jump above the mix."*

**ALSO — ch 19, TB (Beta 58A):** talkback. Utility, **not a show channel.** No EQ, no dynamics, no
reverb send, not in the FOH mix, no Input List section colour. Noted here so it isn't mistaken for
a dropped vocal.

**QUESTIONS** — one, in two parts, and they're the same question:
1. **What does ch 20 carry** — documentary narration, backing tracks, or both? **Mono or stereo?**
   (One XLR reads mono; ch 21/22 are free if a stereo pair is wanted.)
2. **Where are the horns?** *Rehab*, *Valerie*, *Back to Black* and *Monkey Man* are all horn
   records and there is no horn input. Tracks / keys / BGVs / dropped?

My read: **narration on ch 20, mono, and the horn lines sung by the BGVs or played by the keys** —
because a band carrying stereo horn tracks would have asked for a stereo playback pair, and this
list asks for one XLR. **Low confidence. This is exactly the kind of gap a tech rider or stage plot
would close in one line — is there one in an email?**
