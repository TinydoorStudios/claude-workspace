# STAGED KB corrections — from the Back to Black deep build, 2026-07-14

**Status: STAGED, not written.** Brian approved all three in the question round. Hand to
`wiki-publish` at close-out — never write the live wiki silently.

---

## 1. `mic-library.md` — Earthworks DM6 row (Condensers table) — **CORRECTION**

**Currently says:**
> Earthworks DM6 | SeisMic **flat**/extended-LF kick condenser. Honest, uncolored, huge sub reach —
> **takes full shaping.** Weakness: needs EQ to get a 'modern' kick, captures everything incl.
> bleed. | **apply template as-is (flat/honest)**

**Should say:**
> Earthworks DM6 | SeisMic kick condenser — **pre-voiced, NOT flat.** Measured smiley: **+9 dB @
> 20 Hz**, low-mid scoop **≈−8 dB @ ~400 Hz**, **+8 dB @ 11–12 kHz** for beater articulation
> (TapeOp #160). TapeOp: *"a generally natural, but dare I say, pre-mixed/EQ'd tone"* with *"a
> modern, electrified feel"*; reviewer *"was never immediately compelled to reach for an EQ."*
> Weakness: the baked 11–12 kHz sheen is wrong for vintage/dark material; the +9 @ 20 Hz will
> excite a room. | **ease off boom, air — trim the baked peaks, don't shape**

**Why:** the row appears to have inherited "flat/honest" from its genuinely-flat Earthworks siblings
(SR25, SR20sp, DM17) by association. **At Memo the error is live, not academic:** "takes full
shaping" instructs a low boost on a capsule already lifted +9 dB @ 20 Hz, pointed into a room whose
worst node is 63 Hz — a boost stacked on a baked lift stacked on a resonance.

**Source:** TapeOp review #160, "DM6 SeisMic Kick Drum Mic" (verbatim, measured). Corroborated by
Sweetwater's response curve and Earthworks' own copy (*"a slight high-end peak accentuates the
beater impact"*).

---

## 2. `mic-library.md` — Neve RNDI row (DIs table) — **CORRECTION**

**Currently says:**
> Neve RNDI | Active transformer DI, smooth musical top, gentle harmonic warmth, full lows.
> Bass/gtr/keys direct. **Weakness: very slight HF softening vs a clean DI.** | **ease off presence**

**Should say:**
> Neve RNDI | Active transformer DI, class-A discrete FET. **Measured flat: ±0.25 dB from
> 25 Hz–44 kHz** (±1 dB, 12.5 Hz–63 kHz), input headroom **+20.5 dBu** (Rupert Neve published).
> **There is no HF softening** — SOS notes sub-40 Ω output gives *"minimal loss of
> high-frequencies"*, and reviewers find the highs have **more** clarity than a typical DI. The
> character is **level-dependent transformer harmonics**, not a response tilt: SOS finds *"a subtle,
> but definite, character… more pronounced at higher input signal levels."* **Take the warmth from
> DRIVE, not EQ.** | **apply template as-is (flat/honest) — nothing baked at either end**

**Why:** the current tendency line is **inverted**. It instructs cutting top off a DI measured flat
to 44 kHz, chasing a softness that isn't in the response. The row is reaching for something real —
the RNDI *does* have transformer character — but misattributes it to frequency response instead of
harmonic distortion, which loses the actionable half: you get it by hitting the DI harder.

**Reach:** three channels on this show alone (bass DI + keys L/R).

**Source:** Rupert Neve Designs published spec; Sound on Sound RNDI review.

---

## 3. `_tools/mic_data.json` — Lauten LS-408 record — **DATA FIX**

**Currently:**
```json
{"slug": "lauten-ls-408", "name": "Lauten LS-408",
 "category": "Large Diaphragm Condenser",
 "owned": false, "status": "Reference — not in locker"}
```

**Should be:**
```json
{"slug": "lauten-ls-408", "name": "Lauten LS-408",
 "category": "Large Diaphragm Condenser",
 "owned": true, "status": "Owned — in locker"}
```

**Why:** it contradicted `Memorial Hall/mic_inventory.csv`, which lists the mic as owned/Standalone.
Brian confirmed **owned**. Regenerate the gallery with `_tools/mic_wire.py` afterward — the faded
ring in `mic-library.md` comes from this field.

**Worth a sweep while you're in there:** four other records carry `owned: false` — Shure Beta 56A,
AT Pro 35, BSS AR133, Whirlwind IMP. If the Lauten was wrong, some of those may be too.

---

## 4. Enrichments — **ADDITIONS, not corrections** (the KB isn't wrong, just less precise)

| Mic | Add to `mic-library.md` |
|---|---|
| **Sennheiser MD 421-U** | **−8 dB @ 40 Hz** (rolling off from 80 Hz), **even midrange 80 Hz–1.5 kHz**, **+4 dB @ 2.75 kHz** rising into the 4–5 kHz peak (RecordingHacks plot). The −8 @ 40 is the operative fact on a **bass cab** — it physically cannot deliver a low-E fundamental, which is what makes the DI/cab lane split self-evident. Current row says only *"extended low end"*. |
| **Shure SM57** | **+7 dB @ 6 kHz** (*"an upward ramp from 2 kHz to about 6 kHz, where the mic becomes 7 dB more sensitive"*), proximity **+6–10 dB below 100 Hz**, and a **small dip at 300–600 Hz**. Current row says only *"presence 3-5kHz"* and *"builds box/honk 300-500Hz"* — both true, but the dip means **the 400 Hz cut should be lighter than reflex**, which the row doesn't convey. |
| **AKG C422** | The row's *"classic AKG brilliance rise ~6-12kHz"* is attributed to the **CK12** — but the C422 does **not** have the original brass-ring CK12. Gearspace + Austrian Audio: when AKG introduced the late-1970s **Teflon** capsule it *"conveniently retained the name 'CK12'"*. Could not confirm or refute the rise itself (AKG's manual is 403-blocked at both mirrors; no outlet publishes a C422 curve) — **flag the provenance rather than the claim.** Verified specs worth adding: **4.5 mV/Pa @ 1 kHz**, **self-noise ≤22 dB**, **max SPL ~133 dB @ 1 kHz**, and that patterns require the **S42E Remote Control Unit**. |
| **Shure Beta 58A** | **Supercardioid null is ~125° off-axis, with a rear LOBE at 180°.** Operationally the most useful fact on the mic — wedges go side-rear, never straight behind. The row covers the peaks and pattern but not the null angle. |
| **Earthworks SR25** | Maker data sheet: **20 Hz–25 kHz, +2 dB @ 30 cm**, 145 dB SPL, 10 mV/Pa, 20 dBA. Confirms the row's "flat" with a number. Also worth noting: **Brian's DK-25 SR25s are cardioid**; the current *Gen 2* SR25 ships supercardioid. The row is right — but the ambiguity will bite someone. |
| **Earthworks DM17** | **20 Hz–17 kHz** (an 8 kHz lower ceiling than the SR25 — free darkening), and **−51 dBV/Pa (2.8 mV/Pa)**, ~11 dB less sensitive than the SR25 sharing the DK-6 kit. Expect more gain on tom channels than on hat/OH. |

## 5. `venue-memorial-hall.md` — **observation, no change made**

The **locked CM4 crowd EQ** pairs an **HPF at 120 Hz** with a **−5 dB @ 63 Hz bell**. The HPF has
already removed 63 Hz — the bell does nothing. Transcribed **verbatim as locked** into this show
(the article says *"EQ is fixed — do not adjust show to show"*, so I didn't touch it), but it reads
like a leftover. Brian's call.

## 6. `eq-starting-points.md` — **candidate addition, needs a show behind it first**

The **artist-profile-over-genre inversion** this build turned on: for a *recorded-with-one-mic,
bleed-is-the-sound* reference (Daptone/Motown, Sun, early Stax), the KB's "dense / loud" modifier
(*"more aggressive EQ for separation. Faster comp, tighter gates"*) points the **wrong way** — the
overheads become the source, close mics become fill, gates go range-limited or off. Worth writing
up as a genre-modifier caveat **after 2026-07-16 confirms it works in the room**, not before.
