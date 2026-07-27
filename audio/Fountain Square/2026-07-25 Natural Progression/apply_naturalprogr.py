#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — FOUNTAIN SQUARE (FSQ) venue wrapper.

All byte-level logic lives in the SHARED engine:
    ~/Documents/Claude/audio/_shared/q225_ses_engine.py
This file holds only the FSQ template's calibration. Fix bugs in the
engine (both venues inherit); recalibrate templates here.

TEMPLATE: `Fountain Square/_TEMPLATE/brian fsq start.ses`
(39,910,618 bytes — full console save, 2026-07-25; recalibrated same day
against the desk-written USB original, calibration-test PASS).
Retired constants for reference:
  - 3,779,766-byte template (resaved 2026-06-21): SURF_BASE 0xA5571,
    SCAN 0x2D3000..0x33F000 — archived at `_TEMPLATE/_retired/`.
  - 2,466,215-byte template: SURF_BASE 0xA287A, SCAN 0x1A1000..0x1CC000.

This template is a full console save like Memo's, so the layout moved
wholesale: surface table at 0x231A42C, current-scene channel blocks at
0x2548000..0x25A3200 on a uniform 0x16AE stride, 19 in-block name copies
per fader (+1 surface slot = name×20). Block mode stays 'scan'.

CHANGED FADERS vs the retired template: 45/46 are no longer 'Ch 45'/'Ch 46'
— the desk auto-named them '4:Dnt64 57'/'4:Dnt64 58' (Dante card ports
57/58). All other 62 surface names are unchanged.

BASELINE: vocals/wireless (faders 25-36) ship a starting curve (HPF 184,
B4 -18 @5k Q20, B2 -6.3 @335); instrument channels 1-24 are flat.
MD-unnamed bands inherit the template.

Every run: md lint -> offset tripwire -> patch -> stray-byte +
do-not-write verification -> full readback of every MD channel.
Copy into the show folder as apply_<show>.py and run:
    python3 apply_<show>.py \
      --src  ".../Fountain Square/_TEMPLATE/brian fsq start.ses" \
      --dest "<show folder>/<Show>.ses" \
      --md   "<Show> - FOH Channel Processing.md"

To recalibrate after a future template resave: repeat the ZZTOP save-diff
(rename ch1/ch2 + known EQ in the DiGiCo offline editor, diff against the
template — reference pair in ~/.wine/drive_c/Projects/) and update
surf_base / scan_lo / scan_hi / expected_names below. The tripwire fails
loudly if you forget.
"""
import sys, os

ENGINE_DIR = os.path.expanduser("~/Documents/Claude/audio/_shared")
sys.path.insert(0, ENGINE_DIR)
from q225_ses_engine import main_cli   # noqa: E402

CAL = dict(
    venue='fsq',
    template_size=39_910_618,
    # Template channel-map gotchas (Brian, 2026-07-08, Hot Magnolias):
    #   fader 9 'Overheads' is a STEREO channel — BOTH overhead mics live on
    #   that one fader; never split an OH pair across 9/10.
    #   fader 10 'SNARE PL8' is the snare plate reverb RETURN, not an input —
    #   a show build once overwrote it; now hard-protected below.
    protected={10: "SNARE PL8 is the snare plate reverb return, not an input. "
                   "Overheads are STEREO on fader 9 (both mics, one fader) — "
                   "an OH pair never spills onto 10."},
    surf_base=0x231A42C,   # fader 1 surface-label slot (length byte)
    surf_stride=125,
    n_faders=64,
    block_mode='scan',
    scan_lo=0x2548000,     # current-scene channel-block region
    scan_hi=0x25A3200,     # f1 blk 0x2548497 .. f64 blk 0x25A2FE1, stride 0x16AE
    max_block_span=0x4000, # wider = non-unique name (FX returns) — refuse
    # Tripwire — surface-table names, faders 1..64:
    expected_names=[
        'Kick In', 'Kick Out', 'Snare Top', 'Snare Bottom', 'Hat', 'Rack 1',
        'Rack 2', 'Floor', 'Overheads', 'SNARE PL8', 'Bass DI', 'Bass Mic',
        'Guitar 1', 'Guitar 2', 'Guitar 3', 'Guitar 4', 'Misc 1', 'Misc 2',
        'Misc 3', 'Misc 4', 'Misc 5', 'Misc 6', 'Misc 7', 'Misc 8', 'Vocal 1',
        'Vocal 2', 'Vocal 3', 'Vocal 4', 'Vocal 5', 'Vocal 6', 'Vocal 7',
        'Vocal 8', 'Wireless 1', 'Wireless 2', 'Wireless 3', 'Wireless 4',
        'Hall', 'Plate', 'Room', 'Delay', 'Bricasti 1', 'Bricasti 2',
        'Bricasti 3', 'Bricasti 4', '4:Dnt64 57', '4:Dnt64 58', 'Ch 47',
        'Ch 48',
        'Ch 49', 'Ch 50', 'Ch 51', 'Ch 52', 'Ch 53', 'Ch 54', 'Ch 55',
        'Ch 56', 'Ch 57', 'Ch 58', 'Mon 2 FOH', 'RTA', 'Hotshot 2 FOH',
        'Tech Feed', 'Crowd', 'Pandora',
    ],
)

if __name__ == '__main__':
    sys.exit(main_cli(CAL))
