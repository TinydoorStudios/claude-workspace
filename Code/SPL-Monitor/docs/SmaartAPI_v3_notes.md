# Smaart API v3 — distilled notes (what this app actually uses)

Source: `SmaartAPI.pdf` (SDK, 16-Sept-21), API v3, Smaart v8.3+. Full extracted text in `_SmaartAPI_reference.txt`.

## Transport
- Standard WebSocket (RFC6455). Requests and responses are JSON.
- Root endpoint: `ws://<ip>:<port>/api/v3/`
- The `<port>` is the API port shown in Smaart's **Options > Preferences > API** tab (default `26000`). This is the API/WebSocket port, *not* the UDP discovery port.
- Discovery (optional): UDP broadcast on port **25752** for Smaart (signature `0x656E7544`); server replies with its API port. We skip this and connect directly to a known IP:port.

## Handshake
1. Query supported versions — send anything to `ws://<ip>:<port>` root → `{"supportedApiVersions":[{"3":"/api/v3/"},...]}`.
2. Connect to `ws://<ip>:<port>/api/v3/`.
3. Server properties: `{"action":"get"}` → `applicationName`, `applicationVersion`, `authenticationRequired`, `machineName`.
4. If `authenticationRequired`: `{"action":"set","properties":[{"password":"<pw>"}]}`.

## Request / response shape
Request:
```json
{ "sequenceNumber": 42, "action": "get|set|capture|...", "target": "<string|object>", "properties": [ {"k": v} ] }
```
Response:
```json
{ "sequenceNumber": 42, "response": { ... } }     // or { "response": { "error": "<msg>" } }
```
`sequenceNumber` echoes back only if non-zero. We use it to match replies.

## Finding the SPL mic (the part we care about)
`{"action":"get","target":"activeCalibratedInputs"}` →
```json
{ "response": {
    "devices": [
      { "deviceName": "OCTA-CAPTURE",
        "activeCalibratedChannels": [
          { "channelIndex": 3, "channelName": "Mic 1",
            "alarms": [ {"level": 110, "metric": "SPL A Slow"} ],
            "streamEndpoint": "/api/v3/devices/.../channels/...",
            "logEndpointPrefix": "/api/v3/logs/..." } ] } ],
    "metrics": [ "FS Peak", "Peak C", "SPL Fast", ... ] } }
```
- An input only appears here if it is **calibrated AND actively logging** in Smaart. (Brian's existing measurement-mic setup.)
- `streamEndpoint` → instantaneous metric stream. `logEndpointPrefix` + `/<metric>` → logged series.

## SPL Metric Stream (instantaneous) — our primary feed
Open WS to `ws://<ip>:<port>{streamEndpoint}`. Server pushes (≤ **8 fps**, set via `{"action":"set","properties":[{"targetFPS":8}]}`):
```json
{
  "timestamp": "2018-04-02:T16:20:00.000-5:00",
  "deviceName": "Smaart I-O",
  "channelName": "Front Left",
  "metrics": [
    {"FS Peak": -54.41}, {"Peak C": 80.77},
    {"SPL Fast": 74.78}, {"SPL A Fast": 69.86}, {"SPL C Fast": 73.21},
    {"SPL Slow": 75.98}, {"SPL A Slow": 75.86}, {"SPL C Slow": 76.54},
    {"Leq 1": 73.2}, {"LAeq 1": 74.9}, {"LCeq 1": 74.1},
    {"Leq 10": 74.2}, {"LAeq 10": 74.9}, {"LCeq 10": 74.1}
  ]
}
```
- `metrics` is a list of single-key objects. We flatten to `{name: value}`.
- `Leq/LAeq/LCeq <n>` are **user-configurable** Leq metrics in Smaart (the `<n>` is Smaart's metric config, not guaranteed to be our 10s/6min). A 10EaZy mic, if present, contributes its configured Leq too.
- If a metric exceeds a configured **alarm** level, that metric's object also carries `"violation": true`.

## Log Metric Stream (timestamped, for our CSV/XML)
Open WS to `ws://<ip>:<port>/api/v3/logs/{device}/{channel}/{metric}`:
```json
{ "deviceName": "...", "channelName": "...", "metricName": "SPL A Slow",
  "loggedData": [ {"timestamp": "...", "value": 57.16} ] }
```
- On connect, `loggedData` may contain the backlog (multiple items).
- Items may carry `"violation": true` (over alarm) and/or `"overload": true` (input clip).
- Pushes as logged; ignores `targetFPS`.

## How this app uses it
- **Read-only.** We only `get` and subscribe to streams. We never start/stop measurements — Smaart stays the source of truth and keeps its calibration.
- We take an instantaneous A-weighted metric (default **`SPL A Fast`**) and compute our own **rolling LAeq over 10 s and 6 min** — exactly the two windows Brian wants — using true energy averaging: `Leq = 10·log10(mean(10^(L/10)))` over the window.
- We also pass through Smaart's native `LAeq <n>` if present, for an authoritative cross-check.
- Traffic light keys off the 6-min rolling LAeq vs the venue limit. Prediction projects the 6-min LAeq forward if the current 10-s level is sustained, and reports time-to-limit.

## Per-product support (appendix)
Calibrated inputs / metric streams / log streams: supported by **Smaart** and **Smaart SPL**. (Smaart Di does not expose calibrated-input metric streams.) Brian is on Smaart v8 → supported.
