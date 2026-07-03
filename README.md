# SLAM-Capable Autonomous Rover

A rover that autonomously maps a room using LIDAR + ROS2. Built as a portfolio piece for mechatronics/robotics internships.

## Hardware

| Component | Choice | Rationale | Status |
|---|---|---|---|
| Compute | Raspberry Pi 5 | Runs ROS2 + SLAM | Decided |
| Real-time motor control | Raspberry Pi Pico | PWM + **encoder counting** (PIO) | Decided |
| Sensing | RPLidar A1 | Direct `LaserScan` fit for slam_toolbox ([D2](docs/decisions.md)) | Proposed |
| Chassis | **3D-printed diff-drive plate + caster** (Bambu P1S) | Skid-steer corrupts odometry; printing saves $ and adds CAD to portfolio ([D5](docs/decisions.md)) | Proposed |
| Motors | **N20 gearmotors with quadrature encoders** | SLAM needs odometry — encoders are not optional ([R1](docs/risks.md)) | Proposed |
| Motor driver | TB6612FNG or Cytron MDD3A (**not L298N**) | L298N wastes 2–4 V as heat ([D6](docs/decisions.md)) | Proposed |
| Power | Battery → motor rail + separate 5V/5A buck → Pi | Shared rail = brownout reboots ([D7](docs/decisions.md)) | Proposed |

3D printing (Bambu P1S) covers all *structure*: chassis plate, motor mounts, wheel hubs, lidar mast, Pi/Pico tray. Drivetrain internals (motors, gears, caster) stay off-the-shelf. Budget: **~$325–410 CAD total, bought in three stages of ~$90–150** ([shopping-list.md](docs/shopping-list.md)).

## Software Stack

- **ROS2 Jazzy** on Ubuntu 24.04 — *not Humble*: Humble's Ubuntu 22.04 doesn't support the Pi 5 ([D1](docs/decisions.md))
- **slam_toolbox** for SLAM
- **Nav2** for autonomous navigation (stretch goal)
- **Python** for ROS2 nodes; **MicroPython + PIO** on the Pico ([D4](docs/decisions.md))
- Dev environment: WSL2 (learning) + headless Pi + Foxglove Studio (live viz) ([D8](docs/decisions.md))

## Phased Build Plan (~6–8 weeks)

### Phase 0 (Week 0) — Order parts & set up dev environment
Shipping eats calendar time — order **Stage 1** of the [shopping list](docs/shopping-list.md) now (later stages get bought as earlier ones succeed). Meanwhile, all $0: WSL2 + Ubuntu 24.04 + ROS2 Jazzy on the Windows machine; chassis CAD in Onshape; firmware drafted in the Wokwi simulator; GitHub repo created ([D9](docs/decisions.md)). The Pi gets flashed when the Stage 2 box arrives (~week 2).

### Phase 1 (Weeks 1–2) — Get it moving
Assemble chassis, wire motor driver + Pico + two-rail power. Pico firmware: PWM drive, **encoder counting via PIO**, serial protocol, **command watchdog (fail-safe stop, [R4](docs/risks.md))**. Keyboard teleop over SSH. **No ROS2 yet** — isolate hardware learning from software learning.

### Phase 2 (Weeks 3–4) — ROS2 fundamentals + sensing + odometry
Two parallel tracks:
- **Learning track (WSL2, no robot):** nodes, topics, pub/sub, launch files, tf basics.
- **Robot track (Pi):** lidar publishing `LaserScan`; serial-bridge node (`cmd_vel` → Pico, encoder counts → Pi); **odometry node** publishing `odom` + the `odom → base_link` transform. Doing odometry here keeps Phase 3 from overloading.

### Phase 3 (Weeks 5–6) — SLAM integration
slam_toolbox + tf tree (`map → odom → base_link → laser`). Debug coordinate frames, lidar mounting/orientation ([R8](docs/risks.md)), drift; tune. Drive the room, save a clean map.

**✅ Success checkpoint: a rover that maps a room cleanly is a strong standalone demo, even if Phase 4 isn't reached.**

### Phase 4 (Stretch) — Autonomy
Nav2 for point-to-point autonomous navigation. Prep item: closed-loop wheel velocity control (PID on the Pico) makes Nav2 behave much better than open-loop PWM.

## Repo Layout

```
docs/
  roadmap.md         # Beginner roadmap: milestone ladders, concepts, definitions of done
  phase1-guide.md    # Full Phase 1 execution plan: wiring, firmware steps, pin map
  shopping-list.md   # Staged cart (~$325–410 CAD total, 3 purchases)
  debugging-log.md   # Running log: what broke, why, how it was fixed
  decisions.md       # Design decisions D1–D9 with rationale
  risks.md           # Known failure modes R1–R10 and mitigations
pico/                # Pico firmware: main.py + encoder.py + concept walkthrough (WRITTEN — verify at bring-up)
teleop/              # PC-side WASD driving script (WiFi/UDP or USB serial)
cad/                 # Chassis design spec for Onshape (plate, clamps, test-fit coupon)
ros2_ws/             # ROS2 workspace (Phase 2+)
```

**Start here:** [docs/roadmap.md](docs/roadmap.md) — the phase-by-phase ladder — and [docs/shopping-list.md](docs/shopping-list.md) for what to order.

## Debugging Log

Every non-trivial problem gets an entry in [docs/debugging-log.md](docs/debugging-log.md) — symptom, root cause, fix. This doubles as interview storytelling material.
