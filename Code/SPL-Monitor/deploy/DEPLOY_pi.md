# Deploy SPL-Monitor on the Pi (n8n homelab) → view anywhere via Cloudflare

Topology: **Pi runs the app** → connects over the internet to **work Smaart public IP : 26000** →
dashboard served locally on `127.0.0.1:8090` → exposed by **Cloudflare tunnel**.

## 0. Work side (Smaart machine) — prerequisites
- Static/public IP known; router **port-forwards 26000 → Smaart LAN IP**.
- Smaart: **Options > Preferences > API > Enabled** (indicator green).
- Measurement mic input **calibrated and actively logging**.
- **Set an API password** in that same dialog (the port is internet-facing).
- Harden: if possible, restrict the 26000 port-forward to **only the Pi's public IP** as source.

## 1. Get the code onto the Pi
From a machine with SSH to the Pi (rsync the project, excluding the local venv/logs):
```bash
rsync -av --exclude .venv --exclude logs --exclude '*.pyc' \
  ./SPL-Monitor/  pi@<PI_HOST>:/opt/spl-monitor/
```

## 2. Python env on the Pi
```bash
ssh pi@<PI_HOST>
cd /opt/spl-monitor
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install aiohttp
```

## 3. Environment / secrets
```bash
sudo cp /opt/spl-monitor/deploy/spl-monitor.env.example /etc/spl-monitor.env
sudo nano /etc/spl-monitor.env      # fill SMAART_HOST, SMAART_PASSWORD
sudo chmod 600 /etc/spl-monitor.env
```

## 4. Smoke test (foreground, before the service)
```bash
set -a; . /etc/spl-monitor.env; set +a
./.venv/bin/python -m backend.app
# look for: "[smaart] streaming <device> / <channel>"
# then curl from another shell:  curl -s localhost:8090/ | head
```

## 5. systemd service (auto-start, auto-restart)
```bash
sudo cp /opt/spl-monitor/deploy/spl-monitor.service /etc/systemd/system/
# edit User= in the unit if not 'pi'
sudo systemctl daemon-reload
sudo systemctl enable --now spl-monitor
systemctl status spl-monitor
journalctl -u spl-monitor -f
```

## 6. Expose via Cloudflare

### Fast path (instant, for tonight's show) — quick tunnel
```bash
cloudflared tunnel --url http://localhost:8090
# prints a https://<random>.trycloudflare.com URL — open it anywhere
```

### Permanent path — named tunnel + subdomain
Add an ingress rule to the existing cloudflared config (usually
`/etc/cloudflared/config.yml` or `~/.cloudflared/config.yml`):
```yaml
ingress:
  - hostname: spl.tinydoorstudios.com
    service: http://localhost:8090
  # ... existing n8n rule ...
  - service: http_status:404
```
Then point DNS at the tunnel and restart:
```bash
cloudflared tunnel route dns <TUNNEL_NAME> spl.tinydoorstudios.com
sudo systemctl restart cloudflared
```
Optional: protect it with a **Cloudflare Access** policy (Zero Trust) so only your
email can open `spl.tinydoorstudios.com`.

## Notes
- Dashboard binds to `127.0.0.1` only — the tunnel is the only way in. Never port-forward 8090.
- The app auto-reconnects to Smaart if the link drops (3s retry), so a flaky work uplink won't kill it.
- To switch a venue/limits, edit `config.json` and restart the service.
