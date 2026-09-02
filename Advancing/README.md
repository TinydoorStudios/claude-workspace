# Advancing

Everything for advancing a show lives here. Two files you touch, one you read,
one folder that fills itself.

```
Advancing/
  advance-list.xlsx     ← the ONE spreadsheet. Two tabs that matter:
       • Advance List   — you edit this. Every bill goes here.
       • Status         — auto-refreshed read-back: emailed / responded / follow-up due
  generate.command      ← double-click after editing. Builds everything.
  Events/               ← auto-built, one folder per bill:
      2026-09-11 — 513 Airwaves w Inhailer Radio (Fountain Square)/
          Day Sheet.docx                  ← filled from sheet + the band's form
          Advance Email — <Band>.md       ← draft per band (NOTHING is sent)
          Followups/<Band>.md             ← only if a reminder is due
  _template/            ← pristine copies — reset from here if the sheet gets messy
```

Close the workbook in Excel before running generate.command — the run rewrites the
Status tab in place (it never touches your Advance List tab).

## The loop

1. Open **advance-list.xlsx** → the **Advance List** tab. Add a row per act (opener /
   support / headliner). Event name + date + venue group a bill together. Fill what you
   know; the band's form fills the rest. Dropdowns + a How-to tab are built in.
2. Close the file, then double-click **generate.command**. The **Status** tab in the
   same workbook refreshes with who's emailed / responded / follow-up due.
3. Open the new folder under **Events/**. Send each `Advance Email` from your mail
   (drafts-you-approve — the system never sends). Finish the internal cells on the
   `Day Sheet.docx` (PA, consoles, lead, buyout) in Word, then export to PDF.
4. Bands fill the form at **advance.tinydoorstudios.com** (their email carries a
   pre-addressed link). Re-run generate.command any time to pull their answers into
   the day-sheet and status sheet.

## Rules that matter

- **Sheet value wins, the form fills gaps.** The spreadsheet is the source of truth.
- **Nothing auto-sends** — initial emails or follow-ups. You review and send.
- **Follow-up:** 10 days after the email, one reminder, drafted not sent. It stops
  the moment the band submits the form (that = completed).
- **Re-running is safe.** It rebuilds `Events/` from the current sheet and refreshes
  status. Your form submissions are never touched.

## Under the hood

The engine runs on the advance server (n8n VM, `/opt/band-advance/`). `generate.command`
uploads the sheet, runs `tools/package_run.py`, and mirrors the built tree back here.
App/code + database docs: `../Code/BandInfoForm/ARCHITECTURE.md`. Deploy code changes
with `../Code/BandInfoForm/deploy_app.command`.
