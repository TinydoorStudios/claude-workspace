# Context Handoff — 2026-07-20
**Session topic:** Built Patchbay v1 — a self-hosted patch sheet tool (Patchy clone) for the Q225, M32 and Wing, wrapped as a Mac app
**Console / Venue:** All three desks — DiGiCo Quantum 225, Midas M32, Behringer Wing

---

## What We Did

Built `Code/Patchbay/` from scratch after I pointed at usepatchy.io and asked for my own version covering the Q225, M32 and Wing. It's a standalone aiohttp + vanilla-JS app (same stack as ShowBuilder, deliberately — no build step, deployable to the n8n VM later the same way). It does the patch-sheet job Patchy does: inputs grid, visual I/O map, outputs/buses, stage boxes, power distros, rig templates vs one-off events, revision history, and PDF/xlsx/JSON export.

Then it got a dark theme, a real `Patchbay.app` installed to `/Applications`, and a reset/clear pair of buttons. Two real bugs were found and fixed by testing with actual clicks and keystrokes rather than scripted API calls.

---

## Current State

- **Done:**
  - App runs at `http://localhost:8096` (`./run.sh`) and via `/Applications/Patchbay.app`
  - Four house rigs seeded as templates: Memorial Hall (with the permanent crowd rig), Fountain Square, Washington Park, Wing freelance
  - Dark theme default, light toggle in the top bar, choice persists
  - Exports verified: 3-page stage PDF (input list → patching by port → cross-patch/outputs/power), Input List xlsx in my column format, sheet JSON
  - Mac app verified launching from `/Applications`, loopback-only, restores last sheet
  - Not committed — `Code/Patchbay/` is untracked in the workspace git repo

- **In progress:** Nothing mid-flight.

- **Up next (candidates, nothing promised):**
  - Commit it
  - Deploy to the n8n VM behind the Cloudflare tunnel like ShowBuilder (`patchbay.tinydoorstudios.com`) so it's reachable on a phone at load-in
  - Fill in the real card/channel counts for the FSQ and Memo racks — those are marked `(CONFIRM)` in the seeded sheets
  - Click-test the in-app exports (see Watch-Outs)

---

## Key Decisions (Locked)

- **Standalone app, not a ShowBuilder feature.** ShowBuilder captures a show's input list; Patchbay documents persistent rigs. Patchbay can import a `<Show>.brief.json` to prefill an event sheet, but they stay separate apps.
- **Not in the show pipeline.** Patchbay does no EQ, no `.ses`, no research. `show-deep-build` still owns the show packet and console file.
- **Local first**, VM deploy later. The app pins the server to `127.0.0.1`.
- **Console specs come from published manufacturer data**, and anything option-dependent (DMI cards, MADI mode, Wing expansion slot) is marked `configurable` in `knowledge/consoles.json` rather than asserted as fact.
- **Mic data reads live from `../ShowBuilder/knowledge/mics.json`** when present so the two tools can't drift; Patchbay's own `knowledge/mics.json` is only a fallback.
- **Destructive buttons snapshot a revision first.** Clear rows, Reset to blank — both confirm, both snapshot, both recoverable from the Revisions tab.
- **Autosave never bumps the rev.** Only "Mark revision" snapshots and increments.
- **Printed sheets stay light** regardless of UI theme.

---

## Open Items

- Uncommitted. Whole of `Code/Patchbay/` plus the `patchbay` entry added to `.claude/launch.json`.
- In-app export buttons (PDF to browser, xlsx to `~/Downloads`) are implemented but never click-tested inside the Mac window — I can't drive the native window. They work in the browser.
- weasyprint isn't installed on this Mac, so the PDF goes through the browser's print dialog (Letter landscape). If weasyprint ever gets installed, the server renders it directly with no dialog — code path already there.
- FSQ and Memo stage-rack I/O counts are `(CONFIRM)` placeholders.

---

## Files Delivered This Session

| File | Format | Description |
|------|--------|-------------|
| `Code/Patchbay/` | app | The whole tool — backend (aiohttp), web (vanilla JS), knowledge (console + mic data), data (sheets) |
| `Code/Patchbay/mac/Patchbay.app` | .app | Swift/WKWebView wrapper; copy installed at `/Applications/Patchbay.app` |
| `Code/Patchbay/README.md` | md | Launch, features, exports, console data table, storage layout |
| `Code/Patchbay/knowledge/consoles.json` | json | Q225 / M32 / Wing port groups, channel/bus/matrix counts |
| `.claude/launch.json` | json | Added the `patchbay` dev-server config (port 8096) |

---

## Corrections / Watch-Outs

- **Rows were unclickable in v1** — every input row was `draggable="true"` for the I/O map, and WebKit swallows mousedown on child fields of a draggable row. Fixed: drag now lives on a small ⠿ handle in the CH column. Don't put `draggable` back on the `<tr>`.
- **Edits were being silently dropped** — cell changes rebuilt the whole table on blur, and the autosave response replaced the in-memory sheet wholesale, so a save in flight overwrote whatever was typed next. Fixed with in-place cell repaints, an edit sequence counter, and coalesced saves. Rule for this app: **never re-render a table from a change handler.**
- **The ⚑ column was the TOUR flag** with no label — now reads TOUR.
- **I damaged the FSQ template during testing.** Mis-scaled automation clicks hit "+ 8" twice and added 16 blank rows plus a stray port/box on one. Found in an audit and stripped; FSQ is back to 0 input rows with its 10 outputs, 2 boxes and distro intact. Lesson: test clicks go through a scratch sheet, never the house-rig templates.
- Rebuild the app after any Swift change with `mac/build_app.sh` — it now reinstalls to `/Applications` automatically. The repo path and port are constants at the top of `main.swift`; update them if Patchbay moves.

---

## Resume Prompt

> Picking up from a previous session. We built **Patchbay** — a self-hosted patch sheet tool at `Code/Patchbay/`, covering the DiGiCo Quantum 225, Midas M32 and Behringer Wing. It's an aiohttp + vanilla-JS app (ShowBuilder's stack) with an inputs grid, a visual I/O map with conflict detection, outputs/buses, stage boxes, power distros, templates vs one-off events, revision history, and PDF/xlsx/JSON export. Dark theme by default. It's wrapped as `Patchbay.app` and installed to `/Applications`; it also runs via `./run.sh` on port 8096. Four house rigs are seeded as templates (Memo, FSQ, WP, Wing).
>
> Read `Code/Patchbay/README.md` first — it covers the whole thing.
>
> Next task: **commit it** (the folder is untracked, along with the `patchbay` entry in `.claude/launch.json`), and if I ask for it, deploy to the n8n VM behind the Cloudflare tunnel the way ShowBuilder is deployed.
>
> Key context that isn't in standing memory: Patchbay is deliberately NOT part of the show pipeline — no EQ, no `.ses`, no research; `show-deep-build` still owns all of that. Two hard rules in this codebase: never put `draggable` back on a table row (it kills clicking into cells in WebKit), and never re-render a table from a change handler (it eats the field being typed into). When testing the UI, use a scratch sheet — I already clobbered the FSQ template once with stray automation clicks.
