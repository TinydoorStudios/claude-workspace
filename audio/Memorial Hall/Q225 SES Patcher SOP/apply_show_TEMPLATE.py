#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — MEMORIAL HALL (Memo) venue wrapper.

All byte-level logic lives in the SHARED engine:
    ~/Documents/Claude/audio/_shared/q225_ses_engine.py
This file holds only the Memo template's calibration. Fix bugs in the
engine (both venues inherit); recalibrate templates here.

TEMPLATE: `Memorial Hall/_TEMPLATE/brian memo start sept 2026.ses`
(7,195,808 bytes, md5 77630594…, installed 2026-09-27 — Brian trimmed the
preset library in the offline editor. Section 1 shrank and everything after
it moved down by exactly 0x1D0DDF9: surf_base and block_base shift by that,
stride/geometry/names unchanged. The parameter vet vs the June file found
real channel changes — see memo-template-recalibration memory: ch 1-39 (not
4) HPF 20->25 Hz and LPF stored 25000->20000; B4 6300/Q0.71 -> 5162/Q3.93
(0 dB); ch 34/35 B4 -9.95 dB and B3 +9.81 dB @1.6k; ch 4/12 band freq/Q
moves at 0 dB; ch 33-39 0x0705 1->0; Hall (f49) 0x08E1 1->0.)

Previous: `brian memo june 2026.ses`
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
      --src  ".../Memorial Hall/_TEMPLATE/brian memo start sept 2026.ses" \
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
    template_size=7_195_808,
    surf_base=0x60C696,    # fader 1 surface-label slot (length byte)
    surf_stride=125,
    n_faders=72,
    block_mode='positional',
    block_base=0x616FA3,   # channel 1 current-scene block (first name copy)
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
