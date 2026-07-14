# Show Patcher Workflow

This is the procedure for taking a new show's paperwork and producing a
working Q225 `.ses` file. Follow it in order. Stop and ask Brian
wherever the document says to.

## Inputs you should expect

For most Memorial Hall shows you'll receive (or find in the show folder):

- **Patch sheet** — usually `<ShowName> - Patch Sheet.xlsx`. Channel
  number → source name (Kick, Snare, BG Vox 1, etc.) and microphone.
- **Channel processing sheet** — always two files:
  - `<ShowName> - FOH Channel Processing.md` — the patcher source.
    Read this to build the CHANNELS dict.
  - `<ShowName> - FOH Channel Processing.html` — human-readable version,
    produced at the same time.
  Use the `.md` for the patcher. If only a legacy PDF exists, convert
  it to `.md` format first and produce the HTML companion (see Step 4 for the format spec).
- **Template** — the master `.ses` lives at
  `~/Documents/Claude/audio/Memorial Hall/brian memo v2.ses`.
  Do not edit the template. Always copy/patch into the show folder.

If any of these inputs is missing or unclear, **stop and ask**.

## Step 1 — confirm scope

Before writing anything, confirm with Brian:

- Show name and date (used for the folder: `YYYY-MM-DD ShowName`)
- Which channels are in scope (e.g. "1–22 and 24, leave 23 alone")
- Anything non-standard for this show (different template, custom
  mic-to-channel mapping, etc.)

Do not assume scope from the patch sheet alone. The Gospel Awards show
skipped channel 23 entirely; nothing in the paperwork said so until
asked.

## Step 2 — set up the show folder

Inside `~/Documents/Claude/audio/Memorial Hall/`:

```
YYYY-MM-DD ShowName/
├── (Patch sheet + processing PDF go here when Brian uploads them)
├── apply_<showname>.py     ← copy from Q225 SES Patcher SOP/
└── <ShowName>.ses          ← will be created when you run the script
```

If the show folder exists already, do not delete or rename anything
inside without asking.

## Step 3 — copy and rename the template script

```
cp "Q225 SES Patcher SOP/apply_show_TEMPLATE.py" \
   "YYYY-MM-DD ShowName/apply_<showname>.py"
```

Use a short, lowercase name for `<showname>` (e.g. `gospel`,
`christmas_concert`).

## Step 4 — fill in the channel data

Read the channel-processing `.md` file. Edit the `CHANNELS` dict in
your copied script. Each entry is:

```python
strip_num: (
    "New Name",                                            # what shows up on the console
    "OldName",                                             # what the template currently has there (almost always the channel number as a string: "1", "2", ...)
    hpf_hz,                                                # int or float
    lpf_hz_or_OFF_LPF,                                     # use OFF_LPF (= 25000.0) for "no LPF"
    [                                                      # exactly 4 bands, bidx 0..3
        B(gain, freq, q, type),                            # bidx 0  High
        B(gain, freq, q, type),                            # bidx 1  Upper Mid
        B(gain, freq, q, type, deq=True,                   # bidx 2  Lower Mid (common DEQ spot)
          thr=-16, atk=0.010, rel=0.080),
        B(gain, freq, q, type),                            # bidx 3  Low
    ],
),
```

Conventions:

- `SHELF` = 1.0, `BELL` = 2.0 — use the named constants, not the floats.
- High and Low bands are typically `SHELF`; mids are `BELL`. Match what
  the processing `.md` says, not what's "typical".
- Skip channels Brian said to leave alone — just don't include them in
  the dict.
- Use `FLAT()` for a band that should be inactive but still need a
  placeholder (e.g. a Tracks input that only needs Lower Mid and Low).
- `old_name` is what the template has there. For the master template
  it's the channel number as a string (`"1"`, `"2"`, ... `"24"`). If
  the patcher reports `!! no name fields found for old_name='X'`, the
  `old_name` is wrong — fix it.

### Channel processing MD format

The `.md` source file uses this format — parse it directly:

```
## Ch {N} | {Console Name} | {Mic/DI}
HPF: {hz} | LPF: {hz|OFF}
B1: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B2: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B3: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
```

Rules:
- `Ch N` → `strip_num = N`, `old_name = str(N)` (master template always
  has channel numbers as names)
- Console Name → the display name written to the console fader strip
- `LPF: OFF` → `OFF_LPF` (25000.0)
- `FLAT` replaces the entire band line for a bypassed band
- DEQ atk/rel values are in ms in the `.md`; convert to seconds for the
  script (e.g. `atk=8ms` → `atk=0.008`)
- DEQ can appear on any band but is almost always B3 (Lower Mid)
- Channels omitted from the `.md` are left untouched in the template

When producing a new processing document, always deliver three files at
the same time: the `.md` (patcher source), the `.html` (human-readable
channel cards), and a PDF rendered from the HTML. Use weasyprint or
equivalent to render the HTML to PDF — do not use reportlab for the
processing document. Do not assume Brian wants a `.ses` built from the
`.md` — he will ask for that separately.

### Don't add comp, gate, or anything Mustard

The current template has SD comp ON and SD gate OFF as a starting
state, and all Mustard parameters OFF. The script preserves that state
by not writing any of those parameters. **Do not** try to add comp/gate
control without running the console-save-diff method first to find the
real tag IDs.

If Brian asks for comp/gate adjustments, that's a separate task. Tell
him you need to run the diff method first (see `01_Q225_SES_REFERENCE.md`).

## Step 5 — run the patcher

From the show folder:

```bash
python3 apply_<showname>.py \
    --src "/Users/brianlloyd/Documents/Claude/audio/Memorial Hall/brian memo v2.ses" \
    --dest "/Users/brianlloyd/Documents/Claude/audio/Memorial Hall/YYYY-MM-DD ShowName/<ShowName>.ses"
```

Expected output ends with a spot-check block:

```
Spot-check Ch 1 (Kick):
  Name field copies replaced: 20         ← should be ~20, never 0 or 1
  HPF: 40.0 Hz   LPF: 8000.0 Hz          ← should match what you put in
  DEQ enable bidx=2: 1.0                 ← if you set deq=True on that band

Do-not-write tag verification (Mustard + Mustard-suspect):
  PASS — every restricted tag is byte-identical to template.
```

If you see **FAIL** on the verification line, **stop**. Do not hand the
file to Brian. Something in your script wrote to a Mustard tag. Read
the failure list — it shows offsets and tag IDs — and find the bug.

If you see `!! tag 0xNNNN bidx=N NOT FOUND in strip M`, that channel's
strip is missing the expected tag. Either the strip doesn't exist
(check that the channel number is in range 1–24) or the template you
pointed `--src` at is the wrong file.

## Step 6 — hand off to Brian

Tell him the file is ready, give him the path. Then **stop**. Do not
guess at follow-ups. Wait for his report from the console.

Brian's typical report after a console test:

- "Names good, EQ good." → success path.
- "X is on / off when it shouldn't be." → a tag is wrong or your data
  is wrong. Find out which and run the **console-save-diff method** if
  the cause isn't obvious.
- "HPF/LPF on but not adjusted, still 20Hz/20kHz." → the freq write
  didn't land. Check the script ran without `NOT FOUND` warnings.

## Step 7 — show packet (when the patcher is settled)

Brian's CLAUDE.md says every show packet ends with a **master
reference PDF**. Once the .ses is loading correctly on the console,
ask whether he wants you to generate that PDF now. It typically covers:

- Input list summary
- EQ decisions (the channel-card table — High→Low band order)
- Patching
- Mic choices (from the patch sheet)
- Stage plot reference (if one exists)
- File index of everything in the show folder

That's a separate task, not part of the patcher run.

## Common pitfalls

| Symptom | Likely cause |
|---------|--------------|
| `name fields found: 0` for a channel | `old_name` wrong, or NAME_SEARCH range too narrow |
| `name fields found: 1` (only one copy) | NAME_SEARCH range wrong; snapshot copies live further out |
| File opens but a channel name didn't change | Same as above — fewer than ~20 hits |
| Mustard turns on on every touched channel | A `0x1Exx` or `0x1Dxx` write slipped in. Audit your tag list against the DO-NOT-WRITE list. |
| Console crashes / access violation on load | Wrote to `0x0a41c7` (reverb preset table). Do not. |
| Output file is a different size from the template | Bug. The patcher should never change file size. The script's final `assert` should catch this. |
| Verification FAIL with a `0x1Exx` tag | Mustard control got written. Remove that write. |
| Verification FAIL with a tag not in the DO-NOT-WRITE list | Investigate, then add it to the list if it turns out to be off-limits. |

## When to stop and escalate

Stop and surface to Brian (do not iterate silently) if:

- The verification step FAILs after one fix attempt.
- A console test reveals an unexpected parameter state (Mustard on,
  gate on, comp behaving wrong).
- The patch sheet or processing PDF contradicts itself.
- You don't recognize a parameter the paperwork is asking for.
- Anything in the show is non-standard (Theatre mode, surround buses,
  a non-Q225 console). The Q225 is the assumed target.

Brian has done the hard debug. He'd rather answer a question than
chase a guess.
