# NEW SHOW — start here

*The map for a show conversation. Pair with `ROUTING.md`.*
*Last updated: 2026-07-09 — slimmed to a router; the pipeline mechanics live in ONE place now,
the **show-deep-build** skill (which absorbed eq-advisor the same day). This file routes and
holds the don't-forgets; it no longer duplicates the skill's flow.*

---

A new show = a new conversation. Brian opens with the venue and show. From there:

**Deep Think is the default (standing rule, 2026-07-01).** Submitting a new show — channel list,
input list, artist + venue, ShowBuilder brief — means the full deep-research build runs. Brian
never says "deep think"; there is no KB-only fast path.

## 1. Route
Read the venue row in `ROUTING.md`: folder, console(s), base session, patcher, PA, and exactly
which KB articles to load. Pull **only** those.

## 2. Confirm the basics (don't assume) + intake
Show date, show name, input list source, monitors (wedges vs IEM), TOUR gear, anything the venue
row marks "confirm at first show." Ask for the tech rider / stage plot — the densest research
input there is. One round of questions up front beats a wrong rebuild.

**Intake (2026-07-19):** whatever Brian drops — rider/stage-plot PDFs, xlsx/CSV lists, photos or
screenshots of a list or email — gets read in full and normalized into the brief facts BEFORE
research (show-deep-build Step 0). Plot/rider file into the show folder as
`<Show> - Stage Plot.pdf` / `<Show> - Rider.pdf`; artifact conflicts go to the question round.

## 3. Scaffold
`python3 _system/scaffold_show.py --venue <v> --date YYYY-MM-DD --name "Show Name"` — dated
folder, venue patcher copy (Memo/FSQ), FOH Channel Processing stub, and `show.status.json` (the
per-show state file; packet + .ses builds stamp it automatically, the wiki push stamps
`published` — `verified` is optional, stamped only if Brian volunteers a desk load). All show
files live there.

## 4. Run the pipeline — the show-deep-build skill
Everything from here is the **show-deep-build** skill, end to end: artist + genre research
(fresh every show), per-channel EQ in the locked order **instrument → mic → genre → venue**
(Part II of the skill — the former eq-advisor), the mic-locker loop, the single batched question
round, the `spec.json` → `build_packet.py` packet (md / xlsx / Show Packet PDF / EQ Rationale
PDF / MASTER PDF), the `.ses` via the venue patcher, the handover (publish on Brian's go — no
console-verify gate, 2026-07-19), and the harvest.
Don't re-derive any of it here — trigger the skill.

Stage 2 (`.ses`) is Q225 venues only (Memo, FSQ); M32/Wing venues are manual. A rebuild-only
`.ses` run from existing paperwork is the **send-it** skill; publishing a show is
**show-wiki-push** (FSQ + Memo; `fsq-wiki-push` is its alias — other venues → **wiki-publish**),
gated only by Brian's explicit go — console verification is never required (2026-07-19).

## 5. Close out + harvest
The skill's step 7 covers it (KB harvest, eq-advisor log, active-projects + CHANGELOG,
IMPROVEMENTS/QUESTIONS, wiki push on Brian's go). When Brian says an output came out well,
that's the trigger to harvest it into the KB so the next conversation inherits it.

---

## Don't-forget rules

The hard rules are numbered in `_system/RULES.md` — read it, don't rely on memory. This file no longer restates them (2026-09-14). The ones that bite most often: R9 vocals cuts-only · R12 outdoor cuts deeper · R23 the KB is for longevity, not research · R32 locker fork · R33 wireless faders · R34 FSQ ch 10 reserved · R39 one question at a time · R42 console verification is not a gate.
