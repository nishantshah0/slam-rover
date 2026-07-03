# Beginner Roadmap — How You'll Actually Do This

You don't need to already know robotics to finish this project. You need to
climb a ladder of small, testable wins in the right order. This document is
the ladder.

## The five working rules

1. **One new variable at a time.** Never change two things between tests. If
   you wire a new component AND change code, and it breaks, you can't know
   which did it. This single habit is most of what "debugging skill" is.
2. **Bench before robot.** Every component proves itself on the desk (motor
   spins in mid-air, lidar publishes on a desk) before it gets mounted.
   Integration is where bugs hide; make sure the pieces were innocent first.
3. **Small wins, always demonstrable.** Each milestone below is something you
   can *see working* in under a minute. If you're 3 hours into something with
   nothing demonstrable, back up to the last working state.
4. **Log every fight.** When something breaks for more than ~20 minutes, it
   earns an entry in [debugging-log.md](debugging-log.md). This is your
   interview material generating itself.
5. **~8–10 hours/week.** That's the pace the 6–8 week timeline assumes. A
   blocked evening is normal; a blocked week means ask for help (see
   "When you're stuck" below).

## Working pattern

For every new topic the pattern is: **concept first, then code, then test,
then log.** I explain what a thing *is* and why it exists before we write any
of it; we write code in small pieces you can run immediately; you tell me what
the hardware actually did (I can't see it — your observations are the sensor);
when we fix something, we log it. Ask "why" as often as you want — for an
internship interview, understanding *why* the tf tree is shaped the way it is
beats having a working rover you can't explain.

---

## Phase 0 (Week 0) — Order parts, build your workshop

**Goal:** parts in the mail, dev environment working, so Week 1 starts with zero setup friction.

**New concepts:** flashing an OS image, SSH (controlling a computer with no
screen over the network), WSL2 (a real Linux inside Windows), git push/pull.

**Milestone ladder:**
- [ ] Order **Stage 1** of the [shopping list](shopping-list.md) (~$165)
- [x] WSL2 + Ubuntu 24.04 installed on this PC *(2026-07-02)*
- [x] ROS2 Jazzy installed in WSL2; talker/listener test passed ← *first ROS2 moment: done* *(2026-07-02)*
- [x] GitHub repo created and pushed: https://github.com/nishantshah0/slam-rover *(2026-07-02)*
- [ ] (moves to ~week 2, when the Stage 2 box arrives) Pi flashed with Ubuntu Server 24.04, SSH from Windows works

**Definition of done:** Stage 1 is ordered and you've seen two ROS2 nodes talk to each other in WSL2.

**Likely first fight:** WiFi config on a headless Pi (no screen to type on).
The fix is cloud-init/`network-config` on the SD card — we'll set it up before first boot.

---

## Phase 1 (Weeks 1–2) — Get it moving

**Goal:** drivable rover via keyboard over SSH. No ROS2 anywhere — this phase is electronics + firmware only, on purpose.

**New concepts (each explained when we hit it):**
- *Voltage/current/ground*, and why every board must share a ground
- *PWM* — how you get "70% speed" out of a pin that can only be ON or OFF (switch it very fast)
- *H-bridge* — the circuit trick that lets a motor run backwards (what the MDD3A does)
- *Quadrature encoders* — two offset pulse streams; the offset tells you spin direction, the count tells you distance
- *Serial (UART over USB)* — the byte-pipe the Pi and Pico talk through

**Milestone ladder** (each one is minutes-to-an-hour of work, in order):
- [ ] Pico blinks its LED (MicroPython "hello world" — proves toolchain)
- [ ] Pico echoes what you type over USB serial (proves the byte-pipe)
- [ ] One motor spins **on the bench**, driver wired, wheel in mid-air
- [ ] Motor speed and direction controlled from code (PWM working)
- [ ] Encoder counts stream to the screen as you turn the wheel **by hand** — watch the count go up, spin it backwards, watch it go down ← *this is odometry being born*
- [ ] Both motors + both encoders working on the bench
- [ ] **Watchdog test: unplug the USB cable mid-drive → motors stop within half a second** (risk R4 — do not skip)
- [ ] Chassis assembled, two power rails wired (battery→driver, battery→buck→Pi)
- [ ] Drive it around the room with WASD keys over SSH 🎉 **(film this)**

**Definition of done:** the WASD drive video, and the watchdog test passing.

**Likely first fights:** motor spins the wrong way (swap its two wires — every
robotics person has done this); nothing works because grounds aren't common
(multimeter finds it in minutes); encoder counts *down* when driving forward
(sign flip in code).

---

## Phase 2 (Weeks 3–4) — ROS2 fundamentals + sensing + odometry

**Goal:** by the end, the rover speaks fluent ROS2: lidar scans and odometry
out, velocity commands in. Two parallel tracks so a blocked one never stalls the week.

### Track A — Learn ROS2 in WSL2 (no robot needed)

**New concepts:** *nodes* (small programs that each do one job), *topics*
(named channels they publish/subscribe on — a group chat for programs),
*messages* (typed contents, e.g. `LaserScan`, `Twist`, `Odometry`), *launch
files* (start ten nodes with one command), *tf* (the live family tree of
"where is everything relative to everything else").

- [ ] Official ROS2 Jazzy beginner tutorials: CLI tools, then turtlesim
- [ ] Write your own publisher + subscriber pair in Python
- [ ] Write a node that subscribes to turtlesim's pose and publishes commands back — a closed loop, the shape of all robotics software
- [ ] First launch file

### Track B — Robot plumbing (on the Pi)

- [ ] ROS2 Jazzy on the Pi; `sllidar_ros2` driver publishing `/scan` — **see your room as a live point ring in Foxglove Studio on Windows** ← *the single most motivating moment of the whole project*
- [ ] `serial_bridge` node: subscribes `/cmd_vel` (velocity commands) → serial to Pico; reads encoder counts ← Pico
- [ ] Drive the rover with `teleop_twist_keyboard` — same driving as Phase 1, but now it's ROS2 messages doing it
- [ ] `odometry` node: encoder ticks → wheel distances → *diff-drive kinematics* (one page of geometry we'll walk through slowly — ticks in, position-and-heading out) → publish `/odom` + the `odom → base_link` transform
- [ ] **Odometry sanity check:** drive 1 m forward with a tape measure down — does `/odom` say ~1 m? Rotate in place 360° — does heading come back to ~start?

**Definition of done:** Foxglove shows the scan ring live, and the tape-measure odometry test passes within ~5%.

**Likely first fights:** lidar USB permissions on Ubuntu (udev rules); WSL2↔Pi
networking temptation (don't — Foxglove over the bridge, per D8); radians vs
degrees somewhere in the odometry math.

---

## Phase 3 (Weeks 5–6) — SLAM: the boss fight

**Goal:** drive the rover around a room; watch a clean map build; save it. This is the phase that *is* the portfolio piece.

**New concepts:** *coordinate frames & the tf tree* (`map → odom → base_link → laser`
— who publishes each arrow and why), *scan matching* (sliding the current lidar
scan over the map until it clicks into place), *loop closure* (recognizing
"I've been here before" and snapping accumulated drift out of the whole map),
*URDF/static transforms* (telling ROS the lidar sits 12 cm above and 3 cm
ahead of the robot's center).

**Milestone ladder:**
- [ ] Static transform `base_link → laser` published (measure the lidar's mounting offset with a ruler — yes, really)
- [ ] tf tree verified with `view_frames` — one connected tree, no orphans
- [ ] slam_toolbox launches; map appears in Foxglove and grows as you drive
- [ ] Slow lap of the room (slow = better scans = better map)
- [ ] Loop closure observed: drive back to the start and watch the map visibly *snap* tighter
- [ ] Map saved (`map_saver`); the PNG goes in the repo ← **this image is the money shot**
- [ ] Repeatability: map the same room twice; the maps should agree

**Definition of done:** a saved map a stranger could recognize the room from, plus a screen-recording of it building.

**Likely first fights (this phase is 50% debugging by design):** map builds
rotated/mirrored (lidar mounted backwards → fix the static transform, not the
hardware); "message filter dropping message" (timestamps/QoS mismatch — a rite
of passage; we'll decode it together); map smears in the long hallway
(drive slower, tune scan-matching, check odometry quality from Phase 2).

**⛳ Success checkpoint reached.** Everything after this line is bonus.

---

## Phase 4 (Stretch) — Autonomy with Nav2

**Goal:** click a point in the map; the rover drives itself there, around obstacles.

**New concepts:** *localization* (using a finished map to answer "where am I" —
slam_toolbox has a localization mode), *costmaps* (the map inflated by "don't
drive this close to walls"), *planners* (global = route on the map; local =
steering around what the lidar sees right now), *PID control* (closing the
loop so "send 0.2 m/s" actually produces 0.2 m/s at the wheels — Pico-side
upgrade that makes Nav2 dramatically better behaved).

**Milestone ladder:** PID wheel-velocity control on the Pico → Nav2 bringup on
the saved map → rover localizes → first click-to-drive goal → obstacle placed
mid-route gets avoided **(film this too)**.

---

## When you're stuck

In order: (1) re-read the error message slowly — ROS2 errors usually *do* say
what's wrong; (2) reduce to the last working state and re-add one thing;
(3) bring me the exact error text + what you changed since it last worked;
(4) 30 minutes of genuine stuckness = stop, log it, move to the other track —
sleep fixes robots more often than seems reasonable.

## The portfolio payoff (collect as you go)

- **Phase 1:** WASD driving video + a wiring photo + watchdog fail-safe story
- **Phase 2:** Foxglove screenshot of the live scan ring + the odometry tape-measure test
- **Phase 3:** the saved map PNG + a timelapse of it building + your two best debugging-log war stories
- **Phase 4:** click-to-drive video with an obstacle dodge
- **Throughout:** [debugging-log.md](debugging-log.md) *is* the answer to "tell me about a hard problem you solved" — with dates proving it happened.
