# Unit 04 — Drum Pad × passive DI, mono  (ch 4)

INSTRUMENT   Electronic sampling/percussion pad, played by the drummer. Model **unknown**
             (Brian: "unknown what pad it is"), mono, through a DI. Class-standard for this
             role is a Roland SPD-SX or SPD-SX Pro. Content assumed to be claps, snaps,
             sub/808-class hits and FX — an R&B/hip-hop covers set is exactly where 808s live.
MIC          None — line-level pad output into a passive DI. **Locker fork EXEMPT** (DI, no
             capsule).
SEARCHES     "Roland SPD-SX sampling pad live FOH DI EQ HPF 808 samples R&B band mixing"
             → roland.com/us/products/spd-sx/, roland.com/us/products/spd-sx_pro/,
               equipboard.com/items/roland-spd-sx-sampling-pad
CAPSULE FACT No capsule. Device fact instead: **the SPD-SX class outputs MASTER OUT L/MONO + R
             at line level with onboard master EQ and 21 master effects** — so what arrives at
             the DI is already a produced, EQ'd stereo bus, and taking L/MONO gives a proper
             mono sum rather than half the image.
             Source: Roland SPD-SX product page (roland.com).
WEB SAYS     Two practical consequences from the device docs: (1) the pad has its own master EQ
             and effects, so anything the desk does is on top of a mix the drummer already made;
             (2) the correct mono take is the L/MONO jack alone — Y-cabling L+R into one DI is
             the common field mistake and can partially cancel stereo-processed samples.
KB SAYS      **No KB row exists** for a sampling pad or for backing-track-class playback — the
             same gap flagged on the 2026-07-27 2nd Wind build and still unfilled.
             Nearest analogue: the DI rows ("apply template as-is").
VERDICT      **THIN** — device documentation is solid, but there is no KB entry and no
             confirmation of what this specific pad is loaded with. Values are built to be
             safe in either direction and flagged for load-in.
LOCKER       Exempt — DI input.
GENRE BEND   R&B/neo-soul with hip-hop leanings: the pad is very likely carrying the sub. That
             is the single most consequential unknown on this build, because it decides whether
             the acoustic kick or the pad owns 50–80 Hz.
VENUE BEND   FSQ: the KS21 arch will reproduce a real 808 fully and loudly with no room to hide
             it. HPF 60 is the hedge — it keeps a genuine 808 fundamental audible from 60 Hz up
             while refusing to hand the pad the same 50–80 Hz the kick already owns. If the pad
             turns out to be claps-only, this HPF should come UP, not down.
DRAFT BANDS  HPF 60 · LPF 18000
             B4  −3 | 9000 | 2 | BELL
             B3  −5 | 2500 | 2 | BELL
             B2  −6 | 300  | 2 | BELL
             B1  FLAT
GATE CHECK   **No boosts.** Nothing is boosted on a source that arrives pre-produced — the
             samples were mastered by someone else and the pad has its own EQ stage. The −3 @
             9000 is a venue move, not a capsule move: at 96% RH the sample hats and clap tails
             arrive with no air absorption at all, which is exactly when pre-hyped samples turn
             sizzly across a plaza.
             Cross-channel: this channel and ch 2 (Kick Out) **split** the bottom — pad HPF'd at
             60, kick given the only low boost on the show at +3 @ 55. They do not stack.
QUESTIONS    1. What is the pad, and does it carry 808/sub content? If yes: drop this HPF to 30
                and pull ch 2's B1 +3 @ 55 back to FLAT — the pad becomes the sub.
                If it is claps and FX only: raise this HPF to 120 and leave ch 2 alone.
             2. Confirm the pad is patched from L/MONO, not a Y of L+R.
TRACE        base(sampling pad through a passive DI — line-level, pre-produced stereo bus,
             Roland SPD-SX docs) · equip(pad model unknown — no invented behaviour; both
             outcomes written as a one-line change) · genre(R&B/hip-hop — 808 content assumed
             present, drives the kick/pad split) · artist(no change) ·
             venue(FSQ + KS21 arch + 96% RH — HPF 60 as the hedge, −3 @ 9000 because saturated
             air delivers sample HF intact)
