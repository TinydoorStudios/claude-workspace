---
name: show-wiki-push
description: Publishes a completed show (Fountain Square or Memorial Hall) to the Live Sound KB wiki with one command. Trigger when Brian says "push to wiki", "wrap it up", "push the show", or bare "SEND IT" AFTER a .ses has been built. Brian's explicit go is the ONLY gate — console verification is never required (shows are one-offs). If "send it" is paired with a venue name to BUILD a .ses ("send it fsq"/"send it memo"), that is the send-it skill, not this one. Runs Live Sound KB/_tools/publish_show.py, which writes the page from the FOH .md, ships the full packet as assets, updates the shows index and active-projects, publishes, verifies over HTTP, stamps the show published and queues its KB write-backs in _learning/PENDING.md.
---

# Show Wiki Push

One command. The only gate is Brian's explicit go (R42).

## 1. Confirm
If Brian hasn't already said "yes" / "SEND IT" / "push it" for this show, ask exactly **"SEND IT?"** and wait.

## 2. Find the show
If he named it, use that folder. Otherwise list candidates — status files whose latest stage is
`ses_built` (or `verified`) but not `published`:

```bash
for d in ~/Documents/Claude/audio/{"Fountain Square","Memorial Hall"}/2*/; do
  [ -f "$d/show.status.json" ] && python3 ~/Documents/Claude/audio/_shared/show_status.py show --folder "$d" | head -1 && echo "   $d"; done
```

Two candidates or none → ask which (one question).

## 3. Publish
```bash
python3 "$HOME/Documents/Claude/audio/Live Sound KB/_tools/publish_show.py" "<show folder>"
```

It regenerates the wiki page from the FOH `.md` (`make_show_page.py`), copies the MASTER / Show
Packet / EQ Reasoning / Input List / `.md` / `.ses` / stage plot / rider / spec into
`Wiki/assets/shows/<date>-<slug>/`, adds the show to `shows.md` and the Completed Shows table in
`active-projects.md`, runs `kb-publish.sh` (git commit + push, rsync assets to the n8n VM,
publish pages through the Wiki.js API, nav rebuild), checks the page and the MASTER return
HTTP 200, stamps `published` in `show.status.json`, and appends the spec's `kb_writeback` +
`reconciliation` lines to `_learning/PENDING.md`.

Needs Tailscale up and `~/.ssh/proxmox_tds`; secrets in `~/.claude/kb-secrets.sh`
(`KB_WIKI_API_KEY`, `KB_BASIC_AUTH`).

## 4. If verification fails
`publish_show.py` refuses to stamp `published` when the page or the MASTER asset is not
reachable. Then, and only then:

- Assets missing → rsync by hand: `rsync -av --chmod=Da+rx,Fa+r -e "ssh -J tds -i ~/.ssh/proxmox_tds" "<Wiki>/assets/" brian@192.168.200.84:/opt/kb-assets/`
- Page missing → re-run the pages publisher: `KB_WIKI_API_KEY=… python3 ~/.claude/scripts/kb-publish-pages.py`
- Page present but stale render → `ssh -i ~/.ssh/proxmox_tds root@192.168.0.4 'pct exec 101 -- docker restart wikijs-wiki-1'`, wait 10 s, re-run `publish_show.py --skip-verify` is NOT the fix — re-run it plain so the stamp only lands on a 200.

## 5. Report
Page URL, asset count, what landed in PENDING.md, anything escalated. Then stop.

## Constants
| Item | Value |
|---|---|
| Wiki repo | `~/Documents/Claude/audio/Live Sound KB/Wiki/` |
| Public URL | `https://kb.tinydoorstudios.com` |
| Asset store | n8n VM `192.168.200.84:/opt/kb-assets` (nginx `/assets/`, `?dl=1` forces download) |
| Proxmox host | `192.168.0.4` (root, Tailscale alias `tds`), Wiki.js in LXC 101 |
| Publisher | `Live Sound KB/_tools/kb-publish.sh` (called by `publish_show.py`) |

Hard rules: no YAML frontmatter on show pages (the generator writes none); every linked file is
copied (the copy list is derived from the link list); Q225 venues only — other venues and KB
articles go through `wiki-publish`.
