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

Prices in CAD, Amazon.ca unless noted. AliExpress halves some prices if you
can tolerate 2–4 week shipping — fine for Stage 3, risky for Stage 1.

---

## Stage 1 — Buy now (~$165): everything for Phase 1, a complete driving robot

| Item | Spec | ~CAD | Notes |
|---|---|---|---|
| Raspberry Pi **Pico WH** | WiFi + headers pre-soldered | $13 | The robot's brainstem. The "W" ($3 extra) buys **wireless WASD driving** in Phase 1 — no cable dragging behind the rover |
| 2× **N20 gearmotors with encoders** | 6 V, ~200–300 RPM, quadrature hall encoder | $30 | The non-negotiable item (risk R1). Sold as modules with cables pre-attached — **no soldering needed** |
| **SparkFun TB6612FNG "with Headers"** motor driver | dual 1.2 A, headers PRE-soldered | $20 | Swapped from MDD3A (not sold on Amazon.ca). Pushes into the breadboard; motor cable's dupont ends push onto its pins. Wiring note: tie STBY+PWMA+PWMB to 3V3 and the firmware works unchanged (D6) |
| 2× wheels for N20 shafts (3 mm D-shaft) | 34–43 mm | $8 | Or print hubs + rubber-band/O-ring tires on the P1S — $0 |
| Ball caster | ~12 mm | $5 | The third wheel |
| 6×AA battery holder + NiMH AAs + charger | ~7.2 V pack | $40 | Start with alkalines ($8) if needed; NiMH later |
| Jumper wires + mini breadboard | dupont M/M, M/F | $15 | Phase 1 prototyping |
| Multimeter | any $15–20 unit | $18 | The one tool that isn't optional |
| 5 V / **5 A** buck converter | **with screw terminals** | $12 | Moved here from Stage 2: powers the Pico for untethered WiFi driving; later becomes the Pi's battery rail (D7) |
| M3 screw + nut assortment kit | M3 × 8/10/12/16 mix | $10 | Bolts clamps to plate, caster to plate — the printed parts are useless without these |
| Zip ties, small (2.5 mm wide) | 100-pack | $5 | Wire management through the plate's slots |
| Chassis plate, motor mounts | — | **$0** | **Printed on the P1S** — designed in Phase 1, CAD portfolio material |

**Stage 1 total: ~$165.** Deliverable: a keyboard-drivable robot with
encoder odometry and fail-safe firmware. *This is a complete standalone
project* — if you build it and hate the process (you won't), you've risked
$165, not $600.

## Stage 2 — Buy ~week 2 (~$130): the ROS2 brain, for Phase 2

| Item | Spec | ~CAD | Notes |
|---|---|---|---|
| Raspberry Pi 5, **4 GB** | 4 GB is enough for slam_toolbox | $85 | Used Pi 4 (4 GB, ~$50 on FB Marketplace) also runs ROS2 Jazzy fine — saves $35 |
| microSD 64 GB A2 | SanDisk Extreme class | $15 | |
| USB-C PD charger 27 W+ | any decent brand | $20 | Bench power during software work |

**Stage 2 total: ~$120 (or ~$85 with a used Pi 4).** (Buck converter moved to Stage 1.)

## Stage 3 — Buy ~week 3–4 (~$90–140): the lidar, for Phases 2/3

One item, three price points — decide when you get here:

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
| Motors → MDD3A driver | motor wires into MDD3A **screw terminals** (screwdriver) |
| Battery pack → MDD3A + buck | bare leads into **screw terminals** |
| Encoder wires → Pico | motor's included cable → breadboard/dupont **push-in** |
| MDD3A signal pins → Pico | **dupont jumper wires** (they just push on) |
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
