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

**Model routing (2026-09-29, made permanent same day).** Judgment work runs on Opus 5.5 at medium effort; mechanical work runs on Sonnet 5.5 at medium. Three pieces hold it in place without anyone remembering. First, every session starts on Opus · medium: `~/.claude/settings.json` has `"model": "opus"` and `"effortLevel": "medium"`. Second, new-show, send-it and show-wiki-push carry `model: claude-sonnet-5-5` / `effort: medium` in their frontmatter, so the turn that runs them drops to Sonnet by itself and the next prompt returns to Opus. They're one-turn jobs, so the override covers the whole job. Third, show-deep-build carries `model: claude-opus-5-5` and opens with a model gate: it reads the session's own model (`get_session self`), and if the session was switched to Sonnet it stops and asks Brian to flip the menu back before the multi-turn question round starts. A session can't re-price itself, so the gate asks rather than switches. Bump the deep build to Opus high only for a genuinely unusual show, like an uncovered instrument or a big classical spot-mic rig. fable-parity still loads on Opus.

Disambiguation that has bitten before: "send it fsq/memo" (with a venue) = stage 3; bare "SEND IT" after a built show = stage 5.

Skill sources — all of them, including `new-show`, `send-it`, `show-wiki-push`, `show-deep-build` and `pipeline-fix` — live in `audio/_skills/` and are symlinked into `.claude/skills/`, so Claude Code runs the live copy. Shows are built in Claude Code, never Cowork (2026-09-14); there are no `.skill` snapshots to re-upload.

Routing (venue → folder/console/template/KB articles): `ROUTING.md`. Conversation flow + don't-forgets: `NEW-SHOW.md`.
