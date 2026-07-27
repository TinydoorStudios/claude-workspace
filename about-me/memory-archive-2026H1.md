# memory-archive-2026H1.md
*Archived session notes rotated out of `memory.md` (rolling ~30-day window, first rotation 2026-07-14). Nothing reads this at session start — it's the historical record. Durable rules/preferences from these sessions were promoted to CLAUDE.md, the KB, or auto-memory before archiving.*

---

## Session Notes (archived)

### June 24, 2026 — FSQ Stage Backdrop Insert Panels SOP built

- Built FSQ Stage Backdrop Insert Panels SOP from 8 photos already in `SOP Stuff/FSQ/Stage Inserts/` — categorized images first (storage / mounting technique / end panels / finished result), then walked the install + teardown steps with Brian.
- Key facts captured: 5 panels numbered 1–5 SL→SR, install/teardown happens every show, U-bolts finger-tight (no slack, not wrenched down), silver support bar required at every inner joint (wind tear-out prevention), panels 1 & 5 have a rope cut-out for the backdrop pipe — single loop only or the panel won't seat, U-bolt hardware stored assembled (support bar + both nuts on).
- Files: `FSQ-SOP-Stage-Inserts.md/.html/.pdf` in `SOP Stuff/FSQ/Stage Inserts/`, alongside the source photos. PDF rendered via weasyprint, 4 pages, verified clean (no clipping).
- Durable facts promoted before archiving (2026-07-26 consolidation): pointer entry added to `active-projects.md` Tools & Infrastructure (this SOP had no canonical-file presence before).

### 2026-06-25 — DiGiCo OSC macro for Reaper (LiveTrax one-button record-arm) — paused, then superseded

- Goal: one DiGiCo command key arms/starts Reaper LiveTrax recording over OSC. Protocol partially decoded (reference capture + parser saved); self-send and the DiGiCo_OSC module both ruled out. Handoff written at session close: `handoffs/2026-06-25_DiGiCo-LiveTrax-OneButton-Macro-Handoff.md` + `handoffs/digico-livetrax-macro/`. Left mid-debug on the Record Arm macro insert.
- **Superseded:** this same 2026-06-25 date/thread continued as the Companion-button + `reaper_relay.py` approach (REAPER, not LiveTrax, as the actual target) — Phase 2 completed 2026-06-27, extended 2026-07-16, status DONE/in active use. Full current state: `active-projects.md`'s "DiGiCo → REAPER Companion record chain" entry.
- Durable facts promoted before archiving (2026-07-26 consolidation): the open question tracking this as "paused mid-debug" (questions.md, Recording/REAPER section) was stale — resolved and moved to questions.md's Resolved section same pass, pointing at the completed chain.

### June 23, 2026 — eq-advisor EQ skill

- Built the **eq-advisor** skill (installed plugin + source `_skills/eq-advisor/`): instrument → mic → live forum research (PSW LAB, Gearspace) cross-checked against `eq-starting-points`/`mic-library` → genre → venue/room. Web and KB verify each other; stops and asks on any uncertainty (Brian's rule: an unsure answer is ~3× worse than a pause). Cuts-first / whole-dB, inline + PDF.
- Per Brian's follow-up: made it a **required EQ step in the show/ShowBuilder flow** (wired into NEW-SHOW, showbuilder, show-processing-pipeline, eq-starting-points); **self-improving** (logs to `_learning/eq-advisor-log.md`, proposes KB write-backs via wiki-publish, a Brian override = ground truth); and **Q225/Wing only** — no CL3/M32 unless explicitly asked.
- ShowBuilder's Python app (`Code/ShowBuilder/`) is outside the mounted folder, so it wasn't modified — wiring is at the workflow/KB layer; both target the KB to stay consistent. KB edits are local; push on next wiki-publish run. Delivered updated `eq-advisor.plugin` (re-install to pick up the changes).
- Durable facts promoted before archiving (2026-07-24 consolidation): eq-advisor was merged into show-deep-build as Part II on 2026-07-09 — full detail already lives in `active-projects.md`'s "eq-advisor — EQ decision skill (MERGED into show-deep-build 2026-07-09)" entry and KB CHANGELOG's 2026-07-09 entries.

### June 16, 2026 — ShowBuilder app built
- Built **ShowBuilder**, a guided web dashboard at `Code/ShowBuilder/` (Python/aiohttp, `./run.sh` → :8095) that front-ends the existing Q225 pipeline. Wizard: Show → Channels → Review → Build. Collects venue/channels/instruments/mics/genre/artist, suggests EQ+comp and 4–6 Seventh Heaven Pro reverbs, shows a review screen for approval, then renders the locked `FOH Channel Processing.md` and calls the `apply_show_TEMPLATE*.py` patchers + show-packet builder. Outputs MD/HTML/.ses/packet PDF/input-list xlsx + review PDF into the show folder. Does NOT re-derive the .ses byte format.
- Brain is KB-sourced: `reverb_presets.json` parsed from `reverb-reference-memo.md` (236 presets, names verbatim) via `build_knowledge.py`; `eq_rules.json` = CLAUDE.md starting points + genre/venue/mic layering; `mics.json` from `mic-library`. Self-improves: unknown mics → library + KB queue; every build logs to `learning/`.
- Phase 1 = Mac (done). Phase 2 (next session) = package-only instance on the n8n VM behind cloudflared + a passcode on the TDS dashboard; emits `*.spec.json`, Mac builds the .ses + final paperwork.
- Only Memo + FSQ have the calibrated .ses pipeline; other venues are paperwork-only.
- Verified: Blue Eighty-Eight rebuilds byte-identical (md5 match); Memo/FSQ fresh builds PASS at exact sizes (1,543,866 / 2,466,215); packet cover renders clean (no clipping).
- Finding: existing Memo MDs (Seals & Crofts 2, Brit Pack, Gospel Awards) are pre-2026-05-30 backwards B-numbering — logged to QUESTIONS for conversion.
- Durable facts already captured in `active-projects.md`'s ShowBuilder entry (Last updated June 16, 2026) before this rotation.

### May 16, 2026
- Created CLAUDE.md at ~/.claude/CLAUDE.md — global context file covering Brian's full setup, venues, EQ library, show doc format, mic shorthand, and active projects.
- Created about-me.md, writing-rules.md, memory.md in ~/.claude/about-me/
- Updated global instructions to reference all three files on session start.
- Established: default output is PDF, writing tone is warm but direct, never assume — always ask.
- Created `/Documents/Claude/audio/` folder structure with venue subfolders: Memorial Hall, Fountain Square, Washington Park, Elm Street Plaza, Other.
- Created venue-notes.md in each folder — pre-filled from known data.
- Documented PA rigs: Fountain Square (L-Acoustics A15/KS21/X12, Q225 FOH, M32 monitors); Washington Park (JBL SRX915/906/928, M32 FOH, no Tempest).
- Updated CLAUDE.md and about-me.md with PA and console assignments per venue.
- Extracted full session knowledge base from uploaded MD file into CLAUDE.md, memory.md, and about-me.md:
  - Added venue abbreviations (Memo, FSQ, WP, ESP, Greaves) to all files
  - Corrected Memo RT60 to working ~1.6s (previous 2.2s was empty/pre-renovation estimate)
  - Expanded mic shorthand library with Type and Primary Use columns; added B3 numbering and C422 notes
  - Added Celtic Music Engineering section (attack times, gating rules, instrument-specific notes)
  - Added Classical Recording Geometry section (wire array, ORTF, R88, spot mic preferences)
  - Added Frequency Reference tables (problem zones by venue type, instrument fundamental ranges)
  - Added Soundcheck Priority Order and Bus Grouping Standard
  - Updated color palette to full spec (console accent colors, EQ row colors, structure bars)
  - Added Drowsey Lads 2026 and Israeli Chamber Project as new active projects in memory.md
  - Expanded KSO S&G notes with full channel detail
  - Saved show-packet-builder-template.py to /Documents/Claude/audio/

### June 7, 2026 (TDS Proxmox server + n8n migration + cutover)
- Brought new Dell 14G **Proxmox server "TDS"** online (192.168.0.4, web UI :8006). Set up SSH key access (`~/.ssh/proxmox_tds`, alias `ssh tds`). Server was briefly called "venus" — renamed to TDS everywhere 2026-06-07 (SSH alias + key, Tailscale, all docs).
- Accessed **iDRAC** at 192.168.0.7 (root/root factory — flagged to change) via Redfish API.
- **Fixed Proxmox reboot-hang:** SEL showed PCIe fatal error (bus 4) at reboot caused by ASPM. Disabled BIOS `PcieAspmL1` (SysProfile→Custom) via iDRAC, added `pcie_aspm=off reboot=pci` to GRUB. Verified clean cold-boot.
- **Storage:** wiped the 1TB spinner (`sdb`, had an old Windows install — confirmed before wiping), built LVM-thin VG `vmdata`/`vmthin` = Proxmox storage `hdd-vm` (~931GB). SSD untouched.
- **Tailscale** on host → machine renamed to `tinydoorstudios-dashboard-server` (100.99.198.22).
- **n8n migration:** built Debian 12 VM (id 100, 192.168.0.125), Docker Compose n8n + Postgres 16 at `/opt/n8n`. Migrated 13 workflows + 8 credentials off the Pi (encryption key carried over, dropped 9.6GB of execution-log bloat). Workflows imported **INACTIVE** — Pi stays live until Brian triggers cutover. Export backup on Mac at `~/Documents/Claude/Code/n8n-migration/`.
- **Cutover DONE (same day):** Tailscale subnet route `192.168.0.0/24` advertised+approved (iDRAC/VM/Proxmox reachable over tailnet). Relocated the `n8n-tunnel` (cloudflared) from Pi to the VM — no DNS change, same creds. Migrated `tempest-dashboard` to the VM (systemd, :3001). Activated the 8 live workflows by id; n8n + tempest verified 200 from the VM. Stopped Pi cloudflared + pm2. Repointed Pi `spl-monitor` `.env` webhook to the VM n8n.
- **Pi NOT fully decommissioned:** `spl-monitor` still on the Pi. Its public URL spl.tinydoorstudios.com runs on a separate tunnel (`TDS Cold Storage`, connector at the remote SMAART box 192.24.143.121), not the home LAN. Full Pi shutdown needs spl-monitor relocated — blocked on SMAART/venue network access. (Saw spl 502 during this session = the remote cold-storage box being down/asleep, unrelated to the cutover.)
- Behavior: Brian escalated the **no-narration** rule — hardened in CLAUDE.md and saved to project memory.

### June 6–7, 2026 (session 3 — SPL Monitor continued)
- Tiles row: removed redundant headroom tile, moved prediction to slot 3, added Davidson C-A as slot 4.
- Fixed prediction display — em-dash null case replaced with "↓ stable" / "↑ limit in MM:SS" / "OVER LIMIT".
- Backend: added `ca` (LCeq10s − LAeq10s) field to each virtual location in `_compute_virtual()`.
- Compacted full layout — all sections now fit one screen without scrolling (main gap/padding, reduced font sizes throughout, tighter cards in virtual and ordinance sections, chart min-height 220→140).
- Bug: rewrote Pi .env without SPL_PORT=8090, broke public URL with 502. Fixed. Standing instruction added to CLAUDE.md.
- Created /reflect skill at `~/.claude/skills/reflect/SKILL.md`.

### June 5–6, 2026
- Built and deployed the **SPL Monitor** (10EaZy-style remote SPL portal) from scratch — Smaart v8.5 API client (Python/aiohttp) → live dashboard → Cloudflare. Live at **https://spl.tinydoorstudios.com**.
- Proven end-to-end against a real live show on the work rig (DiGiCo UB MADI ASIO / SPL @ 192.24.143.121:26000): native `LAeq 6` compliance number, traffic light, predictive "time-to-limit", CSV/XML logging.
- Debugged an aiohttp connection-reuse hang in the Smaart adapter (fixed with `force_close`) and an HTTPS mixed-content WebSocket bug (ws→wss).
- Deployed on homelab Pi (192.168.0.2) as systemd service `spl-monitor` (boot-enabled); exposed `spl.tinydoorstudios.com` by adding ingress to the existing n8n cloudflared tunnel via the Cloudflare API (token from `~/.cloudflared/cert.pem`). Mac SSH deploy key `~/.ssh/spl_deploy`.
- **Granted full autonomy going forward** — updated `Documents/Claude/CLAUDE.md` "How to Talk to Me": act without asking permission at each step; only stop for consequential/irreversible decisions.
- Saved research + designs for later phases: Red Rocks SPL program analysis, violation counter (3-strikes + n8n escalation), limit verbiage + time-of-night tiers, low-frequency bass meter, virtual location meters.
- Flagged for cleanup: two `cloudflared` instances running the n8n tunnel on the Pi.

### June 10, 2026
- Diagnosed why Cowork kept failing FSQ .ses builds while Memo worked: the KB article `pipeline-spec-fsq.md` still carried the dead "strip region" constants (0x11456/5383 — the console never reads that region on recall) from before the 2026-06-09 console-save-diff discovery. Rewrote the KB Step 3 section to the verified method (surface table 0xA287A + current-scene blocks 0x1A1000–0x1CC000) and updated `console-digico-q225.md` to warn the two venue templates use different regions.
- Confirmed byte-for-byte that the FSQ scene block filter layout is identical to the Memo strip: LPF = tag 0x0703 bidx 1, HPF float at LPF+0x10 under tag 0xFFFF (Memo's HPF_REL=406 is that same record). Open question is encoding only: console saves store HPF ≈ 0.8×display, but the Memo patcher writes raw Hz and recalls fine — read mapping unproven.
- Built the calibration kit at `audio/Fountain Square/_TEMPLATE/Filter Calibration/`: `FSQ_Filter_Cal.ses` (8 bytes changed — Ch1 HPF=80, Ch2 HPF=100, Ch3 LPF=5000, Ch4 LPF=6250) + READ ME with the decode table. Brian loads it once at FSQ, reads four displayed values, then HPF/LPF writes go live in the FSQ patcher and Blue Eighty-Eight.ses gets rebuilt with filters.
- Also asked Brian to capture one-parameter-per-save console diffs for SD comp/gate (both venues) so dynamics can join the pipeline — those tags are still unmapped (0x1D/0x1E are Mustard, do-not-write).

### June 10, 2026 (evening — .ses calibration cracked)
- Brian supplied the decisive save-diff: edited Ch 6 in the DiGiCo offline editor (Wine) and saved `klaud edited.ses` next to the template in `~/.wine/drive_c/Projects/`. Diff confirmed everything: HPF stored = 0.8× display Hz, LPF stored = 1.25× display (off = 25000), EQ bidx 0 = HIGH band … bidx 3 = LOW, DEQ tags (0x040E/0x0411/0x0412/0x0410, seconds), comp threshold 0x050F bidx 0–2, gate enable 0x050E bidx 3. Name copies are each followed by a float64 save-timestamp — the file-wide diff noise.
- Root-caused "Blue 88 barely worked": the FSQ patcher mapped MD B1→bidx0, but B1 = low in the locked convention and bidx0 = high in the file — every channel's EQ was reversed (shelves inverted). Verve Pipe failed earlier for the dead-region reason.
- Rewrote `apply_show_TEMPLATE_FSQ.py`: band mapping fixed (B1→bidx3…B4→bidx0), HPF/LPF writes enabled with the confirmed scales, DEQ writes added, comp-thr now hits all three multiband slots. Rebuilt `Blue Eighty-Eight.ses` from its MD — readback-verified (band placement, shelf types, HPF 40→32/120→96, 0 stray bytes). Awaiting Brian's console verification.
- Memo patcher (`apply_show_TEMPLATE.py`) given the same filter scales — previous Memo shows wrote raw Hz, so their HPFs recalled ~25% above paperwork. Updated KB: pipeline-spec-fsq, pipeline-spec-memo (bidx correction), console-digico-q225. Filter Calibration kit marked obsolete.

### June 10, 2026 (late — send-it skill)
- Brian console-verified the rebuilt Blue Eighty-Eight.ses. Built the **send-it skill** (`~/.claude/skills/send-it/`): "send it fsq" / "send it memo" → MD paperwork → venue template → verified .ses. Both venue patchers now share the same CLI (--src/--dest/--md); upgraded the Memo SOP patcher with read_md (band map B1→bidx3, filter scales, DEQ) and smoke-tested it against the Memo template (HPF 40→32, LPF 6000→7500, bands land at correct bidx, do-not-write PASS).
- Disambiguated the trigger collision: fsq-wiki-push description narrowed — bare "SEND IT" after a verified .ses = wiki push; "send it <venue>" = build the .ses.

### May 28, 2026
- The Brit Pack show paperwork completed at Memorial Hall
- Seventh Heaven Pro reverb section in show doc corrected — replaced all hallucinated preset names with verified presets from official Liquidsonics PDFs
- Early/Late slider hard-jump behavior confirmed and documented in KB + memory
- Built standalone Seventh Heaven Pro reference PDF: `Memo Work/Seventh Heaven Pro Reference.pdf`
- KB article `reverb-reference-memo.md` updated: added Gold Hall, Snare Chamber, Studio A presets; Early/Late behavior section updated
- Pipeline spec finalized as 2-stage

### June 12, 2026
- Built WP Clear-Com Production Intercom SOP (Main Stage) from uploaded PDF — extracted 5 photos, produced .md + .html + .pdf via weasyprint
- SOP filed at `audio/SOP Stuff/WP/WP-SOP-ClearCom-Main-Stage.{md,html,pdf}`
- Routing correction: initially created `Memorial Hall/SOP Stuff/` by mistake — files moved to canonical `audio/SOP Stuff/` after Brian pointed it out and provided audio folder access
- Added feedback memory to Cowork auto-memory: SOP Stuff is always at audio root, never inside a venue folder

### 2026-05-19 — Mic inventory spreadsheet built
- `Memorial Hall/mic_inventory.xlsx` + `.csv` — mic library inventory by category. WA-87 (Warm Audio) corrected to multi-pattern (Omni/Cardioid/Fig-8), not cardioid-only. Audio-Technica AE2500 added to Dynamics (dual-element kick mic, dynamic + condenser capsules, two XLR outs) — Category field set to "Dynamic / Condenser" per Brian's call, so it signals two channels when pulled into an input list.
- Logged to active-projects.md Tools & Infrastructure 2026-07-08 (was untracked until the consolidation pass found it).

### 2026-06-02 — Audio Archive Sync email report built
- Daily confirmation email that the Reaper-PC → Audio NAS sync ran — separate from the existing 2 AM `backup-to-coldstorage.sh` (NAS → cold storage). TrueNAS: `/root/scripts/audio-sync-report.sh`, cron 3 AM, emails `tinydoorstudios@gmail.com` (log on success, "no log found" alert if the Windows side didn't run). Windows (7th-Heaven/Reaper PC): `C:\Scripts\audio-archive-sync.ps1` + Task Scheduler, writes `Z:\sync-logs\`. Hit the usual PowerShell speed bumps (Command Prompt vs. PowerShell confusion, execution policy, em-dash encoding corruption in the script comments) — all resolved, verified working.
- Logged to active-projects.md Tools & Infrastructure 2026-07-08.

### June 15, 2026 (SPL dashboard upgrades + nightly email root-cause)
- **n8n VM IP reconfirmed = `192.168.200.84`** (the `192.168.0.125` in global CLAUDE.md was stale — SSH there is refused). Fixed the IP in `~/.claude/CLAUDE.md` SPL deploy section and the repo `docs/DEPLOYED.md`. Deploy path unchanged: rsync to `brian@192.168.200.84:/opt/spl-monitor` (key `~/.ssh/proxmox_tds`) + `sudo systemctl restart spl-monitor`. spl-monitor itself was fine the whole time (service active, public URL 200).
- **Nightly email was BROKEN every night since the VM migration** — root cause: n8n is now containerized (compose bridge net `n8n_default`), so the workflow's HTTP node calling `http://localhost:8090/api/daily/email` hit the *container*, not the host where spl-monitor runs → instant error nightly. Fix: point it at the host LAN IP `http://192.168.200.84:8090`. (Slack violation path was unaffected — that's host→container on `localhost:5678`.)
- **Second latent bug exposed once the URL worked:** the Gmail node statically requires the `pdf` attachment, but on no-show days the payload has no PDF → "item has no binary field 'pdf'". Fixed app-side: `backend/report.py` `build_minimal_report_pdf()` + `daily._build_pdf` now emit a one-page "no logging recorded" PDF when there's no data, so the email always has its attachment.
- **Verified live end-to-end:** forced a scheduled fire — n8n exec `15003 = success`, real email delivered to **blloyd@3cdc.org**. Same Gmail cred (`3CDCProduction@gmail.com`, id `nIrgTZKXgA3bJ9oP`) also powers Show Reports (sent fine 6/14), so OAuth token is healthy. Restored cron to `30 22 * * *` (22:30 EDT nightly), active=true.
- **n8n 2.23.4 workflow-edit recipe (the painful part):** `import:workflow` DEACTIVATES the workflow; raw DB edits to `workflow_entity.nodes` can corrupt the schedule node and aren't seen as a new version; `n8n execute --id` can't run a Schedule-only workflow ("Missing node to start execution"); the CLI `execute` also collides on task-broker port 5679. **Reliable sequence (separate ssh calls, not one heredoc — multi-`docker compose` heredocs truncate output over ssh):** edit JSON on Mac → scp → `docker compose cp` into container → `import:workflow` → restart n8n → `publish:workflow --id` → restart n8n → verify `active=true`. The scheduler reads `workflow_entity` directly (no `workflow_published_version` row needed). Cron runs in America/New_York. Diagnostic helper left at `/tmp/spl_inspect.sql` on the VM + clean def at `/tmp/wf_fixed.json`.
- **Dashboard upgrades shipped (Red Rocks-inspired, Brian picked these):** (1) **Low-Frequency (Bass) Watch** panel — C-weighted track (6-min LCeq computed from SPL C, live LCeq 10s, C−A spectral tilt) with its own lamp, in WATCH mode (no alarm) until per-venue `cYellow`/`cRed` dBC limits are set in `config.json`; nightly summary now also tracks max 6-min LCeq. (2) **Plain-language limits strip** under the hero (warn/limit/bass/ordinance in words) + warn/limit labels on the chart lines. Brian declined time-of-night tiers; FSQ stays single 80 warn / 90 red + ordinance 75. Assets bumped to `?v=19`.
- **Chart y-scale fixed to 70–100 dB** (was auto-expanding from 60) per Brian — `web/app.js` draw(), with a clamp so a rare >100 peak rides the top edge.
- Durable facts promoted before archiving (2026-07-16 consolidation): n8n VM IP already in CLAUDE.md/DEPLOYED.md (done same session); Bass Watch panel + chart y-scale now reflected in `active-projects.md` SPL Monitor entry (were missing until this pass caught it).

### June 14, 2026 (KB SOP download 404 — root-caused and fixed for good)
- **The bug that kept coming back:** every SOP download at `kb.tinydoorstudios.com/assets/sops/*.pdf` returned a Wiki.js 404. Several past sessions "fixed" it by editing local cloudflared `config.yml` (on the n8n VM and inside CT 101) and nginx — none of it held, because the tunnel never reads those files.
- **Root cause:** the `n8n-tunnel` (b1e6581d-…) is REMOTE-managed (`config_src: cloudflare`, `remote_config: true`). The live ingress lives in Cloudflare's API, not on disk. Every local `config.yml` edit was ignored. The authoritative config routed ALL of `kb.tinydoorstudios.com` straight to Wiki.js (`192.168.200.126:3000`) with no `/assets` rule, so PDFs hit Wiki.js and got its Express "Not found".
- **Fix (durable):** added an ingress rule via the CF API — `kb.tinydoorstudios.com` `path: ^/assets/` → `http://127.0.0.1:8088` (the `landing` nginx), everything else for kb still → Wiki.js. Config bumped v8→v9. Stored server-side, so it survives cloudflared restarts and VM reboots. v8 backup at `audio/Live Sound KB/_tools/_kb_config_backup_20260614-093621.json` (revert = one PUT).
- **Verified live (cache-busted, through Cloudflare):** asset PDF = HTTP 200, `application/pdf`, 3,284,128 bytes, real `%PDF-1.4`, `content-disposition: attachment`; missing asset = 404 (nginx); wiki homepage = 200. `/shows` was already 404 before the change (missing Wiki page, unrelated).
- **Topology confirmed:** cloudflared runs on the n8n VM, co-located with the `landing` nginx (that's why landing + n8n both use `127.0.0.1:8088`). nginx serves `/assets/` → `/kb-assets/` and is reached at `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84`. Wiki.js = CT 101 = `192.168.200.126:3000`. cloudflared preserves the inbound Host header by default — no `httpHostHeader` needed (the old "Fix Host Header" detour was pointless).
- **IP discrepancy to resolve:** older notes (June 7 cutover) list the n8n VM at `192.168.0.125` / LAN `192.168.0.0/24`; the live tunnel + working scripts use `192.168.200.84` / `192.168.200.126`. The `192.168.200.x` net is operative for the KB stack. Treat `192.168.0.x` as possibly stale until reconfirmed on the host.
- **Process lesson:** Cowork's sandbox has NO network path to the LAN, to `kb`/`n8n`/`api.cloudflare.com` (all allowlist-blocked). For any server or Cloudflare op, write a `.command` that runs on the Mac and tees output to a file in the workspace, then read it back. Don't curl those hosts from the sandbox.
- **Tooling:** kept `_tools/KB-Diagnose-API.command` and `_tools/KB-Fix-Tunnel-API.command`. Moved 16 obsolete local-config/nginx debug+fix scripts to `_tools/_archive-obsolete/` (with a README). Don't run those.
- **Cleanup still flagged:** CF API token, KB basic-auth, Wiki admin pass, and a GitHub PAT all sit in plaintext in `TDS_Credentials_CheatSheet.md` / handoffs; June 11 handoff already flagged the PAT for rotation. Not done.

### June 17, 2026 (SPL 63 Hz octave band shipped + Tailscale jump fixed)
- **63 Hz octave "bass cop" band added to the SPL dashboard and deployed.** Replaced the broadband-LCeq big number in the Low-Frequency (Bass) Watch panel with the **63 Hz 1-min Leq** (lamp keys off it), live **63 Hz 10s** tile beside it, C−A tilt + full-band 6-min LCeq kept as secondary tiles. Brian's calls: one band (not 63+31.5), replace (not show-both), 1-min compliance window.
- **Smaart labels are auto-detected, not hard-coded** — `processing.py` `_resolve_sub_labels()` matches any streamed metric containing "63", classes the "10s" one as live and the other as 1-min; optional `config.json` `"subBand"` override. Resolved label shows in the panel note; All Metrics grid made dynamic so new labels surface on their own. **Open:** confirm the real Smaart label at the next live show (simulator used `LZeq 10s/1 63 Hz` placeholders); pin in `subBand` if auto-detect picks wrong. Limit-setting (`subRed`/`subYellow`) still pending the watch period + a 63 Hz FOH→property-line offset.
- Logging extended for the watch period: CSV gains `sub63_10s`/`sub63_1min`, XML summary gains `sub63_1minMax`. Files: `processing.py`, `logging_csv.py`, `sources.py`, `config.json`, `web/index.html`, `web/app.js`. Assets `?v=20`. Handoff `docs/HANDOFF_2026-06-15.md` §0 updated to "shipped".
- **Two doc corrections proven this session:** (1) the Mac CAN reach `192.168.200.84` directly on the house LAN — deployed that way; the old "can't reach .200.x directly" note was wrong (jump only needed when remote). (2) A **Claude Code** shell with the sandbox disabled CAN reach the LAN/jump (ran the whole deploy + ACL read from here) — only the *Cowork* sandbox is LAN-blocked.
- **Tailscale `-J tds` jump no longer prompts for browser re-auth.** Root cause: the tailnet policy's default `ssh` rule used `"action": "check"` (periodic re-auth for `autogroup:self`/root, ~12h). Changed it to `"action": "accept"` in the Tailscale admin ACL (line 54). Brian made the save (I won't commit access-control changes); I gave the exact one-word edit and re-ran the jump test = clean. Applies to all `-J tds` jumps (SPL + KB stack). Updated `~/.claude/CLAUDE.md` SPL section + `spl-monitor-host` memory.
- Durable facts promoted before archiving (2026-07-19 consolidation): 63 Hz band + Bass Watch panel already folded into `active-projects.md` SPL Monitor entry (2026-07-16 pass); Tailscale ACL fix already lives in `~/.claude/CLAUDE.md` SPL section + `spl-monitor-host` auto-memory.

