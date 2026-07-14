# Next up: virtual location meters (one real mic → many locations)

Status: **designed, not built.** Brian's idea + confirmed approach.

## Concept

A fixed PA + fixed geometry + fixed mic positions is a linear, time-invariant
system, so the **dB difference between two static points is constant** regardless of
drive level. Characterize the offset from the reference mic (the live v8 FOH mic) to
each other static location once, then derive live virtual meters everywhere by adding
the stored offset to the reference's live reading.

Example simultaneous capture (same instant, same program/pink noise):
FOH 90, Front of Stage 95, Jeff Ruby's 80 → offsets vs FOH: +5, −10.

The v9 rig is the **calibration tool** (multiple calibrated inputs at once); the live
deployment stays the standard **one-mic v8 rig**.

Computational bonus: offset is constant ⇒ a location's rolling LAeq = reference rolling
LAeq + offset. Adding locations is nearly free and stays time-consistent.

## Get it right

- **Frequency dependence is the real wrinkle.** A single broadband offset holds only
  while spectral content is similar; bass carries farther than highs. Store **two
  offsets per location — dBA and dBC** — and run two virtual meters each. v8's
  calibrated metric stream gives SPL A / SPL C / SPL Z live, so this is free at runtime
  and tracks bass separately (the outdoor problem child). True 25–80 Hz ("dB1") band is
  a later refinement needing a band-limited metric / v9 data; dBC is the live proxy.
- **Anchor offsets to the v8 mic.** During the v9 calibration walk, record what the v8
  FOH mic reads simultaneously; offset = target − v8_FOH. Cancels any inter-rig
  calibration difference; live math becomes exact.
- **Calibrate with pink noise** through the PA — broadband, repeatable, spectrum-independent.
- **Failure modes to model:** each remote location has its own ambient floor — grey out
  / don't alarm when the virtual level is at/under the floor (PA not dominant there).
  Distant outdoor points drift with wind/temperature (tie to Tempest later). PA in heavy
  limiting shifts offsets slightly.

## Live math (per frame, from the single v8 reference stream)

```
ref_A = reference SPL A (instant) ; ref_C = reference SPL C (instant)
for each location L:
    virtual_A_inst = ref_A + L.offsetA
    virtual_C_inst = ref_C + L.offsetC
    rolling LAeq_L  = (reference rolling LAeq) + L.offsetA   # constant offset
    rolling LCeq_L  = (reference rolling LCeq) + L.offsetC
    light_L = compare rolling LAeq_L (and/or LCeq_L) to L.limits
    if virtual_A_inst <= L.noiseFloorA: mark "below ambient — estimate unreliable"
```

## Config schema (per venue)

```json
"Fountain Square": {
  "referenceLocation": "FOH",
  "calibratedOn": "2026-06-04",
  "calibrationMethod": "pink noise, v9 simultaneous, anchored to v8 FOH mic",
  "locations": {
    "FOH":            { "offsetA": 0,   "offsetC": 0,   "noiseFloorA": 55, "limits": { "A": {"yellow":92,"red":98} } },
    "Front of Stage": { "offsetA": 5,   "offsetC": 6,   "noiseFloorA": 60, "limits": { "A": {"yellow":98,"red":103} } },
    "Jeff Ruby's":    { "offsetA": -10, "offsetC": -7,  "noiseFloorA": 50, "outdoorDistant": true,
                        "limits": { "A": {"yellow":55,"red":60}, "C": {"yellow":65,"red":70},
                                    "schedule": [ {"after":"22:00","A":{"yellow":50,"red":55}} ] } }
  }
}
```
(Per-location limits can be time-tiered — see RESEARCH_red_rocks.md. The "C" limits +
schedule are where the bass/curfew control lives for residential-adjacent spots.)

## UI

Multi-location dashboard: each location its own meter card with readout + traffic light
+ prediction + log line. Reference location flagged as real (offset 0); others labeled
"virtual / derived", far+outdoor ones flagged weather-sensitive, below-floor ones greyed.

## Open questions
1. Dual A+C offsets (recommended) vs single broadband?
2. Each location its own limits, or share the venue's?
3. How to flag far / weather-sensitive locations (label only, or confidence indicator)?
4. Build as its own pass, or fold into the violation-counter work?
