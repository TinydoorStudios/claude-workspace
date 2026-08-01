# Constraint card — Repertoire (Sound The Alarm) · FSQ · 2026-07-31

Written from a full re-read of show-deep-build SKILL.md this session. Re-read before the
question round and again before spec.json.

## Hard numeric rules
- **Whole dB only.** No half-dB anywhere, ever. Round up.
- **Cuts before boosts.** Find the problem and remove it before adding anything.
- **Vocals are cuts-only**, every genre, no exceptions. Feedback control, not taste.
- **No high-shelf band** unless Brian explicitly asks. All four bands stay Bell unless a shelf
  is reasoned and named.
- Typical cuts −4 to −7 dB, Q 1.5–2.0. Boosts +3 to +6 dB, non-vocal only.
- **FSQ outdoor override: cuts go DEEPER — −6 to −9 dB typical, up to −10 on mud/box.**
  Torn between two depths, take the deeper one. HPFs run high and decisive.

## Band order / numbering (Q225)
- Band 1 = LF … Band 4 = HF. Document order: HPF → LPF → B4 → B3 → B2 → B1.
- Any band can be Bell or Shelf; a Bell band can be Dynamic (DEQ documented inline in its row).

## Venue — FSQ specifics
- Fader 9 "Overheads" is **STEREO** — both OH mics on one fader. Never split 9/10.
- Fader 10 "SNARE PL8" is the snare plate **return**, not an input. Hard-protected in the patcher.
- Wireless faders **33 / 34 / 35 / 36**. Brittany = 33, BG 1 = 34, BG 2 = 35. 36 unused.
- FSQ faders 25–36 ship a template vocal/wireless curve — an MD override replaces only the
  bands it names, and the template HPF of 184 Hz must be checked against each singer's range.
- No room gain outdoors. The KS21 arch owns everything under ~45 Hz — no channel reaches for it.

## Weather (fetched, not assumed — Open-Meteo 2026-07-30 for 2026-07-31)
- 6 pm 89.8 °F / 32 % RH → 11 pm 78.9 °F / 42 % RH. Gusts 9–14 mph. Rain 1–2 %.
- **HOT and DRY.** Dry air = extra HF loss over the throw → **protect presence, do not
  over-cut the top.** Gusts 9–14 → HPFs high on every open mic; no LF reach.

## Mic rules
- **Locker fork on every mic'd input.** DI and XLR line feeds are EXEMPT (no capsule).
  One alternative max, three-sentence reason (win with a number · what it changes · honest
  cost), alternative must be free. An unanswered fork BLOCKS the build.
- **Capsule gate:** before any boost, state what the capsule already bakes in there. Boost
  inside a baked peak = trim or nothing. Don't deep-cut a zone the capsule already scooped.
- **Two-mic sources** (kick in/out, bass DI+cab): one signal, but each mic owns ONE lane top
  and bottom. No boost on both mics in the same zone.
- **Switchable hardware** (Beta 91A contour, Beta 27 pad/lowcut, SM81 HPF): state the assumed
  position, build for it, write the fallback into mic_notes.
- Ribbon = NO 48V in red. TOUR/artist gear is flagged, never swapped.
- Research floor: every unit gets a fresh web pass with ≥1 quantitative capsule fact and a
  NAMED external source. The KB is cross-check only, never the research source.
- Verdict is one word per unit: AGREE / DISAGREE / THIN. No "broadly aligns."

## Process
- One batched question round, locker forks at the top, before any EQ commits. Carried flags
  count as questions.
- Every unit closes with a five-layer TRACE: base · equip · genre · artist · venue.
- Reverbs required (3 vocal + 1–2 instrument + 1 general), Seventh Heaven preset names
  verbatim, every value anchored to factory.
- Dynamics are DOCUMENTED (COMP:/GATE: lines) — never patched into the .ses.
- Pre-commit audit with quoted evidence before spec.json.

## Genre / artist
- **R&B / neo-soul covers**, Cincinnati. Lead: Brittany Marie (SCPA-trained, jazz + classical
  + 2 yrs Cincinnati Opera). Two BGs. Verified: CincyMusic band page, CincyMusic "Women in
  Cincinnati Music," msmarie513.com.
- Genre bend: modern R&B wants a deep, extended kick and a controlled low-mid; vocal is the
  whole show and must sit forward without being bright; keys and guitar stay out of the
  vocal's 1–3 kHz lane.
