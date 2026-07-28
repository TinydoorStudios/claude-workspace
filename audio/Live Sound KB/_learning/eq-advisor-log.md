# eq-advisor — decision log

*Append-only learning log for the eq-advisor skill. One entry per finalized EQ recommendation.
Newest at the bottom. This is the raw record; durable lessons get proposed as KB write-backs to
`mic-library.md` / `eq-starting-points.md` and published via the wiki-publish skill.*

**Why this exists:** the skill self-improves by improving its knowledge source. Every show's calls —
especially the ones Brian overrides — are captured here so the pattern is visible over time and the
KB can be updated. A Brian override is ground truth.

---

## Entry template (copy for each recommendation)

```
### YYYY-MM-DD — <source> · <mic> · <genre> · <venue>
- Console: Q225 | Wing
- Moves: HPF … | LPF … | B4 … | B3 … | B2 … | B1 …
- Sourced: <which moves from KB, which from web/forum, which from manufacturer curve>
- Web↔KB: agreed | disagreed (how it was resolved)
- Brian override / confirmation: <what changed, or "none">
- Proposed KB write-back: <mic-library row / eq-starting-points note / none> — [pending | published]
```

---

<!-- entries below, newest at the bottom -->

## 2026-07-25 — Nasty Nati Band, FSQ (Rev 2.0, revised input list)

**PRO 35 80 Hz filter is a SWITCH, not a fixed roll-off.** Rev 1.0 of this show (7/23) documented
the Audio-Technica PRO 35 as having an inherent "80Hz rolloff 18dB/oct". The published spec is
"Filter: HPF −18 dB @ 80 Hz (Via Switch)" (RecordingHacks PRO-35 page) — it is defeatable on the
mic body. This matters on low brass: the sousaphone's +3 @ 90 Hz is fighting the mic if the switch
is engaged. Brian's call this show: switch OUT (flat) on sousa and bari. **Proposed KB write-back
to `mic-library.md`:** add the switch fact + max SPL 145 dB to the PRO 35 row, and note "switch OUT
on low brass" as the standing default. Not yet written to the wiki — staged for `wiki-publish`.

**Capsule gate blocked two boosts that the generic advice asks for.**
- Congas × SM57: standard advice is "boost ~5 kHz for crispy slaps." The SM57 bakes in +7 dB @ 6 kHz
  (presence rises from 2 k). Boost refused; took −2 @ 6 k instead, leaving ~+5 dB of the mic's own
  peak to do the work minus the outdoor harshness. Reverse gate on the same channel: the 57 has a
  minor baked dip 250–600 Hz, so the box cut was held to −4 rather than the FSQ default −6..−9.
- Bari sax × PRO 35: no top boost at all, against the generic 6–8 kHz "definition" advice, because
  the KB's correction for this mic is "ease off presence" and the bari is the dark horn of the
  section. Every other horn's 7–9 kHz lift still passes the gate — those sit above the presence
  lift in the rolled extreme top, compensating a roll-off rather than stacking a peak.

**Seven-horn lane map** (worth reusing for any brass-band show): sousa 350 mud / 1.2 k pitch ·
bari 300 mud / 600 honk · tenor 350 / 800 · bone 500 / 1.2 k bark · alto 400 / 1.5 k ·
tpt 1 500 / 2.7 k · tpt 2 450 / 3.0 k. Low instrument = low lane. **Proposed write-back to
`eq-starting-points.md`** as a brass-band section-slotting example.

**Genre note:** Rev 1.0 processed this band as generic "R&B, no artist dig" per Brian. The artist
pass this rev (CSO community-artists page, DownBeat, CincyMusic) puts them as a New Orleans
second-line brass band with HBCU marching and EW&F/Chuck Brown funk influence, led by trumpeter
Mike Wade. The horn section is the identity, not an accent — which is what justified re-slotting
all seven horns by lane.

---

## 2026-07-31 — 2nd Wind · Omega Psi Phi 85th Grand Conclave · FSQ (Rev 1.0 Deep Build)

*Built 2026-07-26/27 on the newly installed 39.9 MB FSQ template. 27 channels, 20 research units,
patcher PASS / readback PASS.*

**Genre gate:** verified before any research ran — R&B/funk/soul show band, evidence from The Bash
artist page (200+ songs, Aretha Franklin → Bruno Mars), GigSalad, Voice of Black Cincinnati and the
band's own Usher Tribute Part II production. Not split, no stop-and-ask.

**Two locker forks raised, both answered by Brian.**
- **CH 3/4 snare — Beta 98H/C → Audix i5, taken.** The measured RecordingHacks Beta drum-mic review
  found significant sub-100 Hz rim coupling and noticeably more hat bleed than a 57; the 98 is a
  horn clip-on doing snare duty. Brian's answer was **"i5 on ch 3 only"** — there's one in the DP8,
  so ch 4 kept the Beta 98. **The mixed pair turned out better than a matched one:** the i5's baked
  +9 dB @ 5500 forces a *trim* on ch 3, while the 98's lift starting *above* 8 kHz leaves room for a
  genuine +3 @ 8000 on ch 4. Same drum pair, opposite treatment, entirely capsule-driven — box 400
  vs 500, mid lane 900 vs 1200, HPF 150 vs 180. **Worth reusing:** when a section needs separation
  and the locker is short a matched pair, deliberately mixing capsules can do the slotting for free.
- **CH 5 hat — M1280BHC offered, ND408 kept.** Brian also confirmed the ambiguous "408" is the **EV
  N/D 408**, not the Lauten LS-408 (his shorthand rule only covers a 408 written on a *snare*).
  Consequence recorded on the channel: the −6 @ 4500 is load-bearing, because EV's own data sheet
  (part 531818-201) shows a broad presence rise centred 4–5 kHz — exactly where hat clank lives.

**Capsule gate blocked or reversed seven boosts.** The strongest three:
- **i5 on snare** — no crack boost (capsule bakes **+9 dB @ 5500**, trimmed −4 instead) and no body
  boost (**+5 dB @ 150**, B1 left flat with the HPF placed at 150 on that shoulder). Zero boosts on
  a snare channel, and the mic is the whole reason.
- **PRO 35 on congas** — every percussion chart says boost 2–4 kHz for slap. This capsule has a
  voiced presence lift and the KB's warning is "plasticky upper-mid if close"; clip-on *is* close.
  Trimmed −4 at 2500/2000 and let the transient carry the slap.
- **D6 kick** — no low boost (+5 dB baked at 40–60), no click boost (4 k and 10 k peaks), **and no
  box/mud cut at all** despite the FSQ outdoor rule, because the capsule already scoops 15–17 dB at
  700–800. Reverse gate: don't deep-cut a hole that exists.

**Gate extended to impulse responses (new).** CH 13's drafted +3 @ 3000 was **withdrawn** once Brian
confirmed the guitar's XLR feed is cab-simulated — a cab IR carries a speaker *and* a mic's response
with its own presence shaping around 2–4 kHz, so boosting there stacks a voicing exactly the way a
capsule peak does. **Worth reusing:** treat a cab-sim'd direct feed as a mic'd cab for gate purposes.

**Four-vocal slot map by VOICE TYPE, not hierarchy** (Brian authorised EQ on the house wireless).
Beta 58A on all four; separation done entirely with cuts:

| | Aretha (f, lead/MC) | Heather (f) | Vince (m, bass) | Markay (m, upper) |
|---|---|---|---|---|
| HPF | 130 | 140 | **90** | 110 |
| Box/chest | −6 @ 600 | −6 @ 550 | **−7 @ 350** | −6 @ 450 |
| Upper-mid | −2 @ 1600 | −3 @ 1800 | **−4 @ 700** | −3 @ 1200 |
| De-ess (dyn) | −3 @ 10000 | −3 @ 9000 | −2 @ 8500 | −3 @ 9500 |

Two reusable findings. (1) **The FSQ template's wireless baseline HPF of 184 Hz is wrong for a bass
voice** — E2 is 82 Hz, so Vince's whole lower octave sits under it. Any male bass singer on faders
33–36 needs that overridden. (2) **A bass voice's presence region is 1–3 kHz, the lowest of the four
voice types**, so his upper-mid cut goes *below* it at 700 Hz while the other three are cut inside
the 1.2–1.8 kHz nasal zone. Cutting a bass singer at 1.5 k costs intelligibility the others can afford.
All four de-essers are **dynamic** because RH climbed 50%→77% across the set — a static top-end value
set at 6 pm is wrong by 11 pm outdoors.

**Show-wide low-end slot map** (six sources, two octaves): 60 kick (baked, no boost) · 85 floor tom ·
100 bass · 110 rack 2 · 130 rack 1 · bass synth HPF'd out at 55. The FSQ template's own tom gate
(thr −36.2 dB, 130–317 Hz sidechain, faders 6/7/8 — new in the 2026-07-26 template) does the
separation between hits, so the three gated tom bodies can sit around the sustained bass.

**Three web↔KB disagreements found; all three carried to Brian rather than averaged.**
1. **SM57 presence peak — the KB row is wrong.** `mic-library` says 3–5 kHz. Shure's own published
   curve (user guide v3.6, 2025-A) is only up ~+2 dB by 3 kHz and peaks at **6–7 kHz, +5 to +6 dB**.
   Sent the bongo trim to 6000 instead of ~4000. **Proposed write-back to `mic-library.md`** — this
   matters more than the others because the 57 is the most-used mic in the locker.
2. **Beta 98H/C low end.** KB says "thin lows"; the measured drum review says enough sub-100 Hz to
   force a high-pass. Both true at different placements — thin clipped to a horn bell, not thin
   bolted to a snare rim. **Proposed write-back:** add the placement distinction to the row.
3. **Audix D6 scoop.** KB says ~600 Hz at −15 dB; sources put it at **700–800 Hz at −17 dB**, and the
   KB has no entry for the **baked peak just above 1 kHz** (trimmed −4 @ 1200 on this show).
   **Proposed write-back:** refine the numbers and add the missing peak.

**Four sources have no KB row at all** — synth bass, modeller/cab-sim direct guitar feed, sampling
pad (SPD-SX class), backing-track playback. All four verdicted THIN for that reason. **Proposed new
rows in `eq-starting-points.md`.** The common thread across three of them: they arrive as *finished
audio* that has already been EQ'd by someone else, so the gate question becomes "has this decision
already been made?" and the honest answer is one moderate venue-driven trim, not a full curve.

None of the write-backs above have been written to the wiki — staged for Brian, per the rule.
