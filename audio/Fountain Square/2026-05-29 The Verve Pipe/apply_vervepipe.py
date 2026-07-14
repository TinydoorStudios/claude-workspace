#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — The Verve Pipe @ FSQ, 2026-05-29
Generated from: The Verve Pipe - FOH Channel Processing.md
"""

import argparse, os, struct, sys

STRIP1_HDR        = 0x011456
STRIP_SIZE        = 5383
HPF_REL           = 0
DISP_NAME_BASE    = 0x0a2a5a
DISP_NAME_STRIDE  = 125
NAME_SEARCH_END   = 0x0a5000

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

DO_NOT_WRITE_TAGS = (
    0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12,
    # 0x1D05 removed — confirmed HPF frequency tag in FSQ (was mislabeled Mustard in Memo)
    0x0503, 0x050e, 0x0511, 0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47,
)

SHELF = 1.0; BELL = 2.0; ON = 1.0; OFF = 0.0; OFF_LPF = 25000.0

def strip_region(n):
    s = STRIP1_HDR + (n - 1) * STRIP_SIZE
    return s, STRIP_SIZE

def find_tag(data, start, size, tag, bidx):
    sig = struct.pack('<HH', tag, bidx)
    for i in range(start, start + size - 7):
        if data[i + 4:i + 8] == sig:
            return i
    return None

def write_tag(data, n, tag, bidx, value):
    s, sz = strip_region(n)
    off = find_tag(data, s, sz, tag, bidx)
    if off is None:
        print(f"    !! tag {tag:#06x} bidx={bidx} NOT FOUND strip {n}")
        return False
    data[off:off + 4] = struct.pack('<f', value)
    return True

TAG_HPF_FREQ  = 0x1d05   # HPF frequency — confirmed in FSQ via empirical analysis
TAG_HPF_FREQ2 = 0x1e05   # Second HPF frequency instance (Q225 has two HPF filters/channel)

def write_hpf(data, n, freq):
    """Write HPF to both TLV HPF records (0x1d05 and 0x1e05 at bidx=0)."""
    write_tag(data, n, TAG_HPF_FREQ,  0, freq)
    write_tag(data, n, TAG_HPF_FREQ2, 0, freq)

def write_all_name_fields(data, n, old_name, new_name):
    s, sz = strip_region(n)
    enc = new_name.encode('ascii')
    field = bytes([len(enc)]) + enc + b'\x00' * (32 - 1 - len(enc))
    old_enc = old_name.encode('ascii')
    old_sig = bytes([len(old_enc)]) + old_enc
    hits = []
    for i in range(s, s + sz - 31):
        if data[i:i + len(old_sig)] == old_sig:
            after = data[i + len(old_sig):i + 32]
            if sum(1 for b in after if b == 0) >= len(after) - 5:
                hits.append(i)
                data[i:i + 32] = field
    # NOTE: display name section (DISP_NAME_BASE) is intentionally NOT written.
    # Those 125-byte slots contain metadata beyond the 32-byte name field;
    # writing 32 bytes of name+zeros corrupts that metadata and crashes the console.
    # The strip-scoped name copies (above) are sufficient for correct console display.
    return len(hits)

def apply_eq_band(data, n, bidx, gain, freq, q, eq_type, enabled=True,
                  deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300):
    write_tag(data, n, TAG_EQ_ENABLE,  bidx, ON if enabled else OFF)
    write_tag(data, n, TAG_EQ_GAIN,    bidx, gain)
    write_tag(data, n, TAG_EQ_FREQ,    bidx, freq)
    write_tag(data, n, TAG_EQ_Q,       bidx, q)
    write_tag(data, n, TAG_EQ_TYPE,    bidx, eq_type)
    write_tag(data, n, TAG_DEQ_ENABLE, bidx, ON if deq else OFF)
    if deq:
        write_tag(data, n, TAG_DEQ_THRESH, bidx, deq_thr)
        write_tag(data, n, TAG_DEQ_ATK,    bidx, deq_atk)
        write_tag(data, n, TAG_DEQ_REL,    bidx, deq_rel)

def B(gain, freq, q, type_, **kw):
    return dict(gain=gain, freq=freq, q=q, type=type_, enabled=True,
                deq=kw.get('deq',False), deq_thr=kw.get('thr',-36.0),
                deq_atk=kw.get('atk',0.010), deq_rel=kw.get('rel',0.300))

def FLAT():
    return dict(gain=0.0, freq=1000.0, q=0.71, type=BELL, enabled=False,
                deq=False, deq_thr=-36.0, deq_atk=0.010, deq_rel=0.300)

CHANNELS = {
    1:  ("Kick In",    "KICK IN",     40,  OFF_LPF, [B(-3.0,8000,0.71,SHELF), B(-3.0,3500,2.5,BELL),  B(-4.0,300,1.5,BELL),  FLAT()]),
    2:  ("Kick Out",   "SNARE TOP",   25,  OFF_LPF, [B(-4.0,8000,0.71,SHELF), B(-4.0,2500,2.0,BELL),  B(-3.0,350,1.5,BELL),  B(3.0,60,0.71,SHELF)]),
    3:  ("Snare Top",  "SNARE BOTTOM",100, OFF_LPF, [B(2.0,10000,0.71,SHELF), B(-2.0,1200,2.0,BELL),  B(-4.0,400,2.0,BELL),  B(-6.0,200,1.5,BELL)]),
    4:  ("Snare Bot",  "HI-HAT",      200, OFF_LPF, [B(3.0,8000,0.71,SHELF),  B(-3.0,2000,2.5,BELL),  B(-5.0,400,2.0,BELL),  B(-8.0,200,0.71,SHELF)]),
    5:  ("Hat",        "RACK 1",      450, OFF_LPF, [B(-2.0,12000,0.71,SHELF),B(-3.0,6000,2.0,BELL),  B(-3.0,800,2.0,BELL),  B(-5.0,350,1.5,BELL)]),
    6:  ("Rack 1",     "FLOOR",       80,  OFF_LPF, [B(-2.0,10000,0.71,SHELF),B(-3.0,2000,2.0,BELL),  B(-4.0,500,1.5,BELL),  B(2.0,80,0.71,SHELF)]),
    7:  ("Floor",      "BASS DI",     50,  OFF_LPF, [B(-2.0,8000,0.71,SHELF), B(-3.0,2000,2.0,BELL),  B(-4.0,400,1.5,BELL),  B(3.0,80,0.71,SHELF)]),
    8:  ("Ride",       "BASS MIC",    500, OFF_LPF, [B(-3.0,12000,0.71,SHELF),B(-2.0,4000,2.0,BELL),  B(-4.0,800,2.0,BELL),  B(-5.0,400,1.5,BELL)]),
    9:  ("OH Left",    "GUITAR 3",    200, OFF_LPF, [B(-1.0,12000,0.71,SHELF),B(-2.0,5000,2.5,BELL),  B(-3.0,250,1.5,BELL),  B(-4.0,150,1.5,BELL)]),
    10: ("OH Right",   "KEY 1",       200, OFF_LPF, [B(-1.0,12000,0.71,SHELF),B(-2.0,5000,2.5,BELL),  B(-3.0,250,1.5,BELL),  B(-4.0,150,1.5,BELL)]),
    11: ("Bass DI",    "CONGA 1",     35,  OFF_LPF, [B(-3.0,8000,0.71,SHELF), B(2.0,1500,2.0,BELL),   B(-4.0,250,1.5,BELL),  B(2.0,80,0.71,SHELF)]),
    12: ("Bass Mic",   "CONGA 2",     60,  OFF_LPF, [B(-4.0,6000,0.71,SHELF), B(-2.0,2500,2.0,BELL),  B(-3.0,400,1.5,BELL),  B(-6.0,100,1.5,BELL)]),
    13: ("GTR C 57",   "BONGO",       100, OFF_LPF, [B(-2.0,8000,0.71,SHELF), B(-3.0,3000,2.0,BELL),  B(-4.0,400,1.5,BELL),  B(-6.0,150,1.5,BELL)]),
    14: ("GTR C B27",  "VOCAL 4",     120, OFF_LPF, [B(-1.0,10000,0.71,SHELF),B(-2.0,2500,2.0,BELL),  B(-3.0,350,1.5,BELL),  B(-4.0,150,0.71,SHELF)]),
    15: ("GTR R 57",   "TINA",        100, OFF_LPF, [B(-2.0,8000,0.71,SHELF), B(-3.0,3000,2.0,BELL),  B(-4.0,400,1.5,BELL),  B(-6.0,150,1.5,BELL)]),
    16: ("GTR R B27",  "KICK IN",     120, OFF_LPF, [B(-1.0,10000,0.71,SHELF),B(-2.0,2500,2.0,BELL),  B(-3.0,350,1.5,BELL),  B(-4.0,150,0.71,SHELF)]),
    17: ("Acoustic",   "STAR",        80,  OFF_LPF, [B(-2.0,10000,0.71,SHELF),B(-3.0,3000,2.5,BELL),  B(-4.0,400,2.0,BELL),  B(-3.0,120,0.71,SHELF)]),
    18: ("Keys",       "Nearfield R", 40,  OFF_LPF, [B(-2.0,12000,0.71,SHELF),B(-3.0,3000,2.0,BELL),  B(-3.0,250,1.5,BELL),  B(-3.0,100,0.71,SHELF)]),
    19: ("SPDX",       "Kick In",     35,  OFF_LPF, [B(-3.0,10000,0.71,SHELF),B(-3.0,3000,2.0,BELL),  B(-3.0,300,1.5,BELL),  FLAT()]),
    20: ("Looper",     "Snare Top",   60,  OFF_LPF, [B(-2.0,10000,0.71,SHELF),B(-3.0,3000,2.0,BELL),  B(-3.0,400,1.5,BELL),  B(-4.0,150,1.5,BELL)]),
}

def verify_do_not_write(src, out):
    sigs = {struct.pack('<H', t) for t in DO_NOT_WRITE_TAGS}
    diffs = []
    for i in range(0, len(src) - 7):
        if src[i + 4:i + 6] in sigs:
            if src[i:i + 4] != out[i:i + 4]:
                tag  = struct.unpack_from('<H', src, i + 4)[0]
                bidx = struct.unpack_from('<H', src, i + 6)[0]
                diffs.append((i, tag, bidx,
                               struct.unpack_from('<f', src, i)[0],
                               struct.unpack_from('<f', out, i)[0]))
    return diffs

def spotcheck(src, out):
    sample = sorted(CHANNELS.keys())[0]
    name, old, hpf_exp = CHANNELS[sample][:3]
    s1 = STRIP1_HDR + (sample - 1) * STRIP_SIZE
    # Read HPF from TLV record 0x1d05 bidx=0
    hpf_v = None
    for i in range(s1, s1 + STRIP_SIZE - 7):
        if out[i + 4:i + 8] == struct.pack('<HH', TAG_HPF_FREQ, 0):
            hpf_v = struct.unpack_from('<f', out, i)[0]
            break
    if hpf_v is None:
        hpf_v = float('nan')
    lpf_v = None
    for i in range(s1, s1 + STRIP_SIZE - 7):
        if out[i + 4:i + 8] == struct.pack('<HH', TAG_LPF_FREQ, 1):
            lpf_v = struct.unpack_from('<f', out, i)[0]
            break
    enc = name.encode(); sig = bytes([len(enc)]) + enc
    hits = sum(1 for i in range(s1, s1 + STRIP_SIZE - 31) if out[i:i + len(sig)] == sig)
    print(f"\n{'=' * 60}")
    print(f"File size: {len(out):,} bytes (template: {len(src):,})")
    print(f"\nSpot-check Ch {sample} ({name}, was '{old}'):")
    print(f"  Name fields in strip: {hits}")
    print(f"  HPF: {hpf_v:.1f} Hz (expected {hpf_exp:.1f})")
    if lpf_v: print(f"  LPF: {lpf_v:.1f} Hz")
    diffs = verify_do_not_write(src, out)
    print(f"\nDo-not-write verification:")
    if not diffs:
        print("  PASS"); return True
    print(f"  FAIL — {len(diffs)} restricted tags modified")
    for off, tag, bidx, sv, ov in diffs[:5]:
        print(f"    @{off:#010x} tag={tag:#06x} bidx={bidx} {sv:.3f}->{ov:.3f}")
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dest", required=True)
    args = ap.parse_args()
    src_bytes = open(args.src, 'rb').read()
    data = bytearray(src_bytes)
    orig_size = len(data)
    print(f"Source: {os.path.basename(args.src)} ({orig_size:,} bytes)")
    print(f"Output: {args.dest}\n")
    print("Applying channels:")
    for n in sorted(CHANNELS):
        name, old, hpf, lpf, bands = CHANNELS[n]
        print(f"  Strip {n:2d}  {name:<14s}  HPF={hpf}  (was '{old}')")
        hits = write_all_name_fields(data, n, old, name)
        if hits == 0:
            print(f"    !! no name fields found for '{old}' in strip {n}")
        write_hpf(data, n, hpf)
        if not write_tag(data, n, TAG_LPF_FREQ, 1, lpf):
            write_tag(data, n, TAG_LPF_FREQ, 0, lpf)
        for bidx, b in enumerate(bands):
            apply_eq_band(data, n, bidx, b['gain'], b['freq'], b['q'], b['type'],
                          b.get('enabled', True), b.get('deq', False),
                          b.get('deq_thr', -36.0), b.get('deq_atk', 0.010), b.get('deq_rel', 0.300))
    assert len(data) == orig_size
    out_bytes = bytes(data)
    with open(args.dest, 'wb') as f:
        f.write(out_bytes)
    ok = spotcheck(src_bytes, out_bytes)
    print(f"\nWritten → {args.dest}")
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
