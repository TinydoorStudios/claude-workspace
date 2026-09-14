# Context Handoff — 2026-09-12
**Session topic:** RiffPay booking CSV → Band Advance pipeline (Washington Park), plus advance-doc/email/form fixes
**System:** Code/BandInfoForm/, branch `advance-system`, n8n VM (192.168.200.84), advance.tinydoorstudios.com

---

## What We Did
Wired the RiffPay web-portal booking export (`riffpay-bookings-2026-09-11.csv`) into the existing advance pipeline as a new intake source, scoped to Washington Park for now, and ran the 4 current WP shows through it (Neo Soul Nights 9/11 — Taymar Israel + Bravo; Blues & Brews 9/16 — Anything Blues; Blues & Brews 10/21 — Ricky Nye). Built `import_riffpay.py`, adapted the WP advance email copy from the FSQ block, made the advance **doc** carry a full schedule + consoles, pulled crew call + curfew from the tech staffing sheet, scoped the form-submit regen to one file, and ran an audit that fixed 5 more issues. All committed + pushed + deployed live.

Everything is drafts-only — **no auto-send** (Brian's standing call this session). The 4 WP advance emails are in the Production@3cdc.org Outlook Drafts folder.

---

## Current State

- **Done:** `import_riffpay.py` (filter WP + Confirmed + today-onward; series→stage; group by date+series; slots by set time; event name `Series - headliner`; schedule anchored on headliner; **seeds `bookings` rows** so a RiffPay show is a true booking entry). WP email copy live (`venue_email.py`). Schedule + Consoles now fill the advance doc. Crew call + curfew come from the staffing sheet (`staffing.event_times_for`, always PM). Form hides lighting/drum-riser for WP Porch/Bandstand and for **FSQ openers/direct-support** (headliner only). Monitor caps apply by series (Bandstand 4 / Porch 2). Stable doc filenames (fall back to series, not act list). Scoped submit regen (`regen_show.py`). Audit fixes #1/#2/#3/#5/#6. Consoles written across all 3 act columns.
- **In progress:** nothing half-done.
- **Up next:** nothing explicitly queued. Candidates Brian flagged but deferred are in Open Items.

Commits on `advance-system` (pushed): `dfafcb6` (RiffPay intake + WP pipeline + staffing + consoles + scoped regen + FSQ riser), `bce8140` (stable filenames), `7d67b05` (audit fixes + consoles-all-columns). Restore point tag from session start: **`restore-point-20260911-174839`** (covers tracked code only — `Advancing/` and `~/Dropbox/Nyquist/` are gitignored / not in the tag).

---

## Key Decisions (Locked)

- **RiffPay filter:** Location = Washington Park only (other sites later), Status = **Confirmed** only (supersedes the earlier "Completed"), date **≥ today** onward.
- **Series → stage (authoritative):** Neo Soul Nights = **Bandstand** (cap 4), Blues & Brews = **Porch** (cap 2). Series is the source of truth for WP location in `forms_config.SERIES_LOCATION` — the form derives location from series even when the per-show location is blank.
- **One event per night**, bands as acts; slots by set time (earliest = opener, latest = headliner). Event name = `<Series> - <headliner>`. Neo Soul's 5PM slot is a **DJ** — ignored for scheduling; the day anchors on the headliner.
- **Schedule, worked back from the headliner's set time:** crew call −2:00, load-in −1:00, soundcheck −0:30, set length 3h (end = +3:00), curfew = +1:00 after set. BUT crew call + curfew are **overridden by the staffing sheet** when present.
- **Staffing sheet Event cell** `<Event> (crew-curfew)` (e.g. `Jazz (3:30-10)`) → crew call + curfew, **always PM**, all sites (`staffing.event_times_for`). On a double-booked date, the row matching the show's series wins.
- **Consoles:** FSQ FOH = DiGiCo Quantum 225; M32 monitors listed by default **only for 513 Airwaves & Salsa**. WP Main Stage FOH = M32. WP Porch/Bandstand = **M32R**. Monitors added by hand otherwise. Console shows in all 3 act columns.
- **Email subject = series only** (not `Series - headliner`), so an opener doesn't get the headliner's name. Archive **filename** keeps `Series - headliner`; filename falls back to series when the event has no name (no more orphan duplicates when a bill grows).
- **FSQ openers/direct-support:** no drum-riser question on their form (headliner only).
- **No auto-send.** Drafts only until further notice. Everything routes to the Outlook Drafts folder via the n8n Graph connector; Brian sends by hand.

---

## Open Items

- **Advance email curfew** still uses the computed value (start + 4:00), not the staffing sheet — so on a date where they differ, the doc and email disagree. Deferred; Brian can say the word to wire it to staffing.
- **Booking entry** (staff hub) still triggers a **full-tree `package_run`** that restamps every event's doc — only the *form-submit* path was scoped to one file. Deferred.
- **Audit finding #4 (4+ band night):** `import_riffpay` maps >3 acts to multiple `direct_support` slots, which collide in the 3-slot doc/DB model. Explicitly deferred — not triggered by the current WP+Confirmed filter.
- **Operational wiring unsettled:** how/where `import_riffpay` runs in production (schedule? staff-hub button? manual?) — it must run **on the VM** to seed bookings (needs the DB), and a `package_run`/`import_sheet` must run afterward to rebuild events before docs reflect changes. Brian hasn't picked the trigger.
- **Auto-send design** (draft at booking, auto-send at T-21, kill on form submit) is fully designed but NOT built — parked until Brian lifts the drafts-only hold.

---

## Corrections / Watch-Outs

- **`import_riffpay` must run on the VM to seed bookings** (DB is 127.0.0.1:5433 on the VM, unreachable from the Mac). Run from the Mac = sheet only, no bookings → degraded lifecycle emails. Use `--no-db` to intentionally skip.
- **After any RiffPay import, events need a rebuild** (`import_sheet`/`package_run`) before docs change — seeding bookings + writing the sheet alone doesn't rebuild the event model.
- **Don't call `daysheet.fill()`/`regen_show` expecting schedule times without the event having details** — the doc's crew schedule fills from `event.details` (load_in/soundcheck/start/end/curfew) + staffing; a bare event with no details = blank times.
- **`~/Dropbox/Nyquist/` is the live archive** (`ADVANCE_ROOT`), synced Mac↔VM. A full `package_run` overlays ALL event docs there (restamps everything) — that's expected, not a bug. Stage plots (band-provided) are never regenerated.
- **VM/Tailscale jump (`tds`) dropped mid-session once** — all deploys go through it; if SSH times out at banner exchange, it's the jump, retry later.
- **Empty/duplicate advance docs**: a doc exists for a band before they submit (skeleton from the booking); the form fills on submit. Duplicate filenames came from act-name-derived names drifting as a bill grew — fixed via series-fallback naming.

---

## Resume Prompt

> Picking up from the 2026-09-12 session on the Band Advance pipeline (`Code/BandInfoForm/`, branch `advance-system`, deployed to the n8n VM). We integrated the RiffPay booking CSV as a WP intake source (`import_riffpay.py` — filters WP + Confirmed + today-onward, seeds `bookings` rows so it's a true booking entry), and fixed a batch of advance-doc/email/form issues: staffing-sheet crew/curfew (always PM), consoles by rule across all 3 act columns, series-only email subjects, series-derived WP location + monitor caps, FSQ opener/direct-support hides the drum-riser question, stable doc filenames, and scoped form-submit regeneration. All committed + pushed (`dfafcb6`, `bce8140`, `7d67b05`) and live on the VM. Still drafts-only — no auto-send.
>
> Likely next: either (a) wire the advance **email curfew** to the staffing sheet (currently still computed start+4h), (b) scope the **booking-entry** path to regenerate one doc instead of the whole tree, or (c) decide how `import_riffpay` runs in production (it must run on the VM to seed bookings, and needs a `package_run` after to rebuild events). Confirm which before starting.
>
> Key context not in standing memory: series→stage is locked (Neo Soul = Bandstand cap 4, Blues & Brews = Porch cap 2); the staffing sheet's Event cell `Name (crew-curfew)` drives crew call + curfew, always PM; WP Porch/Bandstand console = M32R; restore point tag `restore-point-20260911-174839` covers tracked code only.
