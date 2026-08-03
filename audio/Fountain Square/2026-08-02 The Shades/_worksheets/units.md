# Unit worksheets — FSQ 2026-08-02 (shared backline, both shows)

Serialized: each unit completed Steps 1–5 before the next started. Draft bands here are what
spec.json was assembled from — nothing was written from memory.

---

## Unit 01 — Kick in × Shure Beta 91A

INSTRUMENT   Kick drum, inside on the head. Soul/jazz kick: felt beater, round weight, low click.
MIC          Beta 91A half-cardioid boundary condenser. Two-mic pair with the D6 (unit 02).
             Switch state: contour assumed **FLAT** — the 400 Hz cut lives on the desk.
SEARCHES     "Shure Beta 91A kick drum frequency response contour switch 400Hz boundary live";
             site-scoped follow to Shure/Thomann/Mix.
CAPSULE FACT Two-step contour switch centred at 400 Hz attenuating **≈ −7 dB** (Thomann /
             Shure spec, via Mix Online review). Boundary design; pronounced beater click.
WEB SAYS     Flat setting for natural, "low-mid scoop" setting for punch plus attack. Boundary
             mount = no stand, sits on the pillow.
KB SAYS      mic-library: "solid boundary low end + pronounced beater click; nominally flat
             (contour cuts 7 dB @ 400 if engaged). Weakness: picks up shell boxiness 300–500."
VERDICT      **AGREE** — the web's 400 Hz/−7 dB figure and the KB's 300–500 boxiness are the same
             fact from two directions.
LOCKER       First call for the kick attack layer. Silent pass.
GENRE BEND   Neo-soul / smooth jazz kick wants weight and a soft beater, not a metal click. The
             capsule's pronounced click gets trimmed rather than left alone.
VENUE BEND   FSQ: box cut taken to the full outdoor −8 (mechanical box, not room mud).
DRAFT BANDS  HPF 60 · LPF 8000 · B4 −3 @ 5000 Q2 · B3 −8 @ 400 Q2 · B2 −6 @ 250 Q1.8 · B1 FLAT
GATE CHECK   **No boosts on this channel** — nothing to gate. Two-mic lane: the 91A owns the
             ATTACK and mid-definition lane top-to-bottom; the D6 owns the LOW/body lane. That is
             why the 91A is high-passed at 60 with B1 flat — it deliberately vacates the bottom
             so it cannot stack on the D6's baked +14 dB at 60 Hz.
QUESTIONS    none

---

## Unit 02 — Kick out × Audix D6

INSTRUMENT   Kick drum, outside / port side. The weight-and-body half of the pair.
MIC          Audix D6, cardioid dynamic. Heavily pre-voiced.
SEARCHES     "Audix D6 kick drum frequency response scoop 600Hz peak 63Hz 5kHz specs"; Audix
             spec sheet + RecordingHacks curve read.
CAPSULE FACT **+14 dB at 60 Hz, −15 dB scoop at 700–750 Hz, +15 dB at 4–5 kHz, +17 dB at
             10–12 kHz** (Audix AX-D6 spec sheet / RecordingHacks; 30 Hz–15 kHz).
WEB SAYS     "Scooped-mids" curve, 90 Hz–600 Hz attenuated to kill boominess. Designed to need
             almost no EQ for a modern kick.
KB SAYS      mic-library: "pre-scooped smiley voicing: peaks ~63 Hz and ~5 kHz, deep mid scoop
             ~600 Hz (−15 dB). Thump+click baked in. Weakness: one-trick, no midrange body."
VERDICT      **AGREE** — web puts the dip at 700–750 where the KB says ~600; same feature, and
             the web number is the more precise one. Logged as a KB write-back candidate.
LOCKER       Brian's own call this round (D6 to kick out, Beta 52A freed for the floor). Closed.
GENRE BEND   This is the big one. The D6's +15 @ 4–5 k and +17 @ 10–12 k are a *rock* kick
             voicing. A soul kick doesn't want either. Both get pulled — the 10–12 k peak by the
             LPF, the 4–5 k peak by a band.
VENUE BEND   FSQ: no room gain, so the low end is allowed through untouched rather than trimmed.
DRAFT BANDS  HPF 35 · LPF 7000 · B4 −5 @ 4500 Q2 · B3 −4 @ 1200 Q2 · B2 FLAT · B1 FLAT
GATE CHECK   **No boosts.** Three gate decisions, all in reverse: B1 stays flat because +14 dB
             at 60 is already baked; B2 stays flat because 90–600 Hz is already attenuated;
             and B3 sits at 1200 rather than the obvious 700 **because the capsule already cut
             −15 dB there** — cutting into a baked scoop is the failure this gate exists for.
QUESTIONS    none

---

## Unit 03 — Snare top × Audix i5

INSTRUMENT   Snare top. Neo-soul backbeat: ghost notes, cross-stick, rimshots on the chorus.
MIC          Audix i5, cardioid dynamic. **Swapped in from the specified e604** — see LOCKER.
SEARCHES     "Audix i5 snare frequency response 5.5kHz presence peak 150Hz live sound";
             "Sennheiser e604 rack tom frequency response presence peak live sound EQ".
CAPSULE FACT i5: **+5 dB at 150 Hz and +9 dB at 5500 Hz**, −3 dB points at 50 Hz / 16 kHz,
             sensitivity 1.6 mV/Pa (RecordingHacks / Sound On Sound review).
WEB SAYS     That low 1.6 mV/Pa sensitivity is specifically credited with keeping hi-hat spill
             off the snare channel — relevant here, because the hat mic is under the hats.
             On the e604: forum consensus is it's "a little thin [on rack toms] and needs a
             pretty good boost in the lows", optimised for snare more than toms (Gearspace,
             HomeRecording).
KB SAYS      i5 — "body lift ~+5 dB @150 Hz, presence ~+9 dB @5.5 kHz… that 5.5 k peak can get
             harsh on a cracky snare"; listed as the snare primary (DP8).
             e604 — "scooped low-mids, voiced attack… thinner/boxier than a D-series."
VERDICT      **AGREE** on both mics.
LOCKER       **FORK — decided by me at Brian's instruction.** Specified e604, alternative i5.
             Chose the **i5**, three reasons: (1) the i5's +5 dB at 150 Hz is exactly the body a
             soul snare lives on, while the e604's documented weakness is being thin and boxy —
             outdoors with no room gain, a thin snare simply disappears; (2) the i5's one
             liability, the +9 dB at 5.5 kHz, is a liability I'd be *trimming* anyway on a 90% RH
             night, so the trade costs nothing tonight; (3) the honest cost is a stand where the
             e604 clips to the rim, in a night with a two-act changeover — plus the i5's low
             sensitivity actually reduces hat spill, which the under-mounted hat mic makes worse.
             Knock-on: only two e604s now needed (racks), so the three-in-the-case question dies.
GENRE BEND   Soul snare = fat and round, not crack. The 5.5 k peak is trimmed, not exploited.
ARTIST BEND  Both acts are groove bands where ghost notes carry the feel — any gate must be
             shallow enough that ghosts and press rolls live. Documented, not patched.
VENUE BEND   FSQ: box cut to −7. HPF held at 120 rather than the usual 180 so the capsule's
             150 Hz body lift survives — the outdoor rule doesn't get to eat the body.
DRAFT BANDS  HPF 120 · LPF 14000 · B4 −4 @ 5500 Q2 · B3 −3 @ 1000 Q2 · B2 −7 @ 450 Q2 · B1 FLAT
GATE CHECK   **No boosts.** B1 stays flat specifically because +5 dB at 150 Hz is baked — the
             body is bought with the HPF corner, not with a band.
QUESTIONS    none

---

## Unit 04 — Hat × Shure SM81

INSTRUMENT   Hi-hat, mic **under** the hats (from the input list note).
MIC          Shure SM81 cardioid SDC, switchable HPF (6 / 18 dB per octave), −10 dB pad.
SEARCHES     "Shure SM81 hi-hat live sound HPF frequency response flat SDC EQ outdoor".
CAPSULE FACT **Flat 20 Hz–20 kHz** with a switchable LF filter at 6 or 18 dB/oct and a −10 dB
             pad (Shure spec / B&H / soundref). Nothing voiced in.
WEB SAYS     Industry standard for hats; the flat response is what makes it EQ well in any
             direction. Robust outdoors, foam windscreen handles light wind.
KB SAYS      "Ruler-flat SDC, clean detailed highs with no harsh fizz… takes EQ well. Weakness:
             needs care on cymbal wash." Bias: apply the template as-is.
VERDICT      **AGREE** — a flat mic is the one case where web and KB can't disagree.
LOCKER       First call for hat. Silent pass.
GENRE BEND   The genre default here would be an 8–10 kHz shimmer lift. **Inverted** — see venue.
VENUE BEND   FSQ at 87–94% RH: saturated air passes HF essentially intact to the back of the
             plaza, so the shimmer lift becomes a **−3 cut at 9 kHz**. Box cut takes full outdoor
             depth at −7 because an under-mounted hat mic sees more snare shell from below.
DRAFT BANDS  HPF 400 · LPF 16000 · B4 −3 @ 9000 Q2 · B3 −6 @ 1000 Q2 · B2 −7 @ 500 Q2 · B1 FLAT
GATE CHECK   **No boosts** — and on a flat capsule there'd be nothing to stack on anyway. The
             absence of the usual air lift is the humidity call made visible.
QUESTIONS    none

---

## Unit 05 — Rack toms × Sennheiser e604 (CH 6, 7)

INSTRUMENT   Two rack toms, fills and comping. Soul playing: round, musical, not smashed.
MIC          Sennheiser e604 clip-on cardioid dynamic, rim mount.
SEARCHES     "Sennheiser e604 rack tom frequency response presence peak live sound EQ";
             Gearspace + HomeRecording tom threads.
CAPSULE FACT **40 Hz–18 kHz, 160 dB max SPL**, lightweight voice coil for fast transients
             (Sennheiser spec sheet). Forum-measured behaviour: thin on rack toms, wants a low
             boost; presence sits in the **upper midrange**, not the extreme top.
WEB SAYS     "A little thin and needs a pretty good boost in the lows"; "sometimes lacks attack
             or upper midrange." Optimised for snare more than toms.
KB SAYS      "Tom/snare clip dynamic, scooped low-mids, voiced attack. Weakness: thinner/boxier
             than a D-series, modest low end."
VERDICT      **AGREE** — both call it thin in the low-mids. That agreement is what licenses the
             only low boost in the drum section.
LOCKER       Toms clip-on is a documented first call and the racks are a marginal case at worst;
             tie goes to the specified mic. Silent pass.
GENRE BEND   Soul toms want body and pitch, not attack. The voiced attack gets trimmed.
VENUE BEND   FSQ: box cut −6 on both.
DRAFT BANDS  Rack 1 — HPF 90 · LPF 12000 · B4 −3 @ 6000 Q2 · B3 −4 @ 700 Q2 · B2 −6 @ 350 Q2 ·
             **B1 +4 @ 180 Q1.2**
             Rack 2 — HPF 80 · LPF 12000 · B4 −3 @ 5500 Q2 · B3 −4 @ 600 Q2 · B2 −6 @ 320 Q2 ·
             **B1 +4 @ 150 Q1.2**
GATE CHECK   The +4 dB low boost is the gate's positive case: the e604's low-mids are
             **documented as scooped** by both the KB and the forums, so this fills a hole the
             capsule cut rather than stacking on a peak. Rack 1 at 180 and Rack 2 at 150 keep
             the two toms off each other's fundamental.
QUESTIONS    none

---

## Unit 06 — Floor tom × Shure Beta 52A

INSTRUMENT   Floor tom. The deep punctuation in both bands' grooves.
MIC          Shure Beta 52A supercardioid dynamic — a kick mic, deliberately on the floor tom
             (Brian's call this round, which freed the D6 for kick out).
SEARCHES     "Shure Beta 52A floor tom mic live sound forum EQ low mid"; DFO + TalkBass +
             Gearspace threads.
CAPSULE FACT Tailored kick voicing: **presence lift ~4 kHz, scooped low-mids, big lows**
             (Shure spec via Thomann/FrontEndAudio; KB concurs). Forum: "heavily scooped voicing
             baked in", "a very EQ'd and scooped tone with a huge low end up close."
WEB SAYS     DFO consensus: "an absolute monster on floor toms" once the kick mic is something
             else — exactly the configuration Brian chose. Caveat repeated across threads:
             "sounds great soloed but may get lost in a dense mix."
KB SAYS      "Tailored kick dynamic, scooped low-mids, presence lift ~4 kHz, big lows.
             Click+thump voiced in." Bias: ease off attack, box, mud.
VERDICT      **AGREE.**
LOCKER       Brian directed the placement this round. Closed, not re-litigated.
GENRE BEND   Soul floor tom = deep and round. The 4 kHz presence lift is a kick-attack feature
             that a floor tom doesn't want; trimmed.
VENUE BEND   **FSQ depth deliberately NOT taken.** B3 sits at −3 and B2 at −5, short of the
             outdoor −7/−8, and the reason is the capsule not the genre: the mic already scooped
             its own low-mids, and the forums' one warning about it is that it gets lost in a
             dense mix. Stacking the outdoor rule on a baked scoop is how that happens.
DRAFT BANDS  HPF 50 · LPF 10000 · B4 −4 @ 4000 Q2 · B3 −3 @ 800 Q2 · B2 −5 @ 250 Q2 · B1 FLAT
GATE CHECK   **No boosts.** B1 flat because the big lows are baked; B3/B2 held shallow because
             the low-mid scoop is baked. Both directions of the gate on one channel.
QUESTIONS    none

---

## Unit 07 — Overheads × Shure Beta 27 pair (STEREO on fader 9)

INSTRUMENT   Drum overheads, stereo pair — cymbals plus the kit's glue.
MIC          Shure Beta 27 supercardioid LDC ×2, −15 dB pad available.
SEARCHES     "Shure Beta 27 drum overheads supercardioid frequency response 5.5kHz 9kHz peak
             review"; Shure spec sheet + RecordingHacks polar data.
CAPSULE FACT **Nominally flat ~60 Hz–3 kHz with two small HF peaks of +2 dB or less at 5500 Hz
             and 9000 Hz**; HF −3 dB point above 15 kHz (RecordingHacks measurement / Shure
             Beta27 spec sheet). Pattern consistent below 6400 Hz, narrowing above.
WEB SAYS     The −15 dB pad and SPL handling are what make it an overhead choice; bleed into it
             stays relatively flat and therefore blends rather than fighting.
KB SAYS      "Supercardioid LDC, flat 60 Hz–3 kHz, small peaks +2 dB at 5.5 k and 9 k, −15 dB
             pad, flatter than SM57. Weakness: slight 9 k fizz on bright amps."
VERDICT      **AGREE** — identical numbers from both sides.
LOCKER       Precedent choice (Repertoire ran the same pair) and the alternatives are marginal.
             Silent pass.
GENRE BEND   No cymbal-air lift — see venue. Overheads carry the kit's body in a soul mix, so
             the pair is not treated as a cymbal-only channel.
VENUE BEND   **Wind 1–4 mph gusting 9** → HPF **300**, not the 400 a gusty night earns.
             **RH 87–94%** → both baked peaks trimmed rather than left, because saturated air
             delivers them intact to the back. Box/bleed cut takes full outdoor depth at −7.
DRAFT BANDS  HPF 300 · LPF 16000 · B4 −3 @ 9000 Q2 · B3 −3 @ 5500 Q2 · B2 −7 @ 400 Q2 · B1 FLAT
GATE CHECK   **No boosts.** B4 and B3 land exactly on the two measured capsule peaks — the trim
             case, not the boost case.
QUESTIONS    none. Fader 9 is stereo; fader 10 is the SNARE PL8 return and stays untouched.

---

## Unit 08 — Bass DI × Whirlwind IMP (CH 11)

INSTRUMENT   Electric bass, direct. Both acts: the bass is the pocket, fingerstyle, round.
MIC          Whirlwind IMP passive DI. **DI — locker fork exempt.** No capsule.
SEARCHES     "bass DI and cab mic blend live sound phase lane split low end which mic owns";
             TalkBass + Sound On Sound + tapetownstudio phase articles.
CAPSULE FACT No capsule to characterise — the researched fact here is the **blend rule**:
             "below 100 Hz a DI works best… tone is defined above 100 Hz where a mic captures
             the amp and speakers. If you use the DI only below 100 Hz and the mic only above
             100 Hz there is no phase problem" (TalkBass consensus, corroborated by SOS
             "Matching The Phase Of Mic & DI Signals"). **The DI owns the low end.**
WEB SAYS     Blending an un-aligned DI and cab mic gives a thin, hollow, phasey result because
             the mic signal is delayed by the air path. Many DIs want polarity reversed.
KB SAYS      "Passive DI, neutral/honest, reliable… passive = slight HF/level loss into low-Z,
             no active sparkle." Bias: apply template as-is.
VERDICT      **THIN** — the KB has a DI row but no bass DI + cab *blend* entry at all. The lane
             split is carried entirely by the web pass. Logged as a KB write-back candidate.
LOCKER       Exempt (DI).
GENRE BEND   Neo-soul/smooth jazz bass wants weight and roundness, not grind. Nothing added on
             top; the DI's job is the bottom octave.
VENUE BEND   FSQ: no room gain, so the sub lane is supported rather than trimmed.
DRAFT BANDS  HPF 30 · LPF 8000 · B4 FLAT · B3 −4 @ 1200 Q2 · B2 −5 @ 400 Q2 · **B1 +3 @ 60 Q1.2**
GATE CHECK   The +3 at 60 Hz passes because there is **no capsule and no baked curve** to stack
             on — a passive DI is flat by definition — and because the paired cab mic is
             high-passed at 100 Hz and left flat at B1, so nothing else is boosting there.
             **Two-mic lane, bottom:** DI owns everything below 100 Hz.
             **Two-mic lane, top:** the cab mic owns tone above 100 Hz — which is why this
             channel is low-passed at 8 kHz and cut at 400 and 1200, deliberately vacating the
             midrange rather than competing in it.
QUESTIONS    none. Mono-sum both bass channels at soundcheck and flip the cab's polarity if the
             sum is thinner than either alone.

---

## Unit 09 — Bass cab × Shure PG52 (CH 12)

INSTRUMENT   Bass cabinet, close-miked. The tone half of the bass pair.
MIC          Shure PG52 cardioid dynamic (discontinued). Brian's documented bass-cab mic.
SEARCHES     "Shure PG52 bass cabinet mic live sound forum frequency response curve 60-100Hz
             hump"; Shure PG52 spec sheet + TalkBass bass-amp thread + RecordingHacks.
CAPSULE FACT **30 Hz–13 kHz**, cartridge tailored for kick and close-miked bass amps (Shure
             PG52 spec sheet). Published curve: hump at 60–100 Hz, broad dip through
             200–800 Hz, rise at 4–5 kHz, hard roll-off above 10 kHz.
WEB SAYS     TalkBass reports fantastic results on a bass cabinet specifically; sold as a kick
             mic but rated well above its price on cabs, because that exact curve is the right
             shape for one.
KB SAYS      Same curve, plus explicit working rules: "never boost the 60–100 Hz hump… never cut
             into the 200–800 Hz dip (sit a box cut at ~160 Hz instead); ease off presence
             ~4500 Hz."
VERDICT      **AGREE** — and the KB's three rules are the operational form of the web's curve.
LOCKER       Documented first call for a bass cabinet. Silent pass.
GENRE BEND   Round, warm bass tone; the 4–5 kHz rise is string/fret noise here, not definition.
VENUE BEND   FSQ: the box cut takes −5 at the KB's prescribed 160 Hz rather than a deeper cut
             further up, because further up is inside the capsule's own dip.
DRAFT BANDS  **HPF 100** · LPF 9000 · B4 −4 @ 4500 Q2 · B3 −3 @ 1500 Q2 · B2 −5 @ 160 Q2 ·
             B1 FLAT
GATE CHECK   **No boosts.** Three gate calls: B1 flat and HPF at 100 because the 60–100 Hz hump
             is baked *and* because the DI owns that lane; B2 at 160 rather than 300–400
             because 200–800 is a baked dip; B4 at 4500 trims the documented presence rise.
             **Two-mic lane, top:** this mic owns tone above 100 Hz. **Bottom:** it owns none —
             the HPF is the lane boundary, drawn at the exact frequency the research named.
QUESTIONS    none

---

## Unit 10 — Guitar cab × Sennheiser e609 Silver (CH 13)

INSTRUMENT   One electric guitar, cab-miked. Neo-soul comping: clean-to-edge-of-breakup chords,
             chord-melody fills. The only guitar in either band, so it carries real weight.
MIC          Sennheiser e609 Silver, supercardioid dynamic, flat-face, hangs over the cab.
SEARCHES     "Sennheiser e609 silver guitar cab frequency response 4kHz presence peak live EQ";
             "neo-soul R&B live sound mixing FOH EQ vocals Rhodes keys warmth low mids".
CAPSULE FACT **40 Hz–15 kHz supercardioid with a presence peak at ~4 kHz and a broader midrange
             peak across 3–6 kHz** (Sennheiser e609 Silver product specification /
             homestudiobasics comparison).
WEB SAYS     The presence boost is deliberately there to help guitar cut through a mix. Separate
             neo-soul mixing source: cut guitar **2.5–3 kHz by 1–2 dB** specifically to stop it
             overlapping the vocal.
KB SAYS      "Flat-face cab dynamic, bright upper-mid/presence ~4–5 kHz, supercardioid.
             Weakness: can be edgy ~2.5–4 kHz on bright amps." Bias: ease off presence.
VERDICT      **AGREE** — the KB's "edgy 2.5–4 kHz" and the genre source's "cut 2.5–3 kHz to
             clear the vocal" are the same move arrived at independently.
LOCKER       Documented first call for a guitar cab. Silent pass.
GENRE BEND   The vocal-clearing cut at 2.8 kHz comes straight from the neo-soul source, taken
             deeper than its 1–2 dB because outdoors there's no room to blur the overlap.
             Held to −3 rather than −5 because this is a lone guitar carrying the harmony.
VENUE BEND   FSQ: cab box/mud takes the **full outdoor −7**. This is mechanical mud — a wooden
             cab in a plaza — which is exactly where the memory says to spend the depth.
DRAFT BANDS  HPF 90 · LPF 12000 · B4 −4 @ 4000 Q2 · B3 −3 @ 2800 Q2 · B2 −7 @ 300 Q2 · B1 FLAT
GATE CHECK   **No boosts.** B4 lands on the measured 4 kHz presence peak (trim, not lift) and
             B3 sits inside the 3–6 kHz midrange peak — both are trims of baked features.
QUESTIONS    none

---

## Unit 11 — Keys × Whirlwind IMP (CH 17, 18)

INSTRUMENT   Two keyboard channels. Neo-soul and smooth jazz both centre on electric piano —
             Rhodes and Wurlitzer are the genre's signature instruments.
MIC          Whirlwind IMP passive DI ×2. **DI — locker fork exempt.**
SEARCHES     "neo-soul R&B live sound mixing FOH EQ vocals Rhodes keys warmth low mids".
CAPSULE FACT No capsule. Researched fact carrying the channel: neo-soul staging guidance is
             **"reduce 8–10 kHz by 3–5 dB to combat stage reverb; boost 500 Hz by 2 dB for
             proximity warmth"** — i.e. the genre explicitly treats low-mid warmth as a feature
             and the top end as the thing to pull back.
WEB SAYS     Rhodes and Wurlitzer deliver the genre's "mellow, foundational" harmonic bed;
             production prizes analog warmth and organic texture over brightness.
KB SAYS      IMP: "passive DI, neutral/honest… no active sparkle." No KB row exists for a
             keyboard or line-level board at all.
VERDICT      **THIN** — the same KB gap logged on the 2026-07-27 and 2026-08-01 builds. Values
             stay conservative and the reasoning leans on the genre source. Write-back candidate.
GENRE BEND   The 8–10 kHz pull-back from the source, and warmth protected at 300 Hz.
VENUE BEND   **FSQ depth deliberately held at −5**, not −8. The outdoor rule fights mud; a
             Rhodes' 300 Hz is the instrument's warmth, and a plaza has no room buildup to add
             to it. Same trade as the Repertoire build, stated on paper so it's auditable.
DRAFT BANDS  Both channels — HPF 45 · LPF 15000 · B4 −3 @ 8000 Q2 · B3 −4 @ 2000 Q2 ·
             B2 −5 @ 300 Q1.8 · B1 FLAT
GATE CHECK   **No boosts.** The B4 cut at 8 kHz is the genre source's own instruction and is
             reinforced by the humidity call, so it survives twice over.
QUESTIONS    Treated as a **stereo pair** — identical curves, because different EQ on a stereo
             keyboard rig shifts the image. If Keys 1 and Keys 2 turn out to be two separate
             players on two separate boards, CH 18 can take its own curve; flagged in notes.

---

## Unit 12 — Sax × Audio-Technica PRO 35 (CH 19, The Shades only)

INSTRUMENT   Saxophone — Elijah Woodward, per the Spectrum News feature. Horn line in a
             neo-soul band: hooks, pads behind vocals, solo features.
MIC          Audio-Technica PRO 35 clip-on cardioid condenser on the bell.
             **Brian's fork decision** — he took neither the specified N/D 408 nor my 98H/C.
SEARCHES     "Audio-Technica PRO 35 saxophone clip-on live sound frequency response presence
             lift EQ"; "smooth jazz live sound mixing saxophone FOH EQ alto soprano sax outdoor".
CAPSULE FACT **50 Hz–15 kHz with a built-in low-frequency roll-off at 80 Hz, 18 dB per octave**,
             145 dB max SPL, "subtly rounded treble" (Audio-Technica PRO35 product spec /
             Thomann). Instrument fact: **alto sax fundamentals sit 150–700 Hz with presence
             2–4 kHz.**
WEB SAYS     Reliable for live trumpet/trombone/sax precisely because of the rounded treble and
             high SPL headroom. Sax live-mix guidance: high-pass for stage rumble, control the
             honk in the low mids, treat 2–4 kHz as the presence region.
KB SAYS      "Clip-on cardioid condenser, 50 Hz–15 kHz (limited top), voiced presence lift,
             clamp mount. Weakness: rolled-off extreme top, thin lows, plasticky upper-mid if
             close." Bias: ease off presence.
VERDICT      **AGREE.**
LOCKER       Fork closed by Brian. No further alternative raised.
GENRE BEND   Neo-soul horn sits *inside* the arrangement, not on top of it — the honk cut at
             2500 does the work and no air is added.
VENUE BEND   FSQ: bell-proximity box cut at −6. HPF at 120 sits **above** the capsule's own
             80 Hz roll-off so the two aren't duplicating each other — the desk filter is there
             for key noise and stage rumble a bell clip picks up, not to re-cut what's cut.
DRAFT BANDS  HPF 120 · LPF 14000 · B4 −3 @ 6000 Q2 · B3 −5 @ 2500 Q2 · B2 −6 @ 400 Q2 · B1 FLAT
GATE CHECK   **No boosts.** The rounded treble plus 87–94% RH means an air lift would be wrong
             twice; B4 instead trims the "plasticky upper-mid" the KB warns about on a close clip.
QUESTIONS    none. A bell clip hears the bell, not the whole horn — expect it brighter and
             thinner than a stand mic and don't chase that with EQ; it's the mounting position.

---

## Unit 13 — Sax × artist's own mic → FX pedal → XLR (CH 19, Ric Sexton only)

INSTRUMENT   Ric Sexton's saxophone. **He swaps alto and soprano on this one channel** (Brian).
             He's the leader — this channel is the show.
MIC          His own mic, into his own FX pedal, out via XLR at line level.
             **⚑ TOUR — never swapped. XLR line feed — locker fork exempt.** Model unknown.
SEARCHES     "smooth jazz live sound mixing saxophone FOH EQ alto soprano sax outdoor";
             Sax on the Web live-EQ threads.
CAPSULE FACT No capsule of ours to characterise — so the researched facts are the instruments:
             **alto fundamentals 150–700 Hz, presence 2–4 kHz; soprano is naturally brighter and
             turns harsh easily — high-pass around 100 Hz and reduce 3–5 kHz** (sax live-mixing
             guidance, Sax on the Web + musicalinstrumenthub live-EQ guides). One outdoor-jazz
             report describes cutting treble hard (≈ −15 dB) on a Beta dynamic at an outdoor
             venue — directionally the same call this build makes.
WEB SAYS     Wet pedal output arrives with its own top-end lift and often its own reverb; the
             FOH job is to leave room rather than add.
KB SAYS      Nothing — no KB row for a processed line-level horn feed.
VERDICT      **THIN.** No capsule data is knowable before load-in and the KB is silent. Values
             are deliberately conservative and the channel is flagged for a load-in listen.
LOCKER       Exempt twice over — TOUR gear and an XLR line feed.
GENRE BEND   Smooth jazz: the horn is the lead voice. Body protected, harshness controlled.
VENUE BEND   **FSQ depth held at −5**, not −8: this is a line-level feed with no cab, no box and
             no stage bleed, so there is no mechanical mud for the outdoor rule to fight, and
             smooth-jazz sax needs its body.
DRAFT BANDS  HPF 100 · LPF 15000 · B4 −4 @ 8000 Q2 · B3 −5 @ 3500 Q2 · B2 −5 @ 300 Q2 · B1 FLAT
GATE CHECK   **No boosts.** B3 at 3500 is built for the **union of both horns** — it sits in the
             soprano's harsh 3–5 kHz band, which is the worse-behaved of the two, while landing
             just above the alto's 2–4 kHz presence so the alto pays almost nothing for it.
             That is the whole reason one channel can carry both horns without a scene change.
QUESTIONS    none blocking, but three load-in confirmations: set the input to LINE with the pad
             in and **no 48 V**; confirm the pedal's output level before he plays; and if his
             pedal is already producing reverb, keep our send low so the two don't stack.

---

## Unit 14 — Vocals × Shure Beta 58A, house wireless (CH 33, 34, 35 — both shows)

INSTRUMENT   Three vocals per show. **Voice types unknown — Brian asked me to research and
             suggest.**
MIC          Shure Beta 58A on the FSQ house wireless, faders 33/34/35 (Wireless 1–3).
SEARCHES     "Shure Beta 58A frequency response presence peaks 4kHz 10kHz supercardioid live
             vocal EQ"; ""Mic. Carr" Shades vocalist baritone tenor voice neo-soul singer";
             "Ric Sexton saxophonist vocalists "Mr. Wynn" Feyth singer".
CAPSULE FACT **50 Hz–16 kHz, attenuated below 500 Hz to counter proximity, with TWO presence
             peaks at 4 kHz and 10 kHz** (Shure Beta 58A specification sheet; Sound On Sound
             Beta Series review). Supercardioid — keep wedges 30–60° off axis.
WEB SAYS     The dual peaks exist to cut through a loud backing track; several reviewers find
             them grating. Vocal-range references: bass fundamentals 82–330 Hz with presence
             sitting low at 1–3 kHz; tenor 130–523 Hz; alto 175–700 Hz. Live HPF guidance runs
             60–100 Hz for male voices, 80–120 Hz for female.
             **What the web could NOT resolve:** neither act publishes voice types. The Shades
             research confirms Mic. Carr as the male lead and the band's "smooth harmonies";
             Sexton's *Fruition* credits name Mr. Wynn and Feyth as the vocalists on "If You
             Could See". No source classifies any of them.
KB SAYS      "Supercardioid vocal dynamic, 50 Hz–16 kHz, <500 Hz attenuated for proximity
             control, TWO presence peaks (~4 kHz and ~10 kHz) — brighter/more bite than SM58…
             Weakness: those peaks can get strident/sibilant."
VERDICT      **AGREE** on the capsule. **THIN** on the voice types — and the honest answer is
             that this one can't be researched away; it resolves at soundcheck.
LOCKER       House wireless capsule — fixed rig, not a fork.
GENRE BEND   Both acts are vocal-forward with harmony singing. Warmth protected at −5, not −8,
             per the genre-over-venue trade.
VENUE BEND   **Template HPF 184 overridden on all six vocal channels.** 184 Hz sits above the
             entire lower octave of any male voice (E2 = 82 Hz). Leads go to 90, harmonies to
             110 — 110 is the safe overlap of the male 60–100 and female 80–120 ranges, so it
             is correct whichever way the voices fall.
             **RH 87–94%** → both baked peaks trimmed on every vocal.
DRAFT BANDS  **Cuts only, every band, every channel.** Lanes chosen so no two vocals are cut in
             the same place:
             *The Shades* — CH33 Mic. Carr (lead): HPF 90 · LPF 15000 · B4 −3 @ 10000 Q2 ·
             B3 −2 @ 4000 Q3 · B2 −5 @ 700 Q2 · B1 FLAT.
             CH34 Vox 2: HPF 110 · LPF 14000 · B4 −4 @ 10000 Q2 · B3 −4 @ 4000 Q2 ·
             B2 −5 @ 1500 Q2 · B1 FLAT.
             CH35 Vox 3: HPF 110 · LPF 14000 · B4 −4 @ 10000 Q2 · B3 −4 @ 4000 Q2 ·
             B2 −5 @ 1200 Q2 · B1 FLAT.
             *Ric Sexton* — CH33 Vox 1: as the Shades lead. CH34 Vox 2: HPF 110 · LPF 14000 ·
             B4 −4 @ 10000 · B3 −3 @ 4000 · B2 −5 @ 1400 · B1 FLAT.
             CH35 Ric (host/talk): HPF 120 · LPF 12000 · B4 −5 @ 10000 Q2 · B3 −4 @ 3500 Q2 ·
             B2 −6 @ 400 Q2 · B1 FLAT.
GATE CHECK   **Zero boosts across all six vocal channels** — the cuts-only rule, and every
             channel's B4 and B3 land on the two measured capsule peaks. The lead keeps the most
             4 kHz (−2, tight Q3) so he stays the most intelligible voice; the harmonies are
             pulled −3/−4 there to sit behind him. Separation comes from the B2 lane: lead at
             700 Hz, harmonies at 1200/1400/1500 Hz — no two the same, so the cuts don't stack
             when they sing together.
QUESTIONS    Roles are my researched best guess, not confirmed. If the lead isn't on Wireless 1,
             **swap the curves wholesale** — the three are complete, self-consistent sets. And
             if any singer turns out to be a true bass voice, move his B2 cut down to 700 and
             leave 1.2–1.8 kHz alone; cutting a bass singer at 1.5 kHz costs intelligibility the
             higher voices can afford.
