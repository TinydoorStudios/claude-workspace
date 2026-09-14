# Band Advance — Fable review pass (2026-09-13)

Scope: every file on the `advance-system` branch (Code/BandInfoForm), the live VM (192.168.200.84) state as of 22:45 EDT, the advance database, the n8n workflow versions actually running, and a research pass on how other venues and festivals advance artists. Nothing was changed. Nothing was sent.

> **Status 2026-09-14 09:00:** Brian decided every question in Section 9 (H2 → per-cell provenance; nightly 06:30 run; ff-merge + worktree + deploy guard; name gate + honeypot; 48h reminder gap; CANCELLED rename; TBD times; E1 + E4 + E5 built, E6 not). All of it was built on `advance-system` in its own worktree, staging-tested (70/70, `tools/staging/`), and deployed live at 23:26 on 9/13 (app + migrations + timers) and 23:27 (n8n send + lifecycle workflows). Tech-pack drafts for review are in `Handoffs/tech-packs/`. The fast-forward of `main` is deferred: two files are dirty in the shared checkout (`about-me/memory.md`, `Code/landing-redesign/deploy/index.html`) and a merge would have to overwrite them.

## 1. Bottom line

The 23 audit fixes are deployed and the versions n8n is actually executing carry them (Confirm Sent and Mark Cron are both in the active workflow_history rows, 22:22 EDT). Tomorrow's 9am run will send exactly one band email: the 3-day reminder to The Amador Sisters (Salsa, 9/17). No welcomes are due. The 10:15 watchdog will find a `cron` row and stay quiet. The Porch Goose 3-day alert already went out 9/13 13:06.

Six things need a decision before the next build. Two of them are design questions the audit didn't reach, not bugs in what was built. They are listed in Section 2 in the order I'd take them.

## 2. Findings, ranked

Severity is about consequence: double email, wrong band, lost data, silent failure.

### HIGH

**H1. A duplicate booking row sends the welcome twice in one run.**
`shows_due_for_initial_advance` LEFT JOINs `bookings` on venue + date + normalized name with no DISTINCT. Two booking rows for the same band (a double-click on Log booking, a refresh that re-POSTs, a staff re-entry) return the same show twice, and the welcome loop in `advance_lifecycle` sends both before `mark_advance_drafted` is checked again. `bookings` has no unique constraint and the staff form has no idempotency token. The RiffPay importer de-duplicates by delete + insert; the staff form does not. Live DB today: zero duplicates, so nothing has fired yet.
Fix: unique index on `bookings (venue, event_date, lower(btrim(artist_name)))` with `ON CONFLICT DO UPDATE`, `DISTINCT ON (s.id)` in the three lifecycle queries, and a `seen` set on `show_id` in the welcome loop. Same JOIN shape exists in `shows_due_for_followup` (already de-duped by the `by_show` dict) and `shows_due_for_unresponded_alert` (would list a band twice in the alert, cosmetic).

**H2. A returning band's doc is pre-filled from their previous show, and "never overwrite" then blocks their new answers.**
`import_sheet.py` calls `add_act` without a `submission_id`, so `event_acts()` falls back to `newest_submission(artist)` for any venue and any date. On the day a returning band is booked, its doc is created with the answers from the last show (monitors, tent, vehicles, contact). When the band submits the new form, docmerge sees filled cells, leaves them, and emails a diff. Every returning band's real answers arrive as notice emails you apply by hand. Today none of the 18 upcoming acts is in this state (each either has this show's submission or none), so it hasn't bitten yet. It will the first time a band inside the 6-month window is re-booked, e.g. Zumba Latin Band booked again in November. The advance-list sheet has the same problem in miniature: `status_sheet.records()` uses `newest_submission(artist)`, so the new row shows last show's answers in blue before the band responds.
This is a decision, not a patch. Two ways out:
- (a) Only fill a doc from a submission for this show (venue + date match). Prefill stays in the email and the band's form link; the doc stays blank until they answer. Smallest change, keeps decision #1 intact.
- (b) Per-cell provenance: record what the pipeline wrote per cell in `filed_docs`; a cell that still equals what the pipeline wrote is the pipeline's to update, a cell that differs is a hand edit and is protected. Fixes H2 and the general "band corrected a number, you get an email instead of an updated doc" friction. Reopens the wording of decision #1 ("only empty cells get filled"), not its intent (hand edits are never wiped).
My recommendation is (b), with (a) as the fallback if you want zero risk to hand edits.

**H3. A bad internal token makes every send report "sent" with nothing sent.**
In `internal_send_outlook.json`, Check Token returns an empty item on mismatch. With `responseMode: lastNode` n8n answers 200 with no `sent` key, and `mailer.send` treats a 2xx without `"sent": false` as success (judgment call 5). A token rotation, a deploy that resolves the placeholder wrong, or an env edit would stamp every welcome and reminder as sent, no alert, no retry. The same failure mode as the 9/13 empty-body incident.
Fix: Check Token throws (`throw new Error('bad token')`) so the webhook answers 500. One-line change, deploy with `deploy_n8n_workflows.command`.

**H4. The hold check only runs inside a package run.**
`holds.run()` is called from `package_run.py`, which runs only on a booking, a submission's regen (no: regen_show.py does not run it), or "Run again". Delete a row from the sheet on a quiet week and nothing notices; the show keeps emailing on schedule. Judgment call 3 ("sheet edits land late") is the same gap. Fix: a nightly full `run_now.py` (systemd timer, 06:30, before the 7am digest and 9am lifecycle). It sends no band email; it can send doc-notice and hold emails, which is the point.

**H5. Auto-attach can hijack another band's booking.**
`record_submission` path 3: a typed name that matches no artist booked at that venue + date attaches to the single unanswered booking, whatever it is. On a two-band night where the headliner already responded and the opener submits under a variant of their own name ("Blue Jays Quartet" for "The Blue Jays"), path 2 misses (variant name isn't an artist), and the submission attaches to the other band. That stamps the other band's `responded_at` (their reminders stop) and writes the opener's answers into the other band's doc column. Detach fixes the database; the doc cells stay written and then block the real answers (H2 again). Also open to the public: anyone posting the form at a real venue + date with a made-up name attaches to whoever hasn't answered.
Fix: auto-attach only when the typed name is plausibly the booked name (one contains the other after normalizing, or token overlap ≥ 50%); otherwise `pending_pick` and no `responded_at`. Add a honeypot field to the public form.

**H6. The repo's working tree is shared between sessions and a branch switch happened under this review.**
At 22:49 tonight another Claude session checked out `show-pipeline-2026-07-26`, then `main`. The deployed code lives on `advance-system`, 144 commits ahead of `main` (`main` has none it lacks). `deploy_app.command` tars whatever is in the working tree, so a deploy run while another branch is checked out ships the wrong code (the app tar would fail on missing files; the tools tar would not). Fix, in order: fast-forward `main` to `advance-system` and push (nothing to merge); give the advance system its own `git worktree` so its path never changes branch; make both deploy scripts refuse to run unless `git branch --show-current` is the expected branch.

### MEDIUM

**M1. Late bookings get three emails in four days.** The Amador Sisters were booked 4 days out: welcome 9/13, 3-day reminder 9/14, 1-day reminder 9/16. `mark_stale_followup_tiers_skipped` only skips tiers already passed. Suggest: skip any tier that would fire within 48 hours of the welcome, the same shape as the 24-hour rule on the internal alert.

**M2. Bilingual series get English-only reminders.** The Salsa welcome is English + Spanish; the 7/3/1 reminders in `advance_lifecycle` are a hardcoded English body. Add the Spanish half for `BILINGUAL_SERIES`.

**M3. Blank booking times silently become Fountain Square times.** `draft_emails.py` fills any blank schedule field from `SCHEDULE_DEFAULTS` (6:00p load-in, 7:00p start, 11:00p curfew). A Washington Park or Court Street booking with no times entered emails the band an FSQ day schedule as fact. Suggest "TBD, your day-of contact will confirm" for any blank field, or make the five times required unless the series schedule is locked.

**M4. Cancelled shows aren't marked in the doc or the filename.** Decision 4 says CANCELLED everywhere including the filed doc. Nothing writes to the doc (which would collide with decision 1) and `event_display_name` still uses the unfiltered act list, so a cancelled headliner keeps its name in the filename while `daysheet.build` drops its cells. Cheapest honest version: rename the file with a `CANCELLED - ` prefix through the same rename-in-place path.

**M5. The lifecycle renders welcomes into the shared `tools/drafts/` folder that every package run wipes.** A booking landing during the 9am run can delete a draft between render and read, producing "welcome email didn't render", a failure alert, and a retry tomorrow. The glob-by-mtime fallback can also pick a stale draft if one band's render fails while an older file exists. Fix: render to a per-run temp directory (`draft_emails.py --out`), or have `draft_emails` return the text.

**M6. Send-failure nag repeats daily with no escalation.** A legacy show with no contact email produces one failure row per day forever, one alert email per day. Fine for a Graph outage, noisy for a data gap. Suggest: alert on day 1, then weekly, with the band named.

**M7. `ZP Pool` n8n workflow errors every minute.** 1,904 error executions. Unrelated to advancing, but it buries the advance workflows' own executions in the log and is exactly the noise that hides a real failure.

### LOW / cleanup

- `status_sheet.py` still carries its own `STATE_FILL` (no held/cancelled) despite audit #17's one-table rule.
- `advance_reminders` rows for shows 640 and 703 (tier 7) read `sent = true`; they were pre-skips written before the column existed. One UPDATE fixes the record.
- `app.py` still reads `ADVANCE_CLEANUP_DRAFTS_URL`; `advance.env` still carries it and the lifecycle-now URL comment block. Remove the dead var.
- Show Status Log's "Ready to Send" column shows the retired `send_reminder_sent_at`; drop it.
- `dump_followups.py` and `followup_queue` (retired) still run every package run.
- Booking form marks Contact Name required (red asterisk) but neither client nor server enforces it.
- `Nyquist/` root has eight leftovers from earlier migrations (`_pre-universal-migration-2026-09-10`, `_deleted-hand-typed-duplicates-2026-09-12`, `_bin`, `_template`, `advance-list.xlsx.bak.20260911-171218`, `generate.command`, two System Overview files). One `_archive/` folder would leave four things at the top: the sheet, the Status Log, Series Email Templates, Blank Advances.
- ARCHITECTURE.md still describes the Gmail-draft era in three sections; the KB article is behind.
- Four "My workflow" test workflows and the retired draft/delete-draft workflows are still listed in n8n.

### Verified fine (so you don't re-check)

n8n and the VM are both America/New_York, so the 9am cron and the 10:15 watchdog agree. The advisory lock, per-show commits, and closest-tier-only logic read correctly. The `pgrep` bracket trick doesn't self-match. `_atomic_save` plus the pre-replace hash check is sound. Word `~$` lock detection works across Dropbox (those files sync). Stage plots are in the weekly archive. Disk is 28% of 197G after the resize. Gate lockout, safe-redirect, signed artist token, and locked venue/date (hidden inputs) all behave. The FSQ `_attachment.pdf` is picked up.

## 3. The seven judgment calls

1. **Edited docs still get filled.** Right call; keep. It becomes moot under H2 option (b).
2. **No welcome after a submission.** Right.
3. **Sheet edits land late.** Wrong as a steady state; H4's nightly run fixes it without a design change.
4. **"Possible correction" holds, 2-day window, max(3, 30%) guard.** Reasonable. With 18 active shows the guard is 5; fine.
5. **Confirm Sent with no status reports sent.** Right for that node. H3 is the sibling hole (the token node) and should close.
6. **Doc-merge noise filter (new value contained in doc text).** Right. Note it is case-insensitive substring, so "5" in "15 wedges" suppresses a real diff; use whole-token containment.
7. **Engineer line on WP too.** Right.

## 4. Locked decisions I'd ask you to reopen

Only two, both narrow:

- Decision 1's wording ("only empty cells get filled") vs its intent (hand edits are never wiped). See H2 option (b).
- Decision 6's auto-attach rule ("exactly one unanswered booking" is enough). See H5: add a name-plausibility gate.

Everything else stands.

## 5. Efficiency: where the human time actually goes

Counting the touchpoints you personally absorb from this system per week, today:

| Surface | What reaches you | Count when busy |
|---|---|---|
| Email alerts | doc notices, holds, send failures, watchdog, 3-day unresponded, submission matches, slot clashes, thank-you failures, backup failures, gate lockout, lifecycle summary, digest | up to 6 distinct emails on a bad morning |
| Web pages | dashboard, booking form, hold page, match page, artist page | 5 |
| Files | advance-list.xlsx, Show Status Log.xlsx, the filed .docx, Series Email Templates | 4 |

Where I'd cut:

**E1. One "Needs you" surface instead of eight email kinds.** The dashboard already polls every 20 seconds. Add a panel at the top listing open decisions with their links (pending matches, holds, doc notices, send failures, shows with no email, watchdog miss). Keep real-time email for send failures and holds only; fold everything else into the 7am digest under a "Needs you" heading. This removes most of the inbox churn without losing anything.

**E2. Nightly full run** (H4) means the sheet and the docs are never more than a night stale, and "Run again" stops being a habit.

**E3. Stop maintaining two sources of truth.** The advance-list.xlsx round-trip (openpyxl rewriting a Dropbox file, hidden `_advance_meta` sheet, conflicted copies, "open in Excel" locks, STATUS block rebuilds) is the most fragile third of the codebase and exists so the sheet can be edited by hand. The database already holds everything the sheet holds. Option: bookings become the source; the sheet becomes a generated read-only view (or a Google Sheet published from the DB), and per-show overrides move to the booking record via the staff hub. This is a structural change and the biggest single simplification available. Not for this week.

**E4. Tech pack up front.** Every source in Section 6 leads with it, and `forms_config.TECH_PACKS` is empty for all six venues. One PDF per venue (stage dims, PA, consoles, mic inventory, backline policy, power, load-in map) attached to the welcome cuts the back-and-forth that generates most "additional questions" answers. FSQ already has the load-in doc; it's half a tech pack.

**E5. T-1 confirmation for everyone.** The thank-you fires on Mark Finalized only. Industry practice is a day-before message with final times and the day-of contact. Option: an automatic T-1 "see you tomorrow" for every responded show (finalized or not), with schedule, parking, and the engineer's name; the thank-you stays as the sign-off.

**E6. Texting as a second channel.** The form already collects a day-of cell. SMS reminders run around 98% open rates against roughly 20% for email in the event-communication studies found; Life Is Beautiful reported delivery going from 21% to 98% after switching. A Twilio number for the 3-day and 1-day reminders (link only, 160 characters) would likely halve the unresponded list. Cost is a few dollars a month. Needs consent language on the form.

**E7. RiffPay import is a manual CSV drop.** If RiffPay exposes an export URL or API, a nightly pull with the existing importer removes a manual step and the naming drift it caused on 9/11 (two "Neo Soul" events for the same night, two bands emailed under two names).

## 6. How other venues and festivals do it

What the practice literature and the tools agree on:

- **Timing.** Clubs and theatres start the advance 3 to 4 weeks out; festivals 6 to 8 weeks, with international acts earlier. Your 21-day welcome and 7/3/1 cadence sit inside that norm. The consistent add-on is a final confirmation the day before with locked times.
- **Direction.** The venue sends the tech pack first; the artist answers with stage plot, input list, backline needs, and a day-of phone that belongs to someone in the band. Yoshi's Oakland's advance letter is a good compact example: nine yes/no questions, then "reply with plot, input list, backline, DOS phone", with house rules stated once. Your form already collects all of that.
- **Single source of truth.** Every product pitch and every practitioner article names the same failure: information scattered across email, spreadsheets and shared drives. The fix is one record per show that all departments read. You have the record (Postgres) but still maintain the spreadsheet beside it (E3).
- **Structured forms with missing-info nudges.** FestivalPro and Beatswitch both describe portals where the artist fills structured fields and the system emails about what's still missing. Your form plus 7/3/1 reminders is the same pattern; the gap is that a band can't come back and edit what they sent (a resubmission is a new record and, today, a notice email).
- **Milestone timelines.** Beatswitch lets the organiser define the advancing timeline with milestones; Crescat's liaison guide recommends the same. You have the milestones implicitly (21/7/3/1). Making them visible on the dashboard per show (a small timeline strip) is cheap and matches what these tools sell.

Tools, and whether they'd fit a six-venue municipal program:

| Tool | What it is | Fit |
|---|---|---|
| Prism.fm | Venue ops suite: holds, offers, contracts, an Advance tab, run of show, settlement. 3,000+ venues. | Built around ticketed rooms and settlements; most of it is dead weight for free outdoor series. Pricing on request. |
| Opendate | Booking + ticketing + templates and shared event pages for advancing. | Same shape as Prism; ticketing-first. |
| Master Tour Venue (Eventric) | Standardized online venue tech pack; touring parties on Master Tour pull it. Pilot program, tech pack piece live. | The tech pack half is worth a look for FSQ and WP specifically: free listing, and touring acts (513 Airwaves guests) already live in Master Tour. |
| Band Advance (advance.band) | Band and venue profiles, schedules, day-of documents, cross-org sharing, "missing information" dashboard. 30-day trial. | Closest to what you built; would replace the form + doc, not the sheet or the Word filing your team relies on. |
| Beatswitch / FestivalPro | Festival artist portals with advancing timelines and automated nudges. | Oversized; useful as a design reference for the "needs you" panel and milestones. |
| Propared | Production scheduling and one-click schedule sharing. | Solves a different problem (crew and run of show). |
| Jotform / Typeform | Form templates (technical rider, backline request). | You already have a better form. |

Net: nothing off the shelf does the part that's specific to you (fill the 3CDC universal Word doc in the real Dropbox venue folder, feed the staffing sheet, bilingual Salsa). The best ideas to borrow are the tech pack up front, a visible milestone timeline, a day-before confirmation, and SMS as a second channel.

## 7. The VM picture

What runs on 192.168.200.84 for this system:

| Piece | State |
|---|---|
| `band-advance.service` (gunicorn, 4×4 threads, 120s) | active, restarted 22:20 |
| `advance-db` (Postgres 16 container, :5433) | 28 artists, 28 shows, 15 submissions, 28 bookings, 18 filed docs |
| n8n: Advance Lifecycle Check (9am), Daily Digest (7am), Advance Recap Extraction (2am), Advance Notify, Internal Send — Outlook, Crew Report, Backup Report | all active, current versions confirmed |
| n8n retired: Advance Follow-up Check, Create Draft, Delete Drafts, four "My workflow" stubs | inactive but listed |
| timers: advance-db-nightly (02:40), advance-lifecycle-watchdog (10:15), band-advance-backup (weekly Sun 03:17), dropbox-cache-guard (2 min) | all scheduled |
| Dropbox headless client | up to date, cache 37M, disk 28% of 197G |
| `/opt/band-advance/data` | 15 submission JSONs, 56 uploads, logs, `_archive/` |

Clean-up that changes nothing functional: delete the four stub workflows and the three retired advance workflows from n8n (JSON stays in the repo), fix or pause ZP Pool, archive the Nyquist leftovers, drop the dead env var. After that the VM picture is one service, one DB, four timers, seven workflows.

## 8. Test gaps from the handoff, and what I'd add

| Gap | Test |
|---|---|
| Band 2 submits into a doc band 1 filled | Two-act event, fill act A, submit act B, assert A's cells untouched and B's filled; then resubmit B with one changed value, assert notice not overwrite |
| Bilingual Salsa thank-you | `finalize_thankyou.build_email(..., bilingual=True)` contains the separator and both bodies |
| Zero-candidate pick email and manual attach | submit at a venue + date with two unanswered bookings, assert `pending_pick`, no `responded_at`, then `/submission-match/<id>/attach/<show>` moves it |
| `import_sheet` slot-clash email | two rows same slot same event, assert one act, one `slot_clash` notice |
| Status Log 3-failure alert | lock the file three runs, assert one alert, counter resets on success |
| RiffPay under new booking rules | import a CSV with a band already staff-booked under a variant name, assert one event, one welcome (this is the 9/11 case) |
| New from this pass | duplicate booking rows → one welcome; bad token → 500 and no stamp; late booking → no reminder within 48h |

## 9. Questions, in order

1. H2: fix the returning-band doc pre-fill with (a) this-show-only submissions, or (b) per-cell provenance?
2. H4/E2: add the nightly 06:30 full run (no band email; doc-notice and hold emails allowed)?
3. H6: fast-forward `main` to `advance-system`, push, and move the advance system to its own worktree?
4. H5: tighten auto-attach with a name-plausibility gate and add a honeypot?
5. M1: no band-facing reminder within 48 hours of the welcome?
6. M4: mark cancelled shows by renaming the doc with a `CANCELLED - ` prefix?
7. M3: blank booking times say "TBD" instead of FSQ defaults?
8. Which of E1/E4/E5/E6 to build next, if any.

## Sources

- [Tour Manager Info: How to Properly Advance a Show or Tour](https://tourmanager.info/advancing-shows/)
- [Spotify for Artists: How to Advance Your Show Like a Pro](https://artists.spotify.com/en/blog/how-to-advance-your-show-like-a-pro)
- [The Efficient Hustle: Advancing, what to expect from a venue representative](https://www.theefficienthustle.com/blog/2020/6/8/advancing-what-to-expect-from-a-venue-representative)
- [ProSoundWeb: Advancing the Show, the venue tech package](https://www.prosoundweb.com/advancing-the-show-the-what-when-why-of-the-venue-tech-package/)
- [Yoshi's Oakland show advance checklist (PDF)](https://yoshis.com/userfiles/kcfinder/files/ADVANCE-FORM-LETTER-3.pdf)
- [Ticket Fairy: Technical advancing for festivals](https://www.ticketfairy.com/blog/technical-advancing-for-festivals-coordinating-with-artists-production-riders)
- [Crescat: Artist liaison self-help guide](https://crescat.io/blog/ultimate-self-help-guide-artist-liaisons)
- [FestivalPro: The artist advance sheet](https://www.festivalpro.com/festival-management/1070/news/2020/10/14/The-Importance-of-the-Artist-Advance-Sheet-for-Events-and-Festivals.html)
- [Prism.fm for venues and promoters](https://prism.fm/why-prism-for-venues-and-promoters/)
- [Opendate music venue management](https://www.opendate.io/info/music-venue-management-software)
- [Eventric: Master Tour Venue](https://www.eventric.com/master-tour-venue/) and [PLSN: standardized venue tech packs](https://plsn.com/featured/master-tour-launches-industry-first-standardized-tech-packs-for-venues/)
- [Band Advance (advance.band)](https://advance.band/)
- [Beatswitch: Artists](https://www.beatswitch.com/products/artists)
- [Propared](https://www.propared.com/)
- [SimpleTexting: SMS for entertainment venues](https://simpletexting.com/guide/sms-marketing-for-entertainment-venues/) and [Text-Em-All: event text messaging](https://www.text-em-all.com/message-types/event-text-messaging)
- [Jotform: Live music technical rider form](https://www.jotform.com/form-templates/live-music-technical-rider-form)
