---
name: new-show
description: Scaffolds a show folder for any of Brian's venues — runs the advance bridge first (folders for booked shows scaffold themselves, with the band's stage plot and a brief skeleton), then creates the dated folder, the FOH Channel Processing .md stub and show.status.json for anything the bridge didn't cover. No patcher copy — the venue patcher is run in place. Trigger when Brian says "new show", "scaffold the show", "start a show folder", "set up the show folder", or names a venue + date + show with no paperwork yet. NOT the deep build — this only sets up files; EQ/paperwork is the show-deep-build skill, and building the .ses is send-it.
---

# New Show — folder scaffold

One command replaces the manual setup every show starts with. Runs
`~/Documents/Claude/audio/_system/scaffold_show.py`.

## Procedure

0. Run `python3 ~/Documents/Claude/audio/_shared/advance_bridge.py` first — if the show is in
   the band advance database it scaffolds the folder itself (with the band's stage plot and a
   brief skeleton), and you only report what landed.

1. Get the three facts (ask only for what's missing, one round): **venue**
   (memo / fsq / wp / esp / csp / zp / ia / greaves), **date** (YYYY-MM-DD),
   **show name**.
2. Run:
   ```bash
   python3 ~/Documents/Claude/audio/_system/scaffold_show.py \
     --venue <venue> --date YYYY-MM-DD --name "Show Name"
   ```
3. Report what was created. The script refuses to touch an existing folder —
   if it errors on that, ask Brian instead of deleting anything.

## What it creates

- `<Venue folder>/YYYY-MM-DD Show Name/`
- `Show Name - FOH Channel Processing.md` — a STUB with the locked format
  and venue don't-forgets baked in

## After the scaffold — Deep Think is the default

Deep Think is Brian's default for every new show (standing rule, 2026-07-01).
If Brian already supplied show content (channel list, input list, artist,
brief), continue STRAIGHT into the **show-deep-build** skill — do not wait
for him to say "deep think". If all he gave was venue/date/name, scaffold,
then ask for the input list + genre so the deep build can start.

## What this skill itself does NOT do

- No EQ, no research, no paperwork content — that's **show-deep-build**,
  which runs next by default.
- No .ses build — that's **send-it** after the MD is real.
- The Memo skeleton lists the crowd-rig faders (57–59) and the Wireless
  baseline as notes; confirm with Brian before writing crowd EQ into the MD.
