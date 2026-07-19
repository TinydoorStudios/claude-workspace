#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — MEMORIAL HALL (Memo) venue wrapper.

All byte-level logic lives in the SHARED engine:
    ~/Documents/Claude/audio/_shared/q225_ses_engine.py
This file holds only the Memo template's calibration. Fix bugs in the
engine (both venues inherit); recalibrate templates here.

TEMPLATE: `Memorial Hall/_TEMPLATE/brian memo june 2026.ses`
(37,661,337 bytes — full console save, swapped in 2026-07-01; the old
1.5 MB strip-layout `brian memo v2.ses` is retired). Calibration derived
2026-07-01 by structural scan; engine semantics are the console-verified
FSQ set. First show build still needs Brian's console verification.

BASELINE: Wireless 1-4 (faders 41-44) ship a starting vocal curve;
channels 1-39 are flat. MD-unnamed bands inherit the template.

Every run: md lint -> offset tripwire -> patch -> stray-byte +
do-not-write verification -> full readback of every MD channel.
Copy into the show folder as apply_<show>.py and run:
    python3 apply_<show>.py \
      --src  ".../Memorial Hall/_TEMPLATE/brian memo june 2026.ses" \
      --dest "<show folder>/<Show>.ses" \
      --md   "<Show> - FOH Channel Processing.md"

To recalibrate after a future template resave: rescan for the stride-125
surface run carrying the real fader names, walk the contiguous blocks
(the tripwire tells you it's stale), update the constants + name lists
below, then console-verify a test build.
"""
import sys, os

ENGINE_DIR = os.path.expanduser("~/Documents/Claude/audio/_shared")
sys.path.insert(0, ENGINE_DIR)
from q225_ses_engine import main_cli   # noqa: E402

CAL = dict(
    venue='memo',
    template_size=37_661_337,
    surf_base=0x231A48F,   # fader 1 surface-label slot (length byte)
    surf_stride=125,
    n_faders=72,
    block_mode='positional',
    block_base=0x2324D9C,  # channel 1 current-scene block (first name copy)
    block_stride=0x15A6,   # contiguous, one per channel
    block_pre=0x30,        # bounds: [first - pre, first + span)
    block_span=0x15A0,
    # Tripwire — surface-table names, faders 1..72:
    expected_names=[str(n) for n in range(1, 40)] + [
        'Click-Tap', 'Wireless 1', 'Wireless 2', 'Wireless 3', 'Wireless 4',
        'W1 Monitor', 'W2 Monitor', 'W3 Monitor', 'W4 Monitor', 'Hall',
        'Plate', 'Room', '1/4 Note Delay', '1/8 Note Delay', 'Drum Verb',
        'Snare Verb', 'Stage Ambience', 'Above Stage Mics', 'Floor Crowd',
        'Balcony Crowd', 'Video', 'QLab', 'Spotify', 'FOH Playback',
        'Mon TB', 'RTA', 'Pandora', 'Fx 1', 'Fx 2', 'Fx 3', 'Fx 4', 'Fx 5',
        'Fx 6',
    ],
    # Block order in the file != fader order — blocks are matched by name:
    expected_block_names=[str(n) for n in range(1, 40)] + [
        'Click-Tap', 'QLab', 'Above Stage Mics', 'Floor Crowd',
        'Balcony Crowd', 'Wireless 1', 'Wireless 2', 'Wireless 3',
        'Wireless 4', 'W1 Monitor', 'W2 Monitor', 'W3 Monitor', 'W4 Monitor',
        'Hall', 'Plate', 'Room', 'Mon TB', 'RTA', 'Video', 'Spotify',
        'Pandora', '1/4 Note Delay', '1/8 Note Delay', 'Drum Verb',
        'FOH Playback', 'Snare Verb', 'Stage Ambience', 'Fx 6', 'Fx 5',
        'Fx 4', 'Fx 3', 'Fx 2', 'Fx 1',
    ],
)

if __name__ == '__main__':
    sys.exit(main_cli(CAL))
