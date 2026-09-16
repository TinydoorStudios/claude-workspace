# memory.md
*Last consolidation: 2026-09-16 — log in memory-archive-2026H2.md*

*Living document — newest entries at the top of Session Notes. Never delete — archive instead.*
*SIZE RULE: this file loads in full at every session start. Session Notes keep a trailing ~2 weeks and the file stays under 18KB; older notes roll into `memory-archive-YYYYHn.md`. Consolidation passes log to the archive, never here. (Updated 2026-09-14, previously: ~30KB / current calendar month — tightened 2026-08-25.)*

---

## How This File Works

This file is the persistent memory system for Brian Lloyd's sessions. It tracks:
- Active projects and their current state
- Decisions made and why
- Unresolved issues and open questions
- Things to remember for next time

**Rules for updating:**
- Append new entries under the relevant project or create a new section if it's a new topic.
- If updating an existing entry, edit in place and update the date.
- Mark completed items `[DONE]` and resolved issues `[RESOLVED]`.
- Never rewrite history — if something changed, add a note below the original entry.

---

## Active Projects

Canonical project state (active shows, tools & infrastructure, open issues, completed shows) lives in the KB: `Live Sound KB/Wiki/active-projects.md`. This section used to duplicate it verbatim (both frozen at "Last updated May 16, 2026" since the original entry) — trimmed to this pointer 2026-07-08 to stop the drift. SPL Monitor's project-state summary (features, next steps) was also moved there the same day; its build history stays below in Session Notes, which is where it belongs.

---

## Open Issues

*(none)*

---

## Resolved / Done

Archived 2026-08-11 to `memory-archive-2026H2.md` — everything in it was May 2026, dismissed or shipped.

---

## Seventh Heaven Pro

Reference notes moved to the KB 2026-08-11 — canonical source is `Live Sound KB/Wiki/reverb-reference-memo.md` (Early/Late behavior, the Memo preset list, VLF rule). The old copy here is in `memory-archive-2026H2.md`.

---

## Session Notes

*Newest first. Older entries live in `memory-archive-2026H2.md`.*

### 2026-09-15 — Band advance: sheet write-back, "I sent it", and the 0-byte docs explained
Built the durable fix for the bug found rebuilding the advance docs: a booking edited in the app now reaches advance-list.xlsx. `update_booking` flags the row `sheet_dirty` whenever a SHEET_OWNED_FIELD changes, `run_now` syncs those rows (seed_bookings --edited -> append_bookings --edited -> --synced) BEFORE the rebuild that reads the sheet, and a booking whose artist/venue/date was itself the edit is found by the identity its row was written under (`_old_ident`, from the newest booking_edits row) so a rename moves the existing row instead of stranding it. Deliberately a dirty FLAG, not a blanket reconcile: only a row somebody actually edited is pushed, so a value Brian typed straight into the sheet on an untouched booking is never overwritten. Only booking-owned columns are written — never the band-detail ones. Tested end to end on Dixie Karas (10/26, outside the notify window so no band email), edited and reverted, test edit records cleaned up.

Second gap, found by Brian's own draft-branch test: holding a welcome as a draft left NO way to tell the system a human had sent it. Clearing the checkbox means "go ahead and send", which would have put a second copy in front of Joe Jordan; meanwhile the show sat in `queued` and its 7/3/2/1-day reminders stayed shut because nothing knew the band had been written to. Added "Advance drafted — I sent it ✓" on the artist page (`POST /show/<id>/advance-sent` -> mark_advance_sent_by_hand): stamps the show advanced, sends nothing, restarts the ladder. `artist_shows` joins advance_held_draft_at from `shows` rather than adding it to the advance_status view, which a migration recreates wholesale. Answered his status question: a held show goes queued -> responded on its own the moment the band submits (the view checks for a submission), but never passes through the middle states and gets no reminders until this button is clicked.

Also: the "info changed" email now lists fields down the clock (it read Curfew before Load-in), and the rewritten dropbox-guard judges each pipeline SEGMENT separately — it was blocking commands whose `rm` targeted /tmp just because a Dropbox path appeared elsewhere in the same command, including its own test harness and session notes. 17-case matrix passes.

Closed out the same session (22:10, from session 2026-09-15): Brian said "mark Joe Jordan as sent" and the new button was driven through the live UI rather than the database — show moved `queued` -> `ready_to_send`, hold cleared, all four reminder tiers (7/3/2/1 days before 9/25) reopened, and the DB confirmed zero sends in the surrounding ten minutes. The draft-hold -> hand-send -> one-click-reconcile path is now proven end to end on a real show. This also answers the open suggestion left by the 2026-09-15 Amador Sisters note ("worth a real 'send now' button rather than a hand-run script") — the same button covers it.

The Moon Festival / Ricky Nye "0-byte" docs are Dropbox ONLINE-ONLY PLACEHOLDERS on the Mac (xattr com.dropbox.placeholder), not damage: 16 of the 27 advance docs in those two month folders are in that state, the VM holds full local copies, and opening one in Word hydrates it. Reading via `head` did not hydrate them. Worth remembering for any MAC-side script that opens a filed doc — the VM is the safe place to read them.

### 2026-09-15 (night) — Band Advance: Rob Keenan's FSQ 9/23 paperwork regenerated
Brian thought he'd deleted the advance paperwork for "Robert Keenan" at FSQ 9/23 and couldn't find it in Dropbox. Two things: the artist is on file as **Rob Keenan**, not Robert — which is most likely why a Dropbox search came up empty — and the docs really were gone. The booking itself was intact (event 29, show 1719, completed submission), so the doc was regenerated on the VM through the same pipeline the live system uses, pulling his actual form answers rather than a blank template. Back in `3CDC Fountain Square/09.2026 FSQ/` as `092326 Southern Sessions - Rob Keenan Prod Adv.docx`, along with `092326 Know Rulz Stageplot.jpeg` (the opener on that Southern Sessions bill, whose stage plot had gone missing too). No Rob Keenan stage plot came back — open question whether he ever submitted one or that's a separate loss. Independently confirmed the same day's placeholder finding: the regenerated files read 0 bytes on the Mac because Dropbox holds them online-only, not because anything failed. *(from session 2026-09-15)*

### 2026-09-15 — Band advance: all 23 upcoming advance docs rebuilt on the Artist 1/2/3 layout
Brian noticed every already-filed advance still read OPENER/DIR SUPPORT/HEADLINER. Relabelling them was not enough: under the old rules a single artist sat in COLUMN 3 and the day's times sat in the "Headliner" schedule rows, so getting to Artist 1/2/3 moves data between columns and rows. Each doc was re-rendered from the database instead. Before touching anything, audited all of them for hand edits a re-render would destroy — found 11 real ones typed into Word that the DB never had ("Band brings all mics", "they will use our wireless... have a lot of XLR ready", "5 wedge mixes, 1 iem", "1 - USE OURS", the Toad Productions playback note) — and carried each one back into its new cell, matched by artist + row label so the column move couldn't misplace them. 23 docs rewritten, 11 values carried, verified 0 lost and no slot wording left anywhere. Originals tarred to /opt/band-advance/data/doc_backups/ on the VM first.

REAL BUG found doing it, worth fixing properly: **a booking edited in the app never reaches advance-list.xlsx.** seed_bookings/append_bookings only APPEND new bookings; import_sheet then rebuilds event_acts from the sheet, so an edit silently loses to the stale sheet row on the next pipeline run. Bit twice tonight — Brian's own Cincy Steel correction (9/20) and Rob Keenan (9/23) were both reverted to pre-edit times by the 21:37 run his own draft-branch test kicked off, and my first doc rewrite printed those stale times. This used to be a cosmetic staleness; it is not any more, because the sheet's Start column now also decides who is Artist 1 (Rob Keenan should be Artist 2 at 6:30pm but tied at 5:00pm and took Artist 1). Fixed both rows in the sheet by hand, re-imported, re-rendered; every act now matches its booking. The durable fix — writing a booking edit back into the sheet row — is NOT built yet.

Two smaller things: my own new same-set-start clash notice fired correctly on that run (Know Rulz/Rob Keenan, and Bravo/Taymar Israel on the 9/11 WP bill). And two advance docs read 0 bytes on Brian's Mac while being intact on the VM — a Mac-side Dropbox materialisation issue, not data loss.

### 2026-09-15 — Band advance: Artist 1/2/3 deployed; Dropbox guard rewritten
Deployed the Artist 1/2/3 change (commits f28ac7a / 92b2b2c / 881d57d) — service restarted clean, healthz db+form ok, the 2026-09-15-artist-order migration applied and backfilled every act's own set_start/set_end/load_in/soundcheck (FSQ 9/18 verified: Phanta 7:00, Wishy 8:00, RatBoys 9:00). Live form confirmed serving "Drum riser (if available)" plus the hint line. Brian asked explicitly for NO band emails out of this — verified before deploying and after: the deploy script only copies code, runs migrations, reloads systemd and restarts the service; nothing in it sends; run_now/package_run only write draft .md files (draft_emails never sends); the app runs no startup job; and the lifecycle-watchdog timer is Persistent=false, so enabling it can't back-fire a missed run. Zero sends in the hour around the deploy, confirmed against the DB. One PRE-EXISTING queued "info changed" notice (Cincy Steel, FSQ 9/20 — Brian's own 2:55pm schedule edit: load-in 4:00->5:00p, soundcheck 4:30->5:30p, start 5:00->6:00p, end 7:00->8:00p) is still unsent and WILL go out on the next 9am lifecycle run; flagged for his call, unrelated to the paperwork change.

Follow-up same session: Cincy Steel (FSQ 9/20) corrected — Brian confirmed the real day is 6-8pm, 5:00pm load-in, 5:30 sound check, and curfew moved 8:00pm -> 9:00pm (the edit had left the set ending exactly at curfew). Also normalized the four times back to house notation ("5:00p" -> "5:00pm") so the band's email doesn't mix formats, and set length back to "120". Applied through advance_db.update_booking, not raw SQL, so it MERGED into the notice already pending — still one email, not two. Shipped a real fix first: a field edited back to its original value was kept in the merged diff, so "Set length: 120 -> 120 min" was queued to go to the band as news; no-ops are pruned now and an emptied notice is deleted. Known cosmetic wart left alone: build_email lists changed fields in dict order, so the band's email reads Curfew / Load-in / End / Sound check / Start rather than in time order.

Second thing, same session: Brian lifted the Dropbox boundary in his own words ("adjust the hook so you can access things outside of just the Nyquist folder"). Rewrote the guard hook — no location restriction at all now; it blocks only DESTRUCTIVE Bash aimed at a real Dropbox PATH (recursive/forced remove, rmdir, shred, find -delete, find -exec rm, rsync --delete, moving a Dropbox path, a shell redirect onto one) and never blocks Read/Edit/Write. Prose that merely mentions the word passes, which took a second pass to get right: the first cut gated on the bare word and blocked its own session note. 13-case test matrix passes, kept at scratchpad/test_hook.py. Two things learned worth keeping: the OLD hook's allowlist was broken anyway — a folder name written in quotes put a quote character where the regex expected a letter, so "3CDC Fountain Square" was refused despite being explicitly allowlisted — and the old memory claim that the hook can't be edited from inside a session is simply false; it trips on its own source text, so write the file without literal Dropbox paths in it and the edit lands.

### 2026-09-15 — Band advance: Artist 1/2/3 replaces the opener/support/headliner slots
Brian's call, a core change to the advance model: no booking ever declares a slot again. Position on a bill is DERIVED from set start (earliest = Artist 1, latest = Artist 3) and never stored, so an artist booked later with an earlier start renumbers the bill by itself — his stated worry ("copy everything from the first band and move it to band two") turns into nothing happening at all, because there's nothing to move. Word "artist" not "band" — his correction mid-session, since plenty are solo acts. Booking form lost Slot and Bands on the Bill; the bill counts itself. Drum riser now asked of every artist worded "(if available)" with a hint line that the riser is set once for the night (he picked that over a bare relabel or a full reframe) — it used to be hidden from everyone but the FSQ headliner, so the earlier acts' preference existed nowhere until load-in. Relabeled the Word template AND the 513 Airwaves locked crew schedule in Dropbox; schedule rows stay in load-in order (Artist 3 loads in first), which he approved explicitly. Two real bugs fell out: per-act load-in/soundcheck/start/end were collapsed onto the event as "first non-empty across the bill", so FSQ 9/18 printed Headliner Load-In 7:00pm and End 8:45pm for a band playing 9-10 (they were the SECOND act's times); and a slot clash used to silently DROP the second band from the advance doc, where a same-set-start tie now keeps both and reports it. ~25 files, commits f28ac7a + 92b2b2c. Rendered the 9/18 FSQ doc through the real pipeline with the live data as proof. NOT DEPLOYED — the deploy (which also applies the migration) was blocked by the auto-mode classifier as a production action and is waiting on Brian.

### 2026-09-15 — Band advance: merged Neo-Soul spelling variants (WP)
Brian noticed WP's structure had two spellings of the same series. Confirmed real split: "Neo Soul Nights" (the one already canonical in `forms_config.SERIES_LOCATION`, binding it to the Bandstand/monitor-cap 4 config) vs a rogue "Neo-Soul Fridays" from a free-typed staff booking — same real bill, 9/11/26 WP, 4 acts total split across both spellings (Taymar Israel + Bravo under the correct spelling, Special Request Band + DJ Bravo under the wrong one). The wrong spelling meant those 2 bookings silently fell out of the Bandstand stage-location mapping. Merged all "Neo-Soul Fridays" -> "Neo Soul Nights" across bookings.series, events.series, shows.show_series (2/1/2 rows) — real UPDATE, confirmed before/after, one spelling only now. Didn't touch whether the 4 acts are correctly organized on one bill vs duplicated — that's a separate question Brian didn't ask about, flagged nowhere else needed. Ties into the already-logged "series-name governance" TODO (free-typed series field, no dropdown/validation yet).

### 2026-09-15 — Band advance: FSQ parking catch-up draft revised (3rd-party + Salsa excluded)
Brian reviewed the first catch-up draft, asked to delete it and rebuild excluding all 3rd Party events and anything under Salsa On The Square. Built and activated a real general-purpose tool for this: `internal_outlook_drafts_admin.json` (already committed, inactive) — op:list / op:delete-by-id against Production@3cdc.org's Drafts folder, token-protected same as everything else — activated + deployed (commit 998adff). Listed drafts, matched the exact one by subject + Mtully@3cdc.org recipient (only one match), deleted it (Graph 204, confirmed gone from a re-list). Rebuilt the catch-up query adding `show_series <> '3rd party'` and `show_series NOT LIKE '%salsa%'` — count dropped 12 -> 8, correctly dropping Dance Flash Fusion / Spreading the Love Through Dance / Moon Festival 2026 (all 3rd Party) and Zumba Latin Band (Salsa On The Square); the other 8 real bands unchanged. New draft created for real (Graph id confirmed), n8n execution history confirms only the admin list/delete calls and the one draft-create fired — nothing sent. Sitting in Production@3cdc.org for Brian to review and send.

### 2026-09-15 — Band advance: one-time FSQ parking catch-up draft to Mtully
Brian's final ask: a single one-off draft (never sent by me, "I will inspect it and send it") summarizing every FSQ band that has already advanced for a show 9/16/2026 onward — a backfill so Mtully isn't starting blind when the new daily digest (built same session) takes over tomorrow. Real bug caught before running it: `internal_create_outlook_draft.json` always sent contentType 'Text' — no HTML support at all, unlike the sibling send-outlook workflow — so an HTML table would have rendered as literal tags. Fixed to match send-outlook's exact convention (an `html` field -> HTML content type; `body` stays Text, so the existing 'Email band' caller is untouched) — commit 45bcd77, deployed, active. One-off script (not committed, run once from the VM and deleted) queried shows/artists/submissions directly rather than the new queue table (which only holds items created after today's digest deploy — real historical FSQ submissions never passed through it). Pulled 12 real bands, 9/16 through 10/1, excluding cancelled shows; 5 had no vehicle_count on file (mostly staff/third-party bookings) and show "not provided" rather than a misleading 0. Draft created for real via Graph (confirmed in n8n execution history: only Internal Create Draft fired, nothing sent) — sitting in Production@3cdc.org for Brian's review.
