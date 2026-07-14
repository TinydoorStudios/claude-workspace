#!/usr/bin/env python3
"""
Standalone .ses readback verifier — re-checks an ALREADY-BUILT show file
against its FOH Channel Processing .md, without rebuilding.

Every patch run already does this automatically (the engine's step 5),
so this tool is for after the fact: re-verifying a file found on a USB
stick, confirming an old build against its paperwork, or checking a file
someone edited by hand in the offline software.

Usage:
    python3 readback_verify.py --venue memo|fsq \
        --ses "<Show>.ses" --md "<Show> - FOH Channel Processing.md"

Checks every MD channel: surface name, name-copy count, all named EQ
bands (gain/freq/Q/type at the mapped bidx), DEQ, HPF/LPF stored-value
scaling. Exit 0 = PASS, 1 = FAIL.

Note: block location uses the CURRENT name in the file (the MD's console
name), so it works on renamed builds. For the scan-mode venue (fsq) this
requires the show names to be unique in the scene region — they are, by
the same rule the patcher enforces.
"""
import argparse, importlib.util, os, sys

VENUE_WRAPPERS = {
    'memo': "~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/"
            "apply_show_TEMPLATE.py",
    'fsq':  "~/Documents/Claude/audio/Fountain Square/Q225 SES Patcher SOP/"
            "apply_show_TEMPLATE_FSQ.py",
}


def load_cal(venue):
    path = os.path.expanduser(VENUE_WRAPPERS[venue])
    spec = importlib.util.spec_from_file_location(f"wrapper_{venue}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CAL


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--venue', required=True, choices=('memo', 'fsq'))
    ap.add_argument('--ses',   required=True, help="built show .ses")
    ap.add_argument('--md',    required=True, help="FOH Channel Processing .md")
    a = ap.parse_args(argv)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import q225_ses_engine as eng

    cal = load_cal(a.venue)
    buf = open(a.ses, 'rb').read()
    tsize = cal.get('template_size')
    if tsize and len(buf) != tsize:
        print(f"FAIL: {os.path.basename(a.ses)} is {len(buf):,} bytes; the "
              f"{a.venue} template is {tsize:,} — wrong venue or stale build.")
        return 1
    work = eng.read_md(a.md)
    print(f"File:  {os.path.basename(a.ses)}  ({len(buf):,} bytes)")
    print(f"Venue: {a.venue}   MD channels: {sorted(work)}")
    ok = eng.readback(cal, buf, work)
    print(f"\n{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
