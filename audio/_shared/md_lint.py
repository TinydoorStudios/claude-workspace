#!/usr/bin/env python3
"""
FOH Channel Processing .md lint — the locked MD format, enforced as code.

Used two ways:
  - imported by q225_ses_engine (every patch run lints first; errors abort)
  - standalone:  python3 md_lint.py "<Show> - FOH Channel Processing.md"

Locked format (B1 = console LOW band .. B4 = HIGH, since 2026-05-30):
    ## Ch N | NAME | MIC
    HPF: x | LPF: y|OFF
    B4: gain | freq | Q | SHELF|BELL  [| DEQ: thr=-16 atk=10ms rel=100ms]
    ...
    B1: FLAT
    [COMP: <model> | in|out | thr=.. ratio=.. atk=..ms rel=..ms ...]   (optional)
    [GATE: Gate|Duck|MSE | in|out | thr=.. atk=..ms hold=..ms rel=..ms range=..]

Mustard (COMP:/GATE:) is opt-in per channel and validated by the engine's own
_parse_comp / _parse_gate — the same code the patcher runs — so lint and the
build agree on what's legal (model names, model-specific fields, unit forms).

ERRORS (abort the build — the file is wrong or pre-2026-05-30):
  - no channels found / duplicate channel numbers
  - channel number outside 1..max_ch (when max_ch given)
  - missing HPF/LPF line for a channel
  - malformed band line (can't parse gain|freq|Q|type)
  - band order backwards: a LOWER band number carrying a HIGHER frequency
    than a higher band number (the old backwards numbering — do not patch)
  - freq outside 20..20000, gain outside ±18 (console limits)
  - "DEQ" present on a band line but the clause doesn't parse (it would be
    silently dropped by the patcher otherwise)
  - duplicate band line for the same band in one channel

WARNINGS (printed, don't abort):
  - console name longer than 12 characters (fader legibility)
  - fractional-dB gain (house rule is whole dB)
  - Q outside 0.3..20
  - HPF above 2000 Hz / LPF below 1000 Hz (suspicious)
  - unrecognized non-blank line inside a channel block (typo catcher)
"""
import re, sys

_CH   = re.compile(r'##\s*Ch\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.*)')
_FILT = re.compile(r'HPF:\s*([\d.]+)\s*\|\s*LPF:\s*(OFF|[\d.]+)\s*$', re.I)
_BAND = re.compile(r'B([1-4]):\s*(.*)')
_DEQ  = re.compile(r'DEQ:\s*thr=(-?[\d.]+)\s+atk=([\d.]+)ms\s+rel=([\d.]+)ms',
                   re.I)


def lint(path, max_ch=None):
    """Return (errors, warnings) — lists of human-readable strings."""
    errors, warnings = [], []
    cur = None                      # current channel number
    chans = {}                      # ch -> {'name','has_filt',bands:{n:freq}}
    for lineno, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.strip()
        m = _CH.match(line)
        if m:
            ch = int(m.group(1)); name = m.group(2).strip()
            if ch in chans:
                errors.append(f"line {lineno}: duplicate channel Ch {ch}")
            if max_ch and not (1 <= ch <= max_ch):
                errors.append(f"line {lineno}: Ch {ch} outside 1..{max_ch}")
            if len(name) > 12:
                warnings.append(f"Ch {ch}: name {name!r} is "
                                f"{len(name)} chars (>12 — fader legibility)")
            cur = ch
            chans[ch] = {'name': name, 'has_filt': False, 'bands': {}}
            continue
        if cur is None or not line or line.startswith('#'):
            continue
        if _FILT.match(line):
            fm = _FILT.match(line)
            hpf = float(fm.group(1))
            chans[cur]['has_filt'] = True
            if not (20 <= hpf <= 20000):
                errors.append(f"Ch {cur}: HPF {hpf:g} outside 20..20000")
            elif hpf > 2000:
                warnings.append(f"Ch {cur}: HPF {hpf:g} Hz — unusually high")
            if fm.group(2).upper() != 'OFF':
                lpf = float(fm.group(2))
                if not (20 <= lpf <= 20000):
                    errors.append(f"Ch {cur}: LPF {lpf:g} outside 20..20000")
                elif lpf < 1000:
                    warnings.append(f"Ch {cur}: LPF {lpf:g} Hz — unusually low")
            continue
        bm = _BAND.match(line)
        if bm:
            bnum = int(bm.group(1)); body = bm.group(2).strip()
            seen = chans[cur].setdefault('seen', set())
            if bnum in seen:
                errors.append(f"Ch {cur}: duplicate B{bnum} line")
            seen.add(bnum)
            if body.upper().startswith('FLAT'):
                continue
            parts = [p.strip() for p in body.split('|')]
            try:
                g, f, q = float(parts[0]), float(parts[1]), float(parts[2])
                ty = parts[3].upper().split()[0]
                if ty not in ('SHELF', 'BELL'):
                    raise ValueError(f"type {parts[3]!r}")
            except (IndexError, ValueError) as e:
                errors.append(f"line {lineno}: Ch {cur} B{bnum} malformed "
                              f"({e}): {body!r}")
                continue
            chans[cur]['bands'][bnum] = f
            if not (20 <= f <= 20000):
                errors.append(f"Ch {cur} B{bnum}: freq {f:g} outside 20..20000")
            if not (-18 <= g <= 18):
                errors.append(f"Ch {cur} B{bnum}: gain {g:g} outside ±18")
            if g != int(g):
                warnings.append(f"Ch {cur} B{bnum}: fractional gain {g:g} dB "
                                "(house rule: whole dB)")
            if not (0.3 <= q <= 20):
                warnings.append(f"Ch {cur} B{bnum}: Q {q:g} outside 0.3..20")
            if 'DEQ' in body.upper() and not _DEQ.search(body):
                errors.append(f"Ch {cur} B{bnum}: DEQ clause doesn't parse — "
                              "it would be silently dropped. Format: "
                              "DEQ: thr=-16 atk=10ms rel=100ms")
            continue
        cgm = re.match(r'(COMP|GATE):\s', line, re.I)
        if cgm:
            # Reuse the engine's Mustard parsers — one source of truth for the
            # syntax. They raise ValueError with a channel-tagged message on
            # anything malformed; the engine would abort on the same, so lint
            # surfaces it as an error here (the documented first gate).
            try:
                import q225_ses_engine as _eng
            except ImportError:
                import os
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import q225_ses_engine as _eng
            body = line[cgm.end():]
            seen = chans[cur].setdefault('mseen', set())
            key = cgm.group(1).upper()
            if key in seen:
                errors.append(f"Ch {cur}: duplicate {key} line")
            seen.add(key)
            try:
                if key == 'COMP':
                    _eng._parse_comp(body, cur)
                else:
                    _eng._parse_gate(body, cur)
            except ValueError as e:
                errors.append(str(e))
            continue
        warnings.append(f"line {lineno}: unrecognized line inside Ch {cur} "
                        f"block: {line!r}")

    if not chans:
        errors.append("no '## Ch N | NAME | MIC' channel headers found")

    # Band-order gate: B-numbers are console bands, B1 = low .. B4 = high.
    # A lower band number with a HIGHER freq than a higher band number means
    # the file is the pre-2026-05-30 backwards numbering — never patch it.
    for ch, d in chans.items():
        b = d['bands']
        for i in sorted(b):
            for j in sorted(b):
                if i < j and b[i] > b[j]:
                    errors.append(
                        f"Ch {ch}: B{i} ({b[i]:g} Hz) is above B{j} "
                        f"({b[j]:g} Hz) — band order looks BACKWARDS "
                        "(pre-2026-05-30 MD?). Do not patch; fix the MD.")
        if not d['has_filt']:
            errors.append(f"Ch {ch}: missing 'HPF: x | LPF: y' line")
    return errors, warnings


def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    errors, warnings = lint(argv[1])
    for w in warnings:
        print(f"  warn: {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    print(f"\n{'FAIL' if errors else 'PASS'} — {len(errors)} errors, "
          f"{len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
