# DiGiCo Q225 — Mustard .ses byte map

*Decoded 2026-07-15 from controlled offline-editor captures on the FSQ template. Every row below was measured with a two-point capture and a single-parameter diff. Nothing here is inferred from a resting value.*

**Not yet console-verified.** The engine must not write any of this until Brian loads a patched file on the Q225 and says "verified."

---

## Structure

Mustard lives in two per-channel blocks, same 8-byte record shape the engine already uses for EQ:

```
tag (u16 LE) | bidx (u16 LE) | value (f32 LE)
```

| Block | Tag range | Header | What it is |
|---|---|---|---|
| Mustard Dynamics 1 | `0x1Dxx` | `0x1D00` | the compressor |
| Mustard Dynamics 2 | `0x1Exx` | `0x1E00` | the gate / ducker / MSE |

The two blocks mirror each other: `0x1D0E`/`0x1E0E` are both threshold, `0x1D11`/`0x1E11` both attack, `0x1D12`/`0x1E12` both release, `0x1D02`/`0x1E02` both enable, `0x1D03`/`0x1E03` both sidechain-filter-on, `0x1D05`/`0x1E05` both sidechain filter freq, `0x1D0B`/`0x1E0B` both type.

### Record framing — read this before using any offset below

A Mustard record is **tag, then value**: the f32 sits at `tag_offset + 4`.

This is the **opposite** of the EQ records `q225_ses_engine.py` has always written, where the value sits 4 bytes *before* the tag (that's what the engine's `_records()` returns). Both are correct for their own block. The catch is that a record stream reads as self-consistent under either convention — get it backwards and you silently read (or write) the **neighbouring record's** value, with no error. The proof that this framing is the right one for Mustard: at `tag+4` every resting value matches the table below (thr −20, ratio 3, atk 0.01, rel 0.25, mix 1, range 40); at `tag−4` they don't.

### Channel addressing — do NOT use absolute offsets

~~CH1 comp threshold = `0x25499A5`, stride `0x16AE`.~~ **That base is wrong for the file the patcher actually writes**, and this section originally said so without noticing.

The captures `mc00`–`mc20` are 39,910,257 bytes because the offline editor **inflates the file when it resaves**. The production FSQ template (`brian fsq start.ses`) is **3,779,766 bytes** — `0x25499A5` (≈39.1 MB) is past the end of it. (`MCAL SRC.ses` is md5-identical to the production template, so the capture *lineage* is sound; only the offsets are editor-relative.)

The structure itself transfers perfectly. The same 64-channel, `0x16AE`-strided array sits at **`0x2D4AEA`** in the production template — and, better, **each fader's Mustard block lives inside that fader's existing current-scene channel block**. So the bounds the engine already resolves for EQ (name-scan on FSQ, positional on Memo) locate Mustard too:

> **Find Mustard structurally inside the fader's block. No new calibration, no absolute base, nothing to re-derive on a template resave.**

Confirmed: every mapped tag is present **exactly once** inside **every** fader block — all 64 FSQ faders and all 72 Memo faders. The stride/base are useful only for reasoning about the captures.

---

## Mustard Dynamics 1 — compressor

| Tag | Parameter | Encoding | Confirmed by |
|---|---|---|---|
| `0x1D02` | comp in/enable | 0.0 = out, 1.0 = in | mc01→02 |
| `0x1D0B` | **model / type** | enum, see below | mc11→12→13→14→15 |
| `0x1D0E` | threshold | float dB, **direct** | −20.0 → −9.88231 |
| `0x1D09` | makeup gain | float dB, direct | 0.0 → 0.917647 |
| `0x1D10` | ratio | float, direct | 3.0 → 4.03923 |
| `0x1D11` | attack | **SECONDS** | 12.4 mS → 0.0123853 |
| `0x1D12` | release | **SECONDS** | 312 mS → 0.312321 |
| `0x1D47` | mix | **0–1**, not 0–100 | 90% → 0.901961 |
| `0x1D0F` | knee | 1 = hard, 0 = soft | mc07→08 |
| `0x1D46` | detector | 0 = RMS, 1 = peak | mc08→09 |
| `0x1D03` | sidechain filter on | 0 / 1 | mc10→11 |
| `0x1D05` bidx **1** | sidechain LOW Hz | float Hz, direct | 20 → 39.3684 |
| `0x1D05` bidx **0** | sidechain HIGH Hz | float Hz, direct | 20000 → 10160.4 |
| `0x1D50` | compress / limit | 0 = compress, 1 = limit | mc18→19 |
| `0x1D51` | **Levelling Amp** gain | float, direct | 25 → 32 |
| `0x1D52` | **Levelling Amp** peak reduction | float, direct | 20 → 29 |

`0x1D50/51/52` only apply when type = DYN Silver (Levelling Amp), which replaces thresh/ratio/attack/release with peak reduction + gain + compress/limit.

### Model enum (`0x1D0B`) — measured, NOT sequential

| Model | Description | Value |
|---|---|---|
| DYN Blue | Classic | **0** |
| DYN Red | Vintage VCA | **3** |
| DYN Green | FET Limiter | **4** |
| DYN Purple | Optical Compressor | **5** |
| DYN Silver | Levelling Amp | **8** |

1, 2, 6, 7 are unaccounted for — do not interpolate. Menu order is Blue/Red/Purple/Green/Silver, which is *not* the value order; a "reasonable guess" here would have been wrong for three of the five.

**Changing the type resets every other parameter in the block to that model's defaults.** So type must be written FIRST, then the parameters — writing them in the other order silently discards them.

Models expose different controls: Vintage VCA has no attack/release. Levelling Amp replaces thresh/ratio/attack/release with peak reduction + gain + compress/limit.

---

## Mustard Dynamics 2 — gate / ducker / MSE

| Tag | Parameter | Encoding | Confirmed by |
|---|---|---|---|
| `0x1E02` | gate in/enable | 0.0 / 1.0 | mc09→10 |
| `0x1E0B` | **type** | 0 = Gate, 1 = Duck, 2 = MSE | mc15→16→17 |
| `0x1E0E` | threshold | float dB, direct | −20 → −14.1176 |
| `0x1E11` | attack | **SECONDS** | 3.20 mS → 0.00319602 |
| `0x1E12` | release | **SECONDS** | 183 mS → 0.183418 |
| `0x1E13` | hold | **SECONDS** | 187 mS → 0.187467 |
| `0x1E0A` | range | float dB, direct | 40 → 46.2353 |
| `0x1E03` | sidechain filter on | 0 / 1 | mc10→11 |
| `0x1E05` bidx **1** | sidechain LOW Hz | float Hz, direct | 20 → 36.2956 |
| `0x1E05` bidx **0** | sidechain HIGH Hz | float Hz, direct | 20000 → 11323.3 |

The gate enum IS sequential — but that's a coincidence of this block, not a rule. The comp's isn't.

**D2 tags are reused across its three types.** With type = MSE, `0x1E0E` is the MSE threshold and `0x1E0A` is MSE **depth** (confirmed mc19→20: −20 → −14.8235, and 10 → 12.3922). So `0x1E0E` = threshold for Gate/Duck/MSE alike, and `0x1E0A` = range (Gate/Duck) or depth (MSE). A writer must know the type to label these correctly — the tag alone doesn't tell you which parameter the user sees.

---

## Gotchas that will bite

1. **Attack/release/hold are stored in seconds, displayed in milliseconds.** Writing `10` where the desk wants `0.01` is a 1000× error that will read back as an absurd value.
2. **Mix is 0–1, not 0–100.**
3. **Type resets the block.** Write type first. *(Caveat found during the engine work: this is an **editor GUI** behaviour — clicking a new model repopulates the block's defaults. A byte writer sets every field at once, so the ordering is moot in the file. What's still unknown is whether the **console** re-applies that reset when it loads a file whose type differs from the template's. The writer writes type first regardless — it costs nothing — but only Brian's console check settles it.)*
4. **The value is AFTER the tag** — the opposite of the EQ blocks. See the framing note above; getting it backwards fails silently.
4. **`s/c listen` is NOT stored in the .ses** — it produced zero tag changes when toggled. It's a monitor-only function. Don't try to write it.
5. **Every save rewrites ~2,875 timestamp doubles** (values in the 46000–46500 range) plus a UI/layout state region at `0x2600000–0x2620000`. Both are noise; the differ filters them.

---

## Still unmapped

Present in the blocks, resting values known, purpose NOT established. **Leave these in `DO_NOT_WRITE_TAGS`:**

| Tag | Rests at | Suspicion |
|---|---|---|
| `0x1D41` | −20 | ? — my early guess "gate threshold" was WRONG (that's `0x1E0E`) |
| `0x1D4C` | 3 | ? |
| `0x1D4A` | 1 | ? (already in the engine's do-not-write list) |
| `0x1D3F` `0x1D4B` `0x1D48` `0x1D49` `0x1DF5` `0x1D37` `0x1D4D` | 0 | ? |
| `0x1E4C` | 1 | ? |
| `0x1E16` `0x1E37` | 0 | ? |

`0x1D00` / `0x1E00` are the block **headers**, not records — and their "garbage float" is now explained: what follows a header is the **length-prefixed channel name**, not a value. Don't guard them as records. The engine did exactly that for one iteration and every channel rename looked like Mustard corruption.

Controls seen on the page but not yet tied to a tag: the MSE **release** 3-state (slow/medium/fast), `self` / `external key / side-chain`, `comp s/c`, `mse key` / `gate key`, `key listen`.

**Two page controls are NOT stored in the .ses.** `s/c listen` (mc09→10) and the round button under the MSE `release` label (mc19→20) both produced zero tag changes when toggled. `s/c listen` is clearly monitor-only. The release button is unexplained — clicking it lights a red ring but moves neither the slow/medium/fast arrow nor any byte. Do not try to write either.

One unexplained 2-byte change at `0x231A47A` (`ffff` → `1e00`) fired when the comp was first enabled. Outside both blocks. Not understood — worth knowing before any write goes near it.

---

## Method notes

`scratchpad/tagdiff.py <a> <b>` does the decoding. It anchors on each differing **byte** and searches backwards for a record whose value field covers it.

**Do not replace it with a forward scan.** The first version scanned greedily forward, misaligned on a block header, and silently skipped `0x1D0B` — which is how the type tag got missed on the first pass and why an early write of `0x1D47` would have set the mix while I believed it was the enable. The differ now reports any diff run it *can't* explain as a tag record, which is what catches that class of error.

Batching trick that made this affordable: several continuous parameters can move in ONE save because their distinct values self-identify in the diff. Toggles can't (they're all 0↔1), so pair at most one comp toggle with one gate toggle — different tag blocks disambiguate them.
