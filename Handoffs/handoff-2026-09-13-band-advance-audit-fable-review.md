# Context Handoff — 2026-09-13
**Session topic:** Band Advance: full QC audit → 23 fixes decided one at a time → built, staging-tested, deployed live. Handing to Fable for a review and improvement pass.
**System:** Code/BandInfoForm/ on branch `advance-system`, n8n VM 192.168.200.84 (advance.tinydoorstudios.com), n8n workflows, advance-db (Postgres container), Dropbox venue folders

---

## What We Did
I had Claude (Opus 5) audit the whole Band Advance pipeline, since it's now a live workflow with zero room for errors. It found 23 real issues plus a list of low-severity cleanup. The two worst:
- Every pipeline run was rebuilding every filed advance doc from the blank template, wiping hand edits.
- Failed sends were being recorded as sent.

I decided every item one question at a time. Claude then built all of it and tested it on the VM against a cloned database, copied Dropbox folders and a local mail stub: 70 checks, all passing. A preflight against an untouched clone of real data came back clean. It then deployed to live around 22:30.

Commits (not pushed):
- `f5e21e2` — all the fixes
- `02a1a15` — deploy-script fix

Nothing sent any email during the work.

---

## Current State

**Done**, and live on the VM:
- **Filed docs**
  - Docs are never overwritten. `tools/docmerge.py` fills only cells still identical to the blank universal template.
  - A `filed_docs` registry tracks every doc. The 18 current docs are adopted and renamed in place to the "Series - Headliner" names.
  - When a value differs from the doc, the doc is left alone and I get a notice email.
  - A doc open in Word is skipped. Saves are atomic.
- **Sending**
  - Single send path `app/mailer.py`. A send counts only when n8n's new "Confirm Sent" node sees Graph return 202.
  - Failures retry on the next run, with one alert per show / kind / day. `ADVANCE_MAIL_DISABLED=1` is a kill switch.
  - The lifecycle run holds a Postgres advisory lock and commits after each send.
  - Only the closest reminder tier sends per run.
  - The 3-day unresponded alert now includes manual-entry shows and waits 24h after a welcome.
  - A 10:15 watchdog timer checks that the 9am run happened.
- **Holds, cancel, merge**
  - Cancel buttons on the dashboard and artist pages.
  - `tools/holds.py` puts any show missing from advance-list.xlsx on hold; I decide at `/show/<id>/hold` (cancel, restore, or merge a typo into the corrected show).
- **Submissions**
  - A band name that doesn't match its booking auto-attaches when exactly one unanswered booking fits the venue + date. I get Confirm / Detach at `/submission-match/<id>`.
  - Artist token is signed.
  - Stage plot carries forward for returning bands.
  - Disk save happens before translation.
- **Booking form**
  - Contact email is required unless Manual band advance is checked.
  - Series is required: a named series, "Stand-Alone Internal" or "3rd Party". The Event Type field is gone.
  - A slot already taken that night is refused.
  - "Run again" is async.
- **Content**
  - Vehicle counts show everywhere.
  - Day-of contact is the staffing sheet's mix engineer, plus the "part-time staff, don't call before show day" line.
  - Salsa: Nick Radina parking line, stage-escort rep field, no riser question.
  - The garage/QR load-in acknowledgment appears on FSQ forms only.
- **Labels and logs**
  - One shared label table (`app/status_labels.py`).
  - The stale STATUS block is removed from the sheet, and vehicle columns were added.
  - The Show Status Log is never overwritten when it can't be read.
- **Ops**
  - Nightly DB dump to both NAS boxes (02:40), verified.
  - gunicorn is now threaded, 4 workers × 4 threads, 120s timeout.
  - `dropbox_exclude.sh` no longer deletes anything.
  - The delete-drafts and create-draft n8n workflows are unpublished.
  - Token-bearing temp files and 124 `app.py.bak` files are cleaned off the VM.

**In progress:** nothing.

**Up next:** the Fable review pass. Watch the first real sends through the new confirm path at tomorrow's 9am run (9/14), and check the 10:15 watchdog stays quiet.

---

## Key Decisions (Locked)
The full spec is in `Handoffs/band-advance-audit-decisions-2026-09-13.md`; don't re-open these without asking me. The ones most likely to get "improved" wrongly:
- **Docs:** never overwrite a filled cell, on any path. Differences become a notice email, never an edit.
- **Cancelled shows:** kept on record and marked CANCELLED everywhere, never deleted. A typo fix is a merge that carries send history, so there's no second welcome.
- **Staff login:** both passcodes stay (lockdown and 1313). Rate limit is 5 tries per IP, then a 15-minute lockout.
- **No series:** "Stand-Alone Internal" or "3rd Party". A named series means an Internal event. The Event Type field stays gone from the booking form.
- **Salsa:** parking copy reads "Nick Radina will send parking validations" (Salsa only). The escort rep goes under the main contact in the Band Contact rows.
- **Day-of contact:** the mix engineer from the staffing sheet (FSQ and WP), then the booking Lead, then "we'll send your day-of contact the week of the show".
- **Hard rule for any work on this system:** nothing run during development or testing may send an email. If something seems to need a real send to verify, stop and ask me first.

---

## Judgment Calls to Pressure-Test
Claude made these where my answers left room. They're the best targets for Fable.
1. **Edited docs still get filled.** A doc that was hand-edited still gets its blank cells filled; it isn't skipped. That keeps band 2 landing on multi-band nights. The checksum only flags "hand-edited" in the notice and guards against a mid-run save.
2. **No welcome after a submission.** A band that already submitted never gets the welcome.
3. **Sheet edits land late.** A booking run files only its own show, so a sheet edit to some other show lands on that show's next booking, submission, or "Run again". There's no nightly full run.
4. **"Possible correction" holds.** A new show is only held as a possible typo correction if it was created in the last 2 days. The bulk-hold guard skips holding entirely if the sheet reads empty or more than max(3, 30%) of shows are missing.
5. **Confirm Sent with no status.** If the node can't read a status code, it reports sent, never failed, so a real 202 can't trigger a duplicate send.
6. **Doc-merge noise filter.** A notice is suppressed when the new value is already contained in the doc's text (a hand edit that extends the pipeline's value).
7. **Engineer line on WP too.** The part-time-staff line also goes on WP emails.

---

## Open Items
- **Graph client secret expiry is unverified.** The app's Mail.Send permission can't read it; check it in the Entra portal.
- **First live test of the confirm path is tomorrow's 9am run.** It passed the mock test (202 → 200 sent, 4xx → 500, no status → 200) but hasn't been through Graph yet.
- **Venue email copy** for ESP, Court, Zeigler, Imagination Alley and Memorial Hall is still pending my wording. Memorial Hall still isn't in the form's venue list.
- **Git push** of `advance-system` isn't done. Both commits bypassed the repo's pre-commit hook; no skill sources were touched.
- **KB wiki article** `band-advance-pipeline` isn't updated for any of this.
- **Test coverage is thin in places:**
  - multi-band doc fills when band 2 submits into a doc band 1 already filled
  - the bilingual Salsa thank-you
  - the zero-candidate "pick" email and manual attach
  - `import_sheet` slot-clash emails
  - the Status Log's 3-failure alert
  - the RiffPay import path under the new booking rules

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| `Handoffs/band-advance-audit-decisions-2026-09-13.md` | md | Locked spec for all 23 decisions plus cleanup; status says built + deployed |
| `Code/BandInfoForm/ARCHITECTURE.md` | md | New section "QC audit fixes (2026-09-13)" describing the new behavior |
| `Code/BandInfoForm/tools/docmerge.py` | py | Never-overwrite doc engine + registry + notices (new) |
| `Code/BandInfoForm/tools/holds.py` | py | Orphan-show hold check + hold email (new) |
| `Code/BandInfoForm/app/mailer.py` | py | Single send path, confirm rules, kill switch (new) |
| `Code/BandInfoForm/app/status_labels.py` | py | Shared status labels (new) |
| `Code/BandInfoForm/tools/migrate_filed_docs.py` | py | One-time registry adoption + rename (already run on live) |
| `Code/BandInfoForm/tools/run_again.py` | py | Background worker for the Run again button (new) |
| `Code/BandInfoForm/ops/*` | sh / service / timer | Nightly DB dump, watchdog timer, gunicorn unit, alert helper, fixed exclude script |
| `Code/BandInfoForm/app/templates/show_hold.html`, `submission_match.html` | html | New decision pages |

Heaviest rewrites: `app/app.py` (submit, booking, lifecycle, gate, new routes), `app/advance_db.py`, `tools/daysheet.py`, `tools/package_run.py`, `tools/run_now.py`, `tools/merge_status.py`, `tools/status_log.py`, `n8n/internal_send_outlook.json`, `n8n/advance_lifecycle.json`.

---

## Corrections / Watch-Outs
- **Safe-testing recipe** (build it, then tear it down after):
  - Clone the DB to `advance_test`.
  - rsync `~/Dropbox/Nyquist` plus the current venue month folders into `~/advtest/Dropbox`.
  - Set `ADVANCE_DROPBOX_ROOT` to that copy and `ADVANCE_STAGING=1`.
  - Point `ADVANCE_INTERNAL_SEND_URL` and `ADVANCE_NOTIFY_URL` at a 127.0.0.1:8199 stub.
  - Run gunicorn on :8198.
  - Never test against the live DB, the live Dropbox, or n8n webhooks.
- **Any manual run on live** needs `ADVANCE_MAIL_DISABLED=1` exported first. It won't send; it logs to `data/mail.log`.
- **`pgrep -f` inside an `ssh "..."` string matches its own bash process.** Use the bracket trick (`[r]un_now.py`). This stalled the first deploy for 10 minutes.
- **A global string replace turned `_internal_auth()` into infinite recursion** (caught in staging). Don't bulk-replace in `app.py` without re-reading the result.
- **n8n versions workflows.** Always deploy with `deploy_n8n_workflows.command`; it imports, publishes or unpublishes, restarts, and cleans its temp files. Webhook routes only mount after the restart.
- **Word stores line breaks as `<w:br/>`.** The doc-merge text comparison treats breaks and tabs as whitespace; changing that brings back false notices on multi-line cells.
- **Rollback:**
  - Pre-audit DB dump: `/var/backups/band-advance/pre-audit/` on the VM.
  - Sheet, Status Log, Salsa copy and exclude script backups: `~/advance-audit-backups/` on the VM.
  - Code: redeploy commit `9753cfa`.

---

## Resume Prompt

> Picking up from a 2026-09-13 session on the Band Advance system (`Code/BandInfoForm/`, branch `advance-system`, deployed on the n8n VM 192.168.200.84). Claude audited the whole pipeline, I decided 23 fixes one at a time, and all of them were built, tested against a staging clone (70/70), and deployed live. Commits `f5e21e2` and `02a1a15` are not pushed. Read `Handoffs/band-advance-audit-decisions-2026-09-13.md` (the locked spec) and the "QC audit fixes (2026-09-13)" section of `ARCHITECTURE.md` first.
>
> **Your task:** a review and improvement pass on that work. Look for correctness bugs, race conditions, edge cases the tests missed, and anything that could email a band twice, email the wrong band, lose data, or overwrite a filed doc. Start with:
> - `tools/docmerge.py`
> - the `/internal/advance-lifecycle` route and `/submit` in `app/app.py`
> - `record_submission` and `merge_shows` in `app/advance_db.py`
> - `tools/holds.py`
> - `tools/merge_status.py`
> - the Confirm Sent node in `n8n/internal_send_outlook.json`
>
> Also pressure-test the "Judgment Calls" in the handoff, and fill the test-coverage gaps listed under Open Items. Don't reopen the locked decisions. If you think one is wrong, tell me why and ask.
>
> **Hard rules:**
> - Nothing you run may send an email, internal or band-facing. If verifying something seems to need a real send, stop and ask me.
> - Test only in an isolated staging clone (recipe in the handoff): DB copy, Dropbox copy, local mail stub.
> - Any manual step on live runs with `ADVANCE_MAIL_DISABLED=1`.
> - Ask me one question at a time.
> - Present findings with options before changing anything live.
