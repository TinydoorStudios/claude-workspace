# Unit 13 — Vocals × Shure Beta 58A, house wireless  (ch 33 Brittany, 34 BG 1, 35 BG 2)

INSTRUMENT   Three vocals. **Ch 33 Brittany Marie — lead**, and the show. Ch 34 / 35 — two
             backing vocalists. Wireless 4 (fader 36) unused.
             Artist evidence: Brittany Marie entered Cincinnati's School for Creative and
             Performing Arts at eight; trained in jazz, classical and contemporary, plus **two
             years with the Cincinnati Opera**; describes her own music as R&B/neo-soul that
             "dabbles in the hip hop/rap arena." (CincyMusic; msmarie513.com.) That training is
             the useful fact: a supported, projecting instrument with real dynamic range and
             controlled vibrato — not a breathy close-mic pop delivery. She will work the mic at
             distance on the big notes.
MIC          Shure Beta 58A capsules on the FSQ house wireless — faders 33/34/35 per the
             template. **Locker fork EXEMPT** (house wireless, XLR/RF line feed, no capsule
             choice to make).
             KB tendency: "ease off presence; tame box ~600Hz."
SEARCHES     "Shure Beta 58A live vocal EQ R&B female soul frequency response presence peak 4kHz 10kHz proximity"
             → shure.com/en-US/products/microphones/beta_58a,
               musiconstage.com.au Beta 58A complete technical analysis 2026,
               soundref.com Beta 58A review, higherhertz.com Beta 58A
             "live sound mixing neo-soul R&B vocal EQ approach warm not bright low mid 250Hz keys guitar carve"
             → rysupaudio.com "How to Mix R&B Vocals", virtuosocentral.com live vocal EQ,
               musicguymixing.com warm vocal EQ
CAPSULE FACT **50 Hz–16 kHz with two presence peaks at ~4 kHz and ~10 kHz, and a gradually
             falling bass response below 500 Hz to control proximity.** Supercardioid.
             Source: Shure USA Beta 58A + Music On Stage "Beta 58A Complete Technical Analysis
             2026."
WEB SAYS     The two peaks are "significantly more aggressive than the SM58's gentler presence
             lift" and are what makes it cut — and also what makes it strident. Users
             specifically report moving to it from an SM58 for female vocals, for presence
             without losing feedback margin.
             Genre guidance runs the other way and matters more here: R&B/neo-soul vocals want
             warmth and texture, "the breathy moments between words matter as much as the
             words," and for an over-bright vocal the recommended move is a small **dynamic** cut
             around 3.5 kHz to shift the whole vocal warmer.
KB SAYS      mic-library: "Supercardioid vocal dynamic, 50Hz-16kHz, <500Hz attenuated for
             proximity control, TWO presence peaks (~4kHz and ~10kHz) — brighter/more bite than
             SM58, tighter pattern, more gain-before-feedback. Weakness: those peaks can get
             strident/sibilant." Identical.
VERDICT      **AGREE** — same two peaks, same frequencies, same sub-500 Hz proximity roll, same
             stridency warning from both sides.
LOCKER       Exempt — house wireless.
GENRE BEND   Neo-soul is the reason the box cuts here run **lighter** than the FSQ reflex. The
             genre sources are explicit that over-cutting the low-mids costs the "warm, chesty
             tone," and Brittany's opera-trained chest register is the single most valuable
             thing in this mix. So 550/650/750 Hz at −5 and −6, not −8.
             Both baked presence peaks come down rather than being left, which is the same
             conclusion the genre guidance reaches independently ("tame that sound with a small
             dynamic cut to shift the vocal warmer").
VENUE BEND   **The template HPF is the trap.** FSQ's wireless faders ship a baseline HPF of
             184 Hz. A female R&B lead sings down to roughly F3–G3 (175–196 Hz), so 184 Hz would
             sit on top of her lowest fundamentals — the same class of error caught on the
             2026-07-27 build with a male bass voice. Ch 33 is set to **120 Hz**, below her range
             with margin, and still high enough to handle gusts on a supercardioid handheld held
             close. The two BGs go higher (140 / 150) because they sing above her and gain-
             before-feedback is worth more on those channels than low extension.
             96% RH: the 10 kHz peak arrives with essentially no air absorption, so all three
             de-essers are **dynamic** — a static value set at 6 pm would be wrong by 11 as the
             humidity climbs from 93% to 99%.
DRAFT BANDS  **Ch 33 — Brittany (lead)**   HPF 120 · LPF 16000
             B4  −3 | 10000 | 2   | BELL | DEQ thr=−18 atk=3ms rel=80ms
             B3  −2 | 4000  | 1.8 | BELL
             B2  −5 | 550   | 2   | BELL
             B1  FLAT

             **Ch 34 — BG 1**   HPF 140 · LPF 16000
             B4  −3 | 9500 | 2   | BELL | DEQ thr=−18 atk=3ms rel=80ms
             B3  −3 | 3500 | 1.8 | BELL
             B2  −6 | 650  | 2   | BELL
             B1  FLAT

             **Ch 35 — BG 2**   HPF 150 · LPF 16000
             B4  −3 | 9000 | 2   | BELL | DEQ thr=−18 atk=3ms rel=80ms
             B3  −3 | 4500 | 1.8 | BELL
             B2  −6 | 750  | 2   | BELL
             B1  FLAT
GATE CHECK   **Cuts only, all three channels — the standing rule, no exceptions, no boosts to
             justify.** Both HF bands on every channel sit on or beside the capsule's two baked
             peaks (4 kHz and 10 kHz), so every move is a trim of something the mic already
             supplies.
             Sectional slotting: **no two of the three share a single value in any band** —
             HPF 120/140/150, B4 10000/9500/9000, B3 4000/3500/4500, B2 550/650/750.
             Lead-over-BG separation is deliberate and visible: the BGs are cut **deeper** in
             the 3.5–4.5 kHz presence region (−3) than the lead (−2), and deeper in the box
             (−6 vs −5), so Brittany sits above them without her channel being boosted.
QUESTIONS    1. Voice types for BG 1 and BG 2 — the build assumes both sing above the lead,
                which is the norm for this act's format. A male BG would move that channel's
                HPF down to ~90 and its B2 down toward 450.
             2. These channels override the FSQ template's wireless baseline curve — the 184 Hz
                HPF and its feedback notch go away on all three. Confirm that is wanted.
TRACE        base(Beta 58A — baked peaks at 4 kHz and 10 kHz, sub-500 Hz proximity roll,
             Shure/Music On Stage) · equip(house wireless, no capsule choice — exempt) ·
             genre(**neo-soul — low-mid warmth protected, box cuts held to −5/−6 instead of the
             venue's −8**; both baked peaks trimmed to shift the vocal warmer) ·
             artist(**Brittany Marie, SCPA + two years Cincinnati Opera — a supported projecting
             voice, so HPF 120 protects her chest register and the 4 kHz cut stays light at −2
             because she does not need help cutting**) ·
             venue(FSQ — template HPF of 184 rejected as too high for a female lead's F3–G3;
             all three de-essers dynamic because RH climbs 93→99% across the show)
