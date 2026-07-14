#!/usr/bin/env python3
"""
Rename MACROS and BUSES in a FOUNTAIN SQUARE (FSQ) Q225 .ses.

Byte-level logic lives in the shared engine:
    ~/Documents/Claude/audio/_shared/q225_rename.py
This wrapper holds only the FSQ template's calibration.

TEMPLATE: `Fountain Square/_TEMPLATE/brian fsq start.ses` (3,779,766 bytes).
Macro-label table located 2026-07-13 by structural scan: runs from "Save"
through the IEM macros, ahead of the "Aux to Faders / Set N" labels.

FSQ has TWO distinct linked-bus families — Brian keeps them separate and names
which one each time:
  --mix N=NEW  : the mono Mix N bus + its recall macro (Mix N/g, Mix N/r) -> NEW
  --iem N=NEW  : the stereo IEM N bus + its macro (IEM N/g, IEM N/r) -> NEW,
                 with the L/R legs kept ("IEM 1 L" -> "NEW L", "IEM 1 R" -> "NEW R")
Both cover Mix/IEM 1-6. Macro colour codes are preserved automatically.

Dry-run (default):
    python3 rename_fsq.py --mix "1=Star" --iem "3=Drums"
Write it:
    python3 rename_fsq.py --mix "1=Star" --write --dest "<folder>/<Show>.ses"

Generic --macro OLD=NEW and --aux OLD=NEW are also available for one-offs.
"""
import os, sys

ENGINE_DIR = os.path.expanduser("~/Documents/Claude/audio/_shared")
sys.path.insert(0, ENGINE_DIR)
from q225_rename import main_cli   # noqa: E402

CAL = dict(
    venue='fsq',
    template=os.path.expanduser(
        "~/Documents/Claude/audio/Fountain Square/_TEMPLATE/brian fsq start.ses"),
    template_size=3_779_766,
    # Macro-label table (Save/Tap/Mute All, Mix 1-6, Hall/Plate/Room/Delay,
    # off/on, IEM 1-6); ends before "Aux to Faders" + the Set N labels.
    macro_lo=0x399000,
    macro_hi=0x39A505,
    # Two explicit bus families Brian names per-rename (Mix and IEM are
    # DIFFERENT objects here — confirmed 2026-07-13). Each renames the macro
    # ("<prefix> N", colour codes kept) plus every bus copy outside the macro
    # region. IEM is stereo, so its L/R legs are preserved.
    buskinds={
        'mix': {'prefix': 'Mix', 'keep_suffix': False},
        'iem': {'prefix': 'IEM', 'keep_suffix': True},
    },
)

if __name__ == '__main__':
    sys.exit(main_cli(CAL))
