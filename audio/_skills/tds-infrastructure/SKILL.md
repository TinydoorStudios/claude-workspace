---
name: tds-infrastructure
description: 3CDC and Tiny Door Studios server/network reference — the TDS Proxmox host, the n8n VM and its workflows, the Cloudflare tunnel routing, Tempest weather stations, Maestro DMX/Companion OSC, the TrueNAS boxes and backup job, and the REAPER machine paths. Use whenever work touches the home lab, n8n, the Cloudflare tunnel, kb/spl/n8n.tinydoorstudios.com, Proxmox, Tailscale, the NAS, Tempest station IDs, or DMX/Companion control. Not needed for show builds or EQ work.
---

# TDS / 3CDC Infrastructure Reference

Moved out of the always-loaded project `CLAUDE.md` on 2026-08-02 — this is server detail, not
show detail, so it loads on demand instead of every session. SPL Monitor's deploy runbook lives
separately at `Code/SPL-Monitor/CLAUDE.md` (loads when working in that folder).

The one-line version that stayed in the root `CLAUDE.md`: the `n8n-tunnel` is remote-managed —
editing local `config.yml` fixes nothing — and the Cowork sandbox can't reach the LAN or the
public `*.tinydoorstudios.com` hosts.

---

## Cloudflare Tunnel — routing is REMOTE-managed (read before editing)

The `n8n-tunnel` (b1e6581d-…) is dashboard/API-managed (`config_src: cloudflare`). Local `/etc/cloudflared/config.yml` on the n8n VM **or** inside CT 101 is **ignored** — editing it fixes nothing. Change ingress only via the Cloudflare API (token + account/zone IDs in `TDS_Credentials_CheatSheet.md`; ready-made scripts at `audio/Live Sound KB/_tools/KB-Diagnose-API.command` and `KB-Fix-Tunnel-API.command`). cloudflared runs on the n8n VM (`192.168.200.84`) beside the `landing` nginx (`:8088`, serves `/assets/` → `/kb-assets/`); Wiki.js is CT 101 at `192.168.200.126:3000`. kb `/assets/*` → nginx, everything else for kb → Wiki.js. cloudflared preserves the inbound Host header by default. (KB SOP download 404 root-caused and fixed 2026-06-14, config v8→v9.)

**Cowork's sandbox can't reach the LAN, the public `*.tinydoorstudios.com` hosts, or `api.cloudflare.com` (all allowlist-blocked).** For any server or Cloudflare op, write a `.command` that runs on the Mac and tees its output to a file in the workspace folder, then read that file back — don't try to curl those hosts from the sandbox.

## n8n Workflows (n8n VM 192.168.200.84 — n8n.tinydoorstudios.com via Cloudflare tunnel)

- **Lightning Strike Alert** — dual Tempest redundancy, tiered Slack alerts, auto-clear
- **Wind Gust Alert** — three MPH threshold tiers, 15-min rate limiting
- **Rain Forecast Alert** — Open-Meteo polling
- **Show Reports** — Google Sheets trigger → HTML email with conditional Drive photo attachments

**Known issue:** Wind Alert Slack messages still have TEST TEST TEST prefix — unresolved.

**n8n CLI (2026-06-07):** bulk `update:workflow --all --active=true` is removed. Activate per-workflow: `n8n publish:workflow --id=<id>`. On the TDS VM, compose needs sudo and the binary runs inside the container: `cd /opt/n8n && sudo docker compose exec -T n8n n8n <cmd>`. Workflow active-state is NOT carried by `import:workflow` — check the migration export JSON's `active` field to know which to re-publish.

## Tempest Weather Stations

| Station | ID |
|---|---|
| Fountain Square | 215217 |
| Elm Street Plaza | 211956 |
| Zeigler Park | 216868 |

Workflows use scheduled REST API polling (not webhook push).

## Maestro DMX / Companion Control

- Maestro DMX: `maestro.local/#/show` (Chrome bookmark "DMX")
- Companion: Generic OSC module, UDP port 7672
- Key OSC paths: `/global/brightness`, `/show/index`, `/show/cue/index`, `/show/stop`, `/show/play_pause`, `/show/cue/next`, `/show/cue/previous`

## Home Lab / Self-Hosted Infrastructure

| System | Details |
|---|---|
| n8n (Pi — legacy, decommissioned) | Raspberry Pi 192.168.0.2. n8n + tempest CUT OVER to TDS 2026-06-07; `spl-monitor` migrated to the VM 2026-06-09. Pi now powered off — nothing depends on it. |
| **TDS — Proxmox host** (was "venus") | Dell 14G PowerEdge. Proxmox 9.2.3, OS hostname `pve`. LAN 192.168.0.4 (web UI :8006). SSH `ssh tds` (key `~/.ssh/proxmox_tds`). Tailscale machine `tds` = 100.99.198.22, advertises subnet `192.168.0.0/24` (approved). iDRAC 192.168.0.7 (root/root factory — leave as-is per Brian). Storage: SSD=Proxmox, 1TB spinner=`hdd-vm` LVM-thin (~931GB) for VMs. |
| n8n VM (on TDS) | VMID 100 "n8n", Debian 12, **192.168.200.84** (was 192.168.0.125; old subnet retired 2026-06-16), n8n.tinydoorstudios.com, remote-managed Cloudflare tunnel. Reach via ProxyJump through `tds` — `ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84`, passwordless sudo. Docker Compose at `/opt/n8n` (n8n + Postgres 16) — **compose needs sudo (.env root-owned)**. Also runs `tempest-dashboard` (systemd, :3001), `spl-monitor` (systemd, :8090, `/opt/spl-monitor`), + `cloudflared` (systemd, serves n8n-tunnel). 8 workflows active post-cutover. |
| Audio NAS (TrueNAS) | 192.168.200.36 |
| Cold Storage (TrueNAS) | 192.168.200.35 · Tailscale 100.126.177.120 |
| Backup script | `/mnt/AudioNas/scripts/backup-to-coldstorage.sh` · cron 2AM |
| Cold Storage SMB ACL | Must stay nfsv4 |

**TDS reboot-hang fix (2026-06-07):** Proxmox warm reboots hung (PCIe fatal error bus 4 / ASPM). Fixed via BIOS `PcieAspmL1=Disabled` (SysProfile→Custom, set through iDRAC Redfish) + GRUB cmdline `pcie_aspm=off reboot=pci`. Cold boot avoids the hang.

**REAPER:**
- 7th-Heaven machine: primary `A:\2026\$project`, secondary `Z:\FSQ\2026\$project`
- Memo-Fourwinds machine: template at `C:\Users\Memo-Fourwinds\AppData\Roaming\REAPER\ProjectTemplates\memo show.rpp`
