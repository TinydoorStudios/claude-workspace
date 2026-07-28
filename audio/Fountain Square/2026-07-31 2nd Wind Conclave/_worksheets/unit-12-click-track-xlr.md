# Unit 12 — Click / Track × XLR line feed  (ch 15 Click, ch 16 Track)

INSTRUMENT   Two very different jobs on adjacent channels.
             **Ch 15 Click** — the metronome the band plays to. It exists so it can be routed to
             monitors and IEMs. **It must never reach the mains, and it must never reach the
             multitrack bus.** This is a routing channel with a mic input, not a source.
             **Ch 16 Track** — the backing-track playback: the parts this band's press advertises
             (horn section, strings, programmed percussion, sub) that don't appear anywhere on
             this 24-channel input list. It's the reason a 10-piece show band can cover Bruno
             Mars faithfully.

MIC/DI       XLR line feeds from the band's playback rig. **Locker fork: EXEMPT** — line level,
             no capsule. Nothing to swap.
             Practical note: whether the Track arrives mono or stereo isn't stated. One channel
             on the list says mono, but a stereo track folded to one XLR is common. Worth a
             glance at load-in; it doesn't block the build.

SEARCHES     1. Covered by the artist research (Part I) — the click/track pair is the direct
                evidence that this band runs rehearsed, click-locked arrangements, cross-checked
                against The Bash's description of their repertoire and their Usher-tribute
                production.
             2. No capsule research applies: there is no transducer on either channel. Per the
                research floor, the "unit" here is a **finished stereo program feed**, and the
                relevant fact is what's already been done to it, not what a mic did to it.

CAPSULE FACT No capsule on either channel — and for ch 16 that's the whole finding. A backing
             track is **mastered audio**: it has already been EQ'd, compressed and limited by
             whoever produced it, usually to commercial loudness. It is the single most
             finished signal arriving at this desk.

WEB SAYS     Standard live practice for tracks: leave them alone. The playback is the reference
             the rest of the mix is being matched to, so shaping it means shaping the target.
             The only routine desk moves are a protective high-pass and, on an outdoor system, a
             trim where the track's own low end doubles the live rhythm section.

KB SAYS      eq-starting-points has a "Line / BT" style approach in prior FSQ specs — playback
             channels run essentially flat with a protective HPF. No dedicated KB row.

VERDICT      **THIN**, and appropriately so — there's little to reconcile because the correct
             treatment is minimal treatment. Going with the standard practice and flagging the
             missing KB row. → **KB write-back candidate** (a playback/backing-track row).

GENRE BEND   R&B/funk show band: the track carries the horn and string parts. That means it's
             not background — it's a *section* of the band, and it needs to be as intelligible
             as the live players. But it arrives already balanced against itself, so the way to
             make it read is the fader and the low-end trim, not upper-mid EQ.

VENUE BEND   FSQ: the track's own kick and sub content will stack on top of the D6 kick, the
             bass and any 808s from the pads. That's four low sources in a venue with 8× KS21 a
             side and no room gain to absorb the pile. A moderate 250 Hz trim keeps it out of
             the live rhythm section's way without touching what makes it sound like the record.

DRAFT BANDS  **ch 15 Click**
             HPF 200 · LPF OFF
             B4 / B3 / B2 / B1  **all FLAT**
             The click gets no EQ at all. Its only job is to be audible in a wedge or an IEM,
             and it is a synthesised sound that is already exactly what it needs to be. The
             HPF at 200 is housekeeping on the cable run, nothing more.
             ⚠ **Routing, not EQ, is this channel's requirement: OUT of the LR mains, OUT of
             any FOH-fed matrix, and out of the record bus.**

             **ch 16 Track**
             HPF 35 · LPF OFF
             B4  FLAT
             B3  −4 @ 250   Q 1.8  BELL   de-stack from the live rhythm section
             B2  FLAT
             B1  FLAT

GATE CHECK   **One band written across two channels — that is the correct answer here, not a
             thin one.** The gate question for finished audio is "has someone already made this
             decision?", and for a mastered backing track the answer is yes, at every frequency.
             The only move that survives is the one addressing a problem the track's producer
             couldn't have known about: this specific plaza, with this specific live rhythm
             section stacked on top.
             **HPF 35 on the Track is deliberately the lowest filter in the show.** The track's
             sub content is part of what it's for — cutting it would be removing the very thing
             the band is paying to have. It sits below the bass guitar's 45 and well below
             everything else.
             **Against the low-end slot map (unit 09):** the track is the one source down there
             that gets no boost and no deep cut — it's the reference, so it keeps its shape and
             the live sources are slotted around it.

QUESTIONS    1. Confirm the **Click never reaches the mains** and is excluded from the record
                bus — a routing confirmation, not an EQ one.
             2. Is the Track mono, or a stereo pair folded to one channel?
             3. KB write-back candidate — add a playback/backing-track row to eq-starting-points.
