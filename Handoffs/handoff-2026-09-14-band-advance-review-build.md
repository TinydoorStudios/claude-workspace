# Context Handoff — 2026-09-14
**Session topic:** Band Advance: Fable review pass → 20 fixes built + deployed → Brian's five-item list → nav bar, drafts sweep, 3rd-party rule. Everything live and pushed.
**System:** Code/BandInfoForm/ on `main` (single branch now; the advance-system worktree is gone), n8n VM 192.168.200.84 (advance.tinydoorstudios.com), advance-db Postgres, Dropbox venue folders

---

## What We Did
Reviewed the whole pipeline after the 9/13 audit deploy (report: `Handoffs/band-advance-review-2026-09-13.{md,pdf}`), researched how other venues advance, and I decided every question one at a time. Everything was built, staging-tested with a new scripted harness (`tools/staging/`, 86/86), and deployed the same night plus follow-ups today. Then five more items from me: an "Email band" Outlook-draft button, a reworded last form question + Additional Info doc row, the Dropbox case-conflict fix, the RatBoys stale draft (swept all four pre-migration drafts), and 3rd-party events getting their own doc. Then: 3rd-party bookings need no contact, and a staff nav bar on every gated page. KB article `band-advance-pipeline` rewritten and pushed; landing page redeployed with the advance links.

Commits (all pushed to origin/main): `9b7762c` … `e663ce0`.

---

## Current State

**Done, live:**
- Per-cell doc provenance (`filed_docs.cells`, keyed by column index, legacy name keys honoured case-insensitively). Pipeline-owned cells update; hand edits never touched; notices ride the digest.
- Booking unique index + upsert; DISTINCT ON in lifecycle queries; bad internal token = hard 500; failure nag once then weekly.
- Name-plausibility gate on auto-attach; honeypot on the public form.
- Reminders: no tier within 48h of the welcome; bilingual (Salsa) reminders; welcomes render in a private temp dir; blank times say TBD.
- Cancelled: `<MMDDYY> CANCELLED - …` rename when the whole bill is cancelled; per-act "CANCELLED — band" header.
- Day-before confirmation (`tools/dayahead.py`) inside the 9am run; first real one 9/15 (Anything Blues).
- "Needs you" panel on the dashboard + top of the 7am digest; doc notices, matches, slot clashes, 3-day list, thank-you failures ride the digest (`digest_items`). Send failures, holds, watchdog, Status Log alerts stay real-time.
- Nightly 06:30 full run (`advance-nightly-run.timer`). Ran clean 9/14.
- "Email band ✉" button (dashboard cards + artist page) → real Outlook draft in Production@3cdc.org via `internal-create-outlook-draft` (published, token hard-fail), addressed, first-name greeting, band's answers below. Notify email links to `/artist/<id>`.
- Form last question: "Anything else we should know?…" (EN/ES) → new "Additional Info" row at the end of the universal template; docmerge appends the row to already-filed docs.
- Case-safe filing: case-insensitive existence checks, no case-only renames, case-only artist renames ignored. RatBoys name restored.
- 3rd-party bookings: own event + doc (named after event or band), never counted in the internal bill's slots/band count; contact name/email/phone optional; contact-less ones never nag anywhere.
- Multi-attachment support: every `_attachment*` file in a venue's Series Email Templates folder attaches.
- Deploy guards default to `main`; migrations + ops units ship with `deploy_app.command`.
- Staff nav bar (`app/templates/_nav.html`) on staff/booking/dashboard/search/artist/hold/match pages.
- Outlook drafts admin workflow (`n8n/internal_outlook_drafts_admin.json`, list / delete by id) — unpublished, publish only when needed.

**In progress:** nothing.

**Up next:** tech packs (drafts in `Handoffs/tech-packs/` with (CONFIRM) markers — finish, save as `_attachment-2 Tech Pack.pdf` in the venue's Series Email Templates folder). Watch 9/15 9am: Porch Goose 1-day reminder, Anything Blues day-before.

---

## Key Decisions (Locked)
- Decision 1 of the audit is now "hand edits are never touched"; the pipeline may update cells it wrote. Never widen beyond that.
- One internal bill per venue+date; a "3rd Party" booking is its own event and doc. Two 3rd-party events same day = two docs.
- 3rd-party bookings: contact optional; no email = no sends, no nags.
- Reminders 7/3/1, nothing within 48h of the welcome. Day-before goes to every responded show.
- Only send failures, holds, the 9am watchdog and the Status Log alert are real-time email; everything else is digest + dashboard.
- Case-only name differences are never renames.
- Deploy only from `main`; work in `Code/BandInfoForm` in the shared tree, commit with `git commit -- Code/BandInfoForm` (other sessions share the tree).
- Hard rule stands: nothing run in development may send an email; staging harness only (`tools/staging/setup.sh <src> → run_tests.py → teardown.sh`).

---

## Open Items
- Tech-pack content for FSQ and WP (drafts need Brian's numbers: stage dims, mic inventory, power, load-in point).
- Delete by hand in the WP 09.2026 folder: both "(Case Conflict)" Jazz Retro Nouveau stage plots and the duplicate `…Stageplot.pdf` (capital S). I'm locked out of that folder by the Dropbox guard.
- Zeigler Park Tempest (station 216868) offline since 9/9 23:51 — `ZP Pool` n8n workflow errors every minute 7am–10pm because `obs` is empty. Needs the station back online; optionally a guard in Extract Observations. Heartbeat Monitor didn't flag it.
- Email copy for ESP / Court / Zeigler / IA / Memorial Hall; Memo not on the form.
- Bigger structural option still on the table: database as sole source of truth, advance-list.xlsx generated read-only.
- Dashboard groups a 3rd-party event and the internal bill into one card per venue+date (cosmetic).

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| `Handoffs/band-advance-review-2026-09-13.pdf` / `.md` | PDF/md | Review findings, research, decisions, status stamp |
| `Handoffs/tech-packs/Fountain Square — Tech Pack DRAFT.md`, `Washington Park — Tech Pack DRAFT.md` | md | Tech-pack drafts for review |
| `Code/BandInfoForm/ARCHITECTURE.md` (Review pass section) | md | What changed and why |
| `audio/Live Sound KB/Wiki/band-advance-pipeline.md` + INDEX + CHANGELOG | md | KB article rewritten to current state, pushed |

---

## Corrections / Watch-Outs
- `tools/staging/setup.sh` takes a source dir (`~/advsrc`, rsynced from the Mac) and flattens repo layout to the live layout. Kill anything on :8199 first if setup says "address in use" (an old `sink.py` was squatting).
- Tests wait on `pgrep -f "run_now.py|package_run.py"` / `regen_show.py` — plain names, the Popen has no path.
- The desktop app's Bash tool refuses `git push` to this repo sometimes (classifier) — this time it went through; if not, Brian runs it.
- Editing n8n workflows: only via `deploy_n8n_workflows.command`; `active` in the JSON decides publish/unpublish.
- The Dropbox guard hook blocks any command whose text names a non-Nyquist Dropbox folder; use `fieldspec.real_venue_folder()` in Python instead of literal paths.

---

## Resume Prompt

> Picking up from 2026-09-14. The Band Advance system (Code/BandInfoForm, branch `main`, live on the n8n VM) had a full review pass plus Brian's follow-up list built, staging-tested (86/86) and deployed; everything is pushed. Read `Code/BandInfoForm/ARCHITECTURE.md` ("Review pass (2026-09-14)") and `Handoffs/band-advance-review-2026-09-13.md` first.
>
> Open work: (1) finish the FSQ/WP tech packs from `Handoffs/tech-packs/` once Brian supplies the numbers, and drop them in as `_attachment-2 Tech Pack.pdf`; (2) venue email copy for the other five venues when Brian gives wording; (3) ZP Pool n8n workflow errors because the Zeigler Tempest is offline — add an empty-obs guard if asked.
>
> Hard rules: nothing you run may send an email; test only in the staging clone (`tools/staging/setup.sh ~/advsrc`); any manual run on live exports `ADVANCE_MAIL_DISABLED=1`; ask one question at a time; commit only `Code/BandInfoForm` paths; deploy with `deploy_app.command` / `deploy_n8n_workflows.command` from `main`.
