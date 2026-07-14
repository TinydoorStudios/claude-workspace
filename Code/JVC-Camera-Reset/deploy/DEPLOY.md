# Deploy & Test — JVC Camera Reset

Runs on the **n8n VM** (`192.168.200.84`), which is on the camera LAN. The Mac
only talks to the VM over Tailscale, so the VM does the camera work; the Mac
triggers it.

## 1. Fill in `config.json`
Edit the three camera static IPs, and the camera web `username`/`password`
(leave both blank if the cameras have no web login set). `off_seconds` is how
long video is held off before turning back on (default 5).

## 2. Deploy
Double-click **`deploy/deploy.command`** on the Mac (or run it from a terminal).
It rsyncs the code to `/opt/jvc-reset`, builds a venv with `requests`, and
installs + enables the `jvc-reset.timer`. Safe to re-run after any edit.

Manual equivalent:
```bash
rsync -az --exclude .venv -e "ssh -J tds -i ~/.ssh/proxmox_tds" \
  ~/Documents/Claude/Code/JVC-Camera-Reset/ brian@192.168.200.84:/opt/jvc-reset/
ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84
  python3 -m venv /opt/jvc-reset/.venv
  /opt/jvc-reset/.venv/bin/pip install -r /opt/jvc-reset/requirements.txt
```

## 3. Test — do this once before trusting it (I can't reach the cameras to test)
SSH to the VM (`ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84`), then:

**a) Prove connectivity (no change made):**
```bash
/opt/jvc-reset/.venv/bin/python /opt/jvc-reset/reset_cameras.py --method status
```
You should see `power=`, `menu=`, `streaming=` for each camera. If a camera
errors here, fix its IP / credentials first.

**b) Run the real video off/on reset on ONE camera:**
```bash
/opt/jvc-reset/.venv/bin/python /opt/jvc-reset/reset_cameras.py \
    --method video --camera "CAM 1"
```
This sends VideoOutputOff → wait → VideoOutputOn (the controller's exact action).
The camera goes **offline ~30–45s to reinitialise**, then returns with video On
— verify with `--method status --camera "CAM 1"` a minute later. (Confirmed
working on all three cameras 2026-06-21.)

To confirm it clears the real problem: next time control wedges (web page stuck /
black), run `--method video` and check whether control + video come back.
- **Yes** → enable the scheduled auto-healer (step 5).
- **No** → capture the camera web UI's **Reboot** request (gear/settings tab,
  F12 → Network) and send it over to add as another method. (API `reboot` is
  confirmed rejected by PZ100 firmware — `CommandError`.)

## 4. On-demand from the Mac
Double-click **`Reset_JVC_Cameras.command`**. It SSHes to the VM, runs the
`video` reset on all three, and saves a local log. (Edit `METHOD` at the top to
`status` for a dry check, or `stream` for the lighter stream-only bounce.)

## 5. Scheduled (automatic healing) — installed but OFF by default
The deploy script installs the timer but does **not** enable it. Turn it on only
after the `video` reset is confirmed to clear a real wedge (step 3b), so it can't
disrupt a live camera prematurely. It runs every 30 min with `--if-wedged`:
probes each camera (twice, to ignore transient blips) and **only resets the ones
that don't answer**.

```bash
sudo systemctl enable --now jvc-reset.timer  # turn it ON when ready
systemctl list-timers jvc-reset.timer        # see next run
journalctl -u jvc-reset.service -n 50        # see what it did
sudo systemctl stop jvc-reset.timer          # pause (e.g. during a show)
sudo systemctl disable jvc-reset.timer       # turn it OFF
```

Adjust cadence in `jvc-reset.timer` (`OnUnitActiveSec=`) and re-run the deploy
script, or `sudo systemctl daemon-reload && sudo systemctl restart jvc-reset.timer`.
