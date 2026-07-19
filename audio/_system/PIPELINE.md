# PIPELINE — the show chain in one page

*Created 2026-07-14; updated 2026-07-19 (intake step, show.status.json, unified show-wiki-push). The full picture used to live only across four skill descriptions; this names the chain in order. Mechanics stay in the skills — this file never duplicates them.*

A show moves through five stages, each owned by one skill:

| Stage | Skill | Trigger | In → Out |
|---|---|---|---|
| 1. Scaffold | **new-show** | "new show", venue + date + name | nothing → dated show folder + patcher copy + FOH .md stub + `show.status.json` |
| 2. Deep build | **show-deep-build** | any new-show submission (default — Brian never says "deep think") | ANY show artifacts (rider/stage-plot PDFs, xlsx/CSV lists, photos/screenshots, brief) → intake-normalized facts → spec.json, FOH Channel Processing .md, Input List xlsx, Show Packet / EQ Rationale / MASTER PDFs |
| 3. .ses build | **send-it** | "send it fsq" / "send it memo" (venue always named) | FOH .md → console-ready .ses via venue patcher (Q225 venues only) |
| 4. Console load | — (Brian, at the desk, at the show) | load-in | the .ses gets recalled at the show itself — **NOT a publish gate** (rule 2026-07-19: shows are one-offs; if Brian mentions it ran, stamp `verified` as a nice-to-have) |
| 5. Publish | **show-wiki-push** (FSQ + Memo; `fsq-wiki-push` is its alias) / **wiki-publish** (everything else) | "push to wiki", "wrap it up", bare "SEND IT" after the build — **Brian's go is the only gate** | built show → live KB page + full packet assets |

**Show state is a file, not a guess (2026-07-19):** every show folder carries `show.status.json`
(`_shared/show_status.py`). The scaffold writes it; `build_packet.py` stamps `packet_built` and the
.ses engine stamps `ses_built` automatically; the wiki push stamps `published`. `verified` is
optional/informational — stamped only if Brian happens to say the file ran on the desk, never
waited for. Any stage or resume reads it (`python3 _shared/show_status.py show --folder <show>`)
instead of hunting for "the newest folder with a .ses".

Overlay: on a non-Fable model, **fable-parity** loads alongside show-deep-build for stages 2's research (worksheets + serialization).

Disambiguation that has bitten before: "send it fsq/memo" (with a venue) = stage 3; bare "SEND IT" after a built show = stage 5.

Skill sources live in `audio/_skills/` and are symlinked into `.claude/skills/`, so Claude Code always runs the live copy. **Cowork installs are snapshots** — after editing a skill, re-zip and re-upload in Cowork settings or Cowork sessions keep the old behavior.

Routing (venue → folder/console/template/KB articles): `ROUTING.md`. Conversation flow + don't-forgets: `NEW-SHOW.md`.
