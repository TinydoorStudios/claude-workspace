# SPL Monitor — Session 3 Handoff
*2026-06-06 · ~10:30 PM EDT*

---

## What This Is

Third session on the SPL Monitor project. Started from a working deployed dashboard and added features, fixed bugs, and compacted the layout. Ended with the system running in Smaart mode (restored after simulator test).

---

## Current State

**Live URL:** https://spl.tinydoorstudios.com  
**Pi:** 192.168.0.2 · service: `spl-monitor` · port: 8090  
**Source:** `SPL_SOURCE=smaart` (restored at session end — Smaart is off overnight, standby screen will show)  
**Code:** `/Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/` (Mac = source of truth)  
**Asset version:** v=15  

---

## What Was Built This Session

### 1. Tiles Row Overhaul
- Removed redundant "Headroom to red" tile (headroom LED bar in hero already shows it)
- Prediction moved to slot 3
- **Prediction display fixed:** the null TTL case was showing an em-dash that read as a slash. Replaced with:
  - `↓ stable` (dim) — level not trending toward limit
  - `↑ limit in MM:SS` — counting down, turns yellow <3 min, red <1 min
  - `OVER LIMIT` (red) — at or past 6-min compliance limit
- **Davidson C-A tile added (slot 4):** LCeq 10s − LAeq 10s at The Davidson virtual position. Shows sub content reaching that building. Updates live from virtual location data.

### 2. Backend: C-A field on virtual locations
`processing.py` `_compute_virtual()` now computes `ca = lceq10s_virtual − laeq10s_virtual` for every virtual location and includes it in the state payload. Davidson's offsets are −3.62A / −2.49C, so Davidson C-A = FOH C-A + 1.13 dB.

### 3. Layout Compaction
Everything now fits on one screen without scrolling. Key reductions:
- `main` gap: 14px → 8px, padding: 16px → 10px/14px
- Hero: bigpanel padding tightened, `#bigVal` 82px → 64px, lamps 40px → 30px, hbar-meter height 44px → 32px, hbar-num 28px → 22px
- Violations row: padding tightened, viol-n 46px → 34px
- Tiles: font-size 38px → 30px, padding and gaps reduced
- All Metrics: padding tightened
- Virtual cards: vc-val 28px → 22px, all padding and margins reduced, minmax 160px → 140px
- Ordinance cards: orc-val 34px → 26px, padding reduced
- Chart: min-height 220px → 140px

### 4. Bug Fixed: Pi .env SPL_PORT dropout
When rewriting the Pi `.env`, `SPL_PORT=8090` was accidentally dropped. The Cloudflare tunnel routes `spl.tinydoorstudios.com` to port 8090 — the config.json default is 8080. Dropping the var caused a 502 on the public URL. Fixed. Standing instruction added to `~/.claude/CLAUDE.md`.

### 5. /reflect Skill Created
New personal skill at `~/.claude/skills/reflect/SKILL.md`. Invoked as `/reflect` at end of sessions to extract durable knowledge into CLAUDE.md and memory.md.

---

## Pi .env — Full Required Set
```
SPL_SOURCE=smaart
SMAART_HOST=192.24.143.121
SMAART_PORT=26000
SPL_PORT=8090
SPL_ALERT_WEBHOOK=http://localhost:5678/webhook/spl-violation
```
Never write partial. `SPL_PORT=8090` is the one that breaks things if dropped.

To test with generated data: set `SPL_SOURCE=simulator`, restart, test, restore `SPL_SOURCE=smaart`.

---

## Deploy Command
```bash
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  -e "ssh -i ~/.ssh/spl_deploy" \
  /Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/ \
  brian@192.168.0.2:/home/brian/spl-monitor/ \
  && ssh -i ~/.ssh/spl_deploy brian@192.168.0.2 'sudo systemctl restart spl-monitor'
```

---

## Key Files
```
SPL-Monitor/
  backend/
    app.py          — aiohttp server, WebSocket hub, API endpoints
    processing.py   — rolling LAeq, traffic light, virtual locations, prediction, C-A
    violations.py   — strike counter / violation state machine
    logging_csv.py  — CSV logging (METRIC_COLS has all 20 Smaart metrics)
    sources/        — Smaart WebSocket adapter + simulator
  web/
    index.html      — page structure (v=15)
    app.js          — WebSocket client, all render functions (v=15)
    style.css       — all styling (v=15)
  config.json       — venue config, limits, ordinance, virtual location offsets
```

---

## Current Dashboard Layout (top to bottom, all visible on one screen)

1. **Header bar** — venue selector, source ID, connection status, clock
2. **Hero panel** — 10s LAeq big number + headroom LED bar (same row) + traffic light
3. **Violations row** — strike count, status, total time over, last violation, reset button (passcode: 2578)
4. **Tiles row** — Instant dBA Slow · 6-min LAeq (compliance) · Prediction (60s) · Davidson C-A 10s
5. **All Metrics strip** — all 20 raw Smaart values
6. **Virtual Measurement Positions** — 8 cards (Front of Stage → Westin Hotel) with LAeq 10s, LCeq 10s, offsets
7. **Sound Ordinance** — FOH + Westin + Davidson + Jeff Ruby's (LAeq 6-min, 75 dBA limit)
8. **Chart** — 6-min LAeq + instant over rolling window

---

## Smaart Metrics in Use
Native metrics pulled from stream: SPL A Slow (instant), LAeq 6 (compliance), LAeq 10s (violation trigger + hero), LCeq 10s (virtual C weighting), Leq 10s C-A (logged). Full 20-metric list in `logging_csv.py` METRIC_COLS.

---

## Next Session Candidates
- **Cloudflare Access policy** — gate spl.tinydoorstudios.com to Brian's login only
- **PM2 update** — v6.0.13 in memory vs v7.0.1 installed (maintenance window)
- **Pi NVMe migration** — 1TB NVMe installed, unused
- **Verify live data** — confirm all metrics populate when rig is on at Fountain Square

---

## Behavior Change Logged This Session
Brian's preference added to both CLAUDE.md files: **don't narrate work**. Execute, report when done. No play-by-play. Still ask questions when needed.
