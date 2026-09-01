# Band Advance System — Architecture

The advance pipeline: collect show details from artists, store them in one queryable
database, detect returning artists, draft their advance emails, and auto-fill the
standard show document. Built on the existing self-hosted Flask form.

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
| Doc fill | `tools/docfill.py` | submission → filled `.docx` (docxtpl) |
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
