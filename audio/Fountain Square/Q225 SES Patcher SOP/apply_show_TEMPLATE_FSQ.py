#!/usr/bin/env python3
"""
DiGiCo Q225 .ses show patcher — FOUNTAIN SQUARE (FSQ) venue wrapper.

All byte-level logic lives in the SHARED engine:
    ~/Documents/Claude/audio/_shared/q225_ses_engine.py
This file holds only the FSQ template's calibration. Fix bugs in the
engine (both venues inherit); recalibrate templates here.

TEMPLATE: `Fountain Square/_TEMPLATE/brian fsq start.ses`
(39,910,700 bytes — full console save, installed 2026-08-01 from
`~/.wine/drive_c/Projects/brian fsq start july 2026.ses`).

The 2026-08-01 save is a RENAME-ONLY RESAVE of the 2026-07-26 template:
identical block bounds, EQ windows and LPF offsets on all 64 faders, and
ZERO changes to any EQ / filter / DEQ / Mustard / protected-tag value
anywhere in the channel blocks (parameter-level diff, not a byte guess).
Only two constants changed below — template_size and two surface names.
Calibration test (ch 1/13/25) PASS on the new file.
Deltas vs 2026-07-26:
  - fader 57 'Ch 57' -> 'Click - Tempo'   (all 20 name copies)
  - fader 58 'Ch 58' -> 'FOH Playback'    (all 20 name copies)
  - +82 bytes at 0x260F569, in the macro/panel table well past every
    patcher write path: a new macro entry 'Auto Tempo' (sits right after
    'Aux to Faders panel'). Name slots are fixed width, so the renames
    themselves cost nothing and shifted no offsets.
Everything else that differs is the desk's object-ID renumbering
(~3,100 six-byte runs).

Prior template (2026-07-26, 39,910,618 bytes) audio baseline, still true:
faders 6/7/8 (Rack 1 / Rack 2 / Floor) ship the native gate ENABLED —
thr -36.2 dB, rel 227 ms, sidechain band 130 Hz - 317 Hz.

Retired constants for reference:
  - 3,779,766-byte template (resaved 2026-06-21): SURF_BASE 0xA5571,
    SCAN 0x2D3000..0x33F000 — archived at `_TEMPLATE/_retired/`.
  - 2,466,215-byte template: SURF_BASE 0xA287A, SCAN 0x1A1000..0x1CC000.

This template is a full console save like Memo's, so the layout moved
wholesale: surface table at 0x231A42C, current-scene channel blocks at
0x2548000..0x25A3200 on a uniform 0x16AE stride, 19 in-block name copies
per fader (+1 surface slot = name×20). Block mode stays 'scan'.

NAMED SPARES: 45/46 are '4:Dnt64 57'/'4:Dnt64 58' (the desk auto-named
them after the Dante card ports). As of 2026-08-01, 57/58 are named too —
'Click - Tempo' and 'FOH Playback' — so the free spare range is now
faders 47-56, not 47-58.

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
    template_size=39_910_700,
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
        'Ch 56', 'Click - Tempo', 'FOH Playback', 'Mon 2 FOH', 'RTA',
        'Hotshot 2 FOH', 'Tech Feed', 'Crowd', 'Pandora',
    ],
)

if __name__ == '__main__':
    sys.exit(main_cli(CAL))
