# ROUTING — the venue brain

*The control map for every show conversation. Read this + `NEW-SHOW.md` at the start of any show.*
*Last updated: 2026-07-19 (show.status.json in global rules; the venue table's patcher footnote was already current — the header date had just never been bumped since 2026-05-30)*

---

## How to use this file

A show conversation starts with Brian naming a venue (shorthand is fine: Memo, FSQ, WP, ESP, CSP, ZP, IA, Greaves). Look the venue up in the table below to get: the folder to work in, the console(s), the base session file, the patcher, the PA, and **exactly which KB articles to load**. Pull only those articles — do not read the whole KB at startup.

Knowledge lives in one place: `Live Sound KB/Wiki/`. This file routes; the KB holds the facts. If a fact here ever disagrees with the KB, the KB wins and this file gets fixed.

---

## Venue routing table

| Say | Venue | Folder | FOH console | Monitors | Base .ses | Patcher | PA | Tempest | KB specs to load |
|---|---|---|---|---|---|---|---|---|---|
| Memo | Memorial Hall | `Memorial Hall/` | DiGiCo Q225 (house) | per show (IEM/wedges) | `_TEMPLATE/brian memo june 2026.ses` | `apply_show_TEMPLATE.py` * | house | — (indoor) | venue-memorial-hall, console-digico-q225, eq-starting-points, reverb-reference-memo, mic-library |
| FSQ | Fountain Square | `Fountain Square/` | DiGiCo Q225 | Midas M32 | `_TEMPLATE/brian fsq start.ses` | `apply_show_TEMPLATE_FSQ.py` | L-Acoustics A15 / KS21 (X12 fills) | #215217 | venue-fountain-square, console-digico-q225, console-midas-m32, eq-starting-points, input-list-design-spec |
| WP | Washington Park | `Washington Park/` | Midas M32 | M32 | — (no Q225 pipeline) | — (M32: Stage 2 manual) | JBL SRX915 / SRX906 / SRX928 | none | venue-washington-park, console-midas-m32, eq-starting-points |
| ESP | Elm Street Plaza | `Elm Street Plaza/` | confirm at first show | confirm | — | — | confirm at first show | #211956 | venue-elm-street-plaza |
| CSP | Court Street Plaza | `Court Street Plaza/` (create at first show) | confirm | confirm | — | — | confirm | none | venue-court-street-plaza |
| ZP | Zeigler Park | `Zeigler Park/` (create at first show) | confirm | confirm | — | — | confirm | #216868 | venue-zeigler-park |
| IA | Imagination Alley | `Imagination Alley/` (create at first show) | confirm | confirm | — | — | confirm | none | venue-imagination-alley |
| Greaves | Greaves Concert Hall (NKU) | `Greaves Concert Hall/` (create at first show) | Behringer Wing | per show | — | — | house (637-seat, 2× 9ft grands) | — (indoor) | venue-greaves-concert-hall, console-behringer-wing, eq-starting-points (classical), reverb-reference-memo |

\* Memo patcher lives in `Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py` — rebuilt 2026-07-01 on the FSQ engine for the new 37.6 MB console-save template in `Memorial Hall/_TEMPLATE/` (old `brian memo v2.ses` + strip-layout engine retired; archive copy `apply_show_TEMPLATE_v2_OLD_stripformat.py`). FSQ patcher: `Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py`. Both patchers carry offset tripwires and abort on a stale/wrong template. (The old duplicate copies under `Memo Work/` were archived 2026-05-30.)

**"confirm at first show"** means exactly that — the spec isn't established yet. Ask Brian, then write the answer back into the venue's KB article and promote it from emerging to established. Never invent PA, console, or power specs for the emerging venues.

---

## Console → venue quick reference

- **DiGiCo Q225** — Memorial Hall (house) and Fountain Square (FOH). Only these two have the `.ses` patcher pipeline (Stage 2).
- **Midas M32** — Washington Park (FOH), Fountain Square (monitors), in rotation elsewhere.
- **Behringer Wing** — Greaves / secondary venues. ⚠ FX preset save/load broken since firmware v1.13 — `.efx` files won't load.
- **Yamaha CL3** — in rotation.

---

## Where things live

| What | Path |
|---|---|
| Knowledge (canonical) | `Live Sound KB/Wiki/` — start at `INDEX.md` |
| Project state (canonical) | `Live Sound KB/Wiki/active-projects.md` |
| Open questions for Brian | `Live Sound KB/Wiki/QUESTIONS.md` |
| KB change log | `Live Sound KB/CHANGELOG.md` |
| About Brian / writing rules / session history | `about-me/` |
| Routing + new-show flow + improvement log | `_system/` |
| Shared patchers / builders | `_shared/q225_ses_engine.py` (one .ses engine, both venues) + `_shared/md_lint.py` + `_shared/readback_verify.py`; venue calibration wrappers in `Memorial Hall/Q225 SES Patcher SOP/` and `Fountain Square/Q225 SES Patcher SOP/`; show scaffold `_system/scaffold_show.py`; `show-packet-builder-template.py` (root) |
| Venue SOPs (lighting, LED, training) | `SOP Stuff/<venue>/` |
| Automation (n8n) | `N8n/` |
| One-offs | `Other/` |

---

## Global rules (apply to every venue)

- **Show folder name:** `YYYY-MM-DD ShowName` inside the venue folder (date first so folders sort chronologically). Create the venue folder if it's a new venue.
- **Show state lives in `show.status.json`** (2026-07-19, `_shared/show_status.py`) — scaffolded / packet_built / ses_built / verified / published. The scaffold creates it, builds stamp it automatically, and later stages read it instead of guessing from folder recency. `verified` is optional/informational — publishing gates on Brian's explicit go, never on a console check (shows are one-offs). Pre-2026-07-19 shows don't have one; stamp retroactively when touching them.
- **Default deliverable: PDF.** Channel processing docs ship as `.md` + `.html` + PDF (PDF rendered from the HTML via weasyprint, not reportlab).
- **Pipeline is 2-stage:** Stage 1 = combined Show Document (patch · monitors · EQ · stage plot) → PDF + HTML. Stage 2 = Q225 `.ses` via the venue patcher (Q225 venues only). See KB `show-processing-pipeline`.
- **At packet completion:** generate the master reference PDF (input list summary, EQ decisions, patching, mic choices, stage plot reference, file index), update `active-projects.md` + `CHANGELOG.md`, and log anything learned to `_system/IMPROVEMENTS.md`.
- **EQ:** aggressive by default, whole-dB only, subtractive first — except classical (minimal), acoustic/folk (conservative, watch 1.5–2kHz piezo quack), Celtic (5ms+ attack, never gate sustained notes). Full tables in KB `eq-starting-points`.
- **Memo crowd-mic rig** is always patched for Memo shows (CH numbers left blank). OM1 / Deity S2 / CM4 — EQ in KB `eq-starting-points`.
- **Reverb:** always use real Seventh Heaven Pro / Liquidsonics preset names from the KB — never generic descriptions, never invented names.
- **Broadcast shows** use *underheads / underhat*, not overheads.
- **Ribbon mics** (R-121, R88): flag NO 48V in red, every time.

---

## Self-improvement loop

When a session teaches the system something — a new venue spec, a corrected fact, a workflow tweak, a recurring mistake — it gets written down so the next session inherits it:

1. **Facts** → the relevant KB article (and bump its `Last updated` + `CHANGELOG.md`).
2. **Structural / workflow changes** → `_system/IMPROVEMENTS.md`.
3. **Open items needing Brian** → KB `QUESTIONS.md`.
4. **Operational preferences / feedback** → Cowork auto-memory (auto-loads each session).

The `knowledge-base-health-check` skill can be scheduled to audit the KB for drift and stale articles between sessions.
