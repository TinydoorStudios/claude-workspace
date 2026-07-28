# Unit 11 — Talkback × Shure SM58  (ch 14, "Edwin Talkback")

INSTRUMENT   Bandleader/MD talkback — a named mic on a named person. Not a performance vocal:
             counts, cues, "one more time from the bridge," and possibly stage-to-FOH comms.
             **Where it goes is the open question and it changes everything about this channel.**
             If it feeds the mains, it's a speech channel that needs intelligibility and hard
             feedback control. If it's comms/monitors only, it needs almost nothing and must be
             kept out of the PA and out of the recording. → question round.

MIC          Shure SM58 — cardioid dynamic, no 48V, Tall/boom stand. KB tendency: "cardioid
             vocal dynamic, presence ~4–6 kHz, gentle low rolloff, proximity. Tough, consistent.
             Weakness: muddy if close, limited air, upper-mid spit → tame box ~500 Hz."

SEARCHES     1. `Shure SM58 talkback stage microphone live EQ presence peak frequency response
                spec 100Hz rolloff`
             2. Cross-read of Shure's own SM58 technology page, the SoundGuys measured review and
                the Mixdown review for the response detail.

CAPSULE FACT **50 Hz – 15 kHz**, with a **pronounced low-end rolloff that flattens out at
             100 Hz** (bass attenuated from 40–100 Hz, by design, to control handling and wind
             noise), and a **presence rise running from about 2 kHz to 6 kHz** before rolling
             off above 10 kHz. Shure's stated purpose for that presence rise is speech
             intelligibility — which is precisely this channel's job.

WEB SAYS     The SM58's tailored curve is a speech/vocal curve: the built-in low cut plus the
             2–6 kHz presence lift is the whole design. For a talkback role that's close to
             ideal out of the box — the mic is already doing what a talkback EQ would do.

KB SAYS      As above, plus the specific caution: muddy if worked close, upper-mid spit, box
             around 500 Hz.

VERDICT      **AGREE.** Shure's 2–6 kHz presence region and the KB's "~4–6 kHz" describe the
             same broad rise, and both flag the same low-end/proximity behaviour. Nothing to
             escalate. (Note this is a *different* situation from the SM57 in unit 14, where the
             KB and the measured curve genuinely diverge — here they line up.)

LOCKER       **Silent pass.** The SM58 is the locker's stated handheld for "typical gigs," and a
             talkback mic is the one place on a stage where tough, consistent and unremarkable
             is exactly right. Swapping in something better would be spending a good mic on the
             least critical channel — and it would take a handheld away from the vocal pool.
             No fork.

GENRE BEND   Not applicable in the usual sense — this is speech, not music. The only genre
             consideration is that a show band's MD talkback gets used *between* songs on a loud
             plaza, so it has to be instantly intelligible over crowd noise and have enough
             feedback margin to be pushed.

VENUE BEND   FSQ outdoor: a talkback on a stand in front of wedges with a 10,000-person crowd is
             a feedback channel first and a speech channel second. HPF goes to 150 — well above
             the mic's own 100 Hz flattening point — because nothing below that carries speech
             intelligibility and everything below it carries stage rumble. Box cut at outdoor
             depth. **Mute-by-default**, opened only when needed.

DRAFT BANDS  HPF 150 · LPF 12000
             B4  FLAT
             B3  −7 @ 500   Q 2.0  BELL   the 58's known box — outdoor depth
             B2  −4 @ 250   Q 1.8  BELL   proximity/chest, for a mic that will be eaten
             B1  FLAT

GATE CHECK   **No boosts — and here the reason is the vocals rule, not just the capsule.**
             Vocals are cuts-only in every genre (feedback control, not taste), and a talkback is
             a vocal channel by that rule. Separately, the capsule gate would have blocked the
             obvious move anyway: the instinct on a speech channel is to lift 3–4 kHz for
             intelligibility, and this capsule already rises across **2–6 kHz** by design. The
             intelligibility is in the mic; the desk's job is removing what's in the way.
             **Feedback margin:** this channel and the four wireless vocals are the five open
             mics that determine gain-before-feedback on this stage. Every one of them is
             subtractive-only, which is the whole point.

QUESTIONS    1. **Does ch 14 feed the mains, or is it comms/monitors only?** Changes whether
                this channel needs real EQ or just a clean, muted feed — and whether it should
                be excluded from the multitrack.
