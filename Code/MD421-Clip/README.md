# MD421 → SM58-clip adapter (Wilkinson-style)

A parametric 3D-printable replacement for the discontinued Wilkinson Audio MD421
clip. It slides onto the Sennheiser MD 421-II's underside rail (same interface the
stock clip uses) and presents a standard ~22 mm vocal-mic bar underneath, so the
mic drops into any SM57/SM58 / A25D-style clip you already own.

## Files
- `md421_clip.scad` — the parametric source. Edit the parameter block at the top, re-render.
- `md421_clip.stl` — the full adapter, ready to slice.
- `md421_clip_coupon.stl` — a short test stub (rail + latch only). **Print this first.**
- `preview_iso.png` / `preview_side.png` — renders.

Re-render after any edit:
```bash
/opt/homebrew/bin/openscad -o md421_clip.stl md421_clip.scad
/opt/homebrew/bin/openscad -D 'part="coupon"' -o md421_clip_coupon.stl md421_clip.scad
```

## ⚠ Read this before printing all three
The MD421's rail interface is **not published anywhere**. The `MIC RAIL INTERFACE`
numbers in the .scad are reverse-engineered by eye from teardown photos, scaled
against the mic's known 215 × 46 × 49 mm body. They are a **starting estimate**, not
measured truth. A slide-fit that's 0.3 mm off will either jam or fall out.

**So the workflow is: print the coupon, fit it to a real mic, adjust one number, repeat.**
The coupon is ~2 g of filament and prints in minutes — cheap to iterate. Only cut the
full clip once the coupon slides on and the latch clicks.

## Tuning workflow
1. Print `md421_clip_coupon.stl`.
2. Try to slide it into the mic's rail channel (the recess by the "MD 421 II" nameplate).
   - **Won't go in / too tight:** raise `fit` (0.35 → 0.45) *or*, if it's binding on
     width specifically, raise `chan_w_deep` / `chan_w_open` by ~0.5.
   - **Slides but rattles / falls out:** lower `fit` (0.35 → 0.25).
   - **Goes in but won't seat fully / bottoms out early:** raise `chan_len` or lower `tongue_len`.
   - **Latch never clicks:** adjust `lock_from_mouth` (move the detent toward/away from the
     mouth to line up with the mic's lock hole), then `bump_h` for how firmly it grabs.
3. Once the coupon is right, those same numbers carry straight into the full clip. Re-render and print it.
4. Check the stem in one of your SM58 clips:
   - **Loose in the clip:** raise `stem_dia` (22 → 23) or, for 1" clips, set `stem_dia = 25`.
   - **Mic aims wrong on the stand:** change `stem_tilt` (degrees; + leans the bar toward the grille).

Everything above is a single-number edit + re-render. No CAD skills needed.

## Print settings
- **Material:** PETG or ABS/ASA. This part takes the mic's whole weight through a small
  neck — PLA will creep and get brittle. PETG is the sweet spot for toughness + easy printing.
- **Orientation:** lay it **on its side** (stem axis roughly parallel to the bed, tongue in
  the same plane) so the layer lines run *along* the neck and stem. That puts the mic's
  cantilever load along the fibers, not across them — the neck is exactly where stock clips
  snap. Do **not** print it standing straight up.
- **Walls / infill:** 4+ perimeters, 40–60 % infill. This is a structural part, not a bracket.
- **Supports:** minimal if laid on its side; the release pad and stem tip may want a touch.
- **Layer height:** 0.2 mm is fine; 0.16 mm gives a cleaner slide fit on the rail.

## How the latch works
The two rails slide under the channel's ledges. The central finger is a cantilever with a
detent bump that snaps into the mic's lock hole. To remove: pull the mic off with a firm tug
(the bump is chamfered so it ramps out), or pull the ribbed pad hanging below to retract it
first. It's a friction-snap, not the fragile spring-button of the original — that's the point.

---
Built 2026-08-23. Rail dims are estimates — trust the coupon, not the CAD.
