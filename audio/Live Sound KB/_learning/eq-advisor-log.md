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
