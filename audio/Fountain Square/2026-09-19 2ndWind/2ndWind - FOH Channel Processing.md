# 2ndWind — FOH Channel Processing
Venue: Fountain Square · Date: 2026-09-19 · Console: DiGiCo Quantum 225

STUB — filled by the show-deep-build ("Deep Think") flow. Locked format,
one block per processed channel (B1 = console LOW band .. B4 = HIGH):

    ## Ch N | CONSOLE NAME | MIC/DI
    HPF: hz | LPF: hz-or-OFF
    B1: gain | freq_hz | Q | SHELF-or-BELL
    B2: gain | freq_hz | Q | BELL | DEQ: thr=-16 atk=10ms rel=100ms
    B3: FLAT
    B4: gain | freq_hz | Q | SHELF-or-BELL

Rules: console name <= 12 chars · whole-dB gains · display Hz (the patcher
scales) · FLAT for a bypassed band · lint runs automatically on every patch.

FSQ don't-forgets:
  - Channels 1-32 only; MIC/DI column decides what gets processed.
  - Vocals/wireless faders 25-36 ship a baked-in starting curve.
  - Outdoor: HPFs trend higher, cuts over boosts, reverb minimal to none.
