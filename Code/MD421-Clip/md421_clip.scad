// ============================================================================
//  MD421 -> SM58-clip adapter   (Wilkinson-style, parametric)
//  Slides onto the Sennheiser MD 421-II underside rail and presents a
//  standard ~22 mm vocal-mic bar so the mic drops into any SM57/SM58 /
//  A25D-style clip.
//
//  NOTE ON DIMENSIONS: the MD421 rail interface is NOT published anywhere.
//  The RAIL-INTERFACE block below is reverse-engineered by eye from teardown
//  photos scaled against the mic's known 215 x 46 x 49 mm body. Treat those
//  numbers as a starting point. Print the TEST COUPON first (set part="coupon"),
//  check the slide + latch on a real mic, then adjust ONE number and re-render.
//
//  Units: millimetres.   Nyquist, 2026-08-23.
// ============================================================================

part = "clip";     // "clip" = full adapter | "coupon" = rail+latch test stub only

// ---- GLOBAL FIT --------------------------------------------------------------
fit          = 0.35;   // clearance per mating face. Tight? raise to 0.45. Loose? drop to 0.25.

// ---- MIC RAIL INTERFACE  (TUNE THESE FIRST — female pocket on the mic) --------
chan_len       = 30.0;  // usable slide length of the mic's recess channel
chan_w_deep    = 12.0;  // channel width at the floor (widest, under the ledges)
chan_w_open    = 8.0;   // slot opening width at the mic surface (between ledges)
chan_depth     = 4.5;   // depth from mic surface down to the channel floor
ledge_h        = 2.2;   // height of the narrow opening region (ledge thickness)
lock_from_mouth= 22.0;  // mouth -> lock-hole centre, along the slide
lock_dia       = 3.5;   // lock-hole diameter in the channel floor

// ---- TONGUE (male, what we print) -------------------------------------------
tongue_len   = 26.0;                 // <= chan_len
web_h        = ledge_h;              // narrow section height (through the opening)
flange_h     = chan_depth - ledge_h; // wide section height (captured under ledges)
web_w        = chan_w_open  - 2*fit; // narrow width
flange_w     = chan_w_deep  - 2*fit; // wide width (the capture wings)
tongue_topfit= 0.4;                  // gap so the tongue doesn't bottom hard on the floor

// ---- LATCH (cantilever finger + snap detent) --------------------------------
finger_w     = 3.6;
finger_t     = 1.6;                  // beam thickness -> flex stiffness
finger_slot  = finger_w + 2*fit;    // central slot the finger flexes in
finger_len   = lock_from_mouth + 4; // reaches just past the lock hole
bump_dia     = lock_dia - 0.3;      // detent that snaps into the lock hole
bump_h       = flange_h*0.85;       // protrusion into the hole
pad_drop     = 7.0;                 // release pad hangs this far below mic surface
pad_len      = 9.0;
pad_w        = 7.0;

// ---- SPINE / NECK (the strong bit at the mouth, ties everything together) ----
spine_len    = 9.0;   // block length just OUTSIDE the recess mouth (-X)
spine_w      = flange_w + 6;
neck_drop    = 16.0;  // how far below the mic surface the stem shoulder sits

// ---- STEM (SM58-style gripping bar) -----------------------------------------
stem_dia     = 22.0;  // gripping diameter. 1" clips: try 25.0.  Loose clip: +0.5.
stem_len     = 40.0;  // gripped length below the shoulder
stem_tilt    = 15.0;  // deg: leans the bar toward the grille so the mic aims up
shoulder_dia = 27.0;  // stop shoulder so the mic seats above the clip jaws
shoulder_h   = 3.5;
stem_end_r   = 6.0;   // rounded bar tip

// ---- QUALITY -----------------------------------------------------------------
$fn = 72;
eps = 0.01;

// ============================================================================
//  BUILD
// ============================================================================
if (part == "coupon") coupon(); else clip();

module clip() {
    union() {
        tongue();
        latch();
        spine_and_neck();
        stem_assembly();
    }
}

// A short stub with just the rail + latch, for cheap fit testing on the mic.
module coupon() {
    union() {
        tongue();
        latch();
        // small handle block at the mouth so you can grip/pull it
        translate([-8, -spine_w/2, -6])
            cube([8, spine_w, 6 + chan_depth]);
    }
}

// ---- tongue: two T-profile rails split by the central finger slot ------------
module rail_half() {
    // narrow web near the opening (z: 0..web_h), wide flange deeper (z: web_h..)
    total_h = min(web_h + flange_h, chan_depth - tongue_topfit);
    union() {
        // web (through the slot opening)
        translate([0, finger_slot/2, 0])
            cube([tongue_len, (web_w - finger_slot)/2, web_h]);
        // flange (capture wing, under the ledge)
        translate([0, finger_slot/2, web_h])
            cube([tongue_len, (flange_w - finger_slot)/2, total_h - web_h]);
    }
}
module tongue() {
    // lead-in chamfer on the tip so it starts into the channel easily
    chamf = 1.2;
    intersection() {
        union() { rail_half(); mirror([0,1,0]) rail_half(); }
        // clip the +X tip corners
        translate([-eps, -flange_w, -eps])
            cube([tongue_len - chamf, 2*flange_w, chan_depth]);
    }
    // rebuild the chamfered tip
    hull() {
        translate([tongue_len - chamf, -flange_w/2, 0])            cube([eps, flange_w, web_h]);
        translate([tongue_len, -web_w/2, 0])                        cube([eps, web_w, web_h]);
    }
}

// ---- latch: cantilever finger anchored at the mouth, detent near the tip -----
module latch() {
    zf = chan_depth - tongue_topfit - finger_t;   // finger sits at the deep level
    union() {
        // the beam
        translate([-2, -finger_w/2, zf])
            cube([finger_len + 2, finger_w, finger_t]);
        // detent bump (frustum -> self-ramping in and out)
        translate([lock_from_mouth, 0, chan_depth - tongue_topfit])
            cylinder(h = bump_h, d1 = bump_dia, d2 = bump_dia*0.55);
        // release pad hanging below the mic surface at the detent station
        translate([lock_from_mouth - pad_len/2, -pad_w/2, -pad_drop])
            cube([pad_len, pad_w, pad_drop + zf + eps]);
        // grip ribs on the pad
        for (i = [0:2])
            translate([lock_from_mouth - pad_len/2, -pad_w/2 - 0.6, -pad_drop + 1.5 + i*2])
                cube([pad_len, 0.6, 1.0]);
    }
}

// ---- spine + neck: strong root outside the mouth, drops toward the stem ------
module spine_and_neck() {
    // spine block ties the rails at the deep level; lives OUTSIDE the recess (-X)
    hull() {
        translate([-spine_len, -spine_w/2, 0])
            cube([spine_len, spine_w, chan_depth - tongue_topfit]);
        translate([-spine_len, -spine_w/2, 0])
            cube([eps, spine_w, chan_depth - tongue_topfit]);
    }
    // neck: smooth column from the spine bottom down to the stem shoulder top
    hull() {
        translate([-spine_len, -spine_w/2, -eps])
            cube([spine_len, spine_w, eps]);
        stem_top_marker();
    }
}

// small disc at the shoulder top — the neck lofts down to this, keeping the
// transition a clean column instead of a wide funnel.
module stem_top_marker() {
    translate([-spine_len/2, 0, -neck_drop])
        rotate([0, stem_tilt, 0])
            cylinder(h = eps, d = shoulder_dia);
}

// ---- stem: chamfered stop shoulder + gripping bar + rounded tip -------------
module stem_assembly() {
    translate([-spine_len/2, 0, -neck_drop])
        rotate([0, stem_tilt, 0])
            stem();
}
module stem() {
    // built pointing -Z (downward), origin at the shoulder top
    union() {
        // chamfered stop shoulder (frustum: wide at top -> stem_dia at bottom)
        translate([0,0,-shoulder_h])
            cylinder(h = shoulder_h + eps, d1 = stem_dia, d2 = shoulder_dia);
        // gripping bar
        translate([0,0,-shoulder_h - stem_len + stem_end_r])
            cylinder(h = stem_len - stem_end_r + eps, d = stem_dia);
        // rounded tip
        translate([0,0,-shoulder_h - stem_len + stem_end_r])
            sphere(d = stem_dia);
    }
}
