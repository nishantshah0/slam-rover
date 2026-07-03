# SLAM Rover — Phase 1 firmware (Raspberry Pi Pico W, MicroPython)
#
# What this does, in one breath: listens for motor commands over USB serial
# AND WiFi (UDP), drives two motors through the MDD3A, streams encoder counts
# back 20 times a second, and — most importantly — STOPS THE MOTORS if no
# command has arrived for 400 ms (the watchdog, risk R4).
#
# Command protocol (both transports, plain text lines):
#   in :  "M <left> <right>"   speeds -100..100      e.g.  M 60 60
#   out:  "E <left_count> <right_count>"             every 50 ms
#
# Concepts explained in pico/README.md. Wiring in docs/phase1-guide.md pin map.

import sys
import time
import select
from machine import Pin, PWM

# ------------------------------- CONFIG -------------------------------------
PIN_LEFT_FWD, PIN_LEFT_REV = 2, 3      # MDD3A M1A, M1B
PIN_RIGHT_FWD, PIN_RIGHT_REV = 4, 5    # MDD3A M2A, M2B
PIN_ENC_LEFT = 6                       # left encoder A=GP6, B=GP7
PIN_ENC_RIGHT = 8                      # right encoder A=GP8, B=GP9

DUTY_CAP = 0.85          # 7.2 V pack into 6 V motors -> never exceed 85% duty
PWM_FREQ = 20_000        # 20 kHz: above human hearing, motors don't whine
WATCHDOG_MS = 400        # silence longer than this => motors stop
TELEMETRY_MS = 50        # encoder report interval (20 Hz)

WIFI_SSID = ""           # "" = skip WiFi (USB-only). Wokwi sim: "Wokwi-GUEST"
WIFI_PASSWORD = ""       # Wokwi-GUEST has no password
UDP_PORT = 8888

ENCODER_DIR = (1, 1)     # flip to -1 per side if counts run backward (Step 3)

# ------------------------------- MOTORS -------------------------------------
# The MDD3A speaks "sign-magnitude": PWM on the A pin drives forward, PWM on
# the B pin drives reverse, both idle = coast/stop. So each motor is just two
# PWM outputs and a rule about which one gets the duty cycle.

class Motor:
    def __init__(self, pin_fwd, pin_rev):
        self.fwd = PWM(Pin(pin_fwd)); self.fwd.freq(PWM_FREQ)
        self.rev = PWM(Pin(pin_rev)); self.rev.freq(PWM_FREQ)
        self.set(0)

    def set(self, speed):  # speed: -100 .. +100
        speed = max(-100, min(100, speed))
        duty = int(abs(speed) / 100 * DUTY_CAP * 65535)
        if speed >= 0:
            self.rev.duty_u16(0)
            self.fwd.duty_u16(duty)
        else:
            self.fwd.duty_u16(0)
            self.rev.duty_u16(duty)


left_motor = Motor(PIN_LEFT_FWD, PIN_LEFT_REV)
right_motor = Motor(PIN_RIGHT_FWD, PIN_RIGHT_REV)

def stop_all():
    left_motor.set(0)
    right_motor.set(0)

# ------------------------------ ENCODERS ------------------------------------
# Wrapped in try/except so the firmware still runs on simulators that lack
# PIO support — encoders then read 0 and everything else works.
try:
    from encoder import QuadratureEncoder
    enc_left = QuadratureEncoder(PIN_ENC_LEFT)
    enc_right = QuadratureEncoder(PIN_ENC_RIGHT)
    def read_encoders():
        return (ENCODER_DIR[0] * enc_left.read(),
                ENCODER_DIR[1] * enc_right.read())
except Exception as e:
    print("# encoder init failed (ok in simulation):", e)
    def read_encoders():
        return (0, 0)

# ------------------------------- WIFI / UDP ---------------------------------
udp_sock = None
udp_client = None  # whoever talked to us last gets the telemetry

if WIFI_SSID:
    try:
        import network, socket
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), 15_000)
        while not wlan.isconnected() and time.ticks_diff(deadline, time.ticks_ms()) > 0:
            time.sleep_ms(200)
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print("# WiFi up:", ip, "UDP port", UDP_PORT)
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.bind(("0.0.0.0", UDP_PORT))
            udp_sock.setblocking(False)
        else:
            print("# WiFi connect timed out - USB serial only")
    except Exception as e:
        print("# WiFi failed:", e, "- USB serial only")

# ------------------------------ COMMAND INPUT -------------------------------
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
serial_buf = ""

def poll_serial_line():
    """Non-blocking: returns one complete line from USB serial, or None."""
    global serial_buf
    while poller.poll(0):
        ch = sys.stdin.read(1)
        if ch in ("\n", "\r"):
            line, serial_buf = serial_buf, ""
            if line:
                return line
        else:
            serial_buf += ch
    return None

def poll_udp_line():
    """Non-blocking: returns one command line from WiFi, or None."""
    global udp_client
    if udp_sock is None:
        return None
    try:
        data, addr = udp_sock.recvfrom(64)
        udp_client = addr
        return data.decode().strip()
    except OSError:      # nothing waiting
        return None

def handle_command(line):
    """Parse 'M <left> <right>'. Returns True if it was a valid command."""
    parts = line.split()
    if len(parts) == 3 and parts[0] == "M":
        try:
            left_motor.set(int(parts[1]))
            right_motor.set(int(parts[2]))
            return True
        except ValueError:
            pass
    return False

# ------------------------------- MAIN LOOP ----------------------------------
led = Pin("LED", Pin.OUT)
last_cmd_ms = time.ticks_ms() - WATCHDOG_MS   # start "expired": motors off
last_telemetry_ms = time.ticks_ms()
watchdog_tripped = True
stop_all()
print("# rover firmware ready")

while True:
    now = time.ticks_ms()

    for line in (poll_serial_line(), poll_udp_line()):
        if line and handle_command(line):
            last_cmd_ms = now
            watchdog_tripped = False

    # THE WATCHDOG: commands stopped arriving -> stop moving. This is what
    # makes a dropped WiFi link or a crashed PC script safe.
    if not watchdog_tripped and time.ticks_diff(now, last_cmd_ms) > WATCHDOG_MS:
        stop_all()
        watchdog_tripped = True
        print("# watchdog: no command for %dms - motors stopped" % WATCHDOG_MS)

    if time.ticks_diff(now, last_telemetry_ms) >= TELEMETRY_MS:
        last_telemetry_ms = now
        l, r = read_encoders()
        msg = "E %d %d" % (l, r)
        print(msg)
        if udp_sock is not None and udp_client is not None:
            try:
                udp_sock.sendto(msg.encode(), udp_client)
            except OSError:
                pass

    # LED tells you the rover's state at a glance:
    # solid = driving on fresh commands, slow blink = idle/watchdog-stopped
    led.value(1 if not watchdog_tripped else (now // 500) % 2)

    time.sleep_ms(5)
