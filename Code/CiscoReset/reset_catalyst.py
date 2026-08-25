#!/usr/bin/env python3
"""Catcher v5 — one keystroke each, no spamming.

Why v1-v4 all failed: the bootloader buffers console input. Sending a stream of
ESC meant the 1st ESC aborted autoboot and drew the Startup Menu, and the 2nd
buffered ESC was immediately read as "exit". Rate made no difference; the
second keystroke always undid the first.

v5 sends single characters on the timeline measured across three boots
(T = moment the USB gadget console re-enumerates):
    T+3s  BOOTP starts
    T+5s  autoboot prompt, menu draws
  ESC  @ T+4.0  — buffered, aborts autoboot, nothing follows it to exit
  '2'  @ T+6.5  — Restore Factory Defaults
  'Y'  @ T+8.5  — answers a confirmation if one is asked

Raw console bytes stream to reset1300.raw.
"""
import os, sys, time, glob, subprocess, select

BASE = os.path.dirname(os.path.abspath(__file__))
LOG, RAW = BASE + "/reset_catalyst.log", BASE + "/reset_catalyst.raw"
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 900.0

# (delay from T, bytes, label) — each fires exactly once per boot
SEQ = [
    (4.0, b"\x1b", "ESC (abort autoboot)"),
    (6.5, b"2",    "'2' Restore Factory Defaults"),
    (8.5, b"Y\r",  "'Y' confirm"),
]

log = open(LOG, "w", buffering=1)
raw = open(RAW, "wb", buffering=0)
def w(m): log.write("%s  %s\n" % (time.strftime("%H:%M:%S"), m))

w("=== catcher v5 armed — idle until the console drops ===")

end = time.time() + DUR
fd = None; cur = None; T = None
fired = set()
seen_cycle = False

def find_port():
    p = sorted(glob.glob("/dev/cu.usbmodem*"))
    return p[0] if p else None

while time.time() < end:
    port = find_port()

    if port is None:
        if fd is not None:
            try: os.close(fd)
            except OSError: pass
            fd = None; cur = None; T = None
            fired.clear(); seen_cycle = True
            w("*** console DISAPPEARED — powered down ***")
        time.sleep(0.05); continue

    if fd is None or port != cur:
        try:
            subprocess.run(["stty", "-f", port, "115200", "cs8", "-cstopb",
                            "-parenb", "raw", "-echo"], check=False,
                           capture_output=True, timeout=3)
            fd = os.open(port, os.O_RDWR | os.O_NONBLOCK | os.O_NOCTTY)
            cur = port; T = time.time(); fired.clear()
            w("*** console APPEARED — %s ***" %
              ("T0 set, sequence armed" if seen_cycle else "switch already up, idle"))
        except (OSError, subprocess.SubprocessError):
            fd = None; time.sleep(0.1); continue

    if seen_cycle:
        dt = time.time() - T
        for i, (mark, payload, label) in enumerate(SEQ):
            if i not in fired and dt >= mark:
                try:
                    os.write(fd, payload)
                    w(">>> T+%.1fs  %s" % (dt, label))
                except OSError:
                    pass
                fired.add(i)

    try:
        r, _, _ = select.select([fd], [], [], 0.02)
    except (OSError, ValueError):
        fd = None; continue

    if r:
        try: chunk = os.read(fd, 65536)
        except (BlockingIOError, OSError): chunk = b""
        if chunk:
            raw.write(chunk)

w("=== done ===")
log.close(); raw.close()
