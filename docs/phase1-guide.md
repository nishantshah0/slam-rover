# Phase 1 Guide — Get It Moving (Weeks 1–2)

The complete Stage 1 execution plan. End state: a wireless, keyboard-driven
robot with encoder feedback and fail-safe firmware, on a chassis you designed.
No ROS2 anywhere in this phase — that's deliberate (learn hardware without
learning ROS2 at the same time).

**Golden rules for the whole phase:**
- Wheels off the ground for every first test of anything.
- Never touch wiring while the battery is connected.
- Multimeter checks polarity *before* a board sees power, every time.
- Change one thing between tests. One.
- 20+ minute fight → entry in [debugging-log.md](debugging-log.md).

---

## Step 0 — Order + while-the-box-ships (Days 1–3)

**0.1 Order the Stage 1 cart** ([shopping-list.md](shopping-list.md), ~$165).
Get the 6×AA holder **with a built-in switch** — that's your power switch.

**0.2 Install Thonny** (thonny.org) — a beginner Python IDE that talks to the
Pico natively. This is your firmware cockpit for all of Phase 1.

**0.3 Chassis CAD.** Make a free student **Onshape** account
(runs in the browser, nothing to install). We design together:

- **Plate:** ~160 × 120 mm, 4–5 mm thick. Fits the P1S bed easily.
- **Layout:** two N20s on the *center line* (left/right edges), caster at the
  rear, battery holder centered and low (heaviest part near the wheels =
  stable + honest odometry), breadboard + MDD3A + buck on top with room to spare.
- **Motor mounts:** N20s are a standard brick shape (~12×10×26 mm + gearbox);
  printed C-clamp mounts with M2 screw holes (or snap-fit) — proven pattern,
  we'll model it in one session.
- **Print settings:** PLA is fine, 4 walls, 30% infill, no supports needed if
  we design flat-side-down (we will).

Design time budget: 2–3 hours across a couple of evenings. **This is CAD
portfolio material — export nice screenshots as you go.**

**0.4 (Optional, $0):** start Phase 0's software half — WSL2 + ROS2 Jazzy on
this PC. Independent of everything above.

---

## Step 1 — Pico hello world (Evening 1, ~1 hour)

**Concepts first:** what firmware is; what MicroPython is (Python that runs
*on* the chip, no OS); what the REPL is (a live Python prompt running on the
Pico — you type, the chip obeys instantly).

1. Hold the **BOOTSEL** button, plug the Pico into USB → it appears as a USB
   drive. Drag the MicroPython **.uf2** file onto it (Pico W version, from
   micropython.org). It reboots as a Python machine. That's "flashing."
2. Open Thonny → select the Pico interpreter → type into the REPL:
   blink the onboard LED.
3. Save a `main.py` that blinks forever → unplug/replug → it blinks with no
   PC attached. **The Pico is now autonomous.**

✅ **Done when:** LED blinks with no computer attached.

---

## Step 2 — One motor spins on the bench (Evening 2, ~2 hours)

**Concepts first:** voltage/current/ground; why every board must share a
ground (electricity needs a complete loop and a common "zero" reference);
**PWM** — the pin can only be fully ON or OFF, so we switch it thousands of
times per second and the *ratio* of on-time becomes "70% power"; **H-bridge**
— the four-switch circuit inside the MDD3A that lets current flow through the
motor in either direction (that's reverse).

**Wiring (battery DISCONNECTED, wheels in the air):**

| From | To |
|---|---|
| Battery + / − | breadboard power rails (multimeter-check polarity FIRST) |
| TB6612 VM | battery + rail; TB6612 GND → battery − rail |
| TB6612 VCC, **STBY, PWMA, PWMB** | all → Pico 3V3 (the tie-high trick, D6) |
| Motor 1 M+/M− (dupont ends of its cable) | TB6612 AO1 / AO2 pins |
| TB6612 AIN1 / AIN2 | Pico GP2 / GP3 (dupont) |
| Pico GND | battery − rail ← **the common ground** |

The logic per motor (with PWMA/B tied high): PWM on IN1 → forward, PWM on
IN2 → reverse, both low → stop — identical to what the firmware expects.

**Code ladder (each ~10 lines, run from Thonny):** motor full speed → motor
at 30/60/90% duty (see PWM become "speed") → reverse → a `set_motor(speed)`
function taking −100…+100.

One battery note: 6×NiMH ≈ 7.2 V into 6 V motors — slight overvolt is fine;
we cap PWM duty at ~85% in code and never think about it again.

✅ **Done when:** `set_motor(50)` then `set_motor(-50)` does exactly what it
says, wheel in the air.
⚠️ **Predicted fight:** motor spins the wrong way → swap its two wires at the
screw terminals. Everyone does this. Log it anyway.

---

## Step 3 — Encoders: odometry is born (Evening 3, ~2 hours)

**Concepts first:** the encoder is two tiny sensors watching a magnet disc on
the motor shaft, producing two pulse streams (A and B) offset by a quarter
cycle — **quadrature**. Count edges = distance; whether A leads B or B leads A
= direction. And **PIO**: the Pico's little hardware co-processors that count
these pulses in hardware so Python never misses one at speed (risk R7). I'll
provide the PIO quadrature program and we'll walk through what each line does.

**Wiring per encoder:** VCC → Pico 3V3, GND → GND, A/B → GP6/GP7 (left).

**The magic test:** run the counter, **turn the wheel slowly by hand**, watch
the number climb. Backwards → it falls. You are watching odometry exist.

**Calibrate:** rotate the wheel exactly 10 turns by hand (mark the tire),
read the count, divide by 10 → **counts per wheel revolution**. Write this
number down — it's a constant in every odometry calculation for the rest of
the project.

✅ **Done when:** hand-spin counts up forward / down backward, and you know
your counts-per-rev number.

---

## Step 4 — Both sides + serial protocol + THE WATCHDOG (Evenings 4–5, ~3 hours)

Duplicate motor 2 (GP4/GP5) and encoder 2 (GP8/GP9). Then give the robot a language:

```
PC → Pico:   M <left> <right>      speeds −100…100, e.g. "M 60 60"
Pico → PC:   E <left_count> <right_count>    streamed at 20 Hz
```

Firmware structure (we write it together, ~60 lines): read a line → parse →
set motors → every 50 ms send encoder counts → **and a watchdog: if no valid
`M` command has arrived in 400 ms, stop both motors** (risk R4).

✅ **Done when — the watchdog test:** drive via typed commands, then just
*stop typing* → wheels halt within half a second. Later: kill the connection
mid-drive → same result. **Film this test** — "my firmware fails safe" is an
interview line.

---

## Step 5 — Assembly on your printed chassis (Weekend, ~3 hours)

Print the final plate + mounts (revised with anything the bench taught us).
Mount: motors in their printed clamps, wheels on shafts, caster, battery
holder (velcro or screws), breadboard + MDD3A + buck on standoffs or foam
tape. Wire it — same circuit as the bench, just tidier: power wires twisted,
signal wires zip-tied away from motor wires, nothing touching a wheel.

**Power for untethered driving:** battery → buck (screw terminals) → set the
buck to **exactly 5.0 V with the multimeter BEFORE connecting anything** →
buck output → Pico **VSYS + GND** pins. (Safe to also have USB plugged in;
the Pico handles both.)

✅ **Done when:** rover sits on its wheels, both motors respond, encoders
count, nothing rattles when you shake it gently.

---

## Step 6 — Wireless WASD driving (Evenings 6–7, ~3 hours)

Why the Pico **W**: it has WiFi, so teleop needs no cable and no extra parts.

1. Pico joins your home WiFi at boot (10 lines of MicroPython).
2. Pico listens for UDP packets carrying the same `M <l> <r>` commands.
   **The watchdog doesn't care whether commands arrive by USB or WiFi — walk
   out of range and the rover stops.** Same fail-safe, zero new safety code.
3. On the PC: a small Python script (I provide it, we dissect it) — hold
   W/A/S/D → sends commands at 10 Hz; release → sends stop.

First drive: rover on the floor, slow speed cap, thumb hovering over the
battery switch. Then: **film the demo video.** Drive a lap, spin in place,
park it.

✅ **PHASE 1 DONE when:** WASD lap on video + watchdog kill-test on video.

⚠️ **Predicted fights:** university/dorm WiFi blocks device-to-device traffic
(use your phone's hotspot instead — works every time); one wheel slightly
faster than the other so it drives in a shallow arc (normal! open-loop motors
differ — *this is exactly why encoders and closed-loop control exist*, and
it foreshadows Phase 2).

---

## Pin map (single source of truth)

| Pico pin | Goes to |
|---|---|
| GP2 / GP3 | MDD3A motor **left** (A = forward, B = reverse) |
| GP4 / GP5 | MDD3A motor **right** |
| GP6 / GP7 | Encoder **left** A / B |
| GP8 / GP9 | Encoder **right** A / B |
| 3V3 (pin 36) | Both encoders VCC |
| GND (any) | Common ground: MDD3A GND pin + encoder GNDs + buck − |
| VSYS (pin 39) | Buck + output (5.0 V, verified by multimeter first) |

## Phase 1 exit checklist

- [ ] WASD driving video (wireless)
- [ ] Watchdog kill-test video
- [ ] Counts-per-wheel-rev number written down
- [ ] Wiring photo + CAD screenshots saved
- [ ] `pico/` firmware pushed to GitHub
- [ ] At least 2 debugging-log entries (there will be more)
- [ ] You can explain to a rubber duck: PWM, H-bridge, quadrature, watchdog

Then Stage 2 order goes in, and Phase 2 begins.
