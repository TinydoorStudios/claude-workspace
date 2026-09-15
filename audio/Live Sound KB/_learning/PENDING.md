# PENDING — KB write-backs waiting for Brian's yes/no

*Cleared 2026-09-14: Brian approved every item in four rounds; the D6/D4/PG52/SM57/SM81/'408' and four eq-starting-points rows were found already written on 08-08 and closed without a write. Ticked items below are history — the next publish appends new ones under a fresh heading.*

*The harvest queue. `show-wiki-push` appends each published show's `kb_writeback` and
`reconciliation` lines here. Every show-deep-build run opens by walking this list with Brian,
one item at a time (approve / skip / later); an approved item is written into the named KB
article and staged for `wiki-publish`, then removed from this file. Never write the wiki
silently. Seeded 2026-09-14 by pipeline-fix from questions.md, active-projects.md and
eq-advisor-log.md.*

Format: `- [x] **<article>** — <the change> — <source show(s)>`

## Mic Library (`mic-library.md` + the mic page)

- [x] **Audix D6** — mid scoop is at **700–750 Hz, −17 dB** (Audix spec sheet, RecordingHacks), not "~600 Hz −15 dB"; add the **+17 dB @ 10–12 kHz** baked peak the row lacks, and the twin-peak refinement from 2nd Wind 08-08. Flagged in three consecutive log entries — 2nd Wind Conclave 07-31, Repertoire 07-30, Shades/Sexton 08-02.
- [x] **Shure Beta 98H/C** — add a placement note: "thin lows" is true clipped to a horn bell and false rim-mounted on a snare, where the RecordingHacks drum review found enough sub-100 Hz coupling to need a high-pass. Distinction, not a verdict change — 2nd Wind Conclave 07-31.
- [x] **Shure Beta 58A** — four-voice HPF slotting by voice type (lead 100 / harmony 120 / at-kit 150 / low 90) — Buffalo Wabs 08-28; confirms the four-vocal slot map from 2nd Wind Conclave (90/110/130/140).
- [x] **Audix i5 vs Sennheiser e604 on snare** — body wins outdoors — The Shades 08-02.
- [x] **Electro-Voice N/D 408 on hi-hat** — the −6 @ 4500 call — 2nd Wind Conclave 07-31.
- [x] **Shure SM81 ×3** — quantity owned is three — 2nd Wind 08-08.
- [x] **Earthworks DM6 / DM17 / SR25** as a kit set; **Lauten LS-408** on snare — Back to Black 07-16.
- [x] **Audio-Technica PRO 35** on NOLA horns (warm clip, ease plastic top not overtones); **57/Beta 27** guitar blend; **e609-on-hat** flag — The Hot Magnolias 07-11.
- [x] **Shure Beta 27** as overheads — 9 kHz fizz trim — Buffalo Wabs 08-28.
- [x] **Whirlwind IMP** passive bass DI — definition @ 800 — The Hot Magnolias 07-11; upright bass through the IMP — Buffalo Wabs 08-28.

## EQ Starting Points (`eq-starting-points.md`)

- [x] **Four missing rows** — synth bass · modeller/cab-sim direct guitar feed · sampling pad (SPD-SX class) · backing-track playback. Shared principle: they arrive as finished audio someone already EQ'd, so the treatment is one moderate venue-driven trim, not a curve. All verdicted THIN for lack of a row — 2nd Wind Conclave 07-31, 2nd Wind 08-08 (post-EQ amp bass DI, emulated-amp guitar feed added there).
- [x] **Keyboards / line-level boards** and **processed artist pedal → XLR line feed** rows — THIN three builds running — Shades/Sexton 08-02.
- [x] **One-channel union EQ for alto + soprano on a single fader** (B3 at 3.5 kHz inside the soprano's harsh band, just above the alto's presence) — Ric Sexton 08-02.
- [x] **Host/talk mic curve on a house wireless** (HPF 120, LPF 12k, tighter and darker) — Ric Sexton 08-02.
- [x] **Conga trio slotted by physical size** (Quinto/Conga/Tumba rings 250/200/160, harmonics 700/550/450; refuse the 5 kHz slap boost on e604) — Bright Light Social Hour 08-07.
- [x] **Two guitars slotted by amp character** (bright blackface owns the top lane, tweed the midrange); **barrelhouse piano keeps its left hand** (HPF 50); **two mics on one singer share the curve** — J Roddy Walston 08-07.
- [x] **Piezo string band** rows — electric mandolin light-quack (THIN, no row), resonator/dobro 250 / 3.5k cuts, mando/banjo/acoustic FSQ-deep quack + mud — Buffalo Wabs 08-28.
- [x] **Banjo-pickup DI** (−8 @ 4k zing + body @ 200) — The Hot Magnolias 07-11.
- [x] **Kick 91/52 lane de-stack** — Buffalo Wabs 08-28; **bass DI/cab 100 Hz lane split** — The Shades 08-02.
- [x] **Backline-vs-input-sheet mismatch pattern** (sheet said Rack 1 / Rack 2 / Floor; backline shipped one 13" rack and two floors, so a D2 sat on a 16" floor tom — the +3/+4 @ 100 compensation and the template gate's 152–242 Hz sidechain aimed wrong) — Bright Light Social Hour 08-07.

## Pipeline Spec — FSQ (`pipeline-spec-fsq.md`) / venue article

- [x] **Saturated-air inversion, now confirmed on three consecutive FSQ nights** (Repertoire 87–99% RH, Shades/Sexton 87–94%, double bill 82→94%): RH ≥ ~90% ⇒ no HF boosts anywhere, trim every baked peak. Promote from emerging to established; RULES.md R26 already states it.
- [x] **Genre-over-venue low-mid call** — neo-soul warmth keeps −5/−6 on vocals/keys while drums and cabs take the full outdoor −7/−8 — Repertoire 07-30, confirmed The Shades 08-02.
- [x] **FSQ deeper-cut confirmation** — The Hot Magnolias 07-11.

## Reverb Reference / Console

- [x] **Mustard colour-per-source reasoning** (Blue/Red/Green/Purple by source) — Back to Black 07-16 → `console-digico-q225.md`.

## Show close-outs still owed (harvest rows exist in active-projects; wiki pages pending in this run)

- [x] Repertoire (FSQ 2026-08-01) · The Shades (2026-08-02) · Ric Sexton (2026-08-02) · 2nd Wind (2026-08-08) — publish (pipeline-fix does this) and stamp `harvested` once the items above that cite them are decided.

## From Repertoire (FSQ 2026-08-01) — queued 2026-09-14

- [x] **KB write-back** — NEW ROW — Shure PG52 (Brian's explicit instruction this session: 'deep search this and add it to the locker'). Cardioid dynamic, 30 Hz–13 kHz, 300 Ω, −55 dBV/Pa, neodymium, internal shock mount, 470 g, discontinued and superseded by the PGA52. Low hump 60–100 Hz, broad dip 200–800 Hz, presence rise 4–5 kHz, hard rolloff above 10 kHz. Sold as a kick mic; the community rates it a class above its price specifically on BASS CABINETS and floor toms, and a class below a Beta 52 on kick. EQ tendency: ease off presence ~4500; never boost the 60–100 hump; do not cut into the 200–800 dip. — Repertoire 2026-08-01
- [x] **KB write-back** — CORRECTION — Audix D4 row in mic-library.md. Replace 'reaches 35Hz' and 'less upper-mid attack — may need a touch of click' with the current-chart reading: +6 dB at 5 kHz, a secondary peak above 10 kHz, and a rolloff below 70 Hz. EQ tendency becomes: trim the 5 kHz peak, never boost it; restore weight around 80 Hz rather than expecting sub reach. — Repertoire 2026-08-01
- [x] **KB write-back** — GAP — still no KB row for a sampling pad / electronic drum pad, or for a keyboard arriving as a line-level board. Both were flagged on 2026-07-27 and both cost this build a THIN verdict. — Repertoire 2026-08-01
- [x] **Reconciliation** — CH 8 Audix D4 — the one real web-vs-KB conflict, and it contradicts at both ends. RecordingHacks, reading Audix's current published chart, gives +6 dB at 5 kHz and a rolloff below 70 Hz; the mic-library row says the D4 'reaches 35 Hz' and has 'less upper-mid attack — may need a touch of click.' Brian's call: go with the research AND fix the KB row. Under the KB reading this channel would have taken a click boost landing directly on a baked +6 dB peak. — Repertoire 2026-08-01
- [x] **Reconciliation** — CH 4 drum pad and CH 17/18 keyboards — no disagreement, because there is no KB row for either source to disagree with. Both verdicted THIN and built conservatively; the same gap was logged on the 2026-07-27 build and is still open. — Repertoire 2026-08-01
- [x] **Reconciliation** — CH 12 Shure PG52 — verdicted THIN for the same reason: the mic was not in the locker before this session. The web pass itself is strong and manufacturer-anchored, and the forum consensus independently confirms the 80 Hz hump the spec sheet's curve shows. — Repertoire 2026-08-01
- [x] **Reconciliation** — Every other unit AGREE — the KB's figures and the external sources matched on frequency and dB in each case, including the i5's +9 at 5500, the Beta 27's two +2 dB peaks at 5500 and 9000, and the Beta 58A's peaks at 4 kHz and 10 kHz. — Repertoire 2026-08-01

## From The Shades (FSQ 2026-08-02) — queued 2026-09-14

- [x] **KB write-back** — Audix D6 — update the mid-scoop centre from ~600 Hz to the measured 700-750 Hz, and add the +17 dB at 10-12 kHz figure the KB row currently lacks. — The Shades 2026-08-02
- [x] **KB write-back** — Bass DI + cab blend — no KB entry exists. Propose a mic-library blend row: DI owns below 100 Hz, cab mic owns above, HPF the cab at 100 as the lane boundary, mono-sum and flip the cab if thinner. — The Shades 2026-08-02
- [x] **KB write-back** — Keyboards / line-level boards — still no KB row after three builds. Propose an eq-starting-points section. — The Shades 2026-08-02
- [x] **KB write-back** — Shure Beta 52A on floor tom — the 'monster on floor toms once the kick mic is something else' consensus, plus the do-not-stack-the-outdoor-cut-on-a-baked-scoop rule, is worth a mic-library note. — The Shades 2026-08-02
- [x] **KB write-back** — Audio-Technica PRO 35 on sax — the built-in 80 Hz 18 dB/oct roll-off isn't in the KB row, and it changes where the desk HPF should sit. — The Shades 2026-08-02
- [x] **Reconciliation** — Audix D6: the web puts the mid scoop at 700-750 Hz where the KB says ~600 Hz. Same feature, and the web figure is the more precise one — taken as the working value and logged for KB write-back. The practical consequence is real: B3 was moved to 1200 Hz rather than cutting into the scoop. — The Shades 2026-08-02
- [x] **Reconciliation** — Audix i5 vs Sennheiser e604 on snare top: no disagreement between web and KB — both describe the i5 as body-lifted at 150 Hz and the e604 as thin and scooped. The fork was a judgement call Brian delegated, not a source conflict. — The Shades 2026-08-02
- [x] **Reconciliation** — Bass DI + cab blend: the KB has no entry for this at all, so the lane split is web-only. Verdicted THIN rather than papered over as agreement. — The Shades 2026-08-02
- [x] **Reconciliation** — Keyboards on a DI: the KB has no keyboard or line-level row — the same gap logged on the 2026-07-27 and 2026-08-01 builds. Verdicted THIN, values kept conservative. — The Shades 2026-08-02
- [x] **Reconciliation** — Vocal voice types: could not be resolved by research. Brian doesn't know them and no published source classifies these singers. Built as role slots with a male-and-female-safe HPF and three distinct cut lanes, and flagged for a wholesale curve swap at soundcheck rather than guessed at. — The Shades 2026-08-02

## From Ric Sexton (FSQ 2026-08-02) — queued 2026-09-14

- [x] **KB write-back** — Audix D6 — update the mid-scoop centre from ~600 Hz to the measured 700-750 Hz and add the +17 dB at 10-12 kHz figure. — Ric Sexton 2026-08-02
- [x] **KB write-back** — Bass DI + cab blend — no KB entry. Propose a mic-library blend row: DI below 100 Hz, cab mic above, HPF the cab at 100 as the lane boundary. — Ric Sexton 2026-08-02
- [x] **KB write-back** — Keyboards / line-level boards — still no KB row after three builds. — Ric Sexton 2026-08-02
- [x] **KB write-back** — Processed instrument line feeds (artist pedal -> XLR) — no KB guidance at all. Propose an eq-starting-points entry covering LINE input, pad, no 48 V, and the don't-stack-our-reverb-on-theirs rule. — Ric Sexton 2026-08-02
- [x] **KB write-back** — One channel carrying two horns — the union-EQ approach used on CH 19 (cut in the brighter horn's harsh band, just above the darker horn's presence) is reusable and isn't written down anywhere. — Ric Sexton 2026-08-02
- [x] **Reconciliation** — Audix D6: the web puts the mid scoop at 700-750 Hz where the KB says ~600 Hz. Same feature, web figure more precise — taken as the working value and logged for write-back. Consequence on the desk: B3 sits at 1200 Hz rather than cutting into the scoop. — Ric Sexton 2026-08-02
- [x] **Reconciliation** — Bass DI + cab blend: the KB has no entry, so the 100 Hz lane split is web-only. Verdicted THIN rather than paraphrased into false agreement. — Ric Sexton 2026-08-02
- [x] **Reconciliation** — Keyboards on a DI: no KB row exists — the same gap logged on the 2026-07-27 and 2026-08-01 builds. THIN, values conservative. — Ric Sexton 2026-08-02
- [x] **Reconciliation** — CH 19: nothing to reconcile because there is nothing to reconcile against — an unknown artist mic through an unknown pedal has no capsule data and no KB row. Flagged THIN and treated as a load-in item rather than guessed at. — Ric Sexton 2026-08-02
- [x] **Reconciliation** — Vocal voice types: could not be resolved by research. Fruition's credits name Mr. Wynn and Feyth but no source classifies either voice, and Brian doesn't know them. Built as role slots with a male-and-female-safe HPF, flagged for a wholesale curve swap at soundcheck. — Ric Sexton 2026-08-02

## From 2nd Wind (FSQ 2026-08-08) — queued 2026-09-14

- [x] **KB write-back** — mic-library: mark the Shure SM81 quantity as x3 — the row carries no quantity marker so the file currently reads as one, which cost a question round today (Brian confirmed three, 2026-08-08). — 2nd Wind 2026-08-08
- [x] **KB write-back** — mic-library / shorthand: a bare '408' is the Electro-Voice N/D 408 on ANY source including a snare; the Lauten LS-408 is referred to as 'the Lauten' or 'snare mic'. Root CLAUDE.md already corrected 2026-08-08 — the KB should match. — 2nd Wind 2026-08-08
- [x] **KB write-back** — mic-library: correct the SM57 presence peak from 3-5 kHz to Shure's measured 6-7 kHz / +5-6 dB. Carried unactioned from 2026-07-31; the old figure puts a boost onto a baked peak. — 2nd Wind 2026-08-08
- [x] **KB write-back** — mic-library: refine the Audix D6 row — dip nearer 750 Hz at about -15 dB below the peaks, and TWO high peaks at 4 kHz and 10 kHz rather than a single '~5 kHz'. Load-bearing on ch 8 of this very show. — 2nd Wind 2026-08-08
- [x] **KB write-back** — eq-starting-points: add rows for synth bass, modeller / emulated direct guitar feed, sampling pad, and backing-track playback. Carried unactioned from 2026-07-31, and three of this build's four THIN verdicts are caused by exactly these gaps. — 2nd Wind 2026-08-08
- [x] **Reconciliation** — One KB row was found already CORRECTED and matching today's fresh pass: the Audix D4 (ch 7). The row was fixed on 2026-07-30 against the same RecordingHacks reading of Audix's current chart found again today (+6 dB at 5 kHz, secondary peak above 10 kHz, rolloff below 70 Hz), on Brian's own call during the 2026-08-01 Repertoire build. The pre-correction row would have put a click boost straight onto a baked peak. — 2nd Wind 2026-08-08
- [x] **Reconciliation** — One refinement the fresh pass adds to a KB row, and it changed a value: the mic-library D6 entry says 'deep mid scoop ~600 Hz (-15 dB), peaks ~63 Hz and ~5 kHz.' Tape Op's measured review puts the dip nearer 750 Hz and shows TWO high peaks, at 4 kHz and 10 kHz. That moved ch 8's HF trim to 4000 — the peak actually measured — instead of a 5 k figure sitting between the two real peaks and catching neither, and it is why LPF 10000 is doing real work shading the second peak. Staged as write-back item 4. — 2nd Wind 2026-08-08
- [x] **Reconciliation** — One KB row corrected by Brian's own answer rather than by research: mic-library lists a single Shure SM81 with no quantity marker, while marking multiples explicitly everywhere else (MKH 40 (pair), OM1 (pair), DPA 4099 (x4)). Three channels on this list call for an SM81. Raised as Q2; Brian confirmed he owns THREE, so the proposed M1280BHC / M1280B reallocation was withdrawn and all three channels build on the SM81. Staged as write-back item 1. — 2nd Wind 2026-08-08
- [x] **Reconciliation** — One shorthand rule corrected in the root CLAUDE.md, not the KB: it claimed a bare '408' written on a snare meant the Lauten LS-408. Brian's answer on Q1 — 'the EV. i will always refer to the lauten as the lauten or simply snare mic' — means a bare 408 is ALWAYS the Electro-Voice N/D 408, on any source. Corroborated at the time by ch 4's blank 48V cell, since the EV is a dynamic and the Lauten is a phantom-powered condenser. The bad rule had already cost a question round on rev 1's hat; the table was fixed 2026-08-08 and the KB gets the matching note as write-back item 2. — 2nd Wind 2026-08-08

## From RatBoys (FSQ 2026-09-18) — queued 2026-09-14 · all written 2026-09-14 (mic-library touring-mic table; eq-starting-points cab front/rear + pedal steel)

- [x] **KB write-back** — NEW ROW — Shure Nexadyne NXN2: supercardioid dual-transducer kick, 20 Hz–16 kHz, −66 dBV/Pa, built-in 450 Hz scoop + broad 4.5 kHz lift (Mix). Tendency: no click boost, no cut at 450. — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Shure Nexadyne NXN6: supercardioid tom/snare, 50 Hz–16 kHz, −61 dBV/Pa, wide smooth ~6 kHz presence (Mix). Tendency: attack is baked, trim don't boost. — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Shure Nexadyne NXN5: supercardioid amp mic, 50 Hz–16 kHz, presence peak centred 6 kHz (Mix, PSW). Tendency: trim 6k on bright sources (steel). — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Karma K-Micro Silver Bullet: electret SDC, 20–20k, dip ~2 kHz, ~7 dB peak ~6.5 kHz (SOS). Hat/snare-bottom class. Tendency: trim 6.5k, never cut 2k. — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Audio-Technica PRO 37: SDC, 30 Hz–15 kHz, 141 dB SPL, big 7 kHz hype, roll-off above ~12k (Gearspace, RecordingHacks). Tendency: −6 at 7k on cymbals. — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Shure SM27: LDC, 40 Hz–20 kHz, 148 dB SPL, 9.5 dBA, flat with slight presence/air; rolloff 80/115, −15 pad (RecordingHacks). Cab and overhead use; nothing baked to trim. — RatBoys 2026-09-18
- [x] **KB write-back** — NEW ROW — Sennheiser MD 409: ~5 dB bump 100–200 Hz, dip <100, even to ~15k; NOT the e609 (which adds a broad 5k lift) (Xaudia measurements). Tendency: trim the low bump, mids honest. — RatBoys 2026-09-18
- [x] **KB write-back** — eq-starting-points — front + rear mic on one open-back cab: rear leg polarity-flipped, LPF ~2k, body-only lane 70–250, box cut ~450; front mic HPF above the rear's lane (RatBoys 09-18). — RatBoys 2026-09-18
- [x] **KB write-back** — eq-starting-points — pedal steel through a 1×12 combo: wide −7@350, −4@700, trim the mic's top; Steel Guitar Forum consensus (RatBoys 09-18). — RatBoys 2026-09-18
- [x] **Reconciliation** — Nine units THIN — touring mics with no KB row (NXN2, NXN6 ×3, NXN5, Karma K-Micro, PRO 37, SM27 ×2, MD409). Brian: build from the web findings and add the rows. — RatBoys 2026-09-18
