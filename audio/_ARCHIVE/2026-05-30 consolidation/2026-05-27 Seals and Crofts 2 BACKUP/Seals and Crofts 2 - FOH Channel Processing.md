# Seals and Crofts 2 — FOH Channel Processing

<!-- FORMAT: ## Ch {N} | {Console Name} | {Mic/DI}
     HPF: {hz} | LPF: {hz|OFF}
     B1–B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
     FLAT = band bypassed. Omit a channel entirely to leave template untouched.
     Ch 25 and Ch 26 are beyond the 24-strip patcher limit — documented below for console reference only. -->

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

## Ch 9 | Bass DI | Radial Pro DI
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

## Ch 11 | Elec Gtr L | DI
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 2500 | 1.5 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=80ms
B4: -3 | 200 | 1.5 | BELL

## Ch 12 | Elec Gtr R | DI
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 2500 | 1.5 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=80ms
B4: -3 | 200 | 1.5 | BELL

## Ch 13 | Piano Low | DPA 4099
HPF: 60 | LPF: OFF
B1: +2 | 8000 | 0.8 | SHELF
B2: +1 | 2000 | 1.2 | BELL
B3: -5 | 315 | 2.0 | BELL | DEQ: thr=-14 atk=10ms rel=120ms
B4: -2 | 200 | 1.5 | SHELF

## Ch 14 | Piano Hi | DPA 4099
HPF: 120 | LPF: OFF
B1: +3 | 10000 | 0.8 | SHELF
B2: +2 | 3000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-18 atk=10ms rel=100ms
B4: -3 | 200 | 1.5 | SHELF

## Ch 15 | Keys L | Radial DI
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 3000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-16 atk=15ms rel=150ms
B4: -3 | 200 | 1.5 | SHELF

## Ch 16 | Keys R | Radial DI
HPF: 80 | LPF: OFF
B1: +1 | 8000 | 0.8 | SHELF
B2: +2 | 3000 | 1.2 | BELL
B3: -4 | 315 | 2.0 | BELL | DEQ: thr=-16 atk=15ms rel=150ms
B4: -3 | 200 | 1.5 | SHELF

## Ch 17 | Tracks L | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: -3 | 315 | 2.0 | BELL
B4: -2 | 200 | 1.5 | SHELF

## Ch 18 | Tracks R | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: -3 | 315 | 2.0 | BELL
B4: -2 | 200 | 1.5 | SHELF

## Ch 19 | Click | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: FLAT
B4: FLAT

## Ch 20 | Video | Radial DI
HPF: 80 | LPF: OFF
B1: FLAT
B2: FLAT
B3: FLAT
B4: FLAT

## Ch 21 | Ziggy Vox | Beta 58
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 22 | Lua Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 23 | Brady Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3500 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

## Ch 24 | Key Vox | Telefunken M80
HPF: 100 | LPF: 15000
B1: +2 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

<!-- PATCHER LIMIT — Ch 25 and Ch 26 cannot be written by the script (beyond 24-strip range).
     Set manually on console.

Ch 25 | Brian Vox | Beta 58
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF

Ch 26 | John Vox | Beta 56
HPF: 100 | LPF: 15000
B1: +3 | 8000 | 0.7 | SHELF
B2: +3 | 3000 | 1.2 | BELL
B3: -4 | 300 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=80ms
B4: -4 | 200 | 1.5 | SHELF
-->
