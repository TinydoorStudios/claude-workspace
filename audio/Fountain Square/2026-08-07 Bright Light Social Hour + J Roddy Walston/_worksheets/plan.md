# Plan pass — FSQ 2026-08-07 · Bright Light Social Hour + J Roddy Walston

## Gig facts (fetched, not assumed)

- **Fountain Square, Friday 2026-08-07, 7:00 PM**, 520 Vine St — Visit Cincy "Friday Night
  Nationals", free/no ticket. Billed as J Roddy Walston + The Bright Light Social Hour
  (Songkick / allevents / myfountainsquare).
- **Running order (Brian): Bright Light Social Hour first, then J Roddy Walston.**
- Console: DiGiCo Quantum 225 (FOH) / Midas M32 (monitors). PA: L-Acoustics A15 + KS21 arch,
  X12 wedges.

## Weather — Open-Meteo, fetched 2026-08-06 for the 2026-08-07 show window

| Local time | Temp | RH | Precip prob | Wind / gust |
|---|---|---|---|---|
| 18:00 | 78.8 °F | 80 % | 29 % | 10.8 / 17.4 mph |
| 19:00 (doors/downbeat) | 77.5 °F | **82 %** | 26 % | 12.7 / **19.0** mph |
| 20:00 | 72.3 °F | **94 %** | 35 % | 10.1 / 12.3 mph |
| 21:00 | 71.9 °F | **92 %** | 28 % | 8.1 / 18.8 mph |
| 22:00 | 72.4 °F | 92 % | 17 % | 4.5 / 8.3 mph |

**Consequence** ([[humidity-inverts-outdoor-hf]]): RH climbs 82 % → 94 % across the two sets.
Saturated air stops absorbing HF over the throw, so **no HF boosts anywhere on this show** — every
baked capsule presence peak gets trimmed, not reinforced, and the genre-reflex 8–10 kHz cymbal
shimmer lift becomes a cut. De-essing/HF control on vocals goes **dynamic**, because a static value
dialled at 7 pm is wrong by 10 pm as the air keeps closing up. Gusts 17–19 mph at downbeat put the
overhead pair at **HPF 300**; 25 %+ precip probability all evening = rain contingency noted.

## Genre gate (verified before any other research)

**Bright Light Social Hour — Texas psychedelic rock / "mood-punk, cozmic soul"; groove- and
synth-forward, danceable.**
Evidence: Wikipedia ("American psychedelic rock band from Austin, Texas"); the band's own EPK
("mood-punk/cozmic soul", "a lush, space-western odyssey" — Consequence of Sound); Austin
Chronicle review of *Emergency Leisure* (2023) — "dance-flavored melodies, shimmering retro soul,
and sing-along anthems". Not split. Proceed.

**J Roddy Walston — piano-driven rock and roll / Southern-roots rock, "Zeppelin meets '50s rock"
(Brian, 2026-08-06).**
Evidence: Wikipedia (Southern rock, roots rock, hard rock, rock and roll; "known for their
energetic live shows and Walston's pounding style of playing the piano"); NPR 2013, *From A
Punished Piano, A Rollicking Sound* (tours with his own upright, "practically clobbering" it);
ATO Records. Brian's steer resolves the one open ambiguity — the 2026 return is billed as a solo
project "playing all your favorite songs in completely unfamiliar ways" (jroddywalston.com), which
left the arrangement weight genuinely open. **Confirm-item in the question round** (Q1) because
Brian's phrasing didn't name which band; my read is that it describes J Roddy, not BLSH.

## Unit table — 18 unique instrument × mic units (deduped across both bands)

| # | Unit | Bands | Channels |
|---|---|---|---|
| 1 | Kick In × Shure Beta 91A | both | 1 |
| 2 | Kick Out × Shure Beta 52A | both | 2 |
| 3 | Snare Top × Audix i5 | both | 3 |
| 4 | Snare Bottom × Sennheiser e604 | both | 4 |
| 5 | Hi-Hat × Shure SM81 | both | 5 |
| 6 | Rack Toms × Audix D2 (×2) | both | 6, 7 |
| 7 | Floor Tom × Audix D4 | both | 8 |
| 8 | Overheads × Shure Beta 27 (STEREO pair, fader 9) | both | 9 |
| 9 | Bass DI × Whirlwind IMP 2 | both | 11 |
| 10 | Bass Cab × Shure SM57 | both | 12 |
| 11 | Guitar Cab × Sennheiser e609 Silver | both | 13 |
| 12 | Keys DI × Whirlwind IMP 2 | both | BLSH 17/18 + 24 (Pad); JRW 17 |
| 13 | Keys Amp × Shure SM57 | both | BLSH 19; JRW 18 |
| 14 | Congas ×3 × Sennheiser e604 | BLSH | 20, 21, 22 |
| 15 | Aux Perc × Shure SM81 | BLSH | 23 |
| 16 | Vocals ×3 × Shure SM58 (wired) | BLSH | 25, 26, 27 |
| 17 | Guitar 2 Cab × Electro-Voice N/D 408 | JRW | 14 |
| 18 | Vocals ×4 × Shure Beta 58A (house wireless) | JRW | 33–36 |

Two bands share units 1–13; those get researched once and **bent twice** (psych-groove vs.
Zepp/'50s rock), which is where the per-band TRACE lines diverge.

## Lineups (research, cross-checked against the input sheets)

**BLSH** — Jackie O'Brien (bass/vocals), Curtis Roush (guitar/vocals), Mia Carruthers
(keys/vocals), Zac Catanzaro (drums), Juan Alfredo Ríos (percussion). Wikipedia + EPK.
The sheet matches exactly: ch 25/26/27 are named Curtis / Jackie / Mia, and the three conga
channels + aux perc are Ríos's rig. Five-piece, one guitarist → ch 14/15/16 read as spares.

**J Roddy** — sheet is a full band: kit, bass (DI + cab), two guitars, keys + keys amp, four
wireless vocals (BGV 1 / Roddy 1 / Roddy 2 / BGV 2). The Business disbanded end of 2019
(Wikipedia); 2026 is a return under his own name, so the backing lineup is unverified by name.
Doesn't change any EQ — noted only so nobody treats a named-member claim as sourced.

## Mined notes → research questions

| Sheet fact | What it forces |
|---|---|
| Kick In 91A + Kick Out 52A | **Two-mic source.** Both mics carry an attack emphasis (91A 4–9 kHz; 52A +7 dB @ 4 kHz) → hard lane split, no stacked boost, mono/polarity check. |
| Bass DI (IMP) + Bass Mic (57) | **Two-source pair.** 57 rolls off low (~200 Hz down, −10 dB @ 40 Hz) — the community treats it strictly as a blend mic. DI owns the bottom, 57 owns grind. |
| BLSH ch 17/18 "Key 1 Left / Right" | Stereo keyboard across two MONO template faders (Misc 1/2). Pan hard, gain-match, treat as a pair. |
| BLSH ch 24 "Pad" (IMP) | Finished-audio source → [[capsule-gate-covers-cab-irs]] applies: the production decision is already made upstream. Cuts only, one venue trim. Q6. |
| JRW ch 17 "Key 1" (IMP) + ch 18 "Key Amp" (57) | Acoustic upright with pickup vs. electric piano/keyboard is a **completely different channel**. Q2. |
| JRW wireless: Roddy 1 (W2) + Roddy 2 (W3) | Two mics on one singer → position mics or an effected mic? Decides identical vs. differentiated EQ. Q5. |
| BLSH ch 25/26/27 mic field "58", no wireless rows | Wired SM58 on stands, for three people who are all playing instruments. Q4. |
| Blank mic fields (BLSH 14/15/16, 28–32; JRW 15/16, 19–24, 25–32) | Read as template spares, not inputs. Q3. |

## Carried FLAGs from prior revs

None — this is a new show folder, no prior rev.

## Question round + locker forks

Fired to Brian 2026-08-06 before any EQ committed. See `../show.status.json` and the spec
`decisions` lists for the answers.

## Deliverable structure (Q7)

One folder, two complete packets + a changeover sheet:

```
Bright Light Social Hour.spec.json  → packet .md / .xlsx / Show Packet / EQ Reasoning / .ses
J Roddy Walston.spec.json           → packet .md / .xlsx / Show Packet / EQ Reasoning / .ses
FSQ 2026-08-07 - Band Changeover.pdf
FSQ 2026-08-07 - MASTER.pdf   = BLSH packet + BLSH rationale + CHANGEOVER + JRW packet + JRW rationale
```
