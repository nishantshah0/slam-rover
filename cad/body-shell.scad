// ===== SLAM Rover — body shell (SR-006) "make it not a brick" =====
// A car-body style skin that slides down over the printed chassis plate and
// grips its edges (friction lip — no fasteners). Wedge profile: low tail
// over the caster end, high cab over the electronics end.
//
// PRINT: upside-down (roof on the bed, slicer: flip 180 about X), PLA,
// 2-3 walls, 10% infill, no supports needed (walls flare <45deg).
// ~7-9 h, ~150 g. PRINT LAST — after the electronics are assembled and
// measured, in case the cab height needs a bump.
//
// Coordinates: X 0..SHELL_L (low X = tail/caster end), Y 0..SHELL_W,
// Z 0 = top surface of the chassis plate.

$fn = 64;

// --- key dimensions ----------------------------------------------------------
SHELL_L = 166;   SHELL_W = 126;          // outer footprint
PLATE_L = 160;   PLATE_W = 120;          // the printed plate underneath
WALL    = 2.4;   ROOF    = 2.4;
CAB_H   = 46;    // height over the electronics end (clears breadboard+wires)
TAIL_H  = 24;    // height over the caster end (clears battery: 29mm... at
                 // its X the roof is ~35 — see slope note below)
SKIRT   = 9;     // how far the shell wraps down past the plate top
CLEAR   = 0.5;   // per-side clearance around the plate (friction fit; tune)
OX = (SHELL_L - PLATE_L) / 2;            // plate offset inside shell (3,3)
OY = (SHELL_W - PLATE_W) / 2;

module blob(x, y, r, h) { translate([x, y, 0]) cylinder(r = r, h = h); }

// the wedge body: hull between tall cab corners and low tail corners.
// i = wall inset (0 = exterior, WALL = interior cavity)
module wedge(i, h_cab, h_tail) {
    hull() {
        blob(148 - i,  18 + i, 16, h_cab);   // cab corners (high X end)
        blob(148 - i, 108 - i, 16, h_cab);
        blob( 16 + i,  34 + i, 14, h_tail);  // tail corners (narrower nose)
        blob( 16 + i,  92 - i, 14, h_tail);
    }
}

// full-footprint skirt band that wraps the plate edge
module skirt_band(i, h) {
    hull()
        for (p = [[10,10],[SHELL_L-10,10],[10,SHELL_W-10],[SHELL_L-10,SHELL_W-10]])
            blob(p[0] + (p[0] < 50 ? i : -i), p[1] + (p[1] < 50 ? i : -i), 10, h);
}

difference() {
    // ---------------- solid body ----------------
    union() {
        wedge(0, CAB_H, TAIL_H);
        translate([0, 0, -SKIRT]) skirt_band(0, SKIRT + 6);  // bumper band
    }

    // ---------------- hollow it out ----------------
    // main cavity (walls WALL thick, roof ROOF thick)
    translate([0, 0, -SKIRT - 1])
        wedge(WALL, CAB_H - ROOF + SKIRT + 1, TAIL_H - ROOF + SKIRT + 1);
    // plate pocket: the shell slides over the plate like a lid
    translate([0, 0, -SKIRT - 1])
        hull()
            for (p = [[OX+8, OY+8], [OX+PLATE_L-8, OY+8],
                      [OX+8, OY+PLATE_W-8], [OX+PLATE_L-8, OY+PLATE_W-8]])
                blob(p[0], p[1], 8 + CLEAR, SKIRT + 1);

    // ---------------- wheel arches ----------------
    // wheels sit at plate mid-length (shell X=83), axle ~13 below plate top
    translate([83, -2, -13]) rotate([-90, 0, 0])
        cylinder(d = 58, h = SHELL_W + 4);

    // ---------------- top hatch (battery access / future lidar mast) -------
    translate([0, 0, TAIL_H])
        hull()
            for (p = [[83-26, 63-18], [83+26, 63-18], [83-26, 63+18], [83+26, 63+18]])
                blob(p[0], p[1], 8, CAB_H);

    // ---------------- rear-side vents (cab end, 3 per side) ----------------
    for (side = [0, 1], k = [0, 1, 2])
        translate([116 + k*11, side ? SHELL_W - 9 : -3, 16])
            rotate([0, -22, 0])
                cube([3.2, 12, 20]);

    // ---------------- headlight pockets (tall face, cosmetic) --------------
    for (y = [40, 86])
        translate([SHELL_L - 2.6, y, CAB_H - 14])
            rotate([0, 90, 0]) cylinder(d = 9, h = 4);

    // ---------------- cable/USB notch (tail wall) --------------------------
    translate([-2, 55, -2]) cube([10, 16, 12]);
}
