# NEW SHOW — start here

*The map for a show conversation. Pair with `ROUTING.md`.*
*Last updated: 2026-07-09 — slimmed to a router; the pipeline mechanics live in ONE place now,
the **show-deep-build** skill (which absorbed eq-advisor the same day). This file routes and
holds the don't-forgets; it no longer duplicates the skill's flow.*

---

A new show = a new conversation. Brian opens with the venue and show. From there:

**Deep Think is the default (standing rule, 2026-07-01).** Submitting a new show — channel list,
input list, artist + venue, ShowBuilder brief — means the full deep-research build runs. Brian
never says "deep think"; there is no KB-only fast path.

## 1. Route
Read the venue row in `ROUTING.md`: folder, console(s), base session, patcher, PA, and exactly
which KB articles to load. Pull **only** those.

## 2. Confirm the basics (don't assume) + intake
Show date, show name, input list source, monitors (wedges vs IEM), TOUR gear, anything the venue
row marks "confirm at first show." Ask for the tech rider / stage plot — the densest research
input there is. One round of questions up front beats a wrong rebuild.

**Intake (2026-07-19):** whatever Brian drops — rider/stage-plot PDFs, xlsx/CSV lists, photos or
screenshots of a list or email — gets read in full and normalized into the brief facts BEFORE
research (show-deep-build Step 0). Plot/rider file into the show folder as
`<Show> - Stage Plot.pdf` / `<Show> - Rider.pdf`; artifact conflicts go to the question round.

## 3. Scaffold
`python3 _system/scaffold_show.py --venue <v> --date YYYY-MM-DD --name "Show Name"` — dated
folder, venue patcher copy (Memo/FSQ), FOH Channel Processing stub, and `show.status.json` (the
per-show state file; packet + .ses builds stamp it automatically, the wiki push stamps
`published` — `verified` is optional, stamped only if Brian volunteers a desk load). All show
files live there.

## 4. Run the pipeline — the show-deep-build skill
Everything from here is the **show-deep-build** skill, end to end: artist + genre research
(fresh every show), per-channel EQ in the locked order **instrument → mic → genre → venue**
(Part II of the skill — the former eq-advisor), the mic-locker loop, the single batched question
round, the `spec.json` → `build_packet.py` packet (md / xlsx / Show Packet PDF / EQ Rationale
PDF / MASTER PDF), the `.ses` via the venue patcher, the handover (publish on Brian's go — no
console-verify gate, 2026-07-19), and the harvest.
Don't re-derive any of it here — trigger the skill.

Stage 2 (`.ses`) is Q225 venues only (Memo, FSQ); M32/Wing venues are manual. A rebuild-only
`.ses` run from existing paperwork is the **send-it** skill; publishing a show is
**show-wiki-push** (FSQ + Memo; `fsq-wiki-push` is its alias — other venues → **wiki-publish**),
gated only by Brian's explicit go — console verification is never required (2026-07-19).

## 5. Close out + harvest
The skill's step 7 covers it (KB harvest, eq-advisor log, active-projects + CHANGELOG,
IMPROVEMENTS/QUESTIONS, wiki push on Brian's go). When Brian says an output came out well,
that's the trigger to harvest it into the KB so the next conversation inherits it.

---

## Don't-forget rules
- Genre is VERIFIED first with named evidence before any research (2026-07-19); split/hybrid
  evidence = ask Brian immediately, the one exception to the batched round. Notated equipment
  (amp/cab, drum sizes, strings, pickups) rides the instrument layer with the mic-grade research
  floor, and every unit's research_summary closes with the five-layer TRACE line
  (base · equip · genre · artist · venue).
- THE KB IS FOR LONGEVITY, NOT RESEARCH (Brian, 2026-07-08). No model may source an EQ value from
  the KB — every instrument × mic unit gets a fresh web pass with a named external source and a
  quantitative capsule fact, no familiar-mic exemption. The KB's only build-time job is the
  cross-check (disagreement = stop-and-ask); its other job is receiving the post-show harvest.
- Capsule-voicing gate: never boost into a baked peak; trim it. Two-mic sources get full-spectrum
  lane ownership (no stacked boosts top or bottom).
- Sections (horns, BVs, twin guitars) are slotted in the band values, with each channel's lane
  named — a stated principle must be traceable in the numbers.
- Outdoor weather is FETCHED for the show window and quoted with numbers — seasonal assumptions
  are banned. Humid ≠ dry: hot+dry = protect presence from air loss; hot+humid = HF carries
  slightly better, don't over-boost it.
- Reverb settings anchor to factory values ("(factory)" / "(from X factory)"); presets picked for
  this band's material. Switchable hardware (contour, pads, caps) gets an assumed state + fallback.
- The question round consumes carried flags — a FLAG that survives two revs unasked is a failure.
- Memo: crowd-mic rig (OM1 / Deity S2 / CM4) always patched, CH numbers blank, fixed EQ.
- Classical = conservative, cuts-only. Acoustic/folk = watch the 1.5–2kHz piezo quack. Celtic =
  5ms+ attack, never gate sustained notes. Everything else = aggressive, whole-dB only.
- **Reverb suggestions required every show — FSQ included** (2026-07-08): Seventh Heaven Pro,
  3 complementary vocal + 1–2 instrument + 1 general when warranted, settings + in-plugin EQ +
  why + a pairing note. Preset names verbatim from the KB — never invented.
- FSQ / outdoor: cuts DEEPER than indoor — −6 to −9 dB typical, up to −10 on mud. Clarity first.
- Stage plots are band-provided — never generate one. FSQ ch 10 = SNARE PL8 return; OH stereo on 9.
- Broadcast = underheads/underhat, not overheads. Ribbon mics = NO 48V, flagged red.
- Vocals: cuts only, every genre. No high-shelf band unless asked.
- Every show ships the EQ Rationale PDF and the MASTER PDF. Default output is PDF; warm, direct
  writing (`about-me/writing-rules.md`).
