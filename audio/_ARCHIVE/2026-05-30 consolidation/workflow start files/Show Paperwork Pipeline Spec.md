# Show Paperwork Processing Pipeline Spec

*Based on the Seals & Crofts 2 and Gospel Awards 2026 runs at Memorial Hall. Only pipeline-specific decisions and chat-derived corrections appear here — general Brian preferences are in the about-me files.*

---

## 0. Session Startup

### Step 0 — Connect folders first

Two folder connections are required before any files can be read. Request both at session start:

```
~/Documents/Claude/about-me      ← about-me files (separate mount — not inside audio)
~/Documents/Claude/audio          ← covers Memorial Hall, workflow start files, all venues
```

**Note:** The global CLAUDE.md references `~/.claude/about-me/` — that path is protected and cannot be mounted. The correct location is `~/Documents/Claude/about-me/`. Use that path; ignore CLAUDE.md's reference.

### Step 1 — Read in order

```
~/Documents/Claude/about-me/about-me.md                                          ← who Brian is, how to work with him
~/Documents/Claude/about-me/writing-rules.md                                     ← tone and language rules (apply to Quick Summary prose)
~/Documents/Claude/about-me/memory.md                                            ← active projects, open issues, session notes
~/Documents/Claude/audio/Memorial Hall/venue-notes.md                            ← Memo RT60, problem freqs, crowd mic EQ
~/Documents/Claude/audio/Memorial Hall/mic-go-tos.md                             ← mic library quick reference
~/Documents/Claude/audio/workflow start files/venue-notes-3CDC.md                ← PA rigs, consoles, quirks for all 3CDC outdoor venues
~/Documents/Claude/audio/workflow start files/eq-starting-points.md              ← EQ approach by instrument
~/Documents/Claude/audio/workflow start files/console-reference.md               ← VCA layout, gain structure, console-specific workflow
~/Documents/Claude/audio/workflow start files/reverb-reference-memo.md           ← Seventh Heaven Pro preset recommendations for Memo by genre
~/Documents/Claude/audio/workflow start files/Show Paperwork Pipeline Spec.md    ← this file (canonical)
~/Documents/Claude/audio/workflow start files/Show Processing Quick Reference.md ← condensed cheat sheet
```

**Note:** `Memorial Hall/Show Paperwork Pipeline Spec.md` is a redirect stub only — do not read it for session context.

If the user is requesting a .ses build, also read:
```
~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/00_MODEL_BRIEFING.md
~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/01_Q225_SES_REFERENCE.md
~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/02_SHOW_PATCHER_WORKFLOW.md
```

**Key paths:**
```
Template .ses:    ~/Documents/Claude/audio/Memorial Hall/brian memo v2.ses
Patcher template: ~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py
Show folders:     ~/Documents/Claude/audio/Memorial Hall/YYYY-MM-DD ShowName/
SOP folder:       ~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/
```

---

## 1. Pipeline Overview

An Excel input list plus optional genre/influences text enters the pipeline and produces four deliverables in two stages. Stage 1 produces the FOH Channel Processing document as three parallel files: an MD (machine-readable patcher source), an HTML (human-readable channel cards in the locked format), and a PDF rendered from the HTML via weasyprint. Stage 2, on explicit request only, produces a show-specific Python patcher script and the DiGiCo Quantum 225 `.ses` file generated from it. All files land in the show folder under the venue root. Nothing is built speculatively — each stage waits for a request.

---

## 2. Input Format

### Primary upload
Excel spreadsheet (`.xlsx`). Column structure varies by show; adapt on sight. Expected fields:
- **Ch** — channel number (integer)
- **Instrument / Source** — what is on the channel
- **Mic / DI** — transducer make/model or type
- **Notes** — inline contextual flags (see below); may be a dedicated column or embedded in adjacent cells

Apply locked color-coding and SPARE/CONFIRM/TBD handling per CLAUDE.md.

**SPARE** — include in the input list summary table with that label; omit from EQ cards and the .ses.  
**CONFIRM / TBD** — stop and ask Brian before generating any EQ data for those channels. Do not assume.

### Genre and influences (required before EQ decisions)
A short description of the show's musical genre and any named style context — e.g., "Celtic folk, leaning traditional with some contemporary arrangements" or "Romantic-era classical, chamber" or "Southern gospel, dense choir, loud rhythm section."

If not provided with the upload, ask before proceeding. Genre drives:
- Tonal targets per channel group (e.g., acoustic-forward genre → lighter low shelf on kick, more body on acoustic guitar, restraint on hi-end brightness)
- Dynamics aggressiveness (quiet acoustic show → softer comp knees, slower gate releases, ducker over gate on cymbal channels)
- Reverb character (Celtic folk → shorter, brighter rooms; Romantic classical → longer, warmer halls)
- Quick Summary language — frame decisions in the show's musical context, not generic engineering terms

### Inline channel notes
Contextual flags in the input list that affect mic technique, EQ, or dynamics. Examples from this pipeline's runs:

- "True overhead position" vs "underhat / underhead (broadcast restriction)" — determines HPF, HF boost amount, low-mid cut weight, gate vs ducker, polarity check requirement, and reverb send offset. **Do not carry cymbal mic processing assumptions from one show to the next** — read the notes.
- "Mics inside piano with lid closed" — affects HPF (lower), low-mid treatment, and bleed rejection notes
- "Vocalist also playing guitar" — affects gate release (must not chop sustain) and comp approach
- "Drum kit on riser" — may affect low-end buildup assumptions for Memo standing-wave treatment
- "Ribbon mic — no phantom" — flag prominently in card; affects EQ correction curve expectations
- "Horn player moves between two positions" — affects placement note in the channel card

**These notes must carry through into the Quick Summary paragraphs and engineer notes in the HTML.** They are not dropped after the input list summary. If a note is ambiguous, ask before assuming.

---

## 3. Step 1 — FOH Channel Processing Document

### Three output files, always together
```
ShowName - FOH Channel Processing.md
ShowName - FOH Channel Processing.html
ShowName - FOH Channel Processing.pdf
```
Produce all three simultaneously. The PDF is rendered from the HTML:
```bash
weasyprint "ShowName - FOH Channel Processing.html" "ShowName - FOH Channel Processing.pdf"
```
Do not use reportlab. It does not produce output that matches the locked channel card format.

### HTML structure (locked — Gospel Awards 2026 FOH Channel Processing PDF is the reference)
1. Title: show name, console, venue, date
2. Input list summary table: Ch | Instrument | Mic/DI
3. Per-channel cards in channel order (see card spec below)
4. Global reverb section — Seventh Heaven Pro presets, tuned to genre and room (Memo RT60 ≈ 1.6 s)
5. Critical notes — reverberant-room reminders, Memo problem frequencies, polarity warnings, stereo pair linking
6. Workflow reminders — VCA groups, manual-entry channels, anchor channel for the mix

### Vocal EQ — Locked Rule

**Vocals are cuts only. No boosts.** This is a feedback control requirement at Memo, not a stylistic preference — apply it without exception.

Be aggressive: deeper cuts, tighter Qs on problem resonances, more HPF than you might instinctively reach for on an instrument channel. If a vocal channel needs brightness, the mic choice and placement solve that — not a high-shelf boost. The Quick Summary should reflect this explicitly when applicable (e.g., "cuts-only approach for feedback headroom in the Memo").

Applies to: handheld vocals, podium mics, choir mics, any channel where a human voice is the primary source.

---

### Per-channel card structure
Dark navy (`#1c3558`) card header. 3-column table: **Section | Parameter / Value | Details**. Row order:

| Section label | Notes |
|---|---|
| Placement | Only when non-standard — underhat, underhead, inside piano, riser. Omit for standard positions. |
| HPF | Frequency @ slope |
| LPF | Frequency @ slope, or "Off" |
| Band1; High Shelf | gain @ freq, Q, Shelf |
| Band2; Upper-Mid (Param) | gain @ freq, Q |
| Band3; Lower-Mid (Param/Dyn) | gain @ freq, Q; DEQ params in Details if active |
| Band4; Low (Param) *or* Band4; Low (Lowshelf) | match label to actual type |
| Dynamics 1; Compressor | "On" in Value; full settings in Details |
| Dynamics 2; Gate *or* Dynamics 2; Ducker | Use "Ducker" when the function is a light ducker, not a hard gate (e.g., cymbal channels in acoustic-forward shows). Label matters — it tells the engineer what behavior to expect. |
| Polarity | Only for channels where phase verification is required (underhat, underheads, mic pairs). "CHECK" in Value; instructions in Details. |
| Reverb Send | Only where a non-default send offset applies (e.g., underheads +2 to +3 dB to compensate for reduced natural air). |
| Quick Summary | Full paragraph. Reference genre, inline notes, and the reasoning behind non-obvious decisions. This is the most important row. |

Band order is High → Low (Band 1 = High Shelf, Band 4 = Low). Matches Q225 physical console layout. Locked.

### Manual-entry channels
Channels that exceed the patcher's strip range (or that Brian flags as manual) get a dark red (`#8b1a1a`) card header with "★ MANUAL ENTRY" in the title. Still include full EQ/dynamics data in the card — the engineer still needs it, even if the script can't write it. Note in the workflow reminders section that these channels must be set on console before show.

### Reverb section

Full reference: `~/Documents/Claude/audio/workflow start files/reverb-reference-memo.md`

**Algorithm selection:**
- **V1** — static, realistic, low modulation. Classical, jazz, Celtic, acoustic folk, chamber. Use when the source needs to keep its character.
- **V2** — brighter, modulated, lush bloom. Gospel, contemporary, pop/rock, dense choir. Use for wash and bloom rather than accuracy.
- When in doubt on acoustic shows: V1. When in doubt on contemporary shows: V2 for vocals/plates, V1 for halls.

**Memo RT60 rule:** The room adds ~1.6s of natural decay. Pull factory preset decay times back 30–40% as a starting point. A 2.1s factory preset runs 1.2–1.4s at Memo. Exception: close-mic'd sources (kick inside, DI bass, lip-close vocal) that need reverb for placement can run a bit longer — the mic isn't picking up much natural room.

**Preset selection by genre (first choices):**

| Genre | Vocals | Hall/Room | Drums |
|---|---|---|---|
| Classical/Chamber | Chambers 1 / Sunset Chamber | Halls 1 / Concert Hall | — |
| Jazz | Chambers 1 / Vocal Chamber | Rooms 1 / Djangos Room | Rooms 1 / Studio B Close |
| Celtic/Folk | Chambers 1 / Sunset Chamber | Rooms 1 / Large Wooden | Rooms 1 / Studio B Close |
| Gospel | Chambers 1 / Vocal Chamber (V1) or Plates 2 / Vocal Shimmer (V2) | Halls 1 / Sandors Hall | Rooms 1 / Studio B Close |
| Rock/Blues | Chambers 1 / Vocal Chamber or Plates 1 / Vocal Plate | Rooms 2 / Guitar Room (V2) | Rooms 1 / Studio B Close |

Snare across all genres: Plates 1 / Snare Plate A (first choice), Plates 1 / Dark Plate (vintage/warm alternative).

**Line format (locked):**
```
Preset: [Bank / Name] | Decay Xs • PreDelay Xms • Early/Late XX/XX • HF Damp X.X • Mix X% — [rationale]
```
Include return EQ (HS, LC) where applied. Always use exact preset names — cross-reference `reverb-reference-memo.md` for the full by-genre and by-source tables.

### Underhead/underhat defaults
When a show has broadcast/camera visual restrictions, cymbal mics go below, not above. Apply the EQ offset corrections and polarity check requirement per userMemory. For non-broadcast shows, treat Ch 7/8 as true overheads unless the input list says otherwise — and adjust EQ accordingly (lighter HF boost, less low-mid cut, standard gate not ducker if playing dynamics allow).

---

## 4. Step 2 — MD/HTML Conversion

### MD format (patcher source only)
```
## Ch {N} | {Console Name} | {Mic/DI}
HPF: {hz} | LPF: {hz|OFF}
B1: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B2: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B3: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
```

Rules:
- `LPF: OFF` = no LPF active (maps to `OFF_LPF = 25000.0` in the patcher)
- Include the DEQ clause on B3 only when DEQ is active; omit entirely otherwise
- `FLAT` replaces the entire band line for a bypassed band
- Console Name ≤ ~12 characters for fader strip legibility on the Q225
- `old_name` for channels in the master template is always `str(strip_num)` — i.e., the channel number as a string

### What the MD carries
Channel number, console name, mic/DI, HPF, LPF, all four EQ bands, DEQ parameters on Band3.

### What the MD does NOT carry
Comp/gate/ducker parameters, placement notes, polarity checks, reverb sends, Quick Summary text, genre context. These live in the HTML only. The MD is machine input — nothing else.

### Genre and inline notes in the HTML
Genre context and per-channel notes from the input list must appear in the Quick Summary paragraphs. They do not need explicit labeled fields — they inform the prose. A future engineer reading the HTML should understand why a decision was made, not just what the setting is.

---

## 5. Step 3 — .ses File Generation

**Target console: DiGiCo Quantum 225**

This step runs only on explicit request. Do not build the .ses speculatively.

### Source template
```
~/Documents/Claude/audio/Memorial Hall/brian memo v2.ses
```
Never edit the template directly. Copy-and-patch into the show folder only.

### Script
Copy `Q225 SES Patcher SOP/apply_show_TEMPLATE.py` → `YYYY-MM-DD ShowName/apply_showname.py`. Use a short lowercase `showname` (e.g., `apply_seals.py`, `apply_gospel.py`). Fill the `CHANNELS` dict from the MD.

### Layout constants (verified correct)
```python
STRIP1_HDR        = 0x0b0327
STRIP_SIZE        = 5638
HPF_REL           = 406          # fixed offset within strip — not a TLV record
NAME_SEARCH_START = 0x0a2a5a
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 48   # supports strips 1–48
```

### Verified safe EQ / filter tags
```python
TAG_EQ_ENABLE  = 0x0404    TAG_EQ_GAIN    = 0x0403
TAG_EQ_FREQ    = 0x0406    TAG_EQ_Q       = 0x0407
TAG_EQ_TYPE    = 0x040b    TAG_DEQ_ENABLE = 0x040e
TAG_DEQ_THRESH = 0x0411    TAG_DEQ_ATK    = 0x0412
TAG_DEQ_REL    = 0x0410    TAG_LPF_FREQ   = 0x0703
```

### DO-NOT-WRITE tags
```python
0x1E0E, 0x1E0B, 0x1E11, 0x1E12,          # Mustard Dynamic 2 slot
0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05,
0x0503, 0x050e, 0x0511,
0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47
```
Writing to any of these enables Mustard plugin parameters on every touched channel. Tags that look like SD comp/gate controls (`0x1Exx`, `0x1Dxx`) are Mustard — not the compressor. Ten script versions were burned on this. Do not write comp or gate parameters until the console-save-diff method has confirmed the correct tag IDs.

Do not write to `0x0a41c7` (reverb/room preset table) — caused Q225 access violation.

### MD → CHANNELS dict mapping
| MD field | Script position | Notes |
|---|---|---|
| Ch N | strip_num (dict key) | |
| Console Name | `[0]` name | |
| old_name | `[1]` | `str(strip_num)` for master template |
| HPF hz | `[2]` hpf | int or float |
| LPF hz / OFF | `[3]` lpf | `OFF_LPF = 25000.0` |
| B1 gain/freq/Q/type | `bands[0]` bidx=0 | SHELF = 1.0 |
| B2 gain/freq/Q/type | `bands[1]` bidx=1 | BELL = 2.0 |
| B3 + DEQ clause | `bands[2]` bidx=2 | `deq=True, thr=X, atk=X, rel=X`; atk/rel convert ms→s |
| B4 gain/freq/Q/type | `bands[3]` bidx=3 | SHELF or BELL per MD |

DEQ atk/rel: always seconds in the script, always milliseconds in the MD. `atk=8ms` → `atk=0.008`.

### Required verification before delivery
```
File size: matches template exactly (1,543,866 bytes for brian memo v2.ses)
Spot-check Ch 1: Name field copies replaced: ~20  (never 0 or 1)
Do-not-write tag verification: PASS
```
FAIL on any of these = stop. Do not deliver the file. Identify the cause before rerunning.

### What the patcher does not write
- Compressor / gate / ducker parameters — tag IDs unconfirmed
- Mustard plugin parameters — DO-NOT-WRITE
- Reverb and room settings — DO-NOT-WRITE (`0x0a41c7`)

These exist in the HTML for the engineer to set manually.

---

## 6. File Naming Convention

```
Show folder:     ~/Documents/Claude/audio/Memorial Hall/YYYY-MM-DD ShowName/
MD:              ShowName - FOH Channel Processing.md
HTML:            ShowName - FOH Channel Processing.html
PDF:             ShowName - FOH Channel Processing.pdf
Patcher script:  apply_showname.py           (short lowercase, no spaces)
.ses output:     ShowName.ses
```

Show folders sort chronologically because date comes first. Do not deviate from this pattern.

---

## 7. Output Order and Delivery

1. **Stage 1 — Processing document**: present MD, HTML, and PDF links simultaneously. All three or none.
2. **Stage 2 — .ses**: only when Brian asks. Present the file path and the spot-check / verification output. Do not guess at follow-ups. Wait for his console report.
3. **Stage 3 — Show packet PDF**: separate request, per CLAUDE.md. Not part of this pipeline.

If Brian uploads a new input list and says nothing else, produce Stage 1 only, then stop.

---

## 8. Edge Cases and Corrections

**NAME_SEARCH_END too narrow**  
Original scripts had `NAME_SEARCH_END = STRIP1_HDR + STRIP_SIZE * 24`. Any channel beyond strip 24 produced zero name-field hits — the name write silently failed. Fix: `* 48`. The template script is already corrected. Show-specific scripts copied before the fix must be updated manually. Symptom: `name fields found: 0` or `name fields found: 1` in patcher output.

**old_name mismatch**  
`!! no name fields found for old_name='X'` means the old_name is wrong. For channels in the master template, old_name is always `str(strip_num)`. If the script was built against an intermediate .ses (not the master template), old_name must match whatever that file had. Always run against `brian memo v2.ses` unless Brian specifies otherwise.

**Cymbal mic positioning assumptions**  
Do not carry underhead/true-overhead processing from one show to the next. Gospel Awards: underheads (broadcast restriction). S&C 2: true overheads (no restriction). The channel number tells you nothing. The input list tells you everything.

**Gate vs Ducker on cymbal channels**  
In acoustic-forward or quiet shows, cymbal wash is musical — a hard gate chops the tail in a quiet passage. Use a Ducker (light, Thr ≈ −50 dB, Range 30–40 dB) instead. Label it "Dynamics 2; Ducker" in the card. This was the correct call for S&C 2 Ch 7/8.

**DEQ on underhat Band3**  
S&C 2 Ch 3: no DEQ on Band3 because the open-hat pedal pattern in that repertoire is consistent enough that a static cut is cleaner than a dynamic one. Gospel Awards Ch 3: DEQ active because the hat playing was more variable. DEQ is not automatic on underhat — assess per show.

**Missing genre info**  
If genre is absent, ask. Do not start EQ decisions on generic starting points. The genre sentence takes ten seconds and prevents a document that needs revision at soundcheck.

**Ambiguous inline notes**  
If a channel note is unclear (e.g., "ribbon mic" with no phantom status, "two positions" with no stage diagram), ask before assuming. Wrong assumptions create problems that don't surface until the console is on and the clock is running.

**reportlab**  
Abandoned. It does not produce output matching the locked format. All PDFs are rendered from HTML via weasyprint.

**Template script naming**  
`apply_show_TEMPLATE.py` uses "Memo Template" labeling throughout. It must never contain show-specific channel data. The CHANNELS dict in the template is empty with usage comments only. Show scripts are always copies.

---

## 9. Invocation Pattern

When uploading a new input list, type:

```
Process this input list. Genre/influences: [description]. [Any per-channel notes not in the spreadsheet.]
```

If genre/influences are not included, the pipeline will ask before proceeding to EQ.  
If channel notes in the spreadsheet are ambiguous, the pipeline will ask before committing to a card.  
If everything is present, Stage 1 runs without further questions.

To trigger Stage 2 after reviewing Stage 1:

```
Build the .ses from the MD.
```
