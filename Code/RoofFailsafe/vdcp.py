#!/usr/bin/env python3
"""
vdcp.py — minimal VDCP (Louth) controller for the Daktronics DMP-8000.

Purpose: tell the DMP-8000 "D8Roof-P" to play a piece of content by its
VDCP ID, over a TCP or UDP socket, WITHOUT the Show Control PC being alive.
This is the roof-display failsafe: the DMP is a standalone box on the LAN;
we speak the same VDCP an automation controller / switcher would.

Protocol reference (verified against the Imagine/Louth VDCP Protocol Guide,
rev 20):

  Frame:   STX  BC  CMD1  CMD2  [DATA...]  CHECKSUM
    STX      = 0x02
    BC       = number of bytes between BC and checksum = len(CMD1,CMD2,DATA)
    CMD1     = (type nibble << 4) | unit-address nibble   (unit addr = 0)
    CMD2     = command code
    CHECKSUM = 2's complement of the LSB of sum(CMD1 .. last DATA byte)
               i.e. (-sum(body)) & 0xFF     (STX and BC are NOT summed)

  Commands used here:
    SELECT PORT   CMD1=0x20 CMD2=0x22  DATA=[signal_port]      (BC=03)
    OPEN PORT     CMD1=0x30 CMD2=0x01  DATA=[signal_port, n]   (BC=04)
    PLAY CUE      CMD1=0x20 CMD2=0x24  DATA=<8-char ID>        (BC=0A)   (a.k.a "Cue")
    CUE (varID)   CMD1=0xA0 CMD2=0x24  DATA=[len]<ID chars>
    PLAY          CMD1=0x10 CMD2=0x01                          (BC=02)
    STOP          CMD1=0x10 CMD2=0x00                          (BC=02)

  Server replies to system/immediate/preset commands with ACK (0x04) or
  NAK (0x05). OPEN PORT replies with 0x30 0x81 (grant/denied).

Self-test:  python3 vdcp.py --selftest
Fire:       python3 vdcp.py --host 192.168.200.121 --port 5250 \
                   --signal-port 1 --id 1 [--udp] [--open-first]
"""

from __future__ import annotations
import argparse
import socket
import sys
import time

STX = 0x02
ACK = 0x04
NAK = 0x05


def _checksum(body: bytes) -> int:
    """2's complement of the LSB of the sum of the body (CMD1..last data)."""
    return (-sum(body)) & 0xFF


def frame(cmd1: int, cmd2: int, data: bytes = b"") -> bytes:
    """Build a complete VDCP frame."""
    body = bytes([cmd1, cmd2]) + data
    bc = len(body)
    if bc > 0xFF:
        raise ValueError("VDCP body too long")
    return bytes([STX, bc]) + body + bytes([_checksum(body)])


def _pad_id_fixed8(clip_id: str) -> bytes:
    """Fixed 8-char ID, ASCII, space-padded (0x20) to exactly 8 bytes."""
    raw = clip_id.encode("ascii", "strict")[:8]
    return raw.ljust(8, b" ")


def _pad_id_variable(clip_id: str) -> bytes:
    """Variable-length ID: single length byte followed by the visible chars."""
    raw = clip_id.encode("ascii", "strict")
    return bytes([len(raw)]) + raw


# --- individual command frames -------------------------------------------------

def f_select_port(signal_port: int) -> bytes:
    return frame(0x20, 0x22, bytes([signal_port & 0xFF]))


def f_open_port(signal_port: int, count: int = 1) -> bytes:
    return frame(0x30, 0x01, bytes([signal_port & 0xFF, count & 0xFF]))


def f_cue(clip_id: str, id_mode: str = "fixed8") -> bytes:
    if id_mode == "variable":
        return frame(0xA0, 0x24, _pad_id_variable(clip_id))
    return frame(0x20, 0x24, _pad_id_fixed8(clip_id))


def f_play() -> bytes:
    return frame(0x10, 0x01)


def f_stop() -> bytes:
    return frame(0x10, 0x00)


# --- transport -----------------------------------------------------------------

def _hex(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)


def send_sequence(
    host: str,
    port: int,
    frames: list[bytes],
    udp: bool = False,
    read_ack: bool = True,
    timeout: float = 3.0,
    gap: float = 0.10,
    log=print,
) -> bool:
    """
    Send a list of VDCP frames in order. On TCP, optionally read the ACK/NAK
    after each. Returns True if nothing NAK'd / errored.
    """
    ok = True
    if udp:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        try:
            for fr in frames:
                log(f"  TX {_hex(fr)}")
                s.sendto(fr, (host, port))
                time.sleep(gap)
        finally:
            s.close()
        return ok

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        for fr in frames:
            log(f"  TX {_hex(fr)}")
            s.sendall(fr)
            if read_ack:
                try:
                    resp = s.recv(64)
                    log(f"  RX {_hex(resp) if resp else '(none)'}")
                    if resp and resp[0] == NAK:
                        ok = False
                        log("  !! NAK")
                except socket.timeout:
                    log("  RX (timeout, no reply)")
            time.sleep(gap)
    except OSError as e:
        log(f"  !! socket error: {e}")
        return False
    finally:
        s.close()
    return ok


def fire_clip(
    host: str,
    port: int,
    clip_id: str,
    signal_port: int = 1,
    udp: bool = False,
    open_first: bool = False,
    id_mode: str = "fixed8",
    read_ack: bool = True,
    log=print,
) -> bool:
    """
    Full 'put this content on the display now' sequence:
      [OPEN PORT] -> SELECT PORT -> CUE(id) -> PLAY
    """
    seq: list[bytes] = []
    if open_first:
        seq.append(f_open_port(signal_port))
    seq.append(f_select_port(signal_port))
    seq.append(f_cue(clip_id, id_mode))
    seq.append(f_play())
    log(f"Firing clip {clip_id!r} on {host}:{port} "
        f"(signal port {signal_port}, {'UDP' if udp else 'TCP'}, id_mode={id_mode})")
    return send_sequence(host, port, seq, udp=udp, read_ack=read_ack, log=log)


# --- self-test -----------------------------------------------------------------

def _selftest() -> int:
    checks = [
        ("PLAY",              f_play(),               "02 02 10 01 EF"),
        ("STOP",              f_stop(),               "02 02 10 00 F0"),
        ("SELECT PORT 1",     f_select_port(1),       "02 03 20 22 01 BD"),
        ("CUE id='1' fixed8", f_cue("1", "fixed8"),   "02 0A 20 24 31 20 20 20 20 20 20 20 AB"),
    ]
    rc = 0
    for name, got, want in checks:
        got_s = _hex(got)
        status = "ok " if got_s == want else "BAD"
        if got_s != want:
            rc = 1
        print(f"[{status}] {name:20s} {got_s}"
              + ("" if got_s == want else f"   expected {want}"))
    # Re-derive the two documented example checksums independently.
    assert _checksum(bytes([0x10, 0x01])) == 0xEF
    assert _checksum(bytes([0x10, 0x00])) == 0xF0
    print("selftest:", "PASS" if rc == 0 else "FAIL")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="VDCP controller for Daktronics DMP-8000")
    ap.add_argument("--selftest", action="store_true", help="verify frame builder and exit")
    ap.add_argument("--host", default="192.168.200.121")
    ap.add_argument("--port", type=int, help="VDCP socket port on the DMP (from DMP config)")
    ap.add_argument("--id", help="content ID (from the DMP command sign)")
    ap.add_argument("--signal-port", type=int, default=1, help="VDCP signal/output port number")
    ap.add_argument("--udp", action="store_true", help="use UDP instead of TCP")
    ap.add_argument("--open-first", action="store_true", help="send OPEN PORT before SELECT PORT")
    ap.add_argument("--id-mode", choices=["fixed8", "variable"], default="fixed8")
    ap.add_argument("--no-ack", action="store_true", help="do not wait for ACK/NAK (TCP)")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    if not args.port or not args.id:
        ap.error("--port and --id are required to fire (or use --selftest)")

    ok = fire_clip(
        host=args.host, port=args.port, clip_id=args.id,
        signal_port=args.signal_port, udp=args.udp, open_first=args.open_first,
        id_mode=args.id_mode, read_ack=not args.no_ack,
    )
    print("RESULT:", "OK" if ok else "FAILED / NAK")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
