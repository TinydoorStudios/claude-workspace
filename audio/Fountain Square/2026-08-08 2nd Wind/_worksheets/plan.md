# Plan — 2nd Wind · Fountain Square · 2026-08-08 (Rev 2.0, week 2)

## Genre gate (Step 2a) — verified fresh, not carried

**Genre: R&B / funk / soul show band (Motown + Top 40, jazz inflections) — evidence:**
The Bash artist page (self-described "high energy, jazz and R&B… inspired by Motown, funk and R&B,
also rock and top 40", 200+ song list), GigSalad + CincyMusic listings, and Memorial Hall OTR's
own billing of *The Ultimate Usher Tribute Part II featuring 2nd Wind Band* (2026-06-27, live
vocals + dancers + production). Voted Cincinnati's 2025 Best Performance Band. Backing/opening
credits include Kirk Whalum, The Whispers, Fantasia, John Legend, Charlie Wilson.
**Not split — no genre stop-and-ask.**

## The gig — different from last week, and it matters

| | 2026-07-31 (rev 1) | 2026-08-08 (this build) |
|---|---|---|
| Event | Omega Psi Phi 85th Grand Conclave | **Fifth & Vine Live** (free weekly Saturday series) |
| Window | 18:00–23:00 (6–11 pm) | **19:00–22:00 (7–10 pm)** — myfountainsquare.com |
| Crowd | 10,000+ conclave registrants, destination show | Walk-up downtown Saturday crowd, free, casual |
| Stage | Fifth Third Bank Center Stage | same |

A shorter, tighter three-hour set to a walk-up crowd rather than a five-hour destination event.
Same band, same PA. The practical difference is that there is **no long cool-down tail** — the
whole show sits inside the hottest, driest part of the evening (see below), instead of drifting
into cool and humid the way last week's did.

## Artist profile (fresh pass)

Cincinnati show band, four featured vocalists who front the show and work the crowd. Aretha
(Chapman) also MCs. They back national R&B/gospel acts, which is the tell for how they actually
work: **arrangements are tight and rehearsed, the vocal IS the show, and the rhythm section plays
to a click with tracks underneath** — ch 15 Click + ch 16 Track confirm it again this week.

FOH implications, in order:
1. **Four handheld vocals on an open plaza, all night.** Gain-before-feedback is the governing
   constraint. Cuts-only, and the four voices slotted against each other — not four copies of
   one curve.
2. **No horn channels, again.** Keys L/R + the two sampling pads + Track carry the horn and
   string parts the band's press sells. The keys' 1–2 kHz window stays deliberately untouched so
   those parts survive. (Carried confirm — see round.)
3. **The percussion rig is GONE this week** (no congas, no bongos) and the kit grew instead
   (bottom snare, a dedicated ride mic). Last week's 200–500 Hz mud fight was driven by four hand
   drums on top of a full kit; this week the mud fight moves INSIDE the kit — three tom mics,
   three cymbal mics and a bottom snare all pointed at the same shell.
4. **Bass is now mic + DI** where last week it was DI + synth DI. That is a genuine two-mic
   source, and it is the single biggest change in the low end.
5. Dance show on a plaza with no room gain. Kick and bass get shaped, not turned up.

## Week-over-week diff (this is a revision, not a fresh act)

| Ch | 2026-07-31 | 2026-08-08 | Change |
|---|---|---|---|
| 1 | Kick In · Beta 91A | Kick In · Beta 91A | — |
| 2 | Kick Out · **Audix D6** | Kick Out · **Shure Beta 52A** | mic changed |
| 3 | Snare Top · Audix i5 | Snare Top · Audix i5 | — (i5 was Brian's swap last week) |
| 4 | Snare 2 · **Beta 98H/C** | **Snare Bottom** · **"408"** | name + mic changed → **Q1** |
| 5 | Hat · **ND408** | Hat · **SM81** | mic changed → **Q2** |
| 6 | Rack 1 · D2 | Rack 1 · D2 | — |
| 7 | Rack 2 · **D2** | Rack 2 · **D4** | mic changed |
| 8 | Floor · **D4** | Floor · **D6** | mic changed → **FORK 1** |
| 9/10 | OH pair · Beta 27 | OH pair · Beta 27 | — (still collapses to stereo fader 9) |
| 11 | Bass DI · RNDI | Bass DI · XLR (band's) | source changed → **Q4** |
| 12 | **Bass Synth · J48** | **Bass Mic · PG52** | channel repurposed |
| 13 | Guitar · XLR (cab sim ON) | Guitar · XLR **"Rec Out of Marshall"** | source changed → **Q3** |
| 14 | **Edwin TB · SM58** | **Ride · SM81** ("under mic w claw") | channel repurposed → **Q2** |
| 15 | Click · XLR | Click · XLR | — |
| 16 | Track · XLR | Track · XLR | — |
| 17 | Conga 1 · PRO 35 | **Pad 1 · DI** | dropped / renumbered |
| 18 | Conga 2 · PRO 35 | **Pad 2 · DI** | dropped / renumbered |
| 19 | Bongos · SM57 | **Toys · SM81** | dropped / renumbered → **Q2** |
| 20 | Toys · SM81 | **Key Left · XLR** | renumbered |
| 21 | Pad 1 · AR-133 | **Key Right · XLR** | renumbered |
| 22 | Pad 2 · Whirlwind IMP | — | gone |
| 23/24 | Key L / Key R · XLR | — (moved to 20/21) | renumbered |
| 33 | Aretha · Beta 58A W1 | Aretha · Beta 58A W1 | — |
| 34 | Heather · Beta 58A W2 | Heather · Beta 58A W2 | — |
| 35 | Vince · Beta 58A W3 | Vince · Beta 58A W3 | — |
| 36 | **Markay** · Beta 58A W4 | **Brandon** · Beta 58A W4 | **person changed → Q5** |

Net: 27 channels → **24**. Four percussion/talkback channels out, two kit channels in.

**Every EQ value from rev 1 is re-derived, not copied.** Seven of the twenty units changed mic or
source, the weather inverted, and the percussion rig that shaped last week's whole midrange
strategy is gone. Carrying rev 1's numbers forward would be the wrong build.

## The channel map — reconciled against the FSQ template

The band numbered 1–21 + 4 wireless. Checked against the patcher's own surface-name tripwire
(`apply_show_TEMPLATE_FSQ.py`, template 39,910,700 bytes), the template's native fader names are
`Kick In · Kick Out · Snare Top · Snare Bottom · Hat · Rack 1 · Rack 2 · Floor · Overheads ·
SNARE PL8 · Bass DI · Bass Mic · Guitar 1–4 · Misc 1–8 · Vocal 1–8 · Wireless 1–4`.

**This week's list was written to the house template** — channels 1–12 match the template's own
labels word for word, including "Snare Bottom" on 4 and "Bass Mic" on 12. That is useful
corroboration on Q1 (below): fader 4 really is the bottom head, not a second snare drum.

| Their ch | Console fader | Note |
|---|---|---|
| 1–8 | 1–8 | straight across |
| 9 + 10 (OH L/R) | **9** | STEREO pair on one fader |
| — | **10** | RESERVED — SNARE PL8 reverb return, hard-protected |
| 11–21 | 11–21 | straight across (template renames 14–21 from Guitar 2 / Misc n) |
| Wireless 1–4 | **33 / 34 / 35 / 36** | house wireless faders |

Faders 22–32 unused. No mults — no band input names a wireless unit.

## Room + weather (Step 4) — the big change from last week

Open-Meteo, fetched 2026-08-08 10:57 ET for 39.1012 / −84.5120, show window 19:00–22:00:

| Hour | Temp °F | RH % | Dew pt °F | Precip % | Wind mph | Gusts mph |
|---|---|---|---|---|---|---|
| 17:00 (load-in/check) | 94.4 | 38 | 64.9 | 3 | 10.5 | 16.3 |
| 19:00 (downbeat) | 92.9 | 38 | 63.6 | 6 | 10.5 | 15.9 |
| 20:00 | 90.3 | 43 | 64.8 | 14 | 8.6 | 16.3 |
| 21:00 | 85.7 | 53 | 66.6 | 14 | 7.0 | 15.4 |
| 22:00 (out) | 82.8 | 60 | 67.5 | 10 | 5.3 | 11.4 |

**Read — this INVERTS last week's HF call.** Last week ran 80.6 °F / 50 % RH at doors climbing to
77 % RH by 11 pm, so the note was "don't chase presence with boosts that will be too bright by
10 pm." This week is **hot and genuinely dry through the whole set** — 92.9 °F at 38 % RH at
downbeat, only reaching 60 % as the band loads out. Dry air absorbs high frequencies over
distance far more than humid air does, so the throw to the back of the plaza eats real top end
for the entire show and never gives it back. The move is: **protect presence and do not
over-trim the top.** Where a baked capsule peak would normally get a full trim, it gets a
lighter one — the air is already doing part of that job.

Second-order effects worth carrying:
- **Gusts 15–16 mph across the whole window.** Windscreens on every open mic. The overhead pair,
  the hat, the ride and the toys will all collect wash — another reason the HPFs run high.
- **14 % precip at 20:00–21:00.** Low, but non-zero pop-up risk in 90 °F air. Covers within reach;
  no change to the EQ.
- **94 °F at load-in / soundcheck, dropping 12 °F by load-out.** Drum heads and guitar tuning will
  drift. Nothing to do in EQ, worth one word to the band.
- Dew point sits 63–68 °F all evening — humid *feeling*, but RH is what governs HF absorption and
  RH is low. Don't be fooled by the dew point into last week's humid-air call.

## Mined notes → research questions

- **Ch 4 note "claw"** — a rim-clamp mount. Confirms a mic hung on the drum rather than on a
  stand, which means close working distance and proximity low-mid buildup regardless of which
  "408" it is. It also constrains the mic physically: whatever goes there must clamp.
- **Ch 14 note "Under mic w claw"** — an *under*-ride mic in a claw. That is a deliberate and
  slightly unusual choice: from underneath you get stick definition and bell without the wash
  the top of a ride throws at the overheads, but you also get the shell/hardware and a phase
  relationship with fader 9 that has to be checked. Research item + polarity check at soundcheck.
- **Ch 13 note "Rec Out of Marshall"** — an amp's recording/line out, NOT the modeler feed that
  last week's list carried. Whether it is speaker-emulated changes the entire top end. → **Q3**
- **Ch 11 "Bass DI" as plain "XLR"** vs last week's RNDI — the band is now providing the DI (or
  it is the bass amp's own XLR out). Pre- or post-amp-EQ changes what the DI leg is worth. → **Q4**
- **Ch 12 "Bass Mic" PG52** — this is the job the KB says the PG52 is genuinely good at. Pairs
  with ch 11 as a two-mic source needing explicit lane ownership.
- **Ch 17/18 "Pad 1 / Pad 2" on plain "DI"** — resolved last week: sampling pad, **two mono
  channels panned, not a stereo image**. Carrying that decision forward; no re-ask.
- **Ch 19 "Toys"** — aux percussion tray, the only hand percussion left on the list.
- **Ch 20/21 "Key Left / Key Right"** — stereo keys on XLR line feeds.
- **48V and Stand columns arrived blank** except ch 1. Both get filled from the resolved mic
  list; Split Patch is Brian's load-in call and the snake sheet is blank by design.
- **No Mon Patch / Mix sends filled in** — monitors are the M32's problem at FSQ, not this
  packet's.

## Unit table (24 channels → 20 units)

| # | Unit | Ch | Fork? |
|---|---|---|---|
| 01 | Kick in × Shure Beta 91A | 1 | eligible — silent pass (KB first call, pairs with the 52A) |
| 02 | Kick out × Shure Beta 52A | 2 | eligible — silent pass (KB standard combo) |
| 03 | Snare top × Audix i5 | 3 | eligible — silent pass (Brian's own rev-1 swap; not re-litigated) |
| 04 | Snare bottom × "408" ⚠ identity | 4 | **blocked on Q1** |
| 05 | Hat × Shure SM81 | 5 | **blocked on Q2 (availability)** |
| 06 | Rack 1 × Audix D2 | 6 | eligible — silent pass (DP8 rack-tom mic) |
| 07 | Rack 2 × Audix D4 | 7 | eligible — pass with a note (see below) |
| 08 | Floor tom × Audix D6 | 8 | **FORK 1** |
| 09 | Overheads × Shure Beta 27 pair | 9 (stereo) | eligible — silent pass (shipped rev 1, no objection) |
| 10 | Bass guitar × XLR DI | 11 | **exempt (line feed)** |
| 11 | Bass cab × Shure PG52 | 12 | eligible — silent pass (the PG52's actual best job per KB) |
| 12 | Guitar × XLR line (Marshall) | 13 | **exempt (line feed)** |
| 13 | Ride (under) × Shure SM81 | 14 | **blocked on Q2 (availability)** |
| 14 | Click / Track × XLR line | 15, 16 | **exempt (line feed)** |
| 15 | Sampling pads × DI | 17, 18 | **exempt (DI)** |
| 16 | Toys / aux perc × Shure SM81 | 19 | **blocked on Q2 (availability)** |
| 17 | Keys × XLR line | 20, 21 | **exempt (line feed)** |
| 18 | Female lead vocal × Beta 58A wireless | 33, 34 | exempt (fixed house wireless) |
| 19 | Male bass-range vocal × Beta 58A wireless | 35 | exempt (fixed house wireless) |
| 20 | Male vocal, range TBD × Beta 58A wireless | 36 | exempt — **blocked on Q5** |

**Unit 07 note (no fork raised):** D4 on the lower rack tom instead of a second D2 is a sensible
descending-size progression across the kit (D2 → D4 → D6). It passes, but the mic-library row was
CORRECTED on 2026-07-30 precisely for this case: Audix's own current response chart shows **+6 dB
at 5 kHz** plus a secondary peak above 10 kHz and a rolloff below 70 Hz. So ch 7 gets a TRIM at
5 k, never a click boost, and its weight is restored near 80 Hz rather than expected from the mic.

## Locker forks

### FORK 1 — CH 8 · Floor tom

```
Specified:  Audix D6              Alt: Sennheiser MD 421-U (Silver Tail, standalone — free)
```
1. The D6 is a purpose-voiced *kick* capsule with a **−15 to −17 dB scoop at 600–800 Hz** and
   peaks near 63 Hz and 5 kHz (Audix response chart / KB row corrected 2026-07-30), where the
   421-U is a wide 30 Hz–17 kHz large-diaphragm dynamic with extended lows, real low-mid girth
   and a voiced 4–5 kHz presence — and it is the KB's stated **first choice for toms**.
2. Here that scoop is the whole issue: a floor tom's note lives in the 100–300 Hz fundamental and
   the 400–800 Hz body the D6 deliberately removes, so on the D6 I would be building the drum's
   body back with boosts on a plaza that has no room gain to help, while the 421-U hands it to me
   and lets the FSQ deep cuts do what they're for.
3. The honest cost: the D6 gives more effortless sub thump and near-zero EQ if you want a modern
   scooped floor tom, the 421-U is bigger and fussier to place on a crowded riser and blooms
   200–400 Hz if it ends up close, and if the band's sound is deliberately that scooped
   dance-floor floor tom then the D6 is the right call and the fork should be declined.

```
Call: keep D6  ·  swap to MD 421-U
```

No second fork is raised on the kit. Ch 6, 7 and 9 all pass, and the D4/D2/D6 progression is
internally coherent — spending a fork on each would be re-plumbing Brian's kit, not advising it.

## Questions for the round (blocking)

**Q1 — Which "408" is on ch 4, and is fader 4 the bottom head?**
The CLAUDE.md mic table says a "408" written on a *snare* is the **Lauten LS-408**, not the EV
N/D 408. But the KB article for the LS-408 says `Status: Reference — not in locker` — Brian
doesn't own it — and the EV N/D 408 *is* owned and is listed in mic-library for "rack toms, guitar
cab and **snare**." Corroborating: ch 4's 48V arrived **blank**, and the LS-408 is a condenser
that requires phantom while the ND408 is a dynamic that must not have it. This is a mic identity
AND a phantom-power decision, so it cannot be assumed. My read: **EV N/D 408**, same as the
answer on last week's hat. If it IS the LS-408, its onboard HPF (80/140) and LPF (5/12 k) switch
positions have to be stated too, because they do most of the shaping before the desk sees it.
Secondary: the template's own fader 4 is literally named "Snare Bottom" and the note says "claw",
so I am treating it as the bottom head — polarity INVERT vs ch 3, wire-rattle band, no body
boost. Last week's rev-1 flag on this same channel ("Snare 2 read as a second drum, not a bottom
head") is hereby closed unless Brian says otherwise.

**Q2 — Three SM81s are called for and the locker holds one.**
Hat (ch 5), Ride (ch 14) and Toys (ch 19) all say SM81. `mic-library.md` lists a single SM81 with
no pair/quantity marker, and the file marks multiples explicitly everywhere else (MKH 40 (pair),
OM1 (pair), DPA 4099 (×4)), so the evidence says one. Either Brian has more than the KB knows
about, or two of these three need reassigning. My proposed allocation if it's one:
- **Ride (ch 14) keeps the SM81** — the under-ride position is the one that most needs a flat,
  honest capsule with a switchable onboard HPF, and it's a stand/claw mount the SM81 suits.
- **Hat (ch 5) → Audix M1280BHC** (DP8) — the purpose-built ultra-compact hat condenser, clamps
  in the space a hat mic actually has, and frees the SM81.
- **Toys (ch 19) → one Audix M1280B** (DP8 matched pair, one leg) or an sE8 (V Pack Arena) —
  both compact condensers that take the template straight.

**Q3 — Ch 13: is the Marshall's "Rec Out" speaker-emulated, and which amp is it?**
On a DSL/JVM/Origin the emulated line out is speaker-compensated and behaves like a mic'd cab —
which is what last week's build assumed ("cab sim ON"), and it's why the +3 @ 3 k was withdrawn.
A raw preamp/line-out or an FX-loop send is **not** compensated and arrives with real fizz above
4 kHz and no cab rolloff, which needs an aggressive LPF and a different midrange plan entirely.
Same jack name, opposite treatment. Which amp, and does the out say "emulated"?

**Q4 — Ch 11: whose DI is the bass XLR, and is it pre- or post-amp-EQ?**
Last week this was Brian's RNDI. This week it's a plain "XLR" — the band's own box, or the bass
amp's XLR out. If it's the amp's out and post-EQ, the DI leg already carries the player's tone
shaping and I should not shape it a second time; if it's a clean pre-EQ DI or their own box, the
DI leg is mine to build. Either way ch 11 + ch 12 (PG52) are a two-mic source: **DI owns
definition and the top, the PG52 owns the low body** — the PG52's published curve humps 60–100 Hz
and dips through 200–800 Hz, so I let the hump through rather than boosting it and I do not cut
into that dip. Polarity check the pair in mono at soundcheck.

**Q5 — Wireless 4 is now Brandon, not Markay. What's his range?**
Vocals get slotted by voice type, not hierarchy, and I have no public information on Brandon.
Rev 1 built W4 for a male upper-range voice (HPF 110, upper-mid cut 1200). If Brandon is another
bass-baritone like Vince, that HPF is wrong for him the same way the template's 184 was wrong for
Vince. Baritone / tenor / high tenor — or "sounds like Vince" / "sounds like Markay" is enough.

**Q6 — carried flags from rev 1, renew or close (one line each, none block the EQ):**
- Click (ch 15) is out of the mains and out of the record bus — still assumed.
- Track (ch 16) is mono — still assumed.
- The house wireless handhelds are Beta 58A capsules — still assumed.
- No horn channels: keys + pads + Track carry the horn/string parts, which is why the keys'
  1–2 kHz window is left untouched — still assumed.
- Four KB write-backs staged on 2026-07-31 and never actioned: (1) SM57 presence peak 3–5 k →
  Shure's measured 6–7 k / +5–6 dB; (2) D6 scoop refined to 700–800 Hz at −17 dB plus the baked
  peak above 1 kHz; (3) a rim-mount placement note on the Beta 98H/C row; (4) new
  eq-starting-points rows for synth bass, modeller/direct guitar feed, sampling pad and backing
  track. Say the word and they go in as staged write-backs.

## Carried flags — status

Every rev-1 ASSUMED flag is either closed by this week's list (bass simultaneity — now
unambiguous; ch 4 identity — now named "Snare Bottom") or re-raised above in Q6. None are being
shipped silently for a second rev.
