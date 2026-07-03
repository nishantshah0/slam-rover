# Pico Firmware — What Every Piece Is and Why

Three files, one job: turn "M 60 60" arriving over USB or WiFi into spinning
wheels, report back how far they actually turned, and fail safe.

| File | Role |
|---|---|
| [main.py](main.py) | Motors, watchdog, command parsing, WiFi/UDP, telemetry |
| [encoder.py](encoder.py) | PIO-hardware pulse counting (odometry's raw material) |
| [../teleop/teleop_wasd.py](../teleop/teleop_wasd.py) | Runs on your PC — the driver's seat |

## The concepts, in the order the code uses them

**PWM (Motor class).** A GPIO pin is only ever fully ON or OFF. So to get
"60% power," we switch it 20,000 times a second and make it ON 60% of each
cycle. The motor's inertia averages that into smooth partial power. 20 kHz is
chosen because it's above human hearing — at lower frequencies motors audibly
whine. The `DUTY_CAP = 0.85` exists because our 7.2 V battery feeds 6 V
motors: capping duty at 85% means the *average* voltage never exceeds spec.

**Sign-magnitude drive (why two pins per motor).** Inside the MDD3A is an
H-bridge — four electronic switches around the motor. PWM into the A input
closes one diagonal pair (current flows left-to-right: forward); PWM into B
closes the other diagonal (right-to-left: reverse). Our `Motor.set(-100..100)`
just decides which pin gets the duty cycle.

**Quadrature counting (encoder.py).** Two sensors watch a magnet disc on the
motor shaft, producing square waves offset by a quarter turn. Which signal
*leads* tells direction; counting *changes* tells distance. At speed that's
thousands of changes per second — too fast for Python — so a PIO state machine
(a tiny hardware co-processor inside the RP2040) does it and Python just asks
for the total. The PIO program is a MicroPython port of Raspberry Pi's own
reference implementation (credited in the file).

**The watchdog (main loop).** The firmware tracks when the last valid command
arrived. 400 ms of silence → motors stop, LED starts blinking. The teleop
script therefore *re-sends* the current command 10×/second even when nothing
changed — those repeats are a heartbeat, and silence means the driver is gone
(crashed script, dead cable, out of WiFi range). The rover never runs away.

**Two transports, one protocol.** Commands are plain text lines ("M 60 60")
whether they arrive by USB serial or WiFi UDP. Plain text costs a few bytes
but you can *type commands by hand* in Thonny to test — debuggability beats
efficiency everywhere in this project.

## Running it in Wokwi (now, $0, no hardware)

1. Go to **wokwi.com → "MicroPython on Pi Pico W"** new project.
2. Replace its main.py with ours; add a new file tab named `encoder.py` and
   paste ours in. (Encoder init may fail in the sim — that's expected and
   handled; you'll see the note and counts of 0.)
3. Set `WIFI_SSID = "Wokwi-GUEST"` (no password) to exercise the WiFi path,
   or leave `""` for serial-only.
4. Click ▶. In the serial monitor type `M 60 60` → watch telemetry flow.
   Click the Pico's pins panel or wire LEDs (long leg to GP2–GP5, short leg
   via a resistor to GND) to *see* the motor outputs light up.
5. **Watchdog test in sim:** send one `M 60 60`, then stop typing — within
   half a second: `# watchdog: no command for 400ms - motors stopped`.

The sim's one limit: your PC's teleop script can't reach into Wokwi's
virtual network, so the WASD-over-UDP experience waits for real hardware.
The *logic* it exercises is identical.

## Flashing the real Pico (when Stage 1 arrives)

1. Hold BOOTSEL, plug in USB → drag the MicroPython **Pico W** .uf2
   (micropython.org) onto the drive that appears.
2. In Thonny: save `encoder.py` and `main.py` onto the Pico (File → Save as →
   Raspberry Pi Pico). A file named `main.py` runs automatically at power-on.
3. Put your home WiFi into `WIFI_SSID`/`WIFI_PASSWORD` — the rover prints its
   IP at boot; that IP goes into the teleop `--udp` argument.
4. Bring-up order is phase1-guide Steps 1–4 — one subsystem at a time, wheels
   in the air.

## Tuning knobs you'll touch later

- `ENCODER_DIR` — flip signs after the Step 3 hand-spin test if a side counts
  backward.
- `DUTY_CAP` — raise toward 1.0 only if you switch to a true 6 V supply.
- `WATCHDOG_MS` — 400 is right for WiFi driving; don't raise it to "fix" a
  flaky link (fix the link).
