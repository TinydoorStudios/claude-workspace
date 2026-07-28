# Unit 10 — Guitar × XLR line feed  (ch 13)

INSTRUMENT   Electric guitar, one channel, arriving as a line-level XLR rather than a mic on a
             cab. In a Cincinnati R&B/funk show band this is a rhythm chair first — chanks,
             skank chords, 16th-note comping, single-coil territory — with occasional lead work.
             The band's repertoire (Motown → Chaka → Bruno Mars) says clean-and-bright far more
             often than it says overdriven.
             **Equipment: not notated.** No modeller model, no amp, no pickup type. Nothing
             invented. But the *format* is a fact: XLR means a modeller or amp DI out, and
             whether it's cab-simulated is the single biggest unknown on this channel.

MIC/DI       XLR line feed. **Locker fork: EXEMPT** — no capsule in front of it, per the
             eligibility gate. No mic to swap, no fork raised, no line in the packet.

SEARCHES     1. `guitar modeler direct XLR live FOH EQ Helix Kemper cab sim EQ live sound R&B
                funk rhythm guitar`
             2. `funk rhythm guitar live EQ settings high pass 150Hz presence 3kHz clean strat
                live sound engineer`
             3. Cross-read of the returned Sound On Sound guitar-styles piece, the Music Guy
                Mixing funk-guitar EQ page and the Line 6 / Two Notes documentation on what a
                cab-sim'd XLR out actually delivers.

CAPSULE FACT There is no capsule — and that *is* the fact that governs this channel. A
             cab-simulated XLR out has a **speaker-cabinet impulse response already baked into
             it**, and that IR includes a mic's response and the cab's own rolloff (a real
             guitar cab is effectively done above ~5 kHz). So a cab-sim'd feed arrives
             pre-voiced like a mic'd cab, and the desk's job is corrective only. A feed with
             cab sim **off** is the opposite: full-bandwidth, buzzy above 5 kHz, and needs the
             LPF the cab would have provided. Same connector, two completely different channels.
             Genre-side quantitative anchor from the research: for clean funk guitar, engineers
             **high-pass at 150 Hz** (Sound On Sound: 150 Hz on both mics for clean funk
             guitar), cut **250–400 Hz** for mud, and find attack at **2–5 kHz**.

WEB SAYS     Funk/R&B rhythm guitar consensus is unusually tight: keep it clean and bright,
             high-pass hard (100–150 Hz) so it stops competing with the bass, cut the 250–400
             mud rather than boosting highs to compensate, and place presence around 2–3 kHz for
             the chank. Single-coil sources need less help up top than humbuckers.

KB SAYS      eq-starting-points, electric guitar: HPF high, cut the box/honk region, keep the
             mids where the instrument's character lives. The KB's guitar rows all assume a
             *mic'd cab* — it has no row for a modeller direct feed, which is the gap below.

VERDICT      **THIN.** The funk-guitar EQ consensus is strong and I'd stand behind it, but the
             KB has no modeller/direct-feed row to cross-check against, and the cab-sim question
             is unanswered — which means I can't yet know whether this channel needs an LPF at
             5 k or none at all. Not something to average past. → **question round**, with the
             LPF written provisionally.

GENRE BEND   R&B/funk rhythm: this channel wants to be *narrow and sharp*. It lives above the
             bass and below the vocals, and its job is rhythmic articulation, not size. That
             argues for a high HPF and a genuinely deep low-mid cut — deeper than a rock guitar
             would get. Artist layer: with keys (ch 23/24), pads and a Track channel all
             occupying midrange, the guitar has to be given a lane rather than left wide.

VENUE BEND   FSQ outdoor: no room gain, and mud at 60 feet is what kills rhythm-guitar
             intelligibility. The 300 Hz cut goes to the outdoor depth without hesitation, and
             the HPF sits at the top of the researched range (150) rather than the bottom.

DRAFT BANDS  *(RESOLVED — Brian: **cab sim is ON**. The provisional +3 @ 3000 is withdrawn and
             the LPF stays at 8 k as housekeeping rather than as a cab replacement.)*
             HPF 150 · LPF 8000
             B4  FLAT                     was +3 @ 3000 — removed, see gate check
             B3  −8 @ 300   Q 2.0  BELL   mud — outdoor depth, clears the bass
             B2  −4 @ 900   Q 2.0  BELL   honk, keeps the vocal path clear
             B1  FLAT                     HPF at 150 owns the bottom

GATE CHECK   **Boost audit — the +3 @ 3000 was written, then removed.** With no capsule there's
             no baked peak to stack on *unless* the feed is cab-simulated — and Brian confirms
             it is. A cab IR carries a speaker and a mic's response, and its presence shaping
             lives right around 2–4 kHz. A +3 at 3 k on top of that is the same error as
             boosting into a baked capsule peak, just one layer further up the chain. **The
             capsule gate applies to impulse responses too**, and this channel is the proof:
             the boost came out on the answer, and the channel is now cuts-only.
             **LPF 8000 resolved.** With cab sim ON the IR already rolls the top off, so the
             8 k filter is belt-and-braces rather than the thing standing in for a missing cab.
             (Had the answer been OFF it would have had to come to ~5 k.)
             **Zero boosts on this channel** — which is the right answer for a finished,
             already-voiced feed sitting in the middle of a crowded midrange.
             **Against the other midrange sources:** guitar cuts 900, keys will sit above it,
             the D6 kick cuts 1200, bass synth boosts 1200. The guitar's +3 at 3 k is clear of
             all of them.

QUESTIONS    1. **Is the guitar's XLR feed cab-simulated?** (modeller/IR out vs a raw amp DI).
                Blocking for the LPF and for whether B4 stays a boost.
             2. KB write-back candidate — add a modeller/direct-feed row to eq-starting-points.
