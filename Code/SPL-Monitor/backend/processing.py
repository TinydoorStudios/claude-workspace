"""Rolling LAeq, traffic-light state, and the predictive projection.

Everything here works in the linear energy domain and converts to dB only at the
edges. LAeq over a window is the true energy average:

    Leq = 10 * log10( mean( 10^(L/10) ) )   over the samples in the window.

We integrate an instantaneous A-weighted level (default "SPL A Fast" from Smaart)
into two time windows — 10 s and 6 min — and key the traffic light off the long
window vs the active venue's limit.
"""

import math
import time
from collections import deque

from .violations import ViolationTracker


def db_to_energy(db):
    return 10.0 ** (db / 10.0)


def energy_to_db(e):
    return 10.0 * math.log10(e) if e and e > 0 else None


class RollingLeq:
    """Energy-averaged Leq over a trailing time window (seconds)."""

    def __init__(self, window_seconds):
        self.window = float(window_seconds)
        self.samples = deque()  # (t, energy)
        self._sum = 0.0

    def add(self, t, level_db):
        e = db_to_energy(level_db)
        self.samples.append((t, e))
        self._sum += e
        self._evict(t)

    def _evict(self, now):
        cutoff = now - self.window
        s = self.samples
        while s and s[0][0] < cutoff:
            self._sum -= s.popleft()[1]
        if self._sum < 0:
            self._sum = 0.0

    def mean_energy(self):
        n = len(self.samples)
        return (self._sum / n) if n else None

    def value(self):
        return energy_to_db(self.mean_energy())

    def fill_fraction(self, now):
        if not self.samples:
            return 0.0
        span = now - self.samples[0][0]
        return max(0.0, min(1.0, span / self.window))


class Monitor:
    def __init__(self, cfg):
        w = cfg["windows"]
        self.short_secs = w["shortSeconds"]
        self.long_secs = w["longSeconds"]
        self.short = RollingLeq(self.short_secs)
        self.long = RollingLeq(self.long_secs)
        # C-weighted "bass cop" windows — mirror the A windows, fed by SPL C.
        # The rig streams native LCeq 10s but no LCeq 6, so the long C is computed.
        self.shortC = RollingLeq(self.short_secs)
        self.longC = RollingLeq(self.long_secs)
        # 63 Hz octave sub-band ("bass cop" with teeth). 10 s = live readout,
        # 1-min Leq = the LF compliance / lamp number (matches Red Rocks dB1).
        # Labels are auto-detected from the stream (anything containing "63");
        # optional manual overrides via config "subBand". Computed windows are a
        # fallback for when the rig only streams one band reading.
        self.subShort = RollingLeq(self.short_secs)
        self.subLong = RollingLeq(60)
        sub_cfg = cfg.get("subBand", {})
        self._sub_cfg_10s = sub_cfg.get("label10s")
        self._sub_cfg_1m = sub_cfg.get("label1m")
        self.sub_label_10s = None
        self.sub_label_1m = None
        self.horizon = cfg.get("prediction", {}).get("horizonSeconds", 60)
        self.instant_metric = cfg["source"]["smaart"].get("instantMetric", "SPL A Fast")
        self.compliance = cfg.get("complianceMetric", "long")
        comp = cfg.get("compliance", {})
        self.compliance_mode = comp.get("mode", "computed")   # "computed" | "native"
        self.native_long_metric = comp.get("longMetric")       # e.g. "LAeq 6"
        self.venue = cfg.get("activeVenue")
        self.venues = cfg.get("venues", {})
        self.vtracker = ViolationTracker(cfg)
        self.latest = None
        # rolling chart history so a page refresh / new client gets the full
        # graph immediately instead of an empty window that refills over long_secs
        self.history = deque()
        self._virtual_cfg = self._load_virtual(self.venue)
        self._ordinance_cfg = self._load_ordinance(self.venue)

    def _load_virtual(self, venue):
        return self.venues.get(venue, {}).get("virtualLocations", [])

    def _load_ordinance(self, venue):
        return self.venues.get(venue, {}).get("ordinance", {})

    def set_venue(self, name):
        if name in self.venues:
            self.venue = name
            self._virtual_cfg = self._load_virtual(name)
            self._ordinance_cfg = self._load_ordinance(name)
            return True
        return False

    def limits(self):
        v = self.venues.get(self.venue, {})
        return v.get("yellow"), v.get("red")

    def c_limits(self):
        """C-weighted (bass) limits. Null => WATCH mode: lamp idle, no alarm."""
        v = self.venues.get(self.venue, {})
        return v.get("cYellow"), v.get("cRed")

    def sub_limits(self):
        """63 Hz octave-band limits. Null => WATCH mode: lamp idle, no alarm."""
        v = self.venues.get(self.venue, {})
        return v.get("subYellow"), v.get("subRed")

    def _resolve_sub_labels(self, metrics):
        """Auto-detect the 63 Hz octave labels (10 s live + 1-min compliance).
        Honors config overrides; otherwise matches any streamed label containing
        "63", classing one with "10s" as the live reading and the other as the
        1-min. Re-resolves only while a slot is unset/absent so it's cheap."""
        have10 = bool(self.sub_label_10s) and self.sub_label_10s in metrics
        have1m = bool(self.sub_label_1m) and self.sub_label_1m in metrics
        if have10 and have1m:
            return
        cand = [k for k in metrics if "63" in str(k)]
        if not cand:
            return

        def is10s(k):
            return "10s" in str(k).lower().replace(" ", "")

        tens = [k for k in cand if is10s(k)]
        mins = [k for k in cand if not is10s(k)]
        if self._sub_cfg_10s and self._sub_cfg_10s in metrics:
            self.sub_label_10s = self._sub_cfg_10s
        elif tens:
            self.sub_label_10s = tens[0]
        if self._sub_cfg_1m and self._sub_cfg_1m in metrics:
            self.sub_label_1m = self._sub_cfg_1m
        elif mins:
            self.sub_label_1m = mins[0]
        # only one 63 metric streamed: drive the live readout off it, compute the 1-min
        if not self.sub_label_10s and not self.sub_label_1m:
            self.sub_label_10s = cand[0]

    def _instant(self, metrics):
        for key in (self.instant_metric, "SPL A Fast", "SPL A Slow", "SPL Slow", "SPL Fast"):
            if metrics.get(key) is not None:
                return metrics[key]
        return None

    def _instant_c(self, metrics):
        for key in ("SPL C Slow", "SPL C Fast"):
            if metrics.get(key) is not None:
                return metrics[key]
        return None

    def process(self, frame):
        now = time.time()
        metrics = frame.get("metrics", {})
        inst = self._instant(metrics)
        # the rig emits absurd negatives (e.g. -2206) during digital silence;
        # treat anything below a sane SPL floor as no-signal
        if inst is not None and inst < 0:
            inst = None
        if inst is not None:
            self.short.add(now, inst)
            self.long.add(now, inst)

        # C-weighted "bass cop" track — same digital-silence guard as the A path
        inst_c = self._instant_c(metrics)
        if inst_c is not None and inst_c < 0:
            inst_c = None
        if inst_c is not None:
            self.shortC.add(now, inst_c)
            self.longC.add(now, inst_c)

        laeq_short = self.short.value()
        computed_long = self.long.value()
        native_long = metrics.get(self.native_long_metric) if self.native_long_metric else None
        use_native = self.compliance_mode == "native" and native_long is not None
        laeq_long = native_long if use_native else computed_long

        yellow, red = self.limits()
        # Traffic light and headroom key off the 10-s LAeq (the hero metric)
        light = self._light(laeq_short, yellow, red)
        pred = self._predict(laeq_long, laeq_short, red)

        # C-weighted "bass cop": live = native LCeq 10s (fallback computed), the
        # 6-min C is computed (no native LCeq 6). Lamp keys off the 10-s LCeq.
        # With cRed null the lamp stays idle (WATCH mode) — display, no alarm.
        cyellow, cred = self.c_limits()
        native_short_c = metrics.get("LCeq 10s")
        laeq_short_c = native_short_c if native_short_c is not None else self.shortC.value()
        laeq_long_c = self.longC.value()
        light_c = self._light(laeq_short_c, cyellow, cred)
        # spectral tilt (C minus A) is the bass-content tell: native 10-s value if
        # the rig streams it, else derived from the two 10-s readings.
        ca_tilt = metrics.get("Leq 10s C-A")
        if ca_tilt is None and laeq_short_c is not None and laeq_short is not None:
            ca_tilt = laeq_short_c - laeq_short

        # 63 Hz octave sub-band — auto-detected from the stream. Native 10 s = live,
        # native 1-min = compliance number; computed windows backfill a missing one.
        # Same digital-silence guard (rig emits absurd negatives during silence).
        self._resolve_sub_labels(metrics)
        sub_native_short = metrics.get(self.sub_label_10s) if self.sub_label_10s else None
        sub_native_long = metrics.get(self.sub_label_1m) if self.sub_label_1m else None
        if sub_native_short is not None and sub_native_short < 0:
            sub_native_short = None
        if sub_native_long is not None and sub_native_long < 0:
            sub_native_long = None
        if sub_native_short is not None:
            self.subShort.add(now, sub_native_short)
            self.subLong.add(now, sub_native_short)
        sub_short_val = sub_native_short if sub_native_short is not None else self.subShort.value()
        sub_long_val = sub_native_long if sub_native_long is not None else self.subLong.value()
        subyellow, subred = self.sub_limits()
        # lamp keys off the 1-min Leq (LF compliance window); null subRed => WATCH
        sub_light = self._light(sub_long_val, subyellow, subred)
        sub_long_fill = 1.0 if sub_native_long is not None else round(self.subLong.fill_fraction(now), 3)

        native = {k: v for k, v in metrics.items()
                  if k.startswith("LAeq") or k.startswith("LCeq") or k.startswith("Leq")}

        lceq10s = metrics.get("LCeq 10s")
        virtual = self._compute_virtual(laeq_short, lceq10s, inst, yellow, red)
        all_metrics = {k: _r(v) if isinstance(v, float) else v
                       for k, v in sorted(metrics.items())}

        headroom = None
        if laeq_short is not None and red is not None:
            headroom = round(red - laeq_short, 1)

        state = {
            "t": now,
            "timestamp": frame.get("timestamp"),
            "deviceName": frame.get("deviceName"),
            "channelName": frame.get("channelName"),
            "venue": self.venue,
            "yellow": yellow,
            "red": red,
            "instant": _r(inst),
            "instantMetric": self.instant_metric,
            "laeqShort": _r(laeq_short),
            "laeqLong": _r(laeq_long),
            "shortSecs": self.short_secs,
            "longSecs": self.long_secs,
            "headroom": headroom,
            "light": light,
            "longFill": 1.0 if use_native else round(self.long.fill_fraction(now), 3),
            "complianceMetric": self.native_long_metric if use_native else "computed 6-min",
            "lightMetric": "LAeq 10s",
            "prediction": pred,
            "peakC": metrics.get("Peak C"),
            "splCSlow": metrics.get("SPL C Slow"),
            # --- C-weighted bass-cop track ---
            "instantC": _r(inst_c),
            "laeqShortC": _r(laeq_short_c),
            "laeqLongC": _r(laeq_long_c),
            "cYellow": cyellow,
            "cRed": cred,
            "lightC": light_c,
            "cArmed": cred is not None,
            "caTilt": _r(ca_tilt),
            "longCFill": round(self.longC.fill_fraction(now), 3),
            # --- 63 Hz octave sub-band ("bass cop" with teeth) ---
            "subShort": _r(sub_short_val),
            "subLong": _r(sub_long_val),
            "subYellow": subyellow,
            "subRed": subred,
            "subLight": sub_light,
            "subArmed": subred is not None,
            "subLongFill": sub_long_fill,
            "subBandLabel": self.sub_label_1m or self.sub_label_10s,
            "subBand10sLabel": self.sub_label_10s,
            "subBand1mLabel": self.sub_label_1m,
            "native": native,
            "violation": bool(frame.get("violation")),
            "overload": bool(frame.get("overload")),
            "allMetrics": all_metrics,
            "virtualLocations": virtual,
            "soundOrdinance": self._compute_ordinance(laeq_long),
        }
        # Feed the violation tracker. If its trigger metric (e.g. "LAeq 10s") is
        # not in the native stream, fall back to our computed 10-second LAeq so it
        # still works; a native Smaart "LAeq 10s" metric overrides it automatically.
        vmetrics = dict(metrics)
        if laeq_short is not None:
            vmetrics.setdefault(self.vtracker.metric, laeq_short)
        state["violations"] = self.vtracker.process(vmetrics)
        self.latest = state

        # keep a rolling buffer matching the client chart window so refreshes
        # and new clients can be backfilled
        self.history.append({"t": now, "inst": _r(inst), "long": _r(laeq_long)})
        cutoff = now - self.long_secs
        while self.history and self.history[0]["t"] < cutoff:
            self.history.popleft()

        return state

    def history_points(self):
        """Snapshot of the rolling chart buffer for backfilling a client."""
        return list(self.history)

    def _compute_ordinance(self, laeq_long):
        cfg = self._ordinance_cfg
        locs = cfg.get("locations", [])
        if not locs:
            return {}
        limit = cfg.get("limit", 75)
        yellow = cfg.get("yellow", 70)
        offset_map = {loc["name"]: loc["offsetA"] for loc in self._virtual_cfg}
        cards = []
        for name in locs:
            if name == "FOH":
                val = _r(laeq_long) if laeq_long is not None else None
            else:
                oa = offset_map.get(name)
                val = _r(laeq_long + oa) if (laeq_long is not None and oa is not None) else None
            cards.append({
                "name": name,
                "laeq6": val,
                "light": self._light(val, yellow, limit),
                "virtual": name != "FOH",
                "limit": limit,
            })
        return {
            "currentLimit": limit,
            "note": cfg.get("note", ""),
            "cards": cards,
        }

    def _compute_virtual(self, laeq_short, lceq10s, inst, yellow, red):
        out = []
        for loc in self._virtual_cfg:
            oa, oc = loc["offsetA"], loc["offsetC"]
            va = _r(laeq_short + oa) if laeq_short is not None else None
            vc = _r(lceq10s + oc) if lceq10s is not None else None
            vi = _r(inst + oa) if inst is not None else None
            ca = _r(vc - va) if (vc is not None and va is not None) else None
            out.append({
                "name": loc["name"],
                "offsetA": oa,
                "offsetC": oc,
                "laeq10s": va,
                "lceq10s": vc,
                "instant": vi,
                "ca": ca,
                "light": self._light(va, yellow, red),
            })
        return out

    @staticmethod
    def _light(value, yellow, red):
        if value is None or red is None:
            return "idle"
        if value >= red:
            return "red"
        if yellow is not None and value >= yellow:
            return "yellow"
        return "green"

    def _predict(self, long_db, short_db, red):
        """Project the long-window LAeq if the current short level is sustained, and
        estimate seconds until it reaches the red limit. Works for both native and
        computed compliance values (operates in the energy domain on the dB inputs)."""
        out = {"projected": None, "timeToLimitSeconds": None, "horizonSeconds": self.horizon}
        if long_db is None or short_db is None:
            return out

        m_long = db_to_energy(long_db)
        e_now = db_to_energy(short_db)
        W = float(self.long_secs)
        H = min(float(self.horizon), W)
        proj_e = ((W - H) * m_long + H * e_now) / W
        out["projected"] = _r(energy_to_db(proj_e))

        if red is not None:
            e_lim = db_to_energy(red)
            if long_db >= red:
                out["timeToLimitSeconds"] = 0
            elif e_now > m_long:  # only rising levels can reach the limit
                tau = W * (e_lim - m_long) / (e_now - m_long)
                if 0 < tau <= W:
                    out["timeToLimitSeconds"] = round(tau)
        return out


def _r(x, n=1):
    return round(x, n) if isinstance(x, (int, float)) else None
