# Shopping List — Staged Purchases (~$90–165 CAD at a time)

Rebuilt for reality: first project, no existing gear except a **Bambu Lab P1S
3D printer**, budget-sensitive. Two big changes from v1:

1. **You buy in three stages matched to the build phases** — never more than
   ~$165 CAD at once, and each stage only gets bought if the previous one
   succeeded. Total exposure at any moment stays low.
2. **The P1S replaces the store-bought chassis** (decision D5 updated). You
   print the chassis plate, motor mounts, lidar mast, and wheels — which cuts
   ~$40 *and* adds CAD design work to the portfolio (mechatronics internships
   care about CAD as much as code).

Every item has a **fallback**: what gets bought instead if it's sold out,
late, or turns out wrong. Picking these up front is the point: a missing part
should cost an afternoon, not a two-week stall.

Prices in CAD, Amazon.ca unless noted. AliExpress halves some prices if you
can tolerate 2–4 week shipping — fine for Stage 3, risky for Stage 1.

---

## Stage 1 — Buy now (~$165): everything for Phase 1, a complete driving robot

| Item | Spec | ~CAD | Notes | Fallback |
|---|---|---|---|---|
| Raspberry Pi **Pico WH** | WiFi + headers pre-soldered | $13 | The robot's brainstem. The "W" ($3 extra) buys **wireless WASD driving** in Phase 1 — no cable dragging behind the rover | **Pico H** (no WiFi): the firmware already speaks USB serial, so teleop runs over a cable instead |
| 2× **N20 gearmotors with encoders** | 6 V, ~200–300 RPM, quadrature hall encoder | $30 | The non-negotiable item (risk R1). Sold as modules with cables pre-attached — **no soldering needed** | Any N20 encoder listing from 100–500 RPM: the clamps fit every N20 body. Last resort: JGA25-370 encoder motors plus a redesigned clamp |
| **SparkFun TB6612FNG "with Headers"** motor driver | dual 1.2 A, headers PRE-soldered | $20 | Swapped from MDD3A (not sold on Amazon.ca). Pushes into the breadboard; motor cable's dupont ends push onto its pins. Wiring note: tie STBY+PWMA+PWMB to 3V3 and the firmware works unchanged (D6) | **DRV8833** module (~$8): same two-PWM-pins-per-motor control, so the firmware is unchanged. Or the original Cytron MDD3A from RobotShop when it's back in stock |
| 2× wheels for N20 shafts (3 mm D-shaft) | 34–43 mm | $8 | Or print hubs + rubber-band/O-ring tires on the P1S — $0 | Printed wheels ([cad/wheel.scad](../cad/wheel.scad)) with rubber-band tires, $0 |
| Ball caster | ~12 mm | $5 | The third wheel | Any 12–16 mm ball caster: the [parametric spacer](../cad/caster-spacer.scad) adjusts to its height |
| 6×AA battery holder + NiMH AAs + charger | ~7.2 V pack | $40 | Start with alkalines ($8) if needed; NiMH later | Alkaline AAs (~$8) in the same holder: same voltage, just not rechargeable |
| Jumper wires + mini breadboard | dupont M/M, M/F | $15 | Phase 1 prototyping | Any dupont kit; a half-size breadboard fits the plate too |
| Multimeter | any $15–20 unit | $18 | The one tool that isn't optional | Borrow one from the university makerspace |
| 5 V / **5 A** buck converter | **with screw terminals** | $12 | Moved here from Stage 2: powers the Pico for untethered WiFi driving; later becomes the Pi's battery rail (D7) | Phase 1: a USB power bank powers the Pico. Phase 2: a 5 V / 5 A UBEC for the Pi |
| M3 screw + nut assortment kit | M3 × 8/10/12/16 mix | $10 | Bolts clamps to plate, caster to plate — the printed parts are useless without these | Loose M3 screws and nuts from a hardware store |
| Zip ties, small (2.5 mm wide) | 100-pack | $5 | Wire management through the plate's slots | Velcro cable straps |
| Chassis plate, motor mounts | — | **$0** | **Printed on the P1S** — designed in Phase 1, CAD portfolio material | Adjust tolerances from the test coupon and reprint (~6 hr) |

**Stage 1 total: ~$165.** Deliverable: a keyboard-drivable robot with
encoder odometry and fail-safe firmware. *This is a complete standalone
project* — if you build it and hate the process (you won't), you've risked
$165, not $600.

## Stage 2 — Buy ~week 2 (~$130): the ROS2 brain, for Phase 2

| Item | Spec | ~CAD | Notes | Fallback |
|---|---|---|---|---|
| Raspberry Pi 5, **4 GB** | 4 GB is enough for slam_toolbox | $85 | Bench and robot computer for ROS 2 | Used Pi 4 (4 GB, ~$50 on FB Marketplace): also runs ROS2 Jazzy, saves $35 |
| microSD 64 GB A2 | SanDisk Extreme class | $15 | | Any 64 GB A2-rated card (Samsung EVO, Kingston Canvas) |
| USB-C PD charger 27 W+ | any decent brand | $20 | Bench power during software work | The official Raspberry Pi 27 W supply |

**Stage 2 total: ~$120 (or ~$85 with a used Pi 4).** (Buck converter moved to Stage 1.)

## Stage 3 — Buy ~week 3–4 (~$90–140): the lidar, for Phases 2/3

One item, three price points. Each one is the others' fallback, and all three publish the same `LaserScan` message that slam_toolbox reads:

| Option | ~CAD | Trade-off |
|---|---|---|
| **LDROBOT LD19 / STL-19P** (or D500 kit) | ~$90–100 | Newer, smaller, solid ROS2 driver (`ldlidar`) — the budget pick |
| **Used RPLidar A1** (eBay/Marketplace) | ~$60–80 | Cheapest path to the gold-standard beginner lidar |
| **New RPLidar A1** | ~$140 | Most tutorials, most community help when stuck |

Lidar mast/mount: **printed on the P1S, $0.**

---

## Budget summary

| | CAD |
|---|---|
| Stage 1 (driving robot) | ~$165 |
| Stage 2 (ROS2 brain) | ~$85–120 |
| Stage 3 (lidar) | ~$90–140 |
| **Full SLAM rover, total** | **~$340–425, spread over ~4 weeks** |

For calibration: a TurtleBot 4 Lite — the commercial version of this exact
robot — is **~$1,600 CAD**. And unlike a bought robot, *building* it is the
thing internship interviews actually ask about.

## What the P1S contributes (all $0, all portfolio)

- Chassis plate + motor mounts (Phase 1 — designed in Onshape, free for students)
- Wheel hubs if you skip bought wheels
- Pi/Pico/driver mounting tray
- Lidar mast (Phase 2/3)
- Eventually: an enclosure that makes the demo photos look professional

## The no-solder guarantee 🔩

Every connection in this robot is a **plug, a screw terminal, or a breadboard
push-in**. The complete map:

| Connection | How it's made |
|---|---|
| Pico ↔ breadboard | Pico **H** = headers pre-soldered, pushes into breadboard |
| Motors → TB6612 driver | motor cable's dupont ends **push onto** the AO/BO header pins |
| Battery pack → TB6612 + buck | leads into the breadboard power rail (driver VM) and the buck's **screw terminals** |
| Encoder wires → Pico | motor's included cable → breadboard/dupont **push-in** |
| TB6612 signal pins → Pico | **dupont jumper wires** (they just push on) |
| Buck converter → Pi 5 | screw terminals in, USB-C out |
| Lidar → Pi | **USB cable**, nothing else |
| Pi ↔ Pico | **USB cable** |

**Two buying details that keep this true:**
1. Choose an N20 encoder motor listing that says **"with cable"** — the
   encoder cable comes pre-attached (factory-soldered, not by you) with
   dupont-style ends.
2. Choose a buck converter **with screw terminals** (many are; some are
   solder-pad only — avoid those).

Soldering is a 20-minute skill you can pick up at the university makerspace
*whenever you feel like it, or never*. It is not a gate on this project.

## Other tools you do NOT need to buy

- Wire strippers/heat gun — makerspace, or scissors-and-care at this scale.
- Soldering iron — see above. Not used anywhere in this build.
