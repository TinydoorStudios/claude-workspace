# Mustard decode — session state

*2026-07-15. Goal: teach `q225_ses_engine.py` to write DiGiCo Mustard settings, currently all on the engine's `DO_NOT_WRITE_TAGS` list.*

**The result is in [MUSTARD-MAP.md](MUSTARD-MAP.md).** This file is just how to get the rig back.

Earlier drafts of this file mis-identified `0x1D47` as the comp enable and guessed `0x1D41` was the gate threshold. Both were wrong and are corrected in the map. Trust the map, not any memory of this doc.

---

## Rig

The offline editor is a Wine app with no macOS app identity, so the computer-use screenshot tool can never see it. Two workarounds make it drivable:

1. **Launch via `/Applications/Quantum Cal.app`** — a wrapper I created (bundle id `com.tinydoor.quantumcal`) whose `Contents/MacOS/QuantumCal` cds to `~/.wine/drive_c/Quantum2` and execs wine64 on `Quantum2.exe`. Launching `Quantum 225.app` directly produces a process macOS can't grant. `request_access` on "Quantum Cal", then `open_application` to front it.
2. **Screenshots from the shell**: run `cap.sh`, then Read `cur_s.png`.

Healthy offline launch = log shows `starting software version 22.0.2242` then `AudioMaster switched to MASTER`, with **no** `EngineMessenger Client socket error 10065` spam. Log: `~/.wine/drive_c/Quantum2/Log.txt`. Sessions live in `~/.wine/drive_c/Projects/`.

### COORDINATE SCALE — read this first

`cur_s.png` is 1728 px wide; computer-use clicks are in a **1372-wide** space:

> **click = screenshot_coord × 0.794**

Unscaled clicks land harmlessly, the tool still says "Clicked.", and nothing moves. If a control won't respond, check this before anything else. It cost an hour.

### Opening the Mustard page (Brian's gesture)

1. Front Channel Surface 1 — click **(1300, 49)**
2. On the channel strip, click the **M** button next to SD — CH1 = **(198, 584)**. This switches the strip from the SD dynamics to the Mustard section. *Nothing works until M is lit.*
3. **Right-click the comp threshold knob** on that strip — CH1 = **(182, 469)**. Takes **two** right-clicks after fronting: the first only fronts the window.

The page **closes on every save**, so repeat 1–3 before each capture.

### Known-good click coords (already scaled)

Master front (1207,49) · Files (302,65) · Save As new file (302,170) · filename field (484,256) · Save (1047,631).

Mustard page: D1 type (515,730) · mix (495,759) · thresh (580,759) · attack (659,759) · release (740,759) · ratio (820,759) · gain (900,759) · soft/hard (660,780) · RMS/peak (740,780) · s/c listen (900,780) · D1 low (979,756) · D1 filter on/off (1001,769) · D1 high (1063,756) · D1 on (398,768).
D2 type (515,805) · thresh (578,832) · attack (658,832) · hold (738,832) · release (819,832) · range (899,832) · D2 low (979,831) · D2 filter (1001,844) · D2 high (1063,831) · D2 on (398,842).
Type menus (after clicking a type button): entries at x=405, y = 557 / 578 / 598 / 619 / 639.

Channel strip pitch = **80 click-px**, so CH_n M button = 198 + 80(n−1), thresh knob = 182 + 80(n−1).

**Filename entry:** clicking the field opens an on-screen keyboard and selects the old name; physical typing does NOT reach it. Keys: M(745,417) C(580,417) .(827,417) S(517,376) E(539,335) · digits 0(807,294) 1(435,294) 2(477,294) 3(518,294) 4(558,294) 5(612,294) 6(642,294) 7(683,294) 8(723,294) 9(765,294). So "mc19.ses" = M,C,1,9,.,S,E,S then Save.

**Save flow quirk:** the click that fronts the Master screen gets consumed — if the Files menu doesn't drop, click Files again rather than assuming the batch worked. Always screenshot the filename field before hitting Save.

---

## Captures (in `~/.wine/drive_c/Projects/`)

| File | Change |
|---|---|
| mc00 | baseline, no change |
| mc01 | UI navigation only (proves the UI-state region is not audio) |
| mc02 | comp IN |
| mc03 | comp thresh −20 → −9.88 |
| mc04 | makeup gain 0 → 0.92 |
| mc05 | ratio 3 → 4.04 |
| mc06 | mix 90, attack 12.4 mS, release 312 mS |
| mc07 | gate thresh −14.1, attack 3.20, hold 187, release 183, range 46.2 |
| mc08 | soft/hard → soft, sc low 39.4, sc high 10.2k |
| mc09 | RMS → peak, gate sc low 36.3, gate sc high 11.3k |
| mc10 | s/c listen (not stored), gate ON |
| mc11 | comp sc filter on, gate sc filter on |
| mc12 | comp type → Red / Vintage VCA |
| mc13 | comp type → Purple / Optical |
| mc14 | comp type → Green / FET |
| mc15 | comp type → Silver / Levelling Amp |
| mc16 | gate type → Duck |
| mc17 | gate type → MSE |
| mc18 | **CH2** comp thresh −20 → −13.9 (stride) |

---

## Next

**CONSOLE-VERIFIED 2026-07-16 — Mustard is production.** Brian loaded a Back to Black test build on the Q225 (all five comp models, Gate/Duck/MSE) and confirmed every value. The console does NOT re-apply the type→defaults reset on load. The real Back to Black.ses was regenerated with reasoned Mustard, and the pipeline is wired (`md_lint` validates `COMP:`/`GATE:`; `show-deep-build` emits them). Details at the top of [HANDOFF.md](HANDOFF.md).

**Step 2 (the engine work) is done** — see HANDOFF.md, including three corrections to the map that mattered (absolute offsets unusable, framing inverted vs EQ, `0x1D00`/`0x1E00` are headers). What remains:

1. Capture the leftovers listed at the bottom of the map (the gate's key-source buttons, the MSE release 3-state, and the unknown zero-resting tags). Levelling Amp gain / peak reduction / compress-limit are mapped and written.
2. Teach `md_lint.py` the `COMP:` / `GATE:` lines, and have show-deep-build emit them.
3. Human gate unchanged: Brian loads a patched file on the Q225 and says "verified." **Nothing Mustard has been console-verified.**

Note the editor was left with an unsaved MSE-release change on top of `mc20` — check the Master screen's `*` flag before trusting its state.
