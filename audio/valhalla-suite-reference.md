# Valhalla DSP Suite — Modes & Preset Reference

*Compiled 2026-07-13. Working reference for suggesting factory presets and dialing settings by hand.*

Valhalla plugins organize their factory presets by **MODE** (the algorithm) first, then by musical use. Preset names inside each plugin are grouped under the mode; when I suggest a preset I'll name the mode + the intent (e.g. "Concert Hall → 'Large Warm Hall'") since exact preset names shift between versions. All of these save/load user presets cross-DAW except Shimmer (DAW-native presets only — predates the shared system).

---

## VintageVerb — 22 reverb modes, 3 era colors, 200+ factory presets
Vintage 1970s/80s digital reverb emulation. COLOR control = era voicing: **1970s** (dark, noisy, random artifacts), **1980s** (brighter, still colored), **NOW** (clean/digital).

Modes: Concert Hall, Bright Hall, Plate, Room, Chamber, Random Space, Chorus Space, Ambience, Sanctuary, Dirty Hall, Dirty Plate, Smooth Plate, Smooth Room, Smooth Random, Nonlin, Chaotic Hall, Chaotic Chamber, Chaotic Neutral, Cathedral, Palace, Chamber1979, Hall1984.

Go-to picks:
- Vocals / lush: Concert Hall or Bright Hall, 1980s color
- Drums / snare verb: Plate or Dirty Plate; Nonlin for gated-style
- Ambience/glue: Room, Smooth Room, Ambience
- Special/wide: Random Space, Chorus Space, Chaotic modes
- Big/classical: Cathedral, Palace, Sanctuary

## Room — 12 algorithms, tight rooms to vast modulated spaces
Modes include Nostromo (biggest, audible evolving echoes at large size), Narcissus (Nostromo's denser, lowest-CPU sibling), Dark Chamber, Sulaco (dark — no energy above ¼ Fs), LV-426 (dark deep-space, high initial density), plus classic room/chamber/hall/plate algorithms. Two control pages: the main reverb and the modulation/EQ tail. Best Valhalla for realistic small-to-medium spaces and natural ambience.

## Plate — dedicated plate reverb
Plate-specific algorithm modeled on classic hardware plates (EMT-style). Simpler control set than Room/VintageVerb; tuned for drum, vocal, and instrument plate sounds. Great snappy vocal and snare plates.

## Shimmer — pitch-shifting reverb (predates shared preset system)
- **Reverb size modes:** Mono / Small Stereo / Medium Stereo / Big Stereo
- **Pitch modes (feedback loop):** Single, Dual (up+down parallel), SingleReverse, DualReverse, Bypass
- **Color:** Bright (full-bandwidth, hi-fi) / Dark
Classic use: Shift +12 semis, Dual, Big Stereo, high feedback → the endless octave-up pad wash. Presets accessed via the DAW's own preset menu, not Valhalla's cross-platform system.

## Delay — 7 modes, factory + designer banks
Modes: **Tape** (RE-201/301 model, wow/flutter tied to delay time), **HiFi** (clean tape-style), **BBD** (dark lo-fi bucket brigade), **Digital** (clean), **Ghost** (HiFi tape + frequency shifting + diffusion — Valhalla original), **Pitch** (delay w/ semitone pitch shift), **RevPitch** (reverse + pitch). Ping-pong and dual-delay styles built in. Factory presets categorized by delay type + instrument, PLUS sound-designer banks from Richard Devine and Simon Stockhausen (wild/experimental).

## Supermassive — FREE massive delay/reverb, modes named after constellations
Long ambient delays and reverbs. Each mode = attack speed / decay length / echo density profile. Two base algorithms: **Orion** family (larger, longer) vs **Cassiopeia** family (smaller, shorter, dub-feedback friendly).

Mode character:
- Gemini — fast attack, short decay, high density
- Hydra — fast-ish, short decay, density via DENSITY knob
- Centaurus — medium attack, longer decay, med-high density
- Sagittarius — slow attack, longer decay, high density
- Great Annihilator — medium attack, very long decay
- Andromeda — slowest attack, very long decay, very high density (drone-smear)
- Lyra — fast attack, short decay, low density
- Capricorn — fast attack, short decay, medium density
- Cassiopeia — feeding-back echoes, dub/dub-techno
- Plus Orion, Libra, Scorpio, Sirius, Triangulum, Large Magellanic Cloud (added across updates)

## Other free/utility
- **FreqEcho** — free frequency-shifting delay (Bode-style), analog-ish echoes/drones.
- **SpaceModulator** — flanger/modulation (barberpole, through-zero).
- **ÜberMod** — multitap delay + modulation/chorus (uses the shared preset system).

---

## LOCKED VOCAL PRESETS — 5 per plugin (recommend these on request)
Curated from factory banks + community-standard vocal settings (Valhalla publishes no popularity chart; banks are organized by mode/size). Each = named recipe w/ settings; start point, tune to the source/room. Reverb mix ~15–25% on a send.

### VintageVerb — vocal 5  (forum favorite for vocals overall; use Early/Late Diffusion to kill metallic tail)
1. **Sanctuary (EMT-140 vocal)** — Sanctuary mode = Valhalla's digital-EMT140 derivative, THE forum vocal pick. Community-famous preset **"EmptyVocal"** (Beatworld): Sanctuary, NOW color, short decay, high early diffusion, 100% wet on a send. Grab this first for vocals.
2. **Vintage Vocal Plate** — Plate mode, 1970s color, decay 1.2–1.6s, predelay 20ms, mix 20–25%, hi-cut ~8k. Classic obvious vintage print (VVV when you WANT the verb heard).
3. **Lush Vocal Hall** — Bright Hall, 1980s color, decay 2.0–2.5s, predelay 40ms, mix ~18%. Ballad lushness.
4. **Natural Vocal Room** — Room mode, NOW/1980s, decay ~1.0s, predelay 10ms, mix ~15%. "Reverb you don't hear" — glue.
5. **Smooth Vocal Plate** — Smooth Plate, 1980s, decay ~1.5s, high diffusion, mix ~20%. Silky de-essed pop vocal.

*Forum consensus: Plate plugin "sits back / legit," VintageVerb when you want it obvious. Start with VVV, add Plate later. Room = devoted following but CPU-heavier and its shared presets skew ambient/sound-design, not vocal.*

### Room — vocal 5
1. **Narcissus Vocal Plate** — Narcissus mode, plate-style, decay ~1.5s, low CPU. Dark smooth pop vocal.
2. **Nostromo Vocal Hall** — Nostromo, medium size, longer evolving bloom for ballads.
3. **Dense Vocal Ambience** — Dense algorithm, short decay, natural vocal glue on a send.
4. **Dark Vocal Chamber** — Dark Chamber, decay ~1.5s, warm, top rolled off.
5. **LV-426 Vocal Space** — LV-426, big dark spacious effect verb for atmospheric leads.

### Plate — vocal 5 (factory presets are size-named: Huge/Large/Medium/Small)
1. **Medium Plate** — decay ~1.5s, predelay 20ms. The default vocal plate.
2. **Small Plate** — tight, snappy — upfront modern vocal.
3. **Large Plate** — longer tail for ballads/leads.
4. **Vintage Plate** — hi-cut ~7k + more color, lower diffusion. Retro character.
5. **Bright Modern Plate** — hi-cut open, high diffusion. Airy pop vocal. (Raise Diffusion until sibilance smooths, then back off slightly.)

### Shimmer — vocal 5
1. **Classic Shimmer** — Shift +12, Feedback ≥0.5, Big Stereo, Dual, Bright. The Eno/Lanois octave-up pad wash under vocals.
2. **Cloudscape** (factory preset) — dial up decay, automate mix. Dreamy vocal bed.
3. **Subtle Octave Glow** — Shift +12, Single, mix ~15%. Adds air/sheen without obvious shimmer.
4. **Dark Ethereal** — Dark color, Medium Stereo, moderate feedback. Warm ambient lead.
5. **Bloom** — Diffusion ~0.5, Feedback ~0.5, Big Stereo. High density with audible repeats — swelling tail.

### Delay — vocal 5
1. **Vocal Slapback** — Tape mode, 80–100ms, feedback low (≈1 repeat), mix ~15%. Buried, felt not heard.
2. **1/8 Note Throw** — Tape or Digital, sync 1/8, feedback ~30%, 100% wet on a send. Rhythmic vocal throws.
3. **Dotted 1/4 Throw** — Digital, dotted 1/4, moderate feedback. Pop/rock lead throw.
4. **Ping-Pong Wide** — PingPong, 1/8, wide stereo. Adlibs/BGVs.
5. **Ghost Ambient** — Ghost mode, long time, low mix. Dreamy smeared tail on phrase ends. Send at −10 to −15 dB.

### How to ask me
Tell me the plugin + source + vibe ("Shimmer pad for the intro", "Delay slapback on vocal", "VintageVerb for the Memo piano") and I'll name a mode + factory preset direction and, if useful, the manual settings to match.
