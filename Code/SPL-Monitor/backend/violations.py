"""SPL violation tracking — the 3-strikes engine.

Rule (configurable in config.json -> "violations"):
  - A violation begins when the trigger metric (default "SPL A Slow") stays at or
    above the threshold (default 90 dBA) for `sustainSeconds` (default 10) of
    continuous time. A dip below the threshold before that resets the clock.
  - The violation ends when the level drops below the threshold. Duration + peak
    are recorded and the strike counter increments.
  - Strikes 1..strikesBeforeAlert are silent. Every violation AFTER that fires a
    "strike" alert at the moment it is confirmed (the sustain mark).
  - Any confirmed violation that runs past `longViolationSeconds` (default 60s)
    fires a "long" alert once, regardless of strike number.
  - The session counter auto-resets when data resumes after a gap longer than
    `sessionGapSeconds` (so each show/event starts at zero). Manual reset too.

The tracker is pure/synchronous and just queues alert payloads; the app layer
drains them with take_alerts() and sends them to the webhook.
"""

import time


class ViolationTracker:
    def __init__(self, cfg):
        v = (cfg or {}).get("violations", {})
        self.metric = v.get("metric", "SPL A Slow")
        self.threshold = v.get("thresholdDb", 90)
        self.sustain = v.get("sustainSeconds", 10)
        # alert on this violation number and every one after (e.g. 3 -> 3,4,5,...)
        self.alert_from = v.get("alertFromViolation", v.get("strikesBeforeAlert", 3))
        self.long_seconds = v.get("longViolationSeconds", 60)
        self.session_gap = v.get("sessionGapSeconds", 300)
        self._pending = []
        self._completed = []
        self.reset()

    def reset(self):
        self.count = 0
        self.active = None            # current above-threshold episode
        self.total_time_over = 0.0
        self.last_violation = None    # last completed violation summary
        self.history = []
        self.last_frame_ts = None
        self.session_start = time.time()

    # -- main entry: feed one frame's metrics -----------------------------
    def process(self, metrics, now=None):
        now = time.time() if now is None else now

        # new session if data resumed after a long gap
        if self.last_frame_ts is not None and (now - self.last_frame_ts) > self.session_gap:
            self.reset()
        self.last_frame_ts = now

        level = metrics.get(self.metric)
        if level is None:
            return self.state(now)

        if level >= self.threshold:
            if self.active is None:
                self.active = {
                    "start": now, "confirmed": False, "number": None,
                    "peak": level, "alerted_strike": False, "alerted_long": False,
                }
            ep = self.active
            if level > ep["peak"]:
                ep["peak"] = level
            elapsed = now - ep["start"]

            if not ep["confirmed"] and elapsed >= self.sustain:
                ep["confirmed"] = True
                self.count += 1
                ep["number"] = self.count
                if self.count >= self.alert_from:
                    ep["alerted_strike"] = True
                    self._queue("strike", ep, level, elapsed)

            if ep["confirmed"] and not ep["alerted_long"] and elapsed >= self.long_seconds:
                ep["alerted_long"] = True
                self._queue("long", ep, level, elapsed)
        else:
            # dropped below threshold — close any episode
            if self.active is not None:
                ep = self.active
                if ep["confirmed"]:
                    dur = now - ep["start"]
                    self.total_time_over += dur
                    rec = {
                        "number": ep["number"],
                        "start": ep["start"], "end": now,
                        "durationSec": round(dur, 1), "peak": round(ep["peak"], 1),
                    }
                    self.last_violation = rec
                    self.history.append(rec)
                    self._completed.append(rec)
                self.active = None

        return self.state(now)

    def _queue(self, kind, ep, level, elapsed):
        self._pending.append({
            "kind": kind,                      # "strike" | "long"
            "violationNumber": ep["number"],
            "count": self.count,
            "level": round(level, 1),
            "threshold": self.threshold,
            "metric": self.metric,
            "elapsedSec": round(elapsed),
            "peak": round(ep["peak"], 1),
        })

    def take_alerts(self):
        a = self._pending
        self._pending = []
        return a

    def take_completed(self):
        c = self._completed
        self._completed = []
        return c

    def state(self, now=None):
        now = time.time() if now is None else now
        ep = self.active
        cur = (now - ep["start"]) if (ep and ep["confirmed"]) else 0.0
        return {
            "count": self.count,
            "inViolation": bool(ep and ep["confirmed"]),
            "currentDurationSec": round(cur, 1),
            "totalTimeOverSec": round(self.total_time_over, 1),
            "lastViolation": self.last_violation,
            "metric": self.metric,
            "threshold": self.threshold,
            "sustainSeconds": self.sustain,
            "alertFromViolation": self.alert_from,
            "longSeconds": self.long_seconds,
        }
