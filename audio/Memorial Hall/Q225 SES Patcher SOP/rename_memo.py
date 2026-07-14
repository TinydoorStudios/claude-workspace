#!/usr/bin/env python3
"""
Rename MACROS and AUXES in a MEMORIAL HALL (Memo) Q225 .ses.

Byte-level logic lives in the shared engine:
    ~/Documents/Claude/audio/_shared/q225_rename.py
This wrapper holds only the Memo template's calibration.

TEMPLATE: `Memorial Hall/_TEMPLATE/brian memo june 2026.ses` (37,661,337 bytes).
Macro-label table located 2026-07-13 by structural scan: the macro region runs
from the "Save" macro through "Click-Tap", ahead of the Set/A/B/C control-group
labels. Auxes are output buses (Wedge 1-6, W1-4 Monitor, Aux N, Matrix N, ...);
a rename propagates to every send-label copy, matching console behaviour.

Dry-run (default):
    python3 rename_memo.py --macro "Mix 1=Mon 1" --aux "Wedge 1=IEM 1"
Write it:
    python3 rename_memo.py --macro "Mix 1=Mon 1" --write \
        --dest "<show folder>/<Show>.ses"

Macro colour codes ("/r" "/g" "/p" "/o" "/y") are preserved automatically —
rename the base only.
"""
import os, sys

ENGINE_DIR = os.path.expanduser("~/Documents/Claude/audio/_shared")
sys.path.insert(0, ENGINE_DIR)
from q225_rename import main_cli   # noqa: E402

CAL = dict(
    venue='memo',
    template=os.path.expanduser(
        "~/Documents/Claude/audio/Memorial Hall/_TEMPLATE/brian memo june 2026.ses"),
    template_size=37_661_337,
    # Macro-label table (contains only macro button labels; ends before the
    # "Matrix/Wedge Out/FX Send/Set N/A1.../B1.../C1..." bank + control labels).
    macro_lo=0x23E8D00,
    macro_hi=0x23EA320,
    # Linked auxes (Brian's model 2026-07-13): aux N ties three objects together
    # — an output bus ("Wedge N"), a recall macro ("Mix N"), and a monitor-mix
    # bus ("Mix N <instrument>", e.g. "Mix 1 Vox"). Renaming aux N sets ALL
    # THREE to the same performer name in one shot: the bus (all copies), the
    # macro (colour codes /r /g preserved), and the mix bus (full replace, the
    # instrument descriptor dropped). Confirmed with Brian 2026-07-13.
    #   aux N : (output-bus master name, "Mix N" label — macro base & mix prefix)
    links={
        1: ('Wedge 1', 'Mix 1'),
        2: ('Wedge 2', 'Mix 2'),
        3: ('Wedge 3', 'Mix 3'),
        4: ('Wedge 4', 'Mix 4'),
        5: ('Wedge 5', 'Mix 5'),
        6: ('Wedge 6', 'Mix 6'),
    },
)

if __name__ == '__main__':
    sys.exit(main_cli(CAL))
