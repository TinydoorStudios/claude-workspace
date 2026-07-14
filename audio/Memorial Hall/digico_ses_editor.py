#!/usr/bin/env python3
"""
DiGiCo Quantum .SES File Editor
Supports: channel name, EQ (4 bands), gate, comp (DiGiComp)

Usage:
    python3 digico_ses_editor.py show.ses                          # list all channels
    python3 digico_ses_editor.py show.ses --channel "KICK IN"      # show one channel detail
    python3 digico_ses_editor.py show.ses --channel "KICK IN" \
        --name "KICK"                                              # rename channel
    python3 digico_ses_editor.py show.ses --channel "KICK IN" \
        --eq 1 --freq 600 --gain -5.0 --q 0.4                     # set EQ band 1
    python3 digico_ses_editor.py show.ses --channel "KICK IN" \
        --gate-thresh -32.0 --gate-enable 1                        # set gate
    python3 digico_ses_editor.py show.ses --channel "KICK IN" \
        --comp-thresh -18.0 --comp-enable 1 --comp-makeup 4.0     # set comp

Notes:
    - Always supply --out to write a new file; without it the tool is read-only.
    - EQ bands are numbered 0-3 (band 0 = high, band 3 = low on Q225).
    - Gate thresholds in dBFS. Attack/release in seconds.
    - Comp is DiGiComp (optical-style) — no ratio parameter.
    - The tool edits ALL occurrences of a channel name in the file (main + snapshots).
      Use --first-only to restrict to the first occurrence only.
"""

import struct
import argparse
import sys
import copy
from pathlib import Path

# ── Tag constants ────────────────────────────────────────────────────────────
# EQ (per-band, band_index 0–3)
TAG_EQ_ENABLE  = 0x0404
TAG_EQ_FREQ    = 0x0406
TAG_EQ_GAIN    = 0x0403
TAG_EQ_Q       = 0x0410
TAG_EQ_TYPE    = 0x040B   # 2.0 = bell, others = shelf/HP/LP

# Gate (0x1D series)
TAG_GATE_ENABLE      = 0x1D0E
TAG_GATE_OPEN_THRESH = 0x1D0F
TAG_GATE_CLOSE_THRESH= 0x1D4A
TAG_GATE_ATTACK      = 0x1D10
TAG_GATE_RELEASE     = 0x1D12
TAG_GATE_MAKEUP      = 0x1D0B
TAG_GATE_RATIO       = 0x1D09
TAG_GATE_RANGE       = 0x1D05   # idx=0

# Comp / DiGiComp (0x1E series)
TAG_COMP_ENABLE      = 0x1E0E
TAG_COMP_THRESH      = 0x1E11
TAG_COMP_RELEASE     = 0x1E12
TAG_COMP_MAKEUP      = 0x1E0B
TAG_COMP_HOLD        = 0x1E0A   # labeled hold; also 0x1E13

# Channel name field
NAME_FIELD_BYTES = 32   # 1 byte length prefix + up to 31 chars + null padding
PRE_NAME_HEADER  = bytes.fromhex('d70001000000d50001000112000000da003a0001000000')
# The full marker is: [da 00] [pre stuff] [da 00 3a 00 01 00 00 00] [32-byte name]


def float_at(data, offset):
    return struct.unpack_from('<f', data, offset)[0]

def pack_float(val):
    return struct.pack('<f', val)


def find_name_fields(data, channel_name):
    """
    Find all occurrences of a channel name stored as a length-prefixed,
    zero-padded 32-byte field preceded by the standard pre-name header.
    Returns list of (name_field_offset,) where name_field_offset points
    to the length byte.
    """
    enc = channel_name.encode('ascii')
    length_byte = bytes([len(enc)])
    padded = length_byte + enc + b'\x00' * (NAME_FIELD_BYTES - 1 - len(enc))
    assert len(padded) == NAME_FIELD_BYTES

    offsets = []
    pos = 0
    while True:
        pos = data.find(padded, pos)
        if pos == -1:
            break
        # Verify the pre-name header ends just before this field
        header_end = pos
        if data[header_end - 8 : header_end] == b'\xda\x00\x3a\x00\x01\x00\x00\x00':
            offsets.append(pos)
        pos += 1
    return offsets


def find_tag_in_region(data, start, size, tag, idx=0):
    """
    Scan [start, start+size) for an 8-byte TLV record:
        [float32 LE][tag uint16 LE][idx uint16 LE]
    Returns offset of the float value (4 bytes before the tag bytes),
    or None if not found.
    """
    tag_bytes = struct.pack('<H', tag)
    idx_bytes = struct.pack('<H', idx)
    needle = tag_bytes + idx_bytes
    pos = start
    end  = start + size - 7
    while pos < end:
        found = data.find(needle, pos, end)
        if found == -1:
            return None
        val_off = found - 4
        if val_off >= start:
            return val_off
        pos = found + 1
    return None


def read_tag(data, start, size, tag, idx=0):
    off = find_tag_in_region(data, start, size, tag, idx)
    if off is None:
        return None
    return float_at(data, off)


def write_tag(data_bytearray, start, size, tag, idx, new_value):
    """Patch the float value of a TLV record in-place. Returns True on success."""
    data_view = bytes(data_bytearray)
    off = find_tag_in_region(data_view, start, size, tag, idx)
    if off is None:
        return False
    data_bytearray[off:off+4] = pack_float(new_value)
    return True


# ── Channel discovery ────────────────────────────────────────────────────────

def discover_channels(data):
    """
    Find all channel names in the file. Returns list of dicts:
        { name, name_field_offset, block_start (approx), block_size (approx) }
    Ordered by first occurrence.
    """
    # Search for all 32-byte name fields preceded by the da003a00 01000000 header
    header = b'\xda\x00\x3a\x00\x01\x00\x00\x00'
    channels = []
    seen_names = set()
    pos = 0

    while True:
        pos = data.find(header, pos)
        if pos == -1:
            break
        name_field_off = pos + len(header)
        if name_field_off + NAME_FIELD_BYTES > len(data):
            pos += 1
            continue
        length_byte = data[name_field_off]
        if 1 <= length_byte <= 30:
            name_bytes = data[name_field_off + 1 : name_field_off + 1 + length_byte]
            try:
                name = name_bytes.decode('ascii')
                if name.isprintable() and len(name) >= 1:
                    if name not in seen_names:
                        seen_names.add(name)
                        channels.append({
                            'name': name,
                            'name_field_offset': name_field_off,
                            'block_start': name_field_off,  # refined below
                        })
            except UnicodeDecodeError:
                pass
        pos += 1

    # Sort by offset, assign approximate block sizes
    channels.sort(key=lambda c: c['name_field_offset'])
    for i, ch in enumerate(channels):
        next_off = channels[i+1]['name_field_offset'] if i+1 < len(channels) else len(data)
        ch['block_size'] = next_off - ch['name_field_offset']

    return channels


def get_channel(data, channel_name):
    """Return the first channel dict matching name (case-insensitive)."""
    channels = discover_channels(data)
    target = channel_name.strip().upper()
    for ch in channels:
        if ch['name'].strip().upper() == target:
            return ch
    return None


# ── Read channel state ───────────────────────────────────────────────────────

def read_channel_state(data, ch):
    s = ch['block_start']
    sz = ch['block_size']

    state = {'name': ch['name'], 'eq': [], 'gate': {}, 'comp': {}}

    # EQ bands 0-3
    for band in range(4):
        freq   = read_tag(data, s, sz, TAG_EQ_FREQ,   band)
        gain   = read_tag(data, s, sz, TAG_EQ_GAIN,   band)
        q      = read_tag(data, s, sz, TAG_EQ_Q,      band)
        enable = read_tag(data, s, sz, TAG_EQ_ENABLE, band)
        btype  = read_tag(data, s, sz, TAG_EQ_TYPE,   band)
        state['eq'].append({
            'band': band,
            'freq': freq,
            'gain': gain,
            'q':    q,
            'enable': enable,
            'type':   btype,
        })

    # Gate
    g = state['gate']
    g['enable']       = read_tag(data, s, sz, TAG_GATE_ENABLE)
    g['open_thresh']  = read_tag(data, s, sz, TAG_GATE_OPEN_THRESH)
    g['close_thresh'] = read_tag(data, s, sz, TAG_GATE_CLOSE_THRESH)
    g['attack']       = read_tag(data, s, sz, TAG_GATE_ATTACK)
    g['release']      = read_tag(data, s, sz, TAG_GATE_RELEASE)
    g['makeup']       = read_tag(data, s, sz, TAG_GATE_MAKEUP)
    g['range']        = read_tag(data, s, sz, TAG_GATE_RANGE, idx=0)

    # Comp (DiGiComp)
    c = state['comp']
    c['enable']       = read_tag(data, s, sz, TAG_COMP_ENABLE)
    c['thresh']       = read_tag(data, s, sz, TAG_COMP_THRESH)
    c['release']      = read_tag(data, s, sz, TAG_COMP_RELEASE)
    c['makeup']       = read_tag(data, s, sz, TAG_COMP_MAKEUP)
    c['hold']         = read_tag(data, s, sz, TAG_COMP_HOLD)

    return state


def fmt(val, decimals=2):
    if val is None:
        return 'N/A'
    return f'{val:.{decimals}f}'


def print_channel_state(state):
    print(f"\n{'─'*52}")
    print(f"  Channel: {state['name']}")
    print(f"{'─'*52}")

    print(f"\n  EQ Bands:")
    print(f"  {'Band':>4}  {'On':>3}  {'Freq Hz':>8}  {'Gain dB':>8}  {'Q':>6}  {'Type':>5}")
    print(f"  {'────':>4}  {'──':>3}  {'───────':>8}  {'───────':>8}  {'─':>6}  {'────':>5}")
    for b in state['eq']:
        on   = int(b['enable']) if b['enable'] is not None else '?'
        btyp = {1.0: 'Shelf', 2.0: 'Bell', 3.0: 'LP', 4.0: 'HP'}.get(b['type'], '?')
        print(f"  {b['band']:>4}  {str(on):>3}  {fmt(b['freq'],1):>8}  {fmt(b['gain']):>8}  {fmt(b['q'],3):>6}  {btyp:>5}")

    g = state['gate']
    print(f"\n  Gate:")
    print(f"    Enable:        {int(g['enable']) if g['enable'] is not None else 'N/A'}")
    print(f"    Open Thresh:   {fmt(g['open_thresh'])} dBFS")
    print(f"    Close Thresh:  {fmt(g['close_thresh'])} dBFS")
    print(f"    Range:         {fmt(g['range'])} dB")
    print(f"    Attack:        {fmt(g['attack'],4)} s  ({(g['attack']*1000):.1f} ms)" if g['attack'] else "    Attack:        N/A")
    print(f"    Release:       {fmt(g['release'],4)} s  ({(g['release']*1000):.1f} ms)" if g['release'] else "    Release:       N/A")
    print(f"    Makeup:        {fmt(g['makeup'])} dB")

    c = state['comp']
    print(f"\n  Comp (DiGiComp):")
    print(f"    Enable:        {int(c['enable']) if c['enable'] is not None else 'N/A'}")
    print(f"    Threshold:     {fmt(c['thresh'])} dBFS")
    print(f"    Release:       {fmt(c['release'],4)} s  ({(c['release']*1000):.1f} ms)" if c['release'] else "    Release:       N/A")
    print(f"    Hold:          {fmt(c['hold'],4)} s  ({(c['hold']*1000):.1f} ms)" if c['hold'] else "    Hold:          N/A")
    print(f"    Makeup:        {fmt(c['makeup'])} dB")
    print()


# ── Write channel edits ──────────────────────────────────────────────────────

def apply_edits(data_bytearray, ch, args):
    """Apply all requested edits to data_bytearray in-place."""
    s = ch['block_start']
    sz = ch['block_size']
    data = data_bytearray  # alias

    changes = []

    # ── Name ────────────────────────────────────────────────────────────────
    if args.name:
        new_name = args.name[:31]
        enc = new_name.encode('ascii')
        old_field_start = ch['name_field_offset']
        new_field = bytes([len(enc)]) + enc + b'\x00' * (NAME_FIELD_BYTES - 1 - len(enc))
        # Patch ALL occurrences of the old name field
        old_enc = ch['name'].encode('ascii')
        old_field = bytes([len(old_enc)]) + old_enc + b'\x00' * (NAME_FIELD_BYTES - 1 - len(old_enc))
        pos = 0
        count = 0
        while True:
            found = bytes(data).find(old_field, pos)
            if found == -1:
                break
            data[found:found+NAME_FIELD_BYTES] = new_field
            count += 1
            pos = found + NAME_FIELD_BYTES
        changes.append(f'Name: "{ch["name"]}" → "{new_name}" ({count} occurrence(s))')

    # ── EQ ──────────────────────────────────────────────────────────────────
    if args.eq is not None:
        band = args.eq
        if args.freq is not None:
            ok = write_tag(data, s, sz, TAG_EQ_FREQ, band, float(args.freq))
            changes.append(f'EQ band {band} freq → {args.freq} Hz {"✓" if ok else "FAILED"}')
        if args.gain is not None:
            ok = write_tag(data, s, sz, TAG_EQ_GAIN, band, float(args.gain))
            changes.append(f'EQ band {band} gain → {args.gain} dB {"✓" if ok else "FAILED"}')
        if args.q is not None:
            ok = write_tag(data, s, sz, TAG_EQ_Q, band, float(args.q))
            changes.append(f'EQ band {band} Q → {args.q} {"✓" if ok else "FAILED"}')
        if args.eq_enable is not None:
            ok = write_tag(data, s, sz, TAG_EQ_ENABLE, band, float(args.eq_enable))
            changes.append(f'EQ band {band} enable → {args.eq_enable} {"✓" if ok else "FAILED"}')

    # ── Gate ─────────────────────────────────────────────────────────────────
    if args.gate_enable is not None:
        ok = write_tag(data, s, sz, TAG_GATE_ENABLE, 0, float(args.gate_enable))
        changes.append(f'Gate enable → {args.gate_enable} {"✓" if ok else "FAILED"}')
    if args.gate_thresh is not None:
        ok = write_tag(data, s, sz, TAG_GATE_OPEN_THRESH, 0, float(args.gate_thresh))
        changes.append(f'Gate open thresh → {args.gate_thresh} dBFS {"✓" if ok else "FAILED"}')
    if args.gate_close is not None:
        ok = write_tag(data, s, sz, TAG_GATE_CLOSE_THRESH, 0, float(args.gate_close))
        changes.append(f'Gate close thresh → {args.gate_close} dBFS {"✓" if ok else "FAILED"}')
    if args.gate_attack is not None:
        ok = write_tag(data, s, sz, TAG_GATE_ATTACK, 0, float(args.gate_attack))
        changes.append(f'Gate attack → {args.gate_attack} s {"✓" if ok else "FAILED"}')
    if args.gate_release is not None:
        ok = write_tag(data, s, sz, TAG_GATE_RELEASE, 0, float(args.gate_release))
        changes.append(f'Gate release → {args.gate_release} s {"✓" if ok else "FAILED"}')
    if args.gate_range is not None:
        ok = write_tag(data, s, sz, TAG_GATE_RANGE, 0, float(args.gate_range))
        changes.append(f'Gate range → {args.gate_range} dB {"✓" if ok else "FAILED"}')
    if args.gate_makeup is not None:
        ok = write_tag(data, s, sz, TAG_GATE_MAKEUP, 0, float(args.gate_makeup))
        changes.append(f'Gate makeup → {args.gate_makeup} dB {"✓" if ok else "FAILED"}')

    # ── Comp ─────────────────────────────────────────────────────────────────
    if args.comp_enable is not None:
        ok = write_tag(data, s, sz, TAG_COMP_ENABLE, 0, float(args.comp_enable))
        changes.append(f'Comp enable → {args.comp_enable} {"✓" if ok else "FAILED"}')
    if args.comp_thresh is not None:
        ok = write_tag(data, s, sz, TAG_COMP_THRESH, 0, float(args.comp_thresh))
        changes.append(f'Comp thresh → {args.comp_thresh} dBFS {"✓" if ok else "FAILED"}')
    if args.comp_release is not None:
        ok = write_tag(data, s, sz, TAG_COMP_RELEASE, 0, float(args.comp_release))
        changes.append(f'Comp release → {args.comp_release} s {"✓" if ok else "FAILED"}')
    if args.comp_makeup is not None:
        ok = write_tag(data, s, sz, TAG_COMP_MAKEUP, 0, float(args.comp_makeup))
        changes.append(f'Comp makeup → {args.comp_makeup} dB {"✓" if ok else "FAILED"}')
    if args.comp_hold is not None:
        ok = write_tag(data, s, sz, TAG_COMP_HOLD, 0, float(args.comp_hold))
        changes.append(f'Comp hold → {args.comp_hold} s {"✓" if ok else "FAILED"}')

    return changes


# ── CLI ──────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        description='DiGiCo Quantum .SES editor — channel name, EQ, gate, comp')
    p.add_argument('ses_file', help='Path to .ses file')
    p.add_argument('--channel', '-c', metavar='NAME',
                   help='Channel to inspect or edit (exact name, case-insensitive)')
    p.add_argument('--out', '-o', metavar='PATH',
                   help='Output .ses path (omit for read-only)')
    p.add_argument('--list', '-l', action='store_true',
                   help='List all channel names and their first offset')

    # Name
    p.add_argument('--name', metavar='NEW_NAME', help='Rename the channel')

    # EQ
    eq = p.add_argument_group('EQ (requires --eq BAND where BAND is 0-3)')
    eq.add_argument('--eq', type=int, metavar='BAND', help='EQ band to edit (0=high .. 3=low)')
    eq.add_argument('--freq', type=float, metavar='HZ')
    eq.add_argument('--gain', type=float, metavar='DB')
    eq.add_argument('--q', type=float, metavar='Q')
    eq.add_argument('--eq-enable', type=int, metavar='0|1', dest='eq_enable')

    # Gate
    ga = p.add_argument_group('Gate')
    ga.add_argument('--gate-enable',  type=int,   metavar='0|1', dest='gate_enable')
    ga.add_argument('--gate-thresh',  type=float, metavar='DB',  dest='gate_thresh',
                    help='Open threshold dBFS')
    ga.add_argument('--gate-close',   type=float, metavar='DB',  dest='gate_close',
                    help='Close threshold dBFS')
    ga.add_argument('--gate-attack',  type=float, metavar='SEC', dest='gate_attack',
                    help='Attack time in seconds (e.g. 0.001 = 1ms)')
    ga.add_argument('--gate-release', type=float, metavar='SEC', dest='gate_release',
                    help='Release time in seconds (e.g. 0.1 = 100ms)')
    ga.add_argument('--gate-range',   type=float, metavar='DB',  dest='gate_range',
                    help='Gate range dB (depth of closure, e.g. 40)')
    ga.add_argument('--gate-makeup',  type=float, metavar='DB',  dest='gate_makeup')

    # Comp
    co = p.add_argument_group('Comp (DiGiComp — no ratio parameter)')
    co.add_argument('--comp-enable',  type=int,   metavar='0|1', dest='comp_enable')
    co.add_argument('--comp-thresh',  type=float, metavar='DB',  dest='comp_thresh')
    co.add_argument('--comp-release', type=float, metavar='SEC', dest='comp_release',
                    help='Release in seconds (e.g. 0.1 = 100ms)')
    co.add_argument('--comp-makeup',  type=float, metavar='DB',  dest='comp_makeup')
    co.add_argument('--comp-hold',    type=float, metavar='SEC', dest='comp_hold')

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    ses_path = Path(args.ses_file)
    if not ses_path.exists():
        print(f'ERROR: file not found: {ses_path}', file=sys.stderr)
        sys.exit(1)

    data = bytearray(ses_path.read_bytes())
    data_bytes = bytes(data)

    # ── List mode ─────────────────────────────────────────────────────────────
    if args.list or args.channel is None:
        channels = discover_channels(data_bytes)
        print(f'\nFound {len(channels)} channels in {ses_path.name}:\n')
        print(f'  {"#":>3}  {"Offset":>8}  Name')
        print(f'  {"─":>3}  {"──────":>8}  ────')
        for i, ch in enumerate(channels):
            print(f'  {i+1:>3}  {hex(ch["name_field_offset"]):>8}  {ch["name"]}')
        print()
        if args.channel is None:
            return

    # ── Find channel ──────────────────────────────────────────────────────────
    ch = get_channel(data_bytes, args.channel)
    if ch is None:
        print(f'ERROR: channel "{args.channel}" not found.', file=sys.stderr)
        channels = discover_channels(data_bytes)
        print('Available channels:', ', '.join(c['name'] for c in channels), file=sys.stderr)
        sys.exit(1)

    # ── Read & display current state ──────────────────────────────────────────
    state = read_channel_state(data_bytes, ch)
    print_channel_state(state)

    # ── Apply edits if any ────────────────────────────────────────────────────
    has_edits = any([
        args.name, args.eq is not None, args.gate_enable is not None,
        args.gate_thresh, args.gate_close, args.gate_attack,
        args.gate_release, args.gate_range, args.gate_makeup,
        args.comp_enable is not None, args.comp_thresh,
        args.comp_release, args.comp_makeup, args.comp_hold,
    ])

    if has_edits:
        if args.out is None:
            print('  ⚠  Edit flags specified but --out not provided. Dry run only.')
            print('     Add --out path/to/output.ses to write changes.\n')
            return

        # Reload as mutable
        data = bytearray(ses_path.read_bytes())

        # Re-fetch channel against fresh bytearray
        ch2 = get_channel(bytes(data), args.channel)

        changes = apply_edits(data, ch2, args)

        out_path = Path(args.out)
        out_path.write_bytes(data)

        print(f'  Changes applied ({len(changes)}):')
        for c in changes:
            print(f'    • {c}')
        print(f'\n  Written → {out_path}\n')

        # Show updated state
        data_bytes2 = bytes(data)
        ch3 = get_channel(data_bytes2, args.name if args.name else args.channel)
        if ch3:
            state2 = read_channel_state(data_bytes2, ch3)
            print('  ── Updated state ──')
            print_channel_state(state2)
    elif args.out:
        print(f'  No edits specified — file unchanged.\n')


if __name__ == '__main__':
    main()
