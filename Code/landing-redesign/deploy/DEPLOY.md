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

Easiest: run `../deploy-landing.command` from the Mac (picks direct-LAN or the `tds`
jump automatically, backs up both pages on the VM first). Manual equivalent:

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

## Shows board (2026-09-27)

Top panel on /rack/: every show folder from 3 days back to 21 ahead with its pipeline
stage (SCAF/PKT/SES/WIKI from show.status.json), stage-plot presence and build flags.
Show folders live on the Mac, so `../export_shows.py` builds `deploy/rack/shows.json`
and `../push-shows.command` ships it to `/opt/landing/html/rack/shows.json`.

**Auto-push (2026-09-27):** `audio/_shared/show_status.py` fires push-shows.command
(`--delay`, detached, 5 s debounce via /tmp/push-shows.lock, log /tmp/push-shows.log)
after every stamp — scaffold, packet, .ses, publish. Skipped outside audio/ and when
`SHOWS_BOARD_PUSH=0`. Fallback: `~/Desktop/Refresh Shows Board.command`; the board's
sync note turns yellow and says so when the feed is over 24 h old.

## Band advance panel (2026-09-27)

Second panel on /rack/: the advance app's bills (every act with its advance state) and
its Needs-you items, each linking into advance.tinydoorstudios.com. Feed: the advance
app's token-protected `GET /internal/board` (same data as its gated /dashboard), read
by status_writer.py every 30 s using ADVANCE_INTERNAL_TOKEN from
/opt/band-advance/advance.env, written to `/opt/landing/html/rack/advance.json`
(behind the same basic-auth gate — it carries band emails, never make it public).
A down advance app shows as an error on the panel and never blocks status.json.

## Open issues panel (2026-09-27)

Third panel on /rack/. Gear tickets: open, non-duplicate rows from the `tickets` ledger
(n8n-postgres-1), queried by status_writer.py into status.json `tickets`, sorted by
severity, each linking to its Monday item. Ledger status is reconciled from Monday
nightly, so a ticket closed on the board shows until the 7am run. KB write-backs:
unticked lines of `audio/Live Sound KB/_learning/PENDING.md`, parsed by
export_shows.py into shows.json `pending` (rides the same auto-push).

## Action buttons + webhook lockdown (2026-09-27)

Fourth panel on /rack/: Send Daily Digest, Send Crew Report, Check Missing Reports.
Two-click (arm, then fire within 5 s). The page POSTs to `/rack/run/<hook>`; nginx
(`deploy/nginx.conf`, the live copy) proxies ONLY those three paths to n8n
`/webhook/<hook>`, POST only, behind the /rack/ basic-auth gate. Advance Lifecycle
is deliberately NOT a button: it sends due band mail.

Same day, the tickets.tinydoorstudios.com vhost was narrowed from all of
`/webhook|/rest|...` to just `/form/gear-ticket` + form assets; it had been passing
every n8n webhook through. n8n.tinydoorstudios.com still reaches n8n directly via the
remote-managed tunnel, so webhooks are public there by design. Every run-now webhook
now drops calls without X-Advance-Token (Check Token node). Daily Digest, Crew Report,
FSQ Parking and Advance Lifecycle already had one; Report Reminder got its node
2026-09-27 (live export backed up to /opt/n8n or /root as report-reminder.bak.20260927.json).
The rack buttons get the header from nginx: `include /etc/nginx/run-token.conf`, a
secret file at /opt/landing/secrets/run-token.conf (mounted in docker-compose.yml, NOT
in this repo), generated from ADVANCE_INTERNAL_TOKEN in /opt/band-advance/advance.env.
Rotate the token there and regenerate that file together.
Backups: /opt/landing/nginx.conf.bak.20260927-webhooks, .bak.20260927-buttons,
docker-compose.yml.bak.20260927.
