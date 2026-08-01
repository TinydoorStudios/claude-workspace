# Unit 05 — Hat × Shure SM81  (ch 5)

INSTRUMENT   Hi-hat. In R&B/neo-soul the hat carries the subdivision — 16ths, shuffles, the
             thing that makes the groove read as this genre rather than rock. But with a
             stereo OH pair open on ch 9 this is a spot mic, not the whole cymbal picture.
MIC          Shure SM81. Cardioid SDC, requires 48V. Switchable low-frequency filter (flat /
             6 dB per octave / 18 dB per octave) and a −10 dB pad. **Filter ASSUMED FLAT** —
             the desk does the filtering. KB tendency: "apply template as-is (flat/honest)."
SEARCHES     "Shure SM81 hi-hat live sound EQ HPF settings frequency response flat specification"
             → shure.com/en-US/products/microphones/sm81, recordinghacks.com/microphones/shure/sm81,
               gearspace.com "Frequency Response Graphic of Shure SM-81"
CAPSULE FACT **Flat frequency response 20 Hz–20 kHz with a switchable low-frequency filter at
             6 dB/octave or 18 dB/octave.** No presence peak, no baked HF lift.
             Source: Shure USA SM81 product page / RecordingHacks SM81.
WEB SAYS     Consensus is that engineers reach for the SM81 on cymbals and hat specifically
             because it "captures all of the detailed high end without introducing a harsh or
             brittle sound." General hat guidance: HPF 300–500, notch harshness 2–4 kHz, and a
             shimmer boost 8–10 kHz — that last move is the one this build refuses, for reasons
             under VENUE BEND.
KB SAYS      mic-library: "Ruler-flat SDC, clean detailed highs with no harsh fizz, flat/6/18dB
             HPF. Accurate on hat/OH/acoustic — takes EQ well. Weakness: needs care on cymbal
             wash, no built-in flattery." Same.
VERDICT      **AGREE** — flat, switchable filter, no hype, from both sides.
LOCKER       Silent pass. mic-library's entry for the SM81 is literally "Overheads, hi-hat" —
             it is the locker's first call for this source. The Audix M1280BHC (DP8) was
             considered and dropped: a hypercardioid clip would improve rejection, but its
             "thin lows and upper-mid forwardness" is the wrong trade on a night where the top
             end already arrives intact. Marginal win, so the tie goes to the specified mic.
GENRE BEND   The hat needs to be present and articulate for the genre, but present is a fader
             job here, not an EQ job — because the capsule is flat, "present" is what it
             already gives.
VENUE BEND   Two venue layers land hard on this channel. **Gusts to 28 mph** → HPF 400, well
             above the usual 300, and above the point where kick and snare bleed live.
             **96% RH** → the standard 8–10 kHz shimmer boost is actively wrong tonight:
             saturated air absorbs almost no HF, so the cymbal's real top arrives at the back of
             the plaza already, and the correct move is a trim.
DRAFT BANDS  HPF 400 · LPF 16000
             B4  −3 | 8000 | 2 | BELL
             B3  −6 | 1000 | 2 | BELL
             B2  −7 | 500  | 2 | BELL
             B1  FLAT
GATE CHECK   **No boosts.** The SM81 is ruler-flat, so there is no baked peak to permit or
             forbid one — the reason there is no boost here is the venue, not the capsule:
             the genre's usual 8–10 kHz shimmer lift is replaced by a −3 @ 8000 trim because
             saturated air is doing the lifting for free.
QUESTIONS    SM81 filter switch position at load-in — build assumes FLAT. If the 18 dB/oct
             filter is engaged, drop the desk HPF to 150 so the two do not compound.
TRACE        base(SM81 — ruler-flat 20 Hz–20 kHz, switchable 6/18 dB filter, Shure/RecordingHacks) ·
             equip(hats unknown, no rider — generic carries) ·
             genre(R&B — hat carries the subdivision, but a flat capsule needs no help to do it) ·
             artist(no change) ·
             venue(FSQ — HPF 400 for 28 mph gusts; 96% RH inverts the genre's shimmer boost into
             a −3 @ 8000 trim)
