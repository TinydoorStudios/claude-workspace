# Mustard processing (tube, EQ, modelled compressors, gate)

![Mustard — Quantum 2](/figures/q2-mustard.png)

Mustard is a second channel strip that runs alongside the standard SD strip on every Quantum channel: a preamp/tube model, a 4-band EQ with filters, four compressor types and a gate/ducker. A channel counts as "using Mustard" as soon as any one module is on; the count in use and remaining is in System > Diagnostics > **Engine**. The Q225 getting-started guide quotes 24 simultaneous Mustard strips.

![Mustard channel strip](/figures/ref-p054-1.png)

## Switch the strip view

The **SD / Mustard** button in the strip flips the on-screen strip (and the big meters at the top) between the two processors. A small *SD* or *M* shows which is active; an *Active* icon appears above the Mustard icon when Mustard is on.

## Where Mustard sits in the chain

Five positions, shared with Insert A and Insert B (one occupant per position): after trim / before delay, after filters / before EQ-dyn, between EQ and dynamics (default), after processing / before mute and fader, post-fader. Change it with the **insert position** control in the Mustard strip.

## Tube / preamp

**type** chooses *Tubes* (drive, output, six presets: odd harm, even harm, overdrive, distortion, crunch, high distortion) or the *Amp Model* (two stages, each odd or even harmonics, drive, bias with saturate, HF boost above 6 kHz, output gain).

![Mustard amp model](/figures/ref-p056-1.png)

## Mustard EQ

Four parametric bands (outer bands switchable to shelf, middle two to all-pass) and 24 dB/oct HPF and LPF. Combined with the SD EQ that's eight parametric bands per channel.

## Compressors (DYN1)

All have on/off, a **wet/dry mix** and output gain; all but the FET have threshold plus sidechain high and low filters with **s/c listen**.

| Type | Character |
|---|---|
| **Classic** | Feed-forward, full control: threshold, attack, release, ratio, hard/soft knee, RMS or peak sensing. |
| **Vintage VCA** | Fixed attack, auto release; threshold and ratio. |
| **Optical** | Opto behaviour with three attack and three recovery options, ratio, and a ratio-dependent maximum gain reduction. |
| **FET Limiter** | Fixed threshold; drive it with input and output gain. Attack, release, ratio 4:1 / 8:1 / 12:1 / 20:1. |
| **Levelling Amp** (V22) | "The Silver one": tube-style electro-optical behaviour, fixed attack and release. Controls are **Peak Reduction** (effectively threshold), **Gain**, and a **Limit/Compress** ratio switch. Vocals and bass. |

## Gate/ducker and MSE (DYN2)

The gate/ducker mirrors the SD one with different attack/release shapes. Press **Type** on Dynamics 2 and choose **MSE** for the Mustard Source Expander: threshold, depth (to 40 dB), release. It drops the level when the source stops, which is a cleaner way to close a vocal mic than a gate. An external sidechain source chosen under the gate can feed the compressor and/or gate.

## Safes, scopes, presets

Each Mustard module safes individually (tube safe includes the insert position). In snapshot global scope, tube falls under input/trim, EQ under EQ, compressor and gate under dynamics. Channel presets can include or exclude each module.

The house convention here is Mustard **off** by default in the templates; turn it on per channel when you want it.

Manual: [Reference 1.7 Mustard Channels](/reference/1-7-mustard-channels-quantum-only), [V22 release notes 1.3](/docs/v22-release-notes).
