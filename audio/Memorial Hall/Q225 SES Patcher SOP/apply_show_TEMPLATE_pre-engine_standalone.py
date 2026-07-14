#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — MEMORIAL HALL (Memo) template.

TEMPLATE REVISION — 2026-07-01
------------------------------
Recalibrated for the NEW Memo template (`brian memo june 2026.ses`,
37,661,337 bytes, canonical copy in `Memorial Hall/_TEMPLATE/`). This is
a full console save in the same layout as the FSQ template: a
surface-label table (stride 125) plus contiguous current-scene channel
blocks (~5.5 KB each, ~19-20 name copies per block). The old
`brian memo v2.ses` (1,543,866 bytes, strip layout at 0x0b0327 / stride
5638) is RETIRED — its constants do not apply here. The old engine is
archived as `apply_show_TEMPLATE_v2_OLD_stripformat.py`.

Calibration derived 2026-07-01 by structural scan of the new template
(surface run + positional block walk + tag semantics re-confirmed:
band freq defaults 6300/1600/300/100 at bidx 0..3, LPF tag 0x0703
bidx 1 = 25000 off, HPF float at LPF+0x10 under tag 0xFFFF stored
16.0 = 20 Hz display x 0.8, comp thr 0x050F b0-2 = -20, gate slot b3).
NOTE: unlike the FSQ recalibration this one has NOT yet been proven by
a console save-diff — the first .ses built from it must be
console-verified before the pipeline is trusted (send-it hard stop).

WHAT IS CONFIRMED (same semantics as the console-verified FSQ engine)
---------------------------------------------------------------------
  - Fader display NAME   : surface-label slot + every copy in the
                           channel's current-scene block (~19-20).
  - EQ gain / freq / Q / type : tags 0x0403 / 0x0406 / 0x0407 / 0x040b,
                           bidx 0 = HIGHEST band (console Band 4),
                           bidx 3 = LOWEST band (console Band 1).
  - EQ band count        : tag 0x0405 bidx 0.
  - DEQ per band         : enable 0x040e, thresh 0x0411 (dB),
                           attack 0x0412 (s), release 0x0410 (s).
  - HPF                  : float at LPF value offset + 0x10 (record tag
                           reads 0xFFFF). STORED = 0.8 x displayed Hz.
  - LPF                  : tag 0x0703 bidx 1. STORED = 1.25 x displayed
                           Hz ("off" / 20 kHz -> stored 25000).
  - Comp threshold       : tag 0x050f bidx 0..2 (multiband-linked).
                           Gate enable 0x050e b3 — mapped, not written.

TEMPLATE BASELINE: Wireless 1-4 (faders 41-44) ship a starting vocal
curve (HPF ~184 display, notch @ ~5.4k Q20, -6 @ 335, small low moves);
instrument channels 1-39 are flat. Bands an MD doesn't name are left
as-is, so vocal shows inherit the baseline unless the MD overrides.

SAFETY GATE
-----------
On load, the patcher reads the 72 fader names at SURF_BASE and the 72
block names at BLOCK_BASE and compares both against EXPECTED_NAMES /
EXPECTED_BLOCK_NAMES. A mismatch means the offsets are stale (template
resaved) or the wrong .ses was passed as --src — the patcher ABORTS.
To recalibrate after a future resave: rescan for the stride-125 surface
run carrying the real fader names, walk the contiguous blocks
(stride 0x15A6) from the first channel block, and update SURF_BASE /
BLOCK_BASE / both name lists. Then console-verify a test build.

WORKFLOW
--------
  1. Input is the show's FOH Channel Processing .md (--md). B-numbers
     are CONSOLE bands: B1 = lowest, B4 = highest (locked 2026-05-30).
     The patcher maps B1->bidx3 ... B4->bidx0. Pre-2026-05-30 Memo MDs
     numbered bands the other way — do not feed those in unconverted.
  2. Run:  python3 apply_<show>.py \
             --src  "Memorial Hall/_TEMPLATE/brian memo june 2026.ses" \
             --dest "<show folder>/<Show>.ses" \
             --md   "<Show> - FOH Channel Processing.md"
  3. The verification block must print PASS before the file goes to USB.
  4. Brian loads it on the Q225 and says "verified" — only then is the
     build trusted (and only then does the show go to the wiki).
"""

import argparse, os, struct, sys

# ── calibrated Memo layout constants (brian memo june 2026.ses) ──────────────
TEMPLATE_SIZE = 37_661_337
SURF_BASE     = 0x231A48F   # fader 1 surface-label slot (length byte)
SURF_STRIDE   = 125         # bytes per fader in the surface-label table
BLOCK_BASE    = 0x2324D9C   # channel 1 current-scene block (first name copy)
BLOCK_STRIDE  = 0x15A6      # blocks are contiguous, one per channel
N_FADERS      = 72
BLOCK_PRE     = 0x30        # block bounds: [first_copy - PRE, first_copy + SPAN)
BLOCK_SPAN    = 0x15A0      # stays inside this block, clear of both neighbors

# Offset tripwire — surface-table names, faders 1..72 (see SAFETY GATE)
EXPECTED_NAMES = [str(n) for n in range(1, 40)] + [
    'Click-Tap', 'Wireless 1', 'Wireless 2', 'Wireless 3', 'Wireless 4',
    'W1 Monitor', 'W2 Monitor', 'W3 Monitor', 'W4 Monitor', 'Hall', 'Plate',
    'Room', '1/4 Note Delay', '1/8 Note Delay', 'Drum Verb', 'Snare Verb',
    'Stage Ambience', 'Above Stage Mics', 'Floor Crowd', 'Balcony Crowd',
    'Video', 'QLab', 'Spotify', 'FOH Playback', 'Mon TB', 'RTA', 'Pandora',
    'Fx 1', 'Fx 2', 'Fx 3', 'Fx 4', 'Fx 5', 'Fx 6',
]

# Block order in the file differs from fader order — blocks are matched to
# faders BY NAME. This list is the tripwire for the block walk.
EXPECTED_BLOCK_NAMES = [str(n) for n in range(1, 40)] + [
    'Click-Tap', 'QLab', 'Above Stage Mics', 'Floor Crowd', 'Balcony Crowd',
    'Wireless 1', 'Wireless 2', 'Wireless 3', 'Wireless 4', 'W1 Monitor',
    'W2 Monitor', 'W3 Monitor', 'W4 Monitor', 'Hall', 'Plate', 'Room',
    'Mon TB', 'RTA', 'Video', 'Spotify', 'Pandora', '1/4 Note Delay',
    '1/8 Note Delay', 'Drum Verb', 'FOH Playback', 'Snare Verb',
    'Stage Ambience', 'Fx 6', 'Fx 5', 'Fx 4', 'Fx 3', 'Fx 2', 'Fx 1',
]

TAG_EQ_GAIN  = 0x0403
TAG_EQ_FREQ  = 0x0406
TAG_EQ_Q     = 0x0407
TAG_EQ_TYPE  = 0x040B      # 1.0 = shelf, 2.0 = bell
TAG_EQ_COUNT = 0x0405      # bidx 0: number of active EQ bands
TAG_DEQ_EN   = 0x040E      # per-band dynamic EQ enable (0/1)
TAG_DEQ_THR  = 0x0411      # per-band DEQ threshold (dB)
TAG_DEQ_ATK  = 0x0412      # per-band DEQ attack (seconds)
TAG_DEQ_REL  = 0x0410      # per-band DEQ release (seconds)
TAG_LPF      = 0x0703      # bidx 1: LPF; stored = 1.25 x display Hz
TAG_COMP_THR = 0x050F      # bidx 0..2: comp threshold (dB)

# Tags that must never change (Mustard + Mustard-suspect + known-dangerous).
# Checked inside every written block during verification.
DO_NOT_WRITE_TAGS = (
    0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    0x0503, 0x050E, 0x0511, 0x08E1, 0x08E8, 0x0EE8, 0x0EFE, 0x1D47,
)

# Filter value encoding (save-diff confirmed 2026-06-10 / 2026-06-21):
HPF_SCALE = 0.8
LPF_SCALE = 1.25
WRITE_HPF = True
WRITE_LPF = True

SHELF, BELL = 1.0, 2.0
OFF_LPF     = 25000.0      # stored "no LPF" (= 20 kHz display x 1.25)

# .md band number (console: B1 = low .. B4 = high) -> file bidx (0 = high)
BIDX_FOR_BAND = {1: 3, 2: 2, 3: 1, 4: 0}

# ── name readers ──────────────────────────────────────────────────────────────
def _read_lp_name(buf, o):
    """Length-prefixed printable name at offset o, or None."""
    if o + 1 >= len(buf):
        return None
    ln = buf[o]
    if not (1 <= ln <= 24):
        return None
    s = buf[o + 1: o + 1 + ln]
    if len(s) < ln or any(not (32 <= c < 127) for c in s):
        return None
    return s.decode('latin1')

def _surf_offset(fader):
    return SURF_BASE + (fader - 1) * SURF_STRIDE

def _block_first(idx):
    return BLOCK_BASE + idx * BLOCK_STRIDE

def _block_bounds(idx):
    first = _block_first(idx)
    return first - BLOCK_PRE, first + BLOCK_SPAN

# ── safety gate ───────────────────────────────────────────────────────────────
def assert_template(buf):
    """Abort unless surface table AND block walk match the calibration."""
    if len(buf) != TEMPLATE_SIZE:
        sys.stderr.write(
            f"ABORT: --src is {len(buf):,} bytes; the calibrated Memo template\n"
            f"is {TEMPLATE_SIZE:,}. Wrong file or the template was resaved —\n"
            "recalibrate before patching (see SAFETY GATE in the header).\n")
        sys.exit(3)
    surf = [_read_lp_name(buf, _surf_offset(f)) for f in range(1, N_FADERS + 1)]
    blk  = [_read_lp_name(buf, _block_first(i)) for i in range(N_FADERS)]
    for got, want, what in ((surf, EXPECTED_NAMES, 'surface table'),
                            (blk, EXPECTED_BLOCK_NAMES, 'block walk')):
        if got != want:
            first = next((i for i, (a, b) in enumerate(zip(got, want))
                          if a != b), None)
            sys.stderr.write(
                f"ABORT: {what} does not match the calibrated Memo template\n"
                "(template resaved, or wrong --src). Patching would write to\n"
                "the wrong region. Recalibrate SURF_BASE/BLOCK_BASE + name\n"
                "lists, then console-verify a test build.\n")
            if first is not None:
                sys.stderr.write(f"  first mismatch at entry {first + 1}: "
                                 f"got {got[first]!r}, expected {want[first]!r}\n")
            sys.exit(3)

def block_index_for_fader(fader):
    """Blocks are matched to faders by name; both lists are unique."""
    name = EXPECTED_NAMES[fader - 1]
    return EXPECTED_BLOCK_NAMES.index(name)

# ── low-level helpers ─────────────────────────────────────────────────────────
def _name_copies(buf, old, lo, hi):
    """All validated name-field offsets (len byte) for `old` in [lo, hi)."""
    ob = old.encode('latin1'); hits = []; i = lo
    while i < hi:
        j = buf.find(ob, i, hi)
        if j < 0:
            break
        if j > 0 and buf[j - 1] == len(ob) and buf[j + len(ob)] == 0:
            hits.append(j - 1)
        i = j + 1
    return hits

def _records(buf, lo, hi, tag, bidx):
    """Value-offsets of every TLV record with tag/bidx in [lo, hi)."""
    sig = struct.pack('<HH', tag, bidx); out = []; i = lo
    while True:
        j = buf.find(sig, i, hi)
        if j < 0:
            break
        out.append(j - 4)
        i = j + 1
    return out

def _eq_window(buf, lo, hi):
    """Anchor on the high band's freq (only sane 20..25000 value) to bound
    the EQ parameter cluster, avoiding false tag matches in name data."""
    for vo in _records(buf, lo, hi, TAG_EQ_FREQ, 0):
        if 20 <= struct.unpack_from('<f', buf, vo)[0] <= 25000:
            return vo - 0x30, vo + 0x240
    return None

def _lpf_value_offset(buf, lo, hi):
    for vo in _records(buf, lo, hi, TAG_LPF, 1):
        if 20 <= struct.unpack_from('<f', buf, vo)[0] <= 25001:
            return vo
    return None

# ── writers ───────────────────────────────────────────────────────────────────
def _write_rec(data, lo, hi, tag, bidx, value):
    recs = _records(data, lo, hi, tag, bidx)
    if not recs:
        return False
    struct.pack_into('<f', data, recs[0], float(value))
    return True

def write_name(data, fader, new):
    """Replace the surface slot + every current-scene copy. Returns count."""
    old = EXPECTED_NAMES[fader - 1]
    idx = block_index_for_fader(fader)
    lo, hi = _block_bounds(idx)
    nb = new.encode('latin1')
    targets = [_surf_offset(fader)] + _name_copies(data, old, lo, hi)
    for t in targets:
        oldlen = data[t]
        data[t] = len(nb)
        data[t + 1: t + 1 + len(nb)] = nb
        for k in range(t + 1 + len(nb), t + 1 + oldlen):
            data[k] = 0
    return len(targets)

def write_channel(data, fader, bands, hpf=None, lpf=None, deq=None,
                  comp_thr=None):
    """bands: dict {bidx: (gain, freq, q, type)} — only active bands.
    deq: dict {bidx: (thr_db, atk_s, rel_s)}."""
    idx = block_index_for_fader(fader)
    lo, hi = _block_bounds(idx)
    win = _eq_window(data, lo, hi)
    if win is None:
        print(f"    !! fader {fader}: EQ window not found"); return
    w0, w1 = win
    for b, (g, f, q, ty) in bands.items():
        _write_rec(data, w0, w1, TAG_EQ_GAIN, b, g)
        _write_rec(data, w0, w1, TAG_EQ_FREQ, b, f)
        _write_rec(data, w0, w1, TAG_EQ_Q,    b, q)
        _write_rec(data, w0, w1, TAG_EQ_TYPE, b, ty)
    _write_rec(data, w0, w1, TAG_EQ_COUNT, 0, len(bands) if bands else 0)
    for b, (thr, atk, rel) in (deq or {}).items():
        _write_rec(data, w0, w1, TAG_DEQ_EN,  b, 1.0)
        _write_rec(data, w0, w1, TAG_DEQ_THR, b, thr)
        _write_rec(data, w0, w1, TAG_DEQ_ATK, b, atk)
        _write_rec(data, w0, w1, TAG_DEQ_REL, b, rel)
    lpf_vo = _lpf_value_offset(data, lo, hi)
    if lpf_vo is None:
        print(f"    !! fader {fader}: LPF record not found")
    else:
        if WRITE_LPF and lpf is not None:
            stored = OFF_LPF if lpf >= 20000 else lpf * LPF_SCALE
            struct.pack_into('<f', data, lpf_vo, float(stored))
        if WRITE_HPF and hpf is not None:
            hpf_vo = lpf_vo + 0x10
            tagw, = struct.unpack_from('<H', data, hpf_vo + 4)
            if tagw != 0xFFFF:
                print(f"    !! fader {fader}: HPF marker not 0xFFFF — skipped")
            else:
                struct.pack_into('<f', data, hpf_vo, float(hpf) * HPF_SCALE)
    if comp_thr is not None:
        for b in (0, 1, 2):
            for vo in _records(data, lo, hi, TAG_COMP_THR, b):
                if -60.0 <= struct.unpack_from('<f', data, vo)[0] <= 0.0:
                    struct.pack_into('<f', data, vo, float(comp_thr)); break

# ── .md input ─────────────────────────────────────────────────────────────────
_TYPE = {'SHELF': SHELF, 'BELL': BELL}

def read_md(path):
    """Parse a FOH Channel Processing .md (same locked format as FSQ).

    Per channel (B1 = console low band .. B4 = console high band):
        ## Ch N | NAME | MIC
        HPF: x | LPF: y|OFF
        B4: gain | freq | Q | SHELF|BELL  [| DEQ: thr=-16 atk=10ms rel=100ms]
        ...
        B1: FLAT
    Returns {fader: {'name','mic','bands':{bidx:(g,f,q,ty)},
                     'deq':{bidx:(thr,atk_s,rel_s)},'hpf':Hz|None,'lpf':Hz|None}}.
    """
    import re
    out = {}; cur = None
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        m = re.match(r'##\s*Ch\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.*)', line)
        if m:
            cur = int(m.group(1))
            out[cur] = {'name': m.group(2).strip(), 'mic': m.group(3).strip(),
                        'bands': {}, 'deq': {}, 'hpf': None, 'lpf': None}
            continue
        if cur is None:
            continue
        fm = re.match(r'HPF:\s*([\d.]+)\s*\|\s*LPF:\s*(OFF|[\d.]+)', line, re.I)
        if fm:
            out[cur]['hpf'] = float(fm.group(1))
            out[cur]['lpf'] = (20000.0 if fm.group(2).upper() == 'OFF'
                               else float(fm.group(2)))
            continue
        bm = re.match(r'B([1-4]):\s*(.*)', line)
        if bm:
            bidx = BIDX_FOR_BAND[int(bm.group(1))]
            body = bm.group(2).strip()
            if body.upper().startswith('FLAT'):
                continue
            parts = [p.strip() for p in body.split('|')]
            g = float(parts[0]); f = float(parts[1]); q = float(parts[2])
            ty = _TYPE.get(parts[3].upper().split()[0], BELL)
            out[cur]['bands'][bidx] = (g, f, q, ty)
            for p in parts[4:]:
                dm = re.match(r'DEQ:\s*thr=(-?[\d.]+)\s+atk=([\d.]+)ms\s+'
                              r'rel=([\d.]+)ms', p, re.I)
                if dm:
                    out[cur]['deq'][bidx] = (float(dm.group(1)),
                                             float(dm.group(2)) / 1000.0,
                                             float(dm.group(3)) / 1000.0)
    return out

# ── main ──────────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Patch a Memo Q225 .ses from a FOH Channel Processing .md.")
    ap.add_argument('--src',  required=True, help="Memo template .ses "
                    "(master: _TEMPLATE/brian memo june 2026.ses)")
    ap.add_argument('--dest', required=True, help="output .ses (show folder)")
    ap.add_argument('--md',   required=True,
                    help="FOH Channel Processing .md")
    a = ap.parse_args(argv)

    src = open(a.src, 'rb').read()
    assert_template(src)                 # offset tripwire — abort if stale
    data = bytearray(src)

    work = read_md(a.md)
    bad = [ch for ch in work if not (1 <= ch <= N_FADERS)]
    if bad:
        print(f"ERROR: MD channels out of range 1..{N_FADERS}: {bad}")
        return 2

    processed = sorted(work)
    print(f"Source: {os.path.basename(a.src)}  ({len(src):,} bytes)")
    print(f"Processed channels: {processed or 'none'}")
    print(f"Filter writes: HPF x{HPF_SCALE} / LPF x{LPF_SCALE} "
          f"(WRITE_HPF={WRITE_HPF} WRITE_LPF={WRITE_LPF})\n")

    for ch in processed:
        v = work[ch]
        n = write_name(data, ch, v['name'])
        if n < 5:
            print(f"    !! fader {ch}: only {n} name fields written "
                  f"(expected ~20) — output not trustworthy")
        write_channel(data, ch, v['bands'], hpf=v['hpf'], lpf=v['lpf'],
                      deq=v['deq'])
        flags = []
        if v['hpf']: flags.append(f"HPF {v['hpf']:g}")
        if v['lpf'] and v['lpf'] < 20000: flags.append(f"LPF {v['lpf']:g}")
        if v['deq']: flags.append(f"DEQ x{len(v['deq'])}")
        print(f"  f{ch:2d}  {v['name']:<16s} name×{n}  "
              f"EQ:{len(v['bands'])} bands  {' '.join(flags)}")

    assert len(data) == len(src), "size changed"
    open(a.dest, 'wb').write(data)

    ok = verify(src, bytes(data), set(processed))
    print(f"\nWritten -> {a.dest}")
    print("\nNEXT: load on the Q225 and verify before the file is trusted.")
    return 0 if ok else 1

# ── verification ──────────────────────────────────────────────────────────────
def _diff_offsets(src, out):
    """All differing byte offsets, found via fast chunked comparison."""
    CH = 0x10000
    offs = []
    for base in range(0, len(src), CH):
        a, b = src[base:base + CH], out[base:base + CH]
        if a != b:
            offs.extend(base + k for k in range(len(a)) if a[k] != b[k])
    return offs

def verify(src, out, miced):
    print(f"\n{'='*56}\nVerification")
    if len(src) != len(out):
        print("  FAIL size"); return False
    allowed = []
    for ch in miced:
        allowed.append(_block_bounds(block_index_for_fader(ch)))
        o = _surf_offset(ch)
        allowed.append((o, o + SURF_STRIDE))
    def ok_off(k): return any(lo <= k < hi for lo, hi in allowed)
    stray = [k for k in _diff_offsets(src, out) if not ok_off(k)]
    print(f"  bytes changed outside mic'd blocks: {len(stray)}",
          "PASS" if not stray else f"FAIL {[hex(x) for x in stray[:8]]}")
    # do-not-write tags inside the written blocks must be byte-identical
    sigs = {struct.pack('<H', t) for t in DO_NOT_WRITE_TAGS}
    bad = []
    for lo, hi in allowed:
        for i in range(lo, min(hi, len(src) - 7)):
            if src[i + 4:i + 6] in sigs and src[i:i + 4] != out[i:i + 4]:
                bad.append(i)
    print(f"  do-not-write tags modified: {len(bad)}",
          "PASS" if not bad else f"FAIL {[hex(x) for x in bad[:8]]}")
    return not stray and not bad

if __name__ == '__main__':
    sys.exit(main())
