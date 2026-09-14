# Context Handoff — 2026-09-06
**Session topic:** Band Advance pipeline — dark mode, real-data backfill, Washington Park rollout (locations), and a new live Show Status Log
**Console / Venue:** N/A pipeline work; Fountain Square + Washington Park are the venues touched

---

## What We Did

Long session, several arcs, all on `Code/BandInfoForm/`, branch `advance-system`:

1. **Dark mode** — all six BandInfoForm pages (form/booking/thanks/artist/gate/search) flipped from light to the same dark palette every other TDS app uses. Caught a real bug doing it: `input[type=email]` was never in form.html's field selector, so it silently stayed white.
2. **Staff hub + browse** — `/staff` (New Booking vs Browse Advanced Bands), and `/search` grew a venue → series → band drill-down tree alongside the existing name search.
3. **Real-data backfill** — Brian handed over his Desktop "Data Dumb" folder, 34 real Aug 2026 FSQ day-sheet files (the old hand-built process). Hand-read every one (textutil; no pandoc/LibreOffice on this Mac) and ran 25 nights / 35 acts / 43 files through the actual submission pipeline (`record_submission`, `source="manual"`) — not a synthetic fixture.
4. **Workflow assessment** — walked the whole pipeline with Brian post-backfill. Confirmed the new system IS the live process (not running parallel to hand-built docs). Closed the Artist Directory wiki TODO (the `/staff` hub satisfies "one website, do everything"). Confirmed Memorial Hall is the next venue, scope agreed (same app, new venue, rider/hospitality/backline question set) — not started.
5. **WP template** — built `WP Single Band Advance.docx` by cloning the FSQ template's exact formatting and retargeting content, not rebuilding from scratch.
6. **WP locations (Main Stage/Porch/Bandstand)** — monitor caps (6/2/4, hard-enforced on `/submit`), Porch/Bandstand have no lighting (question hidden on the band form), `/booking` gets a conditional Location dropdown, and — after Brian pushed back on leaving it hand-filled — Location now **auto-fills** on the day-sheet via `daysheet.py::fill_location()`, wired all the way through `bookings.location` → the live sheet's new Location column → `events.details`. Included a real live-spreadsheet migration (openpyxl doesn't move merged-cell ranges on `insert_cols` — had to manually re-merge the STATUS block header after inserting the column).
7. **Show Status Log** — new `tools/status_log.py`, generates `~/Dropbox/Nyquist/Show Status Log.xlsx` from `advance_status` + a `bookings` join, called automatically from `run_now.py` after every booking/submission. Iterated through a demo (v1) against a real pull from Brian's team's actual Google Sheet ("Advancing Status," 2196 rows — pulled via the public CSV export URL, no auth needed) to find real gaps, then v2, then the real build: dropped SPL entirely (Brian's call), added "Booked By" (live, from `bookings.entered_by`). The core engineering is a preserve-on-regenerate merge — a hidden Show ID column means hand-typed manual cells (Owner, Advance Deadline, two completion checkboxes, Feedback Survey Sent?, Notes) survive every automatic regeneration instead of getting blanked.
8. **Entered By fix** — that field already existed but was the last item in a collapsed "More detail (optional)" section on `/booking`, so it was going unfilled. Moved it into the main required fields (client + server validated) since the Show Status Log's Booked By column depends on it.

---

## Current State

- **Done, deployed, verified live (real end-to-end tests, not just unit checks):** all seven items above. Show Status Log confirmed to auto-populate from a real test booking with zero manual intervention; manual-cell preservation confirmed by hand-typing then forcing a regen.
- **In progress:** nothing mid-build — this session's last task was writing this handoff + a full workflow doc for the wiki.
- **Up next:** not yet directed by Brian. See Open Items.

---

## Key Decisions (Locked)

- WP monitor caps are a **hard limit** on the band form (not just a note) — Main Stage 6, Porch 2, Bandstand 4.
- Location **auto-fills** on the WP day-sheet now — reversed from the original "hand-filled, staff call" design earlier in this same session once Brian said it was key.
- Blank templates live in **three places, always**: `~/Dropbox/Nyquist/Blank Advances/`, Desktop, and the repo's `tools/doc_templates/` — standing rule for every venue going forward (WP done, Memo next).
- Artist Directory wiki is **closed** — no second Wiki.js instance; the in-app `/staff` hub is "the one website."
- Show Status Log is a **separate file**, not a tab on `advance-list.xlsx` — that sheet stays the working/editing surface, this is a lighter read-mostly status board.
- SPL Reference / SPL Report Received are **out** of the Show Status Log — Brian's explicit call.

---

## Open Items

- **Outlook send step** — drafts still land in Gmail only.
- **Memorial Hall venue** — scope agreed (same app, rider/hospitality/backline question set), not built.
- **Other-venue email content** — `venue_email.py` is FSQ-only.
- **WP 2/3-band day-sheet templates** — don't exist; `daysheet.py` errors cleanly (not silently) on a WP event with 2+ acts.
- **Touring-bill paperwork gap** — Hospitality/Hotel/Runner rows the day-sheet templates don't have (confirmed via a real J. Roddy Walston tab in Brian's team's own sheet). Explicitly out of scope for the Show Status Log conversation; still a real gap in the *day-sheet templates* themselves, not resolved.
- **Post-show Feedback Survey emails** — a real intended pipeline stage (Brian's team has a whole tab for it) that's never been populated or built anywhere.
- **Artist name cleanup** — the Aug 7 Nationals backfill stored "J Rod" / "The Bright Light" (filename shorthand); real names are "J. Roddy Walston & The Business" / "The Bright Light Social Hour." Not corrected in advance-db.
- **Series-name governance** — still freeform-typed on `/booking`, no drift protection (flagged during the workflow assessment, not acted on).
- **Per-venue tech-pack URLs** — `forms_config.TECH_PACKS` still empty for every venue.

---

## Files Delivered This Session

| File | Format | Description |
|---|---|---|
| WP Single Band Advance.docx | docx | WP day-sheet template, matches FSQ formatting; later gained a Location row |
| Show Status Log — DEMO.xlsx | xlsx | v1 demo, real data, before the real-sheet gap comparison |
| Show Status Log — DEMO v2.xlsx | xlsx | v2, added Owner/Deadline/completion flags/SPL/Feedback Survey/Notes |
| Show Status Log.xlsx | xlsx | The real, live, auto-regenerating version — lives at `~/Dropbox/Nyquist/`, not sent as a one-off file |

---

## Corrections / Watch-Outs

- **`openpyxl`'s `insert_cols` moves cell values but not merged-cell ranges.** Inserting a column into the live `advance-list.xlsx` right before the auto-generated STATUS block left its header merge one column out of alignment — had to unmerge before inserting and re-merge one column over after. Tested on a scratch copy before touching the real file.
- **Postgres timestamptz text (`2026-09-03 21:33:00.89885+00`) breaks `datetime.fromisoformat()`** — the `+00` offset (no colon, no minutes) and 5-digit microseconds aren't valid ISO-8601 by Python's strict parser. Fix used throughout: just slice the first 10 characters for the date, don't parse.
- **A "view only" Google Sheet's data is readable without auth** via `https://docs.google.com/spreadsheets/d/<id>/export?format=csv&gid=<n>` — useful for pulling a real reference sheet's content without asking Brian to share edit access.
- **`javascript_tool`'s return-value serialization can mangle a very large string** (double-encoding/truncation) — when a `fetch().text()` result exceeds the tool's inline limit, it gets written to a result file; reading that back needs `json.JSONDecoder().raw_decode()` to salvage the real content past the tool's own trailing annotation text.
- **Backfilled "Buffalo Wabs" (8/12) and "Buffalo Wabs and the Price Hill Hustle" (8/28) are two separate artist records** — `match_key` normalization doesn't merge differently-worded names. Flagged to Brian, never merged.

---

## Resume Prompt

> Picking up on the **band advance pipeline** (`Code/BandInfoForm/`, branch `advance-system`). Last session: dark-moded the whole app, backfilled 34 real August show files into the live DB, rolled out Washington Park (three locations — Main Stage/Porch/Bandstand — with hard monitor caps and auto-filled day-sheet checkboxes), and built a new **Show Status Log** (`tools/status_log.py`) that auto-regenerates `~/Dropbox/Nyquist/Show Status Log.xlsx` after every booking or submission, with hand-typed columns (Owner, Advance Deadline, completion flags, Notes) preserved across regenerations via a hidden Show ID key.
>
> Read `band-advance-form.md` in memory before touching any of this — it's the deep, continuously-updated source of truth for this whole system, more detailed than this handoff.
>
> Nothing was directed as "next." Likely candidates if Brian doesn't name something: Memorial Hall venue build (scope already agreed — rider/hospitality/backline question set), the Outlook send step, WP 2/3-band templates, or the post-show Feedback Survey email pipeline (real gap, currently unbuilt anywhere). Also worth a look: the artist-name cleanup for the two Nationals-backfill bands, and whether series-name freeform drift has become a real problem yet.
