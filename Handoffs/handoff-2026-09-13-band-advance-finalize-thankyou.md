# Context Handoff — 2026-09-13
**Session topic:** Band Advance system — a real live-send incident, a new "Finalized" status + sign-off workflow, headliner-in-filename, a large-vehicle-count question, and a bilingual thank-you email
**System:** Code/BandInfoForm/, branch `advance-system`, n8n VM (192.168.200.84), advance.tinydoorstudios.com

---

## What We Did

Very long session, 11 commits (`7a1ccab` through `9753cfa`), all deployed to the live VM:

1. **Manual band entry.** A "Manual Band Advance" option (checkbox on `/booking`, then promoted to its own permanent card on `/staff`) for a band that emailed its info directly instead of using the form — logs the booking, skips the automated welcome email for that show specifically, gives a direct pre-filled link to the band's own form to fill in by hand.
2. **Real incident, found and fixed same session:** three real bands (Dixie Karas, Queen City Cabaret, Jordan Pollard Trio — all 3+ weeks out) got their welcome email sent early. Root cause: `shows_due_for_initial_advance` had no date-out ceiling — a leftover from the pre-live-send-migration design — so any single urgent booking's on-demand trigger swept up and sent the welcome for every show still queued, not just the one that justified the trigger. Fixed by restoring a `show_date <= CURRENT_DATE + 21` ceiling directly on the send gate.
3. **Dashboard label fixes.** "Awaiting Window" / "Ready to Send" both used to mean "a draft is waiting" — stale since the live-send migration, now both read "Sent — Awaiting Reply". Also fixed truncated band names on the dashboard (the Mark Finalized button was squeezing names to a few characters — band name now gets its own line).
4. **New "Finalized" status + sign-off workflow** — the big feature, built via a full plan-mode pass. Once a band responds, a show now reads "Advancing In Progress" (renamed from "Advanced"/"Completed" — two surfaces disagreed on wording before) until a human clicks **Mark Finalized** (on `/artist/<id>` or right on the live `/dashboard`), at which point it's "Finalized" everywhere — dashboard, artist page, Excel Show Status Log, daily digest. Along the way, fixed a dormant bug: the artist page's Status column had been silently blank since 2026-09-09 (reading a dropped column).
5. **Headliner in filenames.** Reversed a 2026-09-11 decision that deliberately kept band names out of filed advance-doc filenames (to avoid drift when a bill's lineup changes). Filenames now read `<date> <event/series> - <headliner> Prod Adv.docx`. A real-data dry run against all 23 active events caught a duplication bug (some events already have the headliner typed into the Event Name field) before it shipped.
6. **Large-vehicle question changed from Yes/No to a count.** "How many of those need large vehicle parking?" — a bill's vehicles aren't all-or-nothing (1 large + 1 standard is real). New `vehicle_count` + `large_vehicle_count` columns; the old boolean stays on historical submissions only.
7. **Thank-you-on-finalize email — built, killed, then rebuilt for real.** Drafted sample copy against a real band (Wishy) as an actual Outlook draft (never sent), corrected twice (removed Brian's personal contact info, fixed a stale monitor count), then Brian decided against sending any thank-you email at all and that was locked into the code as permanent. He then reversed that later the same session: **all thank-you emails are back on, for every show finalized from now forward** (not retroactive to the 7 already finalized today), bilingual for Salsa On The Square. Built for real this time — reads the filed Word doc (not the database) so a same-day hand-edit reaches the band, fails closed if the doc/band-column can't be resolved, reuses `daysheet.read_filed_advance`/`find_schedule_table` rather than re-parsing from scratch. Verified against multiple real shows (Wishy, RatBoys, Al West Jr., Zumba Latin Band/Salsa bilingual) via read-only dry runs — no sends. Deployed.

---

## Current State

- **Done:** all 7 items above, all deployed, all committed and pushed to `advance-system`.
- **In progress:** nothing.
- **Up next / waiting on Brian:** the thank-you email has never actually fired for real. Brian was asked which real upcoming show to use for one live end-to-end test and said **"none"** — meaning no dedicated test. The feature is live as-is: the *next real show Brian finalizes* will trigger an actual send, with no dry run first.

---

## Key Decisions (Locked)

- **Manual-entry bookings permanently skip the automated welcome email** for that specific show (matched on venue+date+artist name via the `bookings` table) — not a one-time toggle.
- **21-day ceiling on the initial-advance send gate is permanent**, not a one-off patch — a show only ever gets its welcome sent once it's genuinely inside 21 days of its date, regardless of what else triggers a lifecycle run.
- **"Finalized" is a real, permanent third phase** after "responded" — a human must explicitly click Mark Finalized; nothing auto-finalizes.
- **Thank-you-on-finalize emails are ON, for every show, from now forward** (Brian's final word this session, reversing an earlier same-day "never" decision) — bilingual (English then Spanish, same message) only for Salsa On The Square.
- **The thank-you recap/schedule reads from the filed Word doc, not the database** — deliberate, so a same-day hand-edit Brian makes directly in Word reaches the band. Fails closed (skips + logs, never guesses) if the doc or the band's column in it can't be resolved.
- **Advance-doc filenames now include the headliner** — accepted tradeoff: the filename can change (old one left on disk, not deleted) if the headliner changes before the show.
- **Large vehicle parking is a count, not yes/no**, going forward — old boolean data stays readable but nothing new writes it.

---

## Open Items

- **The thank-you email has never sent for real.** Everything is verified via read-only testing against real filed docs, but the first real send will happen whenever Brian next clicks Mark Finalized on an actual show — watch for it / be ready to check the actual received content, not just that it didn't error, the first time it fires.
- **Not addressed, offered but no decision yet:** `run_now.py`/`package_run.py` still rebuilds and re-files *every* currently active event's advance doc on *every* pipeline run (not just the one that changed) — this is what caused every filed doc to get touched at 5:06pm during today's incident investigation. A targeted fix (matching what `regen_show.py` already does for the `/submit` path) was proposed but Brian hasn't said whether he wants it done.
- **Two loose ends from the 5:06pm mass-regeneration investigation and the stray-Outlook-drafts issue:** the `internal-delete-outlook-drafts` n8n workflow intermittently reported "no item to return" when a real draft should have existed (worked correctly on the last two attempts) — never root-caused, low stakes since it's just a demo-mailbox cleanup path, not part of any real send.

---

## Files Delivered This Session

None as standalone deliverables — all work was code changes to the live Band Advance system (Code/BandInfoForm/), deployed directly. One sample email was created as a real (never-sent) Outlook draft in Production@3cdc.org's Drafts folder against Wishy, then deleted once wording was locked in.

---

## Corrections / Watch-Outs

- **The live-send incident today was real:** don't assume "no date-out ceiling" is safe anywhere in this pipeline just because drafting used to be harmless — since the live-send migration, the same query gap means a real, immediate send to real bands. Always check for a ceiling on any query that decides what gets sent.
- **The dashboard/Excel/digest label surfaces drift independently** — "Advanced" vs "Completed" already meant the same thing with different words before this session (caught and fixed). Any future status-model change needs a pass across all of: `app.py` `DASHBOARD_STATE_LABELS`, `dashboard.html`, `status_log.py`, `daily_digest.py`, `merge_status.py`, `status_sheet.py` — not just the one page someone happens to be looking at.
- **`status_sheet.py` had a real regression risk caught before shipping:** three places checked `state == "responded"` by exact equality; once "finalized" became a distinct later state, those would have silently un-checked "Completed" / re-shown a stale follow-up date. Fixed to `state in ("responded", "finalized")`. Watch for the same pattern if the state model ever grows again.
- **Filename-changing code (headliner-in-filename) needed a real-data dry run to catch a duplication bug** — several events already have the headliner hand-typed into the Event Name field, which would have doubled up ("Blues & Brews - Ricky Nye - Ricky Nye") without the substring-check fix. Never trust a naming-logic change without testing it against every real active event first.
- **The Nyquist Dropbox boundary rule was updated this session:** Brian has now explicitly authorized reading into any Dropbox folder starting with "3CDC" + venue name (previously off-limits, "even when relevant"). Still never touch other unrelated personal Dropbox folders.

---

## Resume Prompt

> Picking up from the 2026-09-13 session on the Band Advance system (`Code/BandInfoForm/`, branch `advance-system`). That session found and fixed a real live-send incident (three bands got their welcome email weeks early — root cause was a missing date ceiling on the send gate, now fixed permanently), then built a full "Finalized" sign-off status (Mark Finalized button on the artist page and the live dashboard, consistent labeling across every status surface), changed advance-doc filenames to include the headliner, changed the large-vehicle question from yes/no to a count, and built a bilingual (English/Spanish for Salsa On The Square) thank-you-on-finalize email that reads its recap from the filed Word doc rather than the database. Eleven commits, all deployed and pushed to `advance-system`.
>
> The very last thing in that session: the thank-you email has been wired and deployed but has never actually fired for real — Brian was asked which real show to use for a live test and said "none," meaning the first real send will just happen naturally the next time he finalizes an actual show. If he mentions anything about a thank-you email going out (or not going out, or looking wrong), that's the first real-world test of this feature — check the actual delivered content, not just that nothing errored, the same way earlier incidents this session were only caught by reading real data back rather than trusting an HTTP response.
>
> Also open, no decision yet: whether to fix `run_now.py`/`package_run.py` so a new booking only re-files its own event instead of rebuilding every currently active event's advance doc on every run (this is what caused every filed doc to get touched at once during the incident investigation).
