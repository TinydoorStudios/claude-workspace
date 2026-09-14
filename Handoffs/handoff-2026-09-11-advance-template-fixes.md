# Context Handoff — 2026-09-11
**Session topic:** Band Advance pipeline — Universal Show Advance template fixes
**System:** Code/BandInfoForm/, branch `advance-system`, n8n VM (192.168.200.84)

---

## What We Did
Fixed three gaps on the "3CDC Universal Show Advance.docx" template (the ONE doc `daysheet.py` fills for every venue/band-count) that Brian flagged after reviewing a real filed advance: no dedicated area for IEM count or performer count, no dedicated Lighting Notes area, and the Stage Plot cell had silently reverted from a real hyperlink to plain "(file on record)" text. All three are fixed, deployed, and verified end to end against a real live show — Tailgate @ Fountain Square, 9/13/2026, headliner The Closers.

Also caught and fixed a naming gap in that same real event: its filename never picked up the band name because the advance-list sheet's Event Name cell just said "Tailgate" — unlike every other real show in the sheet, where Event Name already IS the band name.

---

## Current State

**Done:**
- "Number of IEMs" and "Number of Performers" rows added to the Universal template (were previously blended into Input Notes text / hijacking the Drink Tix row respectively). `daysheet.py` and `fieldspec.py` updated to match.
- "Lighting Notes" row added (was folded into Input Notes). `daysheet.py` updated.
- Stage Plot hyperlink regression root-caused and fixed — not a real pipeline bug, see Corrections below.
- Tailgate's Event Name fixed in `advance-list.xlsx` and the `events` table: "Tailgate" → "Tailgate w The Closers", matching the sheet's existing convention (e.g. "513 Airwaves w Inhaler Radio"). Filed `.docx`, stage plot `.pdf`, and email draft `.md` all renamed to match.
- Template mirrored to `Blank Advances/`, Desktop, and the repo. Code deployed to the VM via `deploy_app.command`.
- Two commits pushed to `advance-system`: `5a0aebc` (IEM/performer rows) and `0d792de` (Lighting Notes + stage plot fix).

**In progress:** Nothing left hanging — both fixes verified against the real filed doc.

**Up next:** Nothing explicit from Brian. Worth knowing: the `iem_count` field is brand-new on the intake form as of this session, so no real band has answered it live yet — everything verified so far used a manual `sheet_fields` override (1 monitor / 3 IEMs) Brian gave directly for The Closers, not a live form submission. First real band submission with that field will be the first true end-to-end test.

---

## Key Decisions (Locked)

- **"The generic advance form" = the 3CDC Universal Show Advance.docx template** (the doc `daysheet.py` fills with real band data) — NOT `form.html`, the band-facing web intake form. This was a repeated point of confusion earlier in the session; now settled.
- Drink Tix row is genuinely blank/manual again — it was quietly carrying performer count as a hack before "Number of Performers" existed.
- Stage plot files are named after the **band**, not the event (`091326 The Closers stageplot.pdf`), even when the event's own name includes the band (`091326 Tailgate w The Closers advance.docx`) — these two follow different naming rules, don't try to make them match.
- Event Name in `advance-list.xlsx` should be (or include) the band name for every real show — that's the existing convention across every other filed event; "Tailgate" alone was an anomaly for an internal event.
- New template rows all cloned from "Monitors" (a clean plain-text row), never from "IEMs" — cloning a checkbox row drags its `<w:sdt>` content controls along as orphaned dead structure.

---

## Open Items

- The "091126 Sylmar stageplot.pdf" filename doesn't match its event's name ("513 Airwaves w Inhaler Radio") — noticed in passing while checking naming precedent, not investigated. Could be a genuinely different band name on that bill, or could be the same kind of naming slip as Tailgate. Worth a look if it comes up.
- No real band has submitted the new `iem_count` question yet — flag it if the first live submission with that field looks off.

---

## Corrections / Watch-Outs

- **Never call `daysheet.fill()` directly for testing without passing `stageplot_names`.** Only `package_run.py`'s real pipeline builds that mapping (from the uploaded file, copied and renamed next to the advance doc). Calling `fill()` ad hoc without it silently degrades the Stage Plot cell to plain "(file on record)" text with no link — that's what happened to The Closers' doc during this session's manual verification, not a regression in the real pipeline.
- Don't rename a stage plot PDF to match the event stem — it's band-named by design (see Key Decisions).

---

## Resume Prompt

> Picking up from a previous session on the Band Advance pipeline (`Code/BandInfoForm/`, branch `advance-system`). We just finished adding three dedicated rows to the Universal Show Advance template — Number of IEMs, Number of Performers, Lighting Notes — and fixed a Stage Plot hyperlink regression that was actually caused by ad hoc test calls to `daysheet.fill()` omitting the `stageplot_names` argument, not a real pipeline bug. Also fixed a real filed event (Tailgate @ FSQ, 9/13, headliner The Closers) whose Event Name in `advance-list.xlsx` was just "Tailgate" instead of including the band name like every other real show — renamed the sheet row, the DB event, and all three filed files (advance doc, stage plot, email draft) to match.
>
> Two commits are pushed: `5a0aebc` and `0d792de` on `advance-system`. Everything's deployed to the VM (192.168.200.84) and mirrored to `~/Dropbox/Nyquist/Blank Advances/` and Desktop.
>
> No explicit next task was given — pick up whatever Brian brings next. One thing to watch for: the new `iem_count` form field hasn't been tested against a real live band submission yet, only a manual override. If a real submission's advance doc looks off on IEM count, start there.
