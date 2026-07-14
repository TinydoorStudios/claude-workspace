# ShowBuilder — Handoff

*Last updated: 2026-06-25 · author: Nyquist*

Pick-up doc for the ShowBuilder app after the **facts-only brief** rework. Pair
with `README.md` (usage) and `deploy/DEPLOY.md` (deployment detail). The driving
brief for this change is `audio/handoffs/2026-06-25_ShowBuilder-Brief-Export-Claude-Code-Handoff.md`.

---

## What it is (and the boundary that changed)

ShowBuilder is a **data-capture tool**. It captures a show's input list + metadata
+ free-text notes and exports a facts-only `<Show>.brief.json`. It **does not**
compute EQ, write a `.ses`, or write the FOH Channel Processing `.md`.

Everything downstream — artist + per-source research, EQ, the paperwork packet,
the EQ Rationale PDF, and the `.ses` — is produced by the **`show-deep-build`
skill**, which reads the brief. The app hands the skill clean facts and gets out
of the EQ business.

```
ShowBuilder app            show-deep-build skill (Cowork / Claude Code)
---------------            --------------------------------------------
capture input list   -->   read <Show>.brief.json
+ metadata                 research artist + genre (web)
+ free-text notes          research each source (mic×instr×genre×venue) via eq-advisor
export brief.json    -->   MINE the notes -> research amps / techniques / etc.
                           write <Show>.spec.json (+ EQ, mic_notes, eq_summary, changes)
                           build_packet.py -> .md, .xlsx, Show Packet PDF, EQ Rationale PDF
                           venue patcher   -> <Show>.ses  (byte-verified)
```

**The app never writes EQ. The skill never re-keys the input list.**

### Why the change

The app used to generate EQ instantly from KB/template defaults. That produced
generic — sometimes wrong — values (a template once bled "D6/Beta 91A blend" notes
onto a show with no D6). EQ done right needs the artist + every source researched
with the *why* recorded. That work lives in the skill now.

---

## The brief — `<Show>.brief.json` (the contract)

Facts only. Schema in `backend/brief.py`:

```jsonc
{
  "show_name", "artist", "genre",            // genre = free-text hint, a fact not EQ (added 2026-07-01)
  "venue", "venue_label", "console_label",   // console_label drives the downstream patcher path
  "show_date", "foh_engineer", "mon_engineer", "show_time", "rev",
  "show_notes": "free text, mined verbatim",
  "channels": [
    { "ch", "name", "instrument", "mic", "section",
      "phantom", "ribbon", "stand", "patch", "notes" }
  ],
  "app_version": "brief-1.0"
}
```

Hard rules, enforced by `selftest_brief.py`:
- **No EQ fields** — no `hpf`/`lpf`/`bands`/`comp`/`gate`/`mic_notes`/`eq_summary`,
  no `eq_on`/`comp_on`/`reverbs`, ever.
- `notes` and `show_notes` are **preserved verbatim** — never validated, trimmed,
  or normalized. They carry amps, miking techniques, tunings, stage requests — the
  skill mines and researches them.
- A true spare channel is **omitted**, not emitted blank.

The app fills only no-EQ facts the engineer didn't type: `section` from the
instrument (`knowledge`), `ribbon`/`phantom` from the mic library, `patch` default
`Local <ch>` (the wizard has a Patch column for explicit overrides like Dante),
and the Memo crowd rig as facts-only `AMBIENT` channels (`ch=null`).

### Wizard behavior added 2026-07-01

- **32-channel baseline** — every show starts with 32 rows (venue defaults like
  FSQ's named 32 win when defined; crowd rig is on top, never counted).
- **Autosave draft** (localStorage, `sb_draft_v1`) with a Restore/Discard banner;
  cleared on successful export.
- **Import brief…** — repopulate the wizard from an existing `.brief.json`
  (crowd rows dropped, implicit `Local <ch>` patches stripped, padded to 32).
- **Guards** — venue-switch/Set-rows confirm before wiping typed channels;
  review warns on duplicate/missing CH numbers; Mac export returns **409** when
  the brief exists and the client confirms overwrite (`overwrite: true` re-post).
- **Server** — `GET /health` (unauthenticated); package role writes every export
  to `inbox/` and serves `GET /api/briefs` (list) + `GET /api/briefs/<name>`
  (download). Auth cookie = HMAC(passcode + per-boot secret), `Secure` in package
  role, wrong-passcode attempts slowed per IP.
- **Mobile** — under 760px the channel/review tables render as stacked cards
  (the package instance is meant to be used from a phone at the venue).

---

## Where it runs

| Instance | URL | Role | On export |
|---|---|---|---|
| Mac (local) | http://localhost:8095 (`./run.sh`) | `mac` | writes `<Show>.brief.json` into the show folder |
| Mac (native app) | `mac/ShowBuilder.app` (Dock) | `mac` | same |
| Proxmox (n8n VM) | https://showbuilder.tinydoorstudios.com | `package` | returns the brief as a **download** (no `audio_root`) |

`config.write_enabled` = has an `audio_root` **and** role ≠ `package`. The package
instance just hands back the JSON; Brian drops it into the show folder on the Mac
and runs the deep build there.

---

## Project map

```
Code/ShowBuilder/
  backend/
    brief.py            Brief + BriefChannel — the facts-only export model
    app.py              aiohttp server: wizard + /api/bootstrap + /api/brief; passcode gate
    knowledge.py        loads knowledge/*.json; venue/instrument/mic/genre lookups
    mic_library.py      mic-name helpers
    selftest_brief.py   exports a 19ch FSQ Izzy brief, asserts no-EQ-keys + verbatim notes
    _deprecated/        FROZEN pre-2026-06-25 EQ/build pipeline (eq_engine, reverb_engine,
                        build, engine, spec, buildpkg, build_knowledge, harvest, selftest).
                        Self-contained package, not imported by the live app. Reference only.
  knowledge/            venues / mics / eq_rules (instruments+genres+aliases) / reverb_presets
  web/                  index.html · app.js · style.css  — wizard: Show → Channels → Export brief
  deploy/              showbuilder.service · showbuilder.env.example · DEPLOY.md
  docs/HANDOFF.md      (this file)
  config.json · run.sh · README.md
  _archive/learning/   legacy runtime data (moved 2026-07-01; `shows/` was empty and removed)
  inbox/               package role only: server-side copy of every exported brief (gitignored territory — excluded from deploys)
```

> Note: `knowledge/eq_rules.json` and `reverb_presets.json` are still loaded by
> `knowledge.py` (it reads them at init) but only the instrument/genre/mic maps are
> used now. They're harmless reference data; leave them.

---

## Run / verify

```bash
cd ~/Documents/Claude/Code/ShowBuilder && ./run.sh        # http://localhost:8095

# acceptance / smoke (no server): exports a facts-only Izzy brief and asserts the contract
.venv/bin/python backend/selftest_brief.py
```

The export lands at `audio/<Venue>/YYYY-MM-DD ShowName/<Show>.brief.json`. Then in
Cowork: *"deep build <show>"* → the skill produces the `.md`, xlsx, Show Packet
PDF, EQ Rationale PDF, and the `.ses`. Console verify, then `wiki-publish`.

---

## Acceptance (done 2026-06-25)

- `selftest_brief.py` PASS — a 19-channel FSQ Izzy brief exported with amp +
  miking-technique notes on Guitar 57 / Bass Mic / Kick In; asserted **no EQ keys**
  leaked and notes/`show_notes` round-tripped **verbatim**. Output:
  `Fountain Square/2026-06-26 Izzy Escobar (Brief Test)/Izzy_Escobar_Brief_Test.brief.json`.
- Live HTTP path exercised: `/api/bootstrap` (8 venues, FSQ 32-ch default pre-fill)
  and `POST /api/brief` (Memo show → brief written, 6 crowd-rig channels appended,
  AEA R88 flagged `ribbon`/NO 48V, notes verbatim incl. `<&>`).
- The **downstream half** of the handoff's acceptance (skill builds the 5 paperwork
  files + a passing `.ses`, EQ Rationale `changes` box reflects the mined amp/technique)
  is a `show-deep-build` run in Cowork — that's the skill's job, not the app's, and
  is the next step Brian drives (it ends at the console hard-stop regardless).

---

## Deploy (Proxmox package instance)

Unchanged from before except the payload is now a brief, not a spec. The redeploy
rsync + restart, the env file, and the remote-managed cloudflared route are all in
`deploy/DEPLOY.md`. The instance runs with `SHOWBUILDER_ROLE=package` / empty
`AUDIO_ROOT`, so `/api/brief` returns a download.

```bash
rsync -az --delete --exclude .venv --exclude __pycache__ --exclude 'shows/*' \
  --exclude 'learning/*' --exclude .DS_Store --exclude .claude --exclude '*.log' \
  -e "ssh -i ~/.ssh/proxmox_tds -J tds" \
  ~/Documents/Claude/Code/ShowBuilder/ brian@192.168.200.84:/opt/showbuilder/ \
&& ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'sudo systemctl restart showbuilder'
```

---

## Don't break

- The brief stays **facts-only** — adding an EQ field re-creates the exact problem
  this rework removed. `selftest_brief.py` guards it.
- **Notes are sacred** — never strip/normalize `notes` or `show_notes`. They're the
  skill's research hooks.
- Folder/naming convention `<Venue>/YYYY-MM-DD ShowName/`.
- Input vocabulary: full mic names (no shorthand), `Local N` patch labels, stand
  words (Short/Tall/Boom/Bar/Clip/DI/—), ribbon/48V.
- The `.ses` patcher + its calibration live in the audio tree (`Fountain Square/Q225
  SES Patcher SOP/`, etc.) and belong to the **skill** now — the app must not write
  `.ses` or the channel-processing `.md`.

---

## If you ever need the old EQ engine

It's frozen, intact, and importable in `backend/_deprecated/` (relative imports
resolve within that sub-package). It is **not** the path forward — EQ generation
moved to `show-deep-build` deliberately — but it documents the prior logic
(genre/venue/mic layering, blends, tom voicing, Memo crowd-rig EQ) if a question
comes up.
