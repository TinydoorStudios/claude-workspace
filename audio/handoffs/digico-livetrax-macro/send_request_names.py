#!/usr/bin/env python3
"""
Fire the exact /request_names message at the Q225, byte-for-byte the same as
LiveTrax's own "Create session from console" button (confirmed against
reference-capture_request-names-exchange.pcapng).

Run on the LiveTrax Mac (or any box on the 192.168.200.x LAN). The console
answers with 72 /strip/name/N packets aimed at whatever is registered as the
LTrax device (192.168.200.166:3819) -- NOT reply-to-sender -- so this sender
just needs to land the trigger on the console's port 1024.

DECISIVE TEST: run this with LiveTrax open and WATCH it. If a session
populates / track names appear, the Companion relay plan works with no
template. If nothing happens in LiveTrax, then LiveTrax only builds a session
from its own button press and an external trigger can't create one.

Usage:
    python3 send_request_names.py            # default console IP/port
    python3 send_request_names.py 192.168.200.224 1024
"""
import socket
import sys

CONSOLE_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.200.224"
CONSOLE_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1024

# /request_names ,i 1  -- exact bytes from the canonical capture
PAYLOAD = bytes.fromhex("2f726571756573745f6e616d657300002c69000000000001")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(PAYLOAD, (CONSOLE_IP, CONSOLE_PORT))
s.close()

print(f"sent /request_names ,i 1  ({len(PAYLOAD)} bytes) -> {CONSOLE_IP}:{CONSOLE_PORT}")
print("watch LiveTrax now -- did names/session populate?")
