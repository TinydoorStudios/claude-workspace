# Plan — 2nd Wind Conclave · Fountain Square · 2026-07-31

## Genre gate (Step 2a)

**Genre: R&B / funk / soul show band (Motown + Top 40 + smooth-jazz inflections) — evidence:**
The Bash artist page ("funk, jazz, R&B, soul, pop, Top 40, Motown, big band"; 200+ song list
Aretha Franklin → Bruno Mars), GigSalad/Voice of Black Cincinnati listings ("high energy jazz
and R&B"), and their own event history (Ultimate Usher Tribute Part II, Memorial Hall OTR,
2026-06-27 — live vocals + dancers + production). Cincinnati's 2025 Best Performance Band.
**Not split — no stop-and-ask on genre.**

**The gig:** Omega Psi Phi Fraternity 85th Grand Conclave, Cincinnati, July 31 – Aug 3 2026.
Fountain Square has the community resource fair 9a–2p and **live music 6–11 pm on the 31st**.
10,000+ registered attendees in town — this is a big, loud, dancing crowd on a plaza, not a
listening set.

## Artist profile

Cincinnati show band, ~10-piece, four featured vocalists who front the show and work the crowd
(Aretha — also MCs; Heather; Vince Stroud; Markay — the last two appear in the Usher-tribute
lineup, matching Brian's wireless 3/4 assignment). They back national R&B/gospel acts (Kirk
Whalum, The Whispers, Fantasia, Charlie Wilson, Clark Sisters, Kurt Carr), which is the tell for
how this band actually works: **arrangements are tight and rehearsed, the vocal is the show, and
the rhythm section plays to a click with tracks under it** (ch 15 Click + ch 16 Track on the
input list confirm it).

FOH implications, in order:
1. **Four handheld vocals up front, all night, on an open plaza.** Gain-before-feedback is the
   governing constraint. Vocals stay cuts-only and the four voices get slotted against each
   other, not four copies of one curve.
2. **Tracks + pads carry the horn/string parts** the band's press describes — the input list has
   no horn channels. The tracks channel is a finished stereo-ish bed; treat it as program
   material, not an instrument to shape.
3. **Deep percussion rig** (congas ×2, bongos, toys) on top of a full kit — the 200–500 Hz
   region is where this show turns to mud outdoors. Separation lives in the cuts.
4. Dance-floor show at a fraternity conclave — low end matters, but a plaza has no room gain to
   lend it. Kick and bass get shaped, not just turned up.

## Room + weather (Step 4)

Open-Meteo forecast fetched 2026-07-26 for 2026-07-31, 39.1012 / −84.5120, show window 18:00–23:00:

| Hour | Temp °F | RH % | Precip % | Wind mph | Gusts mph |
|---|---|---|---|---|---|
| 18:00 | 80.6 | 50 | 7 | 2.1 | 9.4 |
| 20:00 | 73.8 | 66 | 7 | 8.3 | 15.4 |
| 21:00 | 71.5 | 71 | 8 | 8.8 | 16.1 |
| 23:00 | 67.9 | 77 | 8 | 6.5 | 14.5 |

Read: hot and moderately dry at doors (80.6 °F / 50% RH) drifting cool and humid by the end
(67.9 °F / 77%). HF air-loss over the throw is real early and eases as the humidity climbs —
so **protect presence, don't chase it with boosts** that will be too bright by 10 pm. Rain risk
7–8%, low, no contingency needed beyond the usual covers. Gusts to 16 mph is the number that
matters: windscreens on every open mic, and the overhead pair and percussion mics will collect
wash — another reason the HPFs run high.

## Channel map — the FSQ template reconciliation

The band numbered 1–24. The FSQ console reserves fader 10 (SNARE PL8 return) and carries the
overheads as a **stereo** channel on fader 9. Their OH L / OH R (their 9 and 10) collapse onto
fader 9, which makes the rest of their list land on the console 1:1 with no renumbering:

| Their ch | Console fader | Note |
|---|---|---|
| 1–8 | 1–8 | straight across |
| 9 + 10 (OH L/R) | **9** | stereo pair on one fader |
| — | **10** | RESERVED — SNARE PL8 return, no input |
| 11–24 | 11–24 | straight across |
| Wireless 1–4 | **33 / 34 / 35 / 36** | house wireless faders |

Faders 25–32 (Vocal 1–8) stay unused. No mults — no band input names a wireless unit.

## Unit table (dedupe: 24 channels + 4 wireless → 20 units)

| # | Unit | Channels | Fork? |
|---|---|---|---|
| 01 | Kick in × Shure Beta 91A | 1 | yes |
| 02 | Kick out × Audix D6 | 2 | yes |
| 03 | Snare × Shure Beta 98 (⚠ shorthand) | 3, 4 | yes |
| 04 | Hi-hat × "408" (⚠ ambiguous) | 5 | yes |
| 05 | Rack toms × Audix D2 | 6, 7 | yes |
| 06 | Floor tom × Audix D4 | 8 | yes |
| 07 | Overheads × Shure Beta 27 pair | 9 (stereo) | yes |
| 08 | Bass guitar × DI | 11 | **exempt (DI)** |
| 09 | Bass synth × DI | 12 | **exempt (DI)** |
| 10 | Guitar × XLR line feed | 13 | **exempt (line)** |
| 11 | Talkback × SM58 | 14 | yes |
| 12 | Click / Track × XLR line feed | 15, 16 | **exempt (line)** |
| 13 | Congas × Audio-Technica PRO 35 | 17, 18 | yes |
| 14 | Bongos × SM57 | 19 | yes |
| 15 | Toys / aux perc × SM81 | 20 | yes |
| 16 | Pads × DI | 21, 22 | **exempt (DI)** |
| 17 | Keys × XLR line feed | 23, 24 | **exempt (line)** |
| 18 | Female lead vocal × Beta 58A wireless | 33, 34 | **exempt (house wireless)** |
| 19 | Male bass-range vocal × Beta 58A wireless | 35 | **exempt (house wireless)** |
| 20 | Male upper-range vocal × Beta 58A wireless | 36 | **exempt (house wireless)** |

## Mined notes → research questions

- **Ch 15 "Click" + ch 16 "Track"** — the band runs to a click with backing tracks. Confirms the
  rehearsed-arrangement read and means the Track channel is program material (already mixed and
  mastered), not a source to shape. Click must never reach the PA.
- **Ch 21/22 "Pad 1 / Pad 2"** sit between the hand percussion and the keys in their numbering.
  That position reads as electronic drum pads (SPD-SX class), not keyboard pad patches — but
  it's a genuine fork. → question round.
- **Ch 3 "Snare Top" + ch 4 "Snare 2"**, both on "98". "Snare 2" is not "Snare Bottom" — it
  could be a side/second top mic or the bottom head. Polarity and EQ both hang on it. → round.
- **Ch 5 "Hat" on "408"** — Brian's own shorthand rule says a "408" written on a *snare* is the
  Lauten LS-408, and the ND408 is the EV N/D 408. Neither is a hi-hat mic in the KB (the hat
  go-tos are SM81 / M1280BHC / SR25). → round.
- **Ch 13 "Guitar" on XLR** — a line feed, so a modeler/amp-sim direct out rather than a mic'd
  cab. Which modeler and whether it's cab-sim'd changes the top-end treatment. → round.
- **Ch 14 "Edwin Talkback" on 58** — MD/bandleader talkback. Needs a routing answer more than an
  EQ (mains or comms only). → round.
- **No horn channels** on a band whose press sells a horn section. Consistent with tracks/pads
  carrying the parts, but worth one confirm line. → round.
- **48V and Stand columns arrived empty**, and the snake patch sheet is blank. Both get filled
  from the resolved mic list; split patch is Brian's load-in call.

## Carried flags

None — new artist, no prior show at any venue in `active-projects.md` or the shows index.
