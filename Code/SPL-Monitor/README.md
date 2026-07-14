# SPL-Monitor

A 10EaZy-style remote SPL/compliance dashboard, fed by a Smaart v8 system over its WebSocket API.

The idea: the Smaart box stays the calibrated measurement engine. This app is a **read-only API client** that pulls Smaart's live SPL/LEQ numbers over the network and renders a big, dead-simple compliance dashboard on a second PC — so Brian never has to mirror calibration or touch a mic on the second machine.

## Locked decisions (as of 2026-06-04)

- **Source of truth:** Smaart v8 (calibrated). This app never measures audio itself; it consumes Smaart's computed values via the API. Keeps calibration intact.
- **Delivery:** local web dashboard — a small Python backend serves a browser UI. Open it on any PC/tablet on the LAN. Later we can wrap it as a standalone app.
- **Features:**
  - Big SPL readout + green/yellow/red traffic light vs a limit
  - Predictive "future level" projection (10EaZy's signature move)
  - Continuous logging to file (CSV + XML)
  - End-of-event PNG/PDF summary report — **file only for now**, no email yet
- **Two rolling LAeq windows:** 10-second (live/responsive) and 6-minute (compliance). Traffic light keys off the 6-minute LAeq vs limit; the 10-second is the live feel. (Confirm with Brian.)
- **Limits:** per-venue config. Placeholders until Brian supplies real numbers for Memorial Hall and the 3CDC outdoor venues.
- **Smaart link:** v8.3+ WebSocket API, same LAN, default port 26000. The built-in **SPL Webviewer** (`http://<smaart-ip>:26000`) is the reference client whose traffic we mirror.

## Architecture

```
[ Smaart v8 PC ]                         [ Second PC (this app) ]
  calibrated mic                           Python backend
  SPL/LEQ engine        WebSocket           - Smaart API client (or simulator)
  API @ :26000   <----  JSON over LAN  ---- - rolling LAeq (10s + 6min)
  SPL Webviewer                             - traffic-light + prediction logic
                                            - CSV/XML logger
                                            - PNG/PDF report generator
                                            - serves dashboard + pushes live data
                                                     |
                                                     v  (browser on LAN)
                                            [ Dashboard UI ]
                                            big SPL, traffic light,
                                            prediction, history graph
```

A built-in **simulator** stands in for Smaart so the whole app can be built and demoed before touching the real system. Once we capture the real Smaart message format, the simulator gets swapped for a real Smaart adapter behind the same interface.

## Running it

```bash
./run.sh                       # or: ./.venv/bin/python -m backend.app
```
Then open http://localhost:8080/ . Ships in **simulator** mode so it runs with no
Smaart present. To point it at the real system, edit `config.json`:
`source.type` → `"smaart"`, and set `source.smaart.host`/`port` (the API port from
Smaart's Options > Preferences > API, default 26000).

## Status

- [x] Research 10EaZy + Smaart API
- [x] Full Smaart API v3 protocol in hand (SDK) — see `docs/SmaartAPI_v3_notes.md`
- [x] Backend + simulator (frames in Smaart's exact format)
- [x] Dashboard UI — big readout, traffic light, prediction, live chart
- [x] Real Smaart adapter (`backend/sources.py:SmaartSource`) — drop-in, untested against live Smaart
- [x] Continuous CSV logging + end-of-session XML summary
- [ ] **Confirm with Brian:** 6-min drives the light; real dBA limits per venue (placeholders in `config.json`)
- [ ] Test SmaartSource against the live box
- [ ] PNG/PDF end-of-event report
- [ ] Wrap as a standalone app (later)

## Layout

```
config.json            venues, limits, windows, source select
run.sh                 launcher
backend/
  app.py               aiohttp server + orchestration
  sources.py           SimulatorSource + SmaartSource (interchangeable)
  processing.py        rolling LAeq (10s/6min), traffic light, prediction
  logging_csv.py       CSV log + XML session summary
  showinfo.py          show/band/engineer lookup from Brian's Google Sheets (dashboard banner + nightly email)
web/                   dashboard (index.html, style.css, app.js)
docs/                  API notes + capture guide (capture no longer needed)
logs/                  session CSV/XML output (created at runtime)
```
