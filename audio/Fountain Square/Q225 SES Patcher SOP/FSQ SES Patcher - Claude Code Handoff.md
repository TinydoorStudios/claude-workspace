# FSQ .ses Patcher — Claude Code Handoff

> **UPDATE 2026-07-01:** the FSQ patcher is now a thin calibration wrapper over
> the shared engine `audio/_shared/q225_ses_engine.py` (one engine for Memo +
> FSQ; regression-proven md5-identical to the standalone, incl. the Izzy 2.0
> Deep Think build). Every run now auto-lints the MD (`_shared/md_lint.py`)
> and auto-reads back every MD channel from the output. The pre-engine
> standalone is archived as `apply_show_TEMPLATE_FSQ_pre-engine_standalone.py`.
> Everything below about the .ses layout and calibration still applies.


Brian runs FOH on a DiGiCo Q225 at Fountain Square (FSQ). This doc tells you how to
turn a show's **FOH Channel Processing .md** into a loadable Q225 **.ses** showfile,
save it for Brian to verify, and — once he confirms — push the show into his Wiki.js.

This was reverse-engineered the hard way. The methods below are **console-verified**
(they reproduce a real Q225 save byte-for-byte). Do not "improve" the byte offsets or
swap in constants from the Memorial Hall patcher — FSQ stores channel data in a
different place and the Memo constants produce files that silently fail to load.

---

## What you have

- `apply_show_TEMPLATE_FSQ.py` — the patcher. Engine + verifier. Already validated.
- `brian fsq start.ses` — the FSQ template. Brian uploads this the **first time only**;
  after that, keep a copy as the canonical base (see Setup).

## What you produce, per show

1. `<Show>.ses` — the patched showfile, saved in the show folder.
2. The rest of the packet, all from the same deep-research source data:
   `<Show> - FOH Channel Processing.md` (patcher input), `<Show> - Input List.xlsx`,
   `<Show> - Show Packet.pdf`, `<Show>_<show>.spec.json`, and the **`<Show> - FOH EQ
   Reasoning.pdf`** (the required EQ Rationale — per-channel *why*, plus a "what changed
   from the KB default / prior rev" box). Reference build: `Izzy 2.0 Deep Think/`.
3. (Brian verifies on the console — hard stop here.)
4. The show paperwork + `.ses` ingested into Wiki.js and pushed.

**EQ is deep-research standard (set 2026-06-24).** The `.md` this patcher consumes is the
output of the deep-research EQ pass — artist + genre researched first, then each source
researched mic × instrument × genre × venue against the KB floor. Don't feed this patcher a
generic KB-default `.md`; the whole point is reasoned values with the *why* captured in the
Rationale PDF.

---

## Scope — what the patcher writes (and what it does NOT)

**Written, confirmed (region by console-save-diff 2026-06-09; values by DiGiCo
offline-editor save-diff 2026-06-10, `klaud edited.ses` vs template):**
- Fader **display name** (all ~20 copies in the channel's current-scene block — partial
  writes do not stick; this was the original bug).
- **EQ** per band: gain, freq, Q, type (shelf/bell), and active-band count.
- **HPF** — stored = **0.8 × displayed Hz** (display 84.1 → stored 67.24; display
  20 → 16.0). The patcher applies the scale; the .md stays in display Hz.
- **LPF** — stored = **1.25 × displayed Hz** (display 5.75 kHz → stored 7191;
  off/20 kHz → 25000). Same: .md stays in display Hz.
- **Dynamic EQ (DEQ)** per band: enable `0x040E`, thresh `0x0411` (dB), attack
  `0x0412` (s), release `0x0410` (s).
- Optional **comp threshold** `0x050F` bidx 0–2 (the three linked multiband slots).

**NOT written — Brian dials these by hand at soundcheck:**
- **Compressor** beyond threshold, **gate** beyond its enable (`0x050E` bidx 3 is
  the gate enable; other gate/comp tags unmapped).

**Channels not in the .md are left 100% untouched (passthrough).**

**Band order (bit Blue Eighty-Eight — do not regress):** file bidx 0 = HIGHEST
band, bidx 3 = LOWEST (template defaults 6300/1600/300/100 Hz). The .md uses
console numbering (B1 = low … B4 = high, locked 2026-05-30), so the patcher maps
**B1→bidx3 … B4→bidx0**. The old code mapped B1→bidx0 and reversed every
channel's EQ (shelves inverted).

---

## Input format — FOH Channel Processing .md

```
## Ch 9 | BASS DI | Radial ProDI
HPF: 40 | LPF: 5000
B4: +2 | 2500 | 0.8 | SHELF
B3: +2 | 800 | 1.5 | BELL
B2: -4 | 250 | 2.0 | BELL | DEQ: thr=-16 atk=10ms rel=100ms
B1: +3 | 80 | 1.2 | SHELF
```

- `## Ch N | NAME | MIC` — N is the fader number, NAME is the new fader label.
- `B1..B4` are CONSOLE band numbers: **B1 = Low, B4 = High** (Brian's locked
  convention). List them high→low in the file for readability; line order
  doesn't matter to the parser. `FLAT` = bypassed band.
- HPF/LPF are display Hz (`LPF: OFF` = no LPF); DEQ values are dB/ms. All are
  parsed AND written — the patcher handles the stored-value scaling itself.

---

## Setup (first run only)

1. Brian uploads `brian fsq start.ses` and the show's `.md`.
2. Save the template as the canonical base at:
   `~/Documents/Claude/audio/Fountain Square/_TEMPLATE/brian fsq start.ses`
   (create `_TEMPLATE/` if missing). Reuse it for every later show — Brian only
   uploads the .md from then on.
3. Confirm the **Wiki.js git repo path** with Brian and record it in your project notes /
   CLAUDE.md so you don't ask again. (It's a Wiki.js deployment backed by a git repo.)

---

## Per-show workflow

### 1. Gather inputs
- Show's `.md` (always). Template from `_TEMPLATE/` (or Brian's upload first run).
- **Ask Brian the show date** (the .md has no date). Derive the **show name** from the
  .md filename (e.g. `Blue Eighty-Eight - FOH Channel Processing.md` → `Blue Eighty-Eight`).

### 2. Create the show folder
`~/Documents/Claude/audio/Fountain Square/YYYY-MM-DD ShowName/`
(date first, so folders sort chronologically — Brian's standard.)

### 3. Patch
```
python3 apply_show_TEMPLATE_FSQ.py \
  --src  "~/Documents/Claude/audio/Fountain Square/_TEMPLATE/brian fsq start.ses" \
  --dest "~/Documents/Claude/audio/Fountain Square/YYYY-MM-DD ShowName/ShowName.ses" \
  --md   "path/to/<Show> - FOH Channel Processing.md"
```
Also drop the source `.md` (and any `.html`/`.pdf` paperwork Brian provides) into the
show folder.

### 4. Verify the output (automatic gate — must pass before you hand it over)
The script prints a verification block. Require:
- `bytes changed outside mic'd blocks: 0  PASS`
- File size **identical** to the template (3,779,766 bytes — new template, 2026-06-21).
- Each processed fader shows `name×20` (not fewer — fewer means the name won't stick).

If any of these fail, **stop and report** — do not give Brian the file.

### 5. HARD STOP — Brian verifies on the console
Tell Brian the `.ses` is in the show folder and list which faders/EQ were written and
which knobs (HPF/LPF/dynamics) he still needs to dial. **Wait for him to load it on the
Q225 and say "verified." Do not proceed to the wiki until he does.**

### 6. After Brian says verified — ingest to Wiki.js and push
1. In the Wiki.js git repo, create/update a page for the show under a Fountain Square
   path, e.g. `fountain-square/YYYY-MM-DD-showname.md`. Include: input list summary,
   per-channel EQ decisions, mic choices, and a file index of the show folder. (First
   run: confirm the repo's folder convention with Brian, then follow it consistently.)
2. Add the show's paperwork (`.md`/`.html`/`.pdf`) to the repo. Put the binary `.ses`
   in the repo's assets/uploads location so it's linkable from the page.
3. Commit and push:
   ```
   git add .
   git commit -m "Add Fountain Square show: YYYY-MM-DD ShowName"
   git push
   ```
4. Confirm the push succeeded and report the wiki page path/URL back to Brian.

---

## Guardrails

- **Never** copy Memo patcher constants into the FSQ patcher.
- **Never** enable `WRITE_HPF` / `WRITE_LPF` without a fresh console-save-diff calibration.
- The output file size must always equal the template's. The script asserts this.
- Only touch channels present in the .md. Everything else is passthrough.
- The console save is the source of truth. If anything seems off, do a save-diff
  (load template, change one thing on one channel, save, diff) before trusting a theory.

---

## Technical reference (for trust / repair only — the script already encodes this)

Confirmed against `brian fsq start.ses` by console-save-diff:

- **Surface-label table** (fader display name): base `0xA5571`, stride `125` bytes/fader.
  *(Recalibrated 2026-06-21 — old base `0xA287A`. See the addendum below.)*
- **Current-scene channel blocks** (where names + EQ actually live and the console reads
  on recall): region `0x2D3000`–`0x33F000`, ~5760 bytes/fader, contiguous in fader order.
  *(Recalibrated 2026-06-21 — old region `0x1A1000`–`0x1CC000`.)*
- **Name** must be written to the surface slot **and** every copy in the fader's
  current-scene block (~20 total). The script locates the block by the fader's existing
  template name, so it's robust per fader.
- **EQ tags** (8-byte TLV: float value, then `<H tag><H bidx>`), inside the EQ window
  anchored on band-0 freq:
  - gain `0x0403`, freq `0x0406`, Q `0x0407`, type `0x040B` (1.0 shelf / 2.0 bell),
    active-band count `0x0405` (bidx 0).
- **LPF** `0x0703` bidx 1 (located, but write disabled). **Comp threshold** `0x050F`
  bidx 0 (confirmed). **HPF** lives just after the LPF record (tag field reads `0xFFFF`),
  value ≈ 0.8×freq — not calibrated, do not write.
- The old "EQ strip" region (`STRIP1_HDR=0x11456`, stride 5383) the earlier FSQ attempts
  used is the **wrong region** — the console does not read it on recall. That's why those
  files showed no names and no EQ.

---

## Addendum 2026-06-10 — filters calibrated, band order fixed (RESOLVED)

Brian edited Ch 6 in the DiGiCo offline software and saved `klaud edited.ses`
(kept with the template in `~/.wine/drive_c/Projects/` as the reference pair).
The diff against the template settled everything:

- **HPF stored = 0.8 × display** (84.1 Hz → 67.243; the field is the float at
  LPF value offset + 0x10 under a `0xFFFF` tag — same record as Memo's
  `HPF_REL=406`). **LPF stored = 1.25 × display** (5.75 kHz → 7191; off →
  25000 = 1.25 × 20 kHz). Both writes are now ENABLED in the patcher.
- **bidx 0 = HIGH band … bidx 3 = LOW band** (screenshot bands 2.55k/2.29k/
  110/43.9 landed at bidx 0/1/2/3). The patcher now maps B1→bidx3 … B4→bidx0.
- **DEQ confirmed:** enable `0x040E`, thresh `0x0411` (−24.5 dB), attack
  `0x0412` (0.0172 s = 17.2 ms), release `0x0410` (0.695 s = 695 ms), all at
  the band's bidx. DEQ ratio/over-under tags not identified (unchanged = 2:1
  default in the diff).
- **Comp threshold `0x050F` bidx 0–2** move together (three multiband slots,
  −27.3 in the diff). **Gate enable = `0x050E` bidx 3** (0→1). `0x0503` bidx 0
  went 1→0 in the same edit — unidentified, leave alone. Note: `0x0503`/`0x050E`
  sit on the Memo DO-NOT-WRITE list labeled "Mustard" — that label is wrong;
  they're SD comp/gate controls. Keep not writing them until deliberately mapped.
- Every name copy is followed by a float64 save-timestamp (days since 1900) —
  that's the file-wide 6-byte diff noise on every save; ignore it.
- The old strip region also went 0 bytes changed in this save — further proof
  the console/editor never touches it.

`Blue Eighty-Eight.ses` was rebuilt 2026-06-10 with the corrected engine
(names + EQ + HPF + band order; all LPF OFF in that show). The
`_TEMPLATE/Filter Calibration/` kit is obsolete — superseded by this diff.

---

## Addendum 2026-06-21 — new template + recalibration (CURRENT)

Brian resaved the FSQ template. The new `brian fsq start.ses` is **3,779,766 bytes**
(was 2,466,215) — "everything changed": many more snapshots and a baked-in
vocal/wireless starting curve. Every absolute offset shifted (the file diverges from
the old one at byte `0x22`), so the patcher was recalibrated. **The byte format is
unchanged — only the constants moved.**

- **Recalibration method (repeat this for any future resave):** in the DiGiCo offline
  editor, open the new template, rename ch1→`ZZTOP1` and ch2→`ZZTOP2`, set known
  EQ/HPF/LPF/DEQ/comp on ch1, Save As a second file, and diff the pair. Both files are
  kept in `~/.wine/drive_c/Projects/` (`brian fsq start.ses` vs `fsq edited new.ses`).
  The 2026-06-21 diff re-confirmed every semantic on the new file: bidx order
  (b0 = high), HPF ×0.8 (100 Hz → 79.1), LPF ×1.25 (8 kHz → 9953), DEQ + comp tags.
- **New constants:** `SURF_BASE 0xA5571`, `SCAN_LO 0x2D3000`, `SCAN_HI 0x33F000`
  (stride 125 unchanged, 64 faders Kick In…Pandora).
- **Offset tripwire (new):** the patcher reads the 64 fader names on load and aborts if
  they don't match `EXPECTED_NAMES`. A future resave (or wrong `--src`) now fails loudly
  instead of silently writing to the wrong region. To recalibrate, update
  `SURF_BASE` / `SCAN_LO` / `SCAN_HI` / `EXPECTED_NAMES` together. A block-span guard
  also skips any non-unique name (e.g. FX returns Hall/Plate/Room/Delay/Bricasti, faders
  37–44) so they can't cause a wild write.
- **Vocal/wireless baseline (faders 25–36):** the template ships these with a starting
  curve — HPF 184, B4 −18 dB notch @5 kHz Q20, B2 −6.3 @335, small B1/B3 moves.
  Instrument channels 1–24 are flat. **Per Brian (2026-06-21): keep the curve.** The
  patcher writes only MD-named bands and leaves the rest, so vocal shows inherit the
  baseline unless an MD overrides it. Paperwork lists only MD-named bands.
- Verified end-to-end 2026-06-21: synthetic CAL test (ch1/13/25) built, patcher PASS
  + read-back match, and Brian confirmed the load on the Q225.
