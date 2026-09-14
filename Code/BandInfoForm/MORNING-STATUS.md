# Morning status — Band Advance framework (built overnight 2026-08-31)

The framework is built, deployed, and tested end to end on the VM. The live form your
boss is evaluating was never at risk — every DB write is best-effort behind the existing
disk save. The database is currently **empty and pristine** (I cleaned up all test data
after verifying).

## What's working right now

| Piece | Status | Proof |
|---|---|---|
| Isolated Postgres (`advance-db`, :5433) | live, healthy | 4 tables, own container, n8n untouched |
| Form → database on submit | working | test submissions landed in all 4 tables |
| Disk-first reliability | working | `/healthz` reports form + db; DB failure can't break the form |
| Case-insensitive band matching | working | mixed-case + extra-spaces resubmit hit the same artist, no duplicate; exact name preserved |
| Returning-artist detection (6-mo, cross-venue) | working | past show → next batch flagged RETURNING |
| Email drafting (NEW vs RETURNING) | working | drafts written to `tools/drafts/`, **nothing sent** |
| Prefilled returning-artist link (`/f/<token>`) | working | opens last submission pre-filled, date blank |
| Gated search + artist detail (`/search`) | working | passcode `lockdown`, file downloads, Eastern timestamps |
| Doc-fill (submission → filled .docx) | working | filled a full sheet from a submission |
| Venue/series form variants | scaffolded | one engine; `forms_config.py` ready for per-series questions |

## Decisions I made autonomously (change any of these)

- **Separate database container** rather than adding tables to n8n's Postgres — keeps this
  fully isolated from the just-upgraded n8n stack. Same VM, reuses the pg16 image (no pull).
- **Search is gated with the `lockdown` passcode**; the form stays fully open. Artist data
  should not be public, so I locked the data views but left the form frictionless.
- **Nothing sends.** The email tool only drafts. Sending stays a human step until you decide
  on send-as (your Gmail vs a system alias) and approve-each vs auto.
- **The form's questions are unchanged** — I didn't touch the copy the boss is reviewing.

## What needs you (the reasons I didn't just do it)

1. **The real standard DOC.** Doc-fill runs against a stand-in template I generated. Drop your
   real show DOC at `tools/doc_templates/advance_sheet.docx` with `{{ placeholders }}` — run
   `docfill.py --fields` for the exact names. Then it fills your real document.
2. **Email send path.** Decide send-as identity + approve-each vs auto, then I wire the send
   step (Gmail) onto the existing drafts.
3. **Contact name/email on the form.** The form currently collects phone only; email comes
   from your advance list. If you want the artist to confirm their own email/contact name,
   that's a small form add — your call, since it changes the boss-eval form.
4. **Monday mirror + Slack ping.** Code path is ready (`ADVANCE_SLACK_WEBHOOK` env for Slack).
   I didn't create a Monday board or post to Slack without your go.

## Still parked (from the plan, untouched)

- Phase 6 search UI polish (basic version is live and gated).
- NAS file sync for uploads (currently on the VM disk + DB-linked).
- PG16 "borrowed time" note is n8n's concern; this app's DB is a separate, fine pg16.

## Credentials (also in TDS_Credentials_CheatSheet.md)

- advance-db: `advance` / (password in `/opt/band-advance/advance.env` and the cheat sheet)
- Search passcode: `lockdown`
