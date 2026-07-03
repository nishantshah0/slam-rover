"""SLAM Rover — Phase 1 teleop. Hold WASD to drive, release to stop.

Two ways to connect (matching the firmware's two transports):

    python teleop_wasd.py --udp 192.168.1.42        # WiFi (rover prints its IP at boot)
    python teleop_wasd.py --serial COM5             # USB cable (find port in Device Manager)

Keys: W/S forward/back, A/D turn, SPACE instant stop, +/- speed, ESC quit.

Needs: pip install pygame        (and: pip install pyserial   for --serial)

SAFETY DESIGN NOTE: this script sends a command 10× per second even when
nothing changed. That's not waste — it's the firmware watchdog's heartbeat.
Close this window, unplug the cable, or walk out of WiFi range, and the
rover stops itself within 400 ms because the heartbeat vanished.
"""

import argparse
import sys

SEND_HZ = 10
DEFAULT_SPEED = 50   # % — start gentle; raise with '+' once trusted


def make_sender(args):
    if args.udp:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dest = (args.udp, args.port)
        print(f"UDP -> {dest[0]}:{dest[1]}")
        return lambda line: sock.sendto(line.encode(), dest)
    else:
        import serial  # pyserial
        ser = serial.Serial(args.serial, 115200, timeout=0)
        print(f"Serial -> {args.serial}")
        return lambda line: ser.write((line + "\n").encode())


def main():
    ap = argparse.ArgumentParser(description="WASD teleop for the rover")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--udp", metavar="ROVER_IP", help="drive over WiFi")
    group.add_argument("--serial", metavar="COM_PORT", help="drive over USB")
    ap.add_argument("--port", type=int, default=8888, help="UDP port (default 8888)")
    args = ap.parse_args()

    send = make_sender(args)

    import pygame
    pygame.init()
    screen = pygame.display.set_mode((420, 160))
    pygame.display.set_caption("Rover teleop - WASD drives, SPACE stops, ESC quits")
    font = pygame.font.SysFont("consolas", 18)
    clock = pygame.time.Clock()

    speed = DEFAULT_SPEED
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    speed = min(100, speed + 10)
                elif event.key == pygame.K_MINUS:
                    speed = max(10, speed - 10)

        keys = pygame.key.get_pressed()
        drive = (keys[pygame.K_w] - keys[pygame.K_s]) * speed
        turn = (keys[pygame.K_d] - keys[pygame.K_a]) * speed
        if keys[pygame.K_SPACE]:
            drive = turn = 0

        # differential-drive mixing: turning = wheels at different speeds
        left = max(-100, min(100, drive + turn))
        right = max(-100, min(100, drive - turn))
        send(f"M {left} {right}")

        screen.fill((20, 20, 30))
        for i, text in enumerate([
            f"speed {speed}%   (+/- to change)",
            f"sending: M {left} {right}",
            "release keys = stop | close window = watchdog stops rover",
        ]):
            screen.blit(font.render(text, True, (200, 220, 200)), (12, 12 + 26 * i))
        pygame.display.flip()

        clock.tick(SEND_HZ)  # the 10 Hz heartbeat

    send("M 0 0")
    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
