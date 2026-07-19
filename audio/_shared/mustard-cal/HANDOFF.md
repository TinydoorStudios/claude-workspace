# Handoff — Mustard .ses decode

*2026-07-15, Nyquist. Paste this into a fresh session to pick the work up.*

## What this is

Teaching `audio/_shared/q225_ses_engine.py` to write DiGiCo Mustard settings. Mustard is currently on the engine's `DO_NOT_WRITE_TAGS` list — mapped as dangerous, never decoded, so every show's Mustard has to be dialled in by hand at the desk.

Brian's instruction: **map everything.**

## Where it stands

**The map is done and it's in [MUSTARD-MAP.md](MUSTARD-MAP.md) — read that first, it's the deliverable.** 26 parameters across both Mustard blocks, every one measured with a two-point capture and a single-parameter diff. Nothing inferred from resting values.

Headlines:
- Records are `tag(u16) + bidx(u16) + f32`, same shape the engine already writes for EQ.
- `0x1Dxx` = Mustard Dynamics 1 (comp), `0x1Exx` = Mustard Dynamics 2 (gate/duck/MSE). The blocks mirror each other.
- CH1 comp threshold at `0x25499A5`, **stride `0x16AE` (5806 B)**, verified on all 40 channels.
- Four traps: attack/release/hold are in **seconds** (displayed in ms); mix is **0–1** (displayed 0–100); **changing type resets the whole block**, so type must be written first; the comp model enum is **not sequential** (Blue 0, Red 3, Green 4, Purple 5, Silver 8).

21 captures, `mc00`–`mc20`, in `~/.wine/drive_c/Projects/`. The per-capture log is in [RESUME.md](RESUME.md).

## UPDATE 2026-07-15 (later session) — the engine work is DONE, pending console verification

`q225_ses_engine.py` now writes Mustard. Item 3 below is finished; items 1, 2 and 4 still stand.

Three things the map got wrong, all found and corrected before any code shipped:

1. **The absolute offsets were unusable.** `0x25499A5` is past the end of the 3.78 MB production template — the captures are 39.9 MB because the editor inflates on resave. Fixed properly rather than by re-deriving a base: each fader's Mustard block sits **inside that fader's existing channel block**, so the bounds the engine already resolves for EQ locate Mustard too. No new calibration, and nothing to redo when a template is resaved.
2. **The framing is the opposite of the EQ blocks** (value *after* the tag, not before). Both read as self-consistent, so the failure mode is silent. Mustard must never go through the engine's `_records()`.
3. **`0x1D00`/`0x1E00` are headers, not records** — the "garbage float" is the channel name. Guarding them made every rename look like corruption.

Also: the "type resets the block" rule is an editor-GUI behaviour, not necessarily a file/console one — see the map's gotcha 3.

What shipped: `write_mustard()`, `_must_rec()`, `COMP:`/`GATE:` MD syntax with unit conversion at the boundary (ms→s, %→0–1) and model-specific validation, a framing-correct do-not-write guard for the still-unmapped tags, and Mustard readback folded into the existing per-channel readback. Unmapped tags stay blacklisted in `MUSTARD_DO_NOT_WRITE`. Mustard is opt-in: no `COMP:`/`GATE:` line means not a byte moves.

Tested: existing shows produce **byte-identical** output to the pre-change engine; a synthetic MD across all five comp models and all three D2 types verifies clean on both venues, independently re-decoded.

**CONSOLE-VERIFIED 2026-07-16.** Brian loaded a Back to Black test build on the Q225 (all five comp models, Gate/Duck/MSE) and confirmed every value read back correctly — including the open question, "does the console re-apply the type→defaults reset on load?" It does **not**: a file whose model differs from the template's loads with its written parameters intact. The MD syntax (`COMP:`/`GATE:`) is signed off. The writer is production. Same day, the real Back to Black.ses was regenerated with the deep-build's reasoned Mustard, and the pipeline was wired: `md_lint` validates the lines (via the engine's own parser), and `show-deep-build` now emits them for any Q225 channel whose reasoning lands on a comp or gate.

### The MD syntax (needs Brian's sign-off)

Two optional lines per channel, alongside the existing `HPF:` / `B1:`–`B4:` lines. Written in **display units** — ms and percent — because that's what the desk shows; the engine converts at the boundary.

```
COMP: Blue | in | thr=-18 | ratio=4 | atk=12ms | rel=180ms | makeup=2 | mix=90 | knee=hard | det=peak | sc=80-8k
GATE: Gate | in | thr=-35 | atk=3ms | hold=180ms | rel=200ms | range=40
```

Models: `Blue` `Red` `Green` `Purple` `Silver`. D2 types: `Gate` `Duck` `MSE`. `in`/`out` sets enable. Levelling Amp takes `peak=` / `gain=` / `limit` instead of thr/ratio: `COMP: Silver | in | peak=31 | gain=17 | limit`. MSE accepts `depth=` as an alias for `range=` (same tag — the type decides what the desk calls it). Every field is optional; anything omitted keeps the template's value. The parser rejects controls a model doesn't have (`atk=` on Red, `thr=` on Silver) rather than writing a byte the desk will ignore.

## What's left

1. **~13 unmapped tags.** Listed at the bottom of the map. All rest at 0/1/3/−20 and I can't tie them to a GUI control. `0x1D41` is the interesting one — it rests at −20 and looks exactly like a threshold, which is why my early guess that it was the gate threshold was wrong (that's `0x1E0E`). Leave them all in `DO_NOT_WRITE_TAGS`.
2. **A few page controls not yet captured:** the MSE release 3-state (slow/medium/fast), `self` / `external key / side-chain`, `comp s/c`, `mse key` / `gate key`, `key listen`. **In progress when I stopped:** I had just clicked "fast" on the MSE release selector on CH1 and had NOT saved it. So the editor currently holds an unsaved change on top of `mc20` — either save it as `mc21` and diff against `mc20`, or reload `mc20` and start clean. Don't assume the editor is in a known state; check the Master screen's File line for the `*` modified flag.
3. ~~**Then the engine work**~~ — **DONE**, see the update above. Remaining engine-adjacent gaps: `md_lint.py` does not yet know about `COMP:`/`GATE:` lines (the engine validates them itself and aborts cleanly, so nothing unsafe gets through — but lint is the documented first gate and should learn them), and the show-deep-build skill doesn't emit Mustard into its MDs yet, so nothing in the pipeline produces a `COMP:` line today.
4. **Human gate unchanged:** Brian loads a patched file on the Q225 and says "verified". Nothing ships before that. **None of this is console-verified yet.**

## Rig notes (the part that costs hours if lost)

Full detail in [RESUME.md](RESUME.md). The three that matter:

- **Clicks are scaled.** Screenshots are 1728 px wide, computer-use clicks are in a 1372-wide space: **click = coord × 0.794**. Unscaled clicks land harmlessly and the tool still reports success. This ate an hour.
- **Screenshots must come from the shell** (`cap.sh` → read `cur_s.png`). The computer-use screenshot tool can never see the Wine window. Launch the editor via `/Applications/Quantum Cal.app` (a wrapper I built); `Quantum 225.app` produces a process macOS can't grant.
- **Opening the Mustard page** (Brian's gesture, took several rounds to learn): front Channel Surface 1 by clicking its **title bar** at (120,40) — the Master/Left/Right buttons do NOT reliably raise it — then click the **M** button next to SD on the strip (CH1 = (198,584)) to switch the strip to the Mustard section, then **right-click the comp threshold knob** (CH1 = (182,469)). Sometimes needs two right-clicks; the first only fronts the window. **The page closes on every save**, so this repeats before each capture.

## Method

`tagdiff.py <a> <b>` (in this folder) does the decoding. It anchors on each differing byte and searches backwards for a record whose value field covers it, and it prints any diff run it *can't* explain.

**Don't replace it with a forward scan.** The first version scanned greedily forward, misaligned on a block header, and silently skipped the type tag — which is also how I briefly mislabelled `0x1D47` (mix) as the comp enable (`0x1D02`). Both errors are corrected in the map; the point is the differ is what catches them.

Every save rewrites ~2,875 timestamp doubles (46000–46500 range) plus a UI region at `0x2600000–0x2620000`. The differ filters both.

**Batching trick that made this affordable:** several continuous parameters can move in ONE save because their distinct values self-identify in the diff. Toggles can't (all 0↔1), so pair at most one comp toggle with one gate toggle — the different tag blocks disambiguate them.

## Files

| File | What |
|---|---|
| `MUSTARD-MAP.md` | **the result** — the byte map |
| `RESUME.md` | rig setup, click coords, capture log |
| `tagdiff.py` | the differ |
| `cap.sh` | screenshot helper |
| `~/.wine/drive_c/Projects/mc00–mc20.ses` | the captures (not in the repo — 40 MB each) |
