# PIPELINE — the show chain in one page

*Created 2026-07-14. The full picture used to live only across four skill descriptions; this names the chain in order. Mechanics stay in the skills — this file never duplicates them.*

A show moves through five stages, each owned by one skill:

| Stage | Skill | Trigger | In → Out |
|---|---|---|---|
| 1. Scaffold | **new-show** | "new show", venue + date + name | nothing → dated show folder + patcher copy + FOH .md stub |
| 2. Deep build | **show-deep-build** | any new-show submission (default — Brian never says "deep think") | input list / brief → spec.json, FOH Channel Processing .md, Input List xlsx, Show Packet / EQ Rationale / MASTER PDFs |
| 3. .ses build | **send-it** | "send it fsq" / "send it memo" (venue always named) | FOH .md → console-ready .ses via venue patcher (Q225 venues only) |
| 4. Console verify | — (Brian, at the desk) | load-in | .ses recalled and checked on the console — the hard stop before publishing |
| 5. Publish | **fsq-wiki-push** (FSQ) / **wiki-publish** (everything else) | "push to wiki", "wrap it up", bare "SEND IT" after verify | verified show → live KB pages + assets |

Overlay: on a non-Fable model, **fable-parity** loads alongside show-deep-build for stages 2's research (worksheets + serialization).

Disambiguation that has bitten before: "send it fsq/memo" (with a venue) = stage 3; bare "SEND IT" after a console-verified build = stage 5.

Skill sources live in `audio/_skills/` and are symlinked into `.claude/skills/`, so Claude Code always runs the live copy. **Cowork installs are snapshots** — after editing a skill, re-zip and re-upload in Cowork settings or Cowork sessions keep the old behavior.

Routing (venue → folder/console/template/KB articles): `ROUTING.md`. Conversation flow + don't-forgets: `NEW-SHOW.md`.
