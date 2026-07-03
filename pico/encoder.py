# Quadrature encoder counter using the Pico's PIO hardware.
#
# WHY THIS EXISTS (risk R7): the N20 encoders emit thousands of pulses/second
# at speed. Counting them in Python interrupts silently drops counts. The PIO
# is a tiny hardware state machine inside the RP2040 that watches the two
# encoder pins every clock cycle and keeps the count in a register — Python
# just asks for the total when it wants it.
#
# HOW QUADRATURE WORKS: the encoder outputs two square waves, A and B, offset
# by a quarter cycle. Each time the pin pair changes state, the 2-bit
# (old A,B) + 2-bit (new A,B) pattern tells the PIO whether the wheel moved
# +1 or -1 step. The 16-entry jump table below encodes exactly that: the
# program computes a 4-bit index (old state << 2 | new state) and jumps into
# the table, which routes to increment / decrement / no-change.
#
# PROVENANCE: MicroPython port of Raspberry Pi's official pico-examples
# quadrature_encoder.pio, as posted (and reported working) on the Raspberry Pi
# forums (viewtopic.php?t=378082, user BillTodd, Oct 2024).
# NOTE: verify on real hardware at bring-up (hand-spin test, phase1-guide
# Step 3) — this file cannot be fully tested in simulation.

import rp2
from machine import Pin


@rp2.asm_pio(autopush=False, autopull=False)
def _quadrature_counter():
    # --- 16-entry jump table (must sit at PIO address 0) -------------------
    # index = (previous A,B state << 2) | (current A,B state)
    jmp("update")        # 00 -> 00  no movement
    jmp("decrement")     # 00 -> 01
    jmp("increment")     # 00 -> 10
    jmp("update")        # 00 -> 11  invalid transition (skipped a state)

    jmp("increment")     # 01 -> 00
    jmp("update")        # 01 -> 01
    jmp("update")        # 01 -> 10  invalid
    jmp("decrement")     # 01 -> 11

    jmp("decrement")     # 10 -> 00
    jmp("update")        # 10 -> 01  invalid
    jmp("update")        # 10 -> 10
    jmp("increment")     # 10 -> 11

    jmp("update")        # 11 -> 00  invalid
    jmp("increment")     # 11 -> 01
    label("decrement")   # 11 -> 10  (doubles as the decrement handler)
    jmp(y_dec, "update")     # y holds the count; jmp y-- decrements it
    label("update")      # 11 -> 11

    # --- main loop ----------------------------------------------------------
    wrap_target()
    set(x, 0)
    pull(noblock)            # did Python request the count? (put() anything)
    mov(x, osr)              # x = request flag (0 if TX FIFO was empty)
    mov(osr, isr)            # stash previous pin state in OSR
    jmp(not_x, "sample_pins")
    mov(isr, y)              # requested: hand the count (y) to Python
    push()
    label("sample_pins")
    mov(isr, null)
    in_(osr, 2)              # shift in previous pin state (2 bits)
    in_(pins, 2)             # shift in current pin state (2 bits)
    mov(pc, isr)             # jump into the table at that 4-bit index
    label("increment")
    mov(x, invert(y))        # y+1 done as ~(~y - 1): PIO can only decrement
    jmp(x_dec, "increment2")
    label("increment2")
    mov(y, invert(x))
    wrap()
    nop()
    nop()
    nop()


class QuadratureEncoder:
    """One encoder on two consecutive pins (A = base_pin, B = base_pin + 1)."""

    _next_sm = 0  # state machine IDs 0..3 handed out in order

    def __init__(self, base_pin):
        Pin(base_pin, Pin.IN, Pin.PULL_UP)
        Pin(base_pin + 1, Pin.IN, Pin.PULL_UP)
        self.sm = rp2.StateMachine(
            QuadratureEncoder._next_sm,
            _quadrature_counter,
            freq=125_000_000,
            in_base=Pin(base_pin),
        )
        QuadratureEncoder._next_sm += 1
        self.sm.active(1)

    def read(self):
        """Current signed count. Forward = one sign, backward = the other
        (which is which depends on wiring — establish it in the hand-spin
        test and flip ENCODER_DIR in main.py if needed)."""
        self.sm.put(1)               # request
        raw = self.sm.get()          # reply
        if raw & 0x8000_0000:        # sign-extend 32-bit two's complement
            raw -= 0x1_0000_0000
        return raw
