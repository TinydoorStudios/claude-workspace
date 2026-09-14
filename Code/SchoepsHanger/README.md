# Schoeps Mic Hanger — Neumann MNV 87 MT clamp unit

3D-printable copy of the **Neumann MNV 87 MT** clamp, sized for a **Schoeps
CMC 6** body (20.0 mm). Flat paddle with, top to bottom:

- **3/8"-16 threaded stud + knurled collar** — the mount (screws into a
  hanger adapter, stand thread, or the chrome 3/8→5/8 reducer)
- flat body with **two round lightening holes**
- **knurled thumbwheel tilt-lock** — pivot pin + arc slot set and lock the aim
- **mic cradle** with internal grip ribs that grips the 20 mm body

> The mic grip is a C-collar cradle (full wrap + front mouth + grip ribs),
> not the literal two-finger spring jaw of the original — it holds a hung mic
> more securely. A two-finger variant is a quick edit if you want the exact look.

## Files
- `schoeps_hanger.scad` — parametric source (`tilt=` previews the aim angle)
- `jaw.stl`  — mic cradle + pivot plate (print 1)
- `base.stl` — body, lightening holes, tilt arc slot, collar + threaded stud (print 1)
- `knob.stl` — knurled tilt thumbwheel (print 1)
- `assembly.png` / `tilted.png` — previews, not for slicing

Re-export after edits:
```
openscad -o jaw.stl  -D 'part="jaw"'  schoeps_hanger.scad
openscad -o base.stl -D 'part="base"' schoeps_hanger.scad
openscad -o knob.stl -D 'part="knob"' schoeps_hanger.scad
```

## Hardware
| Where | Bolt | Retainer |
|---|---|---|
| Tilt pivot pin | M3 × 16 | M3 nut (captive in the jaw plate) |
| Tilt clamp (through the arc slot) | M4 × 20 | the printed knurled knob (M4 nut captive) |

Loosen the knob, tilt the mic to aim, retighten — friction over the arc slot
holds the angle.

## Print
- **Material:** PETG (some flex for the cradle mouth, tough enough to hang).
  ASA/Nylon fine. Not brittle PLA over people.
- **Walls/infill:** 4 perimeters, ≥40% — load path.
- **Layers:** 0.2 mm body; **0.12 mm** if you want the 3/8" stud thread to
  come out cleanly (or run a 3/8-16 die over it). If the thread is fussy,
  print the stud as a plain post and glue in a 3/8" threaded insert instead.
- **Orientation:** base standing with the stud up (support the arc-slot
  overhang); jaw with the cradle mouth to the side; knob flat.

## Use
- The cradle snaps onto the 20 mm body; line it with gaffer/felt to protect
  the finish and firm the grip. Add a safety line for an overhead hang.
- Mount via the 3/8" stud, aim with the thumbwheel.

## Key dimensions (edit in the .scad)
- `bore = 20.3`  (mic 20.0 + clearance)
- `mouth`        cradle opening — narrower grips harder
- `stud_maj/stud_p`  thread size (default 3/8"-16)
- `arc_deg`      tilt range (±28°)
