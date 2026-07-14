#!/usr/bin/env python3
"""
Gospel Awards 2026 — DiGiCo Q225 .ses patcher  v12

What this does
--------------
Takes `brian memo v2-99072ff1.ses` and applies the Gospel Awards 2026
show config on top of it. 23 channels touched (1–22, 24); channel 23 is
left alone.

Parameters written per channel:
  - channel name (all ~20 snapshot copies)
  - HPF frequency (fixed offset in strip)
  - LPF frequency (0x0703 bidx=1)
  - Four EQ bands: gain, freq, Q, type, enable; DEQ on the LowerMid band

Deliberately NOT written: compressor, gate, anything Mustard.

Tag-mapping correction (v12)
----------------------------
The "comp" and "gate" tag mappings used in v1–v11 were wrong. They were
not the SD compressor and gate — they were the Mustard plugin Dynamic
1/2 slot controls. Writing them turned Mustard Dynamic 2 on every
channel the script touched. Confirmed by console-save diff on
2026-05-22: loading the v11 NAMES_EQ_COMP output, disabling Mustard Dyn
2 on channel 1, and saving showed exactly two TLV value changes inside
channel 1's main strip — 0x1E0E (enable) 1.0→0.0 and 0x1E0B (makeup)
4.0→0.0. Threshold/release stayed at the script-written values, which
is classic Mustard-slot behaviour (persistent settings, only the enable
+ makeup zero on disable).

Real SD comp/gate tags are not yet identified. Find them with the same
console-save-diff method when needed — load this v12 output, manually
enable SD comp on channel 1 with known threshold/release/makeup, save,
diff. The bytes that change in ch1's main strip are the real SD comp
controls.

File format (reference)
-----------------------
Every parameter is an 8-byte TLV record:
    [float32 LE value][uint16 LE tag][uint16 LE bidx]

Main channel strips start at STRIP1_HDR (0x0b0327) and are STRIP_SIZE
(5638) bytes each. HPF frequency is a fixed float at strip_start + 406;
all other parameters are tagged TLV records located by scanning the strip.

CRITICAL — do NOT write to 0x0a41c7 (reverb/room preset table; caused
console access violation in earlier versions).
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

# Name scan range: display name section → end of all 24 main strips
NAME_SEARCH_START = DISP_NAME_BASE
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 24

# ── EQ / DEQ / filter tags ───────────────────────────────────────────────────

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

# ── Tags we DO NOT touch (Mustard plugin controls — see header) ─────────────
# Listed for the post-write verification: the output's bytes at every
# record carrying one of these tags must equal the source's bytes.

DO_NOT_WRITE_TAGS = (
    # Mustard Dynamic 2 slot (was mislabeled as SD comp in v1–v11)
    0x1E0E,  # Mustard Dyn 2 ENABLE
    0x1E0B,  # Mustard Dyn 2 MAKEUP
    0x1E11,  # Mustard Dyn 2 THRESHOLD
    0x1E12,  # Mustard Dyn 2 RELEASE
    # Suspected Mustard Dynamic 1 slot (was mislabeled as SD gate) — leave alone
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    # Known Mustard tags from prior investigation
    0x0503, 0x050e, 0x0511, 0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47,
)

# ── EQ shorthand ─────────────────────────────────────────────────────────────

SHELF = 1.0
BELL  = 2.0
ON    = 1.0
OFF   = 0.0
OFF_LPF = 25000.0   # "no LPF"


# ── low-level helpers ────────────────────────────────────────────────────────

def strip_region(strip_num):
    """Return (start, size) for the 1-indexed main strip."""
    start = STRIP1_HDR + (strip_num - 1) * STRIP_SIZE
    return start, STRIP_SIZE


def find_tag(data, start, size, tag, bidx):
    """Locate the first TLV record with this tag/bidx in [start, start+size)."""
    sig = struct.pack('<HH', tag, bidx)
    for i in range(start, start + size - 7):
        if data[i + 4:i + 8] == sig:
            return i
    return None


def write_tag(data, strip_num, tag, bidx, value):
    """Patch the float of the matching TLV record in this strip."""
    start, size = strip_region(strip_num)
    off = find_tag(data, start, size, tag, bidx)
    if off is None:
        print(f"    !! tag {tag:#06x} bidx={bidx} NOT FOUND in strip {strip_num}")
        return False
    data[off:off + 4] = struct.pack('<f', value)
    return True


def write_hpf(data, strip_num, freq_hz):
    """HPF freq lives at a fixed offset, not as a TLV record."""
    start, _ = strip_region(strip_num)
    data[start + HPF_REL:start + HPF_REL + 4] = struct.pack('<f', freq_hz)


# ── name patching (all ~20 snapshot copies per channel) ──────────────────────

def find_all_name_fields(data, old_name):
    """
    Scan NAME_SEARCH_START..NAME_SEARCH_END for every 32-byte name field
    matching old_name. A valid field starts with [len_byte][name_bytes]
    followed by mostly nulls (≤ 5 non-null stray bytes allowed).
    """
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
    """Replace every matching 32-byte name field. Returns hit count."""
    enc   = new_name.encode('ascii')
    field = bytes([len(enc)]) + enc + b'\x00' * (32 - 1 - len(enc))
    hits  = find_all_name_fields(data, old_name)
    for off in hits:
        data[off:off + 32] = field
    return len(hits)


# ── EQ applier ───────────────────────────────────────────────────────────────

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
    print(f"  Strip {strip_num:2d}  {name}   HPF={hpf}  LPF={lpf}")

    n = write_all_name_fields(data, old_name, name)
    if n == 0:
        print(f"    !! no name fields found for old_name='{old_name}'")

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


# ── channel-data shorthand ───────────────────────────────────────────────────

def B(gain, freq, q, type_, deq=False, thr=-36, atk=0.010, rel=0.300, enabled=True):
    return dict(gain=gain, freq=freq, q=q, type=type_,
                deq=deq, deq_thr=thr, deq_atk=atk, deq_rel=rel, enabled=enabled)


def FLAT():
    return dict(gain=0.0, freq=1000.0, q=0.71, type=BELL, enabled=False,
                deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300)


# ── channel table ────────────────────────────────────────────────────────────
# strip_num: (name, old_name, hpf_hz, lpf_hz, [bands])
# Bands: bidx 0 = High, 1 = Upper Mid, 2 = Lower Mid (+DEQ), 3 = Low

CHANNELS = {
    1:  ("Kick",        "1",   40,  8000,
         [B(-3, 6000, 0.8, SHELF), B(+4, 3000, 1.5, BELL),
          B(-6,  250, 2.0, BELL, deq=True, thr=-14, atk=0.008, rel=0.060),
          B(+4,   60, 1.2, SHELF)]),

    2:  ("Snare",       "2",  100,  OFF_LPF,
         [B(+2, 10000, 0.8, SHELF), B(+4, 5000, 1.2, BELL),
          B(-4,   250, 2.0, BELL, deq=True, thr=-16, atk=0.008, rel=0.080),
          B(+2,   160, 1.5, BELL)]),

    3:  ("Underhat",    "3",  200,  OFF_LPF,
         [B(+4, 12000, 0.8, SHELF), B(+4, 6000, 1.2, BELL),
          B(-3,   600, 2.0, BELL),
          B(-5,   315, 1.5, BELL)]),

    4:  ("Rack 1",      "4",  100,  12000,
         [B(-2,  8000, 0.8, SHELF), B(+3, 4000, 1.2, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-14, atk=0.008, rel=0.100),
          B(+3,   200, 1.5, BELL)]),

    5:  ("Rack 2",      "5",  100,  12000,
         [B(-2,  8000, 0.8, SHELF), B(+3, 4000, 1.2, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-14, atk=0.008, rel=0.100),
          B(+3,   200, 1.5, BELL)]),

    6:  ("Floor Tom",   "6",   60,  10000,
         [B(-3,  8000, 0.8, SHELF), B(+2, 3000, 1.2, BELL),
          B(-5,   250, 2.0, BELL, deq=True, thr=-12, atk=0.008, rel=0.100),
          B(+4,   100, 1.2, SHELF)]),

    7:  ("Underhd L",   "7",  200,  OFF_LPF,
         [B(+4, 12000, 0.8, SHELF), B(+4, 8000, 1.0, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-16, atk=0.020, rel=0.200),
          B(-5,   200, 2.0, SHELF)]),

    8:  ("Underhd R",   "8",  200,  OFF_LPF,
         [B(+4, 12000, 0.8, SHELF), B(+4, 8000, 1.0, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-16, atk=0.020, rel=0.200),
          B(-5,   200, 2.0, SHELF)]),

    9:  ("Bass DI",     "9",   40,  5000,
         [B(+2,  3500, 0.8, SHELF), B(+3, 1000, 1.5, BELL),
          B(-5,   250, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.100),
          B(+3,    80, 1.2, SHELF)]),

    10: ("Gtr Dynamic", "10",  80,  6000,
         [B(-4,  4000, 0.8, SHELF), B(+3, 1500, 1.5, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(+2,   150, 1.5, BELL)]),

    11: ("Gtr Cond",    "11", 250,  OFF_LPF,
         [B(+2,  8000, 0.8, SHELF), B(+3, 3500, 1.2, BELL),
          B(-4,   400, 2.0, BELL, deq=True, thr=-18, atk=0.015, rel=0.100),
          B(-4,   250, 1.5, SHELF)]),

    12: ("Keys 1 L",    "12",  80,  OFF_LPF,
         [B(+1,  8000, 0.8, SHELF), B(+2, 3000, 1.2, BELL),
          B(-4,   315, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.150),
          B(-3,   200, 1.5, SHELF)]),

    13: ("Keys 1 R",    "13",  80,  OFF_LPF,
         [B(+1,  8000, 0.8, SHELF), B(+2, 3000, 1.2, BELL),
          B(-4,   315, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.150),
          B(-3,   200, 1.5, SHELF)]),

    14: ("Keys 2 L",    "14",  80,  OFF_LPF,
         [B(+1,  8000, 0.8, SHELF), B(+2, 3000, 1.2, BELL),
          B(-4,   315, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.150),
          B(-3,   200, 1.5, SHELF)]),

    15: ("Keys 2 R",    "15",  80,  OFF_LPF,
         [B(+1,  8000, 0.8, SHELF), B(+2, 3000, 1.2, BELL),
          B(-4,   315, 2.0, BELL, deq=True, thr=-16, atk=0.015, rel=0.150),
          B(-3,   200, 1.5, SHELF)]),

    16: ("Tracks",      "16",  80,  OFF_LPF,
         [FLAT(), FLAT(),
          B(-3,   315, 2.0, BELL),
          B(-2,   200, 1.5, SHELF)]),

    17: ("BG Vox 1",    "17", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    18: ("BG Vox 2",    "18", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    19: ("BG Vox 3",    "19", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    20: ("BG Vox 4",    "20", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    21: ("BG Vox 5",    "21", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    22: ("BG Vox 6",    "22", 100,  15000,
         [B(+3,  8000, 0.7, SHELF), B(+4, 3000, 1.2, BELL),
          B(-5,   300, 2.0, BELL, deq=True, thr=-16, atk=0.010, rel=0.080),
          B(-4,   200, 1.5, SHELF)]),

    24: ("Podium",      "24", 120,  12000,
         [B(+2,  6000, 0.8, SHELF), B(+4, 2500, 1.2, BELL),
          B(-5,   315, 2.0, BELL, deq=True, thr=-18, atk=0.010, rel=0.100),
          B(-5,   200, 1.5, SHELF)]),
}


# ── verification ─────────────────────────────────────────────────────────────

def verify_do_not_write_untouched(src_bytes, out_bytes):
    """
    Walk the file. For every TLV record whose tag is in DO_NOT_WRITE_TAGS,
    the float value at that offset must be identical between src and out.
    """
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


def spotcheck(src_bytes, out_bytes):
    s1 = STRIP1_HDR
    name_hits = find_all_name_fields(bytearray(out_bytes), "Kick")

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
    print(f"\nSpot-check Ch 1 (Kick):")
    print(f"  Name field copies replaced: {len(name_hits)}")
    print(f"  HPF: {hpf_v:.1f} Hz   LPF: {lpf_v:.1f} Hz")
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
    ap = argparse.ArgumentParser(description="Apply Gospel Awards 2026 show config to a Q225 .ses template.")
    ap.add_argument("--src",  required=True, help="Path to template .ses (brian memo v2-99072ff1.ses)")
    ap.add_argument("--dest", required=True, help="Path for output .ses")
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
    print(f"\nWritten → {args.dest}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
