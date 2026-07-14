# Q225 .ses File Format & Tag Reference

> **SUPERSEDED 2026-07-01 — read this first.** The Memo template is now
> `Memorial Hall/_TEMPLATE/brian memo june 2026.ses` (37,661,337 bytes, a full
> console save in the FSQ layout: surface-label table + current-scene channel
> blocks). `apply_show_TEMPLATE.py` was rebuilt on the console-verified FSQ
> engine (offset tripwire, MD-driven CLI, stray-byte verification). The strip
> layout this document describes (`brian memo v2.ses`, strips at 0x0b0327,
> stride 5638, HPF_REL 406, hand-filled CHANNELS dict) is RETIRED — kept for
> history only; the old engine is archived as
> `apply_show_TEMPLATE_v2_OLD_stripformat.py`. Current spec: KB
> `pipeline-spec-memo` and the header of `apply_show_TEMPLATE.py`.
> Tag semantics (EQ/DEQ/LPF TLVs, HPF x0.8 / LPF x1.25, bidx 0 = high band,
> do-not-write Mustard tags) are unchanged and still apply.


Verified against DiGiCo Quantum 225, firmware as of 2026-05-22.
Reference template: `~/Documents/Claude/audio/Memorial Hall/brian memo v2-99072ff1.ses`.

## File layout

A `.ses` file is a 1,543,866-byte binary container holding channel
strips and snapshot data.

### TLV records

Most parameters are stored as **8-byte TLV records**:

```
offset  size  meaning
  +0      4    float32 LE   parameter value
  +4      2    uint16  LE   tag ID
  +6      2    uint16  LE   bidx (band/instance index)
```

Find a record by scanning for the 4-byte signature
`struct.pack('<HH', tag, bidx)` at offset +4 of each candidate position.

### Channel strips

Main channel strips are at fixed positions:

```python
STRIP1_HDR = 0x0b0327   # start of strip 1 (channel 1)
STRIP_SIZE = 5638       # bytes per strip
# Strip N starts at STRIP1_HDR + (N - 1) * STRIP_SIZE  (1-indexed)
# 48 strips total
```

When patching, scan only inside a strip's region — TLV records with
the same tag also appear in snapshot/secondary regions and must not be
touched.

### Channel names

Channel name fields are 32-byte structures, encoded as:

```
[1 byte: length] [N bytes: ASCII name] [pad with 0x00 to 32 bytes]
```

Each channel's name is repeated in roughly 20 places across the file
(every snapshot copy). All copies must be updated for the name to stick
on the console.

Scan range for name fields:
```python
DISP_NAME_BASE    = 0x0a2a5a
NAME_SEARCH_START = DISP_NAME_BASE
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 48
```

A valid name field is identified by matching the length-prefixed name
followed by ≤5 stray non-null bytes in the remaining padding.

### HPF — special case

The HPF cutoff frequency is **NOT** a TLV record. It is a raw float32
at a fixed offset inside the strip:

```python
HPF_REL = 406   # HPF freq float at strip_start + HPF_REL
```

## VERIFIED safe-to-write tags

These tags have been confirmed via console-save-diff and successful
test loads on the Q225. Write only these.

| Tag | Name | Notes |
|------|------|-------|
| `0x0404` | `EQ_ENABLE`  | bidx 0–3 per band (1.0 ON / 0.0 OFF) |
| `0x0403` | `EQ_GAIN`    | dB, signed float |
| `0x0406` | `EQ_FREQ`    | Hz |
| `0x0407` | `EQ_Q`       |  |
| `0x040b` | `EQ_TYPE`    | 1.0 = shelf, 2.0 = bell |
| `0x040e` | `DEQ_ENABLE` | dynamic EQ on the band |
| `0x0410` | `DEQ_RELEASE`| seconds |
| `0x0411` | `DEQ_THRESH` | dB |
| `0x0412` | `DEQ_ATTACK` | seconds |
| `0x0703` | `LPF_FREQ`   | bidx=1; write 25000.0 for "no LPF" |

HPF (fixed offset, not a TLV): write a float32 at `strip_start + 406`.

### EQ band index convention

Bands are bidx 0..3, top→bottom:

- `bidx 0` — High (typically shelf)
- `bidx 1` — Upper Mid (bell)
- `bidx 2` — Lower Mid (bell, common DEQ band)
- `bidx 3` — Low (typically shelf)

This ordering matches the channel-card template Brian uses (Band 1 =
High Shelf, Band 4 = Low). See his memory entry
`feedback_channel_card_template.md`.

## DO NOT WRITE — these break things

### Mustard plugin controls (NOT SD comp/gate)

These tag IDs were mislabeled as SD compressor and SD gate in earlier
script versions. They are actually controls for the Mustard plugin's
internal Dynamic slots. Writing them engages Mustard on every channel
you touch, which is not what the show wants.

| Tag | What it actually is |
|------|--------------------|
| `0x1E0E` | Mustard Dynamic 2 — ENABLE |
| `0x1E0B` | Mustard Dynamic 2 — MAKEUP |
| `0x1E11` | Mustard Dynamic 2 — THRESHOLD (persistent) |
| `0x1E12` | Mustard Dynamic 2 — RELEASE (persistent) |
| `0x1D0E`, `0x1D0F`, `0x1D4A`, `0x1D10`, `0x1D12`, `0x1D05` | Suspected Mustard Dynamic 1 slot |
| `0x0503`, `0x050E`, `0x0511`, `0x08E1`, `0x08E8`, `0x0EE8`, `0x0EFE`, `0x1D47` | Other known Mustard tags |

**Persistent parameter behaviour:** Mustard slots keep their threshold/
release/etc. even when the enable flag is OFF. Only `ENABLE` (1.0 → 0.0)
and `MAKEUP` (default → 0.0) zero out on disable. This is why the slots
can carry "ghost" settings from prior states without sounding engaged.

### Hard-fail address

`0x0a41c7` — reverb/room preset table. Writing here caused a Q225
**access violation** (console crash) in an earlier script. Never write
to this address.

### Real SD comp / SD gate — UNKNOWN

The real tag IDs for the SD Dynamic 1 (compressor) and Dynamic 2 (gate)
sections are not yet identified. Their tags live in the channel strip
but at offsets we haven't pinned down. **Find them with the
console-save-diff method below** before writing anything claiming to be
SD comp or SD gate.

## Console-save-diff method — how to identify an unknown tag

This is the only reliable way to identify a Q225 .ses tag. Use it
whenever a tag's meaning is unknown or suspected wrong. Ten script
versions of guessing were resolved in under a minute by one save.

### Procedure

1. Build a script-generated `.ses` where the parameter of interest is
   in a **known state on every channel** the script touches. Example:
   "Mustard Dyn 2 ON on every channel" or "SD comp ON with threshold
   -20 dB, release 80 ms on every channel."
2. Load that file on the Q225.
3. On **one channel only**, manually flip the parameter to its other
   state from the console. Touch nothing else — no EQ moves, no level
   moves, no other channels.
4. **Save** the session from the console to a new filename.
5. Diff the saved file against the script-generated input.

### Reading the diff

What to **ignore**:

- **Snapshot timestamp/session-ID noise.** Five-byte runs that change
  in the same pattern across every snapshot strip. Common starting
  bytes vary by save (e.g. `34eea5015a → e366dfd78b`). These are not
  parameter changes.
- **Anything outside the modified channel's main strip.** Look only at
  bytes inside that one strip's region (`STRIP1_HDR + (N-1)*STRIP_SIZE`
  for `STRIP_SIZE` bytes).

What's **meaningful**:

- TLV value changes (4 bytes at a record start) inside the modified
  channel's main strip. Those are the controlling tags for the
  parameter you toggled.
- The change pattern matters: enable flags go `1.0 → 0.0`; persistent
  parameters (threshold, release, etc.) often stay put even when the
  section is "disabled" — only the enable plus a few defensive params
  (like makeup gain) clear.

### Proof — the 2026-05-22 Mustard discovery

Brian loaded `Gospel_Awards_2026_NAMES_EQ_COMP.ses` (script set "Mustard
Dyn 2 ON" on every touched channel — though we thought we were enabling
SD comp). He disabled Mustard Dyn 2 on channel 1 from the console and
saved. Diff vs the input showed exactly two TLV value changes inside
channel 1's main strip:

- `0x1E0E bidx=0`: 1.0 → 0.0 (the enable flag)
- `0x1E0B bidx=0`: 4.0 → 0.0 (makeup)

Threshold and release stayed at the values the script wrote (-8.0 and
0.080), confirming Mustard-slot persistence. That single save resolved
ten versions of failed debug.

## How to verify a patched file before handing it to the console

The script writes a verification block. Look for:

```
Do-not-write tag verification (Mustard + Mustard-suspect):
  PASS — every restricted tag is byte-identical to template.
```

If you see **FAIL**, do not hand the file to Brian. Restricted tags
were modified, which means Mustard or something else got engaged. Fix
the script first.

Also check:
- File size equals template size (1,543,866 bytes for the current
  template). The script asserts this.
- Name field hit count for at least one known channel is ~20 (not 0,
  not 1). Fewer means the name scan range is wrong.
- HPF and LPF values for a spot-check channel match what was written.
