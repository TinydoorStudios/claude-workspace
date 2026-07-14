# Live deployment (as built 2026-06-06)

Public URL: **https://spl.tinydoorstudios.com**

> **CURRENT HOST (updated 2026-06-15).** The app no longer runs on the Pi. It runs
> as systemd `spl-monitor` on the **n8n VM `192.168.200.84`**, dir `/opt/spl-monitor`,
> user `brian`. Deploy from the Mac:
> ```
> rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
>   -e "ssh -i ~/.ssh/proxmox_tds" \
>   /Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/ brian@192.168.200.84:/opt/spl-monitor/
> ssh -i ~/.ssh/proxmox_tds brian@192.168.200.84 'sudo systemctl restart spl-monitor'
> ```
> **Nightly-email gotcha (root-caused + fixed 2026-06-15):** n8n is now *containerized*
> (compose bridge net `n8n_default`), so the email workflow's HTTP node must call
> spl-monitor at the **host LAN IP `http://192.168.200.84:8090/api/daily/email`** —
> NOT `localhost:8090` (that resolves to the n8n container, which has nothing on 8090).
> It had been erroring every night since the VM migration. The Slack violation path is
> unaffected (that's host→container on `localhost:5678`). After any workflow edit,
> `publish:workflow` + **restart the n8n container** for the live scheduler to reload it.

## Topology
```
[ Smaart v8.5 @ work ]                 [ Raspberry Pi @ homelab 192.168.0.2 ]        [ Cloudflare ]
  DiGiCo UB MADI ASIO / SPL              spl-monitor.service (systemd)                 n8n tunnel b1e6581d
  API @ 192.24.143.121:26000   <----    backend.app on 127.0.0.1:8090        <----    ingress: spl.tinydoorstudios.com
  (work public IP, port-forward)         connects out to the work rig                  -> http://localhost:8090
                                                                                       (added via CF API; DNS routed)
```

## Pi (192.168.0.2, user `brian`)
- App dir: `/home/brian/spl-monitor` (venv at `.venv`, aiohttp).
- Env: `/home/brian/spl-monitor/.env` (chmod 600) — `SMAART_HOST=192.24.143.121`, `SMAART_PORT=26000`, `SPL_HOST=127.0.0.1`, `SPL_PORT=8090`, `SPL_SOURCE=smaart`.
- Service: `/etc/systemd/system/spl-monitor.service` — **enabled** (auto-start on boot), `Restart=always`.
- SSH from the Mac: key `~/.ssh/spl_deploy` → `ssh -i ~/.ssh/spl_deploy brian@192.168.0.2`.

## Cloudflare
- `spl.tinydoorstudios.com` is a public hostname on the **existing n8n tunnel** (`b1e6581d-…`), added to its remote (dashboard-managed) config via the Cloudflare API using the token inside `~/.cloudflared/cert.pem`. The DNS CNAME was already routed to that tunnel.
- No extra cloudflared process — rides the n8n `cloudflared.service`.
- The throwaway dedicated `spl-monitor` tunnel created during setup was deleted.

## Manage
```bash
# status / logs
systemctl status spl-monitor
journalctl -u spl-monitor -f          # PYTHONUNBUFFERED=1 so prints show
# look for: [smaart] streaming DiGiCo UB MADI ASIO / SPL

# restart after a config/limit change
sudo systemctl restart spl-monitor

# redeploy code from the Mac
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  -e "ssh -i ~/.ssh/spl_deploy" \
  /Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/ brian@192.168.0.2:/home/brian/spl-monitor/
ssh -i ~/.ssh/spl_deploy brian@192.168.0.2 'sudo systemctl restart spl-monitor'

# change venue limits: edit /home/brian/spl-monitor/config.json on the Pi, then restart
```

## Behavior notes
- Compliance number is the rig's **native `LAeq 6`** (6-min); limit set to **88 warn / 90 red** to match the rig's `LAeq 6` alarm. Adjust per venue in `config.json` or the UI venue switcher.
- Only **one** client may connect to the rig API at a time — the app is that client. Don't run debug connections against `192.24.143.121:26000` while the service is up.
- With the rig off / not logging, the portal shows a **standby screen** ("show logging is currently not occurring at this time", green ONLINE pulse) and flips to the live dashboard automatically the moment logging starts — and back to standby when it stops. Detection: no measurement frame in `STALE_SECONDS` (9s); rig pushes ~every 3s.
- Responses are sent `Cache-Control: no-cache` (+ versioned `?v=` assets) so a phone never shows a stale dashboard after a deploy.
- **Violations / 3-strikes** (`config.json` -> `violations`): trigger is the **10-second LAeq** (`metric: "LAeq 10s"`, `sustainSeconds: 0`) >= 90 dBA = one violation; clears below 90. Uses a native Smaart `LAeq 10s` metric if present in the stream; otherwise falls back to the app-computed 10s LAeq (coarse — rig only streams every ~3s, so add the native metric for accuracy). The injection key matches `vtracker.metric`, so renaming the config metric to whatever Smaart calls it (e.g. `LAeq 10`) just works. On-screen strike counter (auto-resets each session after a 5-min data gap). Strikes 1-3 silent; **every violation from #4 fires a Slack alert**, and **any violation past 60s fires one too** (even the first). Alerts POST to `violations.alertWebhookUrl` (`SPL_ALERT_WEBHOOK` in `/home/brian/spl-monitor/.env`), in real time when confirmed.

**Slack DM is wired and live:** `SPL_ALERT_WEBHOOK=http://localhost:5678/webhook/spl-violation` → n8n workflow **"SPL Violation Alerts"** (id `O9VD8lZ1Qse8mNvY`, active) → Slack node DMs Brian (user `UHSLD08SV`) via the dedicated **`SPL Monitor Bot`** credential (`41ISkkYndJkVczWk`) — a standalone Slack app named "SPL Monitor" (separate from the Tempest weather bot), so alerts arrive in their own DM thread. The webhook node reads `{{$json.body.text}}` (the app composes the message). Verified end to end 2026-06-06. To change wording/format, edit the n8n workflow; to change trigger thresholds, edit `config.json` + restart `spl-monitor`.

## Nightly report email
- n8n workflow **"SPL Nightly Summary Email"** (`WjnKfJhmYEsRF4Iq`): Schedule **10:30 PM** → HTTP GET `http://localhost:8090/api/daily/email` → Code (build PDF + CSV binaries) → Gmail (`3CDCProduction@gmail.com`) → **blloyd@3cdc.org**, both attachments.
- The app bundles the whole email at `/api/daily/email`: `{subject, html, show, band, engineer, engineerCode, csvFilename, csvBase64, pdfFilename, pdfBase64}`. PDF built in a thread (matplotlib).
- **PDF report** (`backend/report.py`, Smaart-style): header/metadata, Max/L10/L50/L90 stats table for the full metric set, violations table, and history graphs (SPL A Slow / LAeq 10s / LAeq 6) with **violations shaded red**.
- Per-second CSV now logs the **full metric set** (`logging_csv.py` METRIC_COLS) so the stats table is complete.
- "Report day" rolls at 5am; merged night CSV filtered to that window.
- Pi plotting libs: `python3-matplotlib python3-reportlab python3-numpy` via **apt**, linked into the venv with `.venv/lib/python3.13/site-packages/zz-system-site.pth` -> `/usr/lib/python3/dist-packages` (keeps the venv's own aiohttp).
- **Show/Location/Engineer block (added 2026-07-01):** subject line and HTML body now lead with the night's show, location, and engineer — see "Show/Engineer info" section below. Looked up fresh for the requested report `day` (not just "today"), so a re-run of the email for a past date still gets the right answer.

## Show/Engineer info (added 2026-07-01)
- **Source:** three public ("anyone with the link can view") Google Sheets — no auth/API key. `backend/showinfo.py` pulls each as CSV via `.../export?format=csv&gid=<gid>`.
  - Main crew schedule (`10idHRr...NnJw`, gid `1413426845`) — FSQ block is columns G–J (date/DOTW/event/mix-code).
  - Crew code cross-reference, same spreadsheet, gid `809527620` — mix-code → full name.
  - Band booking sheet (`167bpW3...KSy5XVs`, gid `0`) — Date/Location/Performer; filtered to `Location == FSQ`, gives the real band/event name when the schedule sheet just has a placeholder ("Reggae (4-11)", "TBD", etc.).
  - All IDs/gids/column indices live in `config.json` under `showInfo` — edit there if a sheet's tab layout ever changes, no code change needed for a column shuffle.
- **Live dashboard banner:** `ShowInfoTracker.refresh()` polls every `showInfo.refreshSeconds` (default 300s), matches today's date (America/New_York), and broadcasts a `{"type":"showinfo", show, engineer, band, event, engineerCode}` WS message only when it changes. New clients get the current value immediately on connect. Also exposed at `GET /api/show-info` for debugging. Frontend renders it as a banner under the top bar (`web/index.html` `#showBanner`, `web/app.js` `onShowInfo()`).
- **Nightly email:** `ShowInfoTracker.for_date(day)` re-fetches on demand (doesn't rely on the cached "today" value) and the result is merged into `/api/daily/email`'s payload and HTML.
- **Dependency:** the VM needs outbound HTTPS to `docs.google.com`. If that ever gets firewalled, the banner/email fields silently go blank (`enabled` fetch failures are logged, never crash the request) — check `journalctl -u spl-monitor` for `[showinfo] fetch failed` if the banner stops updating.
- **Extending to another venue:** the tracker is keyed to one `bandLocation` (currently `"FSQ"`) and one FSQ-shaped column block. Memorial Hall's columns exist further right in the same schedule sheet (X onward) but aren't wired up — `comingSoon` venue, not currently needed.

## Open / next
- Confirm live data on `spl.tinydoorstudios.com` with the rig on (proven working end-to-end 2026-06-05).
- Optional: Cloudflare Access policy to gate the URL to Brian's login.
- [RESOLVED 2026-06-06] The n8n tunnel was being run twice — once by systemd (`cloudflared.service`) and once by PM2 (entry `cloudflare-tunnel`). Removed the PM2 duplicate + `pm2 save`; systemd is now the sole runner (one connector, ~4 connections). PM2 runs only n8n + tempest-dashboard.
- PM2 daemon is out of date in memory (6.0.13 vs installed 7.0.1) — `pm2 update` reconciles it but restarts the daemon (brief n8n/tempest blip); do it in a maintenance window.
- `cloudflared` is 2025.10.0; newer available (2026.5.2) — optional upgrade.
