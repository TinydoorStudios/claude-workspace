# Unit 10 — Bass guitar × amp XLR out (post-EQ) · CH 11

INSTRUMENT   Electric bass through the player's own amp. In an R&B/funk/Motown show band the bass
             IS the arrangement's spine — walking Motown lines, funk sixteenth pockets, and it
             locks to a click with programmed low end in the Track channel. Role in THIS mix:
             pitch and articulation you can follow on a plaza with no room gain.
             **Source changed this week** — rev 1 ran Brian's own RNDI here. **Two-mic (mic + DI)
             source with CH 12 (PG52 on the cab).**

MIC          Not a mic — **the bass amp's XLR direct out, POST-EQ.** Confirmed by Brian in the
             round, 2026-08-08. **EXEMPT from the locker fork** (XLR line feed, no capsule).
             The consequential fact from his answer: the player's tone decisions are already baked
             into this signal, so the desk's job here is corrective, not creative.

SEARCHES     1. `bass amp XLR DI out post EQ live sound FOH EQ approach do not re-voice player tone
                250Hz mud`
             2. TalkBass, *Why do so many amps have an XLR out that is only post-EQ?* and
                *DI vs amp XLR?*; Gearspace, *Live bass tones through DIs vs XLR outs*

CAPSULE FACT (equipment fact, in place of a capsule fact) **A post-EQ amp DI is typically noisier
             and often excessively BRIGHT** — the mechanism is quantified in the TalkBass
             consensus: "a traditional bass speaker functions like a high pass filter and rolls off
             the highs — if the player cranks the highs to compensate, the sound coming out of the
             post DI will be obnoxiously bright." Alongside that, "most amps have a baked-in EQ
             curve… typically a cut to the mids and/or boost of lows & highs, which makes them
             sound great through the amp's speakers but not in a full range system." The FOH
             remedy the same threads land on: cut around **250 Hz** for mud, and shape at the
             console rather than asking the player to change their stage tone.

WEB SAYS     Two things that directly set this channel's numbers. First, **expect too much top,
             not too little** — so the treatment up top is a trim, never a lift, which is the
             opposite of what rev 1 did with a clean RNDI (`B4 +3 | 2500`). Second, **the amp has
             already cut its own mids**, so a further mid scoop at the desk would hollow the bass
             out of the arrangement; the mid work here is narrow and corrective, not a broad scoop.

KB SAYS      `eq-starting-points` has no row for a post-EQ amp DI feed — this is one of the four
             gaps in the staged KB write-back Brian approved today (synth bass, modeller/direct
             guitar feed, sampling pad, backing-track playback all have the same hole). The KB's
             general bass guidance and its DI rows assume a CLEAN instrument-level DI, which this
             is not, so leaning on them would have been the wrong read.

VERDICT      **THIN on the KB side, and Brian's answer is what closes it.** The web pass is solid
             and quantitative; the KB simply has no article for this source type. Rather than
             average or guess, this was raised as Q4 in the round and Brian named the source
             ("amp's XLR out, post-EQ") and the lane split. That is ground truth, so the gap is
             resolved by decision rather than by inference — and the missing `eq-starting-points`
             row is one of the write-backs he approved, so the next show inherits it.

LOCKER       **Exempt** — XLR line feed at line level with no capsule in front of it. No fork, no
             question, no line in the packet.

GENRE BEND   Motown/funk bass wants a round, singing fundamental with clear note definition and NO
             clank. Because the feed is post-EQ and likely bright, the genre bend is delivered by
             *removing* what fights that picture rather than by adding warmth. Artist layer: they
             back national R&B/gospel acts and play to a click — the bass is disciplined and
             consistent, so narrow decisive cuts are safe.

VENUE BEND   FSQ outdoor, no room gain. The mud cut at 250 Hz gets full FSQ depth (−7, not a
             polite −4) — a plaza gives back nothing, and 250 Hz mud on a dance floor is what
             turns a bass line into a rumble. HPF at **50** rather than lower: it keeps the low E's
             41 Hz fundamental substantially intact while handing the deep weight to ch 12, per the
             lane split Brian set. Weather layer: **no change** — dry-air HF loss is irrelevant on
             a source whose problem is too MUCH high end arriving, and the correction is a trim
             either way.

DRAFT BANDS  HPF 50 · LPF 8000
             B4  −3 | 5000 | 1.5 | BELL
             B3  −4 | 2000 | 1.8 | BELL
             B2  −7 |  250 | 2.0 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit, and that is the point.** The gate
             applies to a baked EQ curve exactly as it applies to a capsule (same principle as
             cab-sim feeds counting as mic'd cabs):
             - **No presence boost.** Rev 1's `+3 @ 2500` was built for a clean RNDI. Against a
               post-EQ feed whose documented tendency is "obnoxiously bright," a presence lift
               stacks on the player's own high boost plus their compensation for the cab's HF
               rolloff. Withdrawn, and replaced by trims at 5000 and 2000.
             - **No low boost.** The amp's baked curve already boosts lows, and ch 12 owns the
               bottom. B1 FLAT.
             - **No broad mid scoop.** The amp already cut its mids; B3 is a narrow −4 at 2000
               aimed at clank, not a scoop.
             - The 5000 trim is deliberately modest at −3 with a note to expect wanting more:
               "often excessively bright" is a tendency, not a measurement, so this one is a
               soundcheck ride rather than a value to trust blind.

TWO-MIC LANES (CH 11 × CH 12 — mic + DI on one source, assigned top AND bottom)
             CH 11 (post-EQ DI)  owns **DEFINITION / TOP** — pitch, pick, string articulation
             CH 12 (PG52 on cab) owns **LOW BODY** — the weight the KS21 arch reproduces
             Shared zones named: **4–5 kHz** (ch 11 trims 5000, ch 12 trims 4500 — offset, and
             NEITHER boosts, so nothing stacks) · **60–100 Hz** (ch 12 owns it via its published
             hump, ch 11 filtered at 50 and B1 flat) · **200–800 Hz** (ch 11 cuts 250 hard; ch 12
             does NOT cut there at all because its capsule already dips through that whole span —
             see unit 11. Different treatment, same region, no double-dip.)
             **No boost on either leg anywhere.** Verified.
             ⚠ **Polarity-check the pair in mono at soundcheck** — a cab mic and a line-level amp
             out are not time-aligned, and if the sum is thinner than either alone, flip ch 12.

QUESTIONS    None. Q4 answered in the round.

TRACE        base(electric bass, arrangement spine — mud at 250 is the primary target per TalkBass
             FOH consensus) ·
             equip(post-EQ amp XLR out — TalkBass: baked amp curve cuts mids and boosts lows/highs,
             and a post DI is "often excessively bright" because the player compensates for the
             cab's HF rolloff. This layer REVERSED rev 1's presence boost into a trim) ·
             genre(Motown/funk wants a round singing fundamental with no clank — delivered by
             removal, not addition) ·
             artist(disciplined, locked to a click alongside programmed low end — narrow decisive
             cuts are safe) ·
             venue(FSQ outdoor: 250 mud cut deepened to −7; HPF 50 hands the deep weight to ch 12
             per Brian's lane call; dry air = no change on a too-bright source)
