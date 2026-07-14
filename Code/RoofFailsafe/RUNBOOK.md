# Roof Failsafe — Runbook

Ordered steps. Steps 1–2 touch the live DMP and MUST be done in an off-show
window (nothing displayed to a crowd). Steps 3–5 are safe any time. Step 6 is
the real proof and also needs an off-show window (it powers off the PC).

---

## 1. Get the three values off the DMP  (off-show; read-only + one config toggle)

Log into the DMP-8000 web UI at `http://192.168.200.121` (Daktronics DMP
credentials — not the "lockdown" gate). Then, in Content Studio / the DMP
protocol config, capture:

1. **VDCP socket enabled?** The DMP must have VDCP turned on over **TCP/IP** (or
   UDP/IP) with a **port number**. If VDCP isn't enabled yet, add it — this is
   the one config change on the player. Note the port → `config.json: vdcp_port`
   and `transport`.
2. **Signal/output port number** for the roof display's Content region → the
   VDCP "signal port" → `config.json: signal_port` (commonly 1).
3. **Content ID** for the DeckLink feed. The VDCP-triggerable content lives in a
   **command sign** (Daktronics convention: a library named "Switcher"). Each
   entry has an ID. Map the DeckLink Duo (1) entry's ID →
   `config.json: cues.switcher`. If no command sign exists yet, create one in
   Content Studio that exposes `DeckLink Duo (1).dpf` on the roof output, give
   it an ID, and **push it to the player** — once resident it triggers without
   the PC.

> IDs are 8-char, space-padded (`id_mode: fixed8`). If the DMP uses longer IDs,
> set `id_mode: variable`.

Fill `config.json` (copy from `config.example.json`).

---

## 2. Bench-test the trigger  (off-show, board not in front of anyone)

From any machine on the 192.168.200.x LAN, dry-fire with the real values:

```
python3 vdcp.py --host 192.168.200.121 --port <VDCP_PORT> \
    --signal-port <SIGNAL_PORT> --id <CONTENT_ID>
# add --udp if the DMP socket is UDP; add --open-first if SELECT PORT NAKs
```

Watch the roof (or a confidence monitor) flip to the DeckLink feed. Iterate on
`--signal-port` / `--open-first` / `--id-mode` until it lands. TCP replies print
`RX 04` (ACK) / `05` (NAK).

---

## 3. Deploy the service to the n8n VM  (safe any time)

Same pattern as spl-monitor. The VM (192.168.200.84) is always-on and on the
DMP's subnet.

```
rsync -az --exclude .venv --exclude __pycache__ \
  -e "ssh -J tds -i ~/.ssh/proxmox_tds" \
  /Users/brianlloyd/Documents/Claude/Code/RoofFailsafe/ \
  brian@192.168.200.84:/opt/roof-failsafe/

ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 '
  cd /opt/roof-failsafe &&
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt &&
  sudo cp roof-failsafe.service /etc/systemd/system/ &&
  sudo systemctl daemon-reload && sudo systemctl enable --now roof-failsafe'
```

Make sure `config.json` (with the real values) is present at
`/opt/roof-failsafe/config.json`. Health check:

```
curl http://192.168.200.84:8099/            # {"ok":true,...}
```

---

## 4. Trigger #1 — TDS landing dashboard button

Add a button on the TDS command center that calls:

```
GET http://192.168.200.84:8099/fire/switcher?pass=lockdown
```

On-LAN that URL works directly. For **remote** use, expose it through the
existing remote-managed Cloudflare tunnel (same approach as
`spl.tinydoorstudios.com`): add an ingress hostname, e.g.
`roof.tinydoorstudios.com → localhost:8099`, via the Cloudflare API (token +
IDs in `TDS_Credentials_CheatSheet.md`; use the KB tunnel scripts). Then the
button hits `https://roof.tinydoorstudios.com/fire/switcher?pass=lockdown`.

## 5. Trigger #2 — Bitfocus Companion button

Companion → add a **Generic HTTP** connection → a button action:

- Method: `GET`
- URL: `http://192.168.200.84:8099/fire/switcher?pass=lockdown`

(Optional: point it at `https://roof.tinydoorstudios.com/...` if you want the
Stream Deck to work off-site too.)

Both triggers hit the same tested code path — no duplicated VDCP logic.

> Optional: import `n8n_roof_failsafe.json` if you want each fire logged / a
> Slack alert. Then point the buttons at the n8n webhook instead.

---

## 6. The real proof — power-off validation  (off-show)

The whole point is "works when the Show Control PC is dead," so test exactly
that:

1. Set the roof to normal rotation.
2. **Power off the Show Control PC.**
3. Press the dashboard button (and the Companion button). Roof must flip to the
   DeckLink/Carbonite feed.
4. Restore: power the PC back on, confirm Display Studio reclaims control
   cleanly and normal rotation resumes.

If step 3 works with the PC off, the failsafe is real. Document the confirmed
`config.json` values in this folder.

---

## Notes / gotchas

- VDCP has the switcher/automation act as controller and the DMP as the slave —
  we are the controller. Only one controller should drive a given signal port at
  once; that's fine here because the failsafe is used precisely when the normal
  controller (the PC) is gone.
- If SELECT PORT returns NAK (`RX 05`), set `open_port_first: true`.
- If the DMP is on UDP VDCP, there are no ACKs — verify by watching the display.
- Keep `config.json` out of any public repo (it contains the passcode).
