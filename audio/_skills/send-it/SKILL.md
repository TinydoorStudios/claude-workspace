---
name: send-it
description: Builds a DiGiCo Q225 .ses showfile from a show's FOH Channel Processing .md, against the correct venue template. Trigger when Brian says "send it fsq", "send it memo", "send it" plus a venue name, or asks to build/process/patch a .ses from paperwork. NOT the wiki push — when Brian gives the go to publish a built show, that's the show-wiki-push skill. Brian always names the venue; if he didn't, ask which one.
---

# Send It — MD paperwork → Q225 .ses

Takes the show's `* - FOH Channel Processing.md`, applies it to the venue's
master template .ses with the SOP patcher, verifies the output byte-level, and
delivers a console-ready file. One venue per run. Brian says which: **fsq** or
**memo**.

This pipeline is fully calibrated (2026-06-10 save-diff, `~/.wine/drive_c/Projects/klaud edited.ses`
vs template). Do not re-derive offsets, do not "improve" constants, do not mix
venue constants. The patcher scripts already encode everything.

## Paths

| Venue | Template (never edit) | SOP patcher | Show folders |
|---|---|---|---|
| fsq | `~/Documents/Claude/audio/Fountain Square/_TEMPLATE/brian fsq start.ses` | `~/Documents/Claude/audio/Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py` | `~/Documents/Claude/audio/Fountain Square/YYYY-MM-DD ShowName/` |
| memo | `~/Documents/Claude/audio/Memorial Hall/_TEMPLATE/brian memo june 2026.ses` | `~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py` | `~/Documents/Claude/audio/Memorial Hall/YYYY-MM-DD ShowName/` |

Template sizes (output must match exactly): fsq **39,910,700** bytes
(full console save, 2026-08-01 drop; earlier templates retired to
`_TEMPLATE/_retired/`), memo **37,661,337** bytes
(`brian memo june 2026.ses`, swapped in 2026-07-01 — the old 1,543,866-byte
`brian memo v2.ses` is retired).
Both patchers carry an offset tripwire and abort if the template's fader
names don't match their calibration — a resaved template fails loudly;
recalibrate, don't force it.

## Procedure

### 1. Resolve the show
If Brian named the show, use that folder. Otherwise check `show.status.json` in
the venue's recent show folders
(`python3 ~/Documents/Claude/audio/_shared/show_status.py show --folder <dir>`) —
the show sitting at `packet_built` without `ses_built` is the one. Fall back to
the newest dated folder containing a `* - FOH Channel Processing.md`. If it's
ambiguous which show he means, ask — one question, then move.

### 2. Sanity-check the MD (automated hard gate)
Both patchers consume the locked MD format (B-numbers are CONSOLE bands:
**B1 = low, B4 = high**, locked 2026-05-30) and run `_shared/md_lint.py`
automatically before touching a byte — backwards band order (pre-2026-05-30
MDs), missing HPF/LPF lines, malformed bands, and console-limit violations
all ABORT the run with `lint ERROR` lines. If lint aborts, fix the MD or
**stop and ask Brian** — never force it. Lint warnings (name >12 chars,
fractional dB) don't block but should be surfaced to Brian.

### 3. Patch
Run the venue patcher directly — never copy it into the show folder (copies go
stale the moment a template is recalibrated). Same CLI for both venues:

```bash
python3 "<venue SOP patcher>" \
  --src  "<venue template .ses>" \
  --dest "<show folder>/<Show Name>.ses" \
  --md   "<show folder>/<Show Name> - FOH Channel Processing.md"
```

The patchers handle everything internally: name writes (surface slot + all ~20
scene copies on fsq; all ~20 file-wide copies on memo), EQ band mapping
(B1→bidx3 … B4→bidx0; bidx 0 is the HIGHEST band in the file), HPF stored =
0.8 × display Hz, LPF stored = 1.25 × display (off = 25000), DEQ (ms→seconds).
Channels not in the MD are left 100% untouched.

### 4. Verify (hard gate — no PASS, no delivery)
The run must print ALL of these (both venues — the shared engine at
`audio/_shared/q225_ses_engine.py` runs the full battery every build):
- every fader `name×20` (never 0 or 1)
- `bytes changed outside mic'd blocks: 0  PASS`
- `do-not-write tags modified: 0  PASS`
- `readback: PASS` — the engine automatically re-reads EVERY MD channel
  from the output (names, all bands at the mapped bidx, HPF ×0.8 /
  LPF ×1.25 scaling, DEQ) and compares against the MD
- file size = template size (fsq 39,910,700 · memo 37,661,337)

Any FAIL or `!!` line = stop, report, do not deliver. To re-verify an
existing .ses later without rebuilding:
`python3 ~/Documents/Claude/audio/_shared/readback_verify.py --venue fsq|memo --ses <file> --md <md>`.

### 5. Report and hard stop
Tell Brian: channels written, filters written, what he still dials by hand
(comp beyond threshold, gates — not in the .ses scope), and the file path.
**Console verification is NOT a publish gate** (rule 2026-07-19: shows are
one-offs — the .ses gets loaded at the show itself; never ask Brian to load-test
it first). The engine stamps `ses_built` in the show's `show.status.json` on a
PASS build. The wiki push happens on Brian's explicit go ("push to wiki" /
"SEND IT") and is the `show-wiki-push` skill, not this one. If Brian volunteers
that the file ran on the desk, stamp it (informational):
`python3 ~/Documents/Claude/audio/_shared/show_status.py stamp --folder "<show folder>" --stage verified`.

## Guardrails

- Never write to the template files. Copy-and-patch only.
- Never mix venue constants — both templates use the surface-table +
  current-scene-block layout, but every absolute offset is venue-specific
  (fsq: SURF 0x231A42C, scan 0x2548000–0x25A3200 stride 0x16AE; memo:
  SURF 0x231A48F, blocks from 0x2324D9C stride 0x15A6). The two SURF bases
  are now coincidentally close — both templates are full console saves — so
  read the venue off the patcher, never off the offset. The patcher scripts
  are the source of truth; their tripwires catch a mismatch. Old dead
  regions (fsq 0xA5571 / 0x2D3000–0x33F000 and 0x11456 strips, memo
  0x0b0327 strips) are pre-recalibration data — never resurrect them.
- Mustard dynamics are **documented, never written** (writer console-verified
  2026-07-16, then pulled from the build the same day on Brian's call — he
  didn't like the live activation). `COMP:` / `GATE:` lines in the MD are
  paperwork: `md_lint` validates their syntax and the build log flags them
  `[doc-only]`, but the patcher does not touch Mustard bytes. The writer code
  stays in the engine for lint; decode notes in `audio/_shared/mustard-cal/`.
- If the patcher prints `!!` warnings (name fields 0/1, EQ window not found,
  HPF marker not 0xFFFF), the output is not trustworthy — diagnose before
  delivering.
- Full background: `Q225 SES Patcher SOP/` in each venue folder; KB articles
  `pipeline-spec-fsq`, `pipeline-spec-memo`, `console-digico-q225` — read them
  LIVE from `~/Documents/Claude/audio/Live Sound KB/Wiki/` (this skill keeps
  no local copies; the live KB is the single source of truth).
