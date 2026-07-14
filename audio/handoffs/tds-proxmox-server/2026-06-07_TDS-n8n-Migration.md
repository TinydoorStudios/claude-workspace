# TDS Proxmox Server + n8n Cutover — Handoff
*2026-06-07 (updated post-cutover)*

---

## What This Is

The Dell 14G PowerEdge ("TDS", formerly nicknamed "venus") is the Proxmox host that now runs the 3CDC self-hosted services, replacing the Raspberry Pi. As of this date the **n8n + tempest cutover is DONE** and the box/refs were renamed venus → TDS. The Pi is still powered (serves only `spl-monitor`); full decommission is pending one remaining migration.

---

## Access

| Target | Address | Auth |
|---|---|---|
| Proxmox web UI | https://192.168.0.4:8006 | root |
| Proxmox SSH | `ssh tds` (192.168.0.4) | key `~/.ssh/proxmox_tds` (passwordless) |
| iDRAC | https://192.168.0.7 | root / root (factory — Brian chose to leave it) |
| Tailscale (host) | 100.99.198.22 | machine **`tds`** |
| n8n VM SSH | `ssh -i ~/.ssh/proxmox_tds brian@192.168.0.125` | key + passwordless sudo |
| Pi (legacy) | 192.168.0.2 | key `~/.ssh/spl_deploy`, user brian |

**Tailscale subnet routing:** TDS advertises `192.168.0.0/24` (approved) with IP forwarding on, so iDRAC (.7), the n8n VM (.125) and Proxmox UI (.4:8006) are reachable over the tailnet from anywhere. Clients need `--accept-routes`.

---

## Hardware / Storage

- **sda** — 120GB SSD → Proxmox OS (pve VG, `local` + `local-lvm`). OS hostname is `pve` (left as-is; only the nickname/refs changed to TDS).
- **sdb** — 1TB spinner → LVM-thin VG `vmdata`/`vmthin`, Proxmox storage **`hdd-vm`** (~931GB) for VM disks.

**Reboot-hang fix:** BIOS `PcieAspmL1=Disabled` (SysProfile→Custom, via iDRAC Redfish) + GRUB `pcie_aspm=off reboot=pci`. Cold boot is clean. **Still untested:** a warm `reboot` from Proxmox coming back on its own — didn't reboot since it's now serving live traffic.

---

## What runs where (post-cutover)

**TDS n8n VM — 192.168.0.125** (VMID 100, Debian 12, SSH `brian` + passwordless sudo):
- **n8n + Postgres 16** — Docker Compose at `/opt/n8n`. Compose needs **sudo** (`.env` is root-owned). 8 workflows active.
- **tempest-dashboard** — systemd service, `/opt/tempest-dashboard`, Node 22, port 3001.
- **cloudflared** — systemd service, `/etc/cloudflared`, runs the `n8n-tunnel` (b1e6581d) serving `n8n.tinydoorstudios.com` → :5678 and `tempest.tinydoorstudios.com` → :3001.

**Pi — 192.168.0.2** (legacy, still on): only `spl-monitor` (systemd, python, :8090). Its cloudflared and pm2 (n8n, tempest) are stopped.

---

## Cutover — DONE 2026-06-07

1. Relocated the **`n8n-tunnel` (b1e6581d)** from Pi to the VM — copied the tunnel credentials + cert.pem, wrote `/etc/cloudflared/config.yml`, installed the service. **No DNS change needed** (the public CNAME points at `<uuid>.cfargotunnel.com`, so moving the same tunnel to a new host is transparent). Stopped Pi cloudflared, started VM cloudflared.
2. Migrated **tempest-dashboard** to the VM (Node 22 + npm install + systemd unit).
3. **Activated the 8 live workflows** by id (n8n CLI changed — bulk activate removed, used `publish:workflow --id=<id>` per workflow). The active set was matched to the Pi's via the migration export's `active` flags, so test stubs / one-time jobs stayed off (no double-firing): Lightning Strike Alert V2, Rain Forecast Alert, Wind Alert, Show Reports (`LTnAV4N53Lq10XBw`), ZP Pool, Weather Station Heartbeat Monitor, SPL Violation Alerts, SPL Nightly Summary Email.
4. **Repointed the Pi `spl-monitor` `.env`** `SPL_ALERT_WEBHOOK` → `http://192.168.0.125:5678/webhook/spl-violation` (full env rewrite, all 5 vars).
5. Verified: n8n + tempest public URLs 200 from the VM; 8 workflows active; Pi services stopped.

**Cutover backup on Mac:** `~/Documents/Claude/Code/n8n-migration/` (workflows.json, credentials.json, cloudflared/ creds), tempest source at `~/Documents/Claude/Code/tempest-dashboard/`.

---

## venus → TDS rename — DONE

SSH key `proxmox_venus`→`proxmox_tds` + alias `ssh tds`; Tailscale machine → `tds`; global CLAUDE.md, both memory files, about-me log, and this handoff dir/file. **OS hostname stays `pve`** and **iDRAC factory login left alone** — both per Brian's explicit call. Auto-generated permission entries in `Code/.claude/settings.local.json` left untouched (editing risks breaking the JSON).

---

## Remaining — full Pi decommission

The only thing still on the Pi is **spl-monitor**. Its public URL (spl.tinydoorstudios.com) is served by a **separate** tunnel — **`TDS Cold Storage` (70b6ddd8)**, whose connector runs at the **remote SMAART box 192.24.143.121**, not the home LAN. (spl shows 502 whenever that box is off, e.g. between shows — unrelated to the cutover.)

To finish:
1. Relocate spl-monitor off the Pi (source of truth: `~/Documents/Claude/Code/SPL-Monitor/` on Mac). Needs venue/SMAART network access to validate the SMAART connection (192.24.143.121:26000) — do it during a show.
2. Confirm where the `TDS Cold Storage` tunnel forwards spl, so the Pi being off doesn't break public spl.
3. Then power off / decommission the Pi.

**Safe to power-down-test the Pi any time** (n8n/tempest/alerts are fully on TDS) — just don't treat it as the final decommission until spl-monitor is moved.

---

## Session add-on 2026-06-07 (later) — health check, Mac dual backup, RAM spec

**Health check:** All services verified healthy. TDS host + n8n VM had both rebooted ~1.5h before the check (host uptime 1h24m, VM 1h08m, n8n container restarted ~26m) — came back clean on its own, but the cause wasn't chased. The warm-reboot recovery is therefore effectively (accidentally) confirmed working once. iDRAC reachable over tailnet via subnet route (root/root, Redfish PowerState On, Health OK). Pi was fully unreachable (off/down) — expected/safe.

**New Mac dual backup (Claude data) — DONE.** Nightly rsync of `~/.claude` + `~/Documents/Claude` to two targets:
- Synology **TDS-NAS** `192.168.0.253` → `/volume1/ClaudeBackup/` (now a real DSM shared folder, brian R/W).
- TrueNAS **Cold Storage** `100.126.177.120` → `/mnt/The-Pool/ClaudeBackup/` (new **POSIX-ACL** dataset; brian's home set here, dataset chowned to brian so sshd accepts the key).
- Script `~/.claude/scripts/claude-backup.sh`, launchd `com.tinydoor.claude-backup` daily 02:30, log `~/.claude/logs/claude-backup.log`. Uses GNU rsync `/opt/homebrew/bin/rsync` (Apple openrsync is broken). Dedicated key `~/.ssh/claude_backup`.
- Gotchas hit: Synology rsync-over-SSH needs (a) rsync service enabled and (b) destination = a **registered shared folder** (plain mkdir dir → misleading "rsync service is no running"). TrueNAS Cold-Storage main dataset is restricted-NFSv4-ACL → blocks chmod of `.ssh`, hence the separate POSIX dataset.
- **Synology is NOT its own tailnet node** — reached only via TDS's `192.168.0.0/24` subnet route, so it depends on TDS being up. Registering it as its own Tailscale node would make it independent (not done).
- **Tailscale watchdog** added on the Mac (`com.tinydoor.tailscale-watchdog`, every 5 min) to keep the tailnet up while roaming — the MAS Tailscale build has no system daemon.
- **OPEN:** "Allow SSH Login with Password" was temporarily enabled on the Cold Storage `brian` user for key-install debugging — **turn it back OFF** in the TrueNAS UI.

**Hardware (pulled from the box) + RAM upgrade spec.** Board = Dell **04JN2K** (PowerEdge R540-class, 14G), single **Xeon Silver 4110** (mem caps at DDR4-2400), 16 DIMM slots, **only 1× 8 GB** installed (single-channel), 15 empty, single-CPU so only CPU1 channels usable. Recommended buy: **6× 16 GB 2Rx8 PC4-2666 ECC RDIMM ≈ $80–110 used → 96 GB full 6-channel** (pull the 8 GB stick). Full spec PDF: `~/Documents/Claude/TDS_RAM_Upgrade_Spec.pdf`. Note: local-LLM / Hermes idea is not viable until RAM (and ideally a GPU) is added — current 7.3 GB can't host a model alongside the n8n VM; API-based agents already cover the need.

---

## Roadmap — improvements + audio services to self-host (2026-06-07, not yet built)

Ranked. Do top first. Most are gated on the RAM upgrade above.

**Infra hardening (do before piling on services):**
1. **RAM upgrade** — unblocks everything; box is starving on 8 GB single-channel.
2. **Uptime Kuma** — watch n8n / tempest / spl public URLs, push alert on down. Lightweight, ~10 min.
3. **VM backups** — Proxmox `vzdump` nightly → NAS. No VM backup today = rebuild the cutover by hand if it dies.
4. **Tailscale directly on the n8n VM** — today it's reachable only via TDS's subnet route, so it depends on TDS being up. Own node = independent.
5. **Finish Pi kill** — relocate spl-monitor, power off Pi (see section above).
6. **Close the open loop** — turn OFF password-SSH left enabled on the Cold Storage `brian` user.

**Audio services to host (ranked):**
1. **Navidrome** — stream masters/library anywhere. Light. Best first.
2. **Grafana + InfluxDB** — already piping SPL + Tempest data; stop letting it vanish. Per-show SPL history, loudness logs, venue weather over time, queryable. Highest-value for Brian specifically.
3. **Syncthing** — auto-sync REAPER capture projects location ↔ studio ↔ NAS. Kills the thumb-drive shuffle.
4. **Forgejo** (git) — version show docs, SPL-monitor code, n8n exports.
5. **Wiki.js / BookStack** — host the Live Sound KB + show docs as a searchable wiki.
6. **Audiobookshelf / Immich** — bonus; archives/podcasts, or show photos (already feed the Show Reports email).

Suggested build order: RAM → Uptime Kuma → Navidrome → Grafana.

---

## New skill — `/caveman` (2026-06-07)

Built `~/.claude/skills/caveman/SKILL.md`. Blunt caveman-speak response mode — short, simple words, ranked answers, no fluff, still technically correct. For cutting through noise on decisions/brainstorms. Drops the voice (keeps the brevity) for safety/precision-sensitive topics; still obeys no-narration + accuracy rules.

---

## Wiki.js deploy — DONE 2026-06-08
- **CT 101 "wikijs"** on TDS, unprivileged, 2c/1GB/512swap, rootfs hdd-vm:8G, IP **192.168.0.126**, onboot. DNS was unset on create → fixed (`pct set 101 --nameserver 1.1.1.1` + /etc/resolv.conf).
- Docker stack `/opt/wikijs/docker-compose.yml`: requarks/wiki:2 + postgres:16-alpine (vol pgdata, db pass `wikidbpass`), wiki on :3000.
- Admin: tinydoorstudios@gmail.com / `WikiKB-Memo2026!`. Site URL https://kb.tinydoorstudios.com.
- Public: **kb.tinydoorstudios.com**. Tunnel b1e6581d is **remote-managed** (dashboard config, not local config.yml) — added the ingress via the Cloudflare API (token decoded from cert.pem ARGO TUNNEL TOKEN block, acct fbeee704…). `route dns` added the CNAME. Verified 200.
- KB content pushed to private GitHub **TinydoorStudios/live-sound-kb** (main) from `audio/Live Sound KB/Wiki/`.
- **TODO (UI, ~2 min):** Wiki.js → Admin → Storage → Git: repo `https://github.com/TinydoorStudios/live-sound-kb.git`, branch `main`, auth Basic (user `TinydoorStudios`, pass = a GitHub PAT w/ repo scope), set sync direction, Save → forces a sync to import articles. (Local config.yml on the n8n VM also has the kb ingress as a backup but is ignored while remote config is active.)

## Wiki.js content + auto-sync — DONE 2026-06-08 (later)
- Imported all 26 KB articles via GraphQL `pages.create` (direct to CT at http://192.168.0.126:3000/graphql — Cloudflare 403s API POSTs, so always hit the container IP directly for admin API). Built structured homepage at `home`.
- **Auto-sync ON.** Chain: local `Live Sound KB/Wiki/` → GitHub `TinydoorStudios/live-sound-kb` (main) → Wiki.js Git storage (**pull** mode, PT5M).
  - Mac push: `~/.claude/scripts/kb-git-push.sh` + launchd `com.tinydoor.kb-gitpush` (WatchPaths on the Wiki dir + 300s fallback). Commits & pushes on any change. Log `~/.claude/logs/kb-git-push.log`.
  - Wiki.js Git storage configured via GraphQL `storage.updateTargets` (basic auth, PAT). **GOTCHA:** updateTargets stores each config value as JSON `{"v": <val>}` (key is `v`, NOT `value`) — wrong key silently stores null and corrupts the targets query. repoUrl https, branch main, localRepoPath ./data/repo.
  - Pull mode = GitHub is source of truth; wiki-side edits get overwritten on sync (Brian edits local files, so correct). Renamed INDEX/QUESTIONS → index/questions.md to match page paths.
  - Verified end-to-end: local edit → push → sync → page DB content updated.
- Admin password reset to `WikiKBmemo2026` (users.password bcrypt via `docker exec ... bcryptjs`).
