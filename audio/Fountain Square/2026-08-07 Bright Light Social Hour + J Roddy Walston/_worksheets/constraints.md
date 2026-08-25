# Constraint card — FSQ 2026-08-07, written from SKILL.md before any research

Written in my own words after reading show-deep-build in full this session.

1. **Whole dB only.** No half-dB anywhere, ever. Round up.
2. **Cuts before boosts.** Find and remove the problem first; a boost is the exception that
   has to earn itself.
3. **Vocals are cuts-only, every genre.** Not taste — feedback control. Any positive gain on a
   VOCALS-section channel is a build error unless Brian explicitly approved it.
4. **No high-shelf band unless Brian asks.** Top-end lift, when justified, is a wide bell.
5. **Band order/numbering is the console's:** HPF → LPF → Band 4 (HF) → Band 3 → Band 2 →
   Band 1 (LF). B1 = LOW. Never inverted.
6. **Ribbon = NO 48V, in red.** No ribbons on this show, but the rule stands if one appears.
7. **TOUR gear is never swapped and never locker-forked.** Flag amber, confirm at load-in.
8. **Cut/boost ranges:** cuts −4 to −7 tight Q indoors; **FSQ outdoor override −6 to −9, up to
   −10 on mud/box.** Boosts +3 to +6 on non-vocal sources. Torn between two depths outdoors →
   take the deeper one.
9. **FSQ template map:** fader 9 "Overheads" is a **STEREO** channel — both OH mics on that one
   fader. Fader 10 "SNARE PL8" is the snare plate reverb **return, not an input** — hard error.
   House wireless 1–4 = **faders 33–36** (Shure Beta 58A).
10. **Research floor.** KB is the archive, not the research. Every unique instrument × mic unit
    gets a fresh web pass with at least one **quantitative capsule fact + named external
    source**. No "familiar mic" exemption. No cross-show cache.
11. **Capsule gate.** Before writing any boost, state what the capsule already bakes in there.
    Boost inside a baked peak = trim or nothing. Also in reverse: don't deep-cut a scoop the
    capsule already made. Extends to finished-audio sources (cab sims, sampling pads).
12. **Reverbs are required** — Seventh Heaven Pro, preset names verbatim from the reverb KB,
    3 complementary vocal + 1–2 instrument + 1 general, every value anchored to the factory
    setting ("(factory)" / "(from X factory)"), plus a pairing paragraph. FSQ included.
13. **One batched question round** before any EQ commits. Locker forks head it. Genre gate is
    the single exception — split evidence asks immediately.
14. **Genre verified first**, with named evidence, before any downstream research runs.
15. **Equipment rides the instrument layer** — amp/cab, piano type, drum sizes, pickups get the
    mic-grade research floor and must be cited wherever they bend a value.
16. **Per-unit TRACE line** closes every research entry: base · equip · genre · artist · venue,
    each carrying a value or an explicit "no change".
17. **Pacing:** research lands visibly first; numbers get drafted in a later step against it.

Show-specific additions I am binding myself to:

- **Two bands, one console, one night.** Shared kit channels get researched once but bent twice
  — psych-rock and piano-rock ask for different things from the same snare.
- **Humidity rule** ([[humidity-inverts-outdoor-hf]]): the fetched RH decides the top-end call,
  not the season. This show sits at 82–94% RH across the sets — that is the no-HF-boost end of
  the scale, so baked presence peaks get trimmed rather than reinforced.
- **Gust rule:** overheads' HPF tracks the gusts. 17–19 mph at showtime.

Re-read points required by the skill: (a) immediately before the question round, (b) immediately
before writing each spec.json. Both logged in this file when done.

- [x] Re-read before question round — 2026-08-06
- [x] Re-read before writing Bright Light Social Hour.spec.json — 2026-08-06
- [x] Re-read before writing J Roddy Walston.spec.json — 2026-08-06
