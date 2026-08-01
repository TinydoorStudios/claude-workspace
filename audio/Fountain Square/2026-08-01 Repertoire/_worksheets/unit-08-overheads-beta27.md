# Unit 08 — Overheads × Shure Beta 27 pair, STEREO  (ch 9)

INSTRUMENT   Drum overheads. In R&B/neo-soul these are cymbal wash and kit glue — the close
             mics do the work, the OH pair supplies air and the sense of one instrument.
             **STEREO on fader 9** — both mics, one fader. The submitted sheet had OH Left on 9
             and OH Right on 10; ch 10 at FSQ is the SNARE PL8 plate return and is
             hard-protected in the patcher, so the pair was moved onto 9 as a stereo input.
MIC          Shure Beta 27 ×2. Supercardioid side-address LDC, 48V. Three-position low-frequency
             rolloff switch and a −15 dB pad — **both ASSUMED FLAT/OUT**; fallbacks in mic_notes.
             KB tendency: "ease off box, honk; tame harsh ~9000Hz."
SEARCHES     "Shure Beta 27 overheads drum frequency response peaks 5.5kHz 9kHz supercardioid pad low cut"
             → recordinghacks.com/microphones/Shure/Beta-27, bhphotovideo.com Beta 27 listing,
               all-geared-up.com/reviews/shure-beta27/
CAPSULE FACT **Nominally flat from ~60 Hz to 3 kHz, with two small HF peaks of +2 dB or less at
             5500 Hz and 9 kHz.** Supercardioid pattern is extremely consistent below 6400 Hz
             with no widening toward omni at low frequencies. Three-position LF rolloff, −15 dB pad.
             Source: RecordingHacks Shure Beta 27.
WEB SAYS     Achieves its supercardioid response through an acoustic resistance network behind
             the capsule; explicitly listed for drum overheads, amps and piano. The pattern
             consistency is the reason to pick it over a flatter cardioid on a loud stage.
KB SAYS      mic-library: "Supercardioid LDC, flat 60Hz-3kHz, small peaks +2dB at 5.5k and 9k,
             -15dB pad, flatter than SM57. Open, clean cab/instrument mic. Weakness: slight 9k
             fizz on bright amps." Identical figures.
VERDICT      **AGREE** — both sides give the same two +2 dB peaks at the same two frequencies
             and the same pattern behaviour.
LOCKER       **FORK RAISED** — Beta 27 pair vs sE sE8 matched pair (V Pack Arena). The Beta 27
             is not the locker's first call for overheads (mic-library's OH pairs are the
             SR20sp, the sE8, the M1280B and the SR25), so the fork is warranted. See the card
             in the question round. Recommendation: keep the Beta 27 pair.
GENRE BEND   R&B: wash and glue, never a drum-kit picture. Cymbals stay behind the vocal.
VENUE BEND   **This is the most venue-driven channel on the show.** Gusts of 22–28 mph through
             the first three hours, on the pair of mics standing highest and most exposed on the
             stage → HPF 400, a third higher than the 300 the 2nd Wind build used five days
             earlier, because that night's gusts were half these. At 96% RH both baked +2 dB
             peaks arrive across the plaza with essentially no air absorption, so both get cut.
             Rain probability 73–81% makes this the pair most exposed to blowing rain — an
             operational flag, not an EQ one.
DRAFT BANDS  HPF 400 · LPF 16000
             B4  −5 | 9000 | 2 | BELL
             B3  −4 | 5500 | 2 | BELL
             B2  −6 | 800  | 2 | BELL
             B1  FLAT
GATE CHECK   **No boosts.** Both HF bands are trims sitting exactly on the capsule's two baked
             peaks — 9000 and 5500 — which is the capsule gate working as intended: the two
             frequencies an overhead EQ would normally reach for are the two the Beta 27 already
             supplies, so the desk subtracts. B2 −6 @ 800 is cymbal honk and snare-bleed body,
             below the flat region's top and above the HPF.
             Stereo channel: both mics run one identical EQ by definition — no lane split
             applies, and no left/right divergence is written.
QUESTIONS    1. Locker fork (see round).
             2. LF rolloff switch and −15 dB pad positions at load-in — build assumes flat/out.
                If the LF rolloff is engaged, drop the desk HPF to 150 so they do not compound.
             3. Rain cover for a flown/stand-mounted condenser pair at 73–81% rain probability.
TRACE        base(Beta 27 — flat 60 Hz–3 kHz, +2 dB peaks at 5500 and 9000, RecordingHacks) ·
             equip(cymbals unknown, no rider — generic carries) ·
             genre(R&B — wash and glue, cymbals sit behind the vocal) ·
             artist(no change) ·
             venue(FSQ — HPF 400 driven by 28 mph gusts, up from the 300 used on a half-wind
             night; 96% RH turns both baked +2 dB peaks into cuts; rain risk flagged operationally)
