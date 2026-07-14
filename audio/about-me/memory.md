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

### June 15, 2026 (SPL dashboard upgrades + nightly email root-cause)
- **n8n VM IP reconfirmed = `192.168.200.84`** (the `192.168.0.125` in global CLAUDE.md was stale — SSH there is refused). Fixed the IP in `~/.claude/CLAUDE.md` SPL deploy section and the repo `docs/DEPLOYED.md`. Deploy path unchanged: rsync to `brian@192.168.200.84:/opt/spl-monitor` (key `~/.ssh/proxmox_tds`) + `sudo systemctl restart spl-monitor`. spl-monitor itself was fine the whole time (service active, public URL 200).
- **Nightly email was BROKEN every night since the VM migration** — root cause: n8n is now containerized (compose bridge net `n8n_default`), so the workflow's HTTP node calling `http://localhost:8090/api/daily/email` hit the *container*, not the host where spl-monitor runs → instant error nightly. Fix: point it at the host LAN IP `http://192.168.200.84:8090`. (Slack violation path was unaffected — that's host→container on `localhost:5678`.)
- **Second latent bug exposed once the URL worked:** the Gmail node statically requires the `pdf` attachment, but on no-show days the payload has no PDF → "item has no binary field 'pdf'". Fixed app-side: `backend/report.py` `build_minimal_report_pdf()` + `daily._build_pdf` now emit a one-page "no logging recorded" PDF when there's no data, so the email always has its attachment.
- **Verified live end-to-end:** forced a scheduled fire — n8n exec `15003 = success`, real email delivered to **blloyd@3cdc.org**. Same Gmail cred (`3CDCProduction@gmail.com`, id `nIrgTZKXgA3bJ9oP`) also powers Show Reports (sent fine 6/14), so OAuth token is healthy. Restored cron to `30 22 * * *` (22:30 EDT nightly), active=true.
- **n8n 2.23.4 workflow-edit recipe (the painful part):** `import:workflow` DEACTIVATES the workflow; raw DB edits to `workflow_entity.nodes` can corrupt the schedule node and aren't seen as a new version; `n8n execute --id` can't run a Schedule-only workflow ("Missing node to start execution"); the CLI `execute` also collides on task-broker port 5679. **Reliable sequence (separate ssh calls, not one heredoc — multi-`docker compose` heredocs truncate output over ssh):** edit JSON on Mac → scp → `docker compose cp` into container → `import:workflow` → restart n8n → `publish:workflow --id` → restart n8n → verify `active=true`. The scheduler reads `workflow_entity` directly (no `workflow_published_version` row needed). Cron runs in America/New_York. Diagnostic helper left at `/tmp/spl_inspect.sql` on the VM + clean def at `/tmp/wf_fixed.json`.
- **Dashboard upgrades shipped (Red Rocks-inspired, Brian picked these):** (1) **Low-Frequency (Bass) Watch** panel — C-weighted track (6-min LCeq computed from SPL C, live LCeq 10s, C−A spectral tilt) with its own lamp, in WATCH mode (no alarm) until per-venue `cYellow`/`cRed` dBC limits are set in `config.json`; nightly summary now also tracks max 6-min LCeq. (2) **Plain-language limits strip** under the hero (warn/limit/bass/ordinance in words) + warn/limit labels on the chart lines. Brian declined time-of-night tiers; FSQ stays single 80 warn / 90 red + ordinance 75. Assets bumped to `?v=19`.
- **Chart y-scale fixed to 70–100 dB** (was auto-expanding from 60) per Brian — `web/app.js` draw(), with a clamp so a rare >100 peak rides the top edge.

### June 17, 2026 (SPL 63 Hz octave band shipped + Tailscale jump fixed)
- **63 Hz octave "bass cop" band added to the SPL dashboard and deployed.** Replaced the broadband-LCeq big number in the Low-Frequency (Bass) Watch panel with the **63 Hz 1-min Leq** (lamp keys off it), live **63 Hz 10s** tile beside it, C−A tilt + full-band 6-min LCeq kept as secondary tiles. Brian's calls: one band (not 63+31.5), replace (not show-both), 1-min compliance window.
- **Smaart labels are auto-detected, not hard-coded** — `processing.py` `_resolve_sub_labels()` matches any streamed metric containing "63", classes the "10s" one as live and the other as 1-min; optional `config.json` `"subBand"` override. Resolved label shows in the panel note; All Metrics grid made dynamic so new labels surface on their own. **Open:** confirm the real Smaart label at the next live show (simulator used `LZeq 10s/1 63 Hz` placeholders); pin in `subBand` if auto-detect picks wrong. Limit-setting (`subRed`/`subYellow`) still pending the watch period + a 63 Hz FOH→property-line offset.
- Logging extended for the watch period: CSV gains `sub63_10s`/`sub63_1min`, XML summary gains `sub63_1minMax`. Files: `processing.py`, `logging_csv.py`, `sources.py`, `config.json`, `web/index.html`, `web/app.js`. Assets `?v=20`. Handoff `docs/HANDOFF_2026-06-15.md` §0 updated to "shipped".
- **Two doc corrections proven this session:** (1) the Mac CAN reach `192.168.200.84` directly on the house LAN — deployed that way; the old "can't reach .200.x directly" note was wrong (jump only needed when remote). (2) A **Claude Code** shell with the sandbox disabled CAN reach the LAN/jump (ran the whole deploy + ACL read from here) — only the *Cowork* sandbox is LAN-blocked.

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

### 2026-05-19 — Mic inventory spreadsheet built
- `Memorial Hall/mic_inventory.xlsx` + `.csv` — mic library inventory by category. WA-87 (Warm Audio) corrected to multi-pattern (Omni/Cardioid/Fig-8), not cardioid-only. Audio-Technica AE2500 added to Dynamics (dual-element kick mic, dynamic + condenser capsules, two XLR outs) — Category field set to "Dynamic / Condenser" per Brian's call, so it signals two channels when pulled into an input list.
- Logged to active-projects.md Tools & Infrastructure 2026-07-08 (was untracked until the consolidation pass found it).

### 2026-06-02 — Audio Archive Sync email report built
- Daily confirmation email that the Reaper-PC → Audio NAS sync ran — separate from the existing 2 AM `backup-to-coldstorage.sh` (NAS → cold storage). TrueNAS: `/root/scripts/audio-sync-report.sh`, cron 3 AM, emails `tinydoorstudios@gmail.com` (log on success, "no log found" alert if the Windows side didn't run). Windows (7th-Heaven/Reaper PC): `C:\Scripts\audio-archive-sync.ps1` + Task Scheduler, writes `Z:\sync-logs\`. Hit the usual PowerShell speed bumps (Command Prompt vs. PowerShell confusion, execution policy, em-dash encoding corruption in the script comments) — all resolved, verified working.
- Logged to active-projects.md Tools & Infrastructure 2026-07-08.

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
