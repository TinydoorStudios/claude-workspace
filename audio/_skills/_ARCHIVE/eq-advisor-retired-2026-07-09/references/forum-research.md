# Forum & Web Research

How to do Step 3a well: where to look, how to query, what to pull, and how much to trust it.

## Where to look (in order of trust)

1. **The LAB — Pro Sound Web.** The Classic Live Audio Board. Working FOH/monitor engineers, real
   rooms. Best source for *live* mic-on-source settings and feedback-aware moves.
   - Forums home: `https://forums.prosoundweb.com/index.php`
   - The LAB (board 9): `https://forums.prosoundweb.com/index.php?board=9.0`
   - Real-name posting culture → higher signal than most audio forums.
2. **Gearspace — Live Sound board** (formerly Gearslutz). Big archive, more studio crossover.
   - `https://gearspace.com/board/live-sound/`
   - Thread URLs look like `gearspace.com/board/live-sound/<id>-<slug>.html`.
   - Also useful: the post-production board for mix/master EQ on a captured source.
3. **Manufacturer frequency-response spec** for the mic's baseline curve (Shure, Sennheiser,
   Earthworks, DPA, Audix, AKG, Neumann, Royer). Use this for the *shape* (presence bump, proximity,
   HF rolloff), not for "settings."
4. **Reputable engineer write-ups / interviews** (SOS, mix-engineer breakdowns) as supporting, not
   primary.

Skip: SEO listicles, AI-generated "ultimate EQ chart" pages, and anything with no named author and
no reasoning. A number with no "why" behind it is worthless here.

## How to search

The forums' built-in search is weak. Prefer a site-scoped web search:

- `site:forums.prosoundweb.com <mic> <instrument> EQ`
- `site:gearspace.com/board/live-sound <mic> <instrument> EQ`
- `<mic> <instrument> live EQ prosoundweb`  /  `<mic> <instrument> EQ gearspace`
- For the curve: `<mic> frequency response chart` (manufacturer first).

Query the *specific* pairing, then widen: "SM57 guitar cab EQ" before "dynamic mic guitar cab EQ".
Run 2–3 phrasings — engineers describe the same move a dozen ways ("scoop the mud", "cut 400",
"pull the boxiness").

When a fetched page comes back as a JS shell or login wall, don't fight it — note the thread title
and move on, or surface the link to Brian. Never try to scrape around a block.

## What to extract

For each useful source, capture:

- **The move:** band, direction, amount, Q if given (e.g. "−4 dB @ 400 Hz, narrowish").
- **The reasoning:** *why* — "boxiness from the cab", "proximity buildup", "cuts feedback".
- **The context:** room (live club vs. studio), PA, playing style, genre. This is what tells you
  whether the setting transfers to Brian's room.
- **The weight:** one person's preference, or several engineers converging?

## How much to trust it (weighting)

| Signal | Weight |
|---|---|
| Brian's own console-verified past show, same source + room (wiki show page / verified build) | Highest — his ground truth |
| Several named LAB engineers converging on the same move | High |
| One detailed post with clear reasoning from a known name | Medium-high |
| Manufacturer curve (for shape, not settings) | High for shape only |
| One-line "I always cut 400 on a 57" with no why | Low |
| Studio-context advice applied to a live/outdoor source | Low — flag the mismatch |
| No author, no reasoning, listicle | Ignore |

A forum setting from a dead studio room does **not** transfer cleanly to Memo's 1.6 s RT60 or an
open-air FSQ stage. When the context is studio and Brian's job is live (or vice versa), that's a
reason to lean on the KB and, if they diverge, to stop and ask.

## Reconciling with the KB

After the web pass, compare to `mic-library.md` + `eq-starting-points.md` (Step 3b/3c in
`decision-flow.md`).

- **Agree** → sourced baseline, proceed.
- **KB silent, strong web consensus** → use it, label it web-sourced, offer to write it back.
- **Disagree / both thin** → **STOP and ask.** Show both sides with sources.

## Writing findings back to the KB (optional, on Brian's OK)

Brian's KB is self-improving. When research turns up something worth keeping — a new mic's character,
a confirmed mic-on-source setting, a genre note — offer to add it. Don't write silently. Log the
finalized decision to `Live Sound KB/_learning/eq-advisor-log.md` first (see *Self-improvement loop*
in SKILL.md), then propose the durable ones for the KB.

- New mic → propose a row for the Mic Character table in `mic-library.md`.
- Confirmed setting/approach → propose an addition to `eq-starting-points.md`.
- Mark the addition's `Sources:` with the forum thread URL(s) and the date.
- Publishing to the live wiki is the **wiki-publish** skill's job — hand off to it, don't reinvent
  the push.

## Citing sources in the output

Every recommendation lists its sources: forum thread titles + URLs and the KB articles used. In the
PDF, these go in the Sources block. Inline, end with a `Sources:` line of markdown links. This is how
Brian audits a number later and how the next session knows where a value came from.
