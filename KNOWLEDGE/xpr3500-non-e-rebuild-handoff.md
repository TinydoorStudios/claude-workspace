# HANDOFF — XPR 3500 (non-e) codeplug rebuild

**Date:** 2026-08-05 · **Paste this as the opening message of a fresh chat.**

---

## Operating rules for this task (read first)

The previous session died from context bloat — ~60 full-screen screenshots. Do not repeat that.

- **Never take a full screenshot as a default.** Use `zoom` on the exact grid rows you just edited. A full frame is only justified when you genuinely have to relocate a window or the tree shifted.
- **One verification zoom per batch**, cropped to the row(s) touched — e.g. `zoom region [195, <row_y-9>, 1300, <row_y+9>]`.
- **Batch aggressively.** A full channel row (7 field edits) fits in one `computer_batch` call. End it with the zoom.
- Brian's hard rule: **do not narrate work in progress.** Execute, report when done.

---

## The problem this solves

Brian's radio fleet is two generations:

| Model | CPS that can read/write it | Status |
|---|---|---|
| XPR **3500e** | MOTOTRBO CPS 2.0 (2.157.149.0 — newest) | fine |
| XPR **3500** (non-e) | legacy MOTOTRBO **CPS 16** | needed rebuild |

The non-e radios carry codeplug version 06.03.10, which is *below* CPS 2.0's supported floor for the Paradise family. CPS 2.0 read fails 5/5 with `[#101005] BLCompile_UnsupportedVersion_For_Unpacking`. That is not a cable fault and not a CPS-too-old fault — it's the wrong CPS generation. The two generations cannot share a codeplug, and Clone cannot bridge them (`[#1001828]` requires matching model numbers).

So: the non-e fleet needs its own codeplug, hand-built in CPS 16, carrying the 3500e master's channels.

---

## Environment

- **Surface PC**, reached over **AnyDesk** (set AnyDesk menu → Keyboard → **Local** or keystrokes garble).
- **CPS 16** installed at `C:\Program Files (x86)\Motorola` — build `cps_16dot0_build828_standalone`.
- CPS 2.0 also installed (for reading the 3500e master only).
- Windows user is `lake`; everything lives on `C:\Users\lake\Desktop\`.

**Files on that desktop:**

| File | What |
|---|---|
| `XPR3500 non-e MASTER 2026-08-05.ctb` | **the build in progress** (CPS 16) |
| `XPR3500 MASTER 2026-07-29.xctb` | the 3500e master (CPS 2.0), source of truth |
| `Event One FX CP200 4 Channel Digital.xctb` | Event One FX's own radio, used to verify the talkgroup |
| `XPR3500 MASTER 2026-07-29 - Channels Summary.mht` | full text dump of the master |
| `EventOneFX CP200 - Channels Summary.mht` | full text dump of the CP200 |

**How to re-extract report data without screenshots:** in CPS 2.0 open the codeplug → `File → Reports → Channels Summary → Save` as `.mht` to the desktop → open that file in Chrome via `file:///C:/Users/lake/Desktop/<name>.mht` → `Ctrl+A`, `Ctrl+C` → then call `read_clipboard` on the Mac (needs the `clipboardRead` grant on `request_access`). This gives exact frequencies as text instead of OCR off a screenshot. This is how all the data below was obtained.

---

## Brian's rulings (already applied unless noted)

- Drop **ZIEGLER** and **BBB**.
- Drop anything **"garage"** — FSQ-GARAGE and WP-GARAGE deleted.
- **Keep MEM-PROD** (added).
- Keep his own **F/R-LLC** and **Memo FOH** (these are not in the 3500e master; they are deliberate).
- **No scan lists.** All channels set to Scan List = None. CPS 16 refuses to delete the last scan list ("Minimum of 1 item is required"), so `List1` still exists but has been emptied of all members.

---

## BUILD STATE

### Zone 1 — 3CDC · 8 channels · COMPLETE & VERIFIED

| Pos | Channel | RX/TX MHz | DPL |
|---|---|---|---|
| 1 | FSQ-OPS | 451.0375 | 043 |
| 2 | FSQ-PROD | 451.2125 | 116 |
| 3 | WP-OPS | 451.6875 | 174 |
| 4 | WP-PROD | 451.8875 | 331 |
| 5 | OTR-DIST | 452.4625 | 734 |
| 6 | F/R-LLC | 451.6875 | 265 |
| 7 | Memo FOH | 451.6875 | 067 |
| 8 | MEM-PROD | 451.2125 | 244 |

*MEM-PROD landed at position 8 (after Memo FOH). In the 3500e master it sits at 8 with MEM-FOH at 9 — ask Brian whether he wants it moved up in the knob order.*

### Zone 2 — AMERICAN FIREWRK · 10 channels · COMPLETE & VERIFIED · all DPL **225**

| Pos | Channel | RX/TX MHz | | Pos | Channel | RX/TX MHz |
|---|---|---|---|---|---|---|
| 1 | AFX 1i | 462.8625 | | 6 | AFX 6 - Cinci | 464.8250 |
| 2 | AFX 2i | 467.8625 | | 7 | AFX 7 - Cinci | 469.8250 |
| 3 | AFX 3i | 456.8000 | | 8 | AFX 8 - Cinci | 464.1250 |
| 4 | AFX 4i | 464.5500 | | 9 | AFX 9 - Cinci | 469.1250 |
| 5 | AFX 5i | 462.8375 | | 10 | AFX 10 - Cinci | 467.8500 |

### Zone 3 — Rozzi · 16 channels · COMPLETE & VERIFIED · all DPL **023**

| Pos | MHz | | Pos | MHz | | Pos | MHz | | Pos | MHz |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 464.5500 | | 5 | 456.8620 | | 9 | 467.9250 | | 13 | 467.8120 |
| 2 | 456.7870 | | 6 | 456.8870 | | 10 | 467.9000 | | 14 | 467.7620 |
| 3 | 456.8120 | | 7 | 469.5500 | | 11 | 467.8750 | | 15 | 464.8250 |
| 4 | 456.8570 | | 8 | 469.5000 | | 12 | 467.8750 | | 16 | 467.7120 |

*Rozzi 11 and 12 are both 467.8750 in the 3500e master too. Reproduced deliberately, not a typo. Brian was told.*

### Zone 4 — Event One FX · 4 DIGITAL channels · **IN PROGRESS**

Contact **created and verified**: `Contacts → Digital → EVENT ONE FX`, Digital Calls–Group Call, **Call ID 10010**. Confirmed independently against both the 3500e master and Event One FX's own CP200 — both read 10010.

Target values (channel names `Channel1`–`Channel4` match the master exactly, no renaming needed):

| Pos | Channel | RX/TX MHz | Color Code | Slot | Contact |
|---|---|---|---|---|---|
| 1 | Channel1 | 464.5000 | 4 | 1 | EVENT ONE FX |
| 2 | Channel2 | 464.5500 | 4 | 1 | EVENT ONE FX |
| 3 | Channel3 | 469.5000 | 4 | 1 | EVENT ONE FX |
| 4 | Channel4 | 469.5500 | 4 | 1 | EVENT ONE FX |

Also: ARS Disabled, Privacy No, Group List None, Admit Always, Data Call Confirmed Yes, Power High, TOT 60, Repeater/Time Slot already defaults to 1.

**Done so far:** rows 1 and 2 have RX and TX frequencies set correctly (464.5000 / 464.5500).

**⚠ KNOWN BAD — fix first:** the Color Code on rows 1 and 2 reads **14**, not 4. The `ctrl+a` failed to clear the existing `1` and the typed `4` appended to it. 14 is a legal color code so CPS accepted it silently. Re-check and correct both, and watch for the same failure everywhere — see the edit pattern below.

**Still to do in this zone:** rows 3 and 4 frequencies; Color Code 4 on all four; Contact Name = EVENT ONE FX on all four (that column is off-screen right, needs horizontal scroll).

---

## REMAINING WORK after Zone 4

1. **Admit Criteria + RSSI Threshold.** In the 3500e master, AMERICAN FIREWRK and Rozzi are all **Admit = Channel Free, RSSI = −124 dBm**; 3CDC is **Always**. Currently everything sits at the CPS default of Always. 26 channels × 2 fields. Both columns are off-screen right.
2. **Save**, then generate `File → Reports` out of CPS 16 and diff it against the master's report line by line.
3. **Brian checks it line by line before anything is written to a radio.** He asked for this explicitly. Do not write to a radio without his go.
4. **Wiki.** Brian asked for all of this to go on the Live Sound KB wiki. Not started. Use the `wiki-publish` skill. Should cover the two-generation split, the `[#101005]` diagnosis, the CPS 16 workflow, and the full channel tables above.

---

## The CPS 16 grid edit pattern that works

Zone grid columns (grid scrolled **fully left**), and row 1 is at **y=205** with **~17 px** per row:

| Field | x |
|---|---|
| Channel Name | 262 |
| Scan List | 500 |
| Color Code | 653 |
| RX Frequency | 773 |
| RX Squelch Type | 810 |
| RX DPL Code | 845 |
| TX Frequency | 1146 |
| TX Squelch Type | 1183 |
| TX DPL Code | 1220 |

**Per field:** `double_click` the cell → `wait 1` → `ctrl+a` → `type` the value → `left_click` on empty space below the grid (~`700, 450`) to commit.

- **Do NOT press Return to commit.** It advances to the next row and opens that editor, which is how a neighbouring row gets clobbered. Clicking empty space is safe.
- **Dropdowns** (RX/TX Squelch Type, Scan List): `double_click` → `wait 1` → `key down` (CSQ→DPL) or `key up` (Scan List1→None) → click away. Clicking the tiny dropdown items directly misses.
- **The `wait 1` before `ctrl+a` is mandatory** on numeric spinner cells (DPL Code, Color Code). Without it the select-all loses the race and your digits append to the old value — that's how `225` became `232` and `4` became `14`. **Verify every numeric cell after writing it.**
- **Rows shift** when a long channel name wraps to two lines. When filling a zone with long names, **work bottom-up** (row 10 → row 1) so the rows you haven't done yet don't move.
- Add channels: select the zone in the tree, then `shift+F5` analog / `shift+F6` digital, repeatable.
- Add a zone: select `Channels`, `ctrl+F2`. Rename a zone: right-click it in the tree → Rename (F2). Editing the name in the parent Channels grid tends to grab the Position spinner instead.
- The tree does **not** support shift-range selection, and the `Delete` key does nothing there. Delete via right-click → Delete → Yes.
- The non-e 3500 accepts 4+ zones — capacity is not a constraint.

---

## Source data — the 3500e master, for reference

Every channel: **TX freq == RX freq** (simplex), TX DPL == RX DPL, Power High, TOT 60 s, TOT rekey 0, DPL Invert No, DPL Turn-Off Code Yes, VOX No, Voice Emphasis De & Pre, Squelch Normal, ARTS Disabled, Audio Enhancement None, Scrambling No, RX Only No, Bandwidth 12.5 kHz.

Full extracted dump also saved at `~/Documents/Claude/KNOWLEDGE/xpr3500-master-channels.md` (copy it there from the scratchpad if it hasn't been moved yet).
