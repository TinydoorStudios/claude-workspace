#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — FOUNTAIN SQUARE (FSQ) template.

This is NOT the Memo patcher. The FSQ session stores channel data in a
different place than Memo, and the previous FSQ files failed on the
console because they wrote to the wrong region. The locations used here
were confirmed by console-save-diff against `brian fsq start.ses`
(see the SOP notes). Do not copy Memo constants into this file.

WHAT IS CONFIRMED (reproduces a real DiGiCo offline/console save)
-----------------------------------------------------------------
  - Fader display NAME   : surface-label slot + every copy in the
                           channel's current-scene block (~20 copies).
                           Writing only some copies does NOT stick.
  - EQ gain / freq / Q / type : tags 0x0403 / 0x0406 / 0x0407 / 0x040b,
                           bidx 0..3, inside the current-scene block.
                           bidx 0 = HIGHEST band (console Band 4),
                           bidx 3 = LOWEST band (console Band 1).
                           Template defaults 6300/1600/300/100 Hz and the
                           2026-06-10 save-diff both confirm this order.
  - EQ band count        : tag 0x0405 bidx 0.
  - DEQ per band         : enable 0x040e, thresh 0x0411 (dB),
                           attack 0x0412 (s), release 0x0410 (s) — all at
                           the band's bidx. Confirmed by 2026-06-10 diff.
  - HPF                  : float at LPF value offset + 0x10 (record tag
                           reads 0xFFFF). STORED = 0.8 x displayed Hz
                           (display 84.1 -> stored 67.24; display 20 ->
                           stored 16.0). Confirmed 2026-06-10.
  - LPF                  : tag 0x0703 bidx 1. STORED = 1.25 x displayed
                           Hz (display 5.75k -> stored 7191; "off"/20 kHz
                           -> stored 25000). Confirmed 2026-06-10.
  - Comp threshold       : tag 0x050f (dB) — bidx 0..2 are the three
                           (multiband-linked) comp threshold slots.
                           Gate enable: 0x050e bidx 3 (gate thresh is
                           0x050f bidx 3 — untested, leave alone).

CALIBRATION SOURCE: klaud edited.ses vs brian fsq start.ses
(DiGiCo offline software, ch 6 "Digico", 2026-06-10). Keep both in
~/.wine/drive_c/Projects/ as the reference pair.

WORKFLOW
--------
  1. Preferred input is the show's FOH Channel Processing .md (--md).
     B-numbers in the .md are CONSOLE band numbers: B1 = lowest,
     B4 = highest (locked convention, corrected 2026-05-30). The patcher
     maps B1->bidx3 ... B4->bidx0. Older MDs (pre-2026-05-30) numbered
     bands the other way — do not feed those in unconverted.
  2. Channels with a mic in the Patch Master Sheet -> fully processed
     here AND listed in the paperwork.
  3. Channels with an EMPTY mic column -> left 100% untouched in the
     .ses (passthrough) and excluded from the paperwork.
  4. Run:  python3 apply_<show>.py --src "brian fsq start.ses" \
                                   --dest "<show folder>/<Show>.ses" \
                                   --md  "<Show> - FOH Channel Processing.md"
  5. The verification block must print PASS before the file goes to USB.
"""

import argparse, os, struct, sys, math

# ── confirmed FSQ layout constants ───────────────────────────────────────────
SURF_BASE   = 0xA287A      # fader 1 surface-label slot
SURF_STRIDE = 125          # bytes per fader in the surface-label table
SCAN_LO     = 0x1A1000     # current-scene channel-block region (start)
SCAN_HI     = 0x1CC000     # current-scene channel-block region (end)

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

# Filter value encoding (confirmed 2026-06-10 by offline-editor save-diff):
# the file stores HPF at 0.8x the displayed frequency and LPF at 1.25x.
HPF_SCALE = 0.8
LPF_SCALE = 1.25
WRITE_HPF = True
WRITE_LPF = True

SHELF, BELL = 1.0, 2.0
OFF_LPF     = 25000.0      # stored "no LPF" value (= 20 kHz display x 1.25)

# .md band number (console: B1 = low .. B4 = high) -> file bidx (0 = high)
BIDX_FOR_BAND = {1: 3, 2: 2, 3: 1, 4: 0}

# ── low-level helpers ─────────────────────────────────────────────────────────
def _surf_name(buf, fader):
    o = SURF_BASE + (fader - 1) * SURF_STRIDE
    return o, buf[o + 1: o + 1 + buf[o]].decode('latin1')

def _name_copies(buf, old):
    """All current-scene name-field offsets (len byte) for `old`."""
    ob = old.encode('latin1'); hits = []; i = SCAN_LO
    while i < SCAN_HI:
        j = buf.find(ob, i)
        if j < 0:
            break
        if buf[j - 1] == len(ob) and buf[j + len(ob)] == 0:
            hits.append(j - 1)          # store length-byte offset
        i = j + 1
    return hits

def _block_bounds(buf, fader):
    o, old = _surf_name(buf, fader)
    hits = _name_copies(buf, old)
    if not hits:
        return None
    return min(hits) - 0x60, max(hits) + 0x60

def _records(buf, lo, hi, tag, bidx):
    """Value-offsets of every TLV record with tag/bidx in [lo, hi)."""
    sig = struct.pack('<HH', tag, bidx); out = []; i = lo
    while True:
        j = buf.find(sig, i, hi)
        if j < 0:
            break
        out.append(j - 4)               # value is 4 bytes before the tag
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
    """Offset of the sane-valued LPF record's float in this block."""
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
    o, old = _surf_name(data, fader)
    nb = new.encode('latin1')
    targets = _name_copies(data, old)               # length-byte offsets
    if o not in targets:
        targets = [o] + targets
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
    lo, hi = _block_bounds(data, fader)
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
    # Comp threshold (optional) — the three linked multiband slots
    if comp_thr is not None:
        for b in (0, 1, 2):
            for vo in _records(data, lo, hi, TAG_COMP_THR, b):
                if -60.0 <= struct.unpack_from('<f', data, vo)[0] <= 0.0:
                    struct.pack_into('<f', data, vo, float(comp_thr)); break

# ── inputs ────────────────────────────────────────────────────────────────────
def read_sheet(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, data_only=True)['Sheet1']
    rows = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        ch, name, mic = r[0], r[1], r[2]
        if ch is None:
            continue
        rows[int(ch)] = {'name': (name or '').strip(),
                         'mic': (str(mic).strip() if mic else '')}
    return rows

_TYPE = {'SHELF': SHELF, 'BELL': BELL}

def read_md(path):
    """Parse a FOH Channel Processing .md.

    Format per channel (B1 = console low band .. B4 = console high band;
    line order in the file doesn't matter):
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
        description="Patch an FSQ Q225 .ses from a FOH Channel Processing .md.")
    ap.add_argument('--src',   required=True, help="FSQ template .ses")
    ap.add_argument('--dest',  required=True, help="output .ses (show folder)")
    ap.add_argument('--md',    help="FOH Channel Processing .md (preferred input)")
    ap.add_argument('--sheet', help="Patch Master Sheet .xlsx (names only)")
    a = ap.parse_args(argv)
    if not (a.md or a.sheet):
        print("ERROR: provide --md (preferred) or --sheet"); return 2

    src = open(a.src, 'rb').read()
    data = bytearray(src)

    if a.md:
        work = read_md(a.md)
    else:
        sheet = read_sheet(a.sheet)
        work = {ch: {'name': v['name'], 'mic': v['mic'], 'bands': {},
                     'deq': {}, 'hpf': None, 'lpf': None}
                for ch, v in sheet.items() if v['mic']}

    processed = sorted(work)
    print(f"Source: {os.path.basename(a.src)}  ({len(src):,} bytes)")
    print(f"Processed channels: {processed or 'none'}")
    print(f"Filter writes: HPF x{HPF_SCALE} / LPF x{LPF_SCALE} "
          f"(WRITE_HPF={WRITE_HPF} WRITE_LPF={WRITE_LPF})\n")

    for ch in processed:
        v = work[ch]
        n = write_name(data, ch, v['name'])
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
    print(f"\nPaperwork channels (mic'd, for the show packet): {processed}")
    print(f"Written -> {a.dest}")
    print("\nNEXT: load on the Q225 and verify before the file is trusted.")
    return 0 if ok else 1

# ── verification ──────────────────────────────────────────────────────────────
def verify(src, out, miced):
    print(f"\n{'='*56}\nVerification")
    if len(src) != len(out):
        print("  FAIL size"); return False
    # every byte change must fall inside a mic'd fader's current-scene block
    # or its surface slot
    allowed = []
    for ch in miced:
        b = _block_bounds(bytearray(src), ch)
        if b: allowed.append(b)
        o = SURF_BASE + (ch - 1) * SURF_STRIDE
        allowed.append((o, o + SURF_STRIDE))
    def ok_off(k): return any(lo <= k < hi for lo, hi in allowed)
    stray = [k for k in range(len(src)) if src[k] != out[k] and not ok_off(k)]
    print(f"  bytes changed outside mic'd blocks: {len(stray)}",
          "PASS" if not stray else f"FAIL {[hex(x) for x in stray[:8]]}")
    return not stray

if __name__ == '__main__':
    sys.exit(main())
