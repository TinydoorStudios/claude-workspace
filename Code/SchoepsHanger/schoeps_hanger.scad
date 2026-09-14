// ============================================================================
//  Schoeps Mic Hanger  —  Neumann MNV 87 MT clamp unit
//  CORRECTED: the mic clip grips the mic barrel at 90 deg to the paddle,
//  across the mic's CENTRE (balanced), like an SM57-style clip on a hanger.
//
//  Paddle (long axis = Z, wide face = XZ, thickness = Y), top -> bottom:
//    - 3/8"-16 threaded stud + knurled collar   (mount / hang point)
//    - flat body with two round lightening holes
//    - knurled thumbwheel tilt-lock (pivot pin + arc slot)
//    - transverse SPRING CLIP: bore axis = X, snaps onto the 20 mm CMC 6,
//      mic runs left-right through it (capsule one side, XLR the other)
//
//  Hardware:  pivot pin  M3 x 16 + M3 nut
//             tilt clamp M4 x 20 + printed knurled knob (M4 nut captive)
//
//  part = "jaw" | "base" | "knob" | "assembly"
// ============================================================================

part = "assembly";
tilt = 0;
$fn = 96;

mic_d  = 20.0;
bore   = mic_d + 0.3;
barW   = 28;          // paddle width  (X)
barT   = 11;          // paddle thickness (Y)
half_t = barT/2 - 0.3;

m3=3.2; m3nut_af=6.2; m3nut_th=2.6;
m4=4.4; m4nut_af=7.2; m4nut_th=3.4;
clamp_r = 14;  arc_deg = 28;

stud_maj=9.525; stud_p=1.5875; stud_len=13;
collar_d=20; collar_h=7;

jz_top = 11;  jz_bot = -17;          // joint-plate z span
body_h = 46;                          // base body length above the joint

// ---- transverse mic clip --------------------------------------------------
clipW  = 18;          // clip length gripping the barrel (along X = mic axis)
c_wall = 4;
clipOD = bore + 2*c_wall;    // 28.4
clip_z = jz_bot - 24;        // clip centre, below the joint
mouth  = 15;                 // front opening (< bore -> snaps on, grips)
rib_n  = 5; rib_p = 3; rib_h = 0.7;

// ---------------------------------------------------------------- helpers
module bar(h)
  linear_extrude(h) hull(){
    translate([-(barW/2-barT/2),0]) circle(d=barT);
    translate([ (barW/2-barT/2),0]) circle(d=barT);
  };

module halfplate(side){
  rot = side>0 ? -90 : 90;
  hull(){
    translate([0,0,jz_top]) rotate([rot,0,0]) cylinder(d=barW, h=half_t);
    translate([0,0,jz_bot]) rotate([rot,0,0]) cylinder(d=barW, h=half_t);
  }
}

module ext_thread(dmaj,p,h){
  minor=dmaj-1.15*p; turns=h/p;
  intersection(){
    cylinder(d=dmaj+0.2,h=h);
    linear_extrude(height=h, twist=-360*turns, slices=max(24,turns*10), $fn=36)
      union(){ circle(d=minor); polygon([[0,-p*0.5],[dmaj/2,0],[0,p*0.5]]); }
  }
}

module knurl(d,h){
  n=30;
  union(){
    cylinder(d=d,h=h);
    for(i=[0:n-1]) rotate([0,0,i*360/n]) translate([d/2,0,0]) cylinder(d=1.5,h=h,$fn=6);
  }
}

// ---------------------------------------------------------------- JAW (clip)
module jaw(){
  difference(){
    union(){
      halfplate(-1);
      // neck: joint plate -> clip
      hull(){
        translate([0,0,jz_bot+2]) rotate([90,0,0]) cylinder(d=barW*0.8, h=barT, center=true);
        translate([0,0,clip_z]) rotate([0,90,0]) cylinder(d=clipOD, h=clipW, center=true);
      }
      // transverse clip barrel (bore axis = X)
      translate([0,0,clip_z]) rotate([0,90,0]) cylinder(d=clipOD, h=clipW, center=true);
      // flared lead-in lips at the mouth, welded to the barrel (the "pincer")
      for(sz=[-1,1])
        hull(){
          translate([0, -bore/2+2, clip_z + sz*(mouth/2+1.5)])
            cube([clipW, 4, 3], center=true);            // seat on the barrel lip
          translate([0, -bore/2-5, clip_z + sz*(mouth/2+5)])
            cube([clipW, 3, 3], center=true);            // flared tip (funnel)
        }
    }
    // transverse mic bore (axis X)
    translate([0,0,clip_z]) rotate([0,90,0]) cylinder(d=bore, h=clipW+2, center=true);
    // front mouth: open the bore toward -Y so the mic snaps in
    translate([-clipW/2-1, -clipOD, clip_z-mouth/2]) cube([clipW+2, clipOD, mouth]);
    // grip ribs inside the wrap (rings concentric with the X bore)
    for(i=[-2:2])
      translate([i*rib_p, 0, clip_z]) rotate([0,90,0])
        rotate_extrude($fn=64) polygon([[bore/2,-rib_p*0.4],[bore/2-rib_h,0],[bore/2,rib_p*0.4]]);
    // pivot + clamp bolt holes (Y)
    rotate([90,0,0]) cylinder(d=m3, h=barT+6, center=true);
    translate([0,0,-clamp_r]) rotate([90,0,0]) cylinder(d=m4, h=barT+6, center=true);
    translate([0,-half_t,0]) rotate([90,0,0]) rotate([0,0,30])
      cylinder(h=m3nut_th+0.6, d=m3nut_af/cos(30), $fn=6);
  }
}

// ---------------------------------------------------------------- BASE
module base(){
  difference(){
    union(){
      halfplate(1);
      translate([0,0,jz_top-2]) bar(body_h);
      translate([0,0,jz_top-2+body_h-0.1]) knurl(collar_d,collar_h);
      translate([0,0,jz_top-2+body_h+collar_h-0.1]) ext_thread(stud_maj,stud_p,stud_len);
    }
    rotate([90,0,0]) cylinder(d=m3, h=barT+6, center=true);
    for(a=[-arc_deg:2:arc_deg])
      rotate([a,0,0]) translate([0,0,-clamp_r]) rotate([90,0,0])
        cylinder(d=m4, h=barT+6, center=true);
    translate([0,0,jz_top+16]) rotate([90,0,0]) cylinder(d=9, h=barT+6, center=true);
    translate([0,0,jz_top+30]) rotate([90,0,0]) cylinder(d=9, h=barT+6, center=true);
  }
}

// ---------------------------------------------------------------- KNOB
module knob(){
  difference(){
    union(){ knurl(20,7); cylinder(d=12,h=10); }
    translate([0,0,-1]) cylinder(d=m4,h=14);
    translate([0,0,10-m4nut_th]) rotate([0,0,30]) cylinder(h=m4nut_th+1,d=m4nut_af/cos(30),$fn=6);
  }
}

// ---------------------------------------------------------------- output
if(part=="jaw")       jaw();
else if(part=="base") base();
else if(part=="knob") knob();
else {
  color("gray")      base();
  rotate([0,tilt,0]){
    color("SteelBlue") jaw();
    // mic ghost: horizontal (along X), gripped at CENTRE, capsule +X
    %color("silver") translate([-55,0,clip_z]) rotate([0,90,0]) cylinder(d=mic_d, h=110);
  }
  translate([0, -(half_t+2), -clamp_r]) rotate([90,0,0]) color("orange") knob();
}
