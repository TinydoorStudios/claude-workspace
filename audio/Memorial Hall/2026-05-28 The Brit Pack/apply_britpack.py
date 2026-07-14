#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — The Brit Pack 2026-05-28
Memorial Hall

Run:
  python3 apply_britpack.py \
    --src  "/path/to/brian memo v2.ses" \
    --dest "/path/to/2026-05-28 The Brit Pack/The Brit Pack.ses"

Verification block MUST report PASS before loading on console.
Do NOT load a file that reports FAIL.

CRITICAL: Never edit the template (brian memo v2.ses) directly.
CRITICAL: Do NOT write to 0x0a41c7 — reverb preset table, caused access violation.
"""

import argparse
import os
import struct
import sys


# ── layout constants ─────────────────────────────────────────────────────────

DISP_NAME_BASE   = 0x0a2a5a   # Ch1 display name; stride 125 bytes/ch
DISP_NAME_STRIDE = 125

STRIP1_HDR = 0x0b0327
STRIP_SIZE = 5638
HPF_REL    = 406              # HPF: fixed float at strip_start + 406

# Name scan range: display name section → end of all 48 main strips
NAME_SEARCH_START = DISP_NAME_BASE
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 48


# ── EQ / DEQ / filter tags (verified safe to write) ──────────────────────────

TAG_EQ_ENABLE  = 0x0404
TAG_EQ_GAIN    = 0x0403
TAG_EQ_FREQ    = 0x0406
TAG_EQ_Q       = 0x0407
TAG_EQ_TYPE    = 0x040b       # 1.0 = shelf, 2.0 = bell
TAG_DEQ_ENABLE = 0x040e
TAG_DEQ_THRESH = 0x0411
TAG_DEQ_ATK    = 0x0412
TAG_DEQ_REL    = 0x0410
TAG_LPF_FREQ   = 0x0703       # bidx = 1


# ── Tags we DO NOT touch — see reference doc ─────────────────────────────────

DO_NOT_WRITE_TAGS = (
    0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    0x0503, 0x050e, 0x0511, 0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47,
)


# ── EQ shorthand ─────────────────────────────────────────────────────────────

SHELF   = 1.0
BELL    = 2.0
ON      = 1.0
OFF     = 0.0
OFF_LPF = 25000.0   # "no LPF"


# ── low-level helpers ────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# CHANNELS — The Brit Pack 2026-05-28
# Source: The Brit Pack - FOH Channel Processing.md
#
# Band order: bidx 0 = High, bidx 1 = Upper Mid, bidx 2 = Lower Mid, bidx 3 = Low
# old_name = str(strip_num) for the master template
# atk/rel converted from ms (in the MD) to seconds here
# ─────────────────────────────────────────────────────────────────────────────

CHANNELS = {

    # ── Drums ──────────────────────────────────────────────────────────────────

    1: ("KICK IN", "1", 40.0, 6000.0, [
        B(-2.0, 5000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 3.0, 3500.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-4.0,  250.0, 2.0, BELL, deq=True, thr=-14, atk=0.008, rel=0.080),  # bidx 2  Lower Mid DEQ
        B( 3.0,   60.0, 1.2, SHELF),                                       # bidx 3  Low Shelf
    ]),

    2: ("KICK OUT", "2", 40.0, OFF_LPF, [
        B( 2.0, 4000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-5.0,  250.0, 2.0, BELL, deq=True, thr=-12, atk=0.008, rel=0.080),  # bidx 2  Lower Mid DEQ
        B( 4.0,   80.0, 1.2, SHELF),                                       # bidx 3  Low Shelf
    ]),

    3: ("SNARE", "3", 100.0, OFF_LPF, [
        B( 3.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0, 4000.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-5.0,  315.0, 2.0, BELL, deq=True, thr=-16, atk=0.008, rel=0.080),  # bidx 2  Lower Mid DEQ
        B( 3.0,  180.0, 1.5, BELL),                                        # bidx 3  Low Bell (body)
    ]),

    4: ("HAT", "4", 400.0, 14000.0, [
        B( 3.0, 10000.0, 0.8, SHELF),                                     # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-4.0,   600.0, 2.0, BELL),                                       # bidx 2  Lower Mid (static, no DEQ)
        B(-4.0,   315.0, 1.5, BELL),                                       # bidx 3  Low Bell
    ]),

    5: ("RACK", "5", 100.0, 12000.0, [
        B(-2.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0, 4000.0, 1.2, BELL),                                        # bidx 1  Upper Mid
        B(-5.0,  315.0, 2.0, BELL, deq=True, thr=-16, atk=0.008, rel=0.100),  # bidx 2  Lower Mid DEQ
        B( 3.0,  200.0, 1.5, BELL),                                        # bidx 3  Low Bell (body)
    ]),

    6: ("FLOOR", "6", 60.0, 10000.0, [
        B(-3.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0, 3000.0, 1.2, BELL),                                        # bidx 1  Upper Mid
        B(-5.0,  250.0, 2.0, BELL, deq=True, thr=-12, atk=0.008, rel=0.100),  # bidx 2  Lower Mid DEQ
        B( 4.0,  100.0, 1.2, SHELF),                                       # bidx 3  Low Shelf
    ]),

    7: ("OH L", "7", 180.0, OFF_LPF, [
        B( 2.0, 10000.0, 0.8, SHELF),                                     # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-4.0,   315.0, 2.0, BELL, deq=True, thr=-18, atk=0.020, rel=0.200),  # bidx 2  Lower Mid DEQ
        B(-4.0,   200.0, 2.0, SHELF),                                      # bidx 3  Low Shelf
    ]),

    8: ("OH R", "8", 180.0, OFF_LPF, [
        B( 2.0, 10000.0, 0.8, SHELF),                                     # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-4.0,   315.0, 2.0, BELL, deq=True, thr=-18, atk=0.020, rel=0.200),  # bidx 2  Lower Mid DEQ
        B(-4.0,   200.0, 2.0, SHELF),                                      # bidx 3  Low Shelf
    ]),

    # ── Bass ───────────────────────────────────────────────────────────────────

    9: ("BASS DI", "9", 40.0, 5000.0, [
        B( 2.0, 2500.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0,  800.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-4.0,  250.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.100),  # bidx 2  Lower Mid DEQ
        B( 3.0,   80.0, 1.2, SHELF),                                       # bidx 3  Low Shelf
    ]),

    10: ("BASS AMP", "10", 60.0, 5000.0, [
        B( 1.0, 2000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-4.0,  315.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ
        B(-3.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut)
    ]),

    # ── Keys ───────────────────────────────────────────────────────────────────

    11: ("KEYS L", "11", 30.0, OFF_LPF, [
        B( 2.0, 10000.0, 0.8, SHELF),                                     # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-3.0,   250.0, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.120),  # bidx 2  Lower Mid DEQ
        B(-2.0,   200.0, 1.5, SHELF),                                      # bidx 3  Low Shelf (cut)
    ]),

    12: ("KEYS R", "12", 30.0, OFF_LPF, [
        B( 2.0, 10000.0, 0.8, SHELF),                                     # bidx 0  High Shelf
        FLAT(),                                                            # bidx 1  Upper Mid — FLAT
        B(-3.0,   250.0, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.120),  # bidx 2  Lower Mid DEQ
        B(-2.0,   200.0, 1.5, SHELF),                                      # bidx 3  Low Shelf (cut)
    ]),

    # ── Guitar ─────────────────────────────────────────────────────────────────

    13: ("GTR CTR", "13", 100.0, OFF_LPF, [
        B( 2.0, 4000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0, 2500.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-5.0,  400.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ
        B(-3.0,  200.0, 1.5, BELL),                                        # bidx 3  Low Bell (cut)
    ]),

    14: ("GTR C DI", "14", 100.0, OFF_LPF, [
        FLAT(),                                                            # bidx 0  High Shelf — FLAT
        B( 2.0, 2500.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-4.0,  315.0, 2.0, BELL),                                        # bidx 2  Lower Mid (static, no DEQ)
        B(-3.0,  200.0, 1.5, BELL),                                        # bidx 3  Low Bell (cut)
    ]),

    15: ("GTR HL", "15", 100.0, OFF_LPF, [
        B( 2.0, 4000.0, 0.8, SHELF),                                      # bidx 0  High Shelf
        B( 2.0, 2500.0, 1.5, BELL),                                        # bidx 1  Upper Mid
        B(-5.0,  400.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ
        B(-3.0,  200.0, 1.5, BELL),                                        # bidx 3  Low Bell (cut)
    ]),

    # ── Vocals — CUTS ONLY, no boosts ─────────────────────────────────────────

    16: ("BRYAN", "16", 120.0, 15000.0, [
        B(-2.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf (cut)
        B(-3.0, 3000.0, 1.5, BELL),                                        # bidx 1  Upper Mid (cut)
        B(-5.0,  300.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ (cut)
        B(-4.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut)
    ]),

    17: ("MATT", "17", 120.0, 14000.0, [
        B(-3.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf (cut)
        B(-3.0, 3500.0, 1.5, BELL),                                        # bidx 1  Upper Mid (cut)
        B(-5.0,  300.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ (cut)
        B(-4.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut)
    ]),

    18: ("MATT 2", "18", 120.0, 14000.0, [
        B(-3.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf (cut)
        B(-3.0, 3500.0, 1.5, BELL),                                        # bidx 1  Upper Mid (cut)
        B(-5.0,  300.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ (cut)
        B(-4.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut)
    ]),

    19: ("MARK", "19", 120.0, 15000.0, [
        B(-2.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf (cut)
        B(-3.0, 3000.0, 1.5, BELL),                                        # bidx 1  Upper Mid (cut)
        B(-5.0,  300.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ (cut)
        B(-4.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut)
    ]),

    20: ("WILL", "20", 130.0, 15000.0, [
        B(-2.0, 8000.0, 0.8, SHELF),                                      # bidx 0  High Shelf (cut)
        B(-3.0, 3000.0, 1.5, BELL),                                        # bidx 1  Upper Mid (cut)
        B(-5.0,  300.0, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),  # bidx 2  Lower Mid DEQ (cut)
        B(-5.0,  200.0, 1.5, SHELF),                                       # bidx 3  Low Shelf (cut, slightly more aggressive)
    ]),
}


# ── verification ─────────────────────────────────────────────────────────────

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
    if sample_strip not in CHANNELS:
        if not CHANNELS:
            print("\nNo channels defined; skipping spot-check.")
            return verify_do_not_write_untouched(src_bytes, out_bytes) == []
        sample_strip = sorted(CHANNELS.keys())[0]

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


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Apply The Brit Pack 2026-05-28 config to DiGiCo Q225 .ses template.")
    ap.add_argument("--src",  required=True,
                    help="Path to template .ses (master: 'brian memo v2.ses')")
    ap.add_argument("--dest", required=True,
                    help="Path for output .ses (inside the show folder)")
    args = ap.parse_args(argv)

    src_bytes = open(args.src, 'rb').read()
    data      = bytearray(src_bytes)
    orig_size = len(data)

    print(f"Source:  {os.path.basename(args.src)}  ({orig_size:,} bytes)")
    print(f"Output:  {args.dest}\n")
    print("Applying channels:")

    for strip_num in sorted(CHANNELS.keys()):
        name, old_name, hpf, lpf, bands = CHANNELS[strip_num]
        if len(bands) != 4:
            print(f"    !! strip {strip_num} ({name}) has {len(bands)} bands; expected 4")
        apply_channel(data, strip_num, name, old_name, hpf, lpf, bands)

    assert len(data) == orig_size, f"Size mismatch: {len(data)} != {orig_size}"

    out_bytes = bytes(data)
    with open(args.dest, 'wb') as f:
        f.write(out_bytes)

    ok = spotcheck(src_bytes, out_bytes)
    print(f"\nWritten → {args.dest}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
