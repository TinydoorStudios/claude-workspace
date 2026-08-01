# Unit 12 — Keys × Whirlwind IMP  (ch 17 Key 1, ch 18 Key 2)

INSTRUMENT   **Two separate keyboards, two separate players** (Brian, 2026-07-30). Boards
             unknown. With no horns and no percussion in this band, the two keys carry all the
             harmonic colour — which makes their separation from each other, and from the
             vocal, the main arrangement problem on this show.
             R&B/neo-soul convention for a two-keys band: one board covers piano/Rhodes/Wurli,
             the other covers organ, pads and synth. Assumed, and flagged.
MIC          None — **Whirlwind IMP passive DI ×2. Locker fork EXEMPT.**
SEARCHES     "Whirlwind IMP 2 passive DI bass guitar tone transformer high frequency loss review live"
             → sweetwater.com IMP 2, fullcompass.com IMP2 TRHL, bhphotovideo.com IMP 2
             "live sound mixing neo-soul R&B vocal EQ approach warm not bright low mid 250Hz keys guitar carve"
             → rysupaudio.com "How to Mix R&B Vocals", musicngear.com neo-soul/funk techniques,
               sweetwater.com/insync/essential-eq-tips-for-live-sound/,
               stealifysounds.com neo-soul production
CAPSULE FACT No capsule. Device fact: **20 Hz–20 kHz ±1 dB, 133:1 impedance ratio, −20 dB level
             change, TRHL transformer, passive.** Source: Whirlwind IMP 2 published specification
             via Sweetwater / Full Compass.
             Genre fact, since the DI adds nothing: **"keys and guitars operate across different
             frequency ranges — 125 Hz produces boom/thump/warmth, 250 Hz fullness, 500 Hz honk,
             1 kHz whack. Careful carving between these instruments and vocals will prevent
             muddiness while maintaining warmth."** Source: Sweetwater InSync, "8 Essential EQ
             Tips for Live Sound."
WEB SAYS     The genre sources are unusually consistent and unusually relevant here: for
             R&B/neo-soul, "the warmth in the low-mids is a feature, not a problem," and
             "over-cutting the low end will cause you to lose that warm, chesty tone." Guidance
             is to cut 200–600 Hz *delicately*. That is a direct, named tension with the FSQ
             outdoor rule (−6 to −9 typical, up to −10 on mud) and is reconciled below.
KB SAYS      mic-library DI row: "Passive DI, neutral/honest, reliable. Bass/keys direct."
             Tendency: "apply template as-is (flat/honest)."
VERDICT      **AGREE** on the DI (flat from both sides, nothing to compensate).
             **THIN** on the source — there is no KB row for a keyboard/line-level board at all,
             the same gap logged on the 2026-07-27 build. Flagged, not papered over.
LOCKER       Exempt — DI inputs, both channels.
GENRE BEND   This is the channel pair where the genre pushes back hardest against the venue
             default, so the reconciliation is stated rather than assumed: **the FSQ deep-cut
             rule exists to fight mud, and outdoors that mud is mechanical — boxiness, stage
             bleed, cab resonance. It is not room buildup, because an open plaza has none.**
             A Rhodes' 250 Hz warmth is not mud; it is the sound the genre is made of. So the
             keys' low-mid cuts run −5 and −6 rather than the −8 the venue reflex would give,
             and the depth that the venue rule wants is spent instead on drums and the guitar
             cab, where the problem really is mechanical. That trade is deliberate.
VENUE BEND   HPF 60 / 80 for gusts and stage rumble. At 96% RH the electric-piano bell top and
             any synth pad's HF arrive intact, so both channels trim the top rather than lift it.
             **Sectional slotting: the two boards share no value in any band.**
DRAFT BANDS  **Ch 17 — Key 1** (assumed piano/Rhodes)   HPF 60 · LPF 16000
             B4  −3 | 8000 | 2 | BELL
             B3  −4 | 1200 | 2 | BELL
             B2  −5 | 300  | 2 | BELL
             B1  FLAT

             **Ch 18 — Key 2** (assumed organ/pads/synth)   HPF 80 · LPF 16000
             B4  −3 | 6500 | 2 | BELL
             B3  −4 | 1800 | 2 | BELL
             B2  −5 | 450  | 2 | BELL
             B1  FLAT
GATE CHECK   **No boosts on either channel.** Nothing is baked into a ±1 dB flat passive DI, so
             the gate does not forbid a boost here — the reason there is none is that both
             boards arrive already voiced by the player, and in a band with no horns and no
             percussion the risk is two keyboards crowding each other and the vocal, not either
             one being too small. Every move is separation.
             Sectional check, ch 17 vs ch 18: HPF 60/80, B4 8000/6500, B3 1200/1800, B2 300/450.
             No shared frequency, no shared depth.
             Vocal lane: both B3 carves (1200 and 1800) sit **around** the lead vocal's cut at
             4000 and below the BGs at 3500/4500, so the keys clear the vocal band from
             underneath rather than colliding with it.
QUESTIONS    1. Which board is which? The assignment above is a convention, not a fact. If Key 2
                is the piano and Key 1 the organ, swap the two curves wholesale.
             2. Are either of these stereo rigs being summed to one mono DI? If so, check it is
                the board's own mono/L-mono output and not a Y-cable.
TRACE        base(Whirlwind IMP — passive, 20 Hz–20 kHz ±1 dB, Whirlwind spec; source itself has
             no KB row — THIN) · equip(boards unknown, no rider — assignment stated as a
             convention, not invented as a fact) ·
             genre(**R&B/neo-soul — low-mid warmth is a feature; cuts held to −5 instead of the
             venue's −8**, rysupaudio/musicngear/Sweetwater InSync) ·
             artist(no change) ·
             venue(FSQ — HPF 60/80 for gusts; deep-cut budget deliberately spent on drums and
             cab instead of here; 96% RH turns both top bands into trims)
