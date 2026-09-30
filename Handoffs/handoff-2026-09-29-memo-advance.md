# Context Handoff — 2026-09-29
**Session topic:** Memorial Hall advance: new doc, form, filing, email ladder, doc-ingest workflow, first real show (A Man Named Cash)
**Console / Venue:** Memorial Hall (DiGiCo Q225) · Code/BandInfoForm band-advance app on the n8n VM

---

## What We Did
We merged the two old Memo advance docs (the 2018 "Memo Production Advance - BLANK" and the monthly "MEMO Adv -") into one branded, one-page Prod Adv. It comes in 1-artist and 2-artist layouts. We built Memo its own advance form with multi-file uploads, staff-only sections and FSQ-style follow-up questions, plus the doc filer. Both are wired into the existing booking, dashboard and lifecycle pipeline and deployed live. We then ran the first real show through it. A Man Named Cash (10/16/26) was booked with no emails, and its advance was filled from the redlined riders, the stage plot and the cost model.

---

## Current State
- **Done (all live, last deploy `5e6009d`):**
  - **Code:** `app/memo_fields.py` is the one field spec. The form is `templates/memo_form.html`. `/memo/submit` handles saves. `tools/memo_doc.py` + `tools/build_memo_template.py` build and file the doc.
  - **Filing:** each show gets a folder `3CDC Memorial Hall/<MM.YYYY> MEMO/<MM.DD.YY> <Event>/MEMO Adv - <Event>.docx`. Uploads are renamed `<MM.DD.YY> <Act> Stage Plot / Input List / Tech Rider / Hospitality Rider / Lighting Plot and Notes / Video Projection Content`; "Anything else" keeps its own name.
  - **Many hands:** each save is a new submission; merge runs oldest→newest and a blank never erases. Staff saves apply as typed.
  - **Band changes:** a band answer that changes a settled field is HELD in `memo_decisions`. It shows on Doc Review (Keep current / Use new), in the dashboard count and as a staff-form banner, and triggers an internal email.
  - **Internal notes:** staff-only; prints on the doc, never on the band's form.
  - **Crew:** from the staffing sheet's Memo block. Mix→FOH/Mon, Tech→LX, Stagehand→2 slots, Stage Support→3 slots, Other→Additional Info. A "1" = TBD.
  - **Email ladder:** `advance_db.VENUE_LADDERS`. Memo welcomes at 30 days and chases at 15/10/7/5/3/2/1; other venues keep 21 and 10/7/3/1. **Memo is `paused`**: no automatic Memo emails. A Memo booking never triggers the on-demand email run.
  - **A Man Named Cash:** show 4654, booking 77, artist 8310. Booked straight into the DB (no staff summary email, no email run), marked manual advance. Answers are loaded and the doc is filed in `10.2026 MEMO/10.16.26 A Man Named Cash/` with the riders, stage plot and cost model. Backline shows as "ordered".
  - **Staging** (before the last deploy): test_memo 52/52, run_tests 158/158, run_tests_extra 620/620 (on an earlier build).
- **In progress:** nothing mid-flight.
- **Up next:** send A Man Named Cash its band link (not sent yet) and handle what comes back. After that, the Memo welcome email copy, then un-pausing Memo.

---

## Key Decisions (Locked)
- **Doc:** advance only; no post-show notes page and no video section. One page always; a filled 2-artist doc, or a text-heavy 1-artist doc, drops to a compact profile to fit.
- **Answers:** Yes/No only, never N/A.
  - Hospitality and Buyout: Yes + $ / No.
  - Parking: SP+ Lot (dashboard passes #) / Washington Park (passes #) / No.
  - Vehicles: counted by type (personal / sprinter / bus / semi).
  - Risers: 4'x8'x1', ask how many.
- **Schedule:** Set 1 and Set 2 each have start + end times. End of Show = Load-Out. Curfew = End of Show + 90 min.
- **Crew order:** FOH, Monitors, LX, Stage Hand x2, Video, Stage Support x3, Memo Lead (Joe · 216-288-7269) last.
- **Engineers:** Yes/House questions; the name box opens only on Yes. IEMs mirror FSQ (count → own rig → split).
- **Bill size:** a 2nd act booked under the same Event Name switches the doc to the 2-artist layout.
- **Redlined PDFs:** red wins over black. Extract → show Brian for approval → load as a staff save.
- **Backline:** once processed, mark "Backline ordered" on the advance and don't list it.
- **Money:** budgets and deals go only in Internal notes.
- **Band changes to settled answers:** asked, not applied. The system (Doc Review / dashboard / email) handles them, and Nyquist walks Brian through the open ones in chat.
- **No emails** for A Man Named Cash until Brian says so. Memo welcome stays paused.

---

## Open Items
- **Memo welcome email copy:** the `venue_email.VENUE_EMAIL["Memorial Hall"]` text is my DRAFT. Brian reviews it, then set `VENUE_LADDERS["Memorial Hall"]["paused"] = False`.
- **Ladder scope:** is the 30-day / 15-10-7-5-3-2-1 ladder Memo-only (as built) or every venue? Brian hasn't confirmed.
- **Band link for A Man Named Cash:** https://advance.tinydoorstudios.com/s/4EZjtgQF. Not sent; Brian decides when and how. The band still needs to answer settlement, photography, photo restrictions, runner and meet & greet.
- **A Man Named Cash crew:** LX and Video are TBD on the staffing sheet, and the 3rd stage support is blank.
- **Booking-page notice:** the staff "New booking" email still fires for every booking-page save. Consider a "don't send the booking summary" option before booking the next Memo show through the page.
- **Stray folder:** `Code/BandInfoForm/brian@192.168.200.84dvsrc/` is untracked junk in the repo from an earlier session. Not mine; leave or clean it with Brian's OK.

---

## Files Delivered This Session
| File | Format | Description |
|------|--------|-------------|
| Handoffs/memo-advance/Memo Show Advance - DRAFT.pdf | PDF | Blank 1-artist template (early version) |
| Handoffs/memo-advance/Memo Show Advance - 2 Artists - DRAFT.pdf | PDF | Blank 2-artist template (early version) |
| Handoffs/memo-advance/Holly Bowling - Memo Advance DRAFT.pdf/.docx | PDF/docx | Sample fill of the 10/4/26 show in the new layout |
| Handoffs/memo-advance/MEMO Adv - A Man Named Cash.pdf | PDF | Current filed advance for 10/16/26 |
| Handoffs/memo-advance/amn_answers.json, book_amn.py, render_holly.py | json/py | A Man Named Cash answers, the no-email booking script, the Holly sample builder |
| Dropbox: 10.2026 MEMO/10.16.26 A Man Named Cash/ | folder | Advance doc + both redlined riders, stage plot, cost model |

---

## Corrections / Watch-Outs
- **A booking-page save sends email.** Every save sends the staff "New booking" summary, and a booking inside the welcome window used to kick the on-demand email run, which sends OTHER shows' due emails. Paused venues no longer trigger the run; the summary still sends.
- **Loading a band's /s/ link counts as an open.** Resolving it stamps first-opened on the dashboard. Check with the /f/ token or the test client instead; I reset A Man Named Cash's stamp after tripping it.
- **Staging runs need a fresh clone.** Rerunning run_tests on a used staging DB gives false failures. Always `setup.sh ~/advsrc` first.
- **Memo files are 0 bytes on the Mac.** Dropbox online-only files read as empty; read Memo files on the VM (`/home/brian/Dropbox/...`).
- **Reaching the VM:** `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84`. If it times out, Tailscale on the Mac is down.
- **Word PDF export:** `tools/staging/pages.sh` exports through Microsoft Word and occasionally hangs; quitting Word fixes it.

---

## Resume Prompt
> Picking up from the 2026-09-29 session. The Memorial Hall advance system is built and live (last deploy 5e6009d): its own form, a one-page doc in 1 and 2-artist layouts, per-show Dropbox folders, band changes held for my decision, a staff-only Internal notes field, a 30-day welcome with 15/10/7/5/3/2/1 chases, and Memo welcome emails PAUSED.
> Our first real show, A Man Named Cash (Memo 10/16/26, show 4654), is booked with no emails sent and its advance is filled from my redlined riders. The doc is in Dropbox under 10.2026 MEMO/10.16.26 A Man Named Cash/. Its band link (/s/4EZjtgQF) has NOT been sent.
> Next: [send the link / ingest more docs for this or another Memo show / review the Memo welcome email copy].
> Rules: do not send any email unless I say so. Redlines (red) win. Show me every extraction for approval before loading it. Put budgets in Internal notes. Mark processed backline as "ordered". Ask me which answer remains when anything changes. Read Code/BandInfoForm/ARCHITECTURE.md (Memorial Hall section) and auto-memory memo-advance-doc before touching code, test in staging (fresh setup.sh) before deploying, and commit only your own paths.
