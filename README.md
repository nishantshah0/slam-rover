# SLAM Rover

A ~$400 CAD rover designed to map buildings with lidar SLAM, built toward **[Plumb](#whats-next-plumb)**: structural inspection that maps where floors are sinking, sagging, or cracking. Custom 3D-printed chassis, custom Pico W firmware, Raspberry Pi 5 + ROS 2 Jazzy.

## Where it stands

**Done:** the design, the printed chassis, firmware tested in simulation, and the electronics wired. **Next:** on-hardware testing and driving, then lidar mapping ([runbook](docs/phase1-guide.md)).

### Completed

- ✅ **Planned before buying anything.** Nine design decisions with rationale ([D1–D9](docs/decisions.md)), ten known failure modes with mitigations ([R1–R10](docs/risks.md)), and a parts list split into [three purchases](docs/shopping-list.md), each bought only after the previous stage works, so a wrong part costs one stage instead of the whole budget.
- ✅ **Survived a part shortage on paper.** The first-choice motor driver (Cytron MDD3A) sold out on Amazon.ca and RobotShop. Because decision D6 recorded *why* it was chosen, the replacement (SparkFun TB6612FNG) was picked the same afternoon. Tying its STBY/PWMA/PWMB pins high makes it behave like the MDD3A, so the firmware didn't change ([D6](docs/decisions.md)).
- ✅ **Designed and printed the chassis.** 160 × 120 mm diff-drive plate, N20 motor clamps, and a tolerance test coupon in Onshape; drive wheels, caster spacer, and body shell in OpenSCAD (sources included). Printed and dry-fitted on a Bambu P1S ([gallery](#gallery)).
- ✅ **Wrote the Pico W firmware and tested it in simulation.** PWM motor control, PIO quadrature encoder counting, USB serial + WiFi UDP command protocol, and a fail-safe watchdog. A [host-side harness](pico/host_test/run_sim.py) fakes the Pico hardware around a virtual clock and runs the real `main.py`. It passes 9/9 checks:
  - boots with motors stopped
  - `M 60 60` sets both motors to the expected PWM duty
  - a 10 Hz command stream keeps the motors running
  - out-of-range speeds clamp to ±100, and reverse uses the reverse pin
  - **when commands stop (laptop dies, WiFi drops), the watchdog stops both motors within ~400 ms**
  - encoder telemetry streams at ~20 Hz
  - garbage input is ignored and doesn't keep the motors alive
  - firmware falls back cleanly when PIO isn't available, and announces when it's ready
- ✅ **Teleop client.** WASD driving over WiFi or USB, sending the 10 Hz heartbeat the watchdog expects.
- ✅ **ROS 2 Jazzy dev environment** set up in WSL2 (talker/listener verified).

- ✅ **Electronics wired:** motors, TB6612 driver, encoders, and the two-rail power system (battery → driver, battery → buck → Pi), per the [pin map](docs/phase1-guide.md).

### Next

- 🔜 **On-hardware testing:** confirm encoder counts with a hand-spin test, run the watchdog unplug test on the real rover, then WASD driving ([runbook](docs/phase1-guide.md)). The simulation can't test the PIO encoder code, so that gets verified here first.
- ⬜ **Mapping:** lidar + wheel odometry into slam_toolbox, then a saved map of a room.
- ⬜ **Plumb:** the structural inspection layer ([below](#whats-next-plumb)).

## How it's made

1. **Design and print the chassis.** The differential-drive layout puts two N20 motors beside a 160 × 120 mm plate, a caster at the rear, and the battery near the wheel axle. The plate, motor clamps, and fit coupon were modeled in Onshape; the [chassis design spec](cad/chassis-design.md) records the dimensions and layout choices. The [OpenSCAD sources](cad/) generate the wheels, caster spacer, and body shell. The structural parts have been printed and dry-fitted on a Bambu P1S; the STL files and previews are in `cad/`.
2. **Control the wheels with a Pico W.** The wiring connects the Pico to an H-bridge motor driver and the two motor encoders ([pin map and bring-up order](docs/phase1-guide.md)). The [MicroPython firmware](pico/main.py) drives each motor with PWM, while [PIO encoder counting](pico/encoder.py) tracks wheel movement. It accepts `M <left> <right>` over USB serial or WiFi UDP and reports `E <left_count> <right_count>` at 20 Hz. If valid commands stop for 400 ms, it stops both motors.
3. **Drive it from a computer.** The [WASD teleop script](teleop/teleop_wasd.py) mixes forward and turn inputs into left and right motor commands, then sends them 10 times a second over serial or UDP. That repeating command is the firmware watchdog's heartbeat.
4. **Map the room (next).** A Raspberry Pi 5 running Ubuntu 24.04 and ROS 2 Jazzy will bridge motor commands and encoder counts, publish wheel odometry, take lidar scans, and feed both into `slam_toolbox` ([roadmap](docs/roadmap.md)).

## What's next: Plumb

**Plumb turns the rover into a structural inspector. It drives through a building and maps where the floors are sinking, sagging, or cracking.**

Buildings are infrastructure, and they fail quietly: foundations settle, floor slabs sag, cracks spread. Inspectors catch this by spot-checking a few places with a level and a tape measure. Plumb measures the whole floor and hands back a structural condition map instead of a handful of guesses.

**What it measures (three layers on one map):**

1. **Floor slope (settlement).** An MPU6050 IMU on the Pi's I2C bus reads the rover's tilt. The rover pauses ~0.5 s at each grid point for a clean reading, and uneven settlement shows up as a slope gradient across the map.
2. **Floor defects.** The same IMU picks up jolts as the wheels cross cracks, heaved joints, and spalled concrete. Each spike is pinned to the map position where it happened.
3. **Geometry vs. plan.** The lidar map is overlaid on the building's floor plan to flag walls and openings that are out of place or out of square.

**How it fits the existing stack:** a `plumb_logger` ROS 2 node reads the IMU, stamps each reading with the rover's pose from the `map → base_link` transform slam_toolbox already publishes, and bins readings into the occupancy-map grid. The output is the floor map with slope and defect layers on top. The only new hardware is a ~$5 IMU; the Pico firmware doesn't change.

**How it gets tested:**
- **Known slope:** plywood propped on books at 1–2°, checked against a phone level app.
- **Known defects:** cables and pencils taped to the floor as fake cracks, at measured positions.
- **Real run:** a garage or basement floor, spot-checked with a level.

## Gallery

| | | |
|---|---|---|
| ![chassis plate](cad/img/chassis-plate.png) | ![motor clamp](cad/img/motor-clamp.png) | ![body shell](cad/img/body-shell.png) |
| Chassis plate (34-hole grid system) | Motor clamp (N20, no-fastener tunnel) | Body shell (printable car-body skin) |
| ![wheel](cad/img/wheel.png) | ![test coupon](cad/img/test-fit-coupon.png) | ![caster spacer](cad/img/caster-spacer.png) |
| Drive wheel (rubber-band tires, D-bore) | Tolerance test coupon | Parametric caster spacer |

## Hardware

| Component | Choice | Rationale |
|---|---|---|
| Compute | Raspberry Pi 5 | Runs ROS2 + SLAM |
| Real-time motor control | Raspberry Pi Pico W | PWM + **encoder counting** (PIO) |
| Sensing | RPLidar A1 | Direct `LaserScan` fit for slam_toolbox ([D2](docs/decisions.md)) |
| Chassis | **3D-printed diff-drive plate + caster** (Bambu P1S) | Skid-steer corrupts odometry ([D5](docs/decisions.md)) |
| Motors | **N20 gearmotors with quadrature encoders** | SLAM needs odometry — encoders are not optional ([R1](docs/risks.md)) |
| Motor driver | SparkFun TB6612FNG (**not L298N**) | L298N wastes 2–4 V as heat ([D6](docs/decisions.md)) |
| Power | Battery → motor rail + separate 5V/5A buck → Pi | Shared rail = brownout reboots ([D7](docs/decisions.md)) |
| Inspection (Plumb) | MPU6050 IMU on the Pi's I2C bus | Floor tilt + defect jolts, ~$5 |

3D printing (Bambu P1S) covers all *structure*: chassis plate, motor mounts, wheel hubs, lidar mast, Pi/Pico tray. Drivetrain internals (motors, gears, caster) stay off-the-shelf. Budget: **~$340–425 CAD total, bought in three stages of ~$90–165** ([shopping-list.md](docs/shopping-list.md)).

## Software Stack

- **ROS2 Jazzy** on Ubuntu 24.04 — *not Humble*: Humble's Ubuntu 22.04 doesn't support the Pi 5 ([D1](docs/decisions.md))
- **slam_toolbox** for SLAM
- **Nav2** for autonomous navigation (stretch goal)
- **Python** for ROS2 nodes; **MicroPython + PIO** on the Pico ([D4](docs/decisions.md))
- Dev environment: WSL2 (learning) + headless Pi + Foxglove Studio (live viz) ([D8](docs/decisions.md))

## Phased Build Plan (~6–8 weeks)

### Phase 0 (Week 0) — Order parts & set up dev environment
Parts are bought in three stages from the [shopping list](docs/shopping-list.md), each one after the previous stage works. In parallel: WSL2 + Ubuntu 24.04 + ROS2 Jazzy, chassis CAD in Onshape, firmware drafted in the Wokwi simulator ([D9](docs/decisions.md)).

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

### Phase 5 — Plumb (structural inspection)
Mount the MPU6050, write the `plumb_logger` node, and render slope and defect layers over the saved map ([details above](#whats-next-plumb)). Only needs Phase 3 (a working map), not Phase 4.

## Repo Layout

```
docs/
  roadmap.md         # Phase-by-phase milestones and definitions of done
  phase1-guide.md    # Full Phase 1 execution plan: wiring, firmware steps, pin map
  shopping-list.md   # Staged cart (~$340–425 CAD total, 3 purchases)
  debugging-log.md   # Running log: what broke, why, how it was fixed
  decisions.md       # Design decisions D1–D9 with rationale
  risks.md           # Known failure modes R1–R10 and mitigations
pico/                # Pico firmware: main.py, encoder.py, host-side test harness
teleop/              # PC-side WASD driving script (WiFi/UDP or USB serial)
cad/                 # STLs, OpenSCAD sources, chassis design spec, renders
```

## Debugging Log

Every non-trivial problem gets an entry in [docs/debugging-log.md](docs/debugging-log.md): symptom, root cause, fix.
