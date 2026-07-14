# AC Infinity — Grow Tent Dashboard + Control

Self-hosted web app that reads and controls your AC Infinity controllers through
their cloud API (same backend the phone app uses — the hardware has no local
API). Built for Brian's account; confirmed against all three controllers
including the Controller AI (devType 20).

## What it does
- Live dashboard of every controller: temp / humidity / VPD. Auto-refreshes 30s.
- Shows and controls the **Advance Automation** layer (the app's "Plant Kit" /
  "Groups") — one row per automation rule (Fan / Light / Humidifier / etc.) with
  its mode (Auto/Cycle), triggers, speeds, schedule window, and an enable toggle.
  Edit drawer adjusts temp/humidity triggers, speeds, cycle times, and the active
  window, then writes back via the v2.0 Groups API.

> Why the Advance layer and not per-port On/Off: Brian runs his tents on Advance
> automation, which overrides the basic per-port mode. The basic layer reads a
> dormant flat "Off" and controlling it does nothing. The basic-mode client code
> still exists (`set_port_mode`) but the UI uses Groups only. The Groups API was
> mapped by capturing the iOS app's traffic — see `capture/`.

## Run locally
    cp aci.env.example aci.env      # fill in your AC Infinity password
    ./run.sh                        # -> http://localhost:8096

Creates a `.venv`, installs aiohttp, starts the server. Read-only by default
until you change something.

## Controllers on the account
| Name | Type | Ports |
|---|---|---|
| Hydrangea/bees balm | 69-series (devType 11) | 4 |
| GSC/WCC | Controller AI (devType 20) | 8 (6-probe sensor array) |
| New Device | 69-series (devType 11) | 4 |

## Write safety
Writes use **read-modify-write of the whole 69-field group payload**: fetch the
rule via `getGroups`, change only the requested fields (limited to `GROUP_WRITABLE`
in `aci_client.py`), post the full set back to `updateGroupsById`. Only the
well-understood, reversible settings are exposed; mode type and device wiring are
never touched. **Write path verified live 2026-06-29** (fan high-temp 78→79→78
round-trip, read back confirmed). Control is trustworthy.

## Deploy to the n8n VM (later)
Same pattern as SPL Monitor: rsync `app/` + `web/` to the VM, run under systemd
with `aci.env` as the EnvironmentFile, set `ACI_PASSCODE`, and route a
`*.tinydoorstudios.com` host to its port via the Cloudflare tunnel.

## Files
- `app/aci_client.py` — cloud API client (login, list, read, write)
- `app/server.py` — aiohttp server + JSON API
- `web/` — dashboard UI
- `probe.py` — standalone read-only diagnostic dump
