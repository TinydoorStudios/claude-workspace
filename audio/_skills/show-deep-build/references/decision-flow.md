# Decision Flow — full detail

The five steps in order, the reconciliation logic, and two worked examples. The SKILL.md body is the
summary; this is the depth.

## Mental model

You're stacking filters on a baseline. Each step can only *narrow or bend* what the last step
produced — never throw it away. The instrument sets the problem space, the mic shifts it, the
web+KB baseline gives you sourced numbers, the genre bends the targets, and the room does the final
shaping. Cuts first, the whole way down.

**Order of importance = order of process (locked 2026-07-05): instrument → mic → genre → venue.**
The room is often the biggest single bend in dB, but it ranks last in decision authority — it trims
and vetoes, it never replaces the instrument + mic foundation.

Confidence is cumulative too. If you finished a step on a guess, you carry that uncertainty forward
and it compounds. That's why the stop-and-ask gate matters most early — an unsure mic identification
poisons everything after it.

---

## Step 1 — Instrument / source

Get specific. The EQ problem for "electric guitar, cranked Marshall, SM57 on the grille" is a
different animal from "clean jazz archtop into a Polytone." Capture:

- The instrument and how it's being played (fingerstyle vs. pick, brushes vs. sticks, arco vs. pizz).
- One mic, two mics on one source (a **blend** — treat as one signal), or a section.
- Source role in the mix: lead, support, pad, rhythm. A piano comping behind a horn solo gets carved
  differently than a solo piano feature.

If the source is genuinely unclear from what Brian gave you, ask. This is cheap to confirm and
expensive to get wrong.

---

## Step 2 — Mic / DI

The mic is the single biggest swing on the baseline because it changes what's *already in* the signal.

Resolve the model precisely, expanding Brian's shorthand against `mic-library.md` and the `CLAUDE.md`
mic table (DM6, DM17, SR20, MKH40, 87 JR = WA-87 — Brian's ONLY "87", no Neumann U87 in the kit; any
"421" = the vintage MD 421-U Silver Tail, never the 421-II; Beta 58A, RNDI, J48, DPA 4099, B3, R88, etc.).

Then read the mic's **EQ tendency** from `mic-library.md`. The KB classifies every mic as one of:

- **"apply template as-is (flat/honest)"** — DM6, DM17, SR20sp, SM81, Line Audio OM1/CM4, J48. These
  take the full instrument shaping; the mic adds nothing and hides nothing.
- **"ease off X"** — the mic already delivers X, so pull that band back. (e.g. Audix D6: ease off
  attack, boom, box, mud — it's pre-scooped; Neumann KMS 105: ease off air/presence/proximity.)
- **"tame Y ~freq"** — the mic has a known problem peak to cut (e.g. SM57: tame box ~400 Hz; e609:
  tame harsh ~2800 Hz; TLM 102: tame sibilance ~8000 Hz).

Most mics carry both an "ease off" and a "tame." Apply both against the instrument baseline.

**Flag before any math:**

- **Ribbon** (R-121, R-10, R88) → NO 48V, in red. Always.
- **Blend** → back the complement mic's 150–800 Hz off ~half; plan mono + polarity check; notch
  300–500 Hz on the bus if it stacks. See the Two-Mic Blends table in `mic-library.md`.
- **Mic not in the KB** → research it (Step 3) and treat as a stop-and-ask.

### Step 2b — the locker loop

With the mic resolved, sweep `mic-library.md` (loaded once per session) for a better fit *from
gear Brian actually owns*. First-call match → silent pass. A concrete win (less-EQ voicing, a
problem peak that collides with this genre/room, rejection margin, SPL, kit coherence) → record
one alternative with a one-line why. Never on TOUR/artist gear. Suggestions batch into the show
build's single up-front question round; an accepted swap re-enters at Step 2. The EQ you build is
always for the *specified* mic — the alternative is advice, not a substitution.

---

## Step 3 — Baseline: web first, then KB, reconcile

The order is deliberate: **search the community first so you arrive at the KB with an outside read,
then let the two check each other.**

### 3a. Web

Search the LAB (Pro Sound Web) and Gearspace Live Sound for this mic on this instrument, plus the
manufacturer frequency-response curve for the mic's baseline character. Pull:

- Concrete settings engineers report (HPF point, the cuts they reach for, any boost).
- The mic's response shape (presence bump, proximity, HF rolloff, scoop).
- Consensus vs. one-off opinion — weight accordingly.

`forum-research.md` has the query templates and the trust hierarchy.

### 3b. KB

Now compare to:

- `mic-library.md` → the mic's character + EQ tendency, blend logic.
- `eq-starting-points.md` → the instrument's approach and known problem zones.
- `mic-dpa-4099.md` and any source-specific article when relevant.

### 3c. Reconcile — the verification gate

| Web vs. KB | What to do |
|---|---|
| **Agree** | Solid sourced baseline. Proceed to Step 4. |
| **KB silent, web has clear consensus** | Use the web consensus; note it's web-sourced, not yet KB-verified. Offer to write it back to the KB after. |
| **Web silent/thin, KB has it** | Use the KB; it's Brian's verified knowledge. |
| **They disagree** | **STOP.** Show both, give your read, ask Brian which way. Do not average. |
| **Both silent** (unknown mic + unknown combo) | **STOP.** Present what little you have and ask. |

A disagreement between a respected forum thread and the KB is *information* — usually it means the
forum is talking about a different room, PA, or playing style than Brian's. Surface it; don't bury it.

Every move out of this step should be traceable to a source: KB article, forum consensus, or
manufacturer spec. If you can't cite it, it's a guess — stop.

---

## Step 4 — Genre + artist

Bend the sourced baseline toward the genre's signature. See `genre-profiles.md` for per-genre detail;
the spine is the Genre Modifiers in `eq-starting-points.md`.

Genre sets three things:

1. **Aggressiveness** — acoustic-forward = lighter; dense/loud = deeper cuts for separation.
2. **Tonal target** — what the source should *sound* like in that style (thump vs. click vs. natural).
3. **Hard rules** — classical cuts-only/minimal; celtic 5 ms+ attack and never gate sustained notes;
   acoustic/piezo DI always cuts the 1.5–2 kHz quack.

**Then refine with the artist profile** (from the deep build's artist research). It's specific
evidence about this show, so where it and the generic genre profile differ, the artist wins:
vocal character sets the presence/proximity handling, tone references bend the guitar and keys
targets, arrangement density scales how deep the separation cuts go, production style sets the
overall restraint-vs-aggression posture within the genre's frame.

Ambiguous or hybrid genre → ask. "Jazz" covers a quiet trio and a wall-of-brass big band, and they
sit at opposite ends of the aggressiveness scale.

---

## Step 5 — Venue, room, philosophy

The heaviest filter. Default posture: **cuts not boosts, mostly aggressive, because the rooms are
reverberant and often outdoor.**

1. **Venue file** (`venue-*.md`) for the show's room:
   - **Memo:** standing waves 63 / 125 / 200 / 250–315 Hz — boosts there are suspect, cuts favored;
     bodhrán/kick highest risk; DEQ where static won't hold; crowd rig EQ is fixed (don't touch).
   - **FSQ / outdoor:** aggressive scale, higher HPF, no room gain to lean on.
   - **Greaves / classical recording:** correction-only, conservative.
2. **Global philosophy** (`CLAUDE.md` / `eq-starting-points.md`):
   - Cuts before boosts, subtractive first.
   - **Vocals cuts-only, every genre** (feedback control).
   - Whole-dB only. No high shelf unless asked.
   - Cuts −4 to −7 dB tight Q (1.5–2.0); non-vocal boosts +3 to +6 dB when justified.
3. **Live vs. post:** live = feedback-aware, cut-heavier, HPF decisive. Post/recording = correction
   only, gentler, trust placement.

A move that survives all five steps and doesn't trip a stop-and-ask is ready to output.

---

## Worked example A — SM57 on electric guitar cab, blues-rock, Memorial Hall, Q225

1. **Instrument:** electric guitar cab, driven, rhythm + solos.
2. **Mic:** SM57. KB tendency: mid-forward workhorse, builds box/honk 300–500 Hz, thin lows, can be
   harsh upper-mids → *tame box ~400 Hz.*
3. **Web → KB:** LAB/Gearspace consensus on 57-on-cab: HPF ~80–100, cut the 300–500 mud, presence
   lives 2.5–4 k. KB agrees (box ~400, presence 3–5 k). **Agree → baseline:** HPF 100, cut ~400 box,
   cut ~450 mud, lift presence ~2.5 k if the amp's dull.
4. **Genre (blues-rock):** wants body and warmth, moderate aggression; keep some low-mid, don't
   over-scoop. Tonal target: thick but present.
5. **Venue (Memo, Q225):** 250–315 Hz standing wave overlaps the cab's low-mid mud — favor the cut at
   ~300 over a boost anywhere near it. Reverberant room → keep it tight. Output in Q225 layout:
   `HPF 100 · LPF off · B4 — · B3 +4 @ 2.5 k Q1.0 · B2 −5 @ 450 Q2.0 · B1 −4 @ 300 Q1.8`. Whole dB,
   cuts-first. Reasoning paragraph cites the 400 box (mic) + 300 room overlap.

No stop needed — web and KB agreed and nothing fought the room.

## Worked example B — unknown mic, "indie folk", outdoor

1. **Instrument:** acoustic guitar, fingerstyle, lead.
2. **Mic:** a model not in `mic-library.md`.
3. **Web → KB:** forum has a couple of posts, no strong consensus; KB silent on the mic. **Both
   effectively silent → STOP.** Tell Brian: "I don't have [mic] in the library and the forum reads
   are thin/split — here's the instrument baseline for fingerstyle acoustic and the one forum setting
   I found; do you want me to run with the acoustic template and your conservative folk approach, or
   do you know this mic's character?" Wait.
4. (after answer) **Genre (folk):** conservative, cuts-only, watch piezo quack 1.5–2 kHz if it's a
   pickup blend.
5. **Venue (outdoor):** aggressive HPF, no room gain; decisive low-mid cut. Output + PDF.

The stop in B is the whole point — guessing the mic character would have compounded through every
later step.
