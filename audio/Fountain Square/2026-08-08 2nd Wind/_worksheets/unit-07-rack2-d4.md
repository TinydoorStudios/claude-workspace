# Unit 07 — Rack tom 2 (low) × Audix D4 · CH 7

INSTRUMENT   Lower rack tom. Same fill-instrument role as ch 6, one drum bigger — its note sits
             around 110–130 Hz rather than 150+. Middle drum of the three-tom section.
             **Mic changed this week** — rev 1 had a second D2 here. The D2 → D4 → D6 progression
             across ch 6/7/8 is a deliberate descending-size choice and it passed the fork gate
             (see plan.md), but the D4's published curve is nothing like the D2's, so this channel
             is re-derived from scratch rather than copied from rev 1's ch 7.

MIC          Audix D4. Hypercardioid dynamic, no phantom, no switches. Published 38 Hz–19 kHz,
             144 dB SPL.

SEARCHES     1. `Audix D4 tom mic frequency response chart +6dB 5kHz peak rolloff below 70Hz
                RecordingHacks`
             2. Audix D4 product page + RecordingHacks D4/OM6 review (chart history)

CAPSULE FACT **Audix's current response chart shows a +6 dB peak at 5 kHz, a secondary peak above
             10 kHz, and a low-frequency rolloff below 70 Hz** (RecordingHacks D4 profile reading
             Audix's current chart). Worth knowing: an earlier c.2001 chart showed a rising HF
             response peaking **+9 dB at 10 kHz**; RecordingHacks notes the published graph has
             changed without an explanation of whether the mic or the measurement changed. Either
             chart points the same direction — this capsule is HF-forward, not HF-shy.

WEB SAYS     The published 38 Hz figure does not translate into usable deep low end in practice —
             the chart rolls off below 70 Hz. So the D4 is not the mic to lean on for sub reach,
             and it does NOT lack upper-mid attack. Both halves of that matter here.

KB SAYS      mic-library, row **corrected 2026-07-30**: "Audix's current response chart shows
             +6 dB at 5 kHz with a secondary peak above 10 kHz, and a low-frequency rolloff below
             70 Hz — so it does NOT lack upper-mid attack and it does NOT reach into the 30s in
             practice. Weakness: that 5 kHz peak stacks fast on a ringy floor tom, and the sub
             reach isn't there to lean on outdoors." Bias: **trim the peak ~5000 Hz, never boost
             there; restore weight ~80 Hz rather than expecting sub reach.**

VERDICT      **AGREE** — and this is a case where the KB has already absorbed the web finding. The
             row was corrected on 2026-07-30 against exactly the RecordingHacks reading found
             again today, on Brian's own call during the 2026-08-01 Repertoire build. The old row
             ("reaches 35 Hz… less upper-mid attack, may need a touch of click") would have put a
             click boost directly onto a +6 dB baked peak. Fresh pass and corrected KB agree.

LOCKER       Pass with a note, no fork raised. The D4 is mic-library's floor-tom mic rather than
             its rack-tom mic, but on the LOWER of two rack toms its extra low reach relative to a
             D2 is the point, and the alternative that would win on paper (MD 421-U, KB first
             choice for toms) is the same mic offered on the ch 8 fork — it can only go one place,
             and ch 8 was the stronger place to spend it. Brian kept the D6 there, so the 421-U is
             unused; raising a second fork for it now would be re-plumbing the kit rather than
             advising on it.

GENRE BEND   Same as ch 6 — funk/R&B fills want pitch and attack. The attack is baked (+6 @ 5 k),
             so the genre bend here is a refused boost plus a trim. Artist layer: placed fills in
             rehearsed arrangements, nothing to over-emphasise.

VENUE BEND   FSQ outdoor: box cut at FSQ depth, placed at **450 Hz** to offset ch 6's 350. The
             weight restoration sits at **110 Hz**, not the KB's generic ~80, because this is a
             mid rack tom rather than a floor tom and 110 is this drum's own note — and because
             80 Hz belongs to the kick and bass lanes on this show's low-end slot map. Weather
             layer: 38 % RH dry air argued for lightening the 5 kHz trim the way ch 3's was
             lightened, but it is held at −4 — see gate check.

DRAFT BANDS  HPF 80 · LPF 12000
             B4  −4 | 5000 | 1.5 | BELL
             B3  −7 |  450 | 2.0 | BELL
             B2  +3 |  110 | 1.2 | BELL
             B1  FLAT

GATE CHECK   **One boost: B2 +3 @ 110. The fact that permits it —** Audix's current chart shows a
             **low-frequency rolloff below 70 Hz** with no documented peak in the 100–130 Hz
             region. So a lift at 110 lands on unvoiced (and in fact falling) response, restoring
             this drum's own note rather than stacking on a voiced one. This is precisely the KB's
             corrected bias line — "restore weight ~80 Hz rather than expecting sub reach" — moved
             up to 110 for a rack tom instead of a floor tom.
             - **B4 −4 @ 5000 is a trim, never a boost.** The capsule bakes **+6 dB at 5 kHz**. A
               click boost here is the exact mistake the 2026-07-30 KB correction was made to
               prevent. Dry air argued for lightening it to −3 (the reasoning that moved ch 3's
               snare trim), but it is **held at −4**: on a snare that region is crack, which the
               air merely dulls, whereas on a ringy tom it is ring, which the air does nothing to
               shorten. Ring is the bigger liability than the lost air, so the trim stays full.
             - **B1 FLAT.** No sub boost — the chart rolls off below 70 and there is nothing there
               to lift, which is the honest version of "don't lean on it outdoors."
             - B3 −7 @ 450 is shell box, unvoiced on this capsule, full FSQ depth.

TOM SECTION SLOTTING  (see unit 06 for the full three-tom map)
             CH 7 owns box **450** and weight **110**. Neither number appears on ch 6 or ch 8.

QUESTIONS    None.

TRACE        base(low rack tom on a hypercardioid dynamic — RecordingHacks/Audix current chart
             +6 dB @ 5 kHz, secondary peak >10 kHz, rolloff below 70 Hz: attack baked, sub reach
             absent) ·
             equip(no tom sizes or heads notated; the mic CHANGE from rev 1's D2 is what re-derived
             this channel) ·
             genre(funk/R&B fills want pitch and attack — attack refused as baked, pitch restored
             at 110) ·
             artist(placed fills, rehearsed to a click — no over-emphasis needed) ·
             venue(FSQ outdoor: box −7 OFFSET to 450 against ch 6's 350; weight at 110 rather than
             80 to stay off the kick/bass lanes; 38 % RH dry air did NOT lighten the 5 k trim here
             because tom ring outlives the air loss)
