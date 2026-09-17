# Band Advance System — Architecture

The advance pipeline: collect show details from artists, store them in one queryable
database, detect returning artists, draft their advance emails, and auto-fill the
standard show document. Built on the existing self-hosted Flask form.

## VM-native Dropbox sync (2026-09-02, widened 2026-09-12)

The n8n VM (192.168.200.84) runs its own headless Dropbox client (`~/.dropbox-dist/dropboxd`
+ `~/dropbox.py`, linked to Brian's account, selective sync). Originally restricted to
`Nyquist/` only; **as of 2026-09-12, sync also includes every real `3CDC <Venue>` folder**
(Court Street, Elm Street Plaza, Fountain Square, Imagination Alley, Memorial Hall,
Washington Park, Ziegler Park) so the VM can file advance docs straight into them.
Everything else at the Dropbox root (the loose legacy files, `FSQ`/`FSQ Archive`/`FSQ SPL`,
`Production`, `3CDC - BUDGETS`, `3CDC - All Sites Folder`, etc.) stays excluded — Brian's
explicit call, narrower than "sync everything." The keep-list lives in `~/dropbox_exclude.sh`
on the VM (a copy is checked in at `ops/dropbox_exclude.sh` for reference/redeploy). `~/Dropbox/`
on the VM is the same live account as `~/Dropbox/` on the Mac for every synced folder; Dropbox
propagates either side's writes to the other in a few seconds. **Caveat:** the exclude list is a
snapshot taken at setup/widen time — a brand-new top-level item in Brian's Dropbox won't be
auto-included or auto-excluded; re-run `dropbox_exclude.sh` (or hand-edit the exclude list) if
one shows up that matters. **Rule: nothing outside the keep-list is ever written or deleted from
this side.**

This lets `tools/run_now.py` do the whole generate pipeline locally on the VM — seed
pending staff bookings into `advance-list.xlsx`, run `package_run.py`, overlay the
built tree into the live folders, fold status back into the sheet — with no SSH/scp/
rsync hop back to the Mac. `/booking/run` (gated) wraps it; the `/booking` thank-you
page has a **"Run advance now"** button that calls it and shows a result summary.
The Mac's `generate.command` still works (it uses its own separate upload path to
`lists/_current.xlsx`, not the Dropbox-synced copy) but is now largely redundant for
day-to-day use — the button/VM path is the live one.

## The front door: real 3CDC venue folders (2026-09-12)

Day-to-day, Brian never opens this code tree. The production cockpit is the top-level
**`Nyquist/`** folder in Brian's actual Dropbox: he edits `advance-list.xlsx`, and each
show's **finished advance doc + stage plot file directly into the real, shared 3CDC venue
folder** — the same one Brian and the rest of the production team have always hand-filed
into — at **`~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/<MMDDYY> <Event> Prod Adv.docx`**
(e.g. `3CDC Fountain Square/09.2026 FSQ/091826 Wishy Prod Adv.docx`), matching that folder's
own long-standing hand-typed naming convention. Email drafts have no equivalent there (an
internal working artifact, not a finished document) and stay under `Nyquist/<VenueAbbr>/
<Year>/<MM Month>/Email Drafts/` — the old scheme, unchanged. Status folds back into the
sheet as a color-coded block (see below), with the Stage Plot cell linking across to the
real folder. `generate.command` uploads the sheet, runs **`tools/package_run.py`** on the VM
(rebuild events → fill each advance doc → draft each email → emit `status.json` → assemble
BOTH subtrees under `_package/filed/` and `_package/drafts/`), then rsyncs `filed/` onto the
real Dropbox root and `drafts/` onto `Nyquist/`, **each as an overlay (no --delete)** so both
archives accumulate. Filing scheme (real venue folder names, month-folder codes, filename
convention) lives in `tools/fieldspec.py`. Generation never marks anything sent — that moves
to Outlook. Before 2026-09-12 this filed into a Nyquist-only `<VenueAbbr>/<Year>/<MM Month>/`
archive; that history was migrated into the real folders on that date (see
`Nyquist/MIGRATION-LOG-2026-09-12.md`).

## Bridge to the show pipeline (2026-09-14, pipeline-fix Phase D)

The FOH paperwork pipeline (deep build → packet → `.ses` → wiki) lives on Brian's Mac under
`~/Documents/Claude/audio/<Venue>/<date> <Artist>/`, and the VM cannot create Mac folders, so the
bridge runs on the Mac: `audio/_shared/advance_bridge.py`. `--sync` queries this database over
SSH (`docker exec advance-db psql`, read-only) for shows in a ±window, scaffolds any missing show
folder, stamps the canonical **show key** (`fieldspec.show_key()` — `<venue code>-<date>-<slug>`,
identical on both sides) into the folder's `show.status.json`, scps the band's `stage_plot` /
`input_list` uploads from `data/uploads/` into the folder under the packet's own names, and writes
a facts-only `<Show>.brief.json` whose `show_notes` carries the band's monitor / IEM / backline /
input answers for the deep build to mine. It never overwrites anything. `--push-status` (run
automatically after a sync) writes `Nyquist/show-packet-status.json`; Dropbox carries it here and
`tools/status_log.py` folds it into three live columns on the Show Status Log — Packet, .ses,
Wiki — so one sheet answers both "has the band advanced" and "is the FOH paperwork built".
Nothing in the database changed for this; the key is computed, not stored.

## The shape

A **front half Nyquist drives** (batch intake → draft emails → you send) and a
**back half that runs itself** (artist fills the form → database → search / docs).
The database is the spine both halves touch.

```
  Brian's list (artist, date, venue, series, email)
        │
        ▼
  draft_emails.py ──► NEW vs RETURNING (6-month lookback) ──► draft .md files  ──► [you send from Gmail]
        │                                                         │
        │ (returning drafts carry a prefilled form link)          │
        ▼                                                         ▼
   Postgres  ◄────────────── /submit (form) ◄──────────── artist fills the form
   (artists, shows,                                        (public, or /f/<token> prefilled)
    submissions, files)
        │
        ├──► /search + /artist (gated, passcode) — on-the-spot lookup
        └──► docfill.py — fill the standard show DOC from a submission
```

## Components

| Piece | Where | What it does |
|---|---|---|
| Flask app | `app/app.py` on VM `/opt/band-advance/` | public form, `/f/<token>` prefill, gated `/search` + `/artist` + `/file`, `/healthz` |
| DB layer | `app/advance_db.py` | psycopg 3 helpers — upserts, prefill/returning queries, search. Shared by app + tools |
| Form config | `app/forms_config.py` | venue/series form variants (one engine, many variants) |
| Database | `advance-db` docker container, `127.0.0.1:5433` | dedicated Postgres 16 (isolated from n8n's PG) |
| Email drafts | `tools/draft_emails.py` | batch list → NEW/RETURNING → draft `.md` files. **Never sends.** |
| Events | `tools/event.py` + `events`/`event_acts` tables | put up to 3 artists on a bill; Artist 1/2/3 is derived from set start |
| Day-sheet fill | `tools/daysheet.py` | event → filled 513 Airwaves day-sheet `.docx` (writes band cells per act column) |
| Doc fill (generic) | `tools/docfill.py` | single submission → filled `.docx` (docxtpl) — stand-in template |
| Packager | `tools/package_run.py` | the VM entrypoint — sheet → full `Advancing/` tree (events, day-sheets, emails, status) under `_package/` |
| Backfill | `tools/backfill.py` | replay disk JSON into the DB (safety net) |

## Database schema

Four linked tables. Identity anchor is the **artist**; everything hangs off it.

- **artists** — one row per band. `name` is exact/verbatim (drives every email + doc).
  `match_key` is a *generated* column (`lower` + whitespace-collapsed) with a unique
  index, so case/spacing can never split a band and defeat the 6-month lookback.
- **shows** — one booking per row. `UNIQUE(artist_id, venue, show_date)`. Same band at
  two venues = two rows, one artist. Status: `not_advanced → email_sent → responded →
  built → complete`.
- **submissions** — one advance response per row, linked to artist + show. Queryable
  fields are promoted to columns; the full raw form lives in `data JSONB` so nothing is
  ever lost and new questions need no migration.
- **files** — one uploaded asset per row (stage plot / input list), linked to the
  submission and artist.

Full DDL in `db/schema.sql`.

## Reliability rule

A submission is **saved to disk first** (`app/data/*.json`), then written to Postgres
best-effort. If the DB is down, the artist still gets the thank-you page and the disk
record survives; `backfill.py` replays anything the DB missed. The live form can never
break because of the database.

## Returning-artist logic

`played_within(artist, ref_date, months=6)` finds the band's newest prior submission and
returns it if its show date is within the window — **deliberately cross-venue**. Played
Washington Park in June, booked for Fountain Square in September → returning, and the
draft prefills from the June submission.

## Events and the day-sheet

The advance form is per-artist; the day-sheet is per-event with three act columns
(ARTIST 1 / ARTIST 2 / ARTIST 3) — and most bills are 1–2 acts. Position on the bill
is **derived from set start** (Brian, 2026-09-15): earliest is Artist 1, latest is
Artist 3, nothing declares it and nothing stores it, so an artist booked later with
an earlier start renumbers the bill by itself — one artist alone is Artist 1, in
column 1. `advance_db.order_acts` is the only place that decides it. An **event**
groups artists onto one bill; `daysheet.py` then writes each act's
**band-provided** cells (Stage Plot, Engineer, Monitors/IEM, Scenic, Merch, Parking,
Drink Tix, Dressing-room tent, Backline, Contact) into that act's column of your real
template. The schedule and internal cells (PA, consoles, lead, "are we paying them?")
are left exactly as the template has them — those aren't band data, and you finish them.

```
python3 event.py create --name "513 Airwaves w/ Inhaler" --venue "Fountain Square" --date 2026-09-20
python3 event.py add-act --event 1 --artist "Buffalo Wabs and the Price Hill Hustle" --set-start 9:00pm
python3 event.py add-act --event 1 --artist "The Cincy Suns" --set-start 7:00pm
python3 daysheet.py --event 1        # -> tools/filled/<event>__daysheet.docx
```

Field→cell mapping lives in `daysheet.py::act_cells` — edit there to change what fills.

## Sending (the front half)

Decided: **Gmail now, Outlook in production.** `draft_emails.py` only writes drafts and
never sends. The send step is Nyquist-driven: hand over the batch, drafts are generated,
then the drafts are created as Gmail drafts (via the Gmail connector) for you to review
and send — approve-each, not auto. No throwaway Gmail-OAuth sender is built, since the
plan is to swap to Outlook; the interim path is drafts-you-approve.

## Spanish-language form (draft, 2026-09-12)

`?lang=es` on any form route (`/`, `/f/<token>`, `/s/<code>`) serves the form
in Spanish — `app/i18n.py` holds every label/help/option in both languages
(`form.html`/`thanks.html` call `t('key')` instead of carrying literal copy),
and a "Español"/"English" toggle link switches without losing whatever's
already filled in. Field `name=`s and every select/radio's stored `value=`
stay English on both language variants, so the DB/docfill/daysheet pipeline
never has to know which language a band used — only the open textareas
(`changed_notes`, `stage_plot_desc`, `backline`, `scenic`, `lighting`,
`additional`) carry actual Spanish content through.

Those textareas get machine-translated to English on submit, in place,
before disk JSON / Postgres / the notify email / the filed advance doc ever
see them — `app/es_translate.py`, one Groq call (free tier, `openai/gpt-
oss-120b` — same JSON-mode pattern as Code/GearTickets' own triage call,
different model since GearTickets' `llama-3.3-70b-versatile` was retired
from Groq's lineup by 2026-09-12) per Spanish submission, translating
every non-empty free-text field together
for consistent terminology. The original Spanish is kept alongside under
`<field>_es_original` in the same JSON, never dropped. Needs
`GROQ_API_KEY` in `advance.env` — a key of its own, not the one
GearTickets uses (that one lives inside n8n's encrypted credential store,
not a plain env var this app could read). Without it set, a Spanish
submission still works fine, it just stays in Spanish everywhere
downstream — the form itself never depends on translation succeeding.

The Fountain Square advance email also has a Spanish draft —
`tools/venue_email.py`'s `VENUE_EMAIL_ES`/`COMMON_REQUIREMENTS_ES` +
`tools/email_templates/advance_es.md.j2`. Wired into `draft_emails.py`'s
render path for any series in `venue_email.BILINGUAL_SERIES` (Salsa On The
Square is the only one so far, added 2026-09-12 same day as this section
was written but after this paragraph — it went out English-then-Spanish in
one message; see that section of this doc). Every other series stays
English-only through this same template, unaffected.

## Live-send migration (2026-09-13)

The initial advance and every follow-up now SEND for real via Outlook
(`internal-send-outlook`) the moment they're due — no more draft-and-review
step. Cadence trimmed to 7/3/1 days out (was 7/3/2/1). A reminder tier
already on or before the day a show was booked (same day as the welcome
counts as already-passed too) is permanently pre-skipped for that show
instead of firing a backdated reminder later —
`advance_db.mark_stale_followup_tiers_skipped`, checked right after the
welcome sends, in `app.py`'s `advance_lifecycle`. The old 21-day "your
draft is ready to send" nudge is retired. A separate, independent alert
(`shows_due_for_unresponded_alert`) still fires one real email to
`blloyd@3cdc.org` the first time a show crosses 3 days out with no
submission — a manual-follow-up flag, unaffected by any of the above.

**A real incident happened during this migration** — an n8n workflow edit
that looked fully successful (correct SQL, workflow showed active, every
test call returned 200/202) silently never took effect, because this n8n
instance versions workflows separately from the row that looks like the
live definition. Two real bands got a welcome email with an empty body
before it was caught. Full root cause, the correct way to edit an n8n
workflow in this project, and the empty-body guard now in place on both
sides of the Flask/n8n boundary — all in `n8n/README.md`'s "Live-send
migration + a real incident" section. Read that before touching any n8n
workflow file in this project.

## Manual band entry / skip-welcome-email (2026-09-13)

For a band that emails its info directly instead of using the form: check
"Band already emailed their info directly" on `/booking`. Stamps
`bookings.skip_welcome_email`, which `shows_due_for_initial_advance` reads
via its existing bookings LEFT JOIN to permanently exclude that show from
the automated welcome/initial-advance send (`b.skip_welcome_email IS NOT
TRUE` — `IS NOT TRUE`, not `= false`, so a show with no matching booking
row at all, where `b.*` is NULL, still isn't excluded). Permanent, keyed
off the booking row via the same venue+date+artist-name match every other
field on that join already uses — not a one-shot race against the
immediate on-booking trigger. The rest of the pipeline (sheet seed, docfill,
dashboard) runs exactly as normal; only that one send is suppressed.

The thank-you page then shows a direct link to the band's own full advance
form (`app.py`'s `_manual_fill_link`) — same signed-token/short-link shape
as the returning-artist reminder link, just without an artist id (none
exists yet — the pipeline that creates the `shows`/`artists` rows hasn't
run). Venue, date, band name, and contact are all seeded and show up
prefilled; venue/date render locked the same way any other seeded link
locks them. `/f/<token>`'s prefill seeding was widened to apply band_name/
contact_name/contact_email from the token's `s` payload unconditionally
(previously only happened inside the known-artist DB-lookup branch, which
a link with no artist id never enters).

## Security

- Public: the form (`/`, `/f/<token>`, `/submit`) — no login, by design.
- Gated (passcode, `lockdown`): `/search`, `/artist`, `/file`, everything with artist data.
- Prefill tokens are signed (itsdangerous) with `ADVANCE_SECRET`; they encode only the
  artist id + booking context, and expose nothing until loaded server-side.

## Run it

```bash
# draft a batch (writes drafts, never sends)
cd /opt/band-advance/tools
set -a; . /opt/band-advance/advance.env; set +a
../venv/bin/python draft_emails.py lists/your_batch.csv

# fill the standard DOC for a band
../venv/bin/python docfill.py --artist "Band Name"
../venv/bin/python docfill.py --fields        # list template placeholders

# search is at https://advance.tinydoorstudios.com/search  (passcode: lockdown)
```

## Setup (already done once — here for the record)

1. `db/docker-compose.yml` + `db/.env` (ADVANCE_DB_PASSWORD) → `docker compose up -d`
2. `db/schema.sql` applied via `docker exec -i advance-db psql -U advance -d advance`
3. venv deps: `psycopg[binary]`, `python-docx`, `docxtpl`
4. `/opt/band-advance/advance.env` (DB URL, secret, gate pass) + systemd `EnvironmentFile`
5. Cloudflare: `advance.tinydoorstudios.com` CNAME + tunnel ingress → `localhost:8097`

Redeploy code after edits: `./deploy_app.command` from the Mac.

## CLOSED — Artist Directory wiki (2026-09-02, resolved 2026-09-06)

Originally scoped as a second, dedicated Wiki.js instance on the n8n VM, separate from
the Live Sound KB. Superseded: Brian's actual ask was "one website that does everything";
the in-app **`/staff` hub** (log a booking, browse venue → series → band, search, artist
detail with files) built 2026-09-04 satisfies that — confirmed with Brian 2026-09-06, no
separate Wiki.js instance needed. Not revisiting unless something concrete surfaces that
the staff hub genuinely can't do.

## QC audit fixes (2026-09-13)

Full decision record: `~/Documents/Claude/Handoffs/band-advance-audit-decisions-2026-09-13.md`.
What changed in how the system behaves:

- **Filed advance docs are never overwritten** (`tools/docmerge.py`). A show's doc is
  created once; every later pass only fills cells still identical to the blank universal
  template. A value that differs from what the doc says is left alone and emailed to Brian
  as a notice ("doc says X, new info says Y"). The `~$` owner-file check for docs open
  in Word never fires on the VM — Dropbox doesn't sync `~$` files — so since 2026-09-16
  the real guard is a notice for any "(conflicted copy)" beside the doc (see below). Writes are atomic and re-check the file hash before replacing. Every doc
  is registered in `filed_docs`; lookups go through the registry, never filename sort order.
  When the last artist of the night changes, the same file is renamed in place (an artist
  added with an EARLIER start just becomes Artist 1 and renames nothing). Past shows are
  never touched.
  A booking's run files only that show (`run_now.py --scope "Venue|YYYY-MM-DD"`); a submit
  files only its show; "Run again" files every current show — all blank-cells-only.
- **One send path** (`app/mailer.py`). A send counts only when n8n's "Confirm Sent" node saw
  Graph return 202; otherwise the webhook answers 500. Failed sends, missing addresses and
  unrendered drafts are never stamped — they retry next run and Brian gets one alert per
  show/kind/day (`send_failures`). `ADVANCE_MAIL_DISABLED=1` is a hard kill switch for manual
  runs; `ADVANCE_STAGING=1` refuses anything but the local capture stub.
- **Lifecycle** stamps each show immediately after its confirmed send and holds a Postgres
  advisory lock so overlapping runs can't double-send. Only the closest open reminder tier
  sends per run. The 3-day unresponded alert includes manual-entry shows and waits 24h after
  a welcome. The 9am cron run is tagged (`?source=cron`, `job_runs`); a 10:15 systemd timer
  (`ops/advance-lifecycle-watchdog.*`) alerts if it didn't run, and the digest flags a miss.
- **Cancel / hold / merge.** Cancel on the artist page and dashboard (kept on record as
  Cancelled). After every package run `tools/holds.py` holds any current show missing from
  advance-list.xlsx — no sends — plus any fresh show that looks like its corrected version,
  and emails Brian a link to `/show/<id>/hold` (Cancel / Restore / "typo for → merge").
  Merge moves send history, reminders, submissions and sign-off to the corrected show. A bad
  sheet read (empty, or >30% of shows missing) holds nothing and alerts instead.
- **Submissions** save to disk before translation. A name that doesn't match its booking
  auto-attaches when exactly one unanswered booking exists at that venue+date (Brian gets
  Confirm / Detach at `/submission-match/<id>`), otherwise Brian picks. The form carries a
  signed artist token, never a raw id. A returning band that doesn't re-upload keeps its
  latest stage plot (`stage_plot_carried_from`).
- **Booking form**: contact email required unless Manual band advance; Series required —
  a named series, "Stand-Alone Internal" or "3rd Party" (that pick sets Event Type; the
  Event Type field is gone); Set Start / Set End are required, and a set start already
  taken by another artist on that bill is refused — it decides the running order, so it
  has to be unique. Slot and "Bands on the Bill" were removed 2026-09-15: order comes
  from set start and the bill counts itself. "Run again" runs in the background and the
  page polls.
- **Content**: vehicle counts reach the doc Parking row, sheet, artist page, notify email and
  thank-you; day-of contact is the staffing sheet's mix engineer (+ "don't advance with them
  before show day") with Lead/"week of the show" fallbacks; Salsa: no riser question, stage-
  escort rep field, Nick Radina parking line; garage/QR load-in acknowledgment on FSQ forms only.
- **Thank-you** runs as a worker (`finalize_thankyou.py --send --show-id`), skips past and
  cancelled shows, records `thankyou_sent_at`/`thankyou_error`, alerts on failure, and only
  mentions drink tickets where the venue's copy does.
- **Labels**: one table in `app/status_labels.py` for dashboard, artist page, digest, Show
  Status Log and the sheet's STATUS block (adds On Hold and Cancelled). merge_status removes
  any stale STATUS block and always rebuilds one at the far right.
- **Ops**: nightly DB dump to both NAS boxes (`ops/advance_db_nightly.sh`, 02:40, keep 14);
  `dropbox_exclude.sh` never deletes; gunicorn runs threaded workers with a 120s timeout;
  deploys wait for in-flight pipeline runs; `backfill.py` is dry-run by default and skips
  submissions already loaded; the Groq key never appears on a command line.

## Review pass (2026-09-14)

Report and decisions: `~/Documents/Claude/Handoffs/band-advance-review-2026-09-13.md`.
Built, staging-tested (70/70, `tools/staging/`) and deployed the same night. What changed:

- **Per-cell doc provenance** (`filed_docs.cells`, `docmerge.merge`). The registry now
  records what the pipeline wrote into each cell. A cell that still reads exactly that is
  the pipeline's to update (a returning band's prior-show pre-fill, a corrected monitor
  count, a cancelled act); anything a person typed is never touched and becomes a notice.
  Blank cells fill as before. This replaces "only empty cells get filled" (audit #1) with
  the same intent and none of the "band corrected a number, Brian gets an email" friction.
  Diffs are judged on whole tokens, so "5" inside "15 wedges" is a real diff.
- **One booking row per band/venue/date** (`uq_bookings_ident`; `insert_booking` upserts).
  The three lifecycle queries are `DISTINCT ON (s.id)` and the welcome loop de-dupes by
  show — a twin booking row used to send the welcome twice in one run.
- **Bad internal token is a hard 500** in `internal_send_outlook.json` (it used to answer
  200 with no `sent` key, which the app read as sent).
- **Auto-attach gate**: a submission attaches to the one unanswered booking only when the
  typed name plausibly IS that band (`advance_db.names_plausible`); otherwise
  `pending_pick` with no `responded_at`. The public form has a honeypot field.
- **Nightly full run** at 06:30 (`ops/advance-nightly-run.timer`) so holds and sheet edits
  land every day, not only on the next booking.
- **Reminders**: no band-facing tier fires within 48 hours of the welcome; bilingual series
  get the Spanish half on reminders too; the lifecycle renders welcomes into a private
  temp folder (a package run could wipe `tools/drafts/` mid-run).
- **Content**: blank schedule fields say "TBD — your day-of contact will confirm" (the
  FSQ-default times are gone); an all-cancelled bill's doc is renamed in place
  `<MMDDYY> CANCELLED - … Prod Adv.docx` and a cancelled act's column header reads
  "CANCELLED — <band>".
- **Day-before confirmation** (`tools/dayahead.py`, run inside the 9am lifecycle): every
  responded show playing tomorrow gets schedule, day-of contact, load-in/parking text and
  a recap; `dayahead_sent_at` / `dayahead_error` on the show.
- **"Needs you"**: `advance_db.needs_attention` feeds a panel at the top of the dashboard
  (`/dashboard/needs`) and a section at the top of the 7am digest. Doc notices, submission
  matches, set-start clashes, the 3-day unresponded list and thank-you failures are queued in
  `digest_items` and ride the digest instead of their own email. Send failures, holds, the
  watchdog and the Status Log alert stay real-time. A send failure already emailed in the
  last 7 days is suppressed (`send_failures.suppressed`).
- **Attachments**: every `_attachment*` file in a venue's Series Email Templates folder is
  attached (load-in doc + tech pack); `mailer.send(attachments=[...])`.
- **Regen serializes with package runs** (`regen_show` takes the `run_now` lock) — a submit
  during a run used to find "no event" and skip the doc.
- **Deploy guards**: both deploy scripts refuse unless `main` is checked out (`ADVANCE_DEPLOY_BRANCH` overrides). The `advance-system` branch and its `.worktrees/advance-system` checkout were merged into `main` and deleted 2026-09-14 (pipeline-fix) — the workspace is single-branch now.

## Provenance by artist + sheet removals (2026-09-16, audit root causes A and B)

Full record: `~/Documents/Claude/Handoffs/handoff-2026-09-17-band-advance-opus-fixes.md`.

**Removals reach the sheet.** `purge_show` and `merge_shows` write a `sheet_removals`
tombstone (venue, date, match_key). `run_now.one_pass` applies it first, before anything
reads the sheet: `append_bookings.py --remove` deletes the row (its `_advance_meta` entries
follow), `seed_bookings.py --removed` stamps it applied and renames a doc that lost its
last act to "PURGED - …" / "SUPERSEDED - …" in its own folder (never deleted; a digest line
says so). Until applied, `import_sheet.py` and `draft_emails.py` skip that ident, and neither
ever mints a show or artist for a past-dated row. A fresh `/booking` for the same ident
cancels a pending tombstone. Purge and merge kick a pipeline run immediately.

**A booking takes its show with it.** `update_booking` → `carry_show_with_booking`: a rename
renames the artist row in place when this is its only show (else moves the show to the
new-name artist, merging if that artist already has the date); a venue/date change moves the
show row. Stamps stay on the show, so no second welcome. `reregister_docs_for_move` moves
the filed-doc registry row when the old date is left with no show (the next filing pass
renames the file into the new month folder); `merge_shows` does the same, or retires the
old doc when the new date already has one. `edited_bookings._old_ident` reads every edit
since `bookings.synced_at`.

**Doc provenance is keyed by artist.** `filed_docs.columns` = `{column: artist_id}` the doc
was last written with (`daysheet.column_map`; legacy docs fall back to reading their own
header). Every artist cell is keyed `Section|a<artist_id>` in `filed_docs.cells`,
notices, frozen/force and "Keep doc"; `Section|colN` and `Section|<band>` are read as
aliases. When the fresh map differs, `docmerge._rehome_columns` moves each column's cell XML
(hand edits included) to the artist's new column before merging; a column its artist left
gets the template back. The act-name header stays positional (`Act names|colN`).

Other rules in the same pass: a pipeline value the fresh build no longer has goes back to
the template (cancelled/removed act; not Engineer/Consoles under a real artist). A pipeline
value somebody deleted is a "(cleared by hand)" notice, never a refill; "Keep doc" keeps it
empty. `_differs_meaningfully` compares tokens in order, checkbox glyphs included. A 4th act
is left off the doc with a "Bill size" notice. Consoles prints only under occupied columns and
never raises a notice. Notices label from the fresh header. Resolving a doc's last open
decision stamps `filed_docs.reviewed_at`; review mode counts from
`GREATEST(written_at, reviewed_at)`. Conflicted copies of a filed doc, `advance-list.xlsx` or
the Show Status Log raise a notice + digest line.

Staging: `run_tests_extra.py` x-d (reorder + 4th act), x-g (purge), x-j (rename), x-k (merge),
x-l (hand edit travels), x-m (cancel retracts), x-n (conflicted copy).

