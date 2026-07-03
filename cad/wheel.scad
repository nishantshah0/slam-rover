// ===== SLAM Rover — printed drive wheel (SR-004) =====
// Replaces the $8 bought wheels. Print 2: PLA, 4 walls, 30% infill,
// flat face down, no supports.
// TIRES: stretch two rubber bands into the rim grooves — bare PLA slips.

$fn = 120;                 // circle smoothness (segments)

// --- parameters -------------------------------------------------------------
wheel_d      = 43;         // overall diameter — matches the height math in
                           // cad/chassis-design.md (plate underside 29.5 mm)
wheel_w      = 8;          // rim width
hub_d        = 12;         // hub boss diameter
hub_extra    = 4;          // hub boss sticks out this far past the rim face
bore_d       = 3.25;       // N20 shaft is 3.0 round — +0.25 print compensation
flat_w       = 2.75;       // N20 "D" flat is 2.5 across — same compensation
                           // >>> tune bore_d & flat_w from coupon results —
                           // bore must be SNUG (wheel is friction-driven)
groove_depth = 1.5;        // rubber-band grooves in the rim
groove_w     = 2;
lighten_d    = 8;          // weight-saving holes in the web
lighten_r    = 13;         // circle they sit on

// --- the wheel ---------------------------------------------------------------
difference() {
    union() {
        cylinder(d = wheel_d, h = wheel_w);                  // rim/disc
        cylinder(d = hub_d, h = wheel_w + hub_extra);        // hub boss
    }
    // two rubber-band grooves around the rim
    for (z = [1.5, wheel_w - 1.5 - groove_w])
        translate([0, 0, z]) ring_cut(wheel_d, groove_depth, groove_w);
    // D-shaped shaft bore, all the way through
    translate([0, 0, -1])
        linear_extrude(wheel_w + hub_extra + 2) d_shaft_profile();
    // lightening holes
    for (a = [0 : 60 : 359])
        rotate([0, 0, a]) translate([lighten_r, 0, -1])
            cylinder(d = lighten_d, h = wheel_w + 2);
}

// ring-shaped channel cut into the outer rim
module ring_cut(od, depth, w) {
    difference() {
        cylinder(d = od + 2, h = w);
        translate([0, 0, -0.5]) cylinder(d = od - 2*depth, h = w + 1);
    }
}

// circle with one flat = the N20 "D" shaft cross-section
module d_shaft_profile() {
    difference() {
        circle(d = bore_d);
        translate([flat_w - bore_d/2, -bore_d/2 - 1])
            square(bore_d + 2);
    }
}
