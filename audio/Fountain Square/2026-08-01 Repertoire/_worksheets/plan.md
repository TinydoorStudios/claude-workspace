# Plan pass — Repertoire (Sound The Alarm) · FSQ · 2026-07-31

## Genre gate
`Genre: R&B / neo-soul covers — CincyMusic band page (R&B, soul, hip-hop, pop);
CincyMusic "Women in Cincinnati Music: Brittany Marie"; msmarie513.com (lead vocalist's own
description: R&B/neo-soul, "dabbles in hip hop/rap").` Not split — Brian's "mainly R&B cover"
agrees. Neo-soul weighting on the vocal, not retro soul.

## Artist profile (draft)
Sound The Alarm Music Group, Cincinnati. Working R&B/soul cover band — weddings, restaurants,
concerts, corporate. Fronted by **Brittany Marie**, singer-songwriter, School for Creative and
Performing Arts, trained in jazz, classical and contemporary plus two years with the Cincinnati
Opera. That training is the tell: a supported, projecting voice with real dynamic range and
controlled vibrato, not a breathy pop-R&B delivery. Two backing vocalists. The band is a rhythm
section plus two keys and one guitar — no horns, no percussion — so the arrangement leans on
keys and the drum pad for color, and the vocal carries the show.

## Roster (confirmed by Brian 2026-07-30)
Guitar 2–4 (14–16) and Misc 3–8 (19–24) are spares, not used. Vocals 25–32 unused. Wireless 4
(fader 36) unused.

| Fader | Channel | Source | Notes |
|---|---|---|---|
| 1 | Kick In | Shure Beta 91A | boundary, contour assumed FLAT |
| 2 | Kick Out | Shure Beta 52A | |
| 3 | Snare Top | Audix i5 | |
| 4 | Drum Pad | DI, mono | pad model unknown — flagged |
| 5 | Hat | Shure SM81 | |
| 6 | Rack 1 | Audix D2 | |
| 7 | Rack 2 | Audix D2 | |
| 8 | Floor | Audix D4 | |
| 9 | Overheads | Shure Beta 27 (pair) | **STEREO on 9** — sheet had 9/10, corrected |
| 10 | SNARE PL8 | — | reserved plate return, protected |
| 11 | Bass DI | Whirlwind IMP | |
| 12 | Bass Mic | Shure PG52 | new to the locker — researched this session |
| 13 | Guitar 1 | **Electro-Voice N/D 408** | swapped off the sheet's e609 by Brian 2026-07-30; Fender Twin Reverb assumed |
| 17 | Key 1 | Whirlwind IMP | separate board/player |
| 18 | Key 2 | Whirlwind IMP | separate board/player |
| 33 | Brittany | Beta 58A (Wireless 1) | lead |
| 34 | BG 1 | Beta 58A (Wireless 2) | |
| 35 | BG 2 | Beta 58A (Wireless 3) | |

16 active channels.

## Research units (dedupe: 16 channels → 13 units)
1. Kick in × Beta 91A
2. Kick out × Beta 52A  *(two-mic pair with unit 1 — lane split reasoned together)*
3. Snare × Audix i5
4. Drum pad × passive DI  *(DI — locker fork EXEMPT)*
5. Hat × SM81
6. Rack toms × Audix D2  *(ch 6 + 7)*
7. Floor tom × Audix D4
8. Overheads × Beta 27 pair (stereo)
9. Bass DI × Whirlwind IMP  *(DI — fork EXEMPT)*
10. Bass cab × Shure PG52  *(two-mic pair with unit 9)*
11. Electric guitar / Fender Twin Reverb × Electro-Voice N/D 408
12. Keys × Whirlwind IMP  *(ch 17 + 18 — DI, fork EXEMPT)*
13. Vocals × Beta 58A wireless  *(ch 33/34/35 — house wireless XLR/RF, fork EXEMPT)*

Locker forks apply to units 1, 2, 3, 5, 6, 7, 8, 10, 11 only.

## Mined notes / assumptions
- Sheet note on ch 9 "Stereo with ch10" — overridden by the FSQ template rule.
- Guitar amp **assumed Fender Twin Reverb** (Brian, no rider). Bright, clean, 2×12, famously
  scooped-mid and top-forward — this materially changes the e609 EQ and must be cited.
- Drum pad model unknown, mono, through a DI. Content unknown — 808/sub risk against the
  acoustic kick. Flagged.
- No rider, no stage plot. Kick size, bass rig, drum sizes all unknown — the generic
  instrument carries, and nothing is invented.

## Conditions (fetched — Open-Meteo, 2026-07-30, for 2026-08-01 Cincinnati)
| Hour | °F | RH% | Wind | Gust | Rain% |
|---|---|---|---|---|---|
| 17:00 | 75.3 | 93 | 8.6 | 25.3 | 73 |
| 18:00 | 73.1 | 96 | 7.3 | 26.6 | 73 |
| 19:00 | 73.1 | 95 | 8.8 | 27.1 | 73 |
| 20:00 | 72.6 | 96 | 9.1 | 28.0 | 73 |
| 21:00 | 72.8 | 97 | 9.6 | 26.4 | 81 |
| 22:00 | 71.9 | 97 | 7.4 | 22.1 | 81 |
| 23:00 | 71.7 | 99 | 5.2 | 16.1 | 81 |

**Cool, saturated and windy — and probably wet.** 93–99% RH all evening, gusts 22–28 mph
through the first three hours, rain probability 73% climbing to 81%.

Three consequences run through every channel:

1. **Near-saturated air means almost no HF absorption over the throw.** The top end arrives
   at the back of the plaza essentially intact — brighter than the 30-something-percent
   nights this PA gets tuned on. So **no channel gets an HF boost**, and anything with a
   baked presence peak (i5 at 5.5k, Beta 58A at 4k and 10k, e609 at 4–5k, Beta 27 at 9k)
   gets trimmed rather than left alone.
2. **Gusts to 28 mph are the highest-risk factor on the night.** Every open mic runs a high,
   decisive HPF; the OH pair is the most exposed thing on the stage and gets treated as a
   wind problem first and a cymbal mic second.
3. **Rain risk 73–81%.** Operational, not EQ: no ribbons (already none in this list), and
   the Beta 27 pair flown as overheads is the one condenser most exposed to blowing rain.

## Carried flags → question round
1. Drum pad content (808/sub?) — decides the kick/pad low-end split. Assumed to carry some
   sub content; kick and pad built to split the bottom, not stack it.
2. Guitar amp assumed Fender Twin Reverb per Brian — no rider to confirm it.
3. Rain contingency for the flown Beta 27 OH pair.
