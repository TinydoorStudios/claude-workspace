#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — FOUNTAIN SQUARE (FSQ) template.

This is NOT the Memo patcher. The FSQ session stores channel data in a
different place than Memo, and the previous FSQ files failed on the
console because they wrote to the wrong region. The locations used here
were confirmed by console-save-diff against `brian fsq start.ses`
(see the SOP notes). Do not copy Memo constants into this file.

TEMPLATE REVISION — 2026-06-21
------------------------------
Recalibrated for the NEW FSQ template (`brian fsq start.ses`,
3,779,766 bytes). The previous template was 2,466,215 bytes; the resave
("everything changed") shifted every absolute offset. Re-derived by
save-diff of `brian fsq start.ses` vs `fsq edited new.ses`
(ch1 -> ZZTOP1 with known EQ/HPF/LPF/DEQ, ch2 -> ZZTOP2), kept in
~/.wine/drive_c/Projects/. The 2026-06-21 diff re-confirmed, on THIS
file, every semantic below: bidx order (b0 = high band), HPF x0.8,
LPF x1.25, DEQ tags, comp slots. Old constants for reference:
SURF_BASE 0xA287A, SCAN 0x1A1000..0x1CC000.

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
                           2026-06-21 save-diff both confirm this order.
  - EQ band count        : tag 0x0405 bidx 0.
  - DEQ per band         : enable 0x040e, thresh 0x0411 (dB),
                           attack 0x0412 (s), release 0x0410 (s) — all at
                           the band's bidx. Confirmed by 2026-06-21 diff.
  - HPF                  : float at LPF value offset + 0x10 (record tag
                           reads 0xFFFF). STORED = 0.8 x displayed Hz
                           (display 100 -> stored 79.1; display 20 ->
                           stored 16.0). Confirmed 2026-06-21.
  - LPF                  : tag 0x0703 bidx 1. STORED = 1.25 x displayed
                           Hz (display 8k -> stored 9953; "off"/20 kHz
                           -> stored 25000). Confirmed 2026-06-21.
  - Comp threshold       : tag 0x050f (dB) — bidx 0..2 are the three
                           (multiband-linked) comp threshold slots.
                           Gate enable: 0x050e bidx 3 (gate thresh is
                           0x050f bidx 3 — untested, leave alone).

CALIBRATION SOURCE: brian fsq start.ses vs fsq edited new.ses
(DiGiCo offline software, ch1/ch2, 2026-06-21). Keep both in
~/.wine/drive_c/Projects/ as the reference pair.

SAFETY GATE
-----------
On load, the patcher reads the 64 fader names at SURF_BASE and compares
them to EXPECTED_NAMES (this template's known channel list). A mismatch
means the offsets are stale (the template was resaved again) or the
wrong .ses was passed as --src — the patcher ABORTS rather than writing
to the wrong region (the exact silent failure that broke earlier FSQ
builds). To recalibrate after a future resave, repeat the save-diff
above and update SURF_BASE / SCAN_LO / SCAN_HI / EXPECTED_NAMES.

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

# ── confirmed FSQ layout constants (NEW template, 2026-06-21) ─────────────────
SURF_BASE   = 0xA5571      # fader 1 surface-label slot (length byte)
SURF_STRIDE = 125          # bytes per fader in the surface-label table
SCAN_LO     = 0x2D3000     # current-scene channel-block region (start)
SCAN_HI     = 0x33F000     # current-scene channel-block region (end)
N_FADERS    = 64
MAX_BLOCK_SPAN = 0x4000    # a sane channel block is ~0x1680; anything wider
                           # means a non-unique name (FX returns) — skip it

# Known channel list for the new template — the offset tripwire (see SAFETY GATE)
EXPECTED_NAMES = [
    'Kick In', 'Kick Out', 'Snare Top', 'Snare Bottom', 'Hat', 'Rack 1',
    'Rack 2', 'Floor', 'Overheads', 'SNARE PL8', 'Bass DI', 'Bass Mic',
    'Guitar 1', 'Guitar 2', 'Guitar 3', 'Guitar 4', 'Misc 1', 'Misc 2',
    'Misc 3', 'Misc 4', 'Misc 5', 'Misc 6', 'Misc 7', 'Misc 8', 'Vocal 1',
    'Vocal 2', 'Vocal 3', 'Vocal 4', 'Vocal 5', 'Vocal 6', 'Vocal 7',
    'Vocal 8', 'Wireless 1', 'Wireless 2', 'Wireless 3', 'Wireless 4',
    'Hall', 'Plate', 'Room', 'Delay', 'Bricasti 1', 'Bricasti 2',
    'Bricasti 3', 'Bricasti 4', 'Ch 45', 'Ch 46', 'Ch 47', 'Ch 48', 'Ch 49',
    'Ch 50', 'Ch 51', 'Ch 52', 'Ch 53', 'Ch 54', 'Ch 55', 'Ch 56', 'Ch 57',
    'Ch 58', 'Mon 2 FOH', 'RTA', 'Hotshot 2 FOH', 'Tech Feed', 'Crowd',
    'Pandora',
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

# Filter value encoding (confirmed 2026-06-21 by offline-editor save-diff):
# the file stores HPF at 0.8x the displayed frequency and LPF at 1.25x.
HPF_SCALE = 0.8
LPF_SCALE = 1.25
WRITE_HPF = True
WRITE_LPF = True

SHELF, BELL = 1.0, 2.0
OFF_LPF     = 25000.0      # stored "no LPF" value (= 20 kHz display x 1.25)

# .md band number (console: B1 = low .. B4 = high) -> file bidx (0 = high)
BIDX_FOR_BAND = {1: 3, 2: 2, 3: 1, 4: 0}

# ── safety gate ───────────────────────────────────────────────────────────────
def _read_surf_name(buf, fader):
    # Surface-table names are length-prefixed but NOT null-terminated — the
    # byte after the name is the next per-fader field. Validate length +
    # printable only.
    o = SURF_BASE + (fader - 1) * SURF_STRIDE
    if o + 1 >= len(buf):
        return o, None
    ln = buf[o]
    if not (1 <= ln <= 24):
        return o, None
    s = buf[o + 1: o + 1 + ln]
    if any(not (32 <= c < 127) for c in s):
        return o, None
    return o, s.decode('latin1')

def assert_template(buf):
    """Abort unless the surface table matches the calibrated template."""
    got = [_read_surf_name(buf, f)[1] for f in range(1, N_FADERS + 1)]
    if got != EXPECTED_NAMES:
        sys.stderr.write(
            "ABORT: --src does not match the calibrated FSQ template.\n"
            "The fader names at SURF_BASE differ from EXPECTED_NAMES, so the\n"
            "byte offsets are stale (template resaved) or this is the wrong\n"
            ".ses. Patching would write to the wrong region. Recalibrate via\n"
            "a save-diff and update SURF_BASE/SCAN_LO/SCAN_HI/EXPECTED_NAMES.\n")
        first = next((i + 1 for i, (a, b) in enumerate(zip(got, EXPECTED_NAMES))
                      if a != b), None)
        if first:
            sys.stderr.write(
                f"  first mismatch at fader {first}: "
                f"got {got[first-1]!r}, expected {EXPECTED_NAMES[first-1]!r}\n")
        sys.exit(3)

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
    lo, hi = min(hits) - 0x60, max(hits) + 0x60
    if hi - lo > MAX_BLOCK_SPAN:        # non-unique name (e.g. FX return) —
        return None                    # refuse rather than write wild
    return lo, hi

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
    bb = _block_bounds(data, fader)
    if bb is None:
        print(f"    !! fader {fader}: block not found / name not unique — skipped")
        return
    lo, hi = bb
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
    assert_template(src)                 # offset tripwire — abort if stale
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
