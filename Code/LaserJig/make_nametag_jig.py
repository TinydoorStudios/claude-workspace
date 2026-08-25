#!/usr/bin/env python3
"""
Nametag laser-engraving jig generator.

Tag measured / spec'd by Brian 2026-08-13:
    width      76.28 mm
    height     25.35 mm
    thickness   1.40 mm   <- sets pocket depth reasoning

The pocket is the tag outline grown by MARGIN_PCT (2%) on each overall
dimension, so the tag drops in with a small even clearance all round.
Everything below is a parameter. Change a number, re-run, get a new STL.
"""
import numpy as np, trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

# ---------------------------------------------------------------- parameters
TAG_W      = 76.28   # tag width
TAG_H      = 25.35   # tag height
TAG_T      = 1.40    # tag thickness -- the laser-critical number

MARGIN_PCT = 0.02    # 2% insertion margin, added to each overall dimension
POCKET_DEP = 1.00    # pocket depth; tag (1.40) sits 0.40 mm proud for easy grab
PLATE_T    = 3.50    # plate thickness (leaves a 2.50 mm floor under the pocket)

BORDER     = 8.00    # plate edge to pocket, all sides
CORNER_REL = 1.10    # corner-relief circle radius at each pocket corner,
                     #   so a SQUARE-cornered tag seats fully (no inside-radius bind)
PLATE_FIL  = 2.00    # plate outer corner fillet

PUSH_W     = 42.00   # floor push-window width  (pop the tag out from below)
PUSH_H     = 12.00   # floor push-window height
PUSH_R     = 4.00    # push-window corner radius

SEG        = 256     # circle tessellation
OUT        = "nametag_jig.stl"

# ------------------------------------------------------------------ geometry
pk_w = TAG_W * (1.0 + MARGIN_PCT)          # pocket size
pk_h = TAG_H * (1.0 + MARGIN_PCT)
clear_w = (pk_w - TAG_W) / 2.0             # clearance per side, for the readout
clear_h = (pk_h - TAG_H) / 2.0

plate_w = pk_w + 2 * BORDER
plate_h = pk_h + 2 * BORDER
cx, cy  = plate_w / 2.0, plate_h / 2.0     # pocket / plate centre

def rounded_rect(w, h, cx, cy, r, corner_relief=0.0):
    """Axis-aligned rounded rectangle centred at (cx, cy).
    corner_relief > 0 adds a small circle at each true corner so a square part
    seats past the printed inside radius."""
    base = Polygon([(cx - w/2, cy - h/2), (cx + w/2, cy - h/2),
                    (cx + w/2, cy + h/2), (cx - w/2, cy + h/2)])
    if r > 0:
        base = base.buffer(-r, join_style=1).buffer(r, join_style=1)
    if corner_relief > 0:
        corners = [(cx - w/2, cy - h/2), (cx + w/2, cy - h/2),
                   (cx + w/2, cy + h/2), (cx - w/2, cy + h/2)]
        circles = [Point(px, py).buffer(corner_relief, quad_segs=SEG // 4)
                   for px, py in corners]
        base = unary_union([base] + circles)
    return base

pocket_poly = rounded_rect(pk_w, pk_h, cx, cy, r=0.0, corner_relief=CORNER_REL)
push_poly   = rounded_rect(PUSH_W, PUSH_H, cx, cy, r=PUSH_R)

# ---------------------------------------------------------------- build mesh
plate_2d = Polygon([(0, 0), (plate_w, 0), (plate_w, plate_h), (0, plate_h)])
plate_2d = plate_2d.buffer(-PLATE_FIL, join_style=1).buffer(PLATE_FIL, join_style=1)
plate = trimesh.creation.extrude_polygon(plate_2d, PLATE_T)

cuts = []
pk = trimesh.creation.extrude_polygon(pocket_poly, POCKET_DEP + 1.0)
pk.apply_translation([0, 0, PLATE_T - POCKET_DEP])       # cut down from the top face
cuts.append(pk)

win = trimesh.creation.extrude_polygon(push_poly, PLATE_T * 3)
win.apply_translation([0, 0, -PLATE_T])                  # through the floor
cuts.append(win)

jig = trimesh.boolean.difference([plate] + cuts)
jig.export(OUT)

# ------------------------------------------------------------------- readout
# Re-read the exported file so what gets checked is exactly what the slicer opens.
check = trimesh.load(OUT)
tri = check.triangles
up = check.face_normals[:, 2] > 0.99
flat = np.abs(tri[:, :, 2].max(axis=1) - tri[:, :, 2].min(axis=1)) < 1e-6
levels = {}
for i in np.where(up & flat)[0]:
    z = round(float(tri[i, 0, 2]), 4)
    a = tri[i, 1] - tri[i, 0]
    b = tri[i, 2] - tri[i, 0]
    levels[z] = levels.get(z, 0.0) + 0.5 * abs(a[0] * b[1] - a[1] * b[0])

bb = check.bounds
print(f"exported {OUT}")
print(f"  watertight    : {check.is_watertight}   volume {check.volume/1000:.2f} cm3")
print(f"  plate         : {bb[1][0]-bb[0][0]:.2f} x {bb[1][1]-bb[0][1]:.2f} x {bb[1][2]-bb[0][2]:.2f} mm")
print(f"  tag outline   : {TAG_W:.2f} x {TAG_H:.2f} x {TAG_T:.2f} mm")
print(f"  pocket outline: {pk_w:.2f} x {pk_h:.2f} mm  "
      f"(+{clear_w:.2f}/side W, +{clear_h:.2f}/side H)")
print(f"  tag sits proud: {TAG_T - POCKET_DEP:.2f} mm above the plate top")
print("  upward-facing flat surfaces found in the exported mesh:")
for z in sorted(levels, reverse=True):
    if levels[z] < 1.0:
        continue
    tag = "plate top face" if abs(z - PLATE_T) < 1e-6 else \
          f"POCKET FLOOR -> depth {PLATE_T - z:.4f} mm"
    print(f"    z = {z:7.4f}   area {levels[z]:8.1f} mm2   {tag}")
