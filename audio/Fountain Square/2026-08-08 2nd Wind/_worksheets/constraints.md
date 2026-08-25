# Constraint card — 2nd Wind · FSQ · 2026-08-08

Written from a full re-read of show-deep-build (not from memory). Re-read before the question
round and again before spec.json.

1. **Whole dB only.** No half-dB, anywhere, ever. Round up.
2. **Cuts before boosts.** Find the problem, cut it, then decide if a boost is still needed.
3. **Vocals are cuts-only** — every genre, no exceptions. Feedback control, not taste.
4. **No high-shelf band unless Brian asks.** He didn't. All bells (or filters).
5. **Band order + numbering** matches the console: B1 = LF … B4 = HF. Document order is
   HPF → LPF → B4 → B3 → B2 → B1.
6. **Ribbon = NO 48V, in red.** No ribbons on this show — but the Beta 27s, SM81(s) and any
   condenser DO need 48V, and the 48V column arrived blank. Fill it from the resolved mic list.
7. **TOUR gear is never swapped.** Nothing is flagged TOUR on this list yet — the Marshall and the
   band's own DIs/XLR feeds are their gear but they are line feeds, not capsules.
8. **Locker fork on every mic'd input.** DI and XLR line feeds are EXEMPT. Three-sentence reason:
   the win with a number · what it changes here · the honest cost. One alt max per input. An
   unanswered fork BLOCKS the build. Alt must be free (not assigned elsewhere this show).
9. **Cut/boost ranges:** cuts −4 to −7 dB tight Q (1.5–2.0), boosts +3 to +6 dB on non-vocal
   sources. **FSQ/outdoor override: cuts run DEEPER — −6 to −9 typical, up to −10 on mud/box.**
   Torn between two depths, take the deeper. HPFs run higher. Clarity is the whole game.
10. **FSQ template reservations:** fader 10 = SNARE PL8 reverb return, hard-protected, never an
    input. The overhead pair is a STEREO channel on fader 9 — never split across 9/10.
11. **House wireless = FSQ faders 33/34/35/36.** No band input names a wireless unit this week, so
    no mults. A bare "W58" with no unit number would be a stop-and-ask (none present).
12. **Research floor.** Fresh web pass every unit, every show — no cross-show cache, no "familiar
    mic" exemption. A unit is not researched until I can state ≥1 QUANTITATIVE capsule fact
    (a frequency and a dB value) with an EXTERNAL source named. KB is for cross-check and
    conflict resolution, never the source.
13. **Capsule gate.** Before any boost, state what the capsule already bakes in there. A boost
    inside a baked peak becomes a trim or nothing. Don't deep-cut a zone the capsule scooped.
14. **Cab-sim / capsule gate covers IRs.** A speaker-emulated direct feed counts as a mic'd cab —
    don't boost into the emulation's own presence shaping.
15. **Reverbs are required** — 3 complementary vocal, 1–2 instrument, Seventh Heaven Pro preset
    names verbatim from the reverb KB, every value anchored "(factory)" or "(from X factory)",
    preset SELECTION justified by this band's material. Plus `reverb_pairing`.
16. **One batched question round** before any EQ commits. Locker forks first. Carried flags from
    the 2026-07-31 rev go INTO the round.
17. **Genre verified first** with named evidence; split evidence = ask immediately.
18. **Equipment rides the instrument layer** — amp/cab model, drum sizes, string type carry the
    same research floor as a mic.
19. **Per-unit TRACE line**: base · equip · genre · artist · venue, a value or an explicit
    "no change" per layer.
20. **Dynamics get DOCUMENTED, not patched.** COMP:/GATE: lines in the .md; the patcher does not
    write Mustard into the .ses (Brian's 2026-07-16 call).
21. **Sections get slotted in the NUMBERS.** Four vocals, three cymbal mics, three tom mics — no
    two channels share a value in the lane they're competing for.
22. **Two-mic sources get lane ownership, top AND bottom.** Kick (91A + 52A) and bass (DI + PG52)
    both qualify. No boost on both mics in the same zone.
23. **Pacing rule.** Research lands visibly first; numbers are drafted later, against what was
    found. Never in the same message.
