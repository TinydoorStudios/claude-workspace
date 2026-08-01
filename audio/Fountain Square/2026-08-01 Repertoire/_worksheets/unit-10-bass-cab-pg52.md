# Unit 10 — Bass cab × Shure PG52  (ch 12)

*Brian's instruction 2026-07-30: "its a Shure PG52. deep search this and add it to the locker."
Research below is also the source for the mic-library / mic_data write-up.*

INSTRUMENT   Bass amp cabinet. Rig unknown (no rider). Role: the cab's push and the amp's
             character under the DI's note definition.
MIC          **Shure PG52** — cardioid dynamic kick mic, the pre-PG-ALTA generation.
             Discontinued; superseded by the PGA52. Not previously in the locker.
SEARCHES     "Shure PG52 kick drum microphone frequency response specifications PG Alta cardioid"
             → recordinghacks.com/microphones/Shure/PG52, Shure PG52 Product Specifications PDF
               (©2008 Shure Incorporated) — **fetched and read directly**
             "Shure PG52 review vs Beta 52 sound character bass cab gearspace"
             → gearspace.com/board/low-end-theory/284391-shure-pg52.html,
               homerecording.com "Shure PG52 vs. Beta 52",
               talkbass.com "Shure PG-52 for miking bass amp?"
CAPSULE FACT **Frequency response 30 Hz–13,000 Hz; output impedance 300 Ω; sensitivity
             −55 dBV/Pa (1.8 mV) at 1 kHz; dynamic moving coil with a neodymium magnet;
             internal shock mount; 470 g.** The published curve shows a **low hump around
             60–100 Hz, a broad midrange dip through roughly 200–800 Hz, a presence rise around
             4–5 kHz, and a hard rolloff above ~10 kHz.**
             Source: Shure PG52 Product Specifications, ©2008 Shure Incorporated (read from the
             spec sheet PDF, including the printed response and polar plots).
WEB SAYS     Two findings that matter, and they point the same way.
             (1) Character versus its expensive sibling: "the PG52 doesn't sound as detailed and
             open as the Beta 52… in no way an adequate replacement." (HomeRecording, Gearspace)
             (2) **But the forum consensus names bass cabinets as the one place it excels** —
             "the PG52 finds its place on bass cabinets, where you can get fantastic results
             with it," and independently "it appears to hump around 80 Hz, and then roll off
             fairly rapidly down to 30 Hz." (Gearspace "Shure Pg52"; HomeRecording; TalkBass
             "Shure PG-52 for miking bass amp?")
             Which is to say: whoever specced this put the mic on the exact source its own user
             base rates it for. That is worth recording rather than second-guessing.
KB SAYS      **No KB row exists** — this mic is new to the locker as of this session.
VERDICT      **THIN** — solid, multi-source, manufacturer-anchored research, but zero KB history
             and no prior Brian-verified show with this mic. Values built conservatively and the
             KB write-back proposed below.
LOCKER       No fork raised, and the reason is not a technicality: the alternative would have to
             beat a mic the community specifically rates for bass cabs, and the two locker mics
             that could — the Beta 52 and the MD 421-U — are respectively **already committed to
             ch 2 (Kick Out)** and carrying a 200–400 Hz bloat this outdoor build is trying to
             avoid. An alternative has to be free to be offered, and the stronger one is not.
GENRE BEND   R&B bass is round and warm. The mic's own broad 200–800 dip is doing genre-correct
             work for free — this is a case where the capsule's voicing and the genre agree.
VENUE BEND   FSQ: HPF 50. LPF 6000 — the capsule rolls off hard above 10 kHz anyway and there is
             no reason to carry cab hiss and stage bleed across an open plaza.
DRAFT BANDS  HPF 50 · LPF 6000
             B4  −4 | 4500 | 2   | BELL
             B3  −5 | 900  | 2   | BELL
             B2  −5 | 160  | 1.8 | BELL
             B1  FLAT
GATE CHECK   **No boosts on this channel, and two of the four bands were placed by the gate:**
             · B4 −4 @ 4500 sits **on** the capsule's baked presence rise. A boost there would
               stack on it; the correct move is the trim, and the DI owns definition anyway.
             · B1 is **FLAT because the capsule already humps at 60–100 Hz.** This channel owns
               the cab-thump lane by *letting that hump through*, not by boosting it — boosting
               a baked hump is exactly the stack this gate forbids.
             · B3 −5 @ 900 is the lane split: 800 Hz is unit 09's boost, so the cab mic is
               trimmed just above it rather than fighting for the same band.
             · B2 sits at 160 Hz — the shoulder between the baked hump and the baked dip.
               Deliberately **not** at 250, which would be cutting into a scoop the capsule
               already provides and would hollow the cab out.
QUESTIONS    RESOLVED 2026-07-30 — Brian: "PG52 is mine." His own unit, not band-provided.
             Added to mic-library, mic_inventory (xlsx + csv), the CLAUDE.md shorthand table and
             both ShowBuilder/Patchbay mic knowledge files.
KB WRITEBACK Proposed new mic-library row (Dynamics + Mic Character), pending Brian's go:
             *Shure PG52 — cardioid dynamic, 30 Hz–13 kHz, 300 Ω, −55 dBV/Pa, neodymium,
             internal shock mount, 470 g. Discontinued (superseded by PGA52). Low hump 60–100 Hz,
             broad dip 200–800 Hz, presence rise 4–5 kHz, hard rolloff above 10 kHz. Sold as a
             kick mic; the community rates it a class above its price specifically on BASS
             CABINETS and floor toms, and a class below a Beta 52 on kick. Weakness: less
             detailed and open than a Beta 52; lacks snap on toms.
             EQ tendency: ease off presence ~4500; never boost the 60–100 hump; do not cut into
             the 200–800 dip.*
TRACE        base(PG52 — 30 Hz–13 kHz, 60–100 hump, 200–800 dip, 4–5k rise, Shure ©2008 spec
             sheet + Gearspace/HomeRecording/TalkBass) ·
             equip(bass rig unknown, no rider — nothing invented) ·
             genre(R&B — round and warm; the capsule's own 200–800 dip agrees, so no extra cut
             there) · artist(no change) ·
             venue(FSQ — HPF 50, LPF 6000 to keep cab hiss and stage bleed off an open plaza)
