# 3CDC Band Advance System

Started as a blanket band advance / show-details intake form; now the front end of a full
advance pipeline — intake form, a Postgres database of every response, returning-artist
detection, email drafting, and doc auto-fill. Venue-neutral, no login for bands, stage plot
uploadable **or** described/linked.

**Read `ARCHITECTURE.md` for the full design and `MORNING-STATUS.md` for current state.**

## Live

- Public form: **https://advance.tinydoorstudios.com** (also linked on the TDS dashboard)
- Host: n8n VM `192.168.200.84`, deployed at `/opt/band-advance/`
- Service: systemd **`band-advance`** (gunicorn, `0.0.0.0:8097`, auto-restart)
- Database: `advance-db` docker container, `127.0.0.1:5433` (dedicated Postgres, isolated from n8n)
- Search (staff, passcode `lockdown`): https://advance.tinydoorstudios.com/search

## Layout

```
app/        Flask app (form, prefill, gated search) + advance_db.py + forms_config.py
db/         docker-compose.yml + schema.sql for the dedicated Postgres
tools/      draft_emails.py · docfill.py · backfill.py + templates + example list
```

## Redeploy

Edit under `app/` or `tools/`, then run `deploy_app.command` (ships app + tools, restarts).
Database, env files, and the systemd unit are one-time setup — see ARCHITECTURE.md.

## Design notes

- One `--gap` CSS variable drives even spacing; the "split snake" question only appears when
  "bringing your own IEMs" = Yes.
- All copy says **3CDC**, never FSQ (except the venue dropdown option).
- Submission is saved to disk first, then Postgres best-effort — the form can't break on the DB.
- Band identity: exact name stored verbatim; a generated `match_key` makes matching
  case/space-insensitive so a band never splits into duplicates.

## `_superseded/`

First-approach dead ends: Google Apps Script (`build_form.gs` — Google Forms upload needs a
login) and the n8n Form Trigger workflow (couldn't do even spacing / inline conditionals).
