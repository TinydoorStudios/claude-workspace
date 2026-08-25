# Unit 08 — Floor tom × Audix D6 · CH 8 · **Brian kept the D6 (fork declined 2026-08-08)**

INSTRUMENT   Floor tom. On this set it's the big punctuation drum — the bottom of a fill, the
             tribal groove under a breakdown. Lowest of the three toms. **Mic changed this week** —
             rev 1 had a D4 here. The D6 is a kick capsule doing tom duty, which is a real and
             known technique, and it is the single most opinionated capsule choice on the kit.

MIC          Audix D6. Cardioid dynamic, no phantom, no switches.
             **LOCKER FORK RAISED AND DECLINED.** The MD 421-U was offered (KB first choice for
             toms, free this show, real low-mid girth where the D6 has a −15 dB hole). Brian's
             call: **keep the D6.** So this channel is built FOR the scooped voicing, not around
             it — no attempt to reconstruct the midrange body the capsule deliberately removes.
             One line goes in mic_notes so the fork isn't re-litigated next rev.

SEARCHES     1. `Audix D6 floor tom instead of kick mic scoop 600Hz -15dB response chart 63Hz peak
                5kHz`
             2. Tape Op D6 review (via RecordingHacks) + Audix D6 product page

CAPSULE FACT **The low end peaks at 60 Hz, the high end peaks at 4 kHz and 10 kHz, and the
             midrange at 750 Hz sits about 15 dB below those peaks** (Tape Op's measured review of
             the D6, via RecordingHacks) — described elsewhere as a pronounced midrange dip around
             700 Hz with a boost between 5 and 12 kHz. Audix's own product listing names **floor
             tom** as an intended application alongside kick, bass cabs and Leslie lows.

WEB SAYS     Directly on point for this channel: on floor toms the D6 gives "well-defined lows
             coupled with a prominent stick sound even when the mic was pointed towards the edge
             of the drum head." So the technique is externally supported, and the two things it
             delivers are exactly the two things the response chart predicts — bottom and stick.
             What it does NOT deliver is midrange body, by design.

KB SAYS      mic-library: "Pre-scooped 'smiley' kick voicing: peaks ~63 Hz and ~5 kHz, deep mid
             scoop ~600 Hz (−15 dB). Thump + click baked in; needs almost no EQ. Weakness:
             one-trick, no midrange body." Bias: ease off attack, boom, box, mud.

VERDICT      **AGREE, with a refinement the KB should absorb.** Both sides describe the same
             smiley curve. The web pass is more precise on two numbers: the mid dip centres nearer
             **750 Hz** than 600, and the HF has **two** peaks — **4 kHz and 10 kHz** — where the
             KB row says only "~5 kHz." That refinement is one of the five write-backs Brian
             approved today, and it changes this build concretely: the HF trim goes to **4000**,
             the peak Tape Op actually measured, rather than to a 5 k figure that would sit
             between the two real peaks and catch neither.

LOCKER       **Fork raised, declined by Brian.** Recorded in `decisions` and in mic_notes:
             "Locker fork — MD 421-U offered, D6 kept (Brian's call). Built for the scooped
             voicing." The 421-U therefore stays unused this show.

GENRE BEND   R&B/funk: a scooped, modern dance-floor floor tom is a legitimate and current sound —
             this is not a compromise, it's a choice, and Brian made it. So the genre bend is
             *don't fight the capsule*: no midrange reconstruction, let the bottom and the stick
             be the whole drum. Artist layer: they play to a click with programmed low end in the
             Track channel, which is the one real risk of a 60 Hz-peaking capsule on a tom — see
             venue/gate.

VENUE BEND   FSQ outdoor, no room gain, and this is where the D6's voicing needs managing rather
             than exploited: **its 60 Hz peak lands squarely in the kick and bass lanes.** Left
             alone, a floor tom mic'd with a kick capsule reads as a second kick drum on a plaza.
             The HPF is therefore set at **80 Hz — deliberately above the capsule's 60 Hz peak** —
             to trim that peak with the filter and keep the drum out of the kick's territory, and
             the drum's own note is restored just above it. Ring cut gets FSQ depth. Weather
             layer: 38 % RH dry air argues against trimming the top hard, so the 4 kHz trim is
             sized to de-stack rather than to tame — the stick sound is what makes this drum
             audible at the back of the plaza.

DRAFT BANDS  HPF 80 · LPF 10000
             B4  −4 | 4000 | 1.5 | BELL
             B3  FLAT
             B2  −6 |  300 | 2.0 | BELL
             B1  +3 |  105 | 1.2 | BELL

GATE CHECK   **One boost: B1 +3 @ 105. The fact that permits it —** the D6's documented low peak
             is at **60 Hz** and its documented dip is at **750 Hz**; 105 Hz is neither. It sits on
             the descending slope between them, i.e. unvoiced response, so the lift restores this
             drum's own fundamental instead of stacking on the capsule's kick-voiced bottom. This
             is the whole strategy for keeping a kick capsule from sounding like a kick: filter
             OFF the 60 Hz peak at HPF 80, then put the weight back where the drum actually
             speaks.
             - **B3 FLAT is the reverse gate.** The capsule already sits **~15 dB down at 750 Hz**.
               A box/mud cut there — which the FSQ outdoor override would normally push to −7 or
               −8 — would double-dip a hole that already exists. This is the same reasoning applied
               to the D6 on kick duty in rev 1, and it holds identically here.
             - **B2 −6 @ 300 is available and needed.** Floor-tom ring lives 200–400 Hz, which is
               *outside* the 750 Hz scoop, so unlike B3 there is real response there to cut. This
               is what keeps the channel from being uselessly thin.
             - **B4 −4 @ 4000 is a trim on a measured peak**, placed at 4 k rather than 5 k on
               today's Tape Op reading. It de-stacks the stick sound from the three cymbal mics and
               the bottom-snare's 9 k lift. LPF 10000 additionally shades the capsule's SECOND
               documented peak at 10 kHz, which is otherwise pure cymbal-bleed amplification on a
               kit with three cymbal mics.

TOM SECTION SLOTTING  (see unit 06 for the full three-tom map)
             CH 8 owns ring **300** and note **105**. Neither appears on ch 6 or ch 7, and its HF
             trim at 4000 differs from ch 7's 5000 because the two capsules peak in different
             places — the separation is capsule-driven, not cosmetic.

QUESTIONS    None. Fork answered.

TRACE        base(floor tom on a kick capsule — Tape Op measured 60 Hz low peak, 4 k and 10 k high
             peaks, 750 Hz down ~15 dB: bottom and stick baked, midrange body absent by design) ·
             equip(no drum size or head notated; the D6 itself IS the equipment story here, and
             Brian's declined fork locks it) ·
             genre(R&B/funk scooped dance-floor floor tom is the intended sound — bend is DON'T
             fight the capsule, no midrange reconstruction) ·
             artist(click + programmed low end in the Track channel makes a 60 Hz-peaking tom a
             real collision risk) ·
             venue(FSQ outdoor: HPF pushed to 80 specifically to trim the capsule's 60 Hz peak off
             the kick/bass lanes, ring cut at FSQ depth −6 @ 300, and 38 % RH dry air kept the
             4 kHz trim at de-stack size rather than deeper)
