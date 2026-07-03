"""Host-side simulation of the Pico firmware — runs main.py on a desktop PC.

The firmware expects MicroPython hardware modules (machine, rp2, a pollable
stdin, tick-based time). This harness fakes all of them around a VIRTUAL
CLOCK, feeds the firmware a scripted sequence of commands, then asserts that
the right things happened at the right times:

  1. boots with motors stopped (watchdog starts "tripped")
  2. "M 60 60" drives both motors at the expected PWM duty
  3. a 10 Hz command stream keeps the watchdog fed
  4. "M 150 -150" clamps to +/-100 (and reverse uses the reverse pin)
  5. after commands stop, the WATCHDOG kills the motors within ~400 ms
  6. telemetry "E <l> <r>" streams at ~20 Hz throughout
  7. garbage input is ignored (and does NOT feed the watchdog)

Run:  python pico/host_test/run_sim.py
"""

import importlib
import io
import os
import sys
import types
from contextlib import redirect_stdout

PICO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --------------------------- virtual world ----------------------------------

class SimDone(Exception):
    pass


class World:
    def __init__(self):
        self.now = 0                # virtual milliseconds
        self.end = 2600             # stop the sim here
        self.events = []            # (time_ms, text) -> arrives on "serial"
        self.pending = ""           # chars that have "arrived" but not been read
        self.duty_log = []          # (time_ms, pin, duty)

    def deliver_due(self):
        due = [e for e in self.events if e[0] <= self.now]
        for e in due:
            self.pending += e[1]
            self.events.remove(e)


world = World()

# scripted scenario ------------------------------------------------------------
world.events.append((200, "M 60 60\n"))
for t in range(300, 1001, 100):            # 10 Hz heartbeat, like the teleop script
    world.events.append((t, "M 60 60\n"))
world.events.append((1200, "M 150 -150\n"))  # clamp test; then SILENCE -> watchdog
world.events.append((2200, "X garbage\n"))   # invalid: must be ignored

# --------------------------- fake modules -----------------------------------

# fake time (tick-based, virtual)
fake_time = types.ModuleType("time")
fake_time.ticks_ms = lambda: world.now
fake_time.ticks_add = lambda a, b: a + b
fake_time.ticks_diff = lambda a, b: a - b


def _sleep_ms(ms):
    world.now += ms
    world.deliver_due()
    if world.now > world.end:
        raise SimDone


fake_time.sleep_ms = _sleep_ms
fake_time.sleep = lambda s: _sleep_ms(int(s * 1000))

# fake machine
fake_machine = types.ModuleType("machine")


class Pin:
    IN, OUT, PULL_UP = 0, 1, 2

    def __init__(self, pin_id, *a, **k):
        self.id = pin_id

    def value(self, v=None):
        return 0


class PWM:
    def __init__(self, pin):
        self.pin = pin.id
        self._duty = 0

    def freq(self, f):
        pass

    def duty_u16(self, d):
        if d != self._duty:
            world.duty_log.append((world.now, self.pin, d))
        self._duty = d


fake_machine.Pin = Pin
fake_machine.PWM = PWM

# fake select (poll-style, like MicroPython's)
fake_select = types.ModuleType("select")
fake_select.POLLIN = 1


class _Poll:
    def register(self, *a):
        pass

    def poll(self, timeout=0):
        world.deliver_due()
        return [1] if world.pending else []


fake_select.poll = _Poll

# fake stdin the firmware can read char-by-char
class FakeStdin:
    def read(self, n=1):
        ch, world.pending = world.pending[:1], world.pending[1:]
        return ch


# --------------------------- run the firmware -------------------------------

sys.modules["time"] = fake_time
sys.modules["machine"] = fake_machine
sys.modules["select"] = fake_select
real_stdin = sys.stdin
sys.stdin = FakeStdin()
sys.path.insert(0, PICO_DIR)

captured = io.StringIO()
try:
    with redirect_stdout(captured):
        importlib.import_module("main")     # runs the firmware's main loop
except SimDone:
    pass
finally:
    sys.stdin = real_stdin
    sys.modules.pop("time", None)           # let the real module back in
    import time  # noqa: F401  (re-import real time for anything after)

output = captured.getvalue()

# --------------------------- assertions -------------------------------------

L_FWD, L_REV, R_FWD, R_REV = 2, 3, 4, 5
DUTY_60 = int(60 / 100 * 0.85 * 65535)     # expected duty for "M 60 60"
DUTY_100 = int(100 / 100 * 0.85 * 65535)   # expected duty after clamping 150

def duty_at(pin, t):
    """Last duty set on `pin` at or before virtual time t."""
    val = 0
    for when, p, d in world.duty_log:
        if p == pin and when <= t:
            val = d
    return val

results = []

def check(name, cond, detail=""):
    results.append((name, cond, detail))

check("boots into safe state (motors 0, watchdog pre-tripped)",
      duty_at(L_FWD, 150) == 0 and duty_at(R_FWD, 150) == 0)

check("encoder gracefully falls back on a PIO-less platform",
      "encoder init failed" in output)

check("firmware announces ready",
      "rover firmware ready" in output)

check(f"'M 60 60' -> both forward duties = {DUTY_60}",
      duty_at(L_FWD, 250) == DUTY_60 and duty_at(R_FWD, 250) == DUTY_60,
      f"got L={duty_at(L_FWD, 250)} R={duty_at(R_FWD, 250)}")

check("10 Hz heartbeat keeps watchdog quiet through t=1000",
      duty_at(L_FWD, 1000) == DUTY_60)

check(f"'M 150 -150' clamps to +/-100 (fwd={DUTY_100}, right uses REVERSE pin)",
      duty_at(L_FWD, 1300) == DUTY_100
      and duty_at(R_REV, 1300) == DUTY_100
      and duty_at(R_FWD, 1300) == 0,
      f"got Lfwd={duty_at(L_FWD, 1300)} Rrev={duty_at(R_REV, 1300)} Rfwd={duty_at(R_FWD, 1300)}")

check("WATCHDOG stops all motors within ~500 ms of silence",
      duty_at(L_FWD, 1750) == 0 and duty_at(R_REV, 1750) == 0
      and "watchdog: no command" in output)

telemetry_count = output.count("E 0 0")
check("telemetry streams at ~20 Hz (expect ~50 lines in 2.6 s)",
      35 <= telemetry_count <= 60, f"got {telemetry_count}")

check("garbage input ignored (motors still stopped at t=2400)",
      duty_at(L_FWD, 2400) == 0 and duty_at(R_FWD, 2400) == 0)

# --------------------------- report -----------------------------------------

print("=" * 64)
print("FIRMWARE HOST SIMULATION — 2.6 simulated seconds")
print("=" * 64)
passed = 0
for name, ok, detail in results:
    print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail and not ok else ""))
    passed += ok
print("-" * 64)
print(f"{passed}/{len(results)} checks passed")
print()
print("--- firmware output (first/last lines) ---")
lines = output.splitlines()
for line in lines[:6]:
    print("  " + line)
print(f"  ... ({len(lines)} lines total) ...")
for line in lines[-4:]:
    print("  " + line)

sys.exit(0 if passed == len(results) else 1)
