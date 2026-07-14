# Show Paperwork Processing Pipeline Spec — Fountain Square (FSQ)

*Adapted from the Memo pipeline. FSQ-specific differences are noted throughout.*

---

## 0. Session Startup

### Step 0 — Connect folders

Mount both at session start:

```
~/Documents/Claude/about-me
~/Documents/Claude/audio/Fountain Square
```

Also mount if doing show work:

```
~/Documents/Claude/audio/workflow start files
~/Documents/Claude/audio/Live Sound KB
```

### Step 1 — Read in order

```
~/Documents/Claude/about-me/about-me.md
~/Documents/Claude/about-me/writing-rules.md
~/Documents/Claude/about-me/memory.md
~/Documents/Claude/audio/Live Sound KB/Wiki/venue-fountain-square.md    ← FSQ PA, outdoor considerations
~/Documents/Claude/audio/workflow start files/eq-starting-points.md
~/Documents/Claude/audio/workflow start files/console-reference.md
~/Documents/Claude/audio/Fountain Square/Show Paperwork Pipeline Spec — FSQ.md   ← this file
```

**Key paths:**

```
Template .ses:    ~/Documents/Claude/audio/Fountain Square/brian fsq start.ses
Patcher template: ~/Documents/Claude/audio/Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py
Show folders:     ~/Documents/Claude/audio/Fountain Square/YYYY-MM-DD ShowName/
```

---

## 1. Pipeline Overview

Same three-stage structure as Memo. An Excel input list plus genre description enters the pipeline and produces:

- **Stage 1:** FOH Channel Processing document (MD + HTML + PDF) — on first request
- **Stage 2:** Python patcher script + DiGiCo Q225 `.ses` file — on explicit request only
- **Stage 3:** Show packet PDF — separate request, per CLAUDE.md

Nothing is built speculatively. Each stage waits for a request.

---

## 2. Input Format

### Primary upload

Excel spreadsheet (`.xlsx`). The FSQ patch sheet format:

| Ch | Instrument | MIC/DI | Split Patch | 48V | Stand | Notes | Location |

**Processing trigger:** The **MIC/DI column** determines whether a channel is processed.

- **MIC/DI populated** → include in EQ cards and .ses
- **MIC/DI empty** → skip entirely. No EQ card, no MD entry, no .ses strip write.

This applies throughout the pipeline. A channel with no mic listed is invisible to the patcher.

**Channel range:** Channels 1–32 only. Ignore anything above 32.

### Name handling

The input list Instrument name wins over the template. If the input list says "Keyboard 1" for Ch17, the console strip gets renamed to "Keyboard 1" — regardless of what the template currently has at that strip. If the input list name matches the template exactly, no rename occurs but EQ still writes.

Console Name ≤ ~12 characters for fader strip legibility on the Q225.

### Genre and influences

Required before EQ decisions. Same rule as Memo — ask if not provided. Genre drives tonal targets, dynamics approach, and Quick Summary language.

**FSQ note:** This is an outdoor PA with high ambient noise floor. Genre still matters for EQ decisions, but the room acoustics context in Quick Summaries should reflect outdoor conditions, not a reflective room.

---

## 3. Step 1 — FOH Channel Processing Document

### Three output files, always together

```
ShowName - FOH Channel Processing.md
ShowName - FOH Channel Processing.html
ShowName - FOH Channel Processing.pdf
```

PDF rendered from HTML via weasyprint. Not reportlab.

### Outdoor EQ approach (FSQ-specific)

FSQ is an open outdoor plaza. The acoustic context differs significantly from Memo:

- **No room acoustics to manage.** No RT60, no standing waves, no buildup from reflective surfaces.
- **Tighter gain-before-feedback margins.** Outdoor ambient noise (street, crowd, fountain) raises the noise floor. Build in headroom.
- **Wind on open mics.** Factor this into HPF decisions — outdoor HPFs trend higher than indoor equivalents for the same source.
- **Cuts over boosts, always.** Same rule as Memo for vocals — but apply it to all channels. The L-Acoustics A15 rig has clean high-end; there's rarely a need to boost.
- **No flutter echo or comb filtering from parallel walls** — the risk is SPL spillage into the surrounding street grid, not reflections.

### Vocal EQ — Locked Rule

**Vocals are cuts only. No boosts.** Same as Memo, and doubly important outdoors where feedback margins are tighter. If brightness is needed, solve it with mic choice and placement.

Applies to: handheld vocals, podium mics, and any channel where a human voice is the primary source.

### Reverb

**Minimal to none.** FSQ is outdoors. The natural environment has no reverb. Adding reverb muddies the image and competes with ambient reflections from surrounding buildings.

- For most shows: no reverb sends. Note this in the workflow reminders section.
- Exception: if the show specifically requests reverb (e.g., a vocal performer who has reverb in their in-ear mix and needs FOH to match), document it explicitly and keep it short and bright — not a hall.
- No Seventh Heaven Pro preset section in FSQ documents unless Brian asks for it.

### Per-channel card structure

Same locked format as Memo:

Dark navy (`#1c3558`) card header. 3-column table: **Section | Parameter / Value | Details**. Row order:

| Section label | Notes |
|---|---|
| Placement | Only when non-standard |
| HPF | Frequency @ slope |
| LPF | Frequency @ slope, or "Off" |
| Band1; High Shelf | gain @ freq, Q, Shelf |
| Band2; Upper-Mid (Param) | gain @ freq, Q |
| Band3; Lower-Mid (Param/Dyn) | gain @ freq, Q; DEQ in Details if active |
| Band4; Low (Param) *or* Band4; Low (Lowshelf) | match label to actual type |
| Dynamics 1; Compressor | full settings in Details |
| Dynamics 2; Gate *or* Dynamics 2; Ducker | label matches function |
| Polarity | Only where phase check required |
| Quick Summary | Full paragraph — genre, outdoor context, reasoning. Most important row. |

**No reverb send row** unless Brian asks. No global reverb section.

Band order: High → Low (bidx 0 = High Shelf, bidx 3 = Low). Matches Q225 physical layout. Locked.

Manual-entry channels: dark red (`#8b1a1a`) header with ★ MANUAL ENTRY.

### HTML structure (FSQ version)

1. Title: show name, console, venue, date
2. Input list summary table: Ch | Instrument | Mic/DI — **active channels only** (those with mic listed)
3. Per-channel cards in channel order
4. Critical notes — outdoor gain-before-feedback reminders, polarity warnings, stereo pair linking
5. Workflow reminders — VCA groups, manual-entry channels, anchor channel, reverb status

---

## 4. Step 2 — MD/HTML Conversion

### MD format (patcher source)

```
## Ch {N} | {Console Name} | {Mic/DI}
HPF: {hz} | LPF: {hz|OFF}
B1: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B2: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B3: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
```

Same rules as Memo. Only channels with mic listed appear in the MD.

---

## 5. Step 3 — .ses File Generation

**Target console: DiGiCo Quantum 225**

This step runs only on explicit request. Do not build the .ses speculatively.

### Source template

```
~/Documents/Claude/audio/Fountain Square/brian fsq start.ses
```

Never edit the template directly. Copy-and-patch into the show folder only.

### FSQ patcher constants (verified)

```python
STRIP1_HDR        = 0x011456    # ← DIFFERENT from Memo (0x0b0327)
STRIP_SIZE        = 5383        # ← DIFFERENT from Memo (5638)
# HPF is stored as TLV records — NOT a raw fixed offset like Memo's HPF_REL=406
TAG_HPF_FREQ      = 0x1d05      # HPF frequency — confirmed empirically in FSQ
TAG_HPF_FREQ2     = 0x1e05      # Second HPF instance (Q225 has two HPF filters per channel)
DISP_NAME_BASE    = 0x0a2a5a   # same as Memo
DISP_NAME_STRIDE  = 125        # same as Memo
NAME_SEARCH_END   = 0x0a5000
```

### Name replacement — STRIP-SCOPED (critical difference from Memo)

The FSQ template carries names from previous shows. Duplicate names exist across strips — "Kick In" appears at strips 19 and 23, "Rack 1" at strips 5, 21, and 27, etc. Searching the whole file for old_name would clobber wrong channels.

**Strategy:** Scan for name fields only within the target strip's byte range. **Do NOT write to the display name section** (DISP_NAME_BASE). Those 125-byte slots contain metadata beyond the 32-byte name field; writing name+zeros over them zeroes the metadata and crashes the console. Strip-scoped copies are sufficient for correct console display. (Verified 2026-05-29 on Verve Pipe at FSQ.)

### Current template name map

Use as `old_name` in the CHANNELS dict:

```
Ch 1: 'KICK IN'       Ch 2: 'SNARE TOP'    Ch 3: 'SNARE BOTTOM'
Ch 4: 'HI-HAT'        Ch 5: 'RACK 1'       Ch 6: 'FLOOR'
Ch 7: 'BASS DI'       Ch 8: 'BASS MIC'     Ch 9: 'GUITAR 3'
Ch10: 'KEY 1'         Ch11: 'CONGA 1'      Ch12: 'CONGA 2'
Ch13: 'BONGO'         Ch14: 'VOCAL 4'      Ch15: 'TINA'
Ch16: 'KICK IN'       Ch17: 'STAR'         Ch18: 'Nearfield R'
Ch19: 'Kick In'       Ch20: 'Snare Top'    Ch21: 'Rack 1'
Ch22: 'Rack 3'        Ch23: 'Kick In'      Ch24: 'Snare Top'
Ch25: 'Snare Bottom'  Ch26: 'Hat'          Ch27: 'Rack 1'
Ch28: 'Rack 2'        Ch29: 'Rack 3'       Ch30: 'OH Ride'
Ch31: 'OH Crash'      Ch32: 'Bass DI'
```

### EQ tags — verified safe (same as Memo)

```python
TAG_EQ_ENABLE  = 0x0404    TAG_EQ_GAIN    = 0x0403
TAG_EQ_FREQ    = 0x0406    TAG_EQ_Q       = 0x0407
TAG_EQ_TYPE    = 0x040b    TAG_DEQ_ENABLE = 0x040e
TAG_DEQ_THRESH = 0x0411    TAG_DEQ_ATK    = 0x0412
TAG_DEQ_REL    = 0x0410    TAG_LPF_FREQ   = 0x0703
```

### DO-NOT-WRITE tags (FSQ — differs slightly from Memo)

```python
0x1E0E, 0x1E0B, 0x1E11, 0x1E12,
0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12,
# 0x1D05 is NOT in the FSQ DO_NOT_WRITE list — it is the HPF frequency tag here
# (In Memo it was mislabeled Mustard; different tag assignment in FSQ firmware)
0x0503, 0x050e, 0x0511, 0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47
```

Do not write to `0x0a41c7` (reverb/room preset table) — same restriction as Memo.

SD comp/gate tags for FSQ are unconfirmed. Do not write them until verified via console-save-diff.

### Script

Copy `Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py` → `YYYY-MM-DD ShowName/apply_showname.py`. Fill the `CHANNELS` dict from the MD. Only include channels with a mic on the input list.

### Required verification before delivery

```
File size: matches template exactly (2,466,215 bytes for brian fsq start.ses)
Spot-check first channel: name field copies in strip: > 0
Do-not-write tag verification: PASS
```

FAIL on any = stop. Identify the cause before rerunning.

---

## 6. File Naming Convention

```
Show folder:     ~/Documents/Claude/audio/Fountain Square/YYYY-MM-DD ShowName/
MD:              ShowName - FOH Channel Processing.md
HTML:            ShowName - FOH Channel Processing.html
PDF:             ShowName - FOH Channel Processing.pdf
Patcher script:  apply_showname.py
.ses output:     ShowName.ses
```

---

## 7. Output Order and Delivery

1. **Stage 1:** Present MD, HTML, and PDF links simultaneously. All three or none.
2. **Stage 2:** Only when Brian asks. Present the file path and spot-check output. Wait for console report.
3. **Stage 3:** Separate request.

If Brian uploads an input list and says nothing else, produce Stage 1 only, then stop.

---

## 8. Invocation Pattern

```
Process this input list. Genre/influences: [description]. [Any per-channel notes.]
```

If genre is missing, ask before EQ. If channel notes are ambiguous, ask before committing. If everything is present, Stage 1 runs without further questions.

To trigger Stage 2:

```
Build the .ses from the MD.
```

---

## 9. FSQ-Specific Edge Cases

**Channels above 32**
Skip entirely. The FSQ pipeline only processes channels 1–32.

**Channels with no mic listed**
Skip entirely. No card, no MD entry, no strip write. The strip stays exactly as it is in the template.

**Duplicate template names**
The template has duplicate names across strips. The patcher uses strip-scoped name search — it will never accidentally rename the wrong channel. But when building the CHANNELS dict, always verify that the old_name you're using is actually the name in that specific strip (see the name map above).

**Template name update after a show**
After a show run, the .ses output will have the new channel names. If that show's .ses becomes the new FSQ starting template, update the name map in this spec and in the patcher template file.

**Outdoor HPF defaults trend higher than Memo**
Outdoor ambient noise and wind justify pushing HPFs up. A vocal that would get an 80 Hz HPF at Memo might get 100–120 Hz at FSQ. Note the reasoning in the Quick Summary.

**No reverb section**
If you find yourself writing a reverb section in an FSQ document without a direct request from Brian, stop and delete it.
