# Seventh Heaven Pro — Reverb Reference for Memorial Hall

*Memo-specific reverb decisions. RT60 ~1.6s working — the room is already doing reverb work. Start conservative and pull factory decay times back. Full preset list and tweak notes: `Seventh Heaven Pro - Preset Reference.pdf`.*  
*Last updated: May 2026*

---

## Core Principle — Memo RT60

The room adds ~1.6s of natural decay. Factory preset decay times are designed for drier rooms. For most shows at Memo, pull decay time down from factory by 30–40% as a starting point. A Halls 1 / Boston Hall A at 2.1s factory becomes more like 1.2–1.4s in the Memo. Let the room do some of the work.

**Exception:** very close-mic'd sources (DI bass, kick inside drum, lip-close vocal) that need reverb for placement — those can run a bit longer since the mic isn't picking up much natural room.

---

## Algorithm Choice

**V1** — static, realistic, low modulation. Classical, jazz, Celtic, acoustic folk, chamber music. The 'pure' Bricasti sound. Use when you want the source to keep its character.

**V2** — brighter, more modulated, lush bloom. Gospel, contemporary, pop/rock, dense choir. Use when you want wash and bloom rather than accuracy.

When in doubt on acoustic shows: V1. When in doubt on contemporary shows: V2 for vocals/plates, V1 for halls.

---

## Reverb Line Format (Pipeline Spec — Locked)

```
Preset: [Bank / Name] | Decay Xs • PreDelay Xms • Early/Late XX/XX • HF Damp X.X • Mix X% — [rationale]
```

Include return EQ sweetening (HS, LC) where applied.

---

## By Genre — Recommended Starting Presets

### Classical / Chamber / Orchestral (V1)

| Use | Preset | Notes |
|---|---|---|
| Main hall (strings, winds, full ensemble) | Halls 1 / Concert Hall | Low modulation, low diffusion — accurate and stable. Pull decay to 1.2–1.4s at Memo. |
| Solo instrument or small chamber | Halls 1 / Boston Hall A | Nuno Fernandes pick. Brighter, empty-hall character. |
| Piano (solo) | Halls 1 / Piano Hall | Tuned for solo piano. Try as stereo send first. |
| Vocal (classical) | Chambers 1 / Sunset Chamber | Long, warm, low diffusion. Simone Coen pick. 20ms pre-delay minimum. |
| Strings (close-mic'd amplification) | Chambers 1 / A&M Chamber | '70s smoothness. Pre-delay 20ms. |
| All-ensemble air | Ambiences 1 / Large Ambience | Adds space without obvious tail. Good for instruments getting just a touch of room. |

### Jazz (V1)

| Use | Preset | Notes |
|---|---|---|
| Drum bus / overheads | Rooms 1 / Studio B Close | Wood-floor close mic. Dense, no pre-delay. Forum favorite. |
| Acoustic instruments (guitar, bass, piano) | Rooms 1 / Djangos Room | Small jazz-club feel. Right character for the genre. |
| Upright bass / acoustic guitar | Rooms 1 / Large Wooden | 'Sounds really natural for a bit of air around anything.' Set and forget. |
| Lead vocal | Chambers 1 / Vocal Chamber | Classic chamber on vox without crowding. Try 20–40ms pre-delay. |
| Snare | Plates 1 / Snare Plate A | James Richmond go-to. Bright, dense, built for snare. |

### Celtic / Acoustic Folk (V1)

| Use | Preset | Notes |
|---|---|---|
| Acoustic instruments (general) | Rooms 1 / Large Wooden | Natural, airy. Pull decay back — Memo adds warmth already. |
| Flute / whistles | Chambers 1 / Small Chamber | Compact, warm, no long bloom. |
| Uilleann pipes | Chambers 1 / Medium Chamber | James Richmond 'just pick the one named Medium.' Tight enough to stay clean. |
| Bodhran | Rooms 1 / Studio B Close | Short, dense — keeps the drum tight and present. |
| Vocals | Chambers 1 / Sunset Chamber | Long, warm, characterful. Pull decay back for Memo. |
| Fiddle / strings | Chambers 1 / A&M Chamber | Smooth, mid-forward. |

### Gospel / Contemporary (V1 halls, V2 plates/vocals)

| Use | Preset | Notes |
|---|---|---|
| Main hall / choir wash | Halls 1 / Sandors Hall | Long, dense. Pop strings and big choral cues — frequently used as vocal hall. |
| Lead vocal | Chambers 1 / Vocal Chamber (V1) or Plates 2 / Vocal Shimmer (V2) | V1 for traditional feel, V2 for contemporary bloom. |
| Background / choir vocals | Plates 1 / Rich Plate or Plates 2 / Vocal Shimmer | Rich Plate for warmth, Vocal Shimmer for cinematic. |
| Snare | Plates 1 / Snare Plate A | Standard. |
| Drum bus | Rooms 1 / Studio B Close | Keep drums tight — let hall handle the wash. |
| Keys / synth pads | Halls 2 / Large Hall (V2) | V2 bloom suits contemporary gospel pad sounds. |

### Rock / Blues / Americana (V1 or V2)

| Use | Preset | Notes |
|---|---|---|
| Snare | Plates 1 / Snare Plate A or Plates 1 / Dark Plate | A for crack, Dark Plate for vintage warmth (Andy Bradfield pick). |
| Drum bus | Rooms 1 / Studio B Close | Wood-floor density. |
| Electric guitar | Rooms 2 / Guitar Room (V2) | Late delay 300ms baked in — pre-built slap. |
| Vocal | Chambers 1 / Vocal Chamber or Plates 1 / Vocal Plate | Chamber for warmth, Vocal Plate when you need it to sit back further. |

---

## By Source — Quick Picks (Memo-Specific)

| Source | First choice | Alternative |
|---|---|---|
| Lead vocal (acoustic show) | Chambers 1 / Sunset Chamber | Chambers 1 / Vocal Chamber |
| Lead vocal (contemporary) | Plates 1 / Vocal Plate | Plates 2 / Vocal Shimmer |
| Choir / group vocals | Halls 1 / Sandors Hall | Spaces 1 / North Church |
| Snare | Plates 1 / Snare Plate A | Plates 1 / Snare Plate B (pre-delayed) |
| Kick (layer only) | Chambers 1 / Kick Chamber | — |
| Drum bus / overheads | Rooms 1 / Studio B Close | Ambiences 1 / Percussion Air |
| Acoustic guitar | Rooms 1 / Large Wooden | Chambers 1 / Small Chamber |
| Piano (solo) | Halls 1 / Piano Hall | Halls 1 / Boston Hall A |
| Upright bass | Rooms 1 / Djangos Room | Rooms 1 / Small Wooden |
| Orchestral strings | Halls 1 / Concert Hall | Halls 1 / Sandors Hall |
| Amplified strings (clip-on) | Chambers 1 / A&M Chamber | Rooms 1 / Studio B Far |
| Brass section | Halls 1 / Brass Hall | Rooms 1 / Small Room |
| Flute / woodwinds | Chambers 1 / Small Chamber | Halls 1 / Small Hall |
| Uilleann pipes | Chambers 1 / Medium Chamber | Rooms 1 / Large Wooden |
| Bodhran | Rooms 1 / Studio B Close | Rooms 1 / Studio B Far |

---

## Underhead / Underhat Reverb

When cymbal mics are in underhat/underhead position (broadcast restriction), add **+2 to +3 dB** to the reverb send on those channels to compensate for the reduced natural air. The preset choice doesn't change — only the send level offsets.

---

## Tweak Priorities at Memo

1. **Decay time first** — pull down from factory. The room adds to whatever you set.
2. **Pre-delay** — use it to keep the source intelligible before the tail arrives. Minimum 10ms on most vocal and instrument sends. 20–30ms is typical.
3. **HF Damp / Rolloff** — Memo absorbs highs with a full audience. Don't fight it — matching the reverb's HF rolloff to the room character helps it sit naturally.
4. **Early/Late mix** — pull more Early when you want presence without wash. More Late for bloom and size.
5. **Tail ducker (Pro mode)** — use Late mode on vocal reverbs. Keeps sense of place during phrases, only blooms between lines.

---

## Layering (When Applicable)

Classic two-reverb move: short chamber/plate for close perspective + long hall for tail, pre-delayed 40–80ms. At Memo, the room itself is the third layer — so this works best on very close-mic'd sources that aren't picking up much natural room.

Example: vocal chain → Chambers 1 / Vocal Chamber (close) + Halls 1 / Boston Hall A pre-delayed 50ms (tail). Both pulled back from factory decay.

---

*All preset names are exact — cross-reference `Seventh Heaven Pro - Preset Reference.pdf` for full parameter specs.*
