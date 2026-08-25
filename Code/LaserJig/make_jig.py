#!/usr/bin/env python3
"""
RFID keyfob laser-engraving jig generator.

Fob is a teardrop = convex hull of two circles (big round end + smaller nose).
Measured off Brian's fob 2026-08-06:
    widest point (round end dia) 32.21
    overall length               40.18
    width across nose            22.00
    thickness                    3.70

Everything below is a parameter. Change a number, re-run, get a new STL.
"""
import math, numpy as np, trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

# ---------------------------------------------------------------- parameters
FOB_WIDE   = 32.21   # widest point, round end
FOB_LEN    = 40.18   # overall length, nose tip to bottom of round end
FOB_NOSE   = 22.00   # width across the nose
FOB_THICK  = 3.70    # sets pocket depth exactly -- the laser-critical number

CLEAR      = 0.30    # clearance per side; pocket is offset outward by this
POCKET_DEP = FOB_THICK          # flush: fob top level with plate top face
PLATE_T    = 6.00    # plate thickness (leaves 2.3 mm floor under the pocket)

N_POCKETS  = 2
MARGIN     = 9.00    # plate edge to pocket
GAP        = 11.00   # between the two pockets
PUSH_DIA   = 12.00   # through-hole under each pocket, to push the fob out
CORNER_R   = 1.00    # plate corner fillet
SEG        = 256     # circle tessellation

OUT = "keyfob_jig_2up.stl"

# ------------------------------------------------------------------ geometry
def teardrop(wide, length, nose, grow=0.0):
    """Convex hull of two circles. Origin at the centroid of the bounding box.
    +Y is toward the nose."""
    R = wide / 2.0 + grow
    r = nose / 2.0 + grow
    d = length - (wide / 2.0) - (nose / 2.0)      # centre-to-centre, unchanged by grow
    if d <= 0:
        raise ValueError("length too short for those two widths")
    if d <= abs(R - r):
        raise ValueError("nose circle swallowed by the body circle")
    big  = Point(0.0, 0.0).buffer(R, quad_segs=SEG // 4)
    small = Point(0.0, d).buffer(r, quad_segs=SEG // 4)
    hull = unary_union([big, small]).convex_hull
    # recentre on the bounding box so pocket spacing is easy to reason about
    minx, miny, maxx, maxy = hull.bounds
    return hull, (maxx - minx), (maxy - miny), (miny + maxy) / 2.0

pocket_poly, pk_w, pk_l, pk_yc = teardrop(FOB_WIDE, FOB_LEN, FOB_NOSE, grow=CLEAR)
fob_poly,    fb_w, fb_l, _     = teardrop(FOB_WIDE, FOB_LEN, FOB_NOSE, grow=0.0)

plate_w = 2 * MARGIN + N_POCKETS * pk_w + (N_POCKETS - 1) * GAP
plate_l = 2 * MARGIN + pk_l

# pocket centres, measured from the plate's bottom-left corner
xs = [MARGIN + pk_w / 2 + i * (pk_w + GAP) for i in range(N_POCKETS)]
yc = MARGIN + pk_l / 2

# ---------------------------------------------------------------- build mesh
plate_2d = Polygon([(0, 0), (plate_w, 0), (plate_w, plate_l), (0, plate_l)])
plate_2d = plate_2d.buffer(-CORNER_R, join_style=1).buffer(CORNER_R, join_style=1)
plate = trimesh.creation.extrude_polygon(plate_2d, PLATE_T)

cuts = []
for x in xs:
    p = trimesh.creation.extrude_polygon(pocket_poly, POCKET_DEP + 1.0)
    p.apply_translation([x, yc - pk_yc, PLATE_T - POCKET_DEP])
    cuts.append(p)
    h = trimesh.creation.cylinder(radius=PUSH_DIA / 2, height=PLATE_T * 3, sections=SEG // 2)
    h.apply_translation([x, yc - pk_yc, 0])
    cuts.append(h)

jig = trimesh.boolean.difference([plate] + cuts)
jig.export(OUT)

# ------------------------------------------------------------------- readout
# Verify by re-reading the exported file, not the in-memory mesh, so what gets
# checked is exactly what the slicer will open.
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

print(f"exported {OUT}")
print(f"  watertight    : {check.is_watertight}   volume {check.volume/1000:.2f} cm3")
bb = check.bounds
print(f"  plate         : {bb[1][0]-bb[0][0]:.2f} x {bb[1][1]-bb[0][1]:.2f} x {bb[1][2]-bb[0][2]:.2f} mm")
print(f"  fob outline   : {fb_w:.2f} wide x {fb_l:.2f} long")
print(f"  pocket outline: {pk_w:.2f} wide x {pk_l:.2f} long   (+{CLEAR:.2f} per side)")
print("  upward-facing flat surfaces found in the exported mesh:")
for z in sorted(levels, reverse=True):
    if levels[z] < 1.0:
        continue
    tag = "plate top face" if abs(z - PLATE_T) < 1e-6 else \
          f"POCKET FLOOR -> depth {PLATE_T - z:.4f} mm"
    print(f"    z = {z:7.4f}   area {levels[z]:8.1f} mm2   {tag}")
print("  pocket centres, from the plate's bottom-left corner:")
for i, x in enumerate(xs, 1):
    print(f"    pocket {i}:  X {x:.3f}   Y {yc:.3f}")
