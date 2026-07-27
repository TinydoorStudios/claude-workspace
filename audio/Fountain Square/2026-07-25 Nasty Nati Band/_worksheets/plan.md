# Plan — Nasty Nati Band, FSQ, 2026-07-25, Rev 2.0 (revised input list)

GENRE (verified, gate passed before any other search):
New Orleans second-line brass band + funk/soul/R&B. Evidence: Cincinnati Symphony community-artists
page, DownBeat review of the band, CincyMusic artist page, The Bash listing. Founded 2012, led by
trumpeter Mike Wade, nine-piece core of brass + saxes + drums. Rev 1.0 processed this as generic
"R&B per Brian, no artist dig" — this rev the artist research actually ran, and it sharpens the read:
second-line brass is the identity, so the HORN SECTION is the lead instrument and gets slotted by lane.

ARTIST PROFILE (refines the genre, outranks it where they differ):
NOLA second-line tradition + HBCU marching-band influence + Earth Wind & Fire / Chuck Brown funk.
Sousaphone walks the bass line; the horn line is dense and loud and plays as a block. Energetic live.
The sheet is the EXPANDED lineup - core brass band plus rhythm section (bass DI+mic, 2 guitars),
hand percussion and a DJ. Seven horns now, up from five in Rev 1.0.

DELTA vs Rev 1.0 (7/23 build) - what the revised sheet changed:
  ch 15/16  Gtr 3 / Gtr 4 (SM57)      -> Percussion 1 / 2 (SM57), stand Tall -> SHORT
  ch 21     Trumpet (PRO 35)          -> Sax 3 (PRO 35)
  ch 22/23  Perc 1 / Perc 2 (SM57)    -> Trumpet 1 / Trumpet 2 (PRO 35)
  ch 24     BT Aux                    -> EMPTY (dropped from the MD; fader 24 keeps template name)
  Guitars drop from 4 to 2. Horn line grows from 5 to 7.

UNIT TABLE (dedupe; within-show reuse from Rev 1.0 is allowed, cross-show caching is not):
  U1  Congas/bongos x SM57      ch 15, 16   FRESH pass this rev (instrument newly confirmed)
  U2  Bari sax x AT PRO 35      ch 21       FRESH pass - genuinely new unit
  U3  Trumpet x AT PRO 35       ch 22, 23   within-show reuse of Rev 1.0's ch 21 research + a
                                            second lane for the 2nd trumpet
  Untouched this rev: kit (1-9), bass (11,12), guitars (13,14), sousa (17), bone (18),
  tenor (19), alto (20), vocals (25-30), DJ (31,32).

QUESTION ROUND (fired, answered before any EQ committed):
  Q1 "Sax 3" on ch 21 - which horn?                    -> BARI SAX
  Q2 ch 15/16 percussion - what is it?                 -> CONGAS / BONGOS
  Q3 PRO 35's 80Hz HPF is a SWITCH, not a fixed
     roll-off. Where does it run on the low horns?     -> SWITCH OUT (flat) on sousa + bari
  All three recorded as decisions. No carried FLAG left open this rev.

CARRIED-FLAG RESOLUTION: Rev 1.0 shipped ch 22/23 as "aux percussion, instrument not confirmed,
conservative, dial at soundcheck." That flag is now CLOSED - congas/bongos confirmed by Brian.

CORRECTION TO REV 1.0 (factual, worth carrying forward): Rev 1.0's mic_notes described the PRO 35
as having an inherent "80Hz rolloff 18dB/oct". It does not - that is a SWITCHED filter on the mic
body (-18 dB @ 80 Hz via switch, RecordingHacks spec page). With the switch OUT the mic is flat to
50 Hz, which is what the sousaphone's +3@90 actually needs. KB write-back proposed.

HORN SECTION LANE MAP (7 horns - each owns a distinct lane, low instrument = low lane):
  Sousa   mud 350   / pitch-definition boost 1.2k
  Bari    mud 300   / honk 600          <- NEW, slots below the tenor
  Tenor   body 350  / honk 800
  Bone    body 500  / bark 1.2k
  Alto    body 400  / honk 1.5k
  Tpt 1   body 500  / bark 2.7k
  Tpt 2   body 450  / bark 3.0k         <- NEW lane, offset off Tpt 1
