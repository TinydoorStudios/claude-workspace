# Unit 14 — Click + backing Track × XLR line feeds · CH 15, CH 16

INSTRUMENT   CH 15 **Click** — the drummer's/band's click reference. CH 16 **Track** — the backing
             playback bed. Brian confirmed in the round (2026-08-08) that ch 15 is a REAL input, not
             a leftover row: the band genuinely runs to a click. The Track is finished, mixed and
             mastered program material — the horn and string parts the band's press sells live in
             here and in the keys/pads, since there are no horn channels on the list.
             Both unchanged in role from rev 1.

MIC          Neither — XLR line feeds. **EXEMPT from the locker fork** (line level, no capsule).

SEARCHES     1. `backing track playback channel live sound FOH EQ mastered program material do not
                EQ high pass` — consensus: treat as program, not as an instrument
             2. `click track routing live sound must not reach mains muted channel FOH best practice`

CAPSULE FACT (equipment fact) A backing track from a playback rig arrives **already mixed and
             mastered at line level** — its spectral balance is a finished master, not a raw source.
             The externally-consistent live-sound position is that such a channel gets housekeeping
             filtering and level, and that shaping it broadly re-masters someone else's mix in
             public. The one exception worth acting on is low-end overlap, since a mastered bed
             carries its own kick and bass energy which collides with ch 1/2/11/12.

WEB SAYS     For the CLICK the only thing that matters is routing discipline, not tone: it must not
             reach the mains under any circumstance, and it does not belong in the record bus.

KB SAYS      `eq-starting-points` has **no row for backing-track playback and none for a click
             feed** — two of the four rows in the write-back Brian approved today. The KB's general
             principle that applies is the capsule/IR gate generalised: don't shape something that
             has already been shaped.

VERDICT      **THIN on the KB side by absence, AGREE on the web side, and closed by Brian's
             answers.** The KB has no article for either source; the round resolved the routing
             question for ch 15 explicitly and confirmed ch 16 as mono. The missing KB rows are
             staged.

LOCKER       **Exempt** — both are line feeds.

GENRE BEND   The Track carries the arrangement's horns and strings. That is the reason the keys'
             1–2 kHz window is left untouched (unit 17) and the reason the guitar is cut at 800 and
             left alone above it (unit 12) — three sources are deliberately staying out of the band
             where the programmed horn lines live. Artist layer: a rehearsed show band to a click
             means the Track is load-bearing, not decorative; if it disappears, the arrangement has
             holes.

VENUE BEND   FSQ outdoor: the Track's mud cut sits at FSQ-appropriate depth but stays modest,
             because it is a master rather than a source. CH 15 gets no venue treatment at all —
             it is never in the PA.

DRAFT BANDS  **CH 15 — Click** (routing channel, not a tone channel)
             HPF 200 · LPF OFF
             B4 FLAT · B3 FLAT · B2 FLAT · B1 FLAT
             ⚠ **MUTED from the mains. OUT of the record bus.** HPF 200 is housekeeping only.

             **CH 16 — Track** (mono)
             HPF 35 · LPF OFF
             B4  FLAT
             B3  −4 | 250 | 1.8 | BELL
             B2  FLAT
             B1  FLAT

GATE CHECK   **No boosts on either channel — nothing to permit, and on ch 16 that is a rule rather
             than a coincidence.** The Track is a finished master: every boost would be re-EQing
             someone else's mix through a plaza PA. The single cut at 250 Hz is the one defensible
             move — it is not tone, it is making room, because the master's own kick and bass energy
             sits on top of ch 1/2 (kick) and ch 11/12 (bass) in exactly that octave. HPF 35 lets
             the master's sub content through since the KS21 arch can reproduce it and the
             programmed low end is part of the arrangement.
             CH 15 has no EQ at all by design; a click channel with EQ implies someone considered
             putting it in the PA.

QUESTIONS    None. Both resolved in the round.

TRACE        base(click reference + mastered backing bed — program material, not sources) ·
             equip(line-level playback rig; the Track is already mixed and mastered, which is the
             fact that forbids shaping it) ·
             genre(the Track carries the horn/string parts an R&B show band needs — three other
             channels stay out of its window because of this) ·
             artist(rehearsed to a click; the Track is load-bearing, and Brian confirmed the click
             is a real input) ·
             venue(FSQ outdoor: 250 cut on the Track to make room for kick and bass, kept modest
             because it is a master; no venue treatment on the click — it never reaches the PA)
