#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — Seals and Crofts 2 (2026-05-27)
Source: Seals and Crofts 2 - FOH Channel Processing.md

Run:
  python3 apply_seals.py \
      --src  "/Users/brianlloyd/Documents/Claude/audio/Memorial Hall/brian memo v2.ses" \
      --dest "/Users/brianlloyd/Documents/Claude/audio/Memorial Hall/2026-05-27 Seals and Crofts 2/Seals_and_Crofts_2.ses"

All 26 channels patched. Ch 25 (Brian Vox) and Ch 26 (John Vox) require
NAME_SEARCH_END extended to * 48 — included above.
"""

import argparse
import os
import struct
import sys


# ── layout constants ──────────────────────────────────────────────────────────

DISP_NAME_BASE   = 0x0a2a5a
DISP_NAME_STRIDE = 125

STRIP1_HDR = 0x0b0327
STRIP_SIZE = 5638
HPF_REL    = 406

NAME_SEARCH_START = DISP_NAME_BASE
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 48


# ── EQ / DEQ / filter tags (verified safe to write) ──────────────────────────

TAG_EQ_ENABLE  = 0x0404
TAG_EQ_GAIN    = 0x0403
TAG_EQ_FREQ    = 0x0406
TAG_EQ_Q       = 0x0407
TAG_EQ_TYPE    = 0x040b
TAG_DEQ_ENABLE = 0x040e
TAG_DEQ_THRESH = 0x0411
TAG_DEQ_ATK    = 0x0412
TAG_DEQ_REL    = 0x0410
TAG_LPF_FREQ   = 0x0703


# ── DO-NOT-WRITE tags ─────────────────────────────────────────────────────────

DO_NOT_WRITE_TAGS = (
    0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    0x0503, 0x050e, 0x0511, 0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47,
)


# ── EQ shorthand ──────────────────────────────────────────────────────────────

SHELF   = 1.0
BELL    = 2.0
ON      = 1.0
OFF     = 0.0
OFF_LPF = 25000.0


# ── low-level helpers ─────────────────────────────────────────────────────────

def strip_region(strip_num):
    start = STRIP1_HDR + (strip_num - 1) * STRIP_SIZE
    return start, STRIP_SIZE


def find_tag(data, start, size, tag, bidx):
    sig = struct.pack('<HH', tag, bidx)
    for i in range(start, start + size - 7):
        if data[i + 4:i + 8] == sig:
            return i
    return None


def write_tag(data, strip_num, tag, bidx, value):
    start, size = strip_region(strip_num)
    off = find_tag(data, start, size, tag, bidx)
    if off is None:
        print(f"    !! tag {tag:#06x} bidx={bidx} NOT FOUND in strip {strip_num}")
        return False
    data[off:off + 4] = struct.pack('<f', value)
    return True


def write_hpf(data, strip_num, freq_hz):
    start, _ = strip_region(strip_num)
    data[start + HPF_REL:start + HPF_REL + 4] = struct.pack('<f', freq_hz)


def find_all_name_fields(data, old_name):
    enc = old_name.encode('ascii')
    sig = bytes([len(enc)]) + enc
    hits = []
    for i in range(NAME_SEARCH_START, NAME_SEARCH_END - 31):
        if data[i:i + len(sig)] == sig:
            after = data[i + len(sig):i + 32]
            nulls = sum(1 for b in after if b == 0)
            if nulls >= len(after) - 5:
                hits.append(i)
    return hits


def write_all_name_fields(data, old_name, new_name):
    enc   = new_name.encode('ascii')
    field = bytes([len(enc)]) + enc + b'\x00' * (32 - 1 - len(enc))
    hits  = find_all_name_fields(data, old_name)
    for off in hits:
        data[off:off + 32] = field
    return len(hits)


def apply_eq_band(data, strip_num, bidx, gain, freq, q, eq_type, enabled=True,
                  deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300):
    write_tag(data, strip_num, TAG_EQ_ENABLE,  bidx, ON if enabled else OFF)
    write_tag(data, strip_num, TAG_EQ_GAIN,    bidx, gain)
    write_tag(data, strip_num, TAG_EQ_FREQ,    bidx, freq)
    write_tag(data, strip_num, TAG_EQ_Q,       bidx, q)
    write_tag(data, strip_num, TAG_EQ_TYPE,    bidx, eq_type)
    write_tag(data, strip_num, TAG_DEQ_ENABLE, bidx, ON if deq else OFF)
    if deq:
        write_tag(data, strip_num, TAG_DEQ_THRESH, bidx, deq_thr)
        write_tag(data, strip_num, TAG_DEQ_ATK,    bidx, deq_atk)
        write_tag(data, strip_num, TAG_DEQ_REL,    bidx, deq_rel)


def apply_channel(data, strip_num, name, old_name, hpf, lpf, bands):
    print(f"  Strip {strip_num:2d}  {name:<14s}  HPF={hpf}  LPF={lpf}")
    n = write_all_name_fields(data, old_name, name)
    if n == 0:
        print(f"    !! no name fields found for old_name='{old_name}'")
    elif n < 5:
        print(f"    !! only {n} name field copies found (expected ~20)")
    write_hpf(data, strip_num, hpf)
    write_tag(data, strip_num, TAG_LPF_FREQ, 1, lpf)
    for bidx, b in enumerate(bands):
        apply_eq_band(
            data, strip_num, bidx,
            gain=b['gain'], freq=b['freq'], q=b['q'], eq_type=b['type'],
            enabled=b.get('enabled', True),
            deq=b.get('deq', False),
            deq_thr=b.get('deq_thr', -36.0),
            deq_atk=b.get('deq_atk', 0.010),
            deq_rel=b.get('deq_rel', 0.300),
        )


def B(gain, freq, q, type_, deq=False, thr=-36, atk=0.010, rel=0.300, enabled=True):
    return dict(gain=gain, freq=freq, q=q, type=type_,
                deq=deq, deq_thr=thr, deq_atk=atk, deq_rel=rel, enabled=enabled)


def FLAT():
    return dict(gain=0.0, freq=1000.0, q=0.71, type=BELL, enabled=False,
                deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300)


# ── channel table — Seals and Crofts 2 ───────────────────────────────────────
# Source: Seals and Crofts 2 - FOH Channel Processing.md

CHANNELS = {
    1: ("Kick",       "1",  40,    8000, [
        B(-2, 6000, 0.8, SHELF),
        B(+3, 3000, 1.5, BELL),
        B(-5,  250, 2.0, BELL,  deq=True, thr=-16, atk=0.008, rel=0.080),
        B(+2,   60, 1.2, SHELF),
    ]),
    2: ("Snare",      "2",  100,   OFF_LPF, [
        B(+2, 10000, 0.8, SHELF),
        B(+2,  4000, 1.5, BELL),
        B(-4,   250, 2.0, BELL,  deq=True, thr=-16, atk=0.008, rel=0.080),
        B(+3,   180, 1.5, BELL),
    ]),
    3: ("Underhat",   "3",  200,   OFF_LPF, [
        B(+4, 12000, 0.8, SHELF),
        B(+4,  6000, 1.2, BELL),
        B(-3,   600, 2.0, BELL),
        B(-5,   315, 1.5, BELL),
    ]),
    4: ("Rack 1",     "4",  100,   12000, [
        B(-2,  8000, 0.8, SHELF),
        B(+2,  4000, 1.2, BELL),
        B(-5,   315, 2.0, BELL,  deq=True, thr=-16, atk=0.008, rel=0.100),
        B(+3,   200, 1.5, BELL),
    ]),
    5: ("Rack 2",     "5",  100,   12000, [
        B(-2,  8000, 0.8, SHELF),
        B(+2,  4000, 1.2, BELL),
        B(-5,   315, 2.0, BELL,  deq=True, thr=-16, atk=0.008, rel=0.100),
        B(+3,   200, 1.5, BELL),
    ]),
    6: ("Floor Tom",  "6",   60,   10000, [
        B(-3,  8000, 0.8, SHELF),
        B(+2,  3000, 1.2, BELL),
        B(-5,   250, 2.0, BELL,  deq=True, thr=-12, atk=0.008, rel=0.100),
        B(+4,   100, 1.2, SHELF),
    ]),
    7: ("OH Left",    "7",  100,   OFF_LPF, [
        B(+1, 12000, 0.8, SHELF),
        B(+1,  6000, 1.2, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-18, atk=0.020, rel=0.200),
        B(-4,   200, 2.0, SHELF),
    ]),
    8: ("OH Right",   "8",  100,   OFF_LPF, [
        B(+1, 12000, 0.8, SHELF),
        B(+1,  6000, 1.2, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-18, atk=0.020, rel=0.200),
        B(-4,   200, 2.0, SHELF),
    ]),
    9: ("Bass DI",    "9",   50,    5000, [
        B(+1,  3500, 0.8, SHELF),
        B(+2,   800, 1.5, BELL),
        B(-4,   250, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.100),
        B(+2,    80, 1.2, SHELF),
    ]),
    10: ("Ac Guitar", "10",  80,   OFF_LPF, [
        B(+2,  8000, 0.8, SHELF),
        B(+2,  2500, 1.2, BELL),
        B(-5,   250, 2.0, BELL,  deq=True, thr=-16, atk=0.015, rel=0.120),
        B(-2,   200, 1.5, SHELF),
    ]),
    11: ("Elec Gtr L","11",  80,   OFF_LPF, [
        B(+1,  8000, 0.8, SHELF),
        B(+2,  2500, 1.5, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-18, atk=0.010, rel=0.080),
        B(-3,   200, 1.5, BELL),
    ]),
    12: ("Elec Gtr R","12",  80,   OFF_LPF, [
        B(+1,  8000, 0.8, SHELF),
        B(+2,  2500, 1.5, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-18, atk=0.010, rel=0.080),
        B(-3,   200, 1.5, BELL),
    ]),
    13: ("Piano Low", "13",  60,   OFF_LPF, [
        B(+2,  8000, 0.8, SHELF),
        B(+1,  2000, 1.2, BELL),
        B(-5,   315, 2.0, BELL,  deq=True, thr=-14, atk=0.010, rel=0.120),
        B(-2,   200, 1.5, SHELF),
    ]),
    14: ("Piano Hi",  "14", 120,   OFF_LPF, [
        B(+3, 10000, 0.8, SHELF),
        B(+2,  3000, 1.2, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-18, atk=0.010, rel=0.100),
        B(-3,   200, 1.5, SHELF),
    ]),
    15: ("Keys L",    "15",  80,   OFF_LPF, [
        B(+1,  8000, 0.8, SHELF),
        B(+2,  3000, 1.2, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-16, atk=0.015, rel=0.150),
        B(-3,   200, 1.5, SHELF),
    ]),
    16: ("Keys R",    "16",  80,   OFF_LPF, [
        B(+1,  8000, 0.8, SHELF),
        B(+2,  3000, 1.2, BELL),
        B(-4,   315, 2.0, BELL,  deq=True, thr=-16, atk=0.015, rel=0.150),
        B(-3,   200, 1.5, SHELF),
    ]),
    17: ("Tracks L",  "17",  80,   OFF_LPF, [
        FLAT(),
        FLAT(),
        B(-3,  315, 2.0, BELL),
        B(-2,  200, 1.5, SHELF),
    ]),
    18: ("Tracks R",  "18",  80,   OFF_LPF, [
        FLAT(),
        FLAT(),
        B(-3,  315, 2.0, BELL),
        B(-2,  200, 1.5, SHELF),
    ]),
    19: ("Click",     "19",  80,   OFF_LPF, [
        FLAT(),
        FLAT(),
        FLAT(),
        FLAT(),
    ]),
    20: ("Video",     "20",  80,   OFF_LPF, [
        FLAT(),
        FLAT(),
        FLAT(),
        FLAT(),
    ]),
    21: ("Ziggy Vox", "21", 100,   15000, [
        B(+3,  8000, 0.7, SHELF),
        B(+3,  3000, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
    22: ("Lua Vox",   "22", 100,   15000, [
        B(+2,  8000, 0.7, SHELF),
        B(+3,  3000, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
    23: ("Brady Vox", "23", 100,   15000, [
        B(+2,  8000, 0.7, SHELF),
        B(+3,  3500, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
    24: ("Key Vox",   "24", 100,   15000, [
        B(+2,  8000, 0.7, SHELF),
        B(+3,  3000, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
    25: ("Brian Vox", "25", 100,   15000, [
        B(+3,  8000, 0.7, SHELF),
        B(+3,  3000, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
    26: ("John Vox",  "26", 100,   15000, [
        B(+3,  8000, 0.7, SHELF),
        B(+3,  3000, 1.2, BELL),
        B(-4,   300, 2.0, BELL,  deq=True, thr=-16, atk=0.010, rel=0.080),
        B(-4,   200, 1.5, SHELF),
    ]),
}


# ── verification ──────────────────────────────────────────────────────────────

def verify_do_not_write_untouched(src_bytes, out_bytes):
    assert len(src_bytes) == len(out_bytes), "size mismatch"
    sigs = {struct.pack('<H', t) for t in DO_NOT_WRITE_TAGS}
    diffs = []
    for i in range(0, len(src_bytes) - 7):
        if src_bytes[i + 4:i + 6] in sigs:
            if src_bytes[i:i + 4] != out_bytes[i:i + 4]:
                tag  = struct.unpack_from('<H', src_bytes, i + 4)[0]
                bidx = struct.unpack_from('<H', src_bytes, i + 6)[0]
                src_v = struct.unpack_from('<f', src_bytes, i)[0]
                out_v = struct.unpack_from('<f', out_bytes, i)[0]
                diffs.append((i, tag, bidx, src_v, out_v))
    return diffs


def spotcheck(src_bytes, out_bytes, sample_strip=1):
    name = CHANNELS[sample_strip][0]
    s1 = STRIP1_HDR + (sample_strip - 1) * STRIP_SIZE
    name_hits = find_all_name_fields(bytearray(out_bytes), name)

    hpf_v = struct.unpack_from('<f', out_bytes, s1 + HPF_REL)[0]
    lpf_v = deq_v = None
    for i in range(s1, s1 + STRIP_SIZE - 7):
        sig = out_bytes[i + 4:i + 8]
        if sig == struct.pack('<HH', TAG_LPF_FREQ, 1) and lpf_v is None:
            lpf_v = struct.unpack_from('<f', out_bytes, i)[0]
        if sig == struct.pack('<HH', TAG_DEQ_ENABLE, 2) and deq_v is None:
            deq_v = struct.unpack_from('<f', out_bytes, i)[0]

    print(f"\n{'=' * 60}")
    print(f"File size:  {len(out_bytes):,} bytes (template: {len(src_bytes):,})")
    print(f"\nSpot-check Ch {sample_strip} ({name}):")
    print(f"  Name field copies replaced: {len(name_hits)}")
    print(f"  HPF: {hpf_v:.1f} Hz   LPF: {lpf_v:.1f} Hz")
    if deq_v is not None:
        print(f"  DEQ enable bidx=2: {deq_v:.1f}")

    diffs = verify_do_not_write_untouched(src_bytes, out_bytes)
    print(f"\nDo-not-write tag verification (Mustard + Mustard-suspect):")
    if not diffs:
        print(f"  PASS — every restricted tag is byte-identical to template.")
        return True
    print(f"  FAIL — {len(diffs)} restricted records were modified:")
    for off, tag, bidx, sv, ov in diffs[:10]:
        print(f"    @{off:#010x}  tag={tag:#06x} bidx={bidx}  "
              f"src={sv:.3f} -> out={ov:.3f}")
    if len(diffs) > 10:
        print(f"    ... +{len(diffs) - 10} more")
    return False


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Apply Seals and Crofts 2 config to Q225 .ses template.")
    ap.add_argument("--src",  required=True)
    ap.add_argument("--dest", required=True)
    args = ap.parse_args(argv)

    src_bytes = open(args.src, 'rb').read()
    data      = bytearray(src_bytes)
    orig_size = len(data)

    print(f"Source:  {os.path.basename(args.src)}  ({orig_size:,} bytes)")
    print(f"Output:  {args.dest}\n")
    print("Applying channels:")

    for strip_num in sorted(CHANNELS.keys()):
        name, old_name, hpf, lpf, bands = CHANNELS[strip_num]
        apply_channel(data, strip_num, name, old_name, hpf, lpf, bands)

    assert len(data) == orig_size, f"Size mismatch: {len(data)} != {orig_size}"

    out_bytes = bytes(data)
    with open(args.dest, 'wb') as f:
        f.write(out_bytes)

    ok = spotcheck(src_bytes, out_bytes)
    print(f"\nWritten -> {args.dest}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
