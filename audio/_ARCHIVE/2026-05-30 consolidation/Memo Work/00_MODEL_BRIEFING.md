# Q225 .ses Show Patcher — Model Briefing

**Read this first.** You are picking up an established workflow. The
operator (Brian — live sound engineer, 20+ years) has done the
debugging. Do not re-derive it. Follow these documents.

## What this workflow does

Takes a known-good DiGiCo Quantum 225 session file (`.ses`) and patches
it with show-specific channel data: channel names, HPF/LPF, four-band
EQ (with DEQ on the LowerMid band where requested). The result loads
on the Q225 with all the show config in place.

## What this workflow does NOT do

- Does not write to SD compressor or SD gate. The real tag IDs for
  those are not yet identified. Brian will address gate later.
- Does not touch Mustard plugin parameters. Anything Mustard is OFF
  in the template and must stay OFF on any channel you touch.
- Does not write to channels the show doesn't list. The template's
  state for untouched channels is preserved.

## The hard-won lesson — do not relearn this

Tag IDs `0x1E0E`, `0x1E0B`, `0x1E11`, `0x1E12` look like SD compressor
controls. They are not. They are the **Mustard plugin Dynamic 2 slot**.
Writing them turns Mustard Dyn 2 on every channel you touch. Ten script
versions were burned figuring this out. **Do not write to them.** The
full DO-NOT-WRITE list is in `01_Q225_SES_REFERENCE.md`.

## Files in this package

| File | What it is | When to read |
|------|------------|--------------|
| `00_MODEL_BRIEFING.md` | This file | First |
| `01_Q225_SES_REFERENCE.md` | File format, verified tags, do-not-write tags, console-save-diff method | Before writing any code |
| `02_SHOW_PATCHER_WORKFLOW.md` | Step-by-step show patching procedure with stop-and-confirm points | When starting a show |
| `apply_show_TEMPLATE.py` | The working v12 script, generalized — drop in the show data and run | When implementing a show |

## How to work with Brian

These are non-negotiable. They come from his global preferences.

- **Step-by-step when troubleshooting. Stop and confirm before moving
  forward.** Do not chain three speculative fixes in one response. Make
  one change, hand the file back, wait for him to test on the console.
- **Never assume — always ask.** If a channel name or frequency in the
  show paperwork is ambiguous, ask. If you don't know whether a tag is
  safe to write, ask or run the diff method — never guess.
- **No fluff, no over-explaining basics.** He has 20+ years on consoles.
  Skip the "what is an EQ band" explanations.
- **Warm, clear, direct. Not corporate.** Plain language.
- **Default deliverables to PDF unless he says otherwise.** Channel
  processing documents are delivered as three files: `.md` (patcher
  source), `.html` (human-readable channel cards), and a PDF rendered
  from the HTML via weasyprint (not reportlab). Full show packets end
  in a PDF. (This SOP package is markdown only because a model is the
  consumer.)
- **Destructive ops require explicit permission.** Don't overwrite,
  delete, or move existing files without asking first. Creating new
  files in a new show folder is fine.

## Where files live

```
~/Documents/Claude/audio/
├── Memorial Hall/                   ← Q225 lives here
│   ├── brian memo v2.ses            ← THE template, do not edit
│   ├── Q225 SES Patcher SOP/        ← you are here
│   └── YYYY-MM-DD ShowName/         ← one folder per show
│       ├── apply_<show>.py          ← the show's customized script
│       ├── <show>.ses               ← the output you build
│       └── ...other show paperwork
├── Fountain Square/   (FSQ)
├── Elm Street Plaza/  (ESP)
├── Washington Park/   (WP)
└── SOP Stuff/<venue>/               ← procedures live here
```

Show folder is `YYYY-MM-DD ShowName` so they sort chronologically.

## Start a new show — fast path

1. Read `02_SHOW_PATCHER_WORKFLOW.md` end-to-end.
2. Confirm with Brian: show name, date, source paperwork (a patch sheet
   `.xlsx` and channel-processing `.md` + `.html` in the show folder).
3. Create show folder if it doesn't exist.
4. Copy `apply_show_TEMPLATE.py` into the show folder as
   `apply_<showname>.py`.
5. Fill in the `CHANNELS` table from the show paperwork.
6. Run the script with `--src` pointing at the template and `--dest`
   into the show folder.
7. Verify the "Do-not-write tag verification: PASS" line in the script
   output.
8. Hand the .ses to Brian for console-side testing.
9. **Stop. Wait for his report.** Do not iterate without his feedback.

## When something goes wrong on the console

If Brian reports "Mustard is on" or "comp is engaged when it shouldn't
be" or any unexpected state on a channel you touched, that means a tag
mapping is wrong. Do not guess. Run the **console-save-diff method**
described in `01_Q225_SES_REFERENCE.md`. It identifies an unknown tag
in under a minute and replaces hours of script-version guessing.
