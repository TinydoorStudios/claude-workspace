# Band Advance QC audit: locked decisions (2026-09-13)

Audit was read-only (every file in Code/BandInfoForm + live VM state). Brian decided each item one at a time. **Status: ALL BUILT, staging-tested (70/70) and DEPLOYED LIVE 2026-09-13 ~22:30 (commits f5e21e2, 02a1a15).**

## Decisions

### 1. Filed advance docs are never overwritten
- A doc is created once per show. After that, only empty cells get filled. This applies every night, single or multi-band, whether the data comes from a band submission, a booking, or the sheet.
- "Empty" means the cell still matches the blank universal template exactly (e.g. "FOH – " with no name, or a checkbox group with nothing ticked).
- A booking run only touches its own show. A submit writes into the existing filed doc, never the template.
- A checksum is recorded at write time. If a doc changed since the pipeline wrote it, skip it and email Brian.
- A resubmission or booking/sheet edit that differs from a filled cell leaves the doc alone. Brian gets an email diff: show, band, field, what the doc says vs. what just came in.

### 2. Headliner filenames
- Before the next run, rename the 19 existing docs to the new headliner names once, content untouched.
- Later headliner changes rename the file in place (never a second copy).
- Doc lookup keys on venue+date, not filename sort order.

### 3. Failed sends
- Stamp only on a confirmed Graph 202.
- Anything else stays unsent, retries on the next run, and emails Brian the band + error.
- The n8n Send node must surface Graph errors.
- /booking requires a contact email unless "Manual band advance" is checked.
- Check the Graph client secret's expiry.

### 4. Cancel and typo fixes
- Cancel button on the artist page and dashboard stops all sends and doc writes.
- A show missing from the sheet/bookings is auto-held (no sends) and Brian gets an email: cancel or restore.
- Cancelled shows are never deleted. They stay everywhere in the staff hub marked CANCELLED: artist page, search/browse, Show Status Log, sheet, and the filed doc in Dropbox. The dashboard shows them greyed out until the date passes.
- A typo fix is a merge: Brian picks "typo for → corrected show". Send history, reminders, submissions and finalize state move to the corrected record, so the band gets no second welcome. The old record is removed.

### 5. Repeat sends
- Stamp each show immediately after its confirmed send.
- A database lock allows only one lifecycle run to send at a time.

### 6. Band-name mismatch
- If exactly one unresponded booking matches the venue+date, attach the submission now.
- Brian gets an email with both names and one-click Confirm / "Wrong band, detach".
- 0 or 2+ candidates: save it and email Brian to pick.
- Sign artist_id so it can't be tampered with.

### 7. Vehicle counts shown everywhere
- Advance doc Parking row, new Vehicle Count / Large Vehicle Count sheet columns, artist page, notify email, thank-you recap.

### 8. Stage plot carry-forward
- A returning band that doesn't upload gets its most recent plot carried forward and filed with the new doc.
- Notify email notes "carried from <date>".

### 9. Backups
- Nightly DB dump to both NAS boxes, keep 14. Email only on failure. The weekly full archive is unchanged.

### 10. dropbox_exclude.sh
- Remove the rm -rf step entirely. Update the header.

### 11. Delete-drafts-on-submit
- Retire it: remove the call from /submit and deactivate the n8n workflow (JSON stays in the repo).

### 12. Unresponded alert
- Include manual-entry shows with no form on file at 3 days out, labeled "MANUAL — staff never filled the form".

### 13. Gate
- 5 wrong tries per IP locks for 15 minutes and emails Brian.
- Keep BOTH passcodes (lockdown and 1313).
- Restrict the post-login redirect to this site's own pages.

### 14. Thank-you email
- Skip for shows already past.
- Record sent/failed on the show and show it on the artist page.
- Email Brian on failure.
- Drink tickets line only where the venue copy mentions drink tickets (FSQ, WP).

### 15. Content fixes
- **Day-of contact:** the mix engineer's name + cell from the staffing sheet, like WP already does. Then the line: "Please do not advance with them or call them prior to show day, as they are part-time staff." Fall back to the booking Lead. If neither exists, say the day-of contact comes the week of the show and drop the "text them 5 min out" line.
- **Salsa parking (Salsa only):** "Nick Radina will send parking validations" (English + Spanish). Replaces "Attached are QR codes".
- **Salsa riser:** hide the flat/riser question on the Salsa form. Stage Type defaults to Flat.
- **Salsa stage escort:**
  - New required question on the Salsa form: stage-escort band rep (name + cell), English + Spanish.
  - Add to the email: "please identify this person to on-site staff upon arrival."
  - Advance doc Band Contact rows: add under the main contact ("Stage escort: Name" / "Escort: cell"). If the escort is the main contact, append "(stage escort)".
- **Load-in acknowledgment:**
  - Garage/QR acknowledgment on Fountain Square forms only.
  - WP gets a short "review your load-in details with your day-of contact" acknowledgment.
  - ESP/Court/Zeigler/IA copy and Memorial Hall stay open, pending Brian's copy.

### 16. Series
- The Series dropdown's "No series / one-off" becomes two options: "Stand-Alone Internal" and "3rd Party".
- Remove the Event Type field from the lower section of the booking form. The top selection dictates internal vs. 3rd party.
- Doc Event Type checkbox: named series = Internal Event, "3rd Party" = Third Party Event, "Stand-Alone Internal" = Internal.
- The form sends blank, never "default". A blank never overwrites a real series.
- The Closers (booking event_type Internal, show 344) becomes "Stand-Alone Internal".

### 17. Labels and sheet
- One shared label table for the dashboard, Show Status Log, digest, sheet STATUS block and artist page: Queued / Sent — Awaiting Reply / Follow-up Due / Follow-up Sent / Advancing In Progress / Finalized / Cancelled.
- Remove the stale STATUS block (cols 38–44) from the live advance-list.xlsx once.
- STATUS block always at the far right. Never strand a copy or erase hand-added columns.

### 18. Back-to-back bookings
- Queue instead of quit: a locked run waits and re-runs, and the running pipeline re-checks for new bookings before finishing.

### 19. Show Status Log
- If the existing file can't be read, skip the regen and retry next run.
- Email Brian after 3 consecutive failures.
- Keep a dated backup before each rewrite.

### 20. Slot clash
- Block at booking if that slot is already taken at the venue+date.
- Multi-band nights have no default slot.
- Email Brian on a clash coming from the sheet or RiffPay.

### 21. Reminders
- Only the closest open reminder sends per run; older ones are marked skipped.
- The unresponded alert waits 24h after the welcome.
- Email Brian if the 9am check didn't run.

### 22. backfill.py
- Skip submissions already in the DB (submit timestamp + band). Dry-run by default.
- Archive the leftover test JSONs to data/_archive:
  - 20260903-051000 kim-and-the-polaris-stars
  - 20260904-054737 kim-and-her-angels
  - 20260908-135137 sylmar
- 20260908-152149__sylmar.json is the real one (submission 44). Keep it.

### 23. Submit timing
- Disk save first, translate after.
- gunicorn: 120s timeout, 4 threaded workers.
- "Run again" returns immediately and shows progress.

### Low-severity cleanup (fix all)
- Deploy waits for in-flight pipeline runs/sends before restarting.
- Staffing times honor a/p when written, PM only when not.
- Remove the /internal/run-followups route. Deactivate the Create Draft workflow.
- Clear the app.py.bak files and docfill.py on the VM.
- Remove the creds export left in the n8n container's /tmp, and stop deploy_n8n_workflows.command leaving one.
- Pass the Groq key privately (not on the curl command line).
- Escape band names in the digest HTML.

## Evidence notes
- All 23 filed docs were rewritten at 17:04:49–51. 091826 513 Airwaves (Wishy/RatBoys) was hand-edited at 18:27.
- All 52 internal-send-outlook executions returned Graph 202. No send failures so far.
- Lifecycle runs take 2–5s. No gunicorn worker timeouts in the journal.
- Real conflicted copies from Andi Schultes (9/4) exist in FSQ and WP 09.2026: shared-folder concurrent edits happen.
- WP 9/11: RiffPay "Bravo" / "Taymar Israel" duplicated staff-booked "DJ Bravo" / "Special Request Band".
