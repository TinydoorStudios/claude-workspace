# Landing page — command-center deploy (2026-07-06)

Live at https://tinydoorstudios.com. Source of truth: this folder.

**Rev 2 (same day):** VM data moved OFF the public page onto https://tinydoorstudios.com/rack/
behind the nginx basic-auth gate (user `tds`, password `lockdown` — the standard gate).
Engineer name removed from the public SPL card (show name stays).

## What's on the VM (192.168.200.84)

| Piece | Where |
|---|---|
| Main page | `/opt/landing/html/index.html` (dir bind-mounted into the `landing` nginx container — was a single-file mount of `/opt/landing/index.html`) |
| Rack dashboard | `/opt/landing/html/rack/index.html` — gated, shows PVE host + n8n VM detail + systems from rack.json |
| Status feed | `/opt/landing/html/rack/status.json` (gated), rewritten every 30s by `status-writer.timer` → `/opt/status-writer/status_writer.py` (root). The old public `/status.json` is gone — that URL now just falls back to the landing HTML. |
| Systems config | `/opt/status-writer/rack.json` — **add VMs/hosts here** (id, name, role, check: ping/http, target, optional vmid to merge PVE-push stats). Picked up next writer run, nothing to restart. |
| nginx | `/opt/landing/nginx.conf` — `location /rack/` with `auth_basic` (`/etc/nginx/.htpasswd`, tds/lockdown) + no-store |
| compose | `/opt/landing/docker-compose.yml` — volume `./html:/usr/share/nginx/html:ro` |
| Backups | `/opt/landing/*.bak.20260706-*` (index/compose/nginx pre-change) |

Container recreate after compose/nginx edits: `cd /opt/landing && sudo docker compose up -d --force-recreate landing`.

## Redeploying the pages

```
scp -o ProxyJump=tds -i ~/.ssh/proxmox_tds deploy/index.html brian@192.168.200.84:/tmp/main-index.html
scp -o ProxyJump=tds -i ~/.ssh/proxmox_tds deploy/rack/index.html brian@192.168.200.84:/tmp/rack-index.html
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 \
  'sudo cp /tmp/main-index.html /opt/landing/html/index.html && \
   sudo cp /tmp/rack-index.html /opt/landing/html/rack/index.html'
```
No container restart needed for pages (dir mount). NOTE: scp flattens paths — always
stage the two index.html files under different names (learned the hard way).

## rack/status.json contents

VM load/mem/disk/uptime, systemd states (spl-monitor, tempest-dashboard, showbuilder,
acinfinity, cloudflared), docker containers, `systems` array (rack.json checks with
up/ms per entry) — plus `pve` + `guests` host stats IF `/opt/status-writer/pve.json`
is fresher than 120s.

## PVE host telemetry (NOT yet enabled — needs Brian)

The VM can't reach the Proxmox API (8006 unreachable from the .200 subnet), so host
CPU/MEM comes from a push: cron on tds runs `pve-status-push.sh` (staged at
`/opt/status-writer/pve-status-push.sh` on the VM and in this folder) → pvesh →
ssh to the VM. Until enabled, the page shows "HOST TELEMETRY OFFLINE — INFERRED UP".

Enable (from the Mac):
```
# 1. authorize tds root's key on the VM
ssh tds 'cat /root/.ssh/id_rsa.pub' | \
  ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'cat >> ~/.ssh/authorized_keys'
# 2. install the push cron on tds
ssh tds 'cp /root/pve-status-push.sh /usr/local/bin/ 2>/dev/null || true'
scp Code/landing-redesign/deploy/pve-status-push.sh tds:/usr/local/bin/
ssh tds 'chmod +x /usr/local/bin/pve-status-push.sh && \
  (crontab -l 2>/dev/null; echo "* * * * * /usr/local/bin/pve-status-push.sh >/dev/null 2>&1") | crontab -'
```

## Design options kept

- `../option-2-hud.html` — HUD version without infra/probes
- `../mockup.html` — command-center mockup (infra = SSH snapshot, otherwise identical to prod)

## Gotchas

- n8n's helmet headers (`Cross-Origin-Resource-Policy: same-origin`) block cross-origin
  probes of its main page — the page probes `/healthz` instead.
- Tempest station obs come through in °C regardless of units params — page converts.
- The old `/opt/landing/index.html` single-file mount is gone; put files in `/opt/landing/html/`.
