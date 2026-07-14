# JVC Camera Reset

Remotely reproduces the "turn video off, then back on at the controller" fix for
three networked **JVC KY-PZ100** PTZ cameras that lose network control when a
control browser is left open too long.

## Why this happens
The KY-PZ100's control plane is **single-client by design**. JVC's own Web API
spec states *"another client cannot connect while the first client is using the
API interface,"* and the session it hands out expires every 30 seconds and must
be renewed. A control browser left open holds that single slot and keeps
renewing it; over hours the session wedges and nothing else — including the
RM-LP100 controller — can take over until the camera's video pipeline is
bounced. That bounce is your manual fix. This tool does it over the network.

## How it works
Runs on the **n8n VM** (same LAN as the cameras); the Mac can't reach the cameras
directly (only the VM, over Tailscale), so the VM does the work and the Mac
triggers it. The tool uses two of the camera's HTTP channels:
- **`cgi-bin/api.cgi`** (auth via `api.php` → SessionID) — for status probes.
- **`cgi-bin/cmd.cgi`** (auth via `login.php` → a *web* SessionID) — the channel
  the web control page uses, and the only one that accepts the video off/on key.

The `video` reset replays exactly what the web UI / RM-LP100 does for "video
off/on": `SetWebKeyEvent {Kind:System, Key:VideoOutputOff}` then a
`{Kind:Disptv, Key:Set}` commit, wait, then `VideoOutputOn` + commit. Turning
video back on makes the camera **reinitialise its pipeline** — it drops off the
network for ~30–45s and returns, which is what clears a wedged control plane.

Three triggers, same `video` reset:
- **Portal button (primary)** — `https://tinydoorstudios.com/cameras/` has one
  big **Reboot all cameras** button plus live status of the three. Behind a
  single-password gate served by the app itself (passcode `lockdown`, override
  with `JVC_PASSCODE`). Works from any device, including phone.
- **On-demand (Mac)** — double-click `Reset_JVC_Cameras.command`.
- **Scheduled** — `jvc-reset.timer` on the VM (installed, left off) runs with
  `--if-wedged`, resetting only cameras that fail a control probe (twice) so a
  healthy / in-use camera is never interrupted.

### Portal button — how it's wired
`web.py` is a tiny stdlib HTTP service (systemd `jvc-cameras-web`, on
127.0.0.1:8092) that serves the button page and, on click, launches
`reset_cameras.py --method video` in the background. It gates itself with a
single-password login (cookie-based; passcode `lockdown`). The existing
**landing** nginx (host-network container) proxies it at
`tinydoorstudios.com/cameras/` — `auth_basic` was removed from that location so
the only prompt is the app's password box (`deploy/deploy_passcode_gate.command`
does this edit). The portal `index.html` has a Cameras card. No Cloudflare
/ DNS changes — it lives under the already-routed portal host. The nginx
`location /cameras/` + the portal card are a one-time edit to `/opt/landing`
(`nginx.conf` + `index.html`); everything else is in this repo.

## Reset methods
| Method | What it does | Notes |
|---|---|---|
| `video` (default) | `SetWebKeyEvent` VideoOutputOff → wait → VideoOutputOn (+ commit), via `cmd.cgi` | **The real fix** — identical to the controller's video off/on. Camera reinitialises (~30–45s offline) and returns. Confirmed on all three cameras 2026-06-21. |
| `stream` | `SetStreamingCtrl` Off → wait → On | Bounces only the IP stream/encode pipeline. Executes cleanly but does **not** reinitialise the camera. Fallback only. |
| `reboot` | `SystemRequest` Reboot | **Rejected** by PZ100 firmware (`CommandError`) — JVC only supports it on PZ200/400/510. Do not rely on it here. |
| `status` | Probe only, no change | Prints video-output / menu / streaming state. |

## Status (tested 2026-06-21, against the live cameras)
All three cameras (`.11` :80, `.12` :5002, `.13` :5003, login `jvc`/`0000`)
reachable and controllable. The `video` reset was verified on each: CAM 1
On→Off→On, CAM 2 and CAM 3 brought from Off→On — each reinitialised and returned
within ~45s. The tool handles JVC's malformed JSON (trailing comma + missing
final brace), CAM 2/3's ~10s latency on the high ports, and retries the
transient `SessionError`/`DualExeError` the single-client control plane throws.

The scheduled timer is installed but **left disabled** until the `video` reset
is confirmed to clear a real wedge (next time one happens, run the Mac
`.command`; if control returns, enable the timer). It can never bounce a live
camera prematurely while off.

## Files
```
reset_cameras.py             core tool (runs on the VM)
web.py                       portal button service (systemd jvc-cameras-web, :8092)
config.json                  camera IPs + web login + timing
Reset_JVC_Cameras.command    Mac on-demand trigger (double-click)
requirements.txt             requests
deploy/deploy.command        Mac -> VM deploy (rsync + venv + services)
deploy/jvc-reset.service     systemd oneshot (--if-wedged)
deploy/jvc-reset.timer       systemd timer (every 30 min)
deploy/jvc-cameras-web.service  systemd unit for the portal button
deploy/DEPLOY.md             deploy + test procedure
```

## Usage (on the VM)
```bash
# probe only
reset_cameras.py --method status
# the real video off/on reset, all three
reset_cameras.py --method video
# reset just one
reset_cameras.py --method video --camera "CAM 1"
# only reset cameras that are actually wedged (scheduled mode)
reset_cameras.py --method video --if-wedged
```
