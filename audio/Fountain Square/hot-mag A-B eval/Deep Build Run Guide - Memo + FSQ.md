# Deep Build Run Guide — Memo + FSQ

*Exactly what to type to get the best result out of the show pipeline, every run. Built 2026-07-08 from the hot-mag A/B: the prompt below forces the behaviors that made the Fable 5 run (`hot-mag 3`) the stronger packet, so it works on any model — before or after the pipeline upgrade lands.*

---

## Before you type anything

1. **Start a fresh Cowork conversation** with the `audio` folder connected. A new show = a new conversation — don't bolt a build onto an old chat.
2. **Have the input list ready.** Best → worst: ShowBuilder `<Show>.brief.json` · xlsx/typed channel list with mics and notes · artist name only (the build will stop and ask for the list, so don't bother starting without one).
3. **Have the rider and stage plot if they exist.** Drop them in the chat or the show folder as `<Show> - Rider.pdf` and `<Show> - Stage Plot.pdf` — the MASTER PDF picks them up automatically, and the rider is the densest research input there is.
4. **Know your answers** for the question round (list below) so the build runs straight through after one reply.

---

## THE FSQ PROMPT — copy, fill the brackets, paste as your first message

```
New show — FSQ, [YYYY-MM-DD], [ARTIST NAME]. Run the full deep build.

Input list: [attached / pasted below / in the show folder].
Rider / stage plot: [attached / none exists — I asked].

Hold this build to the deep-research floor:

1. THE KB IS FOR LONGEVITY, NOT RESEARCH. Do not source any EQ value from the
   KB. Web-research EVERY instrument x mic unit with named external sources —
   including the familiar ones (57s, 58As, i5, D6, all of them). Each unit needs
   at least one quantitative capsule fact (a frequency + dB) in the research
   summary, and the summary closes with "no web<->KB disagreements" or the list
   of them. The KB's only job during the build is to cross-check what the web
   found; a channel justified by "KB only" is a failed unit. Any web<->KB
   difference comes to me with three options: go with the research, go with the
   KB, or go with the research and update the KB. If the research finds
   something better than the current KB entry (a more precise frequency, a
   baked-peak fact the KB lacks), offer me the KB update in the question round.
2. Before any boost, state what the capsule already bakes in. A boost inside a
   baked peak is wrong — trim it instead. Don't re-cut what a capsule already
   scooped.
3. Two-mic sources (kick in/out, blends): name the shared frequency zones and
   give each mic ONE lane across the whole spectrum — no stacked boosts on the
   same zone, top or bottom. Polarity checks in the notes.
4. Sections (horns, backing vocals, twin guitars): if the research says slot
   them, the band values must actually differ, and each channel's summary names
   the lane it owns. Audit your own numbers against your own stated principles
   before writing the spec.
5. Pull the show-window forecast and quote the real numbers (temp, RH, wind,
   rain risk) in the room context. No seasonal assumptions — humid and dry point
   opposite directions on HF.
6. Switchable hardware on spec'd mics (contour switches, pads, HF caps): state
   the assumed position and the fallback if it's wrong.
7. Reverbs: Seventh Heaven Pro preset names verbatim from the KB, every settings
   value anchored to factory — "(factory)" or "(from X factory)" — and presets
   picked for what THIS band's material needs, not the generic trio.
8. Comp/gate notes carry numbers (attack ms, ratio) and say what must survive
   the gate, tied to the genre.
9. Batch every question, locker alternative, and carried flag into ONE round and
   get them resolved — nothing ships as an open FLAG that I can rule on today.

Remember FSQ: outdoor deeper-cut rule (-6 to -9, up to -10 on mud/box), OH is a
STEREO pair on fader 9 and fader 10 is the reserved SNARE PL8 return, vocal
faders 25/26 ship a template wireless curve/notch — call out any override.

Ask your question round before committing any EQ. I want to see the searches run.
```

## THE MEMO PROMPT — copy, fill the brackets, paste as your first message

```
New show — Memo, [YYYY-MM-DD], [ARTIST NAME]. Run the full deep build.

Input list: [attached / pasted below / in the show folder].
Rider / stage plot: [attached / none exists — I asked].

Hold this build to the deep-research floor:

1. THE KB IS FOR LONGEVITY, NOT RESEARCH. Do not source any EQ value from the
   KB. Web-research EVERY instrument x mic unit with named external sources —
   including the familiar ones (57s, 58As, i5, D6, all of them). Each unit needs
   at least one quantitative capsule fact (a frequency + dB) in the research
   summary, and the summary closes with "no web<->KB disagreements" or the list
   of them. The KB's only job during the build is to cross-check what the web
   found; a channel justified by "KB only" is a failed unit. Any web<->KB
   difference comes to me with three options: go with the research, go with the
   KB, or go with the research and update the KB. If the research finds
   something better than the current KB entry (a more precise frequency, a
   baked-peak fact the KB lacks), offer me the KB update in the question round.
2. Before any boost, state what the capsule already bakes in. A boost inside a
   baked peak is wrong — trim it instead. Don't re-cut what a capsule already
   scooped.
3. Two-mic sources (kick in/out, blends, AxeMount): name the shared frequency
   zones and give each mic ONE lane across the whole spectrum — no stacked boosts
   on the same zone, top or bottom. Polarity checks in the notes. Ribbons = NO
   48V, flagged red.
4. Sections (horns, backing vocals, twin guitars): if the research says slot
   them, the band values must actually differ, and each channel's summary names
   the lane it owns. Audit your own numbers against your own stated principles
   before writing the spec.
5. Switchable hardware on spec'd mics (contour switches, pads, B3 HF caps):
   state the assumed position and the fallback if it's wrong.
6. Reverbs: Seventh Heaven Pro preset names verbatim from the KB, every settings
   value anchored to factory — "(factory)" or "(from X factory)" — and presets
   picked for what THIS band's material needs, not the generic trio.
7. Comp/gate notes carry numbers (attack ms, ratio) and say what must survive
   the gate, tied to the genre.
8. Batch every question, locker alternative, and carried flag into ONE round and
   get them resolved — nothing ships as an open FLAG that I can rule on today.

Remember Memo: standing waves at 63 / 125 / 200 / 250-315 Hz — any boost in that
range is suspect, DEQ where a static cut won't hold; working RT60 1.6s; the crowd
rig (OM1 / Deity S2 / CM4) is always patched with CH numbers blank and keeps its
FIXED EQ — don't re-derive it. Indoor — skip the weather pull.

Ask your question round before committing any EQ. I want to see the searches run.
```

### Why each numbered clause is in there

Every clause maps to a difference the A/B caught. Clause 1 is Brian's hardest guardrail (set 2026-07-08): the KB exists so lessons survive between sessions — longevity — not so a model can skip the search. It's why Fable trimmed the i5 instead of boosting it: it searched a mic Opus treated as "the KB already knows this one." Clause 2 is the same failure generalized. Clause 3 caught Opus boosting lows on both kick mics at once. Clause 4 is the horn line: Opus's research said "slot the horns" and its numbers didn't. Clause 5 is the weather: Opus assumed dry July air; the forecast said 74% humidity. Clauses 6–8 are the anchoring behaviors (contour switch, factory reverb values, numeric comp) that make the paperwork auditable at the desk. Clause 9 keeps flags from riding through two revs unresolved. The closing line — "I want to see the searches run" — matters: instant output is the tell that research was skipped.

---

## Step by step — the full run, both venues

**Step 1 — Paste the prompt.** The build routes via `ROUTING.md`, confirms date + name, and scaffolds `<Venue>/YYYY-MM-DD ShowName/`.

**Step 2 — Watch the research.** You should see artist searches first (live videos and setlists beat press copy), then per-unit mic research. If EQ numbers appear before you've seen searches, stop it and say: `You skipped the research floor — run the per-unit web pass first.`

**Step 3 — Answer the question round.** One message, everything batched. Expect some or all of:

- Mic-locker alternatives (one max per channel, with a concrete why) — accept or decline each
- Any blank or ambiguous mics on the list — name them
- Vocal assignments (who's lead, what's backing, what's SPARE)
- Mono vs stereo on keys/playback
- TOUR/artist gear confirmations (RF coordination, don't-touch gear)
- Monitor counts/splits if the list doesn't say
- Any web↔KB disagreement it found — rule on it, with "update the KB to match" always one of the options
- Anything the research found that beats the current KB entry — accept or decline the KB update
- Any flag carried from a prior rev — resolve it now

Answer everything in one reply. Half-answers mean a second round and a slower build.

**Step 4 — Let it build.** Spec → `build_packet.py` (validates, then writes .md / .xlsx / Show Packet PDF / EQ Rationale PDF / MASTER PDF) → venue patcher for the .ses. Two pass-lines to demand before accepting the .ses:

```
bytes changed outside mic'd blocks: 0  PASS
```
and an identical file size to the venue template. If either fails, the .ses doesn't go to the console.

**Step 5 — Check the packet before load-in.** Fast quality audit (this is the checklist hot-mag 3 passes and hot-mag 2 fails):

- research_summary: a named source per unit, a frequency+dB fact per unit, reconciliation line present
- No boost sitting inside a baked capsule peak
- Two-mic pairs: one lane each, no doubled boosts
- Section EQs actually differ, lanes named
- Outdoor: forecast quoted with numbers (FSQ) / Memo: no standing-wave boosts, crowd rig untouched
- Reverbs: factory-anchored values, genre-fitted preset picks
- Comp/gate notes numeric
- decisions list shows your question-round answers; no orphan FLAGs

**Step 6 — Console verify.** The build stops and waits — this is the hard stop. Check the flagged template overrides first (FSQ: vocal faders 25/26 wireless curve/notch removal). When it's right, say `verified`.

**Step 7 — Close out.** Say `publish to the wiki` for the wiki push, and let the harvest run (KB write-backs, active-projects, changelog). If you moved something live during the show and want it remembered, volunteer it — the pipeline logs it but won't ask.

---

## Quick reference — venue differences that change the run

| | FSQ | Memo |
|---|---|---|
| Console / patcher | Q225 · `apply_show_TEMPLATE_FSQ.py` | Q225 (house) · Memo patcher |
| Base .ses | `_TEMPLATE/brian fsq start.ses` | `_TEMPLATE/brian memo june 2026.ses` |
| Room filter | Outdoor: cuts −6 to −9 (to −10 on mud/box), no room gain, clarity first | Standing waves 63/125/200/250–315 Hz, RT60 1.6s, DEQ over static cuts where needed |
| Weather | Fetch show-window forecast, quote numbers | Skip (indoor) |
| Fixed template traps | Fader 10 = SNARE PL8 return; OH stereo on 9; vocal faders 25/26 ship wireless curve/notch | Crowd rig (OM1/Deity S2/CM4) always patched, CH blank, fixed EQ |
| Monitors | M32, 8× L-Acoustics X12 | Per show (IEM/wedges) — confirm |
| PA | L-Acoustics A15 / KS21 | House |

## What NOT to do

Don't paste EQ numbers into the prompt — the build researches them; your numbers belong in the question round or at the desk. Don't run Memo and FSQ shows in the same conversation. Don't skip the rider question — "none exists — I asked" is an answer; silence isn't. Don't accept a packet whose research summary has no named sources; that's the hot-mag 2 failure mode, and it's the one thing the whole prompt exists to prevent.
