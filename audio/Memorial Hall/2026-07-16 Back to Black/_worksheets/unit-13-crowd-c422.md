# Unit 13 — Audience / Room × AKG C422 (ch 23, 24, 31, 32) — ⚑ **BLOCKED ON THE ROUND**

**INSTRUMENT** — The room. Ch 23/24 "Audience Left/Right," ch 31/32 "Room Left/Right." Note on
ch 23/24: **"Stereo Channel."**

**MIC** — AKG C422. Vintage stereo LDC: **two twin-diaphragm capsules in one body**, coincident,
XY or M/S. Requires 48 V. **Requires the S42E Remote Control Unit** to set patterns. Not a ribbon.
Not TOUR.

---

## ⚑ This unit is not built, and that is the correct outcome. Three separate blockers.

### Blocker 1 — it contradicts the locked Memo crowd rig

`venue-memorial-hall.md` is unambiguous, in two places:

> **"Crowd Mic Rig (Standard — Patch Every Show)"** … *"All three pairs patch standard every show.
> EQ is fixed — do not adjust show to show."*

That rig is **Line Audio OM1** (flown 18' above stage) + **Deity S2** (under the main-floor PA,
into the audience) + **Line Audio CM4** (balcony, rear-facing ORTF) — **six channels**, with EQ the
KB calls **Locked**. `mic-library.md` repeats it under Standard Combos.

**This input list has none of them, and substitutes two C422 pairs.** My constraint card, written
before any research: *"Crowd rig is FIXED with LOCKED EQ — do not re-derive it. This show's list
shows C422 pairs instead. **That is a fork, not a licence to invent. ASK.**"* Deriving fresh crowd
EQ here would be overwriting a locked venue standard on my own authority. Not doing it.

### Blocker 2 — this needs TWO C422 bodies, and the KB records no quantity

The C422 is **one body holding two capsules = two console channels** (CLAUDE.md: *"Single body, two
capsules. XY mode = 2 console channels"*). So:
- ch 23/24 "Audience L/R" = **one** C422
- ch 31/32 "Room L/R" = **a second** C422

`mic_data.json` says `{"slug": "akg-c422", "owned": true, "status": "Owned — in locker"}` — **but
carries no quantity field**, and `mic_inventory.csv` has a single undifferentiated C422 row. Nothing
in the KB, the CSV, or the gallery says whether there are two. **Unanswerable from the files.**

**And a dependency nobody has mentioned:** per AKG's manual, the C422's patterns are set *"on the
Remote Control Unit S42E"* — three basic patterns plus six intermediate positions, independently
per capsule. The mic doesn't work without its remote/PSU and multipin cable. **Two C422s means two
S42Es and two multipin runs.** Worth confirming at the same time.

### Blocker 3 — the research says it may be the wrong mic for the job

See CAPSULE FACT below. **22 dB self-noise** on a mic whose whole job is capturing a quiet room is
a real objection, and the KB's own OM1 entry praises that mic for the opposite property.

---

**SEARCHES**
1. `AKG C422 stereo microphone CK12 capsule frequency response brilliance rise dB specs vintage`
2. `"AKG C422" specifications frequency response "20 Hz" OR "30 Hz" sensitivity mV/Pa self-noise dB max SPL comb stereo`
3. Direct fetches attempted: **Library of Congress AKG C422/C34/C33 manual PDF (403 Forbidden)** ·
   **MicPedia C422 page (403 Forbidden)** — both blocked, recorded rather than worked around.

**CAPSULE FACT** — from AKG's own manual (via search excerpts):
- **Sensitivity 4.5 mV/Pa @ 1000 Hz**
- **Self-noise ≤ 22 dB** open-circuit (**~26 dB** with a normal 500 Ω load)
- **Max SPL ~133 dB @ 1000 Hz** (500 Ω load, ≤0.5% THD)
- Two twin-diaphragm capsules; omni / cardioid / figure-8 plus six intermediate positions, set per
  capsule from the **S42E**; *"capable of comb filtering patterns."*

**Read the self-noise number against the job.** ~22–26 dB of self-noise is unremarkable for a
vintage LDC on a loud source — and **poor for capturing a quiet audience in a 556-seat hall between
songs**, which is precisely what "Audience" and "Room" channels exist to do. The KB's OM1 entry
sells that mic on *"very flat/natural, **low self-noise**"*; the MKH 40 entry on *"extremely low
self-noise."* The standard rig was chosen, in part, for the property the C422 is weakest at.

**WEB SAYS** — Two things worth having:
1. **The C422's "CK12" is not the CK12 the KB is describing.** Gearspace and Austrian Audio both
   record that when AKG introduced the late-1970s **Teflon** capsule, *"it conveniently retained the
   name 'CK12' for that new capsule development."* The C422 carries **two new-style Teflon "CK12"
   capsules — not the original brass-ring CK12** of the C12/C414 lineage.
2. The C422 is *"a further development of the well-known AKG C24."* Reverb/vendor listings
   consistently flag it as large, vintage and delicate.

**KB SAYS** — `mic-library.md`: *"AKG C422 — Vintage stereo LDC, two twin-diaphragm **CK12 capsules
(classic AKG brilliance rise ~6-12kHz)**, elastically suspended, M/S or XY. Smooth/full body with an
airy top. XY on horns. Weakness: large/delicate, proximity, the CK12 top can get bright."*
EQ tendency: *"ease off air, presence."*

**VERDICT — THIN**, with a specific reason to doubt one KB claim.

The KB asserts a **"classic AKG brilliance rise ~6-12 kHz"** and attributes it **to the CK12**.
That rise is genuinely the character of the *original brass-ring* CK12 (C12 / C414 lineage) — but
the C422 doesn't have that capsule; it has the same-named Teflon one. So the KB's line may be
**correct character inherited via the wrong provenance**, or it may be right for a coincidental
reason. **I could not settle it**: AKG's own manual is 403-blocked at both mirrors I tried, and no
outlet publishes a C422 response curve with dB values. I have sensitivity, self-noise, max SPL and
pattern behaviour — enough to argue about the mic's *fitness*, not enough to place a band on its
*curve*. Stated rather than papered over.

**LOCKER** — **The locker alternative here is the venue's own standard rig**, which is an unusual
place to end up and is the point. **OM1 + Deity S2 + CM4**, with concrete wins that are already
documented in the KB and not my opinion:
- **Self-noise** — OM1 *"low self-noise"* vs. the C422's ≤22 dB, on a quiet-room job.
- **Zero EQ work, zero risk** — the rig's EQ is **already locked and proven in this room**; the KB
  hands it over verbatim (below). A C422 rig means deriving crowd EQ from scratch on show day.
- **Placement** — the standard rig is three *purpose-placed* pairs (flown over stage / under the PA
  into the audience / balcony rear-facing). Two C422s cannot be in three places.
- **Robustness** — the KB's own C422 weakness line: *"large/delicate."*

**But the exemption may apply.** If Brian specified the C422s deliberately — and the shape of the
list suggests he might have — this is his call, not a locker swap. See the fork.

---

## The fork, with my read

**My read: the C422 pairs are for the MULTITRACK, not for FOH — and the standard rig is expected on
top of them, not replaced by them.** Reasons:
- Brian **multitracks every show**, and a coincident stereo pair on "Audience" plus a second on
  "Room" is a *recording* architecture — that's how you capture a hall for post, not how you add
  FOH crowd colour.
- The C422's strengths (smooth, full-bodied, coincident, mono-safe) are recording strengths; its
  weakness (self-noise, delicacy) matters less when it's feeding a capture.
- **The list has six blank channels (25–30)** sitting between the Audience pair and the Room pair —
  and the standard rig is **exactly six channels**. Suggestive. Not proof, and I'm not building on
  it.
- The KB says the standard rig patches *every show*. A list that silently drops it reads more like
  an unfinished list than a deliberate reversal.

**The options:**
- **(a)** C422 pairs only — the standard rig is genuinely off for this show. I derive fresh crowd
  EQ for the C422s, against a THIN capsule read. **Least comfortable.**
- **(b)** Standard rig only — the C422 lines come off the list; I use the **locked EQ verbatim**
  (quoted below, not re-derived).
- **(c)** Both — standard rig on its locked EQ for FOH, C422s as a clean multitrack capture with
  minimal/no FOH EQ. **My read.** Needs two C422 bodies + two S42Es, and eats 10 channels total.

**For option (b) or (c), the locked EQ, quoted from `venue-memorial-hall.md` — not re-derived:**

| Pair | Locked EQ |
|---|---|
| **OM1** (flown omni) | HPF 80 Hz · −5 dB @ 200 Hz Q2.0 · −6 dB @ 315 Hz Q2.0 · −3 dB @ 800 Hz Q1.5 |
| **Deity S2** (under PA) | HPF 100 Hz · −5 dB @ 200 Hz Q2.0 · −5 dB @ 315 Hz Q2.0 · −3 dB @ 2.4 kHz Q1.8 · LPF 16 kHz |
| **CM4** (balcony ORTF) | HPF 120 Hz · −5 dB @ 63 Hz Q2.5 · −6 dB @ 200 Hz Q2.0 · −5 dB @ 315 Hz Q2.0 · −4 dB @ 400 Hz Q1.5 · LPF 14 kHz |

**DRAFT BANDS — none. Deliberately.**
Drafting crowd EQ before this fork resolves would mean either overwriting a locked venue standard
or inventing a curve for a mic I've rated THIN. Both are worse than an empty cell.

**GATE CHECK** — N/A; no bands drafted.

**Procedural note for whichever rig lands:** the C422 is coincident, so **polarity-check L vs R and
verify the mono sum is clean before advancing levels** — the KB names this explicitly under
Brass/Horns (*"AKG C422 in XY: stereo pair in one body — polarity-check L vs. R capsule, verify
mono summing is clean"*), and AKG's own manual notes the two capsules are *"capable of comb
filtering patterns."* Also confirm the **XY vs. M/S** setting on the S42E — the list says "Stereo
Channel" but not which mode.

**QUESTIONS** — the biggest on the show, asked as one:
1. **Which crowd rig** — C422s only (a), the standard OM1/S2/CM4 (b), or **both** (c, my read)?
2. **Are there two C422 bodies**, and **two S42E remotes** to go with them?
3. If the C422s stay: **XY or M/S**, and what pattern per capsule?
