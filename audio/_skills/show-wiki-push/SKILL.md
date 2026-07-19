---
name: show-wiki-push
description: Pushes a completed show (Fountain Square OR Memorial Hall) to the Live Sound KB wiki. Trigger when Brian says "push to wiki", "wrap it up", "push the show", or bare "SEND IT" AFTER a .ses has been built. Brian's explicit go is the ONLY gate — console verification is NOT required (rule 2026-07-19: shows are one-offs). (If "send it" is paired with a venue name to BUILD a .ses from paperwork — "send it fsq" / "send it memo" — that's the send-it skill, not this one.) Creates the wiki show page, ships the FULL packet as downloadable assets (MASTER, Show Packet, EQ Reasoning, Input List xlsx, .ses, stage plot), updates the shows index and active-projects log, publishes, verifies the pages landed in the Wiki.js database, and stamps the show published. Replaces fsq-wiki-push (now an alias). Always use this skill for show wiki pushes — never push a show manually.
---

# Show Wiki Push — FSQ + Memo

Packages a completed show into the Live Sound KB wiki, venue-aware. **The only publish gate is
Brian's explicit go** (rule 2026-07-19: shows are one-offs — never ask him to load-test the .ses
on the console before publishing). Supersedes `fsq-wiki-push` (2026-07-19); that skill is now an
alias for this one.

## Step 0 — Confirm before acting

If Brian hasn't already said "yes" or "SEND IT" explicitly, ask exactly: **"SEND IT?"** and wait.

## Step 1 — Locate the show via show.status.json

Every show folder carries `show.status.json` (`audio/_shared/show_status.py`). If Brian named
the show, use that folder. Otherwise scan both venue folders for status files and pick the one
whose latest stage is `ses_built` (or `verified`) but not `published`:

```bash
for d in ~/Documents/Claude/audio/{"Fountain Square","Memorial Hall"}/2*/; do
  [ -f "$d/show.status.json" ] && python3 ~/Documents/Claude/audio/_shared/show_status.py show --folder "$d" && echo "— $d"
done
```

**The only gate is Brian's go (Step 0).** Console verification is NOT required and he is never
asked to load-test the .ses first — shows are one-offs (rule 2026-07-19). A `verified` stamp,
when present, is informational only. Two candidates, or none → ask which show.
Pre-status-file shows have no status file — confirm which show with Brian and stamp
retroactively so the record is complete.

Derive from the folder + status file:
- `VENUE_TAG` = `fsq` | `memo` (from the venue folder)
- `SHOW_DATE` = `YYYY-MM-DD` · `SHOW_TITLE` = human name
- `SHOW_SLUG` = lowercase, hyphens, no special chars
- `ASSET_DIR` = `SHOW_DATE-SHOW_SLUG`
- Page path: `show-VENUE_TAG-SHOW_DATE-SHOW_SLUG`

## Step 2 — Write the show wiki page

**Path:** `~/Documents/Claude/audio/Live Sound KB/Wiki/show-VENUE_TAG-SHOW_DATE-SHOW_SLUG.md`

**Critical: no YAML frontmatter** — start directly with the H1; a `---` block breaks Wiki.js titles.

```markdown
# Show: SHOW_TITLE — VENUE_FULL, SHOW_DATE

**Venue:** VENUE_FULL (VENUE_ABBR) · **Console:** DiGiCo Q225 · **Date:** SHOW_DATE

## Input List

| Ch | Instrument | Mic/DI |
|---|---|---|
[one row per channel from the FOH .md]

## EQ — Channel Processing

Band order: B4 (high) → B3 → B2 → B1 (low). HPF/LPF dialed by hand at soundcheck — not written to .ses.

| Ch | Instrument | HPF (manual) | B4 | B3 | B2 | B1 |
|---|---|---|---|---|---|---|
[one row per channel — "FLAT" for bypassed bands, bands as "±N@FREQHz QX.X TYPE"]

## Downloads

| File | Links |
|---|---|
| MASTER packet (everything, one PDF) | View · Download |
| Show Packet PDF | View · Download |
| FOH EQ Reasoning PDF | View · Download |
| Input List (xlsx) | Download |
| SHOW_TITLE.ses (Q225 showfile) | Download |
| Stage Plot (band-provided, if present) | View · Download |

## .ses File

Patched from `TEMPLATE_NAME` with the venue patcher (shared engine, byte-verify + readback
PASS). Written: fader names, EQ bands. Not written: HPF/LPF, dynamics (documented in the
packet, dialed by hand).

## Show Folder

`~/Documents/Claude/audio/VENUE_FOLDER/SHOW_DATE SHOW_TITLE/`

## Related

[[venue-VENUE-ARTICLE]], [[console-digico-q225]], [[pipeline-spec-VENUE_TAG]]
```

Link pattern (see convention below): PDFs get
`<a href="/assets/shows/ASSET_DIR/FILE.pdf" target="_blank" rel="noopener">View</a> · <a href="/assets/shows/ASSET_DIR/FILE.pdf?dl=1" download>Download</a>`;
`.ses`/`.xlsx` get one `?dl=1` Download link. URL-encode spaces as `%20`. Memo pages: note the
crowd-mic rig rows like any other channel.

## Step 3 — Copy the FULL packet into the wiki repo

Into `~/Documents/Claude/audio/Live Sound KB/Wiki/assets/shows/ASSET_DIR/` (create it):

- `SHOW_TITLE.ses`
- `SHOW_TITLE - MASTER.pdf`
- `SHOW_TITLE - Show Packet.pdf`
- `SHOW_TITLE - FOH EQ Reasoning.pdf`
- `SHOW_TITLE - Input List.xlsx`
- `SHOW_TITLE - FOH Channel Processing.md`
- `SHOW_TITLE - Stage Plot.pdf` / `SHOW_TITLE - Rider.pdf` — if present (band-provided)
- `SHOW_TITLE.spec.json` (or `The_Show.spec.json` variant) — reproducibility

Every file linked on the page MUST be in this copy list — a link with no copied file is the
bug the old FSQ skill shipped.

## Step 4 — Update shows.md

`~/Documents/Claude/audio/Live Sound KB/Wiki/shows.md` — under the venue's heading
(`## Fountain Square (FSQ)` or `## Memorial Hall (Memo)` — remove the "No show pages yet"
placeholder on Memo's first push), newest first:

```markdown
### [SHOW_TITLE — SHOW_DATE](/show-VENUE_TAG-SHOW_DATE-SHOW_SLUG)
DiGiCo Q225 · N channels · [brief mic summary]

| File | Type |
|---|---|
| [Show Page](/show-VENUE_TAG-SHOW_DATE-SHOW_SLUG) | Wiki page |
| MASTER packet — View · Download | PDF |
| SHOW_TITLE.ses — Download | Q225 showfile |
```

## Step 5 — Update active-projects.md

Append to the Completed Shows table:

```
| SHOW_DATE | SHOW_TITLE | VENUE_ABBR | Full packet + .ses | [[show-VENUE_TAG-SHOW_DATE-SHOW_SLUG]] |
```

Bump the `Last updated:` date.

## Step 6 — Publish (pages + assets)

Preferred, one shot — commit/push, rsync assets to the VM, verify a download URL:

```bash
"~/Documents/Claude/audio/Live Sound KB/_tools/kb-publish.sh" "Show: SHOW_TITLE (VENUE_ABBR SHOW_DATE)"
```

(Needs Tailscale + `~/.ssh/proxmox_tds`. The launchd watcher also auto-commits pages within
~60 s, but it does NOT rsync assets — if kb-publish.sh can't run, rsync them explicitly:
`rsync -av --chmod=Da+rx,Fa+r -e "ssh -J tds -i ~/.ssh/proxmox_tds" "<Wiki>/assets/" brian@192.168.200.84:/opt/kb-assets/`.)

## Step 7 — Verify in the Wiki.js DB; patch render/toc if stale

```bash
ssh -i ~/.ssh/proxmox_tds root@192.168.0.4 \
  'pct exec 101 -- docker exec wikijs-db-1 psql -U wiki wiki -c \
  "SELECT path, title, \"updatedAt\" FROM pages ORDER BY \"updatedAt\" DESC LIMIT 6;"'
```

The show page path must appear (allow ~90 s for the watcher). If the `render` column doesn't
contain the show name, restart the container and re-check:

```bash
ssh -i ~/.ssh/proxmox_tds root@192.168.0.4 'pct exec 101 -- docker restart wikijs-wiki-1'
sleep 10 && curl -s -o /dev/null -w "%{http_code}" http://192.168.200.126:3000/
```

Still stale → patch render/toc columns directly (the established replace() SQL pattern).
Verify shows.md's toc carries the new entry.

## Step 8 — Stamp published + report

```bash
python3 ~/Documents/Claude/audio/_shared/show_status.py stamp \
  --folder "<show folder>" --stage published --note "kb.tinydoorstudios.com/show-…"
```

Report: page URL (`https://kb.tinydoorstudios.com/show-VENUE_TAG-SHOW_DATE-SHOW_SLUG`), files
confirmed in the DB + a spot-checked asset download, anything patched along the way.

## Constants

| Item | Value |
|---|---|
| Wiki repo | `~/Documents/Claude/audio/Live Sound KB/Wiki/` |
| SSH key | `~/.ssh/proxmox_tds` |
| Proxmox host (pct exec) | `192.168.0.4` (root) — Tailscale alias `tds` |
| Wiki container | LXC 101 — `pct exec 101 --` |
| Wiki DB | `docker exec wikijs-db-1 psql -U wiki wiki` |
| Wiki.js LAN | `http://192.168.200.126:3000` (the old 192.168.0.126 is retired) |
| Asset store | n8n VM `192.168.200.84:/opt/kb-assets` (nginx `/assets/`) |
| Public URL | `https://kb.tinydoorstudios.com` |
| Publisher script | `Live Sound KB/_tools/kb-publish.sh` |

## Asset link & download convention

nginx serves `/assets/` inline and forces download with `?dl=1`. PDFs: View + Download pair.
Non-viewable (`.ses`/`.xlsx`/`.md`/`.json`): single `?dl=1` Download link. Raw `<a>` anchors
(Wiki.js keeps `target`/`download` through DOMPurify). Never `/downloads/` — not routed, 404s.

## Hard rules

- No YAML frontmatter on show pages.
- No push without Brian's explicit go (Step 0) — and that go is the ONLY gate: console
  verification is never required and never asked for (rule 2026-07-19, shows are one-offs).
- Every page link has its file in the Step 3 copy list; assets must reach `/opt/kb-assets`.
- EQ table band order B4 → B1, matching the .md.
- Don't report success until the page path appears in the Wiki.js DB.
- Q225 venues only (FSQ/Memo). Other venues' shows or KB articles → `wiki-publish`.
