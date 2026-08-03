# Plan pass — FSQ 2026-08-02, two shows

Two separate shows, same stage, same backline, one night. Folders and packets are separate per
Brian ("2 shows"). The instrument × mic units are identical apart from CH19, so the unit research
below was run ONCE in this session and applied to both — that is not a cross-show cache: every
search ran fresh today, in this session, for both builds. The artist, genre, and TRACE layers are
researched and written **separately per act**.

## Genre gate (run before any other research)

- **The Shades** — Genre: live-instrument soul / alternative R&B with jazz and funk.
  Evidence: the band's own copy on CincyMusic ("live-instrument soul and alternative R&B band
  founded by songwriter and artist Mic. Carr"); shadestheband.com; Spectrum News feature
  2025-08-15 naming saxophonist Elijah Woodward. **Not split — no stop-and-ask needed.**
- **Ric Sexton** — Genre: smooth / contemporary jazz drawing on R&B, gospel and funk.
  Evidence: WYSO Dayton feature 2024-01-15 ("evening of smooth grooves"); ricsexton.com;
  album *Fruition* (2020). **Not split.**

Spelling: **Ric**, not Rick. Confirmed by Brian.

## Weather — fetched, not assumed

Open-Meteo, pulled 2026-08-02 for 39.1015/−84.5125, show window 5pm–11pm:
71–75 °F · **RH 87–94%** · wind 1–4 mph, gusts to 9 · rain 15–25% easing to 4% late.

Near-identical to the 2026-08-01 Repertoire night (73 °F / 96% RH). Same top-end call.

## Unit table (deduped)

| # | Unit | Channels | Shows |
|---|---|---|---|
| 01 | Kick in × Beta 91A | 1 | both |
| 02 | Kick out × Audix D6 | 2 | both |
| 03 | Snare top × Audix i5 | 3 | both |
| 04 | Hat × SM81 | 5 | both |
| 05 | Rack tom × e604 | 6, 7 | both |
| 06 | Floor tom × Beta 52A | 8 | both |
| 07 | Overheads × Beta 27 pair (stereo) | 9 | both |
| 08 | Bass DI × Whirlwind IMP | 11 | both |
| 09 | Bass cab × Shure PG52 | 12 | both |
| 10 | Guitar cab × e609 | 13 | both |
| 11 | Keys × Whirlwind IMP | 17, 18 | both |
| 12 | Sax × AT PRO 35 | 19 | Shades only |
| 13 | Sax × artist mic → FX pedal → XLR line | 19 | Sexton only |
| 14 | Vocal × Beta 58A (house wireless) | 33, 34, 35 | both |

Dead per Brian: CH4 (no snare bottom), CH14–16 (one guitar only), CH20–32.
CH10 is the template's SNARE PL8 return — reserved, never an input.

## Mined notes

- *"Stereo Ch 9/10"* on the OH row → **overridden.** FSQ runs the OH pair stereo on fader 9;
  10 is the plate return. Both recent FSQ builds (Repertoire, Nasty Nati) did the same.
- *"under mic"* on the hat row → hat mic under the hats, standard SM81 placement. No EQ change,
  but it means more snare bleed from below than a top-side hat mic → box cut earns its depth.
- *"Sax into FX pedal, out via XLR DI"* (Sexton) + Brian: *"he swaps and has his own mic"* →
  one channel carries alto AND soprano, through his own mic and his own pedal, arriving at
  line level. TOUR flagged. Build for the union of both horns.

## Carried flags — none

No prior rev, no prior show for either act at any venue. Searched active-projects.md and the
FSQ folder: no history for Mic. Carr, Shades, or Sexton.

## Question round — run once, up front, closed

1. **LOCKER FORK CH19 sax (Shades)** — N/D 408 specified, Beta 98H/C offered.
   → Brian: **swap to AT PRO 35** (his own third option). Fork closed.
2. **LOCKER FORK CH3 snare top** — e604 specified, Audix i5 offered.
   → Brian: *"you choose the better option… I'll follow."* → **i5.** Reasoning in unit 03.
3. One bill or two shows → **two shows**, separate folders.
4. Vocal count → **3 wireless each, that's all.**
5. Empty rows → no snare bottom · one guitar · Keys 1/2 on IMP DIs · CH20–24 dead.
6. Beta 52 count → **D6 on kick out, Beta 52A on floor tom.** Inventory conflict resolved.
7. Sexton CH19 → his own mic, he swaps horns on the one channel.
8. Vocalist voice types → **Brian doesn't know; asked me to research and suggest.**
   Web pass could not resolve voice types for either act (see unit 14). Built as ROLE slots with
   a male-and-female-safe HPF and three distinct cut lanes, flagged for swap at soundcheck.

Zero forks left open. No question blocks the build.

## Pre-spec re-read

Constraint card re-read immediately before the question round, and again immediately before
writing spec.json. Confirmed: no half-dB, no vocal boosts, no high shelf, CH10 untouched,
wireless HPF overridden, every boost gate-checked below.
