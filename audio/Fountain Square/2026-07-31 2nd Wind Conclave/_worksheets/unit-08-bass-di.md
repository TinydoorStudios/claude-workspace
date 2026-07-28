# Unit 08 — Bass guitar × DI  (ch 11)

INSTRUMENT   Electric bass, direct. In a Cincinnati R&B/funk show band this is the most
             important instrument on stage after the vocals — it carries the groove and, on a
             dance floor, most of the felt energy. Expect fingerstyle *and* slap across a set
             that runs Motown through Bruno Mars.
             Equipment: **nothing notated** — no amp/cab, no string type, no 4- vs 5-string. The
             generic electric-bass baseline carries and nothing is invented. If the band turns
             up with a 5-string, the HPF is the number to revisit at soundcheck.

MIC/DI       "DI" on the input list. **Specifying the Neve RNDI** — active transformer DI, 48V,
             the locker's designated bass/hi-Z box. KB tendency: "smooth musical top, gentle
             harmonic warmth, full lows. Weakness: very slight HF softening vs a clean DI →
             ease off presence."
             **Locker fork: EXEMPT.** DI input, no capsule — per the eligibility gate this input
             raises no fork and gets no line in the packet about one.

SEARCHES     1. `bass guitar DI live sound EQ R&B funk outdoor 80Hz 250Hz cut 800Hz definition
                prosoundweb`
             2. Cross-read of the returned TalkBass thread, Gear4Music and the stage-focused
                bass EQ write-ups for the live/funk consensus.

CAPSULE FACT DI-side (RNDI, per the KB's verified entry): an active **transformer** front end —
             the colour is harmonic warmth plus a slight softening of the extreme top, not a
             frequency peak. There is no baked peak to gate against on this input, which is
             precisely why a DI takes the instrument template straight where a mic would not.
             Instrument-side quantitative anchor: a 4-string bass's open E fundamental is
             **41 Hz** (CLAUDE.md frequency reference), so everything below ~40 Hz on this
             channel is noise, not note.

WEB SAYS     Strong live consensus for funk/slap bass, consistent across sources: put the punch
             at **80–100 Hz**, **scoop 300–500 Hz** to open space for the pop, lift **1–3 kHz**
             for slap and pop articulation, and **700 Hz–1 kHz is the pluck/attack band**.
             Mud rolls off around 250–300 Hz. The recurring live warning is that boosting below
             80 Hz buys nothing on a PA and eats headroom.

KB SAYS      eq-starting-points, bass DI: conservative subtractive shaping, mud out of the
             low-mids, definition found rather than boosted. mic-library on the RNDI: full lows
             and a musical top, so the DI is not the problem — the instrument and the room are.

VERDICT      **AGREE.** The forum consensus and the KB point the same direction: cut the
             300–500 mud, find definition in the 700 Hz–1 kHz pluck region, keep the fundamental
             tight rather than big. No conflict to escalate.

GENRE BEND   R&B/funk, and specifically a **slap-capable** set — that's the bend. The 300–500
             scoop is deeper here than it would be for a rock or country bass, because the pop
             needs the room. Artist layer: this band plays to a click with a **Bass Synth on
             ch 12** alongside the electric bass. Two bass sources in one octave is the single
             biggest collision risk on this input list, so ch 11 gets slotted deliberately —
             see the de-stack note below.

VENUE BEND   FSQ: 8× KS21 per side in a delayed arch means the PA reaches lower than the
             instrument needs to. HPF at 45 keeps the open E intact (41 Hz) while cutting
             everything beneath it. No room gain means the mud cut goes to outdoor depth — and
             on a plaza, low-mid mud is what turns a bass line into a rumble at 60 feet.

DRAFT BANDS  HPF 45 · LPF 12000
             B4  +3 @ 2500  Q 1.5  BELL   slap/pop articulation
             B3  −8 @ 400   Q 2.0  BELL   the funk scoop, at outdoor depth
             B2  +3 @ 800   Q 1.8  BELL   pluck definition — how the line reads at distance
             B1  +3 @ 100   Q 1.2  BELL   punch, slotted above the kick (see unit 09 slot map)

GATE CHECK   **Boost audit.** A DI has no capsule and no baked peaks, so the capsule gate has
             nothing to catch here — but the *source* gate still applies, and it's the kick:
             · B1 +3 @ 100 sits deliberately **above the D6's baked 60 Hz peak** (unit 02).
               Kick owns 60, bass owns 100. Neither is boosted in the other's slot, and the
               toms' gated bodies sit at 85 / 110 / 130 around it (unit 09 slot map).
             · B4 +3 @ 2500 and B2 +3 @ 800 both sit in regions the ch 1/2 kick channels are
               either cutting (−4 @ 1200 on the D6) or not touching, so the bass's definition
               has clear air.
             · Three +3 boosts on one channel is the most any channel in this show gets, and
               it's justified: this is the only source here with no capsule voicing doing part
               of the work.
             **Two-bass de-stack (ch 11 vs ch 12):** ch 11 owns the **fundamental and the pluck**
             (95 Hz punch, 800 Hz definition). Ch 12 is HPF'd higher and shaped to sit above it
             — full detail in unit 09.

QUESTIONS    None blocking. One note for the round: no bass equipment was notated, so if a
             5-string shows up the HPF at 45 needs to come down to ~35 for the low B.
