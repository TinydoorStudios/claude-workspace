include <ortf_holder.scad>   // renders the holder + gives us its variables

// draw a ghost mic + XLR connector in each cradle to check clearance
module ghost(sign){
    ang = sign>0 ? axis_deg : 180-axis_deg;
    joint = clip_len - stop_t;          // local x of the body front face
    translate([sign*clip_cx,0,H]) rotate([0,0,ang]) translate([-clip_len/2,0,0])
    rotate([0,90,0]) {
        // capsule (forward of joint)
        color([0.7,0.7,0.72]) translate([0,0,joint]) cylinder(h=capsule_len, r=10);
        // CMC6 body (46 mm, rearward of joint)
        color([0.55,0.55,0.58]) translate([0,0,joint-46]) cylinder(h=46, r=10);
        // XLR-3F cable connector barrel (~21 mm dia, ~38 mm, overlaps rear of body)
        color([0.15,0.15,0.15]) translate([0,0,joint-46-20]) cylinder(h=38, r=10.5);
    }
}
ghost(1); ghost(-1);
