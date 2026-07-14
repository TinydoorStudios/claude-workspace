#!/usr/bin/env python3
"""
LiveTrax name-pull relay. Runs ON the LiveTrax Mac (192.168.200.166) so the
/request_names trigger leaves from the registered LTrax device's IP -- the
console only honors the request from that IP. Companion (or anything) pokes
this relay on UDP 9000; the relay fires the exact /request_names byte string
at the console, which then pushes 72 /strip/name packets to LiveTrax:3819.

Listen:  UDP 0.0.0.0:9000  (any payload triggers a pull)
Fire:    /request_names ,i 1  -> 192.168.200.224:1024

Run:   python3 livetrax_relay.py
"""
import socket
import subprocess
import sys

LISTEN = ("0.0.0.0", 9000)
CONSOLE = ("192.168.200.224", 1024)

# The send is run as a FRESH subprocess per poke. An in-process long-lived
# socket would not trigger the console (proven in testing); a short-lived
# standalone process does. So we spawn one each time.
SEND_CODE = (
    "import socket;"
    "s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);"
    "s.sendto(bytes.fromhex('2f726571756573745f6e616d657300002c69000000000001'),"
    "('192.168.200.224',1024))"
)

srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
srv.bind(LISTEN)
print(f"relay up: listening {LISTEN[0]}:{LISTEN[1]} -> fires /request_names to {CONSOLE[0]}:{CONSOLE[1]}")

while True:
    data, addr = srv.recvfrom(2048)
    subprocess.run([sys.executable, "-c", SEND_CODE])
    print(f"poke from {addr[0]}:{addr[1]} -> spawned fresh /request_names send")
