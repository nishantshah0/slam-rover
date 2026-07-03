# Risk Register — Where This Build Can Fail

Every item here is a *known* failure mode of this exact kind of build (Pi + Pico
+ lidar + ROS2 SLAM rover), with the why and the mitigation. Ordered by severity.

---

## R1 — No wheel encoders → SLAM produces a smeared, useless map 🔴 CRITICAL

**The problem:** The original hardware list has no encoders. slam_toolbox
expects **odometry** — a running estimate of "how far have I moved" — published
as an `odom → base_link` transform. It fuses that with lidar scan-matching.
Without odometry, scan-matching alone has to guess the robot's motion from
scratch every scan; in feature-poor areas (long hallways, blank walls) it loses
lock and the map smears or folds over itself.

**Why encoders solve it:** Encoders are small sensors on the motor shafts that
count wheel rotations. Wheel rotations × wheel circumference = distance moved.
That's odometry. The Pico counts encoder pulses (this is *the* reason a
real-time microcontroller is in the design) and streams counts to the Pi.

**Mitigation:**
- Buy motors **with quadrature hall encoders** (e.g. N20 or JGA25-371 gearmotors
  with encoders). Do NOT buy the cheap yellow "TT motor" kits — no usable encoders.
- Encoder reading is now part of Phase 1 firmware; the odometry node is Phase 2.

## R2 — Skid-steer (4WD/tracked) has bad rotation odometry 🔴 HIGH

**The problem:** A 4-wheel or tracked chassis turns by *skidding* — the wheels
slip sideways during every turn. Slipping wheels lie: encoders say "we turned
90°" but the robot actually turned 70°. Rotation error is the most damaging
kind for SLAM (a small heading error becomes a large position error a few
meters later).

**Mitigation:** Use a **2-wheel differential drive chassis + caster wheel**.
Two driven wheels turn without skidding, so encoder odometry is honest. This is
what TurtleBots use — it's the standard indoor SLAM platform shape for a
reason. If you must use 4WD, expect to lean much harder on scan-matching and
tune for it. See decision D6.

## R3 — Power brownouts reboot the Pi mid-run 🔴 HIGH

**The problem:** The Pi 5 wants **5V/5A (25W)** — more than most USB power
banks or cheap converters deliver. Worse, if motors and Pi share one supply,
every motor start/stall pulls the battery voltage down for a few milliseconds
("voltage sag"), and the Pi browns out and reboots. This shows up as
"my rover randomly restarts when it drives" — a classic.

**Mitigation — two separate power rails from one battery:**
- Battery (6×AA NiMH pack) → **motor driver directly** (motors tolerate sag)
- Battery → **dedicated 5V/5A buck converter → Pi 5** (buck rides through sag)
- **Common ground between everything** (circuits need a shared voltage reference)
- The lidar (~0.5A) powers off the Pi's USB — fine *if* the Pi itself has a 5A
  feed (on a weaker feed the Pi limits total USB output current).

## R4 — Runaway rover: motors keep spinning when software dies 🟠 MEDIUM

**The problem:** The Pico holds the last motor command it received. If the
serial link drops, the Pi crashes, or a node hangs, the rover keeps driving
into the wall at full speed.

**Mitigation:** A **watchdog timeout in the Pico firmware**: if no valid
command arrives for ~300–500 ms, stop the motors. The Pi-side teleop/driver
node therefore re-sends commands at ~10 Hz even when unchanged. This is
non-negotiable and is now a Phase 1 firmware requirement. (It's also a great
interview line: "my firmware fails safe.")

## R5 — Wrong motor driver: the L298N trap 🟠 MEDIUM

**The problem:** Nearly every beginner tutorial uses the L298N. It's ancient
Darlington-transistor tech that *eats 2–4 V* of your battery as heat — your
6 V motors might see 3.5 V and crawl.

**Mitigation:** Use a modern MOSFET driver: **TB6612FNG** (cheap, ~1 A/channel)
or a **Cytron MDD3A/MDD10A** (more headroom, dead simple). Near-zero voltage
drop, no heatsink drama.

## R6 — No dev-machine plan: RViz on the Pi is painful 🟠 MEDIUM

**The problem:** RViz (ROS2's 3D visualization tool — you'll live in it during
Phase 3) is sluggish on a Pi, and the plan had ROS2 learning happening…where?
The rover has no screen.

**Mitigation:**
- Run the Pi **headless** (Ubuntu Server 24.04, SSH in).
- Learn ROS2 in **WSL2 on this Windows machine** (Ubuntu 24.04 + ROS2 Jazzy
  installs cleanly; RViz works via WSLg). All Phase 2 ROS2 exercises happen
  here — no robot required.
- To visualize the *live rover*, use **Foxglove Studio** on Windows connected
  to a `foxglove_bridge` on the Pi over WiFi. This deliberately sidesteps DDS
  discovery between WSL2 and the LAN, which is flaky through WSL2's NAT — a
  rabbit hole not worth entering.

## R7 — MicroPython misses encoder pulses at speed 🟡 LOW-MED

**The problem:** A geared motor's encoder can emit thousands of pulses/second.
Counting them with Python interrupt handlers drops counts at speed → odometry
silently under-reports distance.

**Mitigation:** Use the Pico's **PIO** (Programmable I/O — tiny hardware
state machines that count pulses with zero CPU involvement). Usable from
MicroPython. If it becomes a fight, that's the trigger to switch to the C SDK
(decision D4).

## R8 — Lidar mounting and orientation surprises 🟡 LOW-MED

**The problem:** Three recurring ones: (a) the lidar is mounted low and sees
the rover's own posts/wires as permanent obstacles; (b) its "forward" doesn't
match the robot's forward, so the map builds rotated/mirrored; (c) motor
vibration blurs scans.

**Mitigation:** Mount it **top-center with 360° clearance** (this is your one
3D-printed mount); establish the `base_link → laser` transform carefully in
Phase 3 (this is exactly what tf is for); add foam/rubber standoffs if scans
look noisy. Also: RPLidar struggles with direct sunlight and matte-black
surfaces — demo indoors, curtains drawn.

## R9 — Two-computer code workflow confusion 🟡 LOW

**The problem:** This repo lives in OneDrive on Windows, but the ROS2 code
*runs* on the Pi (Linux). Editing in both places without discipline = lost work.

**Mitigation:** **GitHub is the single source of truth.** Push from wherever
you edit, pull before you edit anywhere else. (Also: create the GitHub repo
with a portfolio-worthy name like `slam-rover` — recruiters see repo names.)

## R10 — Slow-burn practical risks 🟡 LOW

- **Parts lead time:** shipping can eat 1–2 weeks of an 8-week plan → order
  each stage *early* (Stage 1 in Week 0; Stage 2 by ~week 2; Stage 3 by ~week 3),
  and prefer fast shipping over AliExpress for anything on the critical path.
  If a part dies, that's when the university makerspace / a quick Amazon
  next-day order covers you — the lean cart skips pre-bought spares.
- **SD card corruption:** cutting power without shutdown corrupts the card
  eventually → `sudo shutdown now` before flipping the switch; keep a backup
  image of the card once it's set up.
- **Battery safety:** LiPos are unforgiving (charge on a LiPo-safe surface,
  never over-discharge). A protected 18650 pack or NiMH pack is the
  lower-stress option at slight weight/power cost.
