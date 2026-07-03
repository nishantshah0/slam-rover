// ===== SLAM Rover — caster spacer (SR-005) =====
// Makes the caster stack match the drive-wheel geometry so the plate sits
// level. Height budget (see cad/chassis-design.md):
//   plate underside = 21.5 (43mm wheel radius) + 5 (motor half-height)
//                     + 3 (clamp flange) = 29.5 mm above ground
//   spacer h = 29.5 − (measured caster height)
// >>> The default h is a PLACEHOLDER. Measure the real caster when it
//     arrives, set h, re-render, print. (This is why it's code.)

$fn = 60;

spacer_l     = 49;    // caster base plate length (Amazon listing spec)
spacer_w     = 20;
h            = 6;     // PLACEHOLDER — set to 29.5 − measured caster height
hole_spacing = 39;    // caster mounting hole spacing (listing spec)
hole_d       = 3.4;   // M3 screw or zip-tie clearance

difference() {
    // rounded-end bar
    hull()
        for (x = [-1, 1])
            translate([x * (spacer_l/2 - spacer_w/2), 0, 0])
                cylinder(d = spacer_w, h = h);
    // mounting holes, through
    for (x = [-1, 1])
        translate([x * hole_spacing/2, 0, -1])
            cylinder(d = hole_d, h = h + 2);
}
