# Show Processing Quick Reference

*Consolidated cheat sheet for in-session use. Full detail lives in the pipeline spec and SOP docs.*  
*Last updated: May 2026*

---

## Session Startup

### Connect these folders first (both required)

```
~/Documents/Claude/about-me      ← separate mount, not inside audio
~/Documents/Claude/audio          ← covers Memorial Hall, workflow start files, all venues
```

Global CLAUDE.md references `~/.claude/about-me/` — that path is protected and inaccessible. Use `~/Documents/Claude/about-me/` instead.

### Then read in order

```
~/Documents/Claude/about-me/about-me.md
~/Documents/Claude/about-me/writing-rules.md
~/Documents/Claude/about-me/memory.md
~/Documents/Claude/audio/Memorial Hall/venue-notes.md
~/Documents/Claude/audio/Memorial Hall/mic-go-tos.md
~/Documents/Claude/audio/workflow start files/venue-notes-3CDC.md
~/Documents/Claude/audio/workflow start files/eq-starting-points.md
~/Documents/Claude/audio/workflow start files/console-reference.md
~/Documents/Claude/audio/workflow start files/Show Paperwork Pipeline Spec.md    ← canonical
~/Documents/Claude/audio/workflow start files/Show Processing Quick Reference.md ← this file
```

If building a .ses, also read the Q225 SES Patcher SOP folder (all three .md files).

`Memorial Hall/Show Paperwork Pipeline Spec.md` is a redirect stub — ignore it.

---

## Key File Paths

| File | Path |
|---|---|
| Template .ses | `~/Documents/Claude/audio/Memorial Hall/brian memo v2.ses` |
| Patcher template script | `~/Documents/Claude/audio/Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py` |
| Mic go-tos | `~/Documents/Claude/audio/Memorial Hall/mic-go-tos.md` |
| Venue notes | `~/Documents/Claude/audio/Memorial Hall/venue-notes.md` |
| Pipeline spec | `~/Documents/Claude/audio/Memorial Hall/Show Paperwork Pipeline Spec.md` |
| About-me files | `~/Documents/Claude/about-me/` |
| Show folders | `~/Documents/Claude/audio/Memorial Hall/YYYY-MM-DD ShowName/` |

---

## Memorial Hall — Room Data

- **RT60:** ~1.6s working (2.2s was empty/pre-renovation — use 1.6s for all processing decisions)
- **Problem frequencies:** 63 Hz, 125 Hz, 200 Hz, 250–315 Hz (standing waves)
- Always treat in EQ on crowd/ambient mics. Room is already doing reverb work — start reverb conservative.

### Crowd Mic EQ (patch every show)

| Pair | HPF | Key Cuts | LPF |
|---|---|---|---|
| Line Audio OM1 (flown omni) | 80 Hz | −5dB@200Hz Q2.0, −6dB@315Hz Q2.0, −3dB@800Hz Q1.5 | Off |
| Deity S2 (under PA) | 100 Hz | −5dB@200Hz Q2.0, −5dB@315Hz Q2.0, −3dB@2.4kHz Q1.8 | 16 kHz |
| Line Audio CM4 (balcony ORTF) | 120 Hz | −5dB@63Hz Q2.5, −6dB@200Hz Q2.0, −5dB@315Hz Q2.0, −4dB@400Hz Q1.5 | 14 kHz |

---

## Vocal EQ — Locked Rule

**Cuts only. No boosts.** Feedback control at Memo — no exceptions.

Be aggressive: deeper cuts, tighter Qs on resonances, more HPF than you'd use on an instrument. Brightness comes from mic choice and placement, not a high shelf. Note the cuts-only approach explicitly in the Quick Summary. Applies to any channel where a human voice is the primary source: handheld vocals, podium mics, choir mics.

---

## Channel Card Format (Locked)

Band order: **High → Low** (Band 1 = High Shelf, Band 4 = Low). Matches Q225 physical layout.

Card header: dark navy `#1c3558`. Manual-entry channels: dark red `#8b1a1a` with ★ MANUAL ENTRY.

Row order in each card:

| Row | Notes |
|---|---|
| Placement | Only when non-standard (underhat, inside piano, riser) |
| HPF | Frequency @ slope |
| LPF | Frequency @ slope, or "Off" |
| Band1; High Shelf | gain @ freq, Q, Shelf |
| Band2; Upper-Mid (Param) | gain @ freq, Q |
| Band3; Lower-Mid (Param/Dyn) | gain @ freq, Q; DEQ in Details if active |
| Band4; Low (Param) or Low (Lowshelf) | match label to actual type |
| Dynamics 1; Compressor | full settings in Details |
| Dynamics 2; Gate *or* Ducker | "Ducker" when light ducking, not hard gate |
| Polarity | Only where phase check required — "CHECK" in Value |
| Reverb Send | Only for non-default offset |
| Quick Summary | Full paragraph. Genre, inline notes, reasoning behind non-obvious calls. Most important row. |

Three output files always together:
```
ShowName - FOH Channel Processing.md
ShowName - FOH Channel Processing.html
ShowName - FOH Channel Processing.pdf   ← weasyprint from HTML, not reportlab
```

---

## Seventh Heaven Pro Reverb Format

Always use real preset names. Line format:
```
Preset: [Name] | Decay Xs • PreDelay Xms • Early/Late XX/XX • HF Damp X.X • Mix X% — [rationale]
```
Include return EQ (HS, LC). In the Memo, start conservative — the room adds reverb naturally.

---

## Cymbal Mic Rules (Don't Carry Between Shows)

Read the input list — never inherit from the previous show.

- **Broadcast/camera restriction** → underhat/underhead position → EQ offsets apply, Ducker not Gate, polarity check required
- **No restriction** → true overhead → lighter HF boost, less low-mid cut, Gate OK if dynamics allow
- **DEQ on underhat Band3:** not automatic — assess per show (S&C 2 Ch 3: no DEQ; Gospel Awards Ch 3: DEQ active)

Ducker settings for acoustic-forward shows: Thr ≈ −50 dB, Range 30–40 dB.

---

## MD Patcher Format (Stage 2 Source)

```
## Ch {N} | {Console Name} | {Mic/DI}
HPF: {hz} | LPF: {hz|OFF}
B1: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B2: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
B3: {gain} | {freq_hz} | {Q} | {SHELF|BELL} [| DEQ: thr={db} atk={ms}ms rel={ms}ms]
B4: {gain} | {freq_hz} | {Q} | {SHELF|BELL}
```

- `LPF: OFF` maps to `OFF_LPF = 25000.0` in script
- `FLAT` replaces entire band line for a bypassed band
- Console Name ≤ ~12 characters
- `old_name` = `str(strip_num)` for master template channels
- DEQ atk/rel: MD uses ms, script uses seconds (`atk=8ms` → `atk=0.008`)

---

## Q225 Patcher — Critical Constants

```python
STRIP1_HDR        = 0x0b0327
STRIP_SIZE        = 5638
HPF_REL           = 406
NAME_SEARCH_START = 0x0a2a5a
NAME_SEARCH_END   = STRIP1_HDR + STRIP_SIZE * 48   # must be *48, not *24
```

Template file size: **1,543,866 bytes** — output must match exactly.  
Spot-check Ch 1 name field copies: **~20** (never 0 or 1 — means NAME_SEARCH_END too narrow or old_name mismatch).

### DO-NOT-WRITE Tags

```python
0x1E0E, 0x1E0B, 0x1E11, 0x1E12          # Mustard Dynamic 2 slot
0x1D0E, 0x1D0F, 0x1D4A, 0x1D10, 0x1D12, 0x1D05
0x0503, 0x050e, 0x0511
0x08e1, 0x08e8, 0x0ee8, 0x0efe, 0x1d47
0x0a41c7                                  # reverb/room preset table — caused access violation
```

Tags `0x1Exx` / `0x1Dxx` look like SD comp/gate — they are Mustard. Do not write comp or gate until tags confirmed via console-save-diff method.

### Verified Safe EQ/Filter Tags

```python
TAG_EQ_ENABLE  = 0x0404    TAG_EQ_GAIN    = 0x0403
TAG_EQ_FREQ    = 0x0406    TAG_EQ_Q       = 0x0407
TAG_EQ_TYPE    = 0x040b    TAG_DEQ_ENABLE = 0x040e
TAG_DEQ_THRESH = 0x0411    TAG_DEQ_ATK    = 0x0412
TAG_DEQ_REL    = 0x0410    TAG_LPF_FREQ   = 0x0703
```

---

## Invocation Pattern

Upload input list + say:
```
Process this input list. Genre/influences: [description]. [Any per-channel notes not in the spreadsheet.]
```

- Genre missing → ask before EQ
- Ambiguous channel notes → ask before committing
- Stage 1 (MD/HTML/PDF) runs immediately if everything is present
- Stage 2 (.ses) runs only on explicit request: `Build the .ses from the MD.`
- Stage 3 (show packet PDF) is a separate request per CLAUDE.md

---

## Writing Rules (Quick Version)

Quick Summary paragraphs must read like a knowledgeable colleague wrote them:
- Reference genre and inline notes — explain *why*, not just *what*
- No AI tells: no "it's worth noting," "furthermore," "comprehensive," tripling, or fake balance
- Specific over general ("cut 6dB at 250Hz" not "reduce the low-mids")
- Contractions fine. Short sentences when the point is sharp.
- Full rules: `~/Documents/Claude/about-me/writing-rules.md`
