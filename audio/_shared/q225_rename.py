#!/usr/bin/env python3
"""
DiGiCo Q225 .ses NAME renamer — MACROS and AUXES (outputs), shared engine.

Separate from the channel-EQ patcher (`q225_ses_engine.py`). This one only
moves text: it renames macro buttons and aux/output buses in a full console
save, byte-for-byte safe (file size never changes; only the intended name
bytes move; everything structural is left alone and verified).

Three rename kinds:

  MACRO  — scoped to the macro-label table (a small contiguous region in the
           console save). A macro's name may carry a trailing colour code
           "/x" (x = one letter: r g p o y ...). That code is DiGiCo's button
           colour and is PRESERVED: rename "Mix 1" -> "Mon 1" turns every
           "Mix 1", "Mix 1/r", "Mix 1/g" into "Mon 1", "Mon 1/r", "Mon 1/g".
           Matching is exact-base only, so "Mix 1" never touches "Mix 12".
           Scoping to the region means a macro that shares a word with an
           input channel (e.g. "Click-Tap") only has its macro copy changed.

  AUX    — an output/aux bus master. The console propagates a bus rename to
           every send label, so this replaces every length-prefixed copy of
           the old name across the whole file (master surface slot + all
           send-button copies in the channel blocks). No colour-code logic.

  MIXBUS — a monitor-mix bus that Brian labels "Mix N" or "Mix N <instrument>"
           (e.g. "Mix 1 Vox", "Mix 4 Piano Sax", "Mix5 Guitar"). A linked-aux
           rename FULL-REPLACES every such field (number + descriptor) with the
           new name, everywhere OUTSIDE the macro region (the macro copies are
           handled by the MACRO rule so their colour codes survive). Number
           boundary is respected: "Mix 1" matches "Mix 1 Vox" but not "Mix 12".

LINKED AUX (Brian's model 2026-07-13): one aux ties three of the above together
— an output bus ("Wedge N"), a recall macro ("Mix N"), and a mix bus
("Mix N ..."). Renaming the aux renames all three to the same performer name in
one shot (see cal['links']).

Each name field is a length-prefixed string sitting at the front of a fixed
record, followed by zero padding then structural bytes. A write sets the
length byte, writes the new text, and clears only the bytes it needs; the
writable capacity (text start up to the first structural byte) is checked
first, so a name that would collide with structure is refused and nothing is
written.

ALWAYS dry-run first (default). Pass write=True to emit the file. After a
write: load on the Q225 and eyeball the macros/aux masters before trusting it.
"""

import os, re, struct, sys


# ── field primitives ──────────────────────────────────────────────────────────
def _writable_capacity(buf, p):
    """Bytes available for text at length-prefixed field `p` (length byte at p).

    Walks from p+1 while bytes are printable-or-zero; stops at the first
    non-printable non-zero byte (the record's structural data). That span is
    the DiGiCo name buffer — safe to overwrite, never touches structure.
    """
    i = p + 1
    n = len(buf)
    while i < n:
        c = buf[i]
        if c == 0 or 32 <= c < 127:
            i += 1
            continue
        break
    return i - (p + 1)


def _scan_fields(buf, lo, hi, maxlen=40):
    """Yield (offset, length, text) for every length-prefixed printable field
    in [lo, hi). Reads exactly `length` bytes as the field (trailing stale
    bytes beyond the prefix are ignored, as the console ignores them)."""
    i = lo
    hi = min(hi, len(buf) - 1)
    while i < hi:
        ln = buf[i]
        if 1 <= ln <= maxlen and i + 1 + ln <= len(buf):
            s = buf[i + 1:i + 1 + ln]
            if all(32 <= c < 127 for c in s):
                yield (i, ln, s.decode('latin1'))
                i += 1 + ln
                continue
        i += 1


def _split_colour(text):
    """('Mix 1/r') -> ('Mix 1', '/r'); ('Mix 1') -> ('Mix 1', '')."""
    if len(text) >= 3 and text[-2] == '/' and text[-1].isalpha():
        return text[:-2], text[-2:]
    return text, ''


# ── target finding ─────────────────────────────────────────────────────────────
def _looks_like_description(buf, off, ln):
    """Tell a real macro button label from a null-terminated DESCRIPTION field
    that the scanner mis-reads as a short label ("Save current Session" read as
    "Save"). Both may carry trailing bytes past the length count, but they
    differ in KIND: a real label's stale tail is a leftover index — space +
    digits (" 9", " 13") — while a description continues into words. Guard:
    a LETTER in the printable run immediately after the counted text => it's a
    description; never rename it. Numeric/space-only tails pass through."""
    j = off + 1 + ln
    n = len(buf)
    while j < n and 32 <= buf[j] < 127:
        if buf[j:j + 1].isalpha():
            return True
        j += 1
    return False


def find_macro_targets(buf, lo, hi, old, new):
    """[(offset, old_text, new_text)] for macro base `old` in [lo, hi),
    colour code preserved. Exact-base match only; description fields skipped."""
    out = []
    for off, ln, text in _scan_fields(buf, lo, hi):
        base, colour = _split_colour(text)
        if base == old and not _looks_like_description(buf, off, ln):
            out.append((off, text, new + colour))
    return out


def find_aux_targets(buf, old, new):
    """[(offset, old_text, new_text)] for every length-prefixed copy of aux
    name `old` across the whole file.

    The one-byte length prefix is authoritative: a hit where buf[j-1] equals
    len(old) and the following bytes equal `old` IS a field storing exactly
    that string — bytes past the count are the console's stale padding and are
    ignored (some copies carry residue like "Wedge 1" + " 1"). A printable
    name can never hold a 0x07-style count byte mid-string, so this can't
    fire inside a longer name; "Wedge 1" never matches "Wedge 10" (prefix 8)."""
    ob = old.encode('latin1')
    out = []
    i = 0
    while True:
        j = buf.find(ob, i)
        if j < 0:
            break
        i = j + 1
        if j > 0 and buf[j - 1] == len(ob):
            out.append((j - 1, old, new))
    return out


def find_bus_targets(buf, macro_lo, macro_hi, prefix, num, new, keep_suffix=False):
    """[(offset, old_text, new_text)] for a bus whose name starts "<prefix> N".

    Scans every length-prefixed field OUTSIDE [macro_lo, macro_hi) whose text
    begins with "<prefix> N" (optional space; N not followed by another digit,
    so "Mix 1" never catches "Mix 12"). Macro-region copies are left to the
    MACRO rule so their /colour codes survive.

    keep_suffix=False (mono / full replace): the whole field -> `new`.
        "Mix 1 Vox" -> "Bass", "Mix 1" -> "Bass".
    keep_suffix=True (stereo / structured): the "<prefix> N" token -> `new`,
        anything after it is preserved.
        "IEM 1 L" -> "Star L", "IEM 1 R" -> "Star R", "IEM 1" -> "Star".
    """
    rx = re.compile(rf'({re.escape(prefix)} ?{num})(?![0-9])(.*)$')
    pb = prefix.encode('latin1')
    out = []
    i = 0
    while True:
        j = buf.find(pb, i)
        if j < 0:
            break
        i = j + 1
        p = j - 1
        if p < 0:
            continue
        ln = buf[p]
        if not (1 <= ln <= 40) or p + 1 + ln > len(buf):
            continue
        s = buf[j:j + ln]
        if any(not (32 <= c < 127) for c in s):
            continue
        text = s.decode('latin1')
        m = rx.match(text)
        if not m:
            continue
        if macro_lo <= p < macro_hi:
            continue
        new_text = new + m.group(2) if keep_suffix else new
        out.append((p, text, new_text))
    return out


# ── apply + verify ─────────────────────────────────────────────────────────────
def _apply(buf, targets):
    """Write targets into bytearray `buf`. Returns (windows, errors).
    windows = [(start, end)] byte ranges actually changed; errors aborts."""
    windows, errors = [], []
    for p, old_text, new_text in targets:
        old_len = buf[p]
        new_bytes = new_text.encode('latin1')
        cap = _writable_capacity(buf, p)
        if len(new_bytes) > cap:
            errors.append(f"{old_text!r} -> {new_text!r}: needs {len(new_bytes)} "
                          f"bytes but only {cap} fit before structural data")
            continue
        buf[p] = len(new_bytes)
        buf[p + 1:p + 1 + len(new_bytes)] = new_bytes
        # clear only what the old text occupied beyond the new text
        clear_to = p + 1 + max(old_len, len(new_bytes))
        for k in range(p + 1 + len(new_bytes), clear_to):
            buf[k] = 0
        windows.append((p, clear_to))
    return windows, errors


def _verify(src, out, windows):
    """No size change; every differing byte lies inside an allowed window."""
    if len(src) != len(out):
        return ["file size changed"]
    def ok(k):
        return any(lo <= k < hi for lo, hi in windows)
    stray = []
    CH = 0x10000
    for base in range(0, len(src), CH):
        a, b = src[base:base + CH], out[base:base + CH]
        if a != b:
            stray.extend(base + k for k in range(len(a)) if a[k] != b[k] and not ok(base + k))
    return [f"stray byte change at {hex(x)}" for x in stray[:8]]


def rename(cal, src_bytes, macros=None, auxes=None, busgroups=None):
    """Plan (and optionally return) a rename set.

    cal       — calibration with 'macro_lo'/'macro_hi'/'template_size'/'venue'.
    macros    — {old_base: new_base}  (macro region, colour code preserved)
    auxes     — {old_name: new_name}  (exact output bus name, all copies)
    busgroups — [(prefix, num, new, keep_suffix), ...]  ("<prefix> N" buses
                outside the macro region; keep_suffix preserves stereo L/R legs)
    Returns dict: {'targets', 'errors', 'out' (bytearray, applied), 'verify'}.
    Does NOT write to disk.
    """
    macros = macros or {}
    auxes = auxes or {}
    busgroups = busgroups or []
    targets = []
    for old, new in macros.items():
        hits = find_macro_targets(src_bytes, cal['macro_lo'], cal['macro_hi'], old, new)
        if not hits:
            targets.append(('MISS', f"macro {old!r}", "no macro field with that base"))
        targets += [('MACRO', old, new, off, ot, nt) for (off, ot, nt) in hits]
    for old, new in auxes.items():
        hits = find_aux_targets(src_bytes, old, new)
        if not hits:
            targets.append(('MISS', f"aux {old!r}", "no bus copy with that name"))
        targets += [('AUX', old, new, off, ot, nt) for (off, ot, nt) in hits]
    for prefix, num, new, keep in busgroups:
        hits = find_bus_targets(src_bytes, cal['macro_lo'], cal['macro_hi'],
                                prefix, num, new, keep_suffix=keep)
        # a bus may legitimately have no copies outside the macro region
        label = f"{prefix} {num}"
        targets += [('BUS', label, new, off, ot, nt) for (off, ot, nt) in hits]

    writes = [(off, ot, nt) for t in targets if t[0] in ('MACRO', 'AUX', 'BUS')
              for (off, ot, nt) in [(t[3], t[4], t[5])]]
    misses = [(t[1], t[2]) for t in targets if t[0] == 'MISS']

    out = bytearray(src_bytes)
    windows, errors = _apply(out, writes)
    verify_errs = _verify(src_bytes, bytes(out), windows) if not errors else []
    return {'targets': targets, 'writes': writes, 'misses': misses,
            'errors': errors, 'verify': verify_errs, 'out': out}


# ── CLI ─────────────────────────────────────────────────────────────────────────
def _parse_pairs(items):
    out = {}
    for it in (items or []):
        if '=' not in it:
            sys.stderr.write(f"ERROR: '{it}' is not OLD=NEW\n")
            sys.exit(2)
        k, v = it.split('=', 1)
        out[k.strip()] = v.strip()
    return out


def main_cli(cal, argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        description=f"Rename macros / auxes in a {cal['venue']} Q225 .ses. "
                    "Dry-run by default; pass --write to emit the file.")
    ap.add_argument('--src', default=cal.get('template'),
                    help="source .ses (defaults to the venue template)")
    ap.add_argument('--dest', help="output .ses (required with --write)")
    if cal.get('links'):
        ap.add_argument('--link', action='append', metavar='N=NEW',
                        help="rename linked aux N — output bus + macro + mix bus "
                             "all become NEW (see cal['links'])")
    buskinds = cal.get('buskinds', {})
    for kind, spec in buskinds.items():
        ap.add_argument(f'--{kind}', action='append', metavar='N=NEW',
                        help=f"rename {spec['prefix']} N bus + its macro to NEW"
                             + (" (stereo L/R legs kept)" if spec.get('keep_suffix')
                                else ""))
    ap.add_argument('--macro', action='append', metavar='OLD=NEW',
                    help="rename a macro by base name (colour code /x preserved)")
    ap.add_argument('--aux', action='append', metavar='OLD=NEW',
                    help="rename an aux/output bus (propagates to all sends)")
    ap.add_argument('--write', action='store_true',
                    help="actually write --dest (otherwise dry-run only)")
    a = ap.parse_args(argv)

    if not a.src or not os.path.exists(a.src):
        sys.stderr.write(f"ERROR: source not found: {a.src}\n"); return 2
    macros = _parse_pairs(a.macro)
    auxes = _parse_pairs(a.aux)
    busgroups = []

    def _num(n_str, opt):
        s = re.sub(r'[A-Za-z]', '', n_str).strip()
        if not s.isdigit():
            sys.stderr.write(f"ERROR: --{opt} '{n_str}': N must be a number\n")
            sys.exit(2)
        return int(s)

    # Memo-style linked aux: output bus "Wedge N" + macro "Mix N" + mix bus.
    links = cal.get('links', {})
    for n_str, new in _parse_pairs(getattr(a, 'link', None)).items():
        n = _num(n_str, 'link')
        if n not in links:
            sys.stderr.write(f"ERROR: aux {n} is not a linked aux "
                             f"(linked: {sorted(links)})\n")
            return 2
        aux_name, mix_label = links[n]
        mnum = _num(mix_label, 'link')
        auxes[aux_name] = new
        macros[mix_label] = new
        busgroups.append(('Mix', mnum, new, False))

    # FSQ-style explicit bus kinds (--mix / --iem): macro "<prefix> N" + bus.
    for kind, spec in buskinds.items():
        for n_str, new in _parse_pairs(getattr(a, kind, None)).items():
            n = _num(n_str, kind)
            macros[f"{spec['prefix']} {n}"] = new
            busgroups.append((spec['prefix'], n, new, spec.get('keep_suffix', False)))

    if not macros and not auxes and not busgroups:
        sys.stderr.write("ERROR: give at least one rename (--link/--mix/--iem/"
                         "--macro/--aux)\n")
        return 2

    src = open(a.src, 'rb').read()
    tsize = cal.get('template_size')
    if tsize and len(src) != tsize:
        sys.stderr.write(
            f"ABORT: --src is {len(src):,} bytes; calibrated {cal['venue']} "
            f"template is {tsize:,}. Wrong file or resaved template.\n")
        return 3

    r = rename(cal, src, macros=macros, auxes=auxes, busgroups=busgroups)

    print(f"Source: {os.path.basename(a.src)}  ({len(src):,} bytes)")
    print(f"Venue:  {cal['venue']}   macro region {hex(cal['macro_lo'])}"
          f"..{hex(cal['macro_hi'])}\n")
    for label, why in r['misses']:
        print(f"  !! MISS  {label}: {why}")
    if r['misses']:
        print("\nABORT: some names were not found — nothing written. "
              "Check exact spelling/case.")
        return 2
    for t in r['targets']:
        if t[0] in ('MACRO', 'AUX', 'BUS'):
            kind, old, new, off, ot, nt = t
            print(f"  {kind:6} {hex(off):>10}  {ot!r:>22} -> {nt!r}")
    print(f"\n  {len(r['writes'])} field(s) targeted")
    if r['errors']:
        for e in r['errors']:
            print(f"  !! {e}")
        print("\nABORT: capacity error — nothing written.")
        return 2
    if r['verify']:
        for e in r['verify']:
            print(f"  !! {e}")
        print("\nABORT: verification failed — nothing written.")
        return 1

    if not a.write:
        print("\nDRY RUN — pass --write --dest OUT.ses to apply.")
        return 0
    if not a.dest:
        sys.stderr.write("ERROR: --write needs --dest\n"); return 2
    open(a.dest, 'wb').write(bytes(r['out']))
    print(f"\nVerification: PASS (size unchanged, no stray bytes)")
    print(f"Written -> {a.dest}")
    print("NEXT: load on the Q225 and confirm the names before trusting it.")
    return 0
