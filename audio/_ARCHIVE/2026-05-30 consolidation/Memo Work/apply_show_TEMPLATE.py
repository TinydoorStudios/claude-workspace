#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — Memo Template

Copy this file into a show folder, rename it apply_<showname>.py, and
fill in the CHANNELS dict at the bottom with the show's per-channel
data. Then run it with --src pointing at the master template .ses and
--dest into the show folder.

See Q225 SES Patcher SOP/02_SHOW_PATCHER_WORKFLOW.md for the full
procedure and 01_Q225_SES_REFERENCE.md for the tag map.

What this writes
----------------
Per channel:
  - channel name (all ~20 snapshot copies in the file)
  - HPF frequency (fixed offset in the strip)
  - LPF frequency (TLV tag 0x0703 bidx=1)
  - Four EQ bands: gain, freq, Q, type, enable; DEQ on requested bands

What this does NOT write
------------------------
  - SD compressor (tags unknown — see reference doc)
  - SD gate (tags unknown — see reference doc)
  - Mustard plugin anything (must stay OFF on touched channels)

The verification block at the end MUST report PASS before the output
file is handed to the console. If FAIL, fix the script — do not load
the file.

CRITICAL — do NOT write to 0x0a41c7. It is a reverb/room preset table.
Writing there caused a Q225 access violation in an earlier version.
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
# Verification at the end of the run checks the output against the source
# for every record carrying one of these tags. Any byte change = FAIL.

DO_NOT_WRITE_TAGS = (
    # Mustard Dynamic 2 slot (was mislabeled as SD comp in v1–v11)
    0x1E0E,  # Mustard Dyn 2 ENABLE
    0x1E0B,  # Mustard Dyn 2 MAKEUP
    0x1E11,  # Mustard Dyn 2 THRESHOLD
    0x1E12,  # Mustard Dyn 2 RELEASE
    # Suspected Mustard Dynamic 1 slot (was mislabeled as SD gate) — leave alone
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    # Other known Mustard tags from prior investigation
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


# ── channel-data shorthand ───────────────────────────────────────────────────
# B(gain, freq, q, type)                                  ← simple band
# B(gain, freq, q, type, deq=True, thr=-16, atk=0.01, rel=0.08)  ← with DEQ
# FLAT()                                                  ← inactive placeholder band

def B(gain, freq, q, type_, deq=False, thr=-36, atk=0.010, rel=0.300, enabled=True):
    return dict(gain=gain, freq=freq, q=q, type=type_,
                deq=deq, deq_thr=thr, deq_atk=atk, deq_rel=rel, enabled=enabled)


def FLAT():
    return dict(gain=0.0, freq=1000.0, q=0.71, type=BELL, enabled=False,
                deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300)


# ─────────────────────────────────────────────────────────────────────────────
# CHANNEL TABLE — FILL THIS IN FROM THE SHOW PAPERWORK
# ─────────────────────────────────────────────────────────────────────────────
# Format:
#   strip_num: (
#       "Display Name",        # new name on the console
#       "OldName",             # what the template currently has (usually "1", "2", ...)
#       hpf_hz,                # HPF cutoff in Hz
#       lpf_hz_or_OFF_LPF,     # LPF cutoff, or OFF_LPF for no LPF
#       [
#           B(gain, freq, q, type),                                 # bidx 0  High
#           B(gain, freq, q, type),                                 # bidx 1  Upper Mid
#           B(gain, freq, q, type, deq=True, thr=-16, ...),         # bidx 2  Lower Mid
#           B(gain, freq, q, type),                                 # bidx 3  Low
#       ],
#   ),
#
# Notes:
#   - Bands MUST be in High→Low order (bidx 0 = High, bidx 3 = Low) to match
#     the Q225 channel-card template. (Brian's standard.)
#   - Use SHELF for shelving bands, BELL for bell. Match the processing PDF.
#   - Skip channels Brian said to leave alone — just don't list them here.
#   - Use FLAT() for an inactive band you still need to occupy a slot.

CHANNELS = {
    # Fill in from the show's FOH Channel Processing .md file.
    # Format:
    #   strip_num: ("Display Name", "OldName", hpf_hz, lpf_or_OFF_LPF,
    #       [B(gain, freq, q, SHELF_or_BELL),          # bidx 0 — High
    #        B(gain, freq, q, SHELF_or_BELL),          # bidx 1 — Upper Mid
    #        B(gain, freq, q, BELL, deq=True,          # bidx 2 — Lower Mid (add DEQ if listed)
    #          thr=-16, atk=0.008, rel=0.080),
    #        B(gain, freq, q, SHELF_or_BELL)]),        # bidx 3 — Low
    # old_name = str(strip_num) for the master template.
    # Use FLAT() for a bypassed band. OFF_LPF for no LPF.
    # Strips 1–48 are in range. Ch 25+ must be set manually if console
    # firmware does not surface them via the patcher strip map.
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


def spotcheck(src_bytes, out_bytes, sample_strip=1):
    if sample_strip not in CHANNELS:
        # Pick the first defined channel for the spot-check.
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
        description="Apply a show config to a DiGiCo Q225 .ses template.")
    ap.add_argument("--src",  required=True,
                    help="Path to template .ses (master: 'brian memo v2.ses')")
    ap.add_argument("--dest", required=True,
                    help="Path for output .ses (inside the show folder)")
    args = ap.parse_args(argv)

    if not CHANNELS:
        print("ERROR: CHANNELS dict is empty. Fill it in from the show paperwork before running.")
        return 2

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
