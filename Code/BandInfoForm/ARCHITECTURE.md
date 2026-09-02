# Band Advance System — Architecture

The advance pipeline: collect show details from artists, store them in one queryable
database, detect returning artists, draft their advance emails, and auto-fill the
standard show document. Built on the existing self-hosted Flask form.

## VM-native Dropbox sync (2026-09-02)

The n8n VM (192.168.200.84) runs its own headless Dropbox client (`~/.dropbox-dist/dropboxd`
+ `~/dropbox.py`, linked to Brian's account, **selective sync restricted to `Nyquist/`
only** — every other top-level item is excluded so the VM never holds Brian's other
Dropbox content locally). `~/Dropbox/Nyquist/` on the VM is the same live folder as
`~/Dropbox/Nyquist/` on the Mac; Dropbox propagates either side's writes to the other
in a few seconds. **Caveat:** the exclude list is a snapshot of what existed at setup
time (188 items) — a brand-new top-level item in Brian's Dropbox won't be auto-excluded.
Brian chose to accept that for now rather than set up a dedicated Dropbox account
scoped to only the Nyquist folder (the structurally bulletproof version); revisit if
he asks. **Rule: nothing outside `Nyquist/` is ever written or deleted from this side.**

This lets `tools/run_now.py` do the whole generate pipeline locally on the VM — seed
pending staff bookings into `advance-list.xlsx`, run `package_run.py`, overlay the
built tree into the live folder, fold status back into the sheet — with no SSH/scp/
rsync hop back to the Mac. `/booking/run` (gated) wraps it; the `/booking` thank-you
page has a **"Run advance now"** button that calls it and shows a result summary.
The Mac's `generate.command` still works (it uses its own separate upload path to
`lists/_current.xlsx`, not the Dropbox-synced copy) but is now largely redundant for
day-to-day use — the button/VM path is the live one.

## The front door: `Advancing/`

Day-to-day, Brian never opens this code tree. The production cockpit is the top-level
**`Advancing/`** folder (destined for a shared Dropbox — set `ADVANCE_ROOT` to point
there): he edits `advance-list.xlsx`, double-clicks `generate.command`, and each show
files into a venue archive at **`<VenueAbbr>/<Year>/<MM Month>/<MMDDYY> <Event> advance.docx`**
with email drafts in an `Email Drafts/` subfolder. Status folds back into the sheet as a
color-coded block (see below). `generate.command` uploads the sheet, runs
**`tools/package_run.py`** on the VM (rebuild events → fill each advance doc → draft each
email → emit `status.json` → assemble the venue tree under `_package/`), then rsyncs it
back **as an overlay (no --delete)** so the archive accumulates. Filing scheme (venue
abbreviations, month-folder format, filename) lives in `tools/fieldspec.py`. Generation
never marks anything sent — that moves to Outlook. See `Advancing/README.md`.

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
| Events | `tools/event.py` + `events`/`event_acts` tables | group up to 3 band submissions into opener/support/headliner slots |
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

The advance form is per-band; the 513 Airwaves day-sheet is per-event with three act
columns (Opener / Direct Support / Headliner) — and most bills are 1–2 acts. An
**event** groups band submissions into slots; `daysheet.py` then writes each act's
**band-provided** cells (Stage Plot, Engineer, Monitors/IEM, Scenic, Merch, Parking,
Drink Tix, Dressing-room tent, Backline, Contact) into that act's column of your real
template. The schedule and internal cells (PA, consoles, lead, "are we paying them?")
are left exactly as the template has them — those aren't band data, and you finish them.

```
python3 event.py create --name "513 Airwaves w/ Inhailer" --venue "Fountain Square" --date 2026-09-20
python3 event.py add-act --event 1 --slot headliner --artist "Buffalo Wabs and the Price Hill Hustle"
python3 event.py add-act --event 1 --slot opener    --artist "The Cincy Suns"
python3 daysheet.py --event 1        # -> tools/filled/<event>__daysheet.docx
```

Field→cell mapping lives in `daysheet.py::act_cells` — edit there to change what fills.

## Sending (the front half)

Decided: **Gmail now, Outlook in production.** `draft_emails.py` only writes drafts and
never sends. The send step is Nyquist-driven: hand over the batch, drafts are generated,
then the drafts are created as Gmail drafts (via the Gmail connector) for you to review
and send — approve-each, not auto. No throwaway Gmail-OAuth sender is built, since the
plan is to swap to Outlook; the interim path is drafts-you-approve.

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
