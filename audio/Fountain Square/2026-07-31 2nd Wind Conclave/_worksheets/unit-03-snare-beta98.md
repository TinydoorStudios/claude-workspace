# Unit 03 — Snare × Shure Beta 98 (H/C)  — now ch 4 ONLY

> **Superseded in part.** Brian's answer to the locker fork: **i5 on ch 3 only.** There is one
> i5 in the DP8, so the main snare takes it (see `unit-03b-snare-top-i5.md`) and **ch 4, the aux
> snare, keeps the Beta 98H/C** — a deliberately mixed pair. Everything below still governs
> ch 4; the ch-3 draft in DRAFT BANDS is superseded by unit 03b and is left in place only as
> the record of what was proposed.
> `mic_notes` line so this isn't re-litigated: *"Locker fork — i5 taken on ch 3; only one in the
> DP8, so the aux snare keeps the Beta 98H/C."*

INSTRUMENT   Main snare (ch 3) plus a second snare (ch 4). R&B/gospel show-band drummers
             routinely carry a main + piccolo/aux snare, and the list gives both the same mic
             and calls the second one "Snare 2" — not "Snare Bottom", which is what the console
             template's own fader 4 is already called. **My read: two separate snare drums, both
             top-miked.** That read goes in the question round; if ch 4 is really a bottom mic,
             it needs a polarity flip and a completely different curve.

MIC          "98" → **Shure Beta 98H/C** — the only 98 in the locker (mic-library lists no other).
             Clip-on cardioid condenser on a gooseneck, 48V, rim-mounted, no stand. Normally
             Brian's horn clip-on; here it's on drums.

SEARCHES     1. `Shure Beta 98 snare drum mic live EQ frequency response presence peak dB rim mount`
             2. `Shure Beta 98A/C frequency response chart presence boost 8kHz low frequency
                rolloff 100Hz specification`
             3. `"Beta 98" snare drum live sound EQ boxy 400Hz gearspace prosoundweb condenser
                snare mic`
             4. Fetched the RecordingHacks Shure Beta drum-mic review (2011-05-06) for measured
                behaviour on snare and toms.

CAPSULE FACT **"A small high end boost above 8 k" vs an SM57, and significant low-frequency
             content below 100 Hz that needs a high-pass around 100 Hz** — RecordingHacks'
             Beta drum-mic review, testing the 98 family on a kit. Same review: noticeably
             **more hi-hat bleed than a 57** on snare, and 160 dB max SPL so rimshots are not
             a level problem.

WEB SAYS     The 98 is voiced bright and open — "punchy, full, and bright" on toms, attack
             emphasised over body vs a dynamic. Its two live liabilities on a snare are the
             sub-100 Hz junk it picks up through the rim (mechanical, not acoustic) and the
             hat bleed its cardioid pattern doesn't reject the way a supercardioid dynamic
             would. General live-snare consensus (Music Guy Mixing, audiospectra): boxiness
             lives 400–700 Hz, and 7 k is the stick-crack band.

KB SAYS      mic-library: "Beta 98H/C — clip-on cardioid condenser, 20 Hz–20 kHz, tailored/voiced
             presence for open natural horn/perc sound, tight pattern, gooseneck. **Weakness:
             thin lows**, the voiced presence can get edgy close. → ease off presence."

VERDICT      **DISAGREE — on the low end.** The KB says "thin lows"; the measured drum review
             says the opposite, enough sub-100 Hz content to force a high-pass. Both are right
             about different placements: clipped to a horn bell in free air it *is* thin, and
             bolted to a snare rim it picks up shell and hardware coupling. The resolution is
             placement, not a coin flip — I'm building for the rim-mounted behaviour (HPF up,
             not a low boost). → carried to the round as a **KB update offer** (add the
             drum-mounted LF note to the Beta 98H/C entry), option (c).

LOCKER       **FORK RAISED — Audix i5 (DP8).** Full card in the question round. Summary: the
             98H/C is a horn clip-on doing snare duty and is not the locker's first call for
             snare; the i5 is, it's in the same DP8 case as the D2/D4/D6 already on this list,
             and being a dynamic it doesn't collect the hat wash the condenser does.
             *Dependency:* the other snare-class alternative, the Lauten LS-408, may be spoken
             for — it's one of the two candidates for the ambiguous "408" on ch 5.

GENRE BEND   R&B/funk/gospel: the snare is a backbeat event, not a rock wall. It needs crack
             and body, and it has to cut through congas, bongos, toys and a programmed track.
             Artist layer: with four vocals live all night, the snare's 1–3 kHz region has to
             stay out of the vocal path — the crack gets placed high (7 k) rather than mid.
             Ch 4 (aux snare) gets slotted *above* the main snare so the two read as different
             drums instead of one thick one.

VENUE BEND   FSQ outdoor: box cut goes to the outdoor depth. HPF runs at 140 rather than the
             review's suggested 100 — no room gain to lose, plenty of stage rumble and gusts
             to reject, and the kick already owns everything below there.

DRAFT BANDS  **ch 3 Snare Top**
             HPF 140 · LPF OFF
             B4  +3 @ 7000  Q 1.5  BELL   stick crack
             B3  −8 @ 450   Q 2.0  BELL   box — outdoor depth
             B2  −5 @ 900   Q 2.0  BELL   honk, keeps the vocal path clear
             B1  FLAT

             **ch 4 Snare 2 (aux/piccolo)**
             HPF 180 · LPF OFF
             B4  +3 @ 8000  Q 1.5  BELL   crack, placed a step above the main snare
             B3  −7 @ 500   Q 2.0  BELL   box
             B2  −4 @ 1200  Q 2.0  BELL   its own lane, above ch 3's 900
             B1  FLAT

GATE CHECK   **Boost audit — B4 +3 @ 7000 (ch 3) and +3 @ 8000 (ch 4).** The measured boost in
             this capsule is "above 8 k." Ch 3's lift at 7 k sits *below* that baked region —
             a genuine lift, not a stack. Ch 4's at 8 k sits at the bottom edge of it, which is
             why it stays +3 and does not go higher; the capsule is already helping there.
             Neither channel gets an air/high-shelf move — the capsule's own top plus 50%→77%
             humidity over the night would make that too bright by the last set.
             **Sectional separation (ch 3 vs ch 4):** they are not two copies. Crack at 7 k vs
             8 k, box at 450 vs 500, and the mid lane at 900 vs 1200 — each snare owns a
             different slot so a two-snare groove reads as two drums.

QUESTIONS    1. Is ch 4 "Snare 2" a second snare drum (my read) or the bottom head?
             2. Locker fork — i5 for the 98 on snare?
             3. KB update offer on the Beta 98H/C low-end note.
