// ─────────────────────────────────────────────────────────────
// Neutrik XXR-* Color Coding Ring  (XX-series XLR)
// Straight-walled hollow cylinder.
//   Inner diameter : 18.60 mm
//   Wall thickness : 1.27 mm  ->  Outer diameter 21.14 mm
//   Width          : 7.00 mm
// ─────────────────────────────────────────────────────────────

inner_D = 18.60;
wall    = 1.27;
width   = 7.00;

outer_D = inner_D + 2*wall;   // 21.14 mm

$fn = 200;

difference() {
    cylinder(h = width, d = outer_D, center = false);
    translate([0, 0, -0.5])
        cylinder(h = width + 1, d = inner_D, center = false);
}
