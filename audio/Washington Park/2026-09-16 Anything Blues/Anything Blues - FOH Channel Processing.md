# Anything Blues — FOH Channel Processing
Venue: Washington Park · Date: 2026-09-16 · Console: Midas M32

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
