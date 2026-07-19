# Console Band Layouts

Step-5/output detail: the recommendation is reasoned in plain frequency moves, then mapped onto the
**actual console's** bands. Get the layout right so the numbers drop straight onto the desk.

The KB console articles are canonical — pull `console-digico-q225.md`, `console-behringer-wing.md`,
`console-yamaha-cl3.md`, `console-midas-m32.md` for the desk in use. This is the working summary; if a
detail here ever conflicts with the KB article, the KB wins.

## Scope — which desks this skill targets

**Default to Q225 or Wing**, picked from the venue: Q225 for Memo and FSQ FOH, Wing for the secondary
venues. **Do not generate CL3 or M32 output unless Brian explicitly names that console** — he isn't
using this skill for those desks by default. The CL3 and M32 layouts below are kept for the times he
does ask; otherwise skip them.

---

## DiGiCo Quantum 225 (default — Memo house, FSQ FOH)

Mustard Processing EQ: **HPF + LPF + 4 bands.**

- **Display order high→low:** `HPF → LPF → Band 4 → Band 3 → Band 2 → Band 1`.
- **Band numbering matches the console:** Band 1 = LF, Band 2 = lower-mid, Band 3 = upper-mid,
  Band 4 = HF.
- Every band switchable **Shelf/Bell**; any band in **Bell** mode can be **Dynamic (DEQ)**.
- **No separate low-shelf control** — a low shelf is **Band 1 in shelf mode**.
- Gain **±18 dB**, Q **0.3–10**, LC slopes **6/12/18/24 dB/oct**.
- Alt EQ models available: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG.

**Canonical output columns** (this is the show-paperwork layout):
`CH · Instrument · HPF · LPF · Band 4 · Band 3 · Band 2 · Band 1 · Notes`

DEQ goes in Notes/Details (threshold, attack ms, release ms). This is the default the PDF script
renders.

### Mustard dynamics — paperwork only, NOT written to the .ses (pulled 2026-07-16)

The Q225 patcher can write **Mustard Dynamics 1 (compressor)** and **Dynamics 2 (gate / duck /
MSE)** per channel from two optional MD lines — console-verified on the Back to Black build,
then pulled from the build the same day on Brian's call after hearing the activation live. The
writer (`write_mustard()`) and decode notes still live in the engine / `audio/_shared/mustard-cal/`,
but `main_cli()` no longer calls it — COMP:/GATE: lines are parsed and linted, never patched into
the .ses. Dial comp/gate in on the desk at soundcheck instead.

Still emit these in the FOH Channel Processing .md **whenever the deep build reasons dynamics for a
channel** — they document the reasoning on the same footing as the EQ, even though the build now
ignores them:

```
COMP: <model> | in|out | thr=.. | ratio=.. | atk=..ms | rel=..ms [| makeup=.. | mix=..% | knee=hard|soft | det=peak|rms | sc=<lo>-<hi>]
GATE: Gate|Duck|MSE | in|out | thr=.. [| atk=..ms | hold=..ms | rel=..ms | range=..]
```

- **Comp models** (from the reasoning, not invented): `Blue` (Neve), `Red` (Vintage VCA — no
  atk/rel), `Green` (FET/1176), `Purple` (Optical/LA-2A), `Silver` (Levelling Amp — uses
  `peak=`/`gain=`/`limit`, not thr/ratio). These are the Mustard colours the KB already names.
- **D2**: `Gate`, `Duck` (the KB's "light ducker over hard gate on acoustic-forward" rule), `MSE`.
  There is **no Expander mode** — realize a spec'd downward expander as a shallow-`range` Gate, or
  leave it for the desk; say which in `mic_notes`.
- **Threshold is a soundcheck call.** The worksheets reason model/ratio/timing + a **GR target**;
  write a documented *starting* threshold (≈ −6 dBFS program peak minus GR/(1−1/ratio), whole dB)
  and carry the GR target into `mic_notes` so it's dialed in the room. Everything omitted keeps the
  template default — Mustard is fully opt-in per channel.
- Units are **display units** (ms, %); the engine's parser (still used for linting) converts to
  seconds / 0–1. `md_lint` validates the syntax with that same parser, so lint and the paperwork
  agree on format — even though nothing gets patched into the .ses.
- Ambient/room/crowd mics and instruments the reasoning leaves flat get **no** Mustard line — the
  build never touches any channel's dynamics blocks now, lined or not.

---

## Behringer Wing (secondary venues)

**6-band parametric:** `L · 1 · 2 · 3 · 4 · H` — **L and H switchable Bell/Shelf.**

- More bands than the Q225 → you rarely have to drop a move; you can place both an "ease off" and a
  "tame" plus a low shelf without competing for a slot.
- Aux/Bus EQ is **4 bands.**
- LC slopes 6/12/18/24; HC slopes 6/12.
- Filter slot also offers **Tilt EQ / Sonic Maximizer / All-Pass.**
- Alt EQ models: SSL 4000E, Neve 88, Neve 1084, Focusrite ISA110, Pultec, MAAG.
- **Known issue:** FX preset save/load broken since firmware v1.13; `.efx` files incompatible — don't
  route an EQ recommendation through an FX preset.

Map the Q225-style reasoning onto: `HPF · L · Band 1 · Band 2 · Band 3 · Band 4 · H · LPF`. Use L/H in
shelf mode where the Q225 would use Band 1 shelf / a requested high shelf.

---

## Yamaha CL3 — only on explicit request

*Not a default target. Use this layout only when Brian names the CL3.*

Channel EQ: **4-band parametric + dedicated HPF.**

- Low band switchable to shelving / HPF-type; High band switchable to shelving / LPF-type.
- Same 4-slot constraint as the Q225 — prioritize moves (see *Translating across band counts*).
- Premium Rack EQs (e.g. Portico-style) available if a channel needs a different curve — note it in
  the recommendation rather than assuming it.

Confirm specifics against `console-yamaha-cl3.md` before committing band-type behavior.

---

## Midas M32 — only on explicit request (WP FOH, FSQ monitors)

*Not a default target. Use this layout only when Brian names the M32.*

Channel EQ: **4-band fully parametric + dedicated low-cut.**

- Low and high bands switchable between shelf and parametric.
- 4-slot constraint — prioritize like the Q225.
- Pair with the venue: WP is outdoor (aggressive), FSQ monitors are about gain-before-feedback, not
  tone-shaping.

Confirm against `console-midas-m32.md`.

---

## Translating across band counts

The recommendation is a set of frequency moves ranked by importance (Step 5 already ordered them:
HPF first, then the biggest problem cut, then the next, then any character). Map them like this:

- **4-band desk (Q225 / CL3 / M32):** you have HPF + LPF + 4 bands. If you have more than 4 tonal
  moves, **keep the highest-priority four and drop or combine the rest** — and say so in the reasoning
  ("dropped the −2 @ 5 k air; not enough bands and it's the least important move"). Two adjacent cuts
  can sometimes be merged into one wider-Q cut between them.
- **6-band desk (Wing):** place everything; use L/H shelves freely.
- If a move genuinely needs a band the desk doesn't have, or the mapping is forced, that's a
  **stop-and-ask** — don't silently mangle the intent to fit the slots.

Always state which console the output is for at the top of the recommendation, so there's no ambiguity
about which band layout the numbers belong to.
