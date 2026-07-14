#!/usr/bin/env python3
"""
DiGiCo Q225 .ses patch engine — SHARED by the Memo and FSQ pipelines.

One engine, two venue calibrations. The venue patchers
(`Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py` and
`Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py`) are thin
wrappers holding only their template's calibration dict; every byte-level
decision lives here, once. Factored 2026-07-01 from the two standalone
patchers after they converged on the same console-save layout — regression:
both venues produce md5-identical output to their pre-factor standalones.

Both templates are full console saves: a surface-label table (stride 125)
plus current-scene channel blocks (~5.5 KB, ~19-20 name copies each). Two
block-location modes, per calibration:
  - "scan"       (FSQ): each fader's block is found by searching its
                 template name inside SCAN_LO..SCAN_HI; bounds are
                 min(hits)-0x60 .. max(hits)+0x60, guarded by max_span.
  - "positional" (Memo): blocks are contiguous at base + i*stride; blocks
                 are matched to faders BY NAME (block order != fader order).

CONFIRMED SEMANTICS (console-save-diff 2026-06-10 / 2026-06-21, re-confirmed
on the 2026-07-01 Memo template):
  - NAME: surface slot + every current-scene copy; partial writes don't stick.
  - EQ gain/freq/Q/type: tags 0x0403/0x0406/0x0407/0x040B; bidx 0 = HIGHEST
    band (console Band 4) .. bidx 3 = LOWEST (Band 1). MD B-numbers are
    console bands (B1 = low), so B1->bidx3 .. B4->bidx0.
  - Band count: 0x0405 bidx 0. DEQ: en 0x040E, thr 0x0411 (dB),
    atk 0x0412 (s), rel 0x0410 (s).
  - LPF: tag 0x0703 bidx 1, stored = 1.25 x display Hz (off = 25000).
  - HPF: float at LPF value offset + 0x10 under a 0xFFFF tag,
    stored = 0.8 x display Hz.
  - Comp threshold 0x050F bidx 0..2 (multiband-linked); gate enable 0x050E
    bidx 3 — mapped, never written.

EVERY RUN, IN ORDER (any failure = no delivery):
  1. md_lint on the input MD (errors abort — catches backwards band order,
     malformed lines, console-limit violations)
  2. offset tripwire (surface names — and block names in positional mode —
     must match the calibration; abort otherwise)
  3. patch
  4. verify: size unchanged, 0 bytes changed outside written blocks,
     do-not-write (Mustard) tags byte-identical
  5. full readback: EVERY MD channel re-read from the output file and
     compared to the MD (names, all bands, HPF/LPF scaling, DEQ)
Then the human gate: Brian loads it on the Q225 and says "verified".
"""

import argparse, os, struct, sys

TAG_EQ_GAIN  = 0x0403
TAG_EQ_FREQ  = 0x0406
TAG_EQ_Q     = 0x0407
TAG_EQ_TYPE  = 0x040B      # 1.0 = shelf, 2.0 = bell
TAG_EQ_COUNT = 0x0405      # bidx 0: number of active EQ bands
TAG_DEQ_EN   = 0x040E
TAG_DEQ_THR  = 0x0411      # dB
TAG_DEQ_ATK  = 0x0412      # seconds
TAG_DEQ_REL  = 0x0410      # seconds
TAG_LPF      = 0x0703      # bidx 1
TAG_COMP_THR = 0x050F      # bidx 0..2

# Mustard + Mustard-suspect + known-dangerous — must never change.
DO_NOT_WRITE_TAGS = (
    0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
    0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
    0x0503, 0x050E, 0x0511, 0x08E1, 0x08E8, 0x0EE8, 0x0EFE, 0x1D47,
)

HPF_SCALE = 0.8
LPF_SCALE = 1.25
SHELF, BELL = 1.0, 2.0
OFF_LPF = 25000.0          # stored "no LPF" (= 20 kHz display x 1.25)

# .md band number (console: B1 = low .. B4 = high) -> file bidx (0 = high)
BIDX_FOR_BAND = {1: 3, 2: 2, 3: 1, 4: 0}


# ── calibration access ────────────────────────────────────────────────────────
def _surf_offset(cal, fader):
    return cal['surf_base'] + (fader - 1) * cal['surf_stride']


def _read_lp_name(buf, o, maxlen=24):
    """Length-prefixed printable name at offset o, or None."""
    if o + 1 >= len(buf):
        return None
    ln = buf[o]
    if not (1 <= ln <= maxlen):
        return None
    s = buf[o + 1: o + 1 + ln]
    if len(s) < ln or any(not (32 <= c < 127) for c in s):
        return None
    return s.decode('latin1')


def assert_template(cal, buf):
    """Offset tripwire — abort unless the file matches the calibration."""
    tsize = cal.get('template_size')
    if tsize and len(buf) != tsize:
        sys.stderr.write(
            f"ABORT: --src is {len(buf):,} bytes; the calibrated "
            f"{cal['venue']} template is {tsize:,}. Wrong file or the "
            "template was resaved — recalibrate before patching.\n")
        sys.exit(3)
    got = [_read_lp_name(buf, _surf_offset(cal, f))
           for f in range(1, cal['n_faders'] + 1)]
    checks = [(got, cal['expected_names'], 'surface table')]
    if cal['block_mode'] == 'positional':
        blk = [_read_lp_name(buf, cal['block_base'] + i * cal['block_stride'])
               for i in range(cal['n_faders'])]
        checks.append((blk, cal['expected_block_names'], 'block walk'))
    for g, want, what in checks:
        if g != want:
            first = next((i for i, (a, b) in enumerate(zip(g, want))
                          if a != b), None)
            sys.stderr.write(
                f"ABORT: {what} does not match the calibrated "
                f"{cal['venue']} template (resaved template, or wrong "
                "--src). Patching would write to the wrong region.\n"
                "Recalibrate the venue patcher's constants + name lists,\n"
                "then console-verify a test build.\n")
            if first is not None:
                sys.stderr.write(f"  first mismatch at entry {first + 1}: "
                                 f"got {g[first]!r}, "
                                 f"expected {want[first]!r}\n")
            sys.exit(3)


# ── block location ────────────────────────────────────────────────────────────
def _name_copies(buf, old, lo, hi):
    """Validated name-field offsets (len byte) for `old` in [lo, hi)."""
    ob = old.encode('latin1'); hits = []; i = lo
    while i < hi:
        j = buf.find(ob, i, hi)
        if j < 0:
            break
        if j > 0 and buf[j - 1] == len(ob) and buf[j + len(ob)] == 0:
            hits.append(j - 1)
        i = j + 1
    return hits


def block_bounds(cal, buf, fader):
    """(lo, hi) of the fader's current-scene block, or None."""
    old = cal['expected_names'][fader - 1]
    if cal['block_mode'] == 'positional':
        idx = cal['expected_block_names'].index(old)
        first = cal['block_base'] + idx * cal['block_stride']
        return first - cal['block_pre'], first + cal['block_span']
    # scan mode
    hits = _name_copies(buf, old, cal['scan_lo'], cal['scan_hi'])
    if not hits:
        return None
    lo, hi = min(hits) - 0x60, max(hits) + 0x60
    if hi - lo > cal['max_block_span']:   # non-unique name — refuse
        return None
    return lo, hi


# ── TLV helpers ───────────────────────────────────────────────────────────────
def _records(buf, lo, hi, tag, bidx):
    sig = struct.pack('<HH', tag, bidx); out = []; i = lo
    while True:
        j = buf.find(sig, i, hi)
        if j < 0:
            break
        out.append(j - 4)               # value is 4 bytes before the tag
        i = j + 1
    return out


def _eq_window(buf, lo, hi):
    """Anchor on the high band's freq (only sane 20..25000 value)."""
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


def write_name(cal, data, fader, new, bb):
    """Replace surface slot + every current-scene copy. Returns count.
    `bb` = block bounds resolved from the PRISTINE source (before renames)."""
    old = cal['expected_names'][fader - 1]
    copies = _name_copies(data, old, *bb) if bb else []
    surf = _surf_offset(cal, fader)
    targets = ([surf] if surf not in copies else []) + copies
    nb = new.encode('latin1')
    for t in targets:
        oldlen = data[t]
        data[t] = len(nb)
        data[t + 1: t + 1 + len(nb)] = nb
        for k in range(t + 1 + len(nb), t + 1 + oldlen):
            data[k] = 0
    return len(targets)


def write_channel(cal, data, fader, bands, hpf=None, lpf=None, deq=None,
                  comp_thr=None, bb=None):
    """bands: {bidx: (gain, freq, q, type)}; deq: {bidx: (thr, atk_s, rel_s)}.
    `bb` = block bounds resolved from the PRISTINE source (before renames)."""
    if bb is None:
        print(f"    !! fader {fader}: block not found / name not unique — skipped")
        return False
    lo, hi = bb
    win = _eq_window(data, lo, hi)
    if win is None:
        print(f"    !! fader {fader}: EQ window not found"); return False
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
        if lpf is not None:
            stored = OFF_LPF if lpf >= 20000 else lpf * LPF_SCALE
            struct.pack_into('<f', data, lpf_vo, float(stored))
        if hpf is not None:
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
    return True


# ── inputs ────────────────────────────────────────────────────────────────────
_TYPE = {'SHELF': SHELF, 'BELL': BELL}


def read_md(path):
    """Parse a FOH Channel Processing .md (locked format; B1 = console low).

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


def read_sheet(path):
    """Patch Master Sheet .xlsx — names only (FSQ fallback input)."""
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


# ── verification ──────────────────────────────────────────────────────────────
def _diff_offsets(src, out):
    """All differing byte offsets via fast chunked comparison."""
    CH = 0x10000
    offs = []
    for base in range(0, len(src), CH):
        a, b = src[base:base + CH], out[base:base + CH]
        if a != b:
            offs.extend(base + k for k in range(len(a)) if a[k] != b[k])
    return offs


def verify(cal, src, out, processed, bounds):
    print(f"\n{'='*56}\nVerification")
    if len(src) != len(out):
        print("  FAIL size"); return False
    allowed = []
    for ch in processed:
        bb = bounds.get(ch)
        if bb:
            allowed.append(bb)
        o = _surf_offset(cal, ch)
        allowed.append((o, o + cal['surf_stride']))
    def ok_off(k): return any(lo <= k < hi for lo, hi in allowed)
    stray = [k for k in _diff_offsets(src, out) if not ok_off(k)]
    print(f"  bytes changed outside mic'd blocks: {len(stray)}",
          "PASS" if not stray else f"FAIL {[hex(x) for x in stray[:8]]}")
    sigs = {struct.pack('<H', t) for t in DO_NOT_WRITE_TAGS}
    bad = []
    for lo, hi in allowed:
        for i in range(max(lo, 0), min(hi, len(src) - 7)):
            if src[i + 4:i + 6] in sigs and src[i:i + 4] != out[i:i + 4]:
                bad.append(i)
    print(f"  do-not-write tags modified: {len(bad)}",
          "PASS" if not bad else f"FAIL {[hex(x) for x in bad[:8]]}")
    return not stray and not bad


def readback(cal, out_bytes, work):
    """Re-read EVERY MD channel from the output and compare to the MD."""
    print(f"\nReadback (every MD channel vs the output file)")
    all_ok = True
    for ch in sorted(work):
        v = work[ch]
        problems = []
        surf = _read_lp_name(out_bytes, _surf_offset(cal, ch))
        if surf != v['name']:
            problems.append(f"surface name {surf!r} != {v['name']!r}")
        bb = block_bounds_out(cal, out_bytes, ch, v['name'])
        if bb is None:
            problems.append("block not found in output")
        else:
            lo, hi = bb
            copies = _name_copies(out_bytes, v['name'], lo, hi)
            if len(copies) < 5:
                problems.append(f"only {len(copies)} name copies")
            win = _eq_window(out_bytes, lo, hi)
            if win is None:
                problems.append("EQ window not found")
            else:
                w0, w1 = win
                for b, (g, f, q, ty) in v['bands'].items():
                    for tag, want, lbl in ((TAG_EQ_GAIN, g, 'gain'),
                                           (TAG_EQ_FREQ, f, 'freq'),
                                           (TAG_EQ_Q, q, 'Q'),
                                           (TAG_EQ_TYPE, ty, 'type')):
                        r = _records(out_bytes, w0, w1, tag, b)
                        got = (struct.unpack_from('<f', out_bytes, r[0])[0]
                               if r else None)
                        if got is None or abs(got - want) > 0.01:
                            problems.append(f"bidx{b} {lbl}: {got} != {want}")
                for b, (thr, atk, rel) in v['deq'].items():
                    for tag, want, lbl in ((TAG_DEQ_EN, 1.0, 'deq_en'),
                                           (TAG_DEQ_THR, thr, 'deq_thr'),
                                           (TAG_DEQ_ATK, atk, 'deq_atk'),
                                           (TAG_DEQ_REL, rel, 'deq_rel')):
                        r = _records(out_bytes, w0, w1, tag, b)
                        got = (struct.unpack_from('<f', out_bytes, r[0])[0]
                               if r else None)
                        if got is None or abs(got - want) > 0.001:
                            problems.append(f"bidx{b} {lbl}: {got} != {want}")
            lpf_vo = _lpf_value_offset(out_bytes, lo, hi)
            if lpf_vo is None:
                problems.append("LPF record not found")
            else:
                if v['lpf'] is not None:
                    want = (OFF_LPF if v['lpf'] >= 20000
                            else v['lpf'] * LPF_SCALE)
                    got = struct.unpack_from('<f', out_bytes, lpf_vo)[0]
                    if abs(got - want) > 0.01:
                        problems.append(f"LPF stored {got:.1f} != {want:.1f}")
                if v['hpf'] is not None:
                    got = struct.unpack_from('<f', out_bytes, lpf_vo + 0x10)[0]
                    want = v['hpf'] * HPF_SCALE
                    if abs(got - want) > 0.01:
                        problems.append(f"HPF stored {got:.2f} != {want:.2f}")
        status = "OK" if not problems else "FAIL: " + "; ".join(problems[:4])
        print(f"  f{ch:2d} {v['name']:<16s} {status}")
        all_ok &= not problems
    print(f"  readback: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


def block_bounds_out(cal, out_bytes, fader, new_name):
    """Block bounds in the OUTPUT file (names already replaced)."""
    if cal['block_mode'] == 'positional':
        old = cal['expected_names'][fader - 1]
        idx = cal['expected_block_names'].index(old)
        first = cal['block_base'] + idx * cal['block_stride']
        return first - cal['block_pre'], first + cal['block_span']
    hits = _name_copies(out_bytes, new_name, cal['scan_lo'], cal['scan_hi'])
    if not hits:
        return None
    lo, hi = min(hits) - 0x60, max(hits) + 0x60
    if hi - lo > cal['max_block_span']:
        return None
    return lo, hi


# ── main ──────────────────────────────────────────────────────────────────────
def main_cli(cal, argv=None):
    ap = argparse.ArgumentParser(
        description=f"Patch a {cal['venue']} Q225 .ses from a FOH Channel "
                    "Processing .md.")
    ap.add_argument('--src',   required=True, help="venue template .ses")
    ap.add_argument('--dest',  required=True, help="output .ses (show folder)")
    ap.add_argument('--md',    help="FOH Channel Processing .md (preferred)")
    ap.add_argument('--sheet', help="Patch Master Sheet .xlsx (names only)")
    a = ap.parse_args(argv)
    if not (a.md or a.sheet):
        print("ERROR: provide --md (preferred) or --sheet"); return 2

    # 1. lint (hard gate)
    if a.md:
        try:
            import md_lint
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import md_lint
        errors, warnings = md_lint.lint(a.md, max_ch=cal['n_faders'])
        for w in warnings:
            print(f"  lint warn: {w}")
        if errors:
            for e in errors:
                print(f"  lint ERROR: {e}")
            print("\nABORT: the MD failed lint — fix it before patching.")
            return 2

    src = open(a.src, 'rb').read()
    assert_template(cal, src)            # 2. offset tripwire
    data = bytearray(src)

    if a.md:
        work = read_md(a.md)
    else:
        sheet = read_sheet(a.sheet)
        work = {ch: {'name': v['name'], 'mic': v['mic'], 'bands': {},
                     'deq': {}, 'hpf': None, 'lpf': None}
                for ch, v in sheet.items() if v['mic']}

    bad = [ch for ch in work if not (1 <= ch <= cal['n_faders'])]
    if bad:
        print(f"ERROR: MD channels out of range 1..{cal['n_faders']}: {bad}")
        return 2

    # Protected faders (venue calibration): template channels that must never
    # be patched (FX returns living in the input range, e.g. FSQ fader 10 =
    # SNARE PL8). Hard abort — fix the MD / input-list mapping instead.
    hit = [ch for ch in work if ch in cal.get('protected', {})]
    if hit:
        for ch in hit:
            print(f"ERROR: Ch {ch} is PROTECTED on the {cal['venue']} "
                  f"template — {cal['protected'][ch]}")
        print("ABORT: remap those inputs to free faders; nothing written.")
        return 2

    processed = sorted(work)
    print(f"Source: {os.path.basename(a.src)}  ({len(src):,} bytes)")
    print(f"Venue:  {cal['venue']}   Processed channels: {processed or 'none'}")
    print(f"Filter writes: HPF x{HPF_SCALE} / LPF x{LPF_SCALE}\n")

    # Resolve every block from the pristine source BEFORE any rename —
    # in scan mode the blocks are found by the template names.
    bounds = {ch: block_bounds(cal, src, ch) for ch in processed}

    for ch in processed:                 # 3. patch
        v = work[ch]
        n = write_name(cal, data, ch, v['name'], bounds[ch])
        if n < 5:
            print(f"    !! fader {ch}: only {n} name fields written "
                  f"(expected ~20) — output not trustworthy")
        write_channel(cal, data, ch, v['bands'], hpf=v['hpf'], lpf=v['lpf'],
                      deq=v['deq'], bb=bounds[ch])
        flags = []
        if v['hpf']: flags.append(f"HPF {v['hpf']:g}")
        if v['lpf'] and v['lpf'] < 20000: flags.append(f"LPF {v['lpf']:g}")
        if v['deq']: flags.append(f"DEQ x{len(v['deq'])}")
        print(f"  f{ch:2d}  {v['name']:<16s} name×{n}  "
              f"EQ:{len(v['bands'])} bands  {' '.join(flags)}")

    assert len(data) == len(src), "size changed"
    out_bytes = bytes(data)
    open(a.dest, 'wb').write(out_bytes)

    ok = verify(cal, src, out_bytes, processed, bounds)    # 4. verify
    ok &= readback(cal, out_bytes, work)                   # 5. readback
    print(f"\nWritten -> {a.dest}")
    print("\nNEXT: load on the Q225 and verify before the file is trusted.")
    return 0 if ok else 1
