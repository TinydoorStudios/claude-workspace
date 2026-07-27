# Soundtoys EchoBoy — Working Reference (FULL version, v5)

*Compiled 2026-07-24 from the official Soundtoys EchoBoy v5 User's Guide. Brian owns the FULL EchoBoy, not Jr — everything below applies. Jr differences noted at the end only so we never confuse the two.*

---

## The shape of the plugin

Four Echo Modes (**Single · Dual · Ping Pong · Rhythm**), each with its own slide-out **Tweak** menu, plus a global **Style Editor** that sits behind every mode. The Style menu (31 modeled styles) sets the tone/character; the Mode sets the topology; Tweak sets the stereo/feel details; the Style Editor is where the styles themselves were built and where custom ones get made.

Signal note: Input and Output level affect **the echo signal only** — dry stays untouched. Yellow LED = 6 dB below clip, red = at clip.

---

## Common controls (all modes)

| Control | What it does |
|---|---|
| **Saturation** | Tube/tape-style compression, emphasis, subtle distortion on the delay. Behavior depends entirely on the Style — on Studio Tape it adds odd-harmonic LF/MF distortion + HF compression (auto-de-essing the echo on loud passages); on Limited it acts like a limiter threshold and pumps. |
| **Input / Output** | Model real analog input stages — clean or dirty depending on Style. Echo path only. |
| **Style** | 31 modeled echo characters (list below). |
| **Mix** | Dry/wet. 12 o'clock = 50/50. Past noon the dry drops out. In-line → use Mix; on a send/bus → 100% wet, ride the return. |
| **Feedback** | Repeats. Genuine self-oscillation available (Space Echo style especially). High settings raise output level a lot — careful. |
| **Prime Numbers** (switch) | Nudges repeat times off exact intervals to kill resonance buildup. Most audible in Dual and Rhythm; best on short times w/ feedback, chorus/flange, reverb-like patches. |
| **Low Cut / High Cut** | Tone-shaping of the repeats. High Cut for the classic tape/analog roll-off and pushing echoes back in depth. Effect depends on Style. |
| **Tap Tempo** | Tap the grey button to set BPM. Useful for un-clicked live material and for deliberately sitting off-grid. |
| **MIDI toggle** | Down = manual/tapped rate. Up = host MIDI clock is master. |
| **Groove** | Bipolar, 12 o'clock = zero. CCW = Shuffle, CW = Swing. Amount is relative to the current rhythm value. Applies regardless of modulation/rate. |
| **Feel** | Shifts the whole delay output against the beat, not just the groove. CCW = "Draggin'" (extra pre-delay, behind the beat); CW = "Rushin'" (negative pre-delay, ahead of the beat). This is the pocket control. |
| **Mode** | Single / Dual / Ping Pong / Rhythm — panel layout changes with it. |
| **Tweak** | Opens the per-mode advanced page. |

---

## The 31 Echo Styles

**Tape**
- **Master Tape** — Ampex ATR-102 @ 30 ips. Subtle, hi-fi, smooth; saturates beautifully.
- **Studio Tape** — ATR-102 @ 15 ips. Subtle distortion + HF compression; "tracked to tape."
- **EchoPlex** — EP-3 solid-state tape echo. The classic.
- **Space Echo** — Roland RE-201. Warm, gritty; dub/reggae staple; self-oscillates via Feedback.
- **Tube Tape** — modern tape echo, heavy high-mids and distortion.
- **Cheap Tape** — Soundtoys original after vintage consumer tape stock. Bright, very compressed.

**Analog / pedal**
- **Memory Man** — EH Memory Man. Warm, low-bandwidth chorus echo.
- **DM-2** — Boss DM-2 (1981–84). The bucket-brigade guitar echo: warm, resonant, punchy, clean.
- **TelRay** — Tel-Ray/Adineko oil-can delay. Dark, warbling, wavering.
- **Binsonette** — Soundtoys original from several Binson Echorec / Echorec II units. Warbly, compressed; the Pink Floyd guitar/keys sound.
- **Analog Delay** — warm, lightly distorted '70s–'80s rackmount.

**Digital / clean**
- **Digital Delay** — clean, accurate, transparent.

**Broadcast / bandwidth**
- **Telephone** — narrowband phone effect, great on vocals.
- **AM Radio** — compressed medium bandwidth.
- **FM Radio** — ultra-compressed, loud, morning-show DJ.
- **Shortwave** — exaggerated long-distance radio, narrow and staccato.
- **Transmitter** — CB-radio-ish, distorted, mid-resonant. Grit for synths.

**Chorus / modulation**
- **Digital Chorus** — the '80s chorus, present and clear, limited in the right way.
- **Analog Chorus** — warm all-rounder.
- **CE-1 Chorus** — Boss CE-1 Chorus Ensemble. Gorgeous on guitar.
- **Vibrato** — true pitch vibrato; keys and guitar.

**Distortion / dynamics**
- **Saturated** — exaggerated tape distortion; vocals and drums.
- **Fat** — super-warm distorted echoes; thick bed around guitar.
- **Distressed** — highly compressed and distorted.
- **Limited** — built-in limiter; pairs with high feedback.
- **Distorted** — distortion, lots.
- **Queeked** — odd multi-band compression echo, very effected.

**Ambient / reverb-like**
- **Ambient** — distortion + diffusion; long feedback loops, solo instruments.
- **Diffused** — reverb-like echo washes.
- **Splattered** — highly reflective reverb effect.
- **Verbed** — echo into a cheap verb chaser; very responsive to Feedback and Saturation.

---

## Single Echo Mode

Soundtoys' own favorite. One delay line, all the common controls, plus:

**Echo Time** — four ways to set it: knob, typed value in the LCD, the up/down menu arrows, or the **Time / Note / Dot / Trip** buttons. Time = milliseconds (turning the knob live gives the analog pitch-slide — automate it for tape-warp transitions). Note/Dot/Trip = tempo-locked, 1/2 down to 1/64, and note-value changes **crossfade smoothly**. Rough map: 0–10 ms = flange, 10–50 ms = chorus/double, 100–200 ms = slapback.

**Tweak menu:** **Width** (min = mono-centered; past 3 o'clock uses out-of-phase info for super-stereo beyond the speakers), **L/R Offset** (0–25 ms, default 8 ms — small = tighter but risks phasing, large = looser but cleaner; only audible with Width up), **Accent** (bipolar; CW emphasizes 1st/3rd/5th repeats for a strong on-beat feel, CCW emphasizes 2nd/4th/6th for syncopation. Best heard with high feedback + 1/8 or 1/16, and pairs with Groove).

---

## Dual Echo Mode

Two independent echo lines — Echo 1 = left, Echo 2 = right. One can free-run in ms while the other is note-synced. Feedback, High Cut, Saturation etc. hit both equally.

**Tweak:** **Balance** (L/R level), **Width / L/R Offset** (as Single), **Accent 1 / Accent 2** (per line), **FB Mix** (cross-feeds Echo 1 into Echo 2 and vice versa — at 12 o'clock equal amounts both ways for dense reverb-like echo; at max it's full cross-feedback, cross-pollinated syncopation), **FB Bal** (weights feedback toward one side — the fix when two different times make one side "appear" louder). FB Mix and FB Bal do nothing unless the main Feedback knob is up.

---

## Ping Pong Mode

Panel looks like Dual, behaves nothing like it. **Input is always summed to mono, output always stereo**, regardless of mono/stereo insert. The first repeat is ALWAYS the left "Ping" channel at the Ping time; the second is ALWAYS right "Pong", and it lands at **Ping + Pong**. Example — Ping 500 ms, Pong 250 ms: repeats at 500 (L), 750 (R), 1250 (L), 1500 (R)… Setting one side to a note value and the other to ms gets wild; both to note values + MIDI sync gets tight and rhythmic.

**Tweak:** just **Width** and **Balance**.

---

## Rhythm Echo Mode

A 16-tap pattern sequencer for echo — "a tape echo with sixteen read heads." The Rhythm Editor grid appears between the Low and High Cut knobs. Left-to-right = time, bar height = level. **Only the taps visible in the window are heard.** Grid defaults to 2 beats long. A **PATT** button saves/recalls patterns, and rhythm patterns are portable between any Soundtoys plugin with a rhythm mode.

**Editing:** click empty grid to add a tap (snaps to nearest line) · Option-click a tap to delete · click-drag to move (snaps; two taps can't share a slot — it'll snap back) · drag up/down for volume · **Cmd-click (Shift on Windows) to move a tap off-grid entirely**, which pops up a readout of position in fractions of a beat and level in dB.

**The "One":** the tap at beat one / 0 ms shows **yellow**, not green. It is not heard unless Feedback is up — with no feedback the "One" is your dry note, and the first audible echo is actually tap 2. With feedback up, the pattern restarts on it and you hear it. Move it off zero and it turns green and speaks. Delete it and you can restore it by clicking the left edge of the grid.

**Repeats** knob = how many individual taps sound (independent of Feedback, which repeats the whole pattern). Dial 1/16 + Repeats 4 for exactly four sixteenth-note repeats; raising Repeats auto-places new taps at the next logical grid position.

**Shape** — applies an amplitude envelope across all taps; the knob sets how much:
- **Decay** — progressively quieter (natural echo, reverb-like)
- **Reverse** — progressively louder (the '80s backwards-echo trick)
- **Swell** — quiet, loud in the middle, quiet
- **Fade** — loud, dip in the middle, loud
- **NonLin** — semi-random cluster with peaks/valleys, after the AMS RMX16 NonLinear program

**Tweak:** **Pan Shape** (Double, Center, Alt 1/2/3, Sweep L, Sweep R, Pan — "Double" halves the taps 16→8 and makes each a stereo pair with independent modulation, which is the thick-chorus setting), **Accent** (as elsewhere) which becomes **Warp** when the Time button is selected — Warp clusters all taps toward the start (CCW) or the end (CW) of the pattern, great with Shape for bouncing/robotic delays — plus **Rhythm Grid** (changes grid resolution without moving existing taps), **Length** (1–8 beats — think time signature), and **L/R Offset / Width**.

---

## The Style Editor — where the styles came from

Every factory style was built with these; opening it on any style shows you exactly how that sound is made.

**3-band EQ** — Low and High are gentle shelves, Mid is a semi-parametric single band. Delay path only, both channels, dry unaffected.
- **Gain** = the tone of the FIRST repeat.
- **Decay** = how the tone changes with EACH successive repeat (needs Feedback up to hear). Negative High Decay = each repeat darker; positive = each repeat brighter. Independent per band, and you can invert them against each other — dull first repeat that brightens as it goes, for instance. Higher Decay = bigger jump per repeat. This is the control that actually mimics tape vs analog vs digital frequency behavior.

**Diffusion** — reverb-style smear/density on the repeats. Short times → small-room effect where repeats melt together; long times + feedback → plate or hall. Denser in Dual/Ping Pong/Rhythm since multiple lines get diffused. Too much causes flanger-ish metallic resonance — balance against Size, the Loop/Post switch, Echo Time, and Feedback (all highly interactive).
- **Size** — character of the diffusion. Small = subtle, phasey at extremes; large = more reverb-like. Percussive vs sustained sources want very different settings.
- **Loop / Post switch** — Post (down): diffusion at the end of the chain, every repeat equally diffused. Loop (up): diffusion inside the feedback loop, each repeat progressively more diffused.

**Wobble** — vari-speed / tape-wow pitch modulation. Off at full CCW; up through subtle analog drift into full mangling.
- **Wobble Rate** — speed of the pitch variation.
- **Wobble Shape** — Triangle (ramps up/down), Sine (smoother), Square (jumps between two pitches), Random Walk (smooth ramps between random values), Random S/H (abrupt sample-and-hold jumps). The two random shapes at slow rate + low depth are the authentic vintage-tape saunter.
- **FB / Out toggles** — FB engaged applies wobble to the initial echo AND all feedback repeats; Out applies it to the wet output only, dry untouched (wild and resonant at high settings).
- **Sync** — at 12 o'clock all echo paths wobble at identical rate and phase. CCW progressively de-syncs the paths (different rates). CW keeps them in sync but flips phase between paths — right pitches up while left pitches down. Both directions are the good chorus/flange territory.

**Saturation section** — works with the front-panel Saturation knob, split into **Decay Sat** (delay only) and **Out Sat** (whole signal). Types: **Clean** (clean w/ limiting as you push), **Tape** (HF compression + LF distortion), **Warm** (dramatic warm distortion), **Pump** (popping/pumping limiter), **Dirt** (grungy, harder-edged), **Hard Limit** (pumps when hit hard), **Soft Limit** (smooth), **Warm Limit** (smooth and warm), **Bright Limit** (adds air/breathiness).
> Building a custom style: leave the front-panel Saturation knob at 12 o'clock and set levels from the Tweak/Style Editor saturation controls.

---

## Practical notes

- Max echo time isn't published in the manual — it states only that the ceiling depends on the mode in use.
- On a send/bus, run Mix 100% wet and control level at the return; in-line, use Mix.
- Feel is the underrated control: a hair of Draggin' pushes a vocal slap behind the beat and stops the echo fighting the phrase.
- Prime Numbers on any short-time/high-feedback patch is basically free — it removes buildup you'd otherwise EQ out.
- For a reverb from a delay: Diffused/Ambient/Splattered style, Diffusion up with Loop engaged, large Size, High Decay negative so the tail darkens.
- Automating Echo Time in ms gives the analog pitch slide; note values crossfade instead, so pick Time when you want the warp.

---

## What people actually use on vocals (web survey, 2026-07-24)

Nobody publishes a popularity chart, and Soundtoys doesn't either — the consensus that exists is at the **Style** level, not the preset level. What recurs across forums, SOS, and engineer interviews:

- **Studio Tape** is the default answer. ATR-102 @ 15 ips — a touch of HF compression that de-esses the repeat and lets the vocal sit back. This is the one that shows up everywhere.
- **EchoPlex** is the other repeat pick, with saturation and the filters tweaked; several engineers name it specifically for vocals.
- **Space Echo (RE-201)** when the vocal wants grit and dub character rather than polish.
- **Ambient / Diffused** for the "delay that reads as space, not as a delay."
- **CE-1 Chorus** for doubling/thickening, not for echo.

Named preset that keeps getting cited: **HallwayVocal** — a heavily diffused Splattered sound plus a very short stereo slap, giving a lead vocal lush stereo presence without sounding like a delay.

The factory vocal folder itself, per SOS's review, is "mostly quite subtle slap tape delays, small ambience effects and vocal doublers" — that's the character of the whole bank, and it's why people grab a preset there and then just change the Style.

The most-repeated *settings* pattern, independent of preset: 1/8 dotted or 1/4 tempo-synced (or a 60–120 ms slap with zero feedback for width), Feedback modest, High Cut down to push it behind the vocal, Saturation up for the analog glue. Declan Gaffney's U2 trick — Ping Pong, no feedback, just one warm bounce for ambience — is the other named pro use.

---

## EchoBoy Jr — what it is NOT (for disambiguation only)

Jr is the stripped version: 7 styles (Studio Tape, Plex, Space, Cheap Tape, Memory, Ambient, +1), a simple stereo Mode selector (mono / wide / ping-pong), a Glide control for enabling/disabling analog pitch sweeps on delay-time changes, and 58 presets. No Dual mode, no Rhythm mode, no Style Editor. Brian has the full version — never suggest Jr-only controls (Glide, the Mode selector) or assume the reduced style list.

---

*Sources: Soundtoys EchoBoy v5 User's Guide (soundtoys.com/wp-content/uploads/EchoBoy-Manual.pdf); Soundtoys product pages for EchoBoy and EchoBoy Jr.*
