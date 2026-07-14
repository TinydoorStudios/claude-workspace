# DiGiCo Q225 → REAPER One-Button Record Chain — Phase 2 Complete

*2026-06-27 · Memorial Hall / Jazz At The Memo · author: Brian + Nyquist*

---

## What Was Built

A one-button record chain running entirely on the .54 PC (Windows). One Companion button pulls channel names from the Q225 for inputs 1–32, renames the REAPER tracks, waits 5 seconds, and starts recording. A second button stops it.

---

## Architecture

```
Companion (on .54)
    │
    │  /record or /stop  →  UDP 127.0.0.1:9001
    ▼
reaper_relay.py  (Python, always running)
    │
    ├── /request_names ,i 1  →  UDP 192.168.200.224:1024  (console)
    │
    │   Console replies with /strip/name/N for all 72 channels
    │   Relay listens on UDP 3819, keeps only channels 1–32
    │
    ├── /track/N/name  →  UDP 127.0.0.1:8000  (REAPER OSC)  × 32
    │
    ├── (waits 5 seconds)
    │
    └── /record  →  UDP 127.0.0.1:8000  (REAPER OSC)

STOP button:
Companion  →  /stop ,i 1  →  relay  →  /stop  →  REAPER
```

---

## What We Proved / What We Learned

These are hard facts from the 2026-06-27 build session, extending the Phase 1 findings.

1. **Windows does not have the long-lived socket quirk.** Phase 1 found that on macOS a persistent UDP socket would not trigger the console — only a freshly-spawned process per send worked. On Windows .54, a long-lived in-process socket works fine. No relay workaround needed for the names request. Companion can fire `/request_names` directly.

2. **LiveTrax port 3819 is hardcoded and cannot be changed.** The LiveTrax Control Protocol Settings dialog shows the port as read-only. This made a filtering relay (intercept 72 names, forward only 1–32 to LiveTrax) architecturally impossible — both the relay and LiveTrax would be fighting for the same port on the same machine.

3. **REAPER is the better target.** REAPER was already installed on .54 with a custom template (tracks 1–32 named per show input, tracks 33–64 fixed). Since REAPER's OSC control surface can receive on any port we choose, there is no port conflict. REAPER also handles `/record` and `/stop` transport commands natively over OSC.

4. **REAPER's `/track/N/name` OSC path is a working setter.** Confirmed live: sending `/track/N/name ,s [string]` to REAPER's OSC listen port (8000) successfully renames the track. No SWS extension or ReaScript required.

5. **Port 9000 was occupied by the StreamDeck on .54.** Relay trigger port moved to 9001.

6. **Companion on .54 must use 127.0.0.1, not 192.168.200.54.** When Companion and the relay are on the same machine, the loopback address works; using the machine's LAN IP did not.

7. **Console External Control must point to .54.** In Setup → External Control → External Devices, the LTrax entry: IP `192.168.200.54`, Send Port `3819`, Rcv Port `1024`, Enabled. The console will silently ignore `/request_names` from any other IP.

8. **The console's LiveTrax macro "Record Arm" is global-only.** It sets a global record-ready state but does not arm individual tracks. It does not replace pre-armed tracks in the project template.

9. **Shift+Space in LiveTrax arms all tracks and starts recording in one command** — but this was not used because it requires LiveTrax to be the foreground window, which cannot be guaranteed reliably in a show environment. The REAPER OSC approach is foreground-independent.

---

## Network Map (Final)

| Device | IP | Role |
|---|---|---|
| Q225 console | 192.168.200.224 | listens :1024 for requests; sends names :3819 |
| .54 PC | 192.168.200.54 | runs Companion, REAPER, reaper_relay.py |

---

## Companion Button Configuration

**RECORD button**

| Field | Value |
|---|---|
| Connection | Generic OSC · 127.0.0.1 · port 9001 · UDP |
| Action | Send integer |
| Path | `/record` |
| Value | `1` |

**STOP button**

| Field | Value |
|---|---|
| Connection | Same as above |
| Action | Send integer |
| Path | `/stop` |
| Value | `1` |

---

## REAPER OSC Configuration

In REAPER: Options → Preferences → Control/OSC/web → Add

| Field | Value |
|---|---|
| Control surface mode | OSC (Open Sound Control) |
| Device name | relay |
| Mode | Configure device IP+local port |
| Device port | 9000 (outgoing feedback — unused, ignored) |
| Device IP | 0.0.0.0 |
| Local listen port | **8000** |
| Local IP | 192.168.200.54 |
| Allow binding | checked |

---

## Console External Control

Setup → External Control → External Devices → LTrax entry:

| Field | Value |
|---|---|
| Type | LTrax |
| IP | 192.168.200.54 |
| Send Port | 3819 |
| Rcv Port | 1024 |
| Enabled | yes |

---

## Files (in `digico-livetrax-macro/`)

| File | Purpose |
|---|---|
| `reaper_relay.py` | The relay. Runs permanently on .54. Trigger port 9001, names port 3819, REAPER OSC port 8000. |
| `run_relay.bat` | Opens a visible command window and runs the relay. Task Scheduler / Startup folder target. |
| `setup_autostart.bat` | One-time setup: copies `run_relay.bat` to the Windows Startup folder so the relay launches at every login. Double-click once to install. |
| `livetrax_relay.py` | Phase 1 artifact — macOS relay, not used on .54. |
| `send_request_names.py` | Phase 1 artifact — standalone one-shot sender for testing. |
| `osc_parser.py` | Phase 1 artifact — OSC decoder for reading packet captures. |

---

## Auto-Start Setup (one time)

1. Copy `reaper_relay.py`, `run_relay.bat`, and `setup_autostart.bat` to `C:\relay\` on .54.
2. Double-click `setup_autostart.bat`. It installs `run_relay.bat` in the Windows Startup folder and launches the relay immediately.
3. From now on the relay starts itself every time someone logs in to .54.

---

## Show Startup Checklist

1. Log in to .54 — relay auto-starts (look for the relay window).
2. Open REAPER, load the show template.
3. Confirm console External Control is set to .54 (one-time per desk reset).
4. Press RECORD in Companion — names pull → tracks rename → 5s → recording starts.
5. Press STOP when done.

---

## Known Limitations / Watch Points

- **Template tracks 1–32 are overwritten on every RECORD press.** Tracks 33–64 are never touched by the relay.
- **Don't double-tap RECORD** — the relay locks against double-triggering, but the console rate-limits `/request_names` anyway (fact from Phase 1).
- **5-second delay is adjustable** — edit `RECORD_DELAY` in `reaper_relay.py` if arm/name settle time needs to change.
- **Relay window must be running** before Companion buttons will do anything. If it's not up, check that `run_relay.bat` is in the Startup folder (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`).
- **If port 9001 is ever occupied**, change `TRIGGER_PORT` in `reaper_relay.py` and update the Companion connection to match.

---

*— Nyquist*
