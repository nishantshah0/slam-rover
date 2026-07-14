# Chassis Design Spec — What Gets Modeled in Onshape

Modeled from scratch, no downloaded parts (that's the point — "designed the
chassis in CAD" is the interview line). This doc is the *engineering spec*:
dimensions, layout logic, and the print plan.

⚠️ All part dimensions marked **nominal** are typical for these components but
vary by listing — final-check them with calipers/ruler when parts arrive.
That's what the test-fit coupon is for.

## Component envelopes (nominal)

| Part | Size (mm) | Notes |
|---|---|---|
| N20 motor body | 12 × 10 × ~24 (+ encoder board ~11 behind) | 3 mm D-shaft, centered on the 12×10 face |
| Wheel | Ø34 × 7 | → axle center sits **17 mm** above ground |
| Ball caster | Ø12 ball, housing ~16 tall | usually 2× M3 mounting holes |
| MDD3A | ~37 × 31 | 4× M3 corner holes |
| Pico W | 51 × 21 | 4× M2.1 holes (M2 screws or zip tie) |
| Buck converter | ~45 × 22 | often M3 holes; else zip-tie slots |
| 6×AA holder (with switch) | ~58 × 48 × 29 | heaviest part — placement matters most |
| Half-size breadboard | 82 × 55 | has adhesive back |

## The layout logic (this reasoning is portfolio material)

- **Plate:** 160 × 120 × 5 mm, flat, printed face-down — fits the P1S bed
  with huge margin, no supports.
- **Wheels on the center line** (mid-length, one each side, outside the plate
  footprint so the plate needs no cutouts). Why center: the robot then spins
  about its own middle — cleaner odometry math and, later, the lidar sits
  directly over the rotation center, which SLAM likes.
- **Battery holder centered between the wheels, directly on the plate.** The
  heaviest mass over the axle = traction on the drive wheels and a stable
  spin. Put it anywhere else and the rover wheelies or the caster carries too
  much weight.
- **Caster at the rear center**, ~50 mm from the back edge.
- **Height math** (do this once, reuse forever): wheel center is 17 mm up;
  motor body is 10 mm tall with a centered shaft, and it hangs in a clamp
  whose 3 mm flange sits between motor and plate → plate underside sits at
  17 + 5 + 3 = **25 mm above ground** → the caster stack (housing + printed
  spacer) must also total **25 mm**, so the plate rides level. The spacer is
  a 5-minute print you'll iterate — expect one reprint after ground truth.
- **Electronics topside:** breadboard front-center (stick-on), MDD3A beside
  it, Pico on the breadboard itself, buck at the rear near the battery leads.
  Keep encoder (signal) wiring away from motor (power) wiring — parallel runs
  of the two invite electrical noise in the counts.

## Parts to model (in order)

**1. Test-fit coupon (print FIRST, before the real plate).** A 40 × 40 × 5 mm
tile containing: one motor-clamp pocket, one M3 hole, one M2 hole, one zip-tie
slot (3 × 5 mm). Print, test the real parts in it when they arrive, adjust
tolerances, *then* print the plate. Costs 10 minutes of filament; saves a
full plate reprint.

**2. Motor clamps (×2, identical — the design is symmetric, no mirroring
needed).** DESIGNED (SR-002, Session 2): a 38.3 × 20 × 3 flange with two Ø3.2
screw holes (5 mm from each end), an 18.3 × 20 × 13.3 block fused on top, and
a **12.3 × 10.3** motor tunnel through it (3 mm walls and roof; tolerance
number tracks whatever the coupon proves). Motor slides in from either end;
friction + two M3 screws to the plate hold it. Print flange-down, no supports.

**3. The plate.** (Coordinates finalized in Session 3 — origin at back-left
corner, X 0→160 toward the front, Y 0→120 left-to-right. Clamp holes: all at
X=80; Y = 5, 33.3, 86.7, 115 — the 28.3 pitch comes from the clamp flange.
Spare grids: Ø3.2 at 20 mm pitch, rear block X 10–50 and front block X 110–150,
Y 20–100 both. Battery zone X ~55–105 kept bare.)
One sketch + one extrude + hole patterns:
- 160 × 120 rectangle, corners filleted R8
- Motor clamp screw holes at the wheel positions (from the clamp design)
- Caster M3 holes at rear center
- MDD3A + buck M3 hole patterns
- A loose grid of spare M3 holes down the middle (future mounts — lidar mast
  bolts here in Phase 2, zero redesign)
- 4–6 zip-tie slots (3 × 5 mm) along the wire routes
- Battery zone: keep it bare; velcro holds the holder (tool-free battery swaps)

**4. Caster spacer.** Cylinder/block to make the caster stack 22 mm. Measure
the real caster first.

## Onshape session plan (~2–3 hrs total)

1. Free **student account** at onshape.com/edu (browser, nothing to install).
2. Learn exactly four tools — Sketch, Extrude, Hole/circle, Fillet — that's
   90% of this design.
3. Model in this order: coupon → clamp → plate → spacer. Each is one sketch
   + one extrude.
4. Make key numbers **variables** (`#plate_len`, `#motor_pocket_w`…) so
   coupon-measured corrections update the plate automatically. This is the
   difference between CAD and drawing — and a great interview detail.
5. Export STL → slice (4 walls, 30% infill, PLA is fine) → print.

## Print queue

| When | What |
|---|---|
| Now ($0) | Test-fit coupon — ready for the day parts arrive |
| After coupon passes | Plate + 2 clamps + caster spacer (~6 hr print, overnight) |
| Phase 2 | Lidar mast (bolts to the spare-hole grid) |
