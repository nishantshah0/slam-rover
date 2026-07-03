# Design Decisions

Decisions with rationale. Update status as things get locked in.
Cross-reference: [risks.md](risks.md) explains the failure modes behind several of these.

## D1 — ROS2 distro: Jazzy, not Humble (proposed)

**Status:** Proposed, needs confirmation before OS install.

The original plan said ROS2 Humble, but Humble requires **Ubuntu 22.04**, and
Ubuntu 22.04 **does not support the Raspberry Pi 5** (Pi 5 needs 23.10+).

Options:
1. **ROS2 Jazzy on Ubuntu 24.04** ← recommended. Pi 5 officially supported,
   Jazzy is an LTS (supported to 2029), slam_toolbox and Nav2 both fully
   supported. Humble tutorials translate almost 1:1 (swap "humble"→"jazzy").
2. Humble in Docker on Raspberry Pi OS — works, but adds container complexity
   a beginner doesn't need.
3. Swap Pi 5 for Pi 4 — supports Humble natively, but weaker compute for SLAM.

## D2 — Primary sensor: RPLidar A1 (proposed)

**Status:** Proposed.

For 2D SLAM with slam_toolbox, a 2D lidar is the direct path: it publishes
`LaserScan` messages, exactly what slam_toolbox consumes. The RPLidar A1 has a
maintained ROS2 driver (`sllidar_ros2`) and is the cheapest option (~$100).

Depth cameras (OAK-D Lite, RealSense) make SLAM *harder* for a first build:
visual/RGB-D SLAM is a different, more complex pipeline. A camera can be
**added later** for perception demos without changing the SLAM stack.

## D3 — Pi ↔ Pico link: plain USB serial (proposed)

**Status:** Proposed.

The Pico talks to the Pi over USB serial with a simple text protocol
(e.g. Pi→Pico `V <left_pwm> <right_pwm>`, Pico→Pi `E <left_count> <right_count>`
at a fixed rate). micro-ROS on the Pico is the "fancy" option but adds
significant setup complexity; a plain serial bridge node on the Pi achieves the
same thing and is far easier to debug. Can migrate to micro-ROS later as a
stretch refinement.

**Firmware requirement (see risk R4):** command watchdog — if no valid command
arrives for ~300–500 ms, stop the motors. The Pi side re-sends commands at
~10 Hz.

## D4 — Pico firmware language: MicroPython + PIO (proposed)

**Status:** Proposed; escalation path defined.

MicroPython keeps the whole project in one language and is much faster to
iterate on. The known weakness — missing encoder pulses at speed (risk R7) —
is solved by counting pulses with the Pico's **PIO hardware state machines**,
which MicroPython can program. If PIO-from-MicroPython becomes a fight, the
defined fallback is rewriting the firmware in the C SDK (which is *also* good
resume material — frame it as a deliberate engineering escalation, not a failure).

## D5 — Chassis: 3D-printed diff-drive plate + N20 encoder motors (revised)

**Status:** Revised 2026-07-01 — printed chassis replaces the bought kit.

Two constraints drove the original "buy a kit" call and both still hold
(risks R1, R2):

1. **Encoders are effectively required.** slam_toolbox expects odometry;
   without it maps smear. → **N20 gearmotors with quadrature hall encoders**
   (~$30/pair, come as plug-in modules, no soldering).
2. **Skid-steer lies to the encoders.** 4WD/tracked slips sideways in every
   turn, corrupting rotation odometry. → **2-wheel differential drive +
   caster** (the TurtleBot shape).

What changed: the owner has a **Bambu Lab P1S**, so the chassis *plate*,
motor mounts, wheel hubs, and lidar mast are **printed, not bought** — saves
~$40 and adds CAD design work (Onshape, free for students) to the portfolio,
which mechatronics recruiters value as much as code. The original plan's
"don't print the drivetrain" rule survives: gears, motors, and bearings stay
off-the-shelf; we print the *structure* (flat plates and brackets — easy,
strong, low-risk prints).

Fallback if chassis design stalls Phase 1 by more than a few days: Pololu
Romi chassis kit + encoder pair (~$55 CAD) drops in with the same electronics.

## D6 — Motor driver: TB6612FNG or Cytron, not L298N (proposed)

**Status:** Proposed.

The tutorial-favorite L298N drops 2–4 V as heat (old Darlington design) — 6 V
motors would see ~3.5 V and crawl (risk R5). Use a modern MOSFET driver:
**TB6612FNG** (cheap, dual channel, ~1 A/ch) or **Cytron MDD3A/MDD10A** (more
current headroom, simplest wiring). Buy a spare.

## D7 — Power architecture: two rails, one battery (proposed)

**Status:** Proposed.

Motor voltage sag reboots a shared-supply Pi (risk R3). Architecture:

```
Battery (6×AA NiMH, ~7.2 V) ──┬── motor driver ── motors
                  └── 5V/5A buck converter ── Pi 5 ── (USB) lidar
                        (common ground across everything)
```

The Pi 5 specifically wants 5V/**5A**; on a weaker feed it caps USB output
current, which the lidar (~0.5 A) needs. Battery chemistry: LiPo (light,
powerful, needs careful handling) vs protected 18650/NiMH (heavier, safer) —
either works; pick based on comfort with LiPo safety.

## D8 — Dev environment: WSL2 for learning, headless Pi + Foxglove for the rover (proposed)

**Status:** Proposed.

- **ROS2 learning (Phase 2):** Ubuntu 24.04 + ROS2 Jazzy in **WSL2** on the
  Windows machine. RViz works via WSLg. No robot needed for the fundamentals.
- **The rover's Pi:** Ubuntu **Server** 24.04, headless, SSH only. RViz on a
  Pi is sluggish; don't try.
- **Live visualization:** **Foxglove Studio** on Windows → `foxglove_bridge`
  on the Pi over WiFi. Avoids DDS discovery between WSL2 and the LAN, which is
  flaky through WSL2's NAT (risk R6).

## D9 — Code workflow: GitHub as single source of truth (proposed)

**Status:** Proposed.

Docs live here (Windows/OneDrive); ROS2 code runs on the Pi; firmware is
flashed from wherever. Rule: **push after editing, pull before editing** —
GitHub is the sync point, never OneDrive or SCP (risk R9). Name the GitHub
repo something portfolio-worthy (e.g. `slam-rover`).
