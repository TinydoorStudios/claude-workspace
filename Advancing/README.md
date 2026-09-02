# Advancing

Everything for advancing a show lives here: one sheet you edit, one command you
run, and a venue-filed archive that builds itself.

```
Advancing/
  advance-list.xlsx     ← the ONE sheet. One tab does everything:
       • you fill the left columns (event / act / band details)
       • the band's form answers fill your blanks, tinted blue
       • a color-coded STATUS block is appended on the right
  generate.command      ← double-click after editing. Builds + files everything.
  _template/            ← pristine copies — reset from here if the sheet gets messy

  FSQ/ 2026/ 09 September/                         ← the filed archive (accumulates)
       091126 513 Airwaves w Inhailer Radio advance.docx
       Email Drafts/
           091126 513 Airwaves w Inhailer Radio advance email - <Band>.md
  WP/  Memo/  ESP/  Court/  IA/  ZP/ …
```

Each show files into **`<Venue>/<Year>/<MM Month>/`** as
`MMDDYY <Event Name> advance.docx`. Venue abbreviations: FSQ, WP, ESP, Court, IA,
ZP (Zeigler), Memo. Email drafts land in an `Email Drafts/` subfolder of the month.

### Reading the sheet after a run

- **Plain cells you typed = yours.** They always win.
- **Blue-tinted cells = the band's form answer**, dropped into a blank you left. They
  mirror the form and refresh every run — so don't edit a tinted cell. To override a
  field the band answered, just type your value in; it turns plain and wins from then on.
- **STATUS block** (green group header, right side): Status is color-coded by state
  (green = responded, amber = follow-up due, grey = queued…), plus Email Sent,
  Follow-up Due, Completed, Responded, What Changed, Additional. Auto — don't edit it.

Close the workbook in Excel before running generate.command — the run rewrites the
tinted cells + STATUS block in place. Your typed cells are never touched.

## The loop

1. Open **advance-list.xlsx** → the **Advance List** tab. Add a row per act (opener /
   support / headliner). Event name + date + venue group a bill together. Fill what you
   know; the band's form fills the rest. Dropdowns + a How-to tab are built in.
2. Close the file, then double-click **generate.command**. Each show files into its
   venue/year/month folder, your blanks fill with the band's answers (tinted), and the
   STATUS block refreshes.
3. Open the show's month folder. Send each **Email Drafts** file from your mail
   (drafts-you-approve — the system never sends). Finish the internal cells on the
   advance `.docx` (PA, consoles, lead, buyout) in Word, then export to PDF.
4. Bands fill the form at **advance.tinydoorstudios.com** (their email carries a
   pre-addressed link). Re-run generate.command any time to pull their answers in.

## Rules that matter

- **Sheet value wins, the form fills gaps.** The spreadsheet is the source of truth.
- **It files, it doesn't mirror.** Re-running a show updates its files in place; other
  shows and past months are never touched — the tree is your archive.
- **Nothing auto-sends.** Generating does NOT mark anything sent — real sending moves to
  Outlook (next step), which is what will start the follow-up clock.
- **Coordinators edit, everyone else reads.** 1–2 people run generate; the rest open the
  filed docs. When this moves to a shared Dropbox folder, set `ADVANCE_ROOT` to that path
  (one line in generate.command) and the tree + sheet live there.

## Under the hood

The engine runs on the advance server (n8n VM, `/opt/band-advance/`). `generate.command`
uploads the sheet, runs `tools/package_run.py` (which files the venue tree), rsyncs it
back as an overlay, and folds status into the sheet with `tools/merge_status.py`.
App/code + database docs: `../Code/BandInfoForm/ARCHITECTURE.md`. Deploy code changes
with `../Code/BandInfoForm/deploy_app.command`.
