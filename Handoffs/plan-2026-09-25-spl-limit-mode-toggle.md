# Plan: FSQ SPL dashboard limit-mode toggle (90 LAeq 10s ⇄ 95 dBA-Slow)

Written 2026-09-25 for execution in a few days. Scope: the FSQ instance only (`config.json`, service `spl-monitor`, port 8090). The Memo instance (`config.memo.json`) is untouched.

## What exists today

The limit is hard-wired in `config.json`: `violations.metric = "LAeq 10s"`, `thresholdDb = 90`, and `venues["Fountain Square"].yellow/red = 80/90`. `backend/processing.py:199-201` keys the traffic light and headroom off the 10-s LAeq against `red`. `backend/violations.py` reads `metric`/`threshold` once in `__init__`.

There's already a passcode-gated runtime toggle to copy: Slack alerts (`toggle_alerts_handler`, `backend/app.py:89`; UI at `web/index.html:121` + modal at `:210`; JS at `web/app.js:612`). The passcode is `resetPasscode`, which is already `"1682"`. So the new toggle reuses that key, no new secret.

## The two modes

| Mode | Light/headroom metric | Violation metric | Red | Yellow |
|---|---|---|---|---|
| `laeq10` (default) | LAeq 10s | `LAeq 10s` | 90 | 80 |
| `aslow95` | SPL A Slow (instant) | `SPL A Slow` | 95 | 90 |

## Build steps

1. **Config.** Add to `config.json`:
   ```json
   "limitModes": {
     "laeq10": { "label": "90 dB LAeq 10s", "metric": "LAeq 10s",  "red": 90, "yellow": 80, "sustainSeconds": 0 },
     "aslow95": { "label": "95 dBA Slow",   "metric": "SPL A Slow", "red": 95, "yellow": 90, "sustainSeconds": 3 }
   },
   "limitMode": "laeq10"
   ```
2. **Processing.** In `processing.py`, `limits()` returns the active mode's yellow/red, and the light/headroom input switches: `laeq10` uses `laeq_short`, `aslow95` uses the `SPL A Slow` value from the frame (fall back to `inst` if Smaart isn't streaming it). Add `limitMode` + `limitLabel` to the broadcast state so the UI and CSV know which rule was live.
3. **Violations.** Add `ViolationTracker.set_rule(metric, threshold)` in `violations.py`. On a switch, close any open episode cleanly first (so one episode is never measured against two rules), then swap. Strikes are kept, not reset — the reset button still does that.
4. **Endpoint.** `POST /api/limit-mode` in `app.py`, body `{mode, passcode}`. Passcode required in BOTH directions (unlike Slack, where only OFF is gated). 403 on wrong code, 400 on unknown mode. Broadcast `{"type":"limitMode", ...}` to every open browser and log `[limit] mode -> aslow95` to console.
5. **Persistence + rollover.** Write the active mode and its report day to `logs/limit_mode.json` and read it on startup, so a restart mid-show keeps the mode. At the 05:00 rollover (`dailySummary.rolloverHour`), or on startup when the saved report day is stale, snap back to `laeq10` and broadcast it. (`logs/` is excluded from rsync — correct, the VM owns that file.)
6. **UI.** A second switch next to the Slack toggle in the header: "90 LAeq10s | 95 A-Slow". Flipping it opens a passcode modal cloned from `slackModal`; the switch doesn't move until the server confirms. The hero label and the limit line text read from `limitLabel`, so the screen always says which rule is live.
7. **Downstream text.** Slack alert text (`app.py:181-184`) already uses `p['metric']`/`p['threshold']` — confirm it reads right ("SPL A Slow hit 96 dBA (limit 95)"). CSV already logs `red_limit`; add a `limit_mode` column in `logging_csv.py`. Nightly email/PDF (`daily.py:260`, `report.py`): draw the threshold line at whatever `red_limit` was logged, and add "Limit rule: …" to the header. If the mode changed mid-night, list both with switch times.
8. **Tests.** Extend `backend/test_violations.py`: switch mid-episode closes it; thresholds apply per rule. Add a handler test for 403/200.

## Verify

Locally with `SPL_SOURCE=simulator` (`./run.sh`): flip both directions with a bad code (rejected, switch stays put) and 1682 (switches; a second browser tab follows via websocket). Restart the process and confirm the mode persists. Check the CSV column and run the daily PDF for today. Then deploy with the standard rsync + restart from `Code/SPL-Monitor/CLAUDE.md` — code only, `/etc/spl-monitor.env` doesn't change, so no .env rewrite is needed. Confirm on https://spl.tinydoorstudios.com.

## Decisions (locked 2026-09-25, Brian)

- Yellow in 95 mode = 90.
- Sustain in 95 mode = 3 s (per-mode `sustainSeconds`; 90 mode stays at 0). Tune in config if it's still twitchy.
- Mode snaps back to 90 LAeq 10s at the 05:00 report-day rollover.
