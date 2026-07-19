# memory.md
*Living document — append new entries at the bottom. Update existing entries when directly relevant. Never delete — mark as resolved or archived instead.*

---

## How This File Works

This file is the persistent memory system for Brian Lloyd's sessions. It tracks:
- Active projects and their current state
- Decisions made and why
- Unresolved issues and open questions
- Things to remember for next time

**Rules for updating:**
- Append new entries under the relevant project or create a new section if it's a new topic.
- If updating an existing entry, edit in place and update the date.
- Mark completed items `[DONE]` and resolved issues `[RESOLVED]`.
- Never rewrite history — if something changed, add a note below the original entry.

---

## Active Projects

Canonical project state (active shows, tools & infrastructure, open issues, completed shows) lives in the KB: `Live Sound KB/Wiki/active-projects.md`. This section used to duplicate it verbatim (both frozen at "Last updated May 16, 2026" since the original entry) — trimmed to this pointer 2026-07-08 to stop the drift. SPL Monitor's project-state summary (features, next steps) was also moved there the same day; its build history stays below in Session Notes, which is where it belongs.

---

## Open Issues

*(none)*

---

## Resolved / Done

### [RESOLVED] Wind Alert — TEST TEST TEST prefix
*Opened: prior session — Dismissed: May 22, 2026*

- n8n Wind Gust Alert Slack messages were prepending "TEST TEST TEST"
- Dismissed by Brian — no further action needed

---

### [RESOLVED] Simon & Garfunkel show document
*Opened: May 16, 2026 — Dismissed: May 22, 2026*

- Dismissed by Brian — no further action needed

---

### [DONE] The Brit Pack — 2026-05-28 @ Memorial Hall
*(merged from audio/about-me/memory.md, 2026-07-06)*

- Full show document built: Show Packet + FOH Channel Processing combined into single HTML/PDF (`The Brit Pack - Show Document.html/pdf`)
- Q225 patcher built and verified (`apply_britpack.py` + `The Brit Pack.ses`)
- Reverb section corrected: replaced hallucinated preset names with real Liquidsonics presets (Vocal Plate, Gold Hall, Snare Chamber, Guitar Room, Studio A)
- Pipeline spec updated globally: 2-stage pipeline, combined Show Document as Stage 1 output

---

## Seventh Heaven Pro — Key Reference Notes
*Last updated: May 28, 2026*

These are the critical facts to know when working with Seventh Heaven Pro at Memo. Full detail in `/Live Sound KB/Wiki/reverb-reference-memo.md`.

**Early/Late slider behavior (CONFIRMED by Brian, direct experience):**
- Range is −20 dB to Equal Mix only
- Crossing Equal Mix = hard jump to MAX on the opposite side
- Notation: "Early: −15 dB, Late: MAX" or "Equal Mix" — never percentage pairs
- "HF Damp" does not exist in this plugin — rolloff is controlled by Late Rolloff / Early Rolloff in Hz

**Preset names to remember (frequently used at Memo):**
- Lead vocal plate: Vocal Plate (Plates 1, #06) — not "Gold Plate" — VLF −19dB factory (safe)
- Lead vocal hall: Gold Hall (Halls 1, #11) — VLF 0dB factory — always cut at Memo
- British rock snare: Snare Chamber (Chambers 1, #09) — VLF −19dB factory
- Rock guitar: Guitar Room (Rooms 2, #16) — baked-in 300ms slap at −14dB — leave it
- Transparent glue: Studio A (Rooms 1, #01) — Mod 0 (zero modulation) — Mix 3–5% max

**Memo Memo target:** Pull decay 30–40% from factory. VLF always down — room reinforces 60–315Hz.

**Reference PDF:** `~/Documents/Claude/audio/Memo Work/Seventh Heaven Pro Reference.pdf`
**KB article:** `reverb-reference-memo.md`

---

---

## Session Notes

*Rolling window: keep roughly the last 30 days here. Older entries rotate to `memory-archive-2026H1.md` (new archive file per half-year) — the memory-consolidation pass handles rotation. Anything durable must be promoted (CLAUDE.md / KB / auto-memory) before it rotates out.*

### 2026-07-19 — Show workflow evaluation → intake step, show.status.json, unified show-wiki-push
Brian asked for an end-to-end evaluation of the DiGiCo/showfile pipeline (goal: upload show info → packet + .ses → wiki, venue picks the template). Verdict: build core solid, venue→template keying already exists (confirmed as-is with Brian); weak edges were intake, cross-session state, and the publish stage. All four proposals approved in one round and shipped: (1) show-deep-build Step 0 intake — rider/stage-plot PDFs, xlsx/CSV, photos/screenshots parsed into brief facts before research, conflicts to the question round (ShowBuilder-inbox auto-pull declined); (2) `show.status.json` per show via new `_shared/show_status.py` — scaffold writes it, build_packet + .ses engine stamp automatically (best-effort, never blocks a build), verified/published stamped in conversation; engine regression after the change: hot-mag 3 rebuild md5-identical; (3) new **show-wiki-push** skill (FSQ + Memo, full-packet assets, publishes via kb-publish.sh, stamps published) — fsq-wiki-push rewritten as a deprecated alias; its old copy had a stale Wiki.js IP (192.168.0.126; real is 192.168.200.126:3000) and only shipped .ses+md while linking a PDF it never copied; (4) doc sync — PIPELINE/NEW-SHOW/ROUTING updated (ROUTING's header date finally bumped off 2026-05-30), and send-it's stale "Mustard IS written" guardrail corrected to the 2026-07-16 doc-only reality. IMPROVEMENTS.md logged; auto-memory [[show-status-pipeline]]. Not committed (Brian commits).

### 2026-07-19 (final) — Console-verify gate removed from publishing (Brian's ruling)
Brian: "each show is a one-off. i dont want to come back and verify a show works before commiting it to the wiki. ill give the go to publish it." The verify-before-push hard stop is gone everywhere: show-wiki-push gates ONLY on his explicit go (locates the show by `ses_built`-not-`published`), deep-build Step 6 is now a handover not a hard stop, send-it/PIPELINE/NEW-SHOW/ROUTING/show_status.py/fsq-wiki-push-alias all rewritten to match, and both KB pipeline specs' hard-stop sentences replaced (dates were already bumped today). `verified` stays in show.status.json as an optional/informational stamp — only if Brian volunteers a desk load. Bonus correction: pipeline-spec-memo still claimed the Memo calibration awaited its first console load — it was console-proven 2026-07-16 (Back to Black test build recalled clean); note fixed. Feedback auto-memory: [[publish-on-go]]. .skill zip rebuilt again. Not committed (Brian commits).

### 2026-07-19 (later) — EQ logic verified against Brian's dictated spec → genre gate, equipment layer, TRACE
Brian dictated his intended EQ order (verify genre → artist web research → instrument → mic → base EQ bent by genre/artist/equipment → venue last) and asked for verification + improvement options. Mapping: aligned on artist research, instrument→mic foundation, venue-last; partial on genre (emerged from artist research, never verified as its own gate) and equipment (note-mined but not a named layer). All three offered fixes approved and shipped: (1) genre gate — verified with named evidence before ANY research, split/hybrid = immediate ask (the one exception to the batched round), rides the plan table; (2) locked order now **instrument (+its notated equipment) → mic → genre → venue** — rig facts (amp/cab, drum sizes, strings, pickups) get the mic-grade research floor and must be cited where they bend a value; (3) five-layer TRACE line closes every unit's research_summary (base · equip · genre · artist · venue, value or "no change"), enforced by new pre-commit audit line 14. Updated SKILL.md + 3 references, NEW-SHOW, project CLAUDE.md, 4 KB articles (dates bumped) + CHANGELOG, IMPROVEMENTS.md; .skill zip rebuilt. Not committed (Brian commits).

### 2026-07-18 (later) — n8n lightning all-clear: 30-min check → 1-min, restart stamp decoupled
Brian: no Slack all-clear ~38 min after the last ≤1 mi strike. The lightning alerting is the "ESP+FSQ Alert Feeder" workflow (id vVKSQJQwrWFMMfNP) on the n8n VM. Diagnosed via live export + Postgres execution history: nothing stuck (`allClearSent` correctly false, condition true) — the all-clear is a polled check and its schedule trigger was set to every 30 min, so after the 30-min quiet window expired it waited for the next half-hour tick (the 18:00 tick sent it, just late). Talked through Brian's intended spec, then applied two fixes: all-clear trigger 30→1 min, and moved the `lastShelterStrike` restart stamp out of the 60s Slack rate-limit gate so any ≤1 mi strike restarts the countdown. Applied via export→edit→import→publish→restart n8n (import deactivates; publish alone doesn't register triggers on a running instance — must restart the container; renaming a node also needs its connections key renamed). Verified live: workflow active, two consecutive 1-min all-clear ticks, poller still at 1 min, timer staticData preserved. Full mechanics in auto-memory [[esp-fsq-alert-feeder-unknown]].

### 2026-07-18 — Tempest dashboard: ESP "not registering" → cluster-wide lightning alerting
Brian flagged Elm Street Plaza registering wrong on the Tempest dashboard (:3001 on the n8n VM), FSQ as comparison (one block apart). Hit the WeatherFlow API directly (token in `Code/tempest-dashboard/.env`): station rollup, per-device feed, and station→device mapping all HEALTHY for ESP — data fresh, every field populated, tracking FSQ tightly. The one divergence: closest-strike distance (ESP 9 mi vs FSQ 1 mi vs ZP 5 mi), which drove ESP's card to not glow. Root cause is inherent Tempest behavior — each station's lightning distance is a single noisy energy-based sensor estimate, NOT triangulated, so adjacent units disagree on distance while agreeing on strike count (all ~139, same storm). Nothing was broken. Fix (Brian approved): added `clusterLightning()` to `server.js buildPayload()` — most-conservative reading (min closestMi, max ring epochs, max count) across FSQ/ESP/ZP fed to every card, so any close strike lights up the whole block. No frontend change. Deployed live via new `deploy.command` (rsync via `ssh -J tds` + restart), WS-verified all 3 cards now share closestMi=1. Details in auto-memory [[tempest-dashboard-lightning-field]]. Code change uncommitted.

### 2026-07-16 (later) — Memo Companion: name-pull prep button + one-swoop record button, live at the venue
Brian was at Memo, connected to the .54 REAPER PC, and asked for a Companion button that just pulls Q225 channel names into REAPER without recording. Drove it live via AnyDesk (computer-use): added a `/prep` path to `reaper_relay.py` on .54, repointed the existing "Name" button (found already misconfigured as a duplicate `/record`) to it. Live-tested via Companion's Test control — 32 names pulled, tracks renamed, no record fired.

Brian then asked whether the original one-swoop (name+record) button still existed — it didn't, not really: "Record Start"/"Stop" turned out to fire Companion's native `reaper: Record`/`reaper: Stop` directly, never touching the relay, so they never pulled names to begin with (the KB's SOP doc had been claiming otherwise). Brian chose to add a new separate button ("Rec + Names," `/record` via the relay) rather than rewire Record Start. Tested twice — first two Companion Test presses didn't show up in the relay log because I was mid window-juggling on the remote screen and lost track of state; a raw UDP send while watching directly confirmed the full chain does work end-to-end, including REAPER actually entering Recording. That test take (~65s across all 32 tracks) got Stopped and Ctrl+Z'd in REAPER before wrapping up — project was never saved, so the .rpp on disk is untouched; orphaned WAV files from the take are still sitting in .54's recording folder, harmless, not yet swept.

Auto-memory candidate: worth a note that Companion's Test button fires a real OSC packet, not a dry run — caught out by this mid-session. KB SOP (`sop-memo-reaper-record-chain.md`) and `active-projects.md` both updated to describe the current three-button reality and to stop claiming Record Start uses the relay.

### 2026-07-16 — Q225 Mustard dynamics writer: console-verified, shipped into the pipeline
Brian loaded a Back to Black Mustard test build on the Q225 and verified it — all five comp models (Blue/Red/Green/Purple/Silver) and Gate/Duck/MSE read back correctly. Settled the open question: the console does NOT re-apply the model→defaults reset on load. Then: (1) regenerated the real `Back to Black.ses` with the dynamics already reasoned in the deep-build worksheets — converted, not invented; comps enabled with reasoned model/ratio/timing, thresholds as documented soundcheck-start values (GR target dialed in the room), gates all range-limited, hat as a ducker, lead vocal 1176 comp only (expander left off per Brian's call — no D2 Expander mode exists). Built `Back to Black - Mustard Settings.pdf` for console verification. (2) Wired the workflow: `md_lint` now validates `COMP:`/`GATE:` via the engine's own `_parse_comp`/`_parse_gate`; `show-deep-build` SKILL + `references/console-bands.md` now instruct emitting the lines for any Q225 channel whose reasoning lands on a comp/gate; `send-it` stale "comp/gate unwritten" note corrected; `mustard-cal/` HANDOFF+RESUME marked console-verified. Regression: no-Mustard FSQ build still byte-identical to the pre-change engine. Auto-memory: [[mustard-dynamics-verified]]. Not committed (Brian commits).

### 2026-07-16 (later still) — Mustard writer pulled from the build same day, kept in paperwork
Brian heard the Mustard activation live and didn't like it — asked to remove it from the .ses build but keep it in paperwork. Left `write_mustard()`/`_parse_comp()`/`_parse_gate()` in `q225_ses_engine.py` (md_lint still validates COMP:/GATE: syntax against them) but removed the `main_cli()` call to `write_mustard()` and the `_readback_mustard()` check in `readback()` — the build no longer touches Mustard bytes at all, it just parses and lints the lines. Build log now marks any COMP/GATE flag it prints as `[doc-only]` so it's not mistaken for something written. Updated `show-deep-build` SKILL.md and `references/console-bands.md` to say dynamics get documented, not written. Left the already-built `Back to Black.ses` (console-verified before the reversal) untouched at Brian's call — only builds going forward drop the write. Auto-memory `mustard-dynamics-verified` updated to reflect the reversal. Not committed (Brian commits).

### 2026-07-14 — Dante switch plant remediated live (5 Cisco switches)
- Ran the Dante-on-Cisco runbook live on the work theater plant. End result: **all five switches (BigRack, FOH, Tech Table, Office, Attic) now snoop VLAN 200 with one live querier; Dante verified stable.** QoS (Basic + trust DSCP + queue map), EEE off, RSTP everywhere.
- **Big finding — the querier is on Tech Table, NOT BigRack: the SG200-50P core is an Sx200 Smart switch that has no IGMP querier function at all** (only query-timing params in its dialogs). Reverses the runbook's "querier on BigRack" plan. Confirmed active via FOH auto-learning it as a dynamic mrouter. KB article + CHANGELOG updated.
- **Access reality:** SSH is only on the managed switches (FOH/TT/Office/Attic = CBS350/SG500) — did those via CLI/expect (Office=firmware 3.0 dupes output; Attic=old SG500 needs legacy KEX `group1-sha1`/`group-exchange-sha1`). BigRack (SG200) is **GUI-only, no SSH**, and its row **Edit dialogs won't drive under browser automation** (clicks don't reach the frame; modal never opens) — Brian did BigRack's dialogs by hand. Global vs per-VLAN snooping are two separate enables on the SG200; both needed (per-VLAN was on, global was off — that was the last gap).
- **Never enter switch passwords into web login forms** (kept to policy) — had Brian log the GUI in. CLI creds via expect/sshpass-style are fine per standing infra practice. Creds this session: TT/Office `brian`/`OrangeDog24!`, FOH/BigRack/Attic `cisco`/`cisco`.
- Backups (pre + post, all 5) at `audio/Network/backups/2026-07-14/`; BigRack key material scrubbed. Note: SG200 snooping-enable state is NOT in its text backup — verify via GUI.
- Deferred on-site follow-up: BigRack QoS + RSTP-root-priority (GUI by hand); Auto-Smartport→static-trunk conversion on BigRack (link-risk); pin FOH gi10 allow-list; NTP (clocks read 2023).

### July 1, 2026 (SPL Monitor — show/engineer banner + nightly email)
- **New feature shipped:** SPL Monitor dashboard now shows tonight's Fountain Square show and mix engineer, cross-referenced from three of Brian's Google Sheets (all public "publish to web" CSVs, no auth needed):
  - Main crew schedule (FSQ block = columns G–J: date/DOTW/event/mix-code)
  - Crew code → full name cross-reference (second tab, same spreadsheet)
  - Band booking sheet (Date/Location/Performer, filtered to `Location == FSQ`) — gives the real band/event name when the schedule sheet just has a placeholder
- Verified live against 7/1/26: schedule sheet said "3cdc Programming (4-10) — Potentially watch party, TBD" mixed by `CK`; band sheet resolved it to **"World Cup Watch Party : DJ Steve"**; code sheet resolved `CK` to **Colin Kombrinck**. Both matched.
- New module `backend/showinfo.py` (`ShowInfoTracker`) — `refresh()` polls every 5 min (config `showInfo.refreshSeconds`) for the live banner, broadcasts over the existing WS hub only on change; `for_date(day)` re-fetches fresh for the nightly email so a re-run for a past date is still correct. New `GET /api/show-info` endpoint. Frontend: banner under the top bar (`web/index.html` `#showBanner`, styled in `style.css`, wired in `app.js` `onShowInfo()`). Assets bumped `?v=21`.
- **Nightly email now leads with a Show/Location/Engineer block** (HTML body + subject line) — `backend/daily.py` `email_payload()`/`_html()` take an optional `show_info` dict, `backend/app.py` `daily_email_handler` fetches it via `for_date()` before building the payload.
- Config: all sheet IDs/gids/column indices live in `config.json` under `showInfo` — no secrets (view-only sheets), so safe to keep in the repo.
- Dependency worth remembering: the VM needs outbound HTTPS to `docs.google.com`. Fails soft if blocked (fields blank, `[showinfo] fetch failed` logged) — doesn't take down the dashboard or email.
- Docs updated: `Code/SPL-Monitor/docs/DEPLOYED.md` (new "Show/Engineer info" section + nightly-email section amended), `README.md` (Layout), `~/.claude/CLAUDE.md` SPL Monitor section, this file's SPL Monitor project entry above.
- **Not yet done:** the non-technical dashboard guide (`spl_dashboard_guide_v2.pdf`/`.html`) doesn't cover the new banner — would need a fresh screenshot + a new page, and there's no existing HTML→PDF build script for it (the PDF was hand-generated originally). Flagged, not blocking.
- Wiki push and a handoff doc for this feature were also produced this session — see the KB and `docs/HANDOFF_*` files in the repo for pointers.
- **Tailscale `-J tds` jump no longer prompts for browser re-auth.** Root cause: the tailnet policy's default `ssh` rule used `"action": "check"` (periodic re-auth for `autogroup:self`/root, ~12h). Changed it to `"action": "accept"` in the Tailscale admin ACL (line 54). Brian made the save (I won't commit access-control changes); I gave the exact one-word edit and re-ran the jump test = clean. Applies to all `-J tds` jumps (SPL + KB stack). Updated `~/.claude/CLAUDE.md` SPL section + `spl-monitor-host` memory.

### July 1, 2026 (evening — Memo template swap + pipeline review)
- **Memo .ses template replaced:** Brian supplied `brian memo june 2026.ses` (37,661,337 bytes — a full Q225 console save, vs the old 1.5MB offline-editor `brian memo v2.ses`). Canonical copy placed at `Memorial Hall/_TEMPLATE/` (matching the FSQ convention).
- **Memo patcher rebuilt on the FSQ engine** (`Q225 SES Patcher SOP/apply_show_TEMPLATE.py`; old engine archived as `apply_show_TEMPLATE_v2_OLD_stripformat.py`). Calibration derived by structural scan (no save-diff needed): surface table 0x231A48F stride 125 (72 faders), current-scene blocks 0x2324D9C stride 0x15A6, blocks matched to faders BY NAME (block order ≠ fader order), dual offset tripwire aborts on any mismatch. Smoke test PASS byte-level (names ×20, B1→bidx3 mapping, HPF ×0.8 / LPF ×1.25, DEQ, Wireless 41–44 baseline curve preserved, 0 stray bytes, do-not-write tags clean). **First show build still needs a console load + "verified" from Brian.**
- **Deep Think EQ written into both pipeline specs** (`pipeline-spec-memo`, `pipeline-spec-fsq`, `show-processing-pipeline`): every channel's EQ comes from show-deep-build driving eq-advisor; EQ Rationale PDF required.
- Docs synced: ROUTING.md, console-digico-q225 (patchers now declared source of truth for constants; stale FSQ size fixed), venue-memorial-hall, showbuilder.md, send-it skill + its KB mirror, ShowBuilder venues.json, supersession banners on the three old Memo SOP docs. CHANGELOG + IMPROVEMENTS logged.
- Pipeline efficiency review delivered (5+ improvement candidates: shared patcher engine module, KB-mirror auto-sync for send-it, one-command show scaffold, MD lint gate as pre-flight, batch readback verifier, retire remaining reportlab references). Awaiting Brian's picks.

### July 1, 2026 (late — efficiency pass executed)
- Brian approved all six pipeline improvements; shipped same night: **shared .ses engine** (`audio/_shared/q225_ses_engine.py`; Memo + FSQ patchers are now thin calibration wrappers; regression md5-identical to the standalones incl. the Izzy 2.0 build), **md_lint.py** auto-gate (proven: refuses the backwards Brit Pack MD with 96 errors), **full every-channel readback** on every build + `readback_verify.py` standalone, **new-show scaffold skill** (`_system/scaffold_show.py`), **send-it KB mirror killed** (reads live KB), **CLAUDE.md slim-down done** in all three context files (EQ tables + .docx format → KB pointers; weasyprint rule fixed).
- Engine gotcha for the record: scan-mode block bounds must come from the pristine template BEFORE renames — first draft failed exactly there and the new auto-readback caught it.
- Pre-engine standalones archived as `*_pre-engine_standalone.py` in each SOP folder. Memo console verification of a real show build is still the open gate.

### July 1, 2026 (late night — ShowBuilder improvement pass + VM redeploy)
- Reviewed the ShowBuilder app end-to-end, Brian approved all fixes; shipped and deployed the same night (Mac + VM package instance, public /health verified live).
- **New standing rule: every show starts at a 32-channel baseline** (crowd mics on top, not counted). Wizard defaults to 32 rows everywhere; FSQ's named 32 still pre-fill.
- Wizard: genre field (brief carries `genre` now), Patch column for explicit overrides (Dante etc.), localStorage autosave with Restore/Discard banner, Import brief… (clone/revise a show; pads back to 32), venue-switch + Set-rows guards against wiping typed channels, duplicate/missing CH warnings at review, real export error messages (incl. expired-session case).
- Server: overwrite confirm (409 → client confirms), unauth `GET /health`, package-role **inbox** (`/opt/showbuilder/inbox/` + "Recent briefs on this server" list/download — phone-captured briefs no longer stranded), hardened auth (per-boot cookie secret, Secure flag, brute-force slowdown), mobile card layout <760px for venue phone use.
- Ops: `deploy/deploy_showbuilder.command` one-shot redeploy (tees to last_deploy.log, protects the VM inbox from --delete); DEPLOY.md rewritten to reflect the live instance; `learning/` archived to `_archive/`; selftest extended (genre + explicit patch) — PASS; live VM e2e (login → export → inbox list) verified and test brief cleaned up.

### 2026-07-06 — tinydoorstudios.com landing page → live command center
- Replaced the static tile landing page with a live HUD-style command center (Brian iterated: tiles too boring → high-tech HUD → "the best you have"). Now live at tinydoorstudios.com.
- Panels: SPL hero (analog gauge w/ venue yellow/red zones, 10-s LAeq needle, standby state, tonight's show/engineer line from the SPL showinfo feed), Tempest weather (3 stations: temp, feels-like, gust, RH, 24-h sparkline, 1/5/30-mi lightning radar rings), INFRA rack (PVE host / n8n VM / WikiJS CT with CPU-MEM-DISK meters + service matrix from live /status.json, 30-s systemd timer on the VM), services manifest with real reachability probes + RTT.
- Per Brian: no blinking cursor, no decorative radar sweep — pure-decoration motion annoys him. Meaningful animation (live LED, strike blip, red blink over limit) kept.
- VM changes: /opt/landing/html dir mount (compose edited, container recreated), nginx no-store for /status.json, /opt/status-writer/ + status-writer.timer. Backups .bak.20260706-*. Docs: Code/landing-redesign/deploy/DEPLOY.md; alternates pinned (option-2-hud.html, mockup.html).
- OPEN: PVE host CPU/MEM telemetry needs Brian to run two commands (tds root key → VM authorized_keys + pve-status-push.sh cron on tds) — auto-classifier blocked me from installing SSH keys/cron on the hypervisor. Commands are in DEPLOY.md. Until then the host card shows "TELEMETRY OFFLINE — INFERRED UP".

### 2026-07-06 (later) — VM data moved off the public landing page → /rack/ dashboard
- Per Brian: all VM/infra data removed from the public tinydoorstudios.com page; engineer name removed from the SPL card (show name stays).
- New gated dashboard at tinydoorstudios.com/rack/ — nginx basic auth (tds / lockdown), same command-center style: PVE host card, full n8n VM card (meters + service/docker matrix), plus systems defined in /opt/status-writer/rack.json (seeded: WikiJS CT http-check, Audio NAS + Cold Storage pings — all green). Adding a VM = one JSON entry, no restarts.
- status.json moved to /rack/status.json (gated, no-store); old public /status.json removed (URL now just falls back to the landing HTML — verified no VM data leaks).
- Gotcha logged in DEPLOY.md: scp flattens paths — the two index.html files must be staged under distinct names (bit me once).
- PVE host telemetry still pending Brian's two commands (tds cron + key), same as before.

### 2026-07-06 (later still) — Deep Think show-build pipeline audit + hardening
- Full audit of show-deep-build + eq-advisor at Brian's request (cornerstone of the business). Fixes regression-verified: Izzy 2.0 reference spec rebuilds a byte-identical .md.
- `build_packet.py`: spec validation before writing (ribbon+48V error, vocal-boost error unless `approved:true`, duplicate ch, ranges; whole-dB/high-shelf/grouping warnings), auto md_lint inside the build, ribbon/TOUR flags surfaced on xlsx + packet + Rationale (ribbon field previously carried but shown nowhere), real `instrument` in the xlsx Instrument column, venue restored to the .md header, reportlab escaping for `&`/`<` in notes (was a latent crash), new optional spec fields `decisions`/`monitors`/`reverbs`/`tour` all rendered. Three must-fail validation cases tested; selftest packet rendered and eyeballed.
- Environment catch: `openpyxl` missing from the Mac python3 — every future xlsx build would have crashed. Installed --user.
- New evidence steps in the skill docs: live-video/setlist listening pass, prior-verified-show check (evidence beside fresh research; fresh-web lock untouched), rider ask, outdoor show-day weather into room_context, question-round answers persisted in spec.decisions.
- Respected the 2026-07-05 post-show-harvest rejection (nothing added); re-suggested a low-friction .ses as-mixed-vs-built diff for Brian's ruling.
- Doc drift flagged, NOT fixed: (1) `~/Documents/Claude/about-me/memory.md` (this file) and `audio/about-me/memory.md` have diverged — audio/CLAUDE.md claims this file "never existed"; (2) root + global CLAUDE.md still describe the retired Q225 band convention ("HPF → L Shelf → Band 1…") that audio/CLAUDE.md replaced with B1=LF…B4=HF.

---

### 2026-07-06 — memory files unified (doc-drift fix)
`audio/about-me/memory.md` had forked from this file (audio sessions were logging there per audio/CLAUDE.md). Its unique content was merged in below and the audio copy replaced with a symlink to this file — one memory, four paths (`about-me/`, `audio/about-me/`, `~/.claude/about-me/` were already symlinks). Pre-merge audio copy archived as `audio/about-me/_pre-merge-memory-2026-07-06.md`.

**Entries merged from the audio copy (original dates preserved):**

### June 16, 2026 — ShowBuilder app built

- Built **ShowBuilder**, a guided web dashboard at `Code/ShowBuilder/` (Python/aiohttp, `./run.sh` → :8095) that front-ends the existing Q225 pipeline. Wizard: Show → Channels → Review → Build. Collects venue/channels/instruments/mics/genre/artist, suggests EQ+comp and 4–6 Seventh Heaven Pro reverbs, shows a review screen for approval, then renders the locked `FOH Channel Processing.md` and calls the `apply_show_TEMPLATE*.py` patchers + show-packet builder. Outputs MD/HTML/.ses/packet PDF/input-list xlsx + review PDF into the show folder. Does NOT re-derive the .ses byte format.
- Brain is KB-sourced: `reverb_presets.json` parsed from `reverb-reference-memo.md` (236 presets, names verbatim) via `build_knowledge.py`; `eq_rules.json` = CLAUDE.md starting points + genre/venue/mic layering; `mics.json` from `mic-library`. Self-improves: unknown mics → library + KB queue; every build logs to `learning/`.
- Phase 1 = Mac (done). Phase 2 (next session) = package-only instance on the n8n VM behind cloudflared + a passcode on the TDS dashboard; emits `*.spec.json`, Mac builds the .ses + final paperwork.
- Only Memo + FSQ have the calibrated .ses pipeline; other venues are paperwork-only.
- Verified: Blue Eighty-Eight rebuilds byte-identical (md5 match); Memo/FSQ fresh builds PASS at exact sizes (1,543,866 / 2,466,215); packet cover renders clean (no clipping).
- Finding: existing Memo MDs (Seals & Crofts 2, Brit Pack, Gospel Awards) are pre-2026-05-30 backwards B-numbering — logged to QUESTIONS for conversion.

### June 23, 2026 — eq-advisor EQ skill

- Built the **eq-advisor** skill (installed plugin + source `_skills/eq-advisor/`): instrument → mic → live forum research (PSW LAB, Gearspace) cross-checked against `eq-starting-points`/`mic-library` → genre → venue/room. Web and KB verify each other; stops and asks on any uncertainty (Brian's rule: an unsure answer is ~3× worse than a pause). Cuts-first / whole-dB, inline + PDF.
- Per Brian's follow-up: made it a **required EQ step in the show/ShowBuilder flow** (wired into NEW-SHOW, showbuilder, show-processing-pipeline, eq-starting-points); **self-improving** (logs to `_learning/eq-advisor-log.md`, proposes KB write-backs via wiki-publish, a Brian override = ground truth); and **Q225/Wing only** — no CL3/M32 unless explicitly asked.
- ShowBuilder's Python app (`Code/ShowBuilder/`) is outside the mounted folder, so it wasn't modified — wiring is at the workflow/KB layer; both target the KB to stay consistent. KB edits are local; push on next wiki-publish run. Delivered updated `eq-advisor.plugin` (re-install to pick up the changes).

### June 24, 2026
- Built FSQ Stage Backdrop Insert Panels SOP from 8 photos already in `SOP Stuff/FSQ/Stage Inserts/` — categorized images first (storage / mounting technique / end panels / finished result), then walked the install + teardown steps with Brian.
- Key facts captured: 5 panels numbered 1–5 SL→SR, install/teardown happens every show, U-bolts finger-tight (no slack, not wrenched down), silver support bar required at every inner joint (wind tear-out prevention), panels 1 & 5 have a rope cut-out for the backdrop pipe — single loop only or the panel won't seat, U-bolt hardware stored assembled (support bar + both nuts on).
- Files: `FSQ-SOP-Stage-Inserts.md/.html/.pdf` in `SOP Stuff/FSQ/Stage Inserts/`, alongside the source photos. PDF rendered via weasyprint, 4 pages, verified clean (no clipping).

### July 5, 2026
- Deep Think EQ flow evaluated at Brian's request. Locked the per-input order (importance + process): **instrument → mic → genre → venue** — written into eq-advisor and show-deep-build (SKILL.md + references). Venue clarified as last-applied constraint filter, not top authority.
- Added the **mic-locker loop** (eq-advisor Step 2b + show-deep-build Step 3): every input's mic checked against mic-library.md for an owned alternative with a concrete win; one alt max, one-line why, never on TOUR gear, batched to the review stop, EQ still built for the specified mic; alts ride mic_notes + `Locker alt —` changes into the Rationale PDF.
- Added research dedupe to the deep build (N channels → M unique instrument × mic units, plan table shown before searching).
- Pending Brian's call: KB-cache skip of the web pass for established pairings, single batched stop-and-ask round, post-show "what did you move" harvest, per-channel role field.

### July 5, 2026 (later)
- Deep Think rulings finalized: cross-show research cache REJECTED (web pass fresh every show — artists never repeat); per-channel role field rejected (notes carry it); **artist_profile added to the per-input chain** (genre+artist layer, artist beats generic genre); **batched question round ADOPTED** (plan pass collects all stop-and-asks + locker alts → one message before any EQ commits); post-show harvest rejected. All written into eq-advisor + show-deep-build skills; IMPROVEMENTS.md logged.

### July 5, 2026 (final)
- Workflow written into all files: eq-advisor + show-deep-build skills, `_system/NEW-SHOW.md`, KB articles (show-processing-pipeline, pipeline-spec-memo, pipeline-spec-fsq, eq-starting-points header, showbuilder — all Last updated bumped), KB CHANGELOG, all three CLAUDE.md files, and the deep-think-default auto-memory. Canonical statement: per-input order instrument → mic → genre → venue; artist profile refines/outranks generic genre; research fresh every show with within-show dedupe; mic-locker alternative check per input; one up-front question round; venue last as constraint filter. Wiki articles updated locally — not yet pushed to the live wiki (wiki-publish when Brian says).

### July 6, 2026 — memory-consolidation skill built + scheduled daily
- Brian flagged a public GitHub skill ("dream-skill") replicating Anthropic's unreleased auto-memory-consolidation feature for Claude Code. Evaluated it: its 4-phase shape and contradiction/backup habits are portable, but its JSONL-transcript scan and Stop-hook auto-trigger are Claude-Code-CLI-only and don't exist in Cowork.
- Built the equivalent: `_skills/memory-consolidation/SKILL.md` — orient → gather signal (via Cowork's `list_sessions`/`read_transcript`, best-effort) → consolidate (contradiction format `Updated YYYY-MM-DD, previously: X`, absolute dates, source attribution, never-delete-without-replacement) → prune/index. Targets the real memory layout here: `active-projects.md` for project state, this file for history.
- Wired to a Cowork scheduled task running once a day. First run is a dry run (proposes changes, confirms with Brian before writing); after that it applies changes automatically and logs a one-line summary here each time.
- Logged to KB CHANGELOG and `_system/IMPROVEMENTS.md`. Open item in `questions.md`: confirm/adjust the daily run time.


### 2026-07-06 — doc drift fixed
- Q225 band convention corrected in root `CLAUDE.md` (console section, Core EQ Rules, EQ Document Column Order) and global `~/.claude/CLAUDE.md` — all now state B1 = LF … B4 = HF, doc order HPF → LPF → B4 → B1, matching audio/CLAUDE.md, the KB, and the .ses pipeline. `Brian Lloyd - Context.md` (2026-06-26 portable export) got a stale-snapshot banner instead of a rewrite — its embedded EQ tables are the retired format; KB is canonical.
- Memory/about-me unification: see the "memory files unified" entry below (audio copies merged + symlinked; audio/CLAUDE.md's wrong "never existed" claim corrected).

---

**Entries below found by the 2026-07-08 memory-consolidation pass, scanning sessions never logged here (original session dates preserved, from file mtimes where the session itself wasn't dated):**

### 2026-06-25 — DiGiCo OSC macro for Reaper (LiveTrax one-button record-arm) — paused
- Goal: one DiGiCo command key arms/starts Reaper LiveTrax recording over OSC. Protocol partially decoded (reference capture + parser saved); self-send and the DiGiCo_OSC module both ruled out. Handoff written at session close: `handoffs/2026-06-25_DiGiCo-LiveTrax-OneButton-Macro-Handoff.md` + `handoffs/digico-livetrax-macro/`. Left mid-debug on the Record Arm macro insert — no further session found continuing it.
- Logged to active-projects.md Tools & Infrastructure and flagged in questions.md 2026-07-08 — was an orphaned open thread until now.

### 2026-06-29–30 — FSQ L-Acoustics Network Manager SOP built + published
- Built from 8+ screenshots in `SOP Stuff/FSQ/L-Acoustics Network Manager/`: connect to amps, load checker, restore session, confirm restore flow. Output: `FSQ-SOP-LA-Network-Manager.pdf`.
- Pushed to the wiki: `kb.tinydoorstudios.com/sop-fsq-la-network-manager`, PDF at `/assets/sops/fsq/fsq-la-network-manager-sop.pdf`. GitHub push + n8n VM asset sync confirmed; Wiki.js force-sync and nav-sidebar rebuild both skipped (normal — same known gaps as every other wiki-publish run, auto-resolve within 5 min / need `WIKI_API_KEY`).

### Hog5 lighting programming (session date not captured — flagging, not asserting)
- A session covered Hog5 command-key cue programming (toggle-style engage/release on a blue-out look, fade-in/release timing, kind-mask discipline at Record) and researched whether Hog5 showfiles (`.h3`) can be processed externally — they're SQLite databases under the hood, readable but ETC doesn't publish the schema, so editing is possible but risky. This is a new domain — not lighting console work Brian's about-me/CLAUDE.md currently covers at all. Flagged to questions.md: is this a recurring responsibility that should get its own tracking, or a one-off?

---

### Memory Consolidation — 2026-07-08
- Scanned: 24 sessions (list_sessions, best-effort sample of ~9 read in full) / no prior watermark — first-ever run, looked back across everything list_sessions could reach.
- Added: 6 entries (mic inventory, audio archive sync, DiGiCo OSC macro, FSQ network manager SOP, Hog5 lighting flag, SPL Monitor moved to active-projects.md) · Updated: 4 (Wind Alert + KSO S&G resolved in active-projects.md and questions.md; active-projects.md header/sync date; memory.md Active Projects section trimmed to a pointer — 2 contradictions resolved) · Archived/trimmed: 1 (memory.md's duplicate 5-show Active Projects block → pointer)
- Flagged to questions.md: LDB status (frozen since May 16, no show date on record), DiGiCo OSC macro resume/shelve call, Hog5 lighting recurring-or-one-off
- First run was a dry run confirmed by Brian 2026-07-08 ("yes do this, do not ask again") — this run applied the changes and future daily runs proceed automatically per the skill's safety rule.

### July 8, 2026 (FSQ feedback pass — Hot Magnolias)
- Brian console-loaded the first shared-engine FSQ .ses (Hot Magnolias) — recalled properly. Five corrections from that pass, all landed as code + docs same night:
  1. FSQ cuts deeper: −6 to −9 dB typical, −10 on mud (pipeline-spec-fsq, eq-advisor, NEW-SHOW, CLAUDE.md genre tables).
  2. FSQ fader 9 "Overheads" = STEREO (both OH mics, one fader); fader 10 "SNARE PL8" = snare plate return, never an input — Hot Magnolias had overwritten it. Now double-gated: build_packet RESERVED_CH validation error + FSQ patcher `protected` hard-abort.
  3. Stage plots band-provided, never generated; file as `<Show> - Stage Plot.pdf`.
  4. `build_packet.py` now emits `<Show> - MASTER.pdf` (packet + rationale + band stage plot/rider, pypdf) alongside the individual files.
  5. Reverb suggestions required every show incl. FSQ: 3 complementary vocal + 1–2 instrument (horn on request) + 1 general; Seventh Heaven presets verbatim with settings + in-plugin EQ + why + pairing paragraph. Validator-enforced (`reverbs`/`reverb_pairing`, opt-out `no_reverb: true`); Reverbs xlsx sheet + Rationale block upgraded.
- Verified: old Hot Magnolias spec fails with exactly the two intended errors; corrected spec builds clean incl. 24-page MASTER; patcher refuses the ch-10 MD.
- **Open: the shipped 2026-07-11 Hot Magnolias packet/.ses predates these rules — Brian re-running the input list through the updated pipeline.** *(Updated 2026-07-09: done — Rev 2 rebuilt on the corrected pipeline (`hot-mag 2/`), Rev 3 blind rebuild (`hot-mag 3/`), A/B evaluated 2026-07-09 (see below); console verify still pending.)*

### 2026-07-08 (late) — Hot Magnolias Rev 3 blind rebuild (`hot-mag 3/`)
- Brian's call: run the deep build "from the beginning" as a comparison test vs `hot-mag 2` — no values reused, full fresh web pass (artist + all 14 research units). Rulings from the question round: OH = stereo pair on fader 9 (fader 10 stays SNARE PL8 return), V1/V2 Beta 58A only, no locker swaps, blanks stay spares, date 2026-07-11.
- Shipped: spec.json, FOH Channel Processing .md, Input List xlsx (Input List + Monitors + Reverbs sheets), Show Packet PDF, EQ Reasoning PDF (reverb section included), MASTER PDF, .ses via apply_hotmag3.py (0 stray bytes, readback PASS, size identical).
- **Caught by Brian, then root-caused:** first build shipped with NO reverb section. Cause: I ran the *plugin-cache* copy of build_packet.py (stale, pre-2026-07-08) instead of the canonical `audio/_skills/show-deep-build/scripts/build_packet.py`, which validates reverbs as REQUIRED, expects spec key `reverb_pairing` (not `reverb_note`), and emits the MASTER itself. Rebuilt with the canonical script — validation PASS 0 warnings, .ses re-patched PASS. Rule for future sessions: **always run the `_skills/` copy of build_packet.py, never the plugin cache.**
- Sandbox gotchas: build_packet.py needs `--packet-builder /…/audio/show-packet-builder-template.py` and the patcher needs `PYTHONPATH=…/audio/_shared` (both scripts resolve paths against $HOME, which differs in the Cowork sandbox).
- Awaiting Brian's A/B vs Rev 2 + console verify; harvest deferred until then.

### 2026-07-08 — Hot Magnolias A/B eval (Opus 4.8 vs Fable 5) + new KB guardrail
- Evaluated `hot-mag 2` (Opus 4.8 High) vs `hot-mag 3` (Fable 5 High) — same command, same input, blind rebuild. Verdict: Fable 5 stronger. Root cause of nearly every difference: Opus web-researched only 3 of 11 units and leaned on the KB for familiar mics (produced the i5 +2@5k boost into its baked +9dB@5.5k peak, and stacked kick-pair low boosts); Fable sourced all 11 units quantitatively, fetched the real forecast (74% RH vs Opus's assumed "dry July"), and executed its stated principles (horn slotting) in the numbers.
- Deliverables in `Fountain Square/hot-mag A-B eval/`: A/B eval PDF · `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` (11 anchored edits to eq-advisor/show-deep-build/NEW-SHOW/KB pipeline article — NOT YET APPLIED, Brian runs it through Opus) · `Deep Build Run Guide - Memo + FSQ` (MD+PDF, word-for-word prompts).
- **New guardrail (Brian, 2026-07-08): "The KB is for longevity, not research."** No model may source an EQ value from the KB — every instrument × mic unit gets a fresh web pass with a named external source + quantitative capsule fact, no familiar-mic exemption. KB's build-time role is cross-check only (disagreement = stop-and-ask); its other role is receiving the harvest. The eq-advisor sentence "when it speaks to the source, it's authoritative" was the loophole Opus used — Edit 1b in the upgrade MD rewrites it. Guardrail is baked into both run-guide prompts and the upgrade MD.
- Brian declined deletion of the intermediate .html render sources in the eval folder — leave them.
- **Guardrail refinement (Brian, same session):** web↔KB differences always come to Brian with three options — research / KB / research + update the KB — and when research beats the current KB entry even without a conflict, offer the KB update in the question round. Added as Edit 1c in the upgrade MD and baked into both run-guide prompts.

### 2026-07-09 — Skill consolidation + pipeline upgrade applied (session line added retroactively by the verification audit — the consolidation session logged to IMPROVEMENTS.md/CHANGELOG but skipped this file)
- **eq-advisor merged into show-deep-build — one skill.** Part I = show pipeline, Part II = the EQ method (former eq-advisor). NEW-SHOW.md rewritten as a thin router + don't-forgets. eq-advisor source archived to `_skills/_ARCHIVE/eq-advisor-retired-2026-07-09/`. Full detail: `_system/IMPROVEMENTS.md` 2026-07-09 entry.
- **All 11 edits from `PIPELINE-UPGRADE-FOR-OPUS-4.8.md` folded in during the merge** (research floor, capsule-voicing gate, two-mic lane ownership, sectional slotting in the numbers, fetched weather, factory-anchored reverbs, numeric dynamics, carried-flags rule, KB quality-floor section). The upgrade file carries a do-not-re-apply banner.
- **Stale installs caught:** the Cowork-installed eq-advisor plugin (06-23) and show-deep-build skill (06-25) predate every July rule. Fresh `_skills/show-deep-build.skill` built — Brian must delete both installed copies and upload the new one. OPEN until done.

### 2026-07-09 — Verification audit of the upgrade application
- Ran the upgrade file's full checklist against the consolidated files. All five anchor strings present in `show-deep-build/SKILL.md`; NEW-SHOW.md don't-forgets and the KB quality-floor section in place, Last updated bumped; no contradictions with locked rules; one voice throughout. IMPROVEMENTS.md + KB CHANGELOG entries confirmed.
- Confirmed the installed skill caches are still stale (zero new-anchor hits; eq-advisor plugin still installed). Reinstall remains the open item.
- Acceptance test unchanged: next deep build judged against `hot-mag 3/The_Hot_Magnolias.spec.json`.

### 2026-07-09 — Mic Reference SOP built (FSQ input list + photo mic guide) *(from session 2026-07-09, logged by 2026-07-10 consolidation)*
- Built a 4-page **Mic Reference** in `SOP Stuff/Mic Reference/`: page 1 = full 32-channel FSQ input list (shorthand decoded to full mic names), pages 2–4 = a photo mic-ID guide. Deliverables: PDF + HTML + xlsx (two tabs: Input List, Mic Guide) + `build_mic_reference.py` + a sample-page PNG. Handoff at `handoff-2026-07-09-mic-reference.md`.
- **Known quality limit:** the delivered PDF is soft — sandbox can't reach image hosts and the browser bridge blocks image data, so pages were browser-rendered then re-sliced by hand (rasterized twice). Sharp path is a **local weasyprint / headless-browser render** with direct network access (fetches photos, keeps text vector); Claude offered to build that repeatable local mic-sheet script — Brian's call. Interim sharp copy: open the HTML, let photos load, Chrome Print → Save as PDF (keeps text vector).
- **Mic-spec discrepancy flagged** (see questions.md): per Shure specs the Beta 27 and Beta 98D/S are supercardioid, but `Memorial Hall/mic_inventory.xlsx` lists the Beta 27 as cardioid. Not reconciled — awaiting Brian's call on which is authoritative.

### Memory Consolidation — 2026-07-09
- Scanned: 3 sessions / 1 day back (watermark: the 2026-07-08 run — it updated active-projects.md and questions.md but never appended its watermark entry here; chain restored with this entry)
- Added: 2 entries · Updated: 2 (0 contradictions resolved) · Archived/trimmed: 0
- Flagged to questions.md: none (pipeline-upgrade follow-through logged to active-projects.md Open Issues instead — it's a task, not a question)

### Memory Consolidation — 2026-07-10
- Scanned: 31 sessions via list_sessions (watermark 2026-07-08); ~4 read in full. All 2026-07-08/09 pipeline + hot-mag work was already logged; only the 2026-07-09 Mic Reference session was unrecorded.
- Added: 2 entries (Mic Reference SOP → memory.md + active-projects.md Tools) · Updated: 0 (0 contradictions resolved) · Archived/trimmed: 0
- Flagged to questions.md: 1 (Beta 27 supercardioid-vs-cardioid inventory discrepancy)

### 2026-07-11 — "421" locked to the MD 421-U "Silver Tail" (mic-identity correction) *(from session 2026-07-11, logged by 2026-07-11 consolidation)*
- **Standing rule (Brian, explicit):** any `421` / `MD421` on Brian's paperwork = his vintage 1970s **Sennheiser MD 421-U "Silver Tail"** (native XLR, chrome connector base), **NOT** the modern MD 421-II. Research + document it as the 421-U every time; the MD 421-II only appears as a comparison line, never as his gear. Same 27 mm 421 element, so EQ character is unchanged — the identity is what's corrected.
- Applied during that session across the three source-of-truth files: CLAUDE.md mic shorthand (read at paperwork-build time), the ShowBuilder matcher (`421`/`MD421`/`421-U`/`Silver Tail` all aliased to the 421-U entry), and the KB `mic-library` character row (published to the live wiki; folder-watcher auto-committed as "KB auto-sync 22:09"). The wiki MD 421 page + PDF + gallery card were also corrected from the -II to the Silver Tail earlier in the same session.
- Consistency flag raised to questions.md: `Memorial Hall/mic_inventory.xlsx` wasn't touched — check it labels the 421 as the 421-U so all four references agree.

### Memory Consolidation — 2026-07-11
- Scanned: 33 sessions via list_sessions (watermark 2026-07-10); 1 read in full. Only one work session postdated the watermark ("Mic Photos to Wiki" / the 421-U identity lock); everything else was already logged.
- Added: 1 entry (421 → MD 421-U "Silver Tail" standing rule) · Updated: 0 (0 contradictions resolved) · Archived/trimmed: 0
- Flagged to questions.md: 1 (MD 421-U label consistency in mic_inventory.xlsx)

### 2026-07-11 — Audiority Echoes T7E preset library + KB article *(from session "Echos T7E plugin research", logged by 2026-07-12 consolidation)*
- Built an **8-preset library** for the Audiority Echoes T7E mkII (Binson Echorec T7E magnetic-drum echo emulation) — a color/FX plugin that lives on a send in Studio One / WaveLab, not a console effect. Every preset was derived from Brian's known-good factory **Slapback** file so the 12-position head matrix and file structure are guaranteed to load. 6 core by source (Vocal Slap · Vocal Ambient Swell · Guitar Multi-Head Gilmour · Guitar Rockabilly Slap · Keys Wide Stereo · Horns Vintage Warmth) + 2 signature-style interpretations (Brauer Vocal Slap Drive, Blake Character Echo — Claude's reads of each engineer's approach, not published patches). Delivered in an "Echoes T7E Presets" folder in the Claude folder → drop in `/Users/Shared/Audiority/` or Load Preset in-plugin.
- New KB article built the same session: `Live Sound KB/Wiki/fx-echoes-t7e.md` (full mkII manual v2.3 ingested — four heads, Classic/Vari/Sync play modes, Echo/Rep/Swell echo modes, 0 ms preamp color mode, per-head Tone/Error/Vol/Pan). Status emerging.
- **Two open loops** (see questions.md): the **Selector** mapping was inferred from the Slapback file (Echo=1.0 / Rep=0.5 / Swell=0.0) — Brian to eyeball one preset's mode on first load and confirm; all presets ship **Mix 100%** for send use (back to ~20–30% on an insert). Claude also offered to add a preset-library section to the KB article — pending Brian's yes.

### 2026-07-11 — Memo Lead Door Access SOP (UniFi) built *(from session "Event leads door access SOP", logged by 2026-07-12 consolidation)*
- Built a 4-page **event-lead SOP for UniFi door access at Memorial Hall**: log in as 3CDC → unlock the applicable door(s) for that event → set custom duration → lock at close. Key correction folded in on Brian's note: leads unlock **only the doors that event needs, not all three every time** — which doors apply comes from the **event paperwork or Joe Johnson**, referenced in the Quick Reference "Doors" row, the Task line, and the unlock/lock steps.
- Red **WARNING box** added on Lockdown, confirmed against Ubiquiti docs first: the Lock**down** button triggers UniFi **Emergency Lockdown** (active-threat mode), overrides normal credential access on that door, and stays on until an admin manually clears it — not a closing-time action.
- Filed at `SOP Stuff/Memo/Lead Door SOP/Memo_Unifi_Door_Access_SOP.pdf` (with step screenshots) — correct SOP-Stuff/<venue> routing. New contact captured: **Joe Johnson** = who to ask for which doors an event needs.

### Memory Consolidation — 2026-07-12
- Scanned: 36 sessions via list_sessions (watermark 2026-07-11); 2 read in full. Two work sessions postdated the watermark — both unlogged, both added this pass; everything else was already recorded.
- Added: 2 entries (Echoes T7E preset library + KB article; Memo Lead Door Access SOP) · Updated: 0 (0 contradictions resolved) · Archived/trimmed: 0
- Flagged to questions.md: 1 (Echoes T7E Selector-mapping confirm + preset-library KB section pending)

### 2026-07-12 (afternoon) — Fable-parity evaluation: discipline merged into show-deep-build, heavy scaffolding split to an overlay *(logged by 2026-07-13 consolidation)*
- Evaluated how Fable 5 executes the deep build vs. the written skill; found the audio content already hardened (07-08 A/B patches), the real gap was execution discipline. Brian chose "discipline only" for the merge into `show-deep-build/SKILL.md` (all models): pacing rule (final numbers never in the same message as research), constraint card re-read before the question round and before spec.json, one-word AGREE/DISAGREE/THIN reconcile verdict, consolidated pre-commit audit (`references/pre-commit-audit.md`), zero-questions-is-suspicious heuristic, failure-mode catalog. Per-unit worksheet files + strict one-unit-at-a-time serialization stayed in a new non-Fable-only overlay, `_skills/fable-parity/`.
- Both `.skill` zips rebuilt; Cowork installs are snapshots — Brian still needs to delete the installed show-deep-build copy and upload both fresh (same open item as the 2026-07-09 consolidation, not yet closed).
- Full detail: `_system/IMPROVEMENTS.md` 2026-07-12 entry.

### 2026-07-12 (evening) — Full Mic Locker Gallery published to the wiki (52 mic pages) *(from session "Mic Photos to Wiki", logged by 2026-07-13 consolidation)*
- Built out the rest of the mic-library wiki pages — 35 new pages (SDCs, LDCs, ribbons, DIs, Countryman B3 lavalier) added to the existing dynamics, for 52 total — each with a spec table, sound/placement notes, comparable mics, and a downloadable reference PDF. Grouped into a clickable **Locker Gallery** on `mic-library.md` spanning all six categories (solid ring = owned, faded ring = reference-only — AT Pro 35, Lauten LS-408, Telefunken M80, Beta 56A, BSS AR133, Whirlwind IMP).
- Specs pulled from manufacturer data cross-checked against the KB's verified character notes; where a manufacturer doesn't publish a clean number, the row was left out rather than guessed. Ribbon pages (R-121, R-10, R88) all carry the NO-48V warning; R88 keeps the "disengage phantom before plugging" note.
- Placeholder "Photo: drop…" caption removed from every page (Brian's mid-turn note) — hero image now shows the photo when present, a neutral box when not. Importer alias map extended to 127 shorthand names (`81`, `r121`, `c414`, `j48`, `mkh40`, etc.) so future photo drops auto-route.
- Published live: push + asset sync + nav-sidebar rebuild all succeeded within the normal ~5 min window.
- **Left incomplete:** Brian asked to add the Deity S3 shotgun mic to the kit next — research had just started (one web search fired) when the session hit its usage limit. Deity S3 is NOT yet in the kit or the gallery. Flagged to questions.md.

### Memory Consolidation — 2026-07-13
- Scanned: 37 sessions via list_sessions (watermark 2026-07-12); 2 read in full. Two items postdated the watermark, both unlogged, both added this pass: the fable-parity skill merge (afternoon) and the full 52-page Mic Locker Gallery wiki build (evening). "Slate coaster engraving white" session also postdated the watermark but is a non-audio hobby project with its own separate KB — out of scope, not logged here.
- Added: 2 entries (fable-parity merge; Mic Locker Gallery) · Updated: 1 (active-projects.md Tools & Infrastructure — new Mic Locker Gallery entry, sync date bumped) · Archived/trimmed: 0
- Flagged to questions.md: 1 (Deity S3 shotgun mic research started but not finished — session hit its usage limit mid-search; kit addition still open)

### 2026-07-13/14 — Mic Locker Gallery continued: Royer merge, Preamp category (TRP2), U87 removed / WA-87 locked as "87 JR" *(from session "Mic Photos to Wiki", continued past the 2026-07-13 consolidation's watermark — logged by 2026-07-14 consolidation)*
- Same session as the 2026-07-12 gallery build, picked back up: fixed a mislabeled `OM4.png` photo (it was actually the CM4) → routed to the correct page. Merged the two Royer pages into one — Brian owns only the R-121 **Live** (red label); the R-121L page was deleted, and "Royer R-121 Live (red label)" is now the sole Royer entry, so every "R-121" in his paperwork means this unit.
- **New Preamp category** added to the KB gallery — AEA TRP2 built first (63 kΩ input, ~85 dB gain), cross-linked with the R88 page since it's Brian's near-exclusive R88 preamp. Brian asked for the rest of his preamps by make/model to build out the category — open, no inventory exists yet beyond the TRP2.
- **Neumann U87 deleted from the kit** — Brian confirmed he doesn't own one. Removed from the KB page, gallery, and character table; Warm Audio WA-87 is now flagged as his only "87," nicknamed **"87 JR"** — `mic-library.md` and its alias map resolve "87"/"U87" to the WA-87 page. 47 mics now have real photos; Countryman B3 and Schoeps MK41 remain on placeholders.
- **Contradiction caught by this consolidation pass:** the session reported CLAUDE.md and the ShowBuilder matcher were updated to match the U87 removal, but the mounted `audio/CLAUDE.md` mic shorthand table still lists U87 and "U87 Jr" as two separate mics, and so do `_skills/show-deep-build/references/decision-flow.md` and `about-me/portable-context.md`. Only the KB itself is actually correct. Not fixed here — editing those pipeline/context files is outside this run's scope (memory.md/active-projects.md/questions.md only); flagged to questions.md as a real fix, not just a doc-drift note, since `decision-flow.md` feeds EQ research routing.

### Memory Consolidation — 2026-07-14
- Scanned: 38 sessions via list_sessions (watermark 2026-07-13); 1 read in full. Only "Mic Photos to Wiki" postdated the watermark — it turned out to be the same long-running session already partly logged on 2026-07-13, continued further (Royer merge, TRP2 preamp page, U87 removal / "87 JR" lock-in) after that pass's cutoff. "Slate coaster engraving white" reappeared in the session list but is the same out-of-scope hobby project already excluded.
- Added: 1 entry (Mic Locker Gallery continuation) · Updated: 2 (active-projects.md Mic Locker Gallery entry + header sync date — 1 contradiction resolved: U87 kit status) · Archived/trimmed: 0
- Flagged to questions.md: 2 (U87 removal not propagated to CLAUDE.md/decision-flow.md/portable-context.md — needs an actual fix, not just a note; other preamps needed from Brian for the new Preamp category)

### 2026-07-14 — Workspace structure cleanup (memory / skills / git / layout)
- Full audit of the Claude structure, then all eight fixes applied. Headlines: `audio/CLAUDE.md` was a stale 2026-05-27 fork (Neumann U87, Pi n8n, weasyprint packet claim) loading into every audio session — rewritten as a thin pointer layer. about-me had re-forked (audio copy was getting the nightly consolidation writes, canonical was stale) — merged and replaced with real symlinks this time. memory.md now runs a rolling ~30-day Session Notes window; older entries live in `about-me/memory-archive-2026H1.md`.
- `~/Documents/Claude` is a git repo now (baseline commit `c7e1f64` captured pre-cleanup). Commit rule-file changes instead of .bak copies. Ignored: Kims Stuff, SOP Stuff, the Wiki (own repo), venvs, credentials.
- Skills: `_skills/` sources symlinked into `.claude/skills/` (Claude Code always runs live copies; Cowork uploads still snapshots). New `_system/PIPELINE.md` = the five-stage show chain on one page. `/reflect` rewritten to feed auto-memory, not `~/.claude/CLAUDE.md`. CLAUDE.md Active Projects → pointer to active-projects.md. U87/421-U identities fixed in decision-flow.md + portable-context.md (matcher was already right); questions.md item closed.
- Full detail: `_system/IMPROVEMENTS.md` 2026-07-14 entry.

### 2026-07-14 — Cisco switch audit + Dante networking standard (dark day)
- Audited Brian's four work Cisco switch config backups (Tech Table .253 / FOH .251 / BigRack .254 core / Attic .252 — VLANs 100 Data, 200 Dante, 300 sACN, 101 Paradigm Attic-local). Real findings: FOH gi10 uplink trunk had no allowed-VLAN list (possibly management-only), the only IGMP querier lived on Tech Table (edge, election disabled) with no global snooping enable visible anywhere, Attic had zero multicast handling + no local user account + a banner advertising "cisco", QoS three different ways, trunks held up by dynamic Smartport macros.
- Deep-researched Dante switch practice (Audinate official admin PDF + Yamaha/Audinate SG300 guide + Biamp + Shure) and wrote it into the KB: new article `dante-cisco-switch-config.md` (established) — DSCP 56/46/8 strict-priority map, one querier per VLAN on the core, snooping-without-querier failure mode, unregistered multicast must stay Forwarding, sACN VLANs stay un-snooped, Auto Smartport trap. Added to INDEX + CHANGELOG.
- Built the dark-day runbook PDF with per-switch paste-in CLI: `audio/Live Sound KB/Outputs/Dante-Switch-Runbook-2026-07-14.pdf`. Not yet applied to the switches — Brian executes at the rack. Open: which venue the plant is (Paradigm + attic + rail suggest Memo — unconfirmed), FOH gi10 stale-backup check, VLAN 300 node IGMP capability, BigRack/Attic firmware upgrades on a later dark day.

### Memory Consolidation — 2026-07-15
- Scanned: 1 session via list_sessions (watermark 2026-07-14; "Mic Photos to Wiki" tail re-checked, no unlogged content — matches what's already in the 2026-07-13/14 entry above and active-projects.md). No sessions found active since the 2026-07-14 watermark with unrecorded content.
- Added: 0 entries · Updated: 0 (0 contradictions resolved) · Archived/trimmed: 1 (June 14, 2026 "KB SOP download 404" entry rotated to `memory-archive-2026H1.md` — past the 30-day window; durable fixes it depends on are already captured as kept tooling, `_tools/KB-Diagnose-API.command` / `KB-Fix-Tunnel-API.command`)
- Flagged to questions.md: none

### Memory Consolidation — 2026-07-16
- Scanned: 40 sessions via list_sessions (watermark 2026-07-15); "Mic Photos to Wiki" tail re-checked (transcript read), no unlogged content — same U87/87-JR/photo-import summary already captured 2026-07-13/14. No sessions found active since the watermark with unrecorded content; CHANGELOG.md tail also confirms nothing shipped since 2026-07-14.
- Added: 0 entries · Updated: 1 (active-projects.md SPL Monitor entry — Low-Frequency Bass Watch panel and 63 Hz octave-band feature, both shipped 2026-06-15/17, were never added to the "Current features" list; promoted now along with two pending items (Smaart 63 Hz label confirm, subRed/subYellow limit-setting) into the Next line; 0 contradictions, this was an omission not a conflict) · Archived/trimmed: 1 (June 15, 2026 "SPL dashboard upgrades + nightly email root-cause" entry rotated to `memory-archive-2026H1.md` — past the 30-day window; its durable facts (VM IP fix, Bass Watch panel) were already promoted or promoted as part of this run)
- Flagged to questions.md: none

### Memory Consolidation — 2026-07-17
- Scanned: session list re-checked (watermark 2026-07-16); no sessions found active since the watermark — the Companion prep-button and Mustard dynamics-writer work from 2026-07-16 was already fully logged same-day in this file's Session Notes.
- Added: 1 entry (Mustard/Back to Black dynamics writer — built + console-verified, then pulled from the .ses build same day at Brian's call, dynamics now doc-only — added to `active-projects.md` Q225 Show Pipeline; this was genuine project state that had only been captured in memory.md history, not the canonical project-state file) · Updated: 1 (active-projects.md header/sync date) · Archived/trimmed: 0
- Flagged to questions.md: none

### Memory Consolidation — 2026-07-18
- Nothing to consolidate — no sessions found active since the 2026-07-17 watermark (most recent non-consolidation session is still "Mic Photos to Wiki," already fully logged 2026-07-13/14 and re-confirmed clean by three prior passes); CHANGELOG.md tail unchanged since 2026-07-16.

### Memory Consolidation — 2026-07-19
- Scanned: list_sessions re-checked (watermark 2026-07-18); no session in reach postdates it — the two 2026-07-18 entries at the top of this file (n8n lightning all-clear fix, Tempest dashboard clustering) were already logged same-day by their own sessions, which list_sessions can't see from here (best-effort limit, noted in the skill). CHANGELOG.md tail unchanged since 2026-07-14.
- Added: 1 entry (`active-projects.md` Tools & Infrastructure — "Weather & Lightning Alerting (ESP/FSQ/ZP)" — the two 2026-07-18 fixes were genuine project state that had only been captured here, not in the canonical file, same gap pattern as the 2026-07-17 Mustard promotion) · Updated: 1 (active-projects.md header/sync date) · Archived/trimmed: 1 (June 17, 2026 "SPL 63 Hz band + Tailscale jump" entry rotated to `memory-archive-2026H1.md` — past the 30-day window; its durable facts were already promoted in the 2026-07-16 pass and to CLAUDE.md/auto-memory at the time)
- Flagged to questions.md: none
