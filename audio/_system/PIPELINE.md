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

**Model routing (2026-09-29).** Judgment work runs on Opus 5.5 at medium effort; mechanical work runs on Sonnet 5.5 at medium. Each skill's frontmatter sets its own `model:` and `effort:` so the switch happens on its own: show-deep-build → `claude-opus-5-5`, while new-show, send-it and show-wiki-push → `claude-sonnet-5-5`. The catch is that a skill's override only lasts for the turn that invoked it; the session model comes back on the next prompt. A deep build runs across many turns (the one-question-at-a-time round, the locker forks, the audit), so start a build in a session already set to Opus 5.5 medium, not Sonnet, or every answer after the first turn gets handled by Sonnet. The three Sonnet stages are one-shot runs, so their override covers the whole job. The ideal flow is a build on Opus, then a fresh Sonnet session for "send it" and the wiki push, which avoids re-sending the whole research context. Bump the deep build to Opus high only for a show that's genuinely unusual, like an uncovered instrument or a large classical spot-mic rig. fable-parity still loads on Opus.

Disambiguation that has bitten before: "send it fsq/memo" (with a venue) = stage 3; bare "SEND IT" after a built show = stage 5.

Skill sources — all of them, including `new-show`, `send-it`, `show-wiki-push`, `show-deep-build` and `pipeline-fix` — live in `audio/_skills/` and are symlinked into `.claude/skills/`, so Claude Code runs the live copy. Shows are built in Claude Code, never Cowork (2026-09-14); there are no `.skill` snapshots to re-upload.

Routing (venue → folder/console/template/KB articles): `ROUTING.md`. Conversation flow + don't-forgets: `NEW-SHOW.md`.
