# ShowBuilder — Deployment

## Mac (local)

Runs locally; no deployment needed.

```bash
cd ~/Documents/Claude/Code/ShowBuilder && ./run.sh    # http://localhost:8095
```

`config.json` has `audio_root` pointing at `~/Documents/Claude/audio` and
`role: "mac"`. Exports write `<Show>.brief.json` straight into the show folder
(with an overwrite confirm if one already exists).

## n8n VM (package instance) — LIVE

**https://showbuilder.tinydoorstudios.com** — capture-only instance on the n8n VM
(`192.168.200.84`), behind the remote-managed cloudflared tunnel + passcode.
systemd unit `showbuilder`, code at `/opt/showbuilder`, env at
`/etc/showbuilder.env` (root:600, `SHOWBUILDER_ROLE=package`, passcode set, no
`AUDIO_ROOT`).

What the package role does on export:
- returns the brief as a **download**, and
- keeps a server-side copy in `/opt/showbuilder/inbox/` as
  `YYYY-MM-DD_<Show>.brief.json` — the wizard lists these under
  "Recent briefs on this server", so a brief captured on a phone at the venue
  can be re-downloaded later from the Mac's browser. Nothing gets stranded.

Ops endpoints: `GET /health` (unauthenticated JSON — use for uptime checks),
`GET /api/briefs` + `GET /api/briefs/<name>` (passcode-gated inbox list/download).

Auth notes: the session cookie is an HMAC of passcode + a **per-boot secret** —
every service restart invalidates existing sessions (re-enter the passcode).
Cookies are `Secure` in package role; wrong-passcode attempts are slowed
(1–5s per consecutive failure per IP, honors `CF-Connecting-IP`).

### Redeploy

One shot, from the Mac (tees to `deploy/last_deploy.log`):

```bash
~/Documents/Claude/Code/ShowBuilder/deploy/deploy_showbuilder.command
```

That's rsync (excludes `.venv`, `_archive`, `inbox`, `mac/ShowBuilder.app`) →
`systemctl restart showbuilder` → public `/health` check. The `--exclude inbox`
also protects the VM's inbox from `--delete`.

### First-time setup (already done — kept for rebuilds)

1. rsync the project to `/opt/showbuilder`; `python3 -m venv .venv &&
   .venv/bin/pip install aiohttp`.
2. `cp deploy/showbuilder.env.example /etc/showbuilder.env` (root:600), set
   `SHOWBUILDER_ROLE=package` + a real `SHOWBUILDER_PASSCODE`, leave
   `SHOWBUILDER_AUDIO_ROOT` empty.
3. Install `deploy/showbuilder.service`, `systemctl enable --now showbuilder`.
4. cloudflared ingress `showbuilder.tinydoorstudios.com → localhost:8095` via the
   **Cloudflare API** (the n8n-tunnel is remote-managed — never edit the local
   config.yml). See `TDS_Credentials_CheatSheet.md` + the KB tunnel SOP.

### Getting a brief onto the Mac

Either grab it from "Recent briefs on this server" in any browser, or pull the
inbox directly:

```bash
scp -o ProxyJump=tds -i ~/.ssh/proxmox_tds \
  'brian@192.168.200.84:/opt/showbuilder/inbox/*.brief.json' \
  ~/Documents/Claude/audio/_inbox/
```

Drop the brief into `audio/<Venue>/YYYY-MM-DD ShowName/` and run the deep build.
