#!/usr/bin/env python3
"""Tag-aware .ses diff for the Mustard blocks.

Record layout: tag(u16 LE) + bidx(u16 LE) + value(f32 LE)

Anchors on each differing BYTE and looks backwards for a plausible record start
whose value field covers that byte. A greedy forward scan misaligns and silently
skips records (that's how 0x1D0B/type was missed once) — don't go back to it.

Usage: tagdiff.py mc11 mc12 [--all]
"""
import struct, sys

P = '/Users/brianlloyd/.wine/drive_c/Projects/'
a = open(P + sys.argv[1] + '.ses', 'rb').read()
b = open(P + sys.argv[2] + '.ses', 'rb').read()
show_all = '--all' in sys.argv
if len(a) != len(b):
    print("SIZE DIFFERS", len(a), len(b)); sys.exit(1)

UI_LO, UI_HI = 0x2600000, 0x2620000       # UI/layout state — never audio


def is_ts_byte(i):
    """Byte i sits inside a session-timestamp double (~46000-46500)."""
    for st in range(max(0, i - 7), i + 1):
        try:
            va = struct.unpack('<d', a[st:st + 8])[0]
            vb = struct.unpack('<d', b[st:st + 8])[0]
            if 46000 < va < 46500 and 46000 < vb < 46500 and i < st + 8:
                return True
        except Exception:
            pass
    return False


def record_at(i):
    """Find a record start j in [i-7, i] whose f32 value field covers byte i."""
    for j in range(i - 7, i + 1):
        if j < 0:
            continue
        tag = struct.unpack('<H', a[j:j + 2])[0]
        tag_b = struct.unpack('<H', b[j:j + 2])[0]
        if tag != tag_b:
            continue
        # Mustard Dynamics 1 = 0x1Dxx, Mustard Dynamics 2 (gate) = 0x1Exx
        if not (0x1D00 <= tag <= 0x1EFF):
            continue
        bidx = struct.unpack('<H', a[j + 2:j + 4])[0]
        if bidx != struct.unpack('<H', b[j + 2:j + 4])[0] or bidx > 15:
            continue
        if not (j + 4 <= i < j + 8):
            continue
        va = struct.unpack('<f', a[j + 4:j + 8])[0]
        vb = struct.unpack('<f', b[j + 4:j + 8])[0]
        if va != vb:
            return (j, tag, bidx, va, vb)
    return None


diffs = [i for i in range(len(a)) if a[i] != b[i]]
seen, unexplained = {}, []
for i in diffs:
    if UI_LO <= i < UI_HI or is_ts_byte(i):
        continue
    r = record_at(i)
    if r:
        seen[r[0]] = r
    else:
        unexplained.append(i)

BLK = {0x1D: 'D1/comp', 0x1E: 'D2/gate'}
for off in sorted(seen):
    _, tag, bidx, va, vb = seen[off]
    print(f"  0x{off:X}  tag=0x{tag:04X} b{bidx}  {va:<14.6g} -> {vb:<14.6g} {BLK.get(tag >> 8, '')}")

if unexplained:
    runs = []
    for i in unexplained:
        if runs and i - runs[-1][1] <= 8:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    print(f"\n  !! {len(runs)} run(s) NOT explained by a tag record:")
    for s, e in runs:
        if not show_all and e - s > 32:
            print(f"     0x{s:X} ({e-s+1}B) [large run, use --all]")
            continue
        print(f"     0x{s:X} ({e-s+1}B)")
        print(f"        a: {a[max(0,s-16):e+17].hex()}")
        print(f"        b: {b[max(0,s-16):e+17].hex()}")
