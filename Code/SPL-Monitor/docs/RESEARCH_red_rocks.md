# Research: Red Rocks Amphitheatre SPL program — and what to borrow

Red Rocks (Morrison, CO; operated by Denver Arts & Venues) is the U.S. reference
case for venue SPL compliance because the program is engineered and data-driven,
not just a meter with a redline. Built over a ~4-year project starting ~2013 by
**K2 Audio** (Boulder acoustics firm — Rich Zwiebel, Ted Pyper) after residents a
mile away in Morrison complained about late-night bass through the bedrock.

## Policy & limits

| Metric | Limit | Averaging | Notes |
|---|---|---|---|
| Broadband A-weighted | 108 dBA (2015 reg) → tightened to ~105 dBA after a set hour | 1-minute average | Headline engineer-facing number |
| Leq in bands | 123 dB | 1-minute average | Per-band ceiling |
| "dB1" custom low-frequency band | 125 dB | 1-minute average | **25–80 Hz only**, applies after a designated hour — built for the bass complaints |
| Curfew | 11:45 pm weeknights / 12:30 am weekends & pre-holiday | — | $10k per half-hour past the third minute |

Numbers shifted year to year (protocols are refined annually from the logs), so
sources disagree on 105 vs 108 — both are real, at different points in the program.

Two key design choices:
- The enforcement metric is a **rolling 1-minute Leq**, not instantaneous.
- They invented a **separate low-frequency band metric (dB1) with its own limit and
  its own time-of-night tier**, because A-weighting deliberately discounts the
  sub-bass that is the actual neighbor complaint.

## System

- **QSC Q-SYS** for analysis; **Studio Six Digital** and **Brüel & Kjær** for
  calibrated capture. Permanently installed.
- Main readout **at the FOH mix position**, one reading per second, so the engineer
  gets real-time feedback and self-manages. Some sensing outside the venue.
- Enforcement is at the board (the controllable point); K2 derived FOH limits that
  *correlate* with neighborhood impact through years of data analysis.

## Process / enforcement

- Auto-emails to K2 staff + venue management whenever a threshold is exceeded.
- **Three exceedances → automatic fine** to the promoter ($10k; another $10k after
  three more).
- Curfew penalties separate.
- Protocols refined annually from accumulated per-second logs.

## Why it's considered best

1. Enforce at the point the engineer can control (FOH), with limits *derived* to map
   to off-site impact — rather than a meter at the property line nobody can act on.
2. A dedicated low-frequency band metric, because broadband dBA hides the real problem.
3. Time-of-night tiers (limits tighten late).
4. Real-time, per-second, engineer-facing display — guidance, not just a verdict.
5. Logged everything; used the data to tune the program over years.

## What to adopt in SPL-Monitor (prioritized)

1. **Time-of-night limit tiers.** Make each venue's limits a *schedule*, not one pair
   (e.g., FSQ 95 until 10pm, 90 after). Traffic light switches limits by clock.
   Highest payoff for the 3CDC outdoor venues with downtown curfews.
2. **Low-frequency "bass cop" metric (their dB1).** Second compliance track: a
   C-weighted or 25–80 Hz rolling Leq with its own limit + lamp, alongside the
   A-weighted one. Smaart already streams SPL C / LCeq, so it's nearly free. Folds
   into the "LAeq + LCeq two limits" option. This is the single smartest Red Rocks idea.
3. **Three-strikes escalation on the violation counter.** Configurable strike
   threshold (warn at 1, escalate at 3); on threshold, fire a notification via Brian's
   existing n8n (Slack/email — same path as the wind/lightning alerts). Turns the
   counter from a number into something with teeth. Directly extends the violation
   counter already on the build list (see NEXT_violations_and_limits.md).
4. **Named regulatory window.** Let a venue declare its enforcement window explicitly
   (1-min, 15-min, per ordinance) as the compliance number; keep 10-s as live feel.
5. **"Neighborhood estimate" offset.** Per-venue measured offset so the dashboard also
   shows an estimated property-line level (board − offset). Measure once with a
   handheld at the boundary. Path to real multi-point later: Smaart can expose a second
   calibrated input → show FOH + remote side by side.
6. **Treat the logs as the tuning substrate.** Per-second CSV/XML isn't just CYA — it's
   how you'd justify/adjust a limit later, the way K2 refines annually.

## Sources
- Westword — how the regulations changed: https://www.westword.com/music/heres-how-the-regulations-for-shows-at-red-rocks-changed-this-year-6280496/
- Conscious Electronic — the K2 Audio buildout: https://consciouselectronic.com/2021/06/30/red-rocks-sound-controversy/
- SVC / AVIXA — noise problems addressed by data analysis: https://www.svconline.com/products/noise-problems-red-rocks-addressed-audio-data-analysis-408905
- CPR — new noise rules (2015): https://www.cpr.org/2015/01/08/new-noise-rules-in-2015-for-red-rocks/
