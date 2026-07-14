# UniFi OS Server → Raspberry Pi Migration — Handoff
*2026-06-07*

---

## Goal

Migrate the locally-hosted **UniFi OS Server** running on Brian's Mac to a **Raspberry Pi 4** (8GB), so the Pi becomes the always-on UniFi controller.

**Key compatibility fact:** UniFi OS Server (the "UOS" wrapper app) is **x86-64 only — does NOT run on ARM/Pi**. The Pi runs the **UniFi Network Application** (the controller underneath), via Docker. Settings/devices migrate between them with a `.unf` backup because it's the same Network app under the hood. So this is: UniFi OS Server (Mac) → UniFi Network Application in Docker (Pi).

---

## The Pi

- **Hardware:** Raspberry Pi 4, **8GB RAM** (7.6 GiB reported), aarch64.
- **OS:** Ubuntu 26.04 LTS, kernel 7.0.0-1009-raspi.
- **Hostname:** `unifyberry`
- **User:** `brian` / password `brian` (uid 1000, gid 1003, in sudo + docker groups).
- **Static IP (set this session):** **192.168.0.3/24**, gw 192.168.0.1, DNS 192.168.0.1 + 8.8.8.8, on **eth0**.
- **WiFi:** `wlan0` kept on DHCP (SSID "Area 53"). Brian chose to keep both links.

### Access (already wired up on the Mac)
- SSH alias: **`ssh unifyberry`** → 192.168.0.3, user brian, key `~/.ssh/unifyberry` (added to `~/.ssh/config`).
- Dedicated key `~/.ssh/unifyberry` (ed25519, no passphrase) — public key installed in the Pi's `authorized_keys`.
- `sudo` needs the password — pattern used: `echo brian | sudo -S <cmd>`. (Passwordless sudo NOT set up.)

---

## Network gotcha (resolved — don't re-chase it)

The Pi kept showing **10.10.10.2** for a long time. Cause: it was patched into the **Mac's en7 USB-ethernet adapter** (which holds a permanent 10.10.10.66/16 and was feeding it that address). On the real switch it DHCPs normally. It now has a clean static .3. The "either .119 or .126" the router showed = same Pi on eth0 (.119, since replaced by static .3) and wlan0 (.126).

Other notes from the slog:
- Fresh Ubuntu image had SSH off; enabled via `apt install openssh-server` at the console.
- "unknown command" errors were just **missing `sudo`** (the `ip` tool's permission error), NOT a keyboard/slash problem.
- `ifconfig` not installed (no net-tools) — use `ip`.
- Console font was tiny; `setfont Ter-132b` (or `Lat15-Terminus32x16`) enlarges it.
- Reading the Pi screen remotely: opened **Photo Booth** on the Mac with **Brian's iPhone as Continuity Camera** (works; image is mirrored in Photo Booth's live view).

---

## Networking config written this session

- `/etc/netplan/50-cloud-init.yaml` — **overwritten** with static eth0 (.3) + wifi (wlan0 DHCP, Area 53). chmod 600.
- `/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg` → `network: {config: disabled}` so cloud-init won't clobber the static on reboot.
- `netplan generate` validated OK; `netplan apply` succeeded; .3 verified reachable, internet OK.

---

## Software installed

- **Docker 29.5.3** + **Compose v5.1.4** (via get.docker.com). `brian` added to `docker` group, docker enabled+started. `docker ps` works without sudo in a fresh SSH session.

---

## UniFi stack — WRITTEN but NOT yet started

Directory **`/opt/unifi`** (owned by brian) contains:

- **`docker-compose.yml`** — two services on a `unifi` bridge network:
  - `unifi-db`: **`docker.io/mongo:4.4`** (pinned to 4.4 on purpose — see below), volume `./db`, runs `./init-mongo.js` on first init.
  - `unifi-network-application`: **`lscr.io/linuxserver/unifi-network-application:latest`**, depends_on db, PUID=1000/PGID=1003, TZ=America/New_York, MEM_LIMIT/STARTUP=1024, volume `./config`, ports 8443/3478udp/10001udp/8080/1900udp/8843/8880/6789/5514udp. MONGO_USER=unifi, MONGO_HOST=unifi-db, MONGO_DBNAME=unifi.
- **`init-mongo.js`** — creates `unifi` user (dbOwner) on `unifi` + `unifi_stat` dbs.
- **Mongo password:** `50801de4aeef8da8fc4481b26569a36a` — saved on the Mac at `~/.unifi_mongo_pass.txt` and embedded in the compose `MONGO_PASS`.

### CRITICAL Pi-4 / Mongo note
Pi 4 CPU is **ARMv8.0**; **MongoDB 5+ requires ARMv8.2 and will crash** ("illegal instruction"). That's why Mongo is pinned to **4.4** (arm64, runs on Pi 4, and is a UniFi-supported Mongo version). Do NOT bump Mongo to 5/6/7.

---

## NEXT STEPS (resume here)

1. **Start the stack** (this is the command that was about to run when we paused):
   ```
   ssh unifyberry 'cd /opt/unifi && docker compose up -d'
   ```
   Pulls mongo:4.4 + linuxserver image (few min). Watch for mongo "illegal instruction" — if it appears, the 4.4 pin failed somehow; investigate an ARMv8.0-safe mongo.
2. **Verify** containers healthy: `ssh unifyberry 'docker ps; docker logs unifi-network-application --tail 30'`. App listens on **https://192.168.0.3:8443** (self-signed).
3. **Confirm controller version >= 9.5.21** before restoring (latest tag should be). If not, pin the linuxserver image to a `9.5.21`+ tag.
4. **Restore the backup:**
   - Backup on Mac: **`/Users/brianlloyd/Downloads/network_backup_03.12.2026_06-08-PM_v9.5.21.unf`** → confirms source **Network app v9.5.21** (the "v5" Brian saw was the UOS wrapper version).
   - **This backup is from March 12, 2026 (~3 mo old).** Recommend Brian export a FRESH backup first: UniFi OS Server → Network → Settings → System → Backups → Download. Use the newest `.unf`.
   - Restore via the new controller's setup wizard at https://192.168.0.3:8443 → "Restore from backup" → upload the `.unf`. (A backup restores only into an **equal-or-newer** Network version — 9.5.21 target is fine.)
5. **Re-adopt devices:** small home network, handful of devices. After restore, devices need to point at the new controller (inform host 192.168.0.3). May need set-inform via SSH to each device, or layer-2 adoption since they're on the same LAN. Confirm device count/types with Brian (never got specifics).
6. **Decommission** the Mac's UniFi OS Server once the Pi is confirmed managing everything.

---

## Open items / unknowns

- Exact UniFi device inventory (count/models) — not captured. Brian said "small home / few devices."
- Whether to set a DHCP reservation for .3 on the router as belt-and-suspenders (static is already set on the Pi).
- The Mac has a permanent 10.10.10.66/16 on en7 (some other gear's network) — unrelated, leave alone.
- Consider a Mongo 4.4 data backup routine once live.

## Side win this session
Fixed Brian's Mac **Messages → Android (green-bubble SMS) failing**: it was **Text Message Forwarding** off on the iPhone. Mac iMessage settings were healthy (signed in as lordkovax@yahoo.com, phone # registered). After enabling Text Message Forwarding on the iPhone, green-bubble sends started working (confirmed live in the thread).
