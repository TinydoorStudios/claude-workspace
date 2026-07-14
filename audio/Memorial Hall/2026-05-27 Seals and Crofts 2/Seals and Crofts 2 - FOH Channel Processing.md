# Seals and Crofts 2 — FOH Channel Processing

<!-- FORMAT: ## Ch {N} | {Console Name} | {Mic/DI}
     HPF: {hz} | LPF: {hz|OFF}
     B1–B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
     FLAT = band bypassed.
     v2: Keyboards dropped. Channels 15-18 = Tracks/Click/Video. All 24 channels patchable. -->

## Ch 1 | Kick | Earthworks DM6
HPF: 40 | LPF: 8000
B1: -2 | 6000 | 0.8 | SHELF
B2: +3 | 3000 | 1.5 | BELL
B3: -5 | 250 | 2.0 | BELL | DEQ: thr=-16 atk=8ms rel=80ms
B4: +2 | 60 | 1.2 | SHELF

## Ch 2 | Snare | Lauten LS-408
HPF: 100 | LPF: OFF
B1: +2 | 10000 | 0.8 | SHELF
B2: +2 | 4000 | 1.5 | BELL
B3: -4 | 250 | 2.0 | BELL | DEQ: thr=-16 atk=8ms rel=80ms
B4: +3 | 180 | 1.5 | BELL

## Ch 3 | Underhat | Audix M1280BHC
HPF: 200 | LPF: OFF
B1: +4 | 12000 | 0.8 | SHELF
B2: +4 | 6000 | 1.2 | BELL
B3: -3 | 600 | 2.0 | BELL
B4: -5 | 315 | 1.5 | BELL

## Ch 4 | Rack 1 | Earthworks DM17
HPF: 100 | LPF: 12000
B1: -2 | 8000 | 0.8 | SHELF
B2: +2 | 4000 | 1.2 | BELL
B3: -5 | 315 | 2.0 | BELL | DEQ: thr=-16 atk=8ms rel=100ms
B4: +3 | 200 | 1.5 | BELL

## Ch 5 | Rack 2 | Earthworks DM17
HPF: 100 | LPF: 12000
B1: -2 | 8000 | 0.8 | SHELF
B2: +2 | 4000 | 1.2 | BELL
B3: -5 | 315 | 2.0 | BELL | DEQ: thr=-16 atk=8ms rel=100ms
B4: +3 | 200 | 1.5 | BELL

## Ch 6 | Floor Tom | Earthworks DM17
HPF: 60 | LPF: 10000
B1: -3 | 8000 | 0.8 | SHELF
B2: +2 | 3000 | 1.2 | BELL
B3: -5 | 250 | 2.0 | BELL | DEQ: thr=-12 atk=8ms rel=100ms
B4: +4 | 100 | 1.2 | SHELF

## Ch 7 | OH Left | Earthworks SR20sp G2
HPF: 100 | LPF: OFF
B1: +1 | 12000 | 0.8 | SHELF
B2: +1 | 6000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=20ms rel=200ms
B4: -4 | 200 | 2.0 | SHELF

## Ch 8 | OH Right | Earthworks SR20sp G2
HPF: 100 | LPF: OFF
B1: +1 | 12000 | 0.8 | SHELF
B2: +1 | 6000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=20ms rel=200ms
B4: -4 | 200 | 2.0 | SHELF

## Ch 9 | Bass DI | Artist DI (XLR)
<!-- NOTE: Input list shows XLR only — artist's own DI/rig. Confirm on load-in. -->
HPF: 50 | LPF: 5000
B1: +1 | 3500 | 0.8 | SHELF
B2: +2 | 800 | 1.5 | BELL
B3: -4 | 250 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=100ms
B4: +2 | 80 | 1.2 | SHELF

## Ch 10 | Ac Guitar | Neve RNDI
HPF: 80 | LPF: OFF
B1: +2 | 8000 | 0.8 | SHELF
B2: +2 | 2500 | 1.2 | BELL
B3: -5 | 250 | 2.0 | BELL | DEQ: thr=-16 atk=15ms rel=120ms
B4: -2 | 200 | 1.5 | SHELF

## Ch 11 | Elec Gtr L | DI (XLR)
<!-- NOTE: Artist's own signal chain. Confirm on load-in. -->
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 2500 | 1.5 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=80ms
B4: -3 | 200 | 1.5 | BELL

## Ch 12 | Elec Gtr R | DI (XLR)
<!-- NOTE: Artist's own signal chain. Confirm on load-in. -->
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 2500 | 1.5 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=80ms
B4: -3 | 200 | 1.5 | BELL

## Ch 13 | Piano Low | DPA 4099
<!-- Yamaha C6, closed lid. -->
HPF: 60 | LPF: OFF
B1: +2 | 8000 | 0.8 | SHELF
B2: +1 | 2000 | 1.2 | BELL
B3: -5 | 315 | 2.0 | BELL | DEQ: thr=-14 atk=10ms rel=120ms
B4: -2 | 200 | 1.5 | SHELF

## Ch 14 | Piano Hi | DPA 4099
<!-- Yamaha C6, closed lid. -->
HPF: 120 | LPF: OFF
B1: +3 | 10000 | 0.8 | SHELF
B2: +2 | 3000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=100ms
B4: -3 | 200 | 1.5 | SHELF

## Ch 15 | Tracks L | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: -3 | 315 | 2.0 | BELL
B4: -2 | 200 | 1.5 | SHELF

## Ch 16 | Tracks R | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: -3 | 315 | 2.0 | BELL
B4: -2 | 200 | 1.5 | SHELF

## Ch 17 | Click | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: FLAT
B4: FLAT

## Ch 18 | Video | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: FLAT
B4: FLAT

## Ch 19 | Ziggy Vox | Beta 58
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 20 | Lua Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 21 | Brady Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3500 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 22 | Key Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 23 | Brian Vox | Beta 58
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 24 | John Vox | Beta 56A
<!-- NOTE: Beta 56A is a tom/kick dynamic. Confirm this is correct vs Beta 58. Starting points same as other vocals; heavier high shelf compensates for earlier HF rolloff. -->
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 25 | Test | SM57
<!-- NOTE: Application TBD — adjust all parameters at soundcheck once source confirmed. -->
HPF: 100 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 5000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -3 | 200 | 1.5 | SHELF
