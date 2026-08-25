# Unit 17 — Keys × XLR line feeds (stereo pair) · CH 20, CH 21

INSTRUMENT   Keyboard rig, stereo. On this show the keys are doing **two jobs at once**: the piano
             and organ/Rhodes comping an R&B/Motown set needs, AND — with no horn channels on the
             list — a share of the horn and string lines the band's press sells. Brian confirmed
             that read in the round. Role in THIS mix: harmonic bed plus the arrangement's
             "orchestra", sitting between the guitar and the vocals.
             Renumbered from rev 1's faders 23/24 to 20/21; same source type.

MIC          Neither — XLR line feeds from the keyboard rig. **EXEMPT from the locker fork**
             (line level, no capsule).

SEARCHES     1. `keyboard rig stereo XLR line feed live sound FOH EQ Rhodes organ piano 300Hz mud
                horn parts` 
             2. `keys live mix EQ leave 1-2kHz alone horn line masking vocal presence region`

CAPSULE FACT (equipment fact) A keyboard's stereo XLR out is a **finished line-level signal whose
             voicing was chosen at the instrument** — patch selection, onboard EQ and effects are
             all upstream, and a Rhodes/organ/piano patch already carries its own presence and
             brightness shaping. There is no transducer to correct. The single reliable FOH problem
             is 250–400 Hz accumulation, because a full-range keyboard patch overlaps guitar, bass
             and the sampling pad in that octave.

WEB SAYS     The consistent position for keys at FOH is subtractive and narrow: clear the mud, do
             not add presence, and protect the vocal's intelligibility band because a stereo
             keyboard bed is the widest, most continuous thing in the mix and will mask a vocal
             before any drum does.

KB SAYS      `eq-starting-points` covers acoustic piano but has no row for a keyboard rig's
             line-level stereo feed carrying substitute horn parts. Nothing contradicts the web
             read.

VERDICT      **AGREE on the web side, KB partially silent.** No conflict to resolve. This channel's
             defining constraint comes from the artist layer rather than from either source — see
             below.

LOCKER       **Exempt** — line feeds.

GENRE BEND   R&B/Motown/funk: warm Rhodes and organ, bright acoustic piano stabs, and horn-section
             lines. **The load-bearing decision on this channel is a REFUSED CUT rather than an
             applied one:** the 1–2 kHz window is left completely untouched, because that is where
             the substitute horn and string lines live. On a normal show that window is a prime
             candidate for a cut to protect vocal intelligibility; here, cutting it would gut the
             arrangement's brass. Artist layer explicitly outranks the generic genre read: no horn
             channels on the list means keys + pads + Track are the horn section, confirmed in the
             round.

VENUE BEND   FSQ outdoor: the mud cut at 300 Hz gets real FSQ depth (−6), and the low-mid honk cut
             at 800 Hz keeps the keys from stacking onto the guitar's own 800 Hz honk cut region —
             both instruments occupy that band and on a plaza only one can. HPF **60**: a piano
             patch's low register is musical and the KS21 arch reproduces it, but everything below
             60 belongs to the kick and bass. Weather layer: **no change** — the top of a
             line-level keyboard feed is whatever patch was chosen, and with the 1–2 kHz window
             protected and no presence boost permitted there is nothing for the dry-air read to act
             on.

DRAFT BANDS  **CH 20 — Key L** and **CH 21 — Key R**, identical (a stereo pair):
             HPF 60 · LPF OFF
             B4  FLAT
             B3  −4 | 800 | 2.0 | BELL
             B2  −6 | 300 | 1.8 | BELL
             B1  FLAT

GATE CHECK   **No boosts on either channel — nothing to permit.**
             - **No presence boost.** The patch's brightness was chosen at the instrument; lifting
               presence at the desk stacks on it and walks straight into the four vocals'
               intelligibility band.
             - **No cut in the 1–2 kHz window** — the deliberate omission described above. This is
               the artist layer overriding a move the genre and venue layers would both otherwise
               call for.
             - B3 −4 @ 800 is kept modest on purpose: the guitar (ch 13) already takes −5 at 800 for
               the 1960 4×12's honk, and both channels cutting hard at the same frequency would dig
               a hole in the band where the comping interlocks.
             - **Identical L/R values are CORRECT, not a sectional-rule failure** — this is one
               instrument's stereo image, and differing curves would smear it. The sectional rule
               applies to competing members of a section (the three toms, three cymbal mics, four
               vocals), not to the two sides of one source.

QUESTIONS    None. The no-horns read was confirmed in the round ("what's on the list is what there
             is").

TRACE        base(stereo keyboard line feed — 250–400 Hz accumulation is the only reliable FOH
             problem; no transducer to correct) ·
             equip(keyboard rig XLR out, patch voicing chosen upstream — forbids a presence boost) ·
             genre(R&B/Motown Rhodes, organ and piano — warm and subtractive) ·
             artist(NO horn channels: keys + pads + Track ARE the horn section, so the 1–2 kHz
             window is left untouched — this layer overrides the cut the genre and venue would
             otherwise want, and it is the most consequential call on the channel) ·
             venue(FSQ outdoor: mud deepened to −6 @ 300, honk held to −4 @ 800 so it doesn't stack
             with the guitar's cut at the same frequency, HPF 60 to protect the kick/bass lanes;
             dry air = no change)
