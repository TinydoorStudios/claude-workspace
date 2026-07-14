# Next up: violation counter + on-screen limit verbiage

Status: **designed, not built.** Awaiting Brian's calls on the open questions below.
Deferred alongside the PNG/PDF report (also on hold).

---

## 1. Violation counter section

**Definition.** A violation = the compliance value (6-min LAeq) *entering* the red
limit. Edge-triggered event count, plus accumulated time-over. Not a per-sample tally.

**Backend (Monitor).** Per frame, integrate `dt = now - last_now`:
- rising edge (under → over red): `redEvents += 1`, start event timer, record start ts
- while over: `redTimeOverSec += dt`; track `maxLaeqDuringRed`
- falling edge: finalize event (duration, peak), set `lastViolation`
- track Smaart's own `violation` flag (its configured alarm) as a *separate* edge-counted total
- optional: same treatment for the yellow band (≥ yellow, < red) → warnings

Proposed `state.violations`:
```
{
  "redEvents": int,
  "redTimeOverSec": float,
  "inRedNow": bool,
  "currentRedDurationSec": float,
  "maxLaeqDuringRed": float | null,
  "yellowEvents": int,          # optional
  "yellowTimeSec": float,       # optional
  "smaartAlarmEvents": int,
  "lastViolation": { "start": ts, "end": ts|null, "peak": float, "durationSec": float } | null
}
```

**UI — dedicated "Violations" panel.**
- Headline count: red + loud when > 0; green "0 — clean" when 0
- Sub-stats: total time over limit (mm:ss), peak LAeq during breach, last violation
- Live "OVER for m:ss" while `inRedNow`
- Small **Reset** button
- Secondary line: "Smaart alarms: N" (only if any)

**Logging.** Enrich the XML session summary (already has `violationSamples` + `result`)
with event count and total time-over so the documentation matches the screen.

**Open questions:**
1. Count yellow excursions too, or red headline only? (rec: red headline, yellow as a secondary stat)
2. Reset behavior: manual button only, or also auto-reset on venue change? (rec: manual; tag each event with the venue/limit active at the time)
3. Also monitor a peak / LCpeak limit (some ordinances cap it separately)? We already read Peak C / SPL C, so a second violation type is cheap.

---

## 2. On-screen limit verbiage

Today the only limit text is "limit 95" on the big panel. Add:

- **Limits strip** under the big panel / in the header, plain language:
  `Compliance: 6-min rolling LAeq (A-weighted) · warn ≥ 90, limit 95 dBA`
- **Chart line labels** inline at the right end of each dashed line: "Limit 95", "Warn 90"
- **Per-venue note** field in `config.json`, rendered on screen — ordinance reference,
  measurement position, etc. e.g.:
  ```
  "Fountain Square": { "yellow": 92, "red": 98, "note": "City ordinance — measured at FOH" }
  ```

**Open questions:**
1. Want per-venue notes? Give me the wording per venue (ordinance §, mic position, …).
2. Preferred wording for the metric/compliance line.
