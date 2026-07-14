# memory-archive-2026H1.md
*Archived session notes rotated out of `memory.md` (rolling ~30-day window, first rotation 2026-07-14). Nothing reads this at session start — it's the historical record. Durable rules/preferences from these sessions were promoted to CLAUDE.md, the KB, or auto-memory before archiving.*

---

## Session Notes (archived)

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

