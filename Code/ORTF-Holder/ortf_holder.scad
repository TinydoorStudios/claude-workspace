// ============================================================
// ORTF holder for two Schoeps CMC6 bodies
// Classic ORTF: 170 mm capsule spacing, 110 deg included angle
//
// Free-standing snap-in C-clips (flex to admit the 20 mm body,
// retain it). Two tapered legs tie the clips to a central boss
// ENTIRELY BELOW the mic bore -- the round cradle stays clear.
// Central boss carries a 5/8"-27 female thread for a US stand.
//
// Units: millimeters.  Nyquist / Brian Lloyd
// ============================================================

// ---------- MIC BODY ----------
body_d          = 20.0;   // CMC6 amplifier tube diameter
fit_clearance   = 0.15;   // radial slip clearance per side in the cradle
clip_wall       = 3.0;    // C-clip wall thickness (thinner = easier snap)
clip_len        = 26.0;   // grip length along the body
mouth_chord     = 15.0;   // top opening width (< body_d so it snaps & retains)
lip_round       = 1.2;    // rounding on the lip tips so the mic cams them open

// ---------- DEPTH STOP (the real fix) ----------
// The front of each cradle has an internal shoulder. Push the mic forward
// until the body's FRONT FACE (the capsule joint) bottoms on it -> the
// diaphragm lands in the same spot every time. No eyeballing.
stop_id         = 17.0;   // shoulder inner diameter (catches the 20 mm body
                          // front rim; capsule sits forward of it in free air)
stop_t          = 2.5;    // shoulder thickness

// ---------- ORTF GEOMETRY ----------
spacing        = 170.0;   // diaphragm-to-diaphragm spacing (classic ORTF)
included_angle = 110.0;   // included angle between mic axes (classic ORTF)
capsule_len    = 22.0;    // <-- MEASURE THIS ONCE, with calipers.
                          // Distance from the body/capsule JOINT (the front
                          // face of the CMC6 tube) to the diaphragm (~ the
                          // front of the capsule grille). Set it and the stop
                          // puts the diaphragms at exactly 170 mm / 110 deg.
                          // No test prints needed. 22 = nominal MK4.

// ---------- MOUNT ----------
thread_major    = 15.875; // 5/8" major diameter
thread_pitch    = 0.9407; // 27 TPI  (25.4/27)
thread_len      = 12.0;   // engagement depth
thread_clear    = 0.35;   // print clearance added to female major
thread_hand     = -1;     // -1 = right-hand (standard). Flip to +1 only if a
                          // test print threads on backwards.
boss_d          = 26.0;   // outer diameter of the mount boss
boss_extra      = 7.0;    // boss wall below the thread bottom

// ---------- STRUCTURE ----------
bore_height     = 26.0;   // bore centerline height above the mount face
leg_w           = 18.0;   // leg width
$fn             = 96;

// ------------------------------------------------------------
// Derived
half_ang    = included_angle/2;                 // 55
bore_r      = body_d/2 + fit_clearance;         // cradle radius (10.15)
out_r       = bore_r + clip_wall;               // clip outer radius (13.15)
gap_ang     = 2*asin(min(0.99, mouth_chord/(2*bore_r))); // top opening angle
ax          = [sin(half_ang), cos(half_ang)];   // right mic axis unit (X,Y)
// diaphragm sits (clip_len/2 - stop_t + capsule_len) forward of the clip center,
// because the body front face bottoms on the stop at (clip_len - stop_t).
dia_fwd     = clip_len/2 - stop_t + capsule_len;
clip_cx     = spacing/2 - ax[0]*dia_fwd;         // clip center X for 170 mm
axis_deg    = atan2(ax[1], ax[0]);              // body axis angle from +X (=35)
H           = bore_height;                      // bore centerline Z
bore_bottom = H - bore_r;                       // lowest point of the bore
clip_bottom = H - out_r;                        // lowest point of the clip wall

// ============================================================
// 5/8"-27 female thread (cut a male tool out of the boss)
// ============================================================
module male_thread(major_d, pitch, length){
    tooth   = 0.587*(pitch/0.9407);
    minor_d = major_d - 2*tooth;
    turns   = length/pitch;
    rh = 0.48*pitch;
    ch = 0.12*pitch;
    intersection(){
        cylinder(h=length, d=major_d);
        union(){
            cylinder(h=length, d=minor_d+0.02);
            linear_extrude(height=length, twist=thread_hand*360*turns,
                           slices=max(4, ceil(48*turns)), convexity=12)
                translate([minor_d/2 - 0.02, 0])
                    polygon([[0,-rh],[tooth,-ch],[tooth,ch],[0,rh]]);
        }
    }
}

// ============================================================
// C-clip: bore along local +X, gap on top (+Z). Free-standing
// so the lips can flex. Rounded lip tips + bore lead-in.
// ============================================================
// bore along +X, x=0 is the REAR (cable side), x=clip_len is the FRONT
// (capsule side) where the depth-stop shoulder lives.
module cclip(){
    difference(){
        rotate([0,90,0]) cylinder(h=clip_len, r=out_r);   // body
        // main bore -- grip region, stops at the shoulder
        rotate([0,90,0]) translate([0,0,-1])
            cylinder(h=clip_len - stop_t + 1, r=bore_r);
        // lip bore -- smaller hole through the front stop shoulder
        rotate([0,90,0]) translate([0,0,clip_len - stop_t])
            cylinder(h=stop_t + 1, r=stop_id/2);
        // top opening wedge (full length, incl. through the shoulder)
        rotate([0,90,0]) translate([0,0,-1])
            linear_extrude(height=clip_len+2)
                polygon([[0,0],
                         [ (out_r+3)*sin(gap_ang/2), (out_r+3)*cos(gap_ang/2)],
                         [ 0, out_r+4],
                         [-(out_r+3)*sin(gap_ang/2), (out_r+3)*cos(gap_ang/2)]]);
        // lead-in chamfer at the rear mouth (drop-in / cable side)
        translate([lip_round,0,0]) rotate([0,-90,0])
            cylinder(h=lip_round+0.02, r1=bore_r, r2=bore_r+lip_round);
    }
    // round the two lip tips (cam-in). Fillet cylinders along the axis.
    for(s=[-1,1])
        rotate([0,90,0])
            rotate([0,0, s*gap_ang/2])
                translate([bore_r+clip_wall/2, 0, 0])
                    cylinder(h=clip_len, r=clip_wall/2);
}

module placed_clip(sign){
    translate([sign*clip_cx, 0, H])
        rotate([0,0, sign>0 ? axis_deg : 180-axis_deg])
            translate([-clip_len/2,0,0])
                cclip();
}

// ============================================================
// Two tapered legs from the central boss out to under each clip,
// staying BELOW the bore. Plus the boss itself.
// ============================================================
mount_bottom = -(thread_len + boss_extra);   // bottom face of the boss

module leg(sign){
    hull(){
        // central root at the boss
        translate([0,0,0]) cylinder(h=12, d=boss_d-2);
        // foot directly under the clip, top flush with bore bottom
        translate([sign*clip_cx, 0, bore_bottom-4])
            rotate([0,0, sign>0 ? axis_deg : 180-axis_deg])
                cube([clip_len*0.85, leg_w, 8], center=true);
    }
}

module boss(){
    difference(){
        translate([0,0,mount_bottom])
            cylinder(h = 12 - mount_bottom, d = boss_d);
        // thread, opening downward from the bottom face
        translate([0,0,mount_bottom-0.01])
            male_thread(thread_major+thread_clear, thread_pitch, thread_len+0.02);
        // clearance recess above the thread
        translate([0,0,mount_bottom+thread_len-0.01])
            cylinder(h = 12 - mount_bottom - thread_len + 0.2, d = thread_major-1.0);
    }
}

// ============================================================
// ASSEMBLY
// ============================================================
module assembly(){
    placed_clip(1);
    placed_clip(-1);
    leg(1); leg(-1);
    boss();
}

assembly();
