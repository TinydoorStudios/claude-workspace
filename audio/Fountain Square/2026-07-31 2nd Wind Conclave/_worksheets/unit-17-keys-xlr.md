# Unit 17 — Keys × XLR line feed, stereo  (ch 23 Key Left, ch 24 Key Right)

INSTRUMENT   Stage keyboard rig, stereo out, line level. In a Cincinnati R&B/funk show band the
             keys chair covers the widest ground of anyone: acoustic piano for the ballads,
             Rhodes/Wurlitzer for the soul material, B3 for the gospel-adjacent moments, and
             synth brass or strings standing in for the horn parts this input list doesn't have.
             That range is the defining fact about this channel — one EQ has to serve all of it,
             so it has to be corrective and conservative, not characterful.
             **Equipment: not notated.** No board model, no patch list. Nothing invented.

MIC/DI       XLR line feed, stereo pair. **Locker fork: EXEMPT** — line-level input, no capsule
             in front of it. No fork raised, no line in the packet.
             Note for the patch: hard-panned L/R, and the two channels must carry **identical**
             EQ or the stereo image will shift with frequency.

SEARCHES     1. `stage keyboard DI stereo live EQ high pass 60Hz mud 300Hz Rhodes organ pads
                R&B live sound`
             2. Cross-read of the returned MusicRadar live-keys guide, the YamahaSynth "Art of
                EQ" piece, the Gearspace stereo-vs-mono-keys thread and the instrument EQ charts.

CAPSULE FACT No capsule — and that is the operative fact. A stage keyboard's XLR out is a
             finished, already-voiced signal: the patch designer has already made every tonal
             decision, and the board's own output stage is flat. There is nothing baked in to
             gate against and nothing missing to restore, which is why this channel is almost
             entirely subtractive. Quantitative anchors from the research: high-pass **50–60 Hz**
             for stage rumble, and the **300–500 Hz** region is where keyboard energy stacks
             against everything else on the stage.

WEB SAYS     Consistent live-keys guidance: high-pass from 50–60 Hz upward to lose rumble; the
             first move on a Rhodes is always cutting mud, because its dense harmonics clash
             with the bass; check 200–300 Hz with a narrow cut for muddiness; organ wants
             low-mid presence around 300–500 Hz, which pulls directly *against* the mud cut —
             so the honest answer for a rig playing both is a moderate cut placed carefully,
             not a deep one. Hard-panned stereo DI is the standard live approach.

KB SAYS      eq-starting-points, keys/DI: subtractive, let the instrument's voicing stand, watch
             the low-mid stack against bass and guitar. The KB has no Rhodes/organ-specific row.

VERDICT      **AGREE**, with one caveat I'm resolving rather than escalating: the research itself
             contains an internal tension (cut 300 for Rhodes mud, boost 300–500 for organ) and
             the KB's "subtractive, conservative" line is what breaks the tie. On a rig that
             plays both inside one set, a **moderate** cut at 300 is the move that serves both —
             it clears the Rhodes without gutting the organ, and the organ's weight can come
             back on the fader.

GENRE BEND   R&B/funk: the keys are the harmonic bed under four vocals. Their job is to be
             wide, warm and *out of the way*. Artist layer — with no horn channels on this input
             list, the keys and pads are almost certainly carrying the horn and string lines this
             band's press advertises, so the upper-mid region needs to stay clear enough for
             those parts to speak. That's an argument against cutting the 1–2 kHz region hard.

VENUE BEND   FSQ outdoor: no room gain, and the 300–500 Hz stack is the single biggest mud
             contributor in a mix that also has bass, bass synth, guitar and pads. Outdoor depth
             applies — but this channel gets the **moderate** end of the outdoor range (−6) rather
             than the deep end, because the same band is carrying organ weight. HPF at 60 keeps
             the piano's left hand while losing the rumble.

DRAFT BANDS  *(identical on ch 23 and ch 24 — stereo pair)*
             HPF 60 · LPF OFF
             B4  FLAT
             B3  −6 @ 300   Q 1.8  BELL   the Rhodes/piano mud stack — moderate, see verdict
             B2  −4 @ 800   Q 2.0  BELL   low-mid honk against guitar and vocals
             B1  FLAT

GATE CHECK   **No boosts on this channel.** There is no capsule to gate against, but the source
             gate applies and it's decisive: this signal is a finished patch. Anything the
             keyboard player wants more of, they can dial on their own board with far more
             precision than a 4-band desk EQ — boosting a stage keyboard at FOH is a way of
             fighting a patch rather than fixing a problem.
             **Against the other midrange sources:** guitar cuts 900, keys cut 800, bass synth
             boosts 1200, D6 kick cuts 1200. The 1–2 kHz window where synth horns and strings
             would live is left untouched on this channel — deliberately, per the genre bend.
             **Stereo integrity:** both channels carry byte-identical EQ. A different curve on
             L and R would make the image wander, which is worse than any EQ benefit.

QUESTIONS    None blocking. Noted for the round: with no horn channels on the list, confirm the
             horn/string parts are coming from keys, pads and the Track channel.
