# Question Round — answered 2026-07-14

Six questions, six answers. Nothing committed before this.

| # | Question | Brian's answer | What it changed |
|---|---|---|---|
| 1 | **Crowd rig** — C422s vs. the locked OM1/S2/CM4 rig | **BOTH** | Standard rig on **locked EQ** for FOH; C422 pairs as **flat multitrack capture**. Unit 13 unblocked. **+6 channels.** |
| 2 | **DM6 + RNDI web↔KB conflicts** | **Research wins + fix both KB rows** | Units 01, 06, 09 build to the measurements. **Two KB corrections staged** (not written live). |
| 3 | **What keyboard** | **Nord-class stage keys, patches** | Unit 09's provisional stands as drafted — the conservative 4-voice-safe curve was built for exactly this. |
| 4 | **Ch 20 + the missing horns** | **Backing tracks incl. horns** | **Unit 12 rebuilt.** Not narration — a full-range music channel in the horn lane. HPF 80 → 35 Hz. |
| 5 | **Lauten LS-408 owned?** | **Owned — use it + fix the record** | Unit 02 keeps the specified mic. **`mic_data.json` correction staged.** DM17 fallback dropped. |
| 6 | **Which snare** | **BOTH — swapped mid-set** | **Unit 02 needs a snapshot**, not one curve. Base = Supraphonic; snapshot carries the maple deltas. |

---

## Q1 — Crowd rig: BOTH. Channel assignment.

Standard rig needs six channels. The list's only blanks are **25–30** — exactly six. Assigned:

| Ch | Pair | Placement | EQ |
|---|---|---|---|
| 23/24 | **C422 #1** — Audience L/R | — | **Flat capture** (HPF 40 only) |
| 25/26 | **OM1** | Flown 18' above stage, 12' apart | **LOCKED** (verbatim) |
| 27/28 | **Deity S2** | Under main-floor PA, into audience | **LOCKED** (verbatim) |
| 29/30 | **CM4** | Balcony, rear-facing ORTF | **LOCKED** (verbatim) |
| 31/32 | **C422 #2** — Room L/R | — | **Flat capture** (HPF 40 only) |

**⚑ Two things to confirm at load-in:**
1. **CLAUDE.md says the Memo crowd rig should have CH numbers left BLANK on the input list.** The
   builder and the `.ses` patcher both require numbers, so I've used the list's own blanks. **These
   six are my assignment, not yours — move them freely.**
2. **Two C422 bodies + two S42E remotes** (+ two multipin runs). AKG's manual: patterns are set
   *"on the Remote Control Unit S42E."* No file records a C422 quantity.

**C422s left flat on purpose.** They're a capture — EQ decisions belong in post, where your
documented workflow already lives (`LDB_FabFilter_ProQ4_Settings.pdf`). I also rated the C422's
capsule research **THIN** (AKG's manual 403-blocked at both mirrors; no published curve), so
placing bands on it would be invention. HPF 40 Hz for subsonic/HVAC and nothing else.

**Observation on the locked CM4 EQ, not a change:** `venue-memorial-hall.md` gives the CM4 an
**HPF at 120 Hz** *and* a **−5 dB @ 63 Hz bell**. The HPF has already removed 63 Hz — the bell is
doing nothing. I've transcribed it **verbatim as locked** and am not touching it, but it looks like
a leftover. Worth a look when you're next in that article.

## Q4 — Ch 20 rebuilt: tracks, not narration

My read was wrong (I'd said narration, low confidence, and said so). The channel is now a
**full-range music bed carrying the horn lines** — one of the more important inputs in the show.

- **HPF 80 → 35 Hz.** The 80 Hz I'd drafted for speech would have gutted the tracks' own kick and
  bass. This was the specific thing the question existed to catch.
- **Section → HORNS**, so the paperwork says out loud where the horns are.
- **EQ is room-correction only** — Memo's 315 node and the 1.2 kHz brass bark. I am *not*
  second-guessing a finished mix; both moves are the room, not the record.
- **The KB's brass rule does not apply as written.** *"Compression with a fast attack — brass
  transients are aggressive"* is for **live** horns. This is a mastered track that arrives
  compressed. Light Neve glue (2 dB GR), not control.
- **Reverb: no send.** The tracks arrive with Ronson's production reverb already on them.
- **Knock-on to Unit 11:** I'd speculated the BGVs might be covering the horn lines. They're not.
  The Spector blend decision is unaffected — it was never resting on that.
- **Still open (a note, not a blocker):** one XLR reads mono. Backing tracks are usually stereo,
  and **ch 21/22 are free**. Built mono as the list specifies.

## Q6 — Snare: both, swapped mid-set

**Base curve = Ludwig Supraphonic** — the confirmed setlist is mostly *Back to Black* material and
the show is named after that album, so the aluminum drum carries the majority.

**Snapshot: `SNARE — MAPLE`**, deltas only:

| | Supraphonic (base) | Gretsch maple (snapshot) | Why |
|---|---|---|---|
| **HPF** | 90 Hz | **100 Hz** | Deeper 5.5" shell, more low. |
| **B2 @ 200 Hz** | −4 | **−6** | Maple's boosted lows **and** long sustain sitting on Memo's 200 Hz node — the room will smear it. |
| **B3 @ 315 Hz** | −3 | **−5** | Shell resonance/ring. Aluminum is dry and *"do[es] not necessarily need dampening"*; maple rings. |

**⚠ Re-check gain at the swap.** The Supraphonic's aluminum crack will hit the Lauten harder than
the maple. Headroom isn't the issue (135 dB dynamic range; Mixonline needed only 5–8 dB of gain) —
the fader balance is.

**Mic switches stay put across the swap** — they're physical and can't be snapshotted. **80 Hz LC /
12 kHz HC** serves both drums.

## Q2 + Q5 — Three KB corrections, STAGED not written

Per the skill: never write the live wiki silently. These are staged for `wiki-publish` at close-out.

1. **`mic-library.md` — DM6 row.** Replace *"flat/extended-LF… takes full shaping"* / EQ tendency
   *"apply template as-is (flat/honest)"* with the measured voicing: **+9 dB @ 20 Hz**, **≈−8 dB
   @ ~400 Hz**, **+8 dB @ 11–12 kHz** (TapeOp review #160) → tendency **"ease off boom, air;
   pre-voiced smiley — trim, don't shape."**
2. **`mic-library.md` — RNDI row.** Remove *"very slight HF softening"* and the *"ease off
   presence"* tendency. Replace with **±0.25 dB, 25 Hz–44 kHz** (Rupert Neve published) and the
   real character: **level-dependent transformer harmonics — take it from drive, not EQ** (SOS).
3. **`mic_data.json` — Lauten LS-408.** `"owned": false` → `true`; `"status": "Reference — not in
   locker"` → `"Owned — in locker"`. Gallery regenerates via `mic_wire.py`.

**Worth writing back too (enrichment, not corrections):** the MD 421-U's **−8 dB @ 40 Hz** and
**+4 dB @ 2.75 kHz** (RecordingHacks plot), and the SM57's **+7 dB @ 6 kHz** — the KB currently
says only *"presence 3-5kHz"*.
