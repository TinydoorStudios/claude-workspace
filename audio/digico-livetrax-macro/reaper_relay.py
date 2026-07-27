#!/usr/bin/env python3
"""
DiGiCo Q225 → REAPER relay for Jazz At The Memo
-----------------------------------------------
Listens on UDP 9000 for triggers from Companion.
  /record  → pull channel names 1-32 from console, rename REAPER tracks,
              wait RECORD_DELAY seconds, start recording
  /prep    → pull channel names 1-32 from console, rename REAPER tracks.
              No record. For staging tracks ahead of a show.
  /stop    → stop REAPER

Console:       192.168.200.224 : 1024
Name replies:  listen on UDP 3819
REAPER OSC:    127.0.0.1 : 8000
"""

import socket
import struct
import time
import threading

# ── Config ──────────────────────────────────────────────────────────────────
CONSOLE_IP    = "192.168.200.224"
CONSOLE_PORT  = 1024
TRIGGER_PORT  = 9001        # Companion sends here
NAMES_PORT    = 3819        # console sends name replies here
REAPER_IP     = "127.0.0.1"
REAPER_PORT   = 8000        # REAPER OSC receive port
MAX_CHANNELS  = 32          # only rename tracks 1–32
RECORD_DELAY  = 5.0         # seconds between arm and record

# ── OSC encode/decode ────────────────────────────────────────────────────────

def _pad4(n):
    return (n + 3) & ~3

def _enc_str(s):
    b = s.encode("utf-8") + b"\x00"
    return b.ljust(_pad4(len(b)), b"\x00")

def encode_osc(path, *args):
    data = _enc_str(path)
    if not args:
        data += _enc_str(",")
        return data
    types = ","
    arg_bytes = b""
    for a in args:
        if isinstance(a, int):
            types += "i"
            arg_bytes += struct.pack(">i", a)
        elif isinstance(a, str):
            types += "s"
            arg_bytes += _enc_str(a)
        elif isinstance(a, float):
            types += "f"
            arg_bytes += struct.pack(">f", a)
    data += _enc_str(types)
    data += arg_bytes
    return data

def decode_osc(data):
    """Return (path, args) or (None, []) on error."""
    try:
        end = data.index(b"\x00")
        path = data[:end].decode("utf-8")
        pos = _pad4(end + 1)

        if pos >= len(data):
            return path, []   # no type tag — path-only message

        end2 = data.index(b"\x00", pos)
        tags = data[pos:end2].decode("utf-8")
        pos = _pad4(end2 + 1)

        if not tags.startswith(","):
            return path, []

        args = []
        for t in tags[1:]:
            if t == "i":
                args.append(struct.unpack(">i", data[pos:pos+4])[0])
                pos += 4
            elif t == "f":
                args.append(struct.unpack(">f", data[pos:pos+4])[0])
                pos += 4
            elif t == "s":
                end3 = data.index(b"\x00", pos)
                args.append(data[pos:end3].decode("utf-8"))
                pos = _pad4(end3 + 1)
        return path, args
    except Exception:
        return None, []

def osc_send(ip, port, path, *args):
    msg = encode_osc(path, *args)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(msg, (ip, port))
    s.close()

# ── Name pull ────────────────────────────────────────────────────────────────

def pull_names():
    """Send /request_names to console, collect /strip/name/N replies for 1-32."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", NAMES_PORT))
    except OSError as e:
        print(f"  ERROR: cannot bind port {NAMES_PORT}: {e}")
        return {}

    sock.settimeout(0.1)   # short per-packet timeout so we can check the deadline
    osc_send(CONSOLE_IP, CONSOLE_PORT, "/request_names", 1)

    names = {}
    deadline = time.monotonic() + 6.0
    got_end = False
    last_pkt = time.monotonic()

    try:
        while time.monotonic() < deadline and not got_end:
            try:
                data, _ = sock.recvfrom(4096)
                last_pkt = time.monotonic()
            except socket.timeout:
                # quiet for 0.75s after the last packet — console is done
                if names and (time.monotonic() - last_pkt) > 0.75:
                    break
                continue

            path, args = decode_osc(data)
            if path and path.startswith("/strip/name/"):
                try:
                    ch   = int(path.rsplit("/", 1)[-1])
                    name = args[0] if args else ""
                    flag = args[1] if len(args) > 1 else 0
                    if 1 <= ch <= MAX_CHANNELS and name:
                        names[ch] = name
                    # NOTE (2026-07-19): args[1] is NOT an end-of-list marker.
                    # Packet capture off the Q225 shows it varies per channel
                    # (CH10 Overhead = 2, CH11 = 3, most = 1). Treating 2 as
                    # end-of-list truncated every pull at the first channel
                    # that happened to carry it. Do not reinstate.
                except (ValueError, IndexError):
                    pass
    finally:
        sock.close()

    return names

# ── REAPER control ───────────────────────────────────────────────────────────

def rename_reaper_tracks(names):
    """Send /track/N/name to REAPER for channels 1-32."""
    for ch in sorted(names):
        osc_send(REAPER_IP, REAPER_PORT, f"/track/{ch}/name", names[ch])
        time.sleep(0.02)

# ── Record chain (runs in a thread) ──────────────────────────────────────────

_chain_lock = threading.Lock()

def record_chain():
    if not _chain_lock.acquire(blocking=False):
        print("Record chain already in progress — ignoring trigger")
        return
    try:
        print("── Record chain start ──────────────────")
        print("  Pulling names from console...")
        names = pull_names()
        print(f"  Received {len(names)} names for channels 1–{MAX_CHANNELS}")
        for ch in sorted(names):
            print(f"    CH {ch:2d}: {names[ch]}")

        if names:
            rename_reaper_tracks(names)
            print("  Track names sent to REAPER")
        else:
            print("  WARNING: no names received — tracks not renamed")

        print(f"  Waiting {RECORD_DELAY:.0f}s before record...")
        time.sleep(RECORD_DELAY)

        osc_send(REAPER_IP, REAPER_PORT, "/record")
        print("  /record sent to REAPER")
        print("────────────────────────────────────────")
    finally:
        _chain_lock.release()

def prep_chain():
    """Name pull + REAPER track rename only — no record."""
    if not _chain_lock.acquire(blocking=False):
        print("Chain already in progress — ignoring trigger")
        return
    try:
        print("── Prep (name pull only) ───────────────")
        print("  Pulling names from console...")
        names = pull_names()
        print(f"  Received {len(names)} names for channels 1–{MAX_CHANNELS}")
        for ch in sorted(names):
            print(f"    CH {ch:2d}: {names[ch]}")

        if names:
            rename_reaper_tracks(names)
            print("  Track names sent to REAPER")
        else:
            print("  WARNING: no names received — tracks not renamed")
        print("────────────────────────────────────────")
    finally:
        _chain_lock.release()

# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", TRIGGER_PORT))
    print(f"DiGiCo→REAPER relay running")
    print(f"  Trigger:  UDP {TRIGGER_PORT} (/record, /prep, /stop)")
    print(f"  Console:  {CONSOLE_IP}:{CONSOLE_PORT}")
    print(f"  Names:    UDP {NAMES_PORT}")
    print(f"  REAPER:   {REAPER_IP}:{REAPER_PORT}")
    print()

    while True:
        data, addr = sock.recvfrom(1024)
        path, _ = decode_osc(data)
        if path == "/record":
            print(f"RECORD trigger from {addr}")
            threading.Thread(target=record_chain, daemon=True).start()
        elif path == "/prep":
            print(f"PREP trigger from {addr}")
            threading.Thread(target=prep_chain, daemon=True).start()
        elif path == "/stop":
            print(f"STOP trigger from {addr}")
            osc_send(REAPER_IP, REAPER_PORT, "/stop")

if __name__ == "__main__":
    main()
