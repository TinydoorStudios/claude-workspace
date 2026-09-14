# Context Handoff — 2026-09-03
**Session topic:** Band Advance pipeline — VM-native Dropbox + auto-run, day-sheet fix, US dates, short links, notify email, and date-driven send guardrails (T-21 initial / T-7 follow-up)
**Console / Venue:** N/A (venue-neutral pipeline; FSQ is the fully-wired venue)

---

## What We Did
Picked up the advance pipeline (`Code/BandInfoForm/`, branch `advance-system`) from yesterday's handoff and pushed it a long way toward production. Gave the VM its own Dropbox sync so the whole pipeline can run server-side (added a real "Run advance now" button on the `/booking` thank-you page). Fixed the day-sheet AUDIO row to show band names next to each slot in 3 clean lines, switched drafted-email dates to US format, shortened the prefill link in emails, wired a Gmail-draft test against a real artist, built a quick-glance notify email on every booking/submission, made form submissions auto-run the pipeline in the background, and — the big one — built date-driven send guardrails: the initial advance auto-drafts 21 days out from a show, and a follow-up auto-drafts if nothing's heard back by 7 days out. Also logged (not built) a TODO for a second Artist Directory wiki.

---

## Current State
- **Done:** VM-native Dropbox sync (headless dropboxd, selective-sync restricted to `Nyquist/` only) + working "Run advance now" button; day-sheet band names + 3-line AUDIO cell + blanked-unbooked-slots; US date format in email drafts; short `/s/<code>` links replacing the long signed token; quick-glance "Advance Notify" email on every booking/submission (n8n); `/submit` auto-runs the full pipeline in the background after every response; **Advance Lifecycle Check** (n8n, daily 9am) live and active — T-21 initial advance draft, T-7 follow-up draft, both Gmail-drafts-only with a "ready to send" summary email to Brian.
- **In progress:** nothing mid-build — this session's work is all committed and deployed.
- **Up next:** not yet directed by Brian. Candidates from the open-items list below — likely the Outlook send step, or other venues' email content.

---

## Key Decisions (Locked)
- **VM now runs its own Dropbox client**, selective-sync restricted to `Nyquist/` only — **nothing else in Brian's Dropbox may ever be touched from the VM side** (his explicit hard rule). Current exclude-list is a snapshot (188 items at setup), not structural — Brian explicitly accepted that risk for now rather than set up a dedicated Dropbox account scoped to just that folder ("it's your sandbox for now, I don't care about local VM disk, just never touch anything outside Nyquist").
- **Drafts-you-approve stays the rule**, confirmed again for the new T-21/T-7 automation: n8n creates real Gmail drafts (3CDCProduction@gmail.com), nothing auto-sends to artists. Brian explicitly asked for a reminder email when a draft is ready — built.
- **Follow-up trigger redefined**: date-driven off the **show date** (7 days out, no response), not days-since-email-sent. The old 10-day-since-sent workflow is deactivated in n8n, not deleted.
- **Internal service-to-service calls never go through a public hostname**: app→n8n uses n8n's `localhost:5678` (dodges Cloudflare's bot-blocking on the public tunnel); n8n→app uses the VM's **LAN IP** `192.168.200.84:8097`, not `localhost` (inside the n8n container, localhost is the container's own loopback, not the VM host's — opposite direction, opposite fix, same lesson).
- **"Email Sent" renamed "Advance Drafted"** throughout the status sheet — nothing tracks a real send yet (Outlook integration still not built), so the column now honestly reflects what actually happens today.

---

## Open Items
- **Outlook send step** — still not built. Drafts → Outlook drafts; a real send is what should eventually stamp a "sent" timestamp.
- **Other venues' email content** — only Fountain Square is wired in `tools/venue_email.py`.
- **Artist Directory wiki** — logged as an open item in `Live Sound KB/Wiki/active-projects.md` (opened 2026-09-02), not started. Design questions parked there: subdomain, access/gating, sync direction, stage-plot file handling.
- **Dropbox isolation hardening** — current setup is a snapshot exclude-list on Brian's own account. The bulletproof version (a dedicated Dropbox account sharing in only `Nyquist/`) was explicitly deferred by Brian.
- **Test Gmail drafts need manual cleanup** — a couple of clearly-labeled test/safe-to-delete drafts landed in the `3CDCProduction@gmail.com` Drafts folder during this session's testing. Claude has no access to that account to remove them — Brian needs to do it by hand.
- **Real Dropbox path** — the Mac pilot cockpit is still `~/Dropbox/Nyquist/`, a placeholder name/location per the 2026-09-01 handoff. Not yet finalized.

---

## Corrections / Watch-Outs
- **`with advance_db.get_conn() as conn` already commits on context exit.** Found the SAME bug pattern a second time (first was `insert_booking` on 2026-09-01, this time `seed_bookings.py --seed`) — a stray `conn.commit()` after the `with` block throws on the already-closed connection. Fixed by moving commit inside the `with`. Watch for this pattern in any new DB write handler.
- **Cloudflare's bot protection blocks server-to-server calls** through the public `*.tinydoorstudios.com` tunnel (Python's default User-Agent reads as a bot, gets a 403). Route same-VM service calls through localhost/LAN IP instead, never the public hostname.
- **n8n docker networking**: `localhost` inside the n8n container is the container's own loopback, not the VM host — use the VM's real LAN IP (`192.168.200.84`) for the n8n container to reach host-bound services like the Flask app.
- **`CREATE OR REPLACE VIEW` can't insert a new column ahead of existing ones** in Postgres — must `DROP VIEW` + `CREATE VIEW` instead when the column order changes.
- **Guardrail found in testing**: a late-booked show landing inside BOTH the 21-day and 7-day windows on day one must not get an initial advance AND a follow-up in the same automation run (reads as following up on something just sent). Fixed — `shows_due_for_followup` now requires `advance_draft_created_at` already set.
- **Linking a fresh Dropbox client to an existing large personal account syncs everything by default** — had to stop the daemon and exclude everything except the target folder immediately; even then, a brief race let some content download before the exclude list caught up (cleaned up after, nothing lost — just local VM disk cache, which Brian said he doesn't care about anyway).
- **Schedule Trigger n8n nodes can't be curl-tested directly** — to test a scheduled workflow end-to-end, swap in a temporary Webhook trigger node with identical downstream wiring, curl it, then swap back. Used this to validate both new n8n workflows this session.

---

## Resume Prompt

> Picking up on the **band advance pipeline** (`Code/BandInfoForm/`, branch `advance-system`). It's now running date-driven automation: n8n's **Advance Lifecycle Check** (daily 9am) auto-drafts the initial advance email 21 days out from a show and a follow-up if nothing's heard back by 7 days out — both land as real Gmail drafts (3CDCProduction@gmail.com) with a summary email to Brian, nothing auto-sends. The VM also runs its own Dropbox sync now (restricted to `~/Dropbox/Nyquist/` only — **never touch anything outside that folder from the VM side**), so the whole pipeline (seed bookings → build docs → file venue tree → fold status) can run server-side via the `/booking` page's "Run advance now" button or automatically whenever a band submits the advance form.
>
> Read `Code/BandInfoForm/ARCHITECTURE.md` + `Code/BandInfoForm/n8n/README.md` + the memory file `band-advance-form` first — the n8n README has the two networking gotchas (Cloudflare blocks public-tunnel server-to-server calls; the n8n container's `localhost` isn't the VM host's) that will bite again if not remembered.
>
> Likely next, ask Brian which: (1) the **Outlook send step** (drafts → Outlook, a real send stamps "sent"); (2) **other venues' email content** in `venue_email.py` (only FSQ is wired); (3) the **Artist Directory wiki** (logged as an open item, not started — see `Live Sound KB/Wiki/active-projects.md`). Also: a couple of test Gmail drafts are sitting in the `3CDCProduction@gmail.com` Drafts folder from this session's testing — worth reminding Brian to clear them, since Claude can't reach that account.
