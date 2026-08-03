# SPL Monitor — VM Deployment (Critical)

Moved out of the always-loaded project `CLAUDE.md` on 2026-08-02. This file loads automatically
whenever Claude is working under `Code/SPL-Monitor/`.

The hard rule that stayed in the root file: **never rewrite a VM/Pi `.env` partially** — always
write the full set of vars. A partial rewrite silently drops critical overrides (this is how
`SPL_PORT=8090` got dropped once and 502'd the public URL).

---

Live at **https://spl.tinydoorstudios.com** — systemd service `spl-monitor` on the **n8n VM** (`192.168.200.84`), at `/opt/spl-monitor`, running as user `brian`. **Migrated off the Pi 2026-06-09** (Pi was powered off; this is now its permanent home). SSH key: `~/.ssh/proxmox_tds`. Source of truth: `/Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/` on Mac.

**Network path (corrected 2026-06-17):** the VM is `192.168.200.84` — the old `192.168.0.x` subnet is retired and `192.168.0.125` is dead. Two working routes: (1) **direct** `ssh -i ~/.ssh/proxmox_tds brian@192.168.200.84` when the Mac is on the house/venue LAN (confirmed working 2026-06-17 — the older "Mac can't reach .200.x directly" note was wrong; it can when on-LAN); (2) **ProxyJump through `tds`** (`ssh -J tds ...`) from anywhere — `tds` is the Tailscale node `tinydoorstudios-dashboard-server` = Proxmox host `pve`. The Cowork sandbox can't reach the LAN, but a Claude Code shell with the sandbox disabled can (this is how the 2026-06-17 deploy ran). The `deploy_tz_fix.command` in the repo also works from Brian's terminal.

**Tailscale SSH jump no longer prompts (fixed 2026-06-17):** the `-J tds` hop used to stall on *"Tailscale SSH requires an additional check, visit <URL>"* every ~12h. Cause = the tailnet policy's default `ssh` rule used `"action": "check"` (periodic browser re-auth for `autogroup:self`/root). Changed it to `"action": "accept"` in the Tailscale admin ACL (line 54 of the policy file). Key auth still gates the connection; the browser re-auth is gone for all `-J tds` jumps (SPL deploys, KB stack, etc.). To revert, set that rule back to `"check"` (optionally with `"checkPeriod": "168h"`).

**Deploy command (rsync to VM via tds, then restart):**
```
rsync -az --exclude .venv --exclude logs --exclude __pycache__ -e "ssh -J tds -i ~/.ssh/proxmox_tds" /Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/ brian@192.168.200.84:/opt/spl-monitor/ && ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'sudo systemctl restart spl-monitor'
```
`/opt/spl-monitor` is owned by `brian`, so rsync needs no sudo. Deps live in `/opt/spl-monitor/.venv` (aiohttp, reportlab, matplotlib, numpy). `rsync` had to be `apt install`-ed on the VM.

**Timezone (fixed 2026-06-16):** VM was on `Etc/UTC`, making all backend timestamps +4h. Set VM system tz with `timedatectl set-timezone America/New_York` AND pinned `TZ=America/New_York` in `/etc/spl-monitor.env` (include it in the full var set below). Dashboard on-screen clock also forced to NY in `web/app.js`.

**.env at `/etc/spl-monitor.env` (root:600) — always write ALL of these, never partial:**
```
SPL_SOURCE=smaart
SMAART_HOST=192.24.143.121
SMAART_PORT=26000
SPL_PORT=8090
SPL_ALERT_WEBHOOK=http://localhost:5678/webhook/spl-violation
TZ=America/New_York
```
`SPL_PORT=8090` is critical — config.json default is 8080; dropping it breaks the public URL. Webhook is now `localhost:5678` since spl-monitor and n8n run on the same VM. The systemd unit is `/etc/systemd/system/spl-monitor.service` (`EnvironmentFile=/etc/spl-monitor.env`).

**spl public routing (corrected 2026-06-09):** spl.tinydoorstudios.com's DNS CNAME points to the **`n8n-tunnel` (b1e6581d)**, which routes `spl → localhost:8090` on the VM. (The old CLAUDE.md note about a separate "TDS Cold Storage" tunnel at the SMAART box was WRONG.) The portal serves a standby screen with no SMAART data — it only 502s if the VM service itself is down. SMAART data source is the show box at `192.24.143.121:26000` (only up during shows).

To test with generated data: set `SPL_SOURCE=simulator` in `/etc/spl-monitor.env`, restart, test, then restore `SPL_SOURCE=smaart`.

**Show/Engineer banner + nightly email (added 2026-07-01):** dashboard now shows tonight's FSQ show name and engineer, and the nightly email leads with a Show/Location/Engineer block. Sourced from three public Google Sheets (crew schedule, crew-code cross-reference, band booking — all "anyone with the link" view-only, no API key) via `backend/showinfo.py`, refreshed every 5 min for the live banner and re-fetched fresh per report-day for the email. Requires the VM to have outbound HTTPS to `docs.google.com` — if that's ever blocked, the fields just go blank (logged as `[showinfo] fetch failed`, doesn't break the dashboard or email). Full detail in `Code/SPL-Monitor/docs/DEPLOYED.md`.
