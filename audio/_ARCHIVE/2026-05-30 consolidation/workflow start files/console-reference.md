# Console Reference — Brian Lloyd

*Live mixing workflow conventions by console. Not a beginner's guide — this documents Brian's specific approach.*  
*Last updated: May 2026*

---

## General Conventions (All Consoles)

### Gain Structure
Drive the preamp to a solid level, then use the digital trim at the console to adjust. Don't compensate for a weak preamp with trim — get it right at the stage box.

### VCA Groups (Standard Layout)
| VCA | Contents |
|---|---|
| Drums | All drum channels |
| Instruments | All instrument channels (guitars, keys, bass, horns, strings, etc.) |
| Vocals | All vocal channels |
| FX | Effects returns |

This layout is the default for all shows. Deviations get noted in show paperwork.

### EQ Philosophy
- Cuts before boosts — always
- Vocals: cuts only, no exceptions (feedback control)
- Classical/acoustic shows: conservative cuts-only across the board
- Instrument EQ starting points: see `eq-starting-points.md`

---

## DiGiCo Quantum 225 (Q225)

**Used at:** Memorial Hall (house), Fountain Square (FOH)

### Key Workflow Notes
- Master template: `~/Documents/Claude/audio/Memorial Hall/brian memo v2.ses` — never edit directly, always copy-and-patch for shows
- Patcher workflow and .ses file format: see `Q225 SES Patcher SOP/` folder
- Show-specific .ses files go in the show folder: `YYYY-MM-DD ShowName/`

### Live Mixing Notes
- The Memo PA is tuned and running Lake processing — do not touch system processor settings
- Anchor channel: establish early in soundcheck, use as your reference point throughout the mix
- Workflow reminders (from processing docs): VCA assignments, manual-entry channels, and any pre-show console setup requirements are listed in the Channel Processing document for each show
- Mustard plugin: OFF on all channels unless Brian explicitly activates it. Writing to Mustard tags via script activates it on every touched channel — see SES patcher SOP for full DO-NOT-WRITE list

### Royer AxeMount (Memorial Hall — SR Guitar)
- CH 13: SM57 (primary) — set level first
- CH 15: R-121 (blend) — bring up from zero, typically 6–10 dB below SM57
- Polarity check in mono before advancing the blend — should be fuller, not thinner
- Post-blend: watch 300–500 Hz buildup on bus EQ
- ⚠ CH 15 phantom power must be OFF — R-121 is a ribbon

### SR Guitar VCA
- Group both CH 13 and CH 15 to the same VCA for level riding after blend is set

---

## Midas M32

**Used at:** Washington Park (FOH), Fountain Square (monitors), in rotation at other venues

### Key Workflow Notes
- At FSQ, M32 is dedicated monitor console — does not rotate to FOH at that venue
- At WP, M32 is FOH
- At smaller 3CDC venues (CSP, ZP, IA), M32 may rotate in as FOH when Wing is not available

### Live Mixing Notes
- *[Add M32-specific workflow notes as they come up — routing conventions, scene recall behavior, etc.]*

---

## Behringer Wing

**Used at:** Elm Street Plaza (fixed installation), secondary venues in rotation

### Key Workflow Notes
- Fixed Wing console at ESP — does not travel from that venue
- Wing also used at KSO/Greaves and other traveling gigs where a compact console is needed
- *[Add Wing-specific workflow notes as they come up]*

### Greaves Concert Hall (NKU) — Wing Notes
- Behringer Wing is the console for KSO Simon & Garfunkel Tribute and similar shows at NKU
- 40-channel shows are typical at Greaves; Wing handles this comfortably
- *[Add Greaves-specific routing/patching notes as discovered]*

---

## Yamaha CL3

**Used at:** In rotation — various venues

### Key Workflow Notes
- *[Add CL3-specific workflow notes, scene recall conventions, and routing as they come up]*

---

## Console-Agnostic Show Prep Checklist

These apply regardless of which console you're on:

1. Confirm input list against actual patch — don't trust paperwork blindly
2. Confirm phantom power assignment before soundcheck (ribbon mics, passive DIs)
3. Polarity check all coincident mic pairs before advancing levels
4. Set VCA assignments before soundcheck begins
5. Establish anchor channel early
6. Check system processor status — do not adjust tuned systems
7. Manual-entry channels (those not written by the patcher) — set before show, note in processing doc

---

*Add console-specific notes after each show as quirks, behaviors, or workflow refinements are discovered.*
