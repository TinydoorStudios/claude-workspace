# Context Handoff — 2026-09-12
**Session topic:** Band Advance system — Dropbox migration/wiring, VM infra fixes, live dashboard, and a string of feature/bug fixes
**System:** Code/BandInfoForm/, branch `advance-system`, n8n VM (192.168.200.84), advance.tinydoorstudios.com + tinydoorstudios.com

---

## What We Did

Long session, several distinct chunks, all finished and deployed:

1. **Migrated the whole advance pipeline off the Nyquist-only Dropbox scheme onto the real, shared 3CDC venue folders** (`3CDC Fountain Square/09.2026 FSQ/`, etc.), matching the naming convention Brian and the rest of the production team already hand-type into those folders. Rewrote `fieldspec.py`/`package_run.py`/`run_now.py`/`daysheet.py`/`regen_show.py`/`extract_advance_recap.py` to match. Migrated the existing Sept/Oct show archive by hand, resolved 8 duplicate docs where a hand-typed one already existed (pipeline wins, per Brian's call).
2. **Widened + then had to firefight the VM's Dropbox sync.** Added the 7 real venue folders to the VM's selective sync (was Nyquist-only) — this blew the VM's 40G disk to 98% (bad capacity estimate: the Mac's Dropbox client uses online-only placeholders, the VM's headless one doesn't). Fixed by excluding legacy bulk subfolders (ARCHIVE OLD DATES / Box Office / ZARCHIVE / OLD FILES) and, when Dropbox's own local `.dropbox.cache` kept re-ballooning, installed a permanent systemd timer (`dropbox-cache-guard`, every 2 min) that clears it whenever disk crosses 85%.
3. **Grew the VM's disk 40G → 200G** at the Proxmox host level (`qm resize` + guest `growpart`/`resize2fs`, live, no reboot) — real headroom now (138G free), and ~880G more available on the physical drive if ever needed again.
4. **Rebuilt the Universal Show Advance template's SCHEDULE table** to Brian's exact 13-row spec (Crew Call through Curfew), then tightened margins/spacing to fit back on one page after the edit pushed it to two.
5. **Locked 513 Airwaves' crew schedule permanently** (3:00pm Crew Call → 11:00pm Curfew, never changes) via the existing per-series lock file mechanism — had to add a prefix-match fallback in `venue_email.py` since the DB's `series` field carries that week's guest act name, so it never exact-matched.
6. **Built a live dashboard** at `advance.tinydoorstudios.com/dashboard` — sites, bands, pipeline status, today-forward only, auto-refreshing, grouped by day with color-coded status pills. Linked from tinydoorstudios.com's command center, which also got its SERVICES panel reorganized into sections and then rebuilt as a properly column-aligned table after Brian called the first pass chaotic.
7. **Added a second gate passcode** (`1313`, alongside `lockdown`) for advance.tinydoorstudios.com.
8. **Built Outlook-drafts cleanup**: when a band submits their form, a new n8n workflow (`internal_delete_outlook_drafts.json`) finds and deletes any stale draft/follow-up sitting in Production@3cdc.org's Drafts folder for them (matched by the artist's own known email, not whatever the band typed).
9. **Fixed FSQ's Load-In & Parking email copy** and built a general **per-venue email attachment mechanism** — drop a file named `_attachment.<ext>` in a venue's `Series Email Templates/<Venue>/` folder and it auto-attaches to every advance + follow-up email for that venue. FSQ's real load-in PDF is in place now, verified byte-for-byte through a live Graph test.
10. **Found and fixed a real bug**: every new booking was wrongly emailing "Advance form completed" instead of "New booking" — a dict-key collision (the booking form's own "Event Type" field shared the key `event_type` with the notify function's own event-type tag, and clobbered it). Deterministic, hit every booking, not intermittent. Fixed and verified against a real n8n execution.
11. **Wired Drink Tix = 2× band/crew headcount**, computed automatically in `daysheet.py`, applies to every band at every venue — verified live.
12. Renamed the landing page's Band Advance links (Staff Hub → **Band Advancing**, Live Dashboard → **Advancing Status**) and removed New Booking from that list per Brian's ask.

---

## Current State

Everything above is done, deployed, and verified live — nothing half-finished.

- **Done:** all 12 items above.
- **In progress:** nothing.
- **Up next:** nothing explicitly queued by Brian. 13 commits this session on `advance-system`, all pushed to origin (not merged to `main`).

---

## Key Decisions (Locked)

- **Real filing scheme:** `~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/<MMDDYY> <Event> Prod Adv.docx` (and `... Stageplot.<ext>`) — venue codes FSQ/WP/MEMO/ESP/CSP/IA/ZP. `fieldspec.py` carries both this (`real_venue_folder`/`real_month_folder`) and the old Nyquist-drafts-only scheme (`venue_abbr`/`month_folder`, unchanged) — don't conflate them.
- **Email drafts stay in Nyquist** (`Nyquist/<VenueAbbr>/<Year>/<MM Month>/Email Drafts/`) — no analog in the real folders, deliberately not migrated there.
- **VM Dropbox sync scope:** Nyquist + the 7 real `3CDC <Venue>` folders, minus 4 excluded legacy-bulk subfolders (see above). `ops/dropbox_exclude.sh` is the checked-in reference for the keep-list; `ops/dropbox_cache_guard.sh` + the two systemd unit files are the permanent disk guard.
- **513 Airwaves schedule is fixed, not computed** — 3:00p/4:30p/5:00p/6:00p/6:30p/7:00p/7:45p/8:00p/8:45p/9:00p/10:00p/10:00p/11:00p across the 13 rows, every week, regardless of who else is on the bill.
- **Drink Tix is always 2× Number of Performers** — never band- or staff-entered, computed at fill time, blank if headcount isn't on file.
- **Per-venue email attachments** are venue-wide, not per-series — one `_attachment.<ext>` file covers every email for that venue.
- **Gate passcodes:** `lockdown` and `1313` both work, same access level.
- **Outlook-drafts cleanup matches by the artist's stored email** (`artists.last_email`), never by subject (subjects are series-based, never the band's name) and never by whatever email the band typed into their own submission.

---

## Open Items

None outstanding from this session. Two things worth knowing rather than acting on:
- The root cause of `.dropbox.cache` ballooning was mitigated (systemd guard), not fully diagnosed — if it keeps recurring long after the initial sync settles, worth a closer look.
- Only Fountain Square has a `_attachment` file in place; the mechanism is ready for any other venue whenever Brian wants one there.

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| 3CDC Universal Show Advance.docx | docx | The blank advance template — sent twice (after the SCHEDULE table rebuild, and again after the one-page fix) |

---

## Corrections / Watch-Outs

- Initial capacity estimate for the VM's Dropbox sync was wrong (undercounted by ~4x) because the Mac's Dropbox client uses online-only placeholders and the VM's headless one doesn't — don't size a headless Linux Dropbox sync off a Mac's local folder size again.
- During the file migration, a move script that was supposed to skip Word `~$` lock files didn't, and a blanket cleanup pass then deleted 2 pre-existing lock files that weren't part of the migration — verified harmless (real docs untouched, nobody had them open) but worth being more surgical with cleanup globs next time.
- Some VM-touching Bash commands (SSH into the VM, some git commits) got blocked by the permission classifier mid-session and needed either a retry or an explicit go-ahead from Brian — not a code issue, just expect it on infra work.

---

## Resume Prompt

> Picking up from the 2026-09-12 session on the Band Advance system (`Code/BandInfoForm/`, branch `advance-system`, deployed to the n8n VM at 192.168.200.84). That session migrated the whole pipeline onto the real 3CDC Dropbox venue folders, fixed a VM disk crisis (grew it 40G→200G, added a permanent systemd guard against Dropbox's local cache filling it again), rebuilt the advance doc template's SCHEDULE table, locked 513 Airwaves' crew schedule, built a live dashboard at advance.tinydoorstudios.com/dashboard, added Outlook-drafts cleanup on band submission, wired per-venue email attachments (FSQ's load-in PDF is live), fixed a real bug where every new booking wrongly emailed as if a band had submitted, and wired Drink Tix to auto-compute as 2× headcount. Everything from that session is done, deployed, and verified — nothing was left half-finished. 13 commits pushed to `advance-system`, not yet merged to `main`.
>
> No specific next task was queued. If Brian doesn't have something new, ask what he wants to work on rather than assuming a follow-up to any of the above.
>
> Key context not necessarily in standing memory yet: the real Dropbox filing scheme (`3CDC <Venue>/MM.YYYY <Code>/<MMDDYY> <Event> Prod Adv.docx`), the VM's Dropbox sync scope (Nyquist + 7 real venue folders, minus 4 excluded legacy-bulk subfolders), the `dropbox-cache-guard` systemd timer, 513 Airwaves' fixed schedule, and the per-venue `_attachment.<ext>` email-attachment convention.
