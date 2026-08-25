# ORTF Holder — 2× Schoeps CMC6

Printable dual-mic holder for two CMC6 bodies in **classic ORTF**
(170 mm diaphragm spacing, 110° included angle) that threads onto a standard
US mic stand (**5/8"-27**). Free-standing snap-in C-cradles up top; two tapered
legs tie them to the central threaded boss **entirely below the bore**, so the
round mic seat stays clear (no flat under the body) and the cradle lips can flex
to snap the mic in. No hardware.

Files:
- `ortf_holder.scad` — parametric source (edit this to tune)
- `ortf_holder.stl` — ready to slice
- `hero.png`, `section.png` — reference renders (`section.png` shows the stop shoulder)

## How the angle and spacing are guaranteed

**The 110° angle is built into the print** — the fixed leg geometry and cradle
yaw set it. It cannot be wrong, regardless of how the mic sits.

**The 170 mm spacing is set by a hard depth stop, not by eye.** Each cradle has
an internal shoulder at its front (capsule) end. Drop the mic in from the top,
push it forward until the **front face of the CMC6 body (the capsule joint)
bottoms on the shoulder**, and the diaphragm lands in the same place every
time. The snap grip holds it there. No logo alignment, no eyeballing, no test
prints.

## The one number to set: `capsule_len`

The stop references the body/capsule joint, so the design only needs to know how
far the diaphragm sits ahead of that joint.

`capsule_len` (default **22 mm**) = distance, measured once with calipers, from
the **front face of the CMC6 tube** (where the capsule threads on) to the
**diaphragm** (≈ the front of the capsule grille). Set it and re-export — the
stop then places the diaphragms at exactly ±85 mm / 110°.

- MK4 / MK41 / MK5 differ slightly in length; measure whichever capsule pair
  lives on this bar and set `capsule_len` to match. Use a matched pair (same
  capsule) on both sides — that keeps the array symmetric.
- Rotation of the mic in the cradle (which way the logo faces) is acoustically
  irrelevant with these end-addressed capsules, so there's nothing to align
  there. Seat it however looks tidy.

`spacing` (170) and `included_angle` (110) are the ORTF standard — leave them
unless you deliberately want NOS/DIN/etc.

## Printing

- **Material:** PETG or PLA+ (PETG preferred — the snap clips flex without
  snapping cold). ABS/ASA fine too.
- **Layer height:** 0.16 mm or finer. The 5/8"-27 thread is fine-pitch
  (0.94 mm / 27 TPI) — coarse layers make a rough thread. 0.12 mm is best.
- **Walls/infill:** 4 perimeters, 40%+ infill. This holds real mics; don't go
  hollow.
- **Orientation:** print it **as modeled** — boss down on the bed, cradles up,
  snap gaps facing up. Thread axis stays vertical (cleanest threads) and the
  cradles are open U-channels facing up (no support inside them).
- **Supports:** the two legs cantilever out from the boss, so add supports under
  the legs (tree/organic supports work well). The cradles and the thread need
  none.
- **First fit:** the cradle bore is 20.3 mm (0.15 mm/side clearance) with a
  ~15 mm top mouth so it snaps and retains. If the snap is too tight/loose,
  nudge `fit_clearance` or `mouth_chord`. The front stop hole is 17 mm
  (`stop_id`); it just needs to catch the 20 mm body rim while clearing whatever
  protrudes from the capsule joint — widen it if your capsule has a fat collar.

## Thread notes

- Default is **right-hand** (`thread_hand = -1`), which is what a normal stand
  stud wants. If a test print threads on backwards, flip `thread_hand` to `+1`
  and re-export — that's the only change needed.
- Run the stud in gently the first time; a printed thread self-clears.
- **If the printed thread ever strips:** counterbore the boss and epoxy in a
  5/8"-27 brass mic-clip nut. Say the word and I'll model the counterbore
  variant.

## Regenerate the STL

```bash
openscad -o ortf_holder.stl ortf_holder.scad
```

Nyquist
