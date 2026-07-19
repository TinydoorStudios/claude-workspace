# audio/ — Show Work Layer

*Last updated: 2026-07-14 (slimmed — this file was a stale 2026-05-27 fork of the old global CLAUDE.md, carrying outdated mic identities (Neumann U87), retired infrastructure (Pi-hosted n8n), and a superseded packet format. Everything general now lives one level up in `~/Documents/Claude/CLAUDE.md`, which loads for every session here. This file holds ONLY what is specific to working under `audio/`.)*

## Control files for show work

- `_system/ROUTING.md` — venue → folder · console · specs map. Read first for any show task.
- `_system/NEW-SHOW.md` — router + don't-forgets for any show conversation.
- `Live Sound KB/Wiki/INDEX.md` — KB article map; pull articles as the task requires, never all at startup.

Every new show runs the **show-deep-build** skill (the Deep Think pipeline — see the Deep Think section of the main CLAUDE.md). Scaffolding = **new-show** skill; .ses build = **send-it**; wiki publish = **show-wiki-push** (FSQ + Memo; `fsq-wiki-push` is its alias) / **wiki-publish** for everything else. Full chain: `_system/PIPELINE.md`. Show state per folder: `show.status.json` (2026-07-19).

## Canonical sources — where truth lives

- Knowledge → `Live Sound KB/Wiki/` (mic identities in `mic-library.md` — the KB gallery is authoritative on what Brian owns; his only "87" is the Warm Audio WA-87 "87 JR", and every "421" is the vintage MD 421-U Silver Tail).
- Project state → `Live Sound KB/Wiki/active-projects.md`.
- Open questions → `Live Sound KB/Wiki/questions.md`.
- Console/venue/EQ rules → main CLAUDE.md + KB. When any local table disagrees with the KB, the KB wins.
- Session history → `about-me/memory.md` (symlink to the canonical `~/Documents/Claude/about-me/memory.md`).

## After meaningful show/KB work

Update `active-projects.md` + KB `CHANGELOG.md`, log workflow/structure changes to `_system/IMPROVEMENTS.md`, open items to `questions.md`, and append session history to `about-me/memory.md`.
