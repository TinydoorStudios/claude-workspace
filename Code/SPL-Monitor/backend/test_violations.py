"""Deterministic checks for the violation state machine. Run:
    ./.venv/bin/python -m backend.test_violations
"""
from backend.violations import ViolationTracker

CFG = {"violations": {"metric": "L", "thresholdDb": 90, "sustainSeconds": 10,
                      "alertFromViolation": 4, "longViolationSeconds": 60,
                      "sessionGapSeconds": 300}}


def run():
    t = ViolationTracker(CFG)
    alerts = []
    clock = {"now": 1000.0}

    def feed(level, dt=1.0):
        clock["now"] += dt
        t.process({"L": level}, now=clock["now"])
        alerts.extend(t.take_alerts())

    def violation(secs):
        for _ in range(secs):
            feed(95)
        feed(80)  # drop below threshold -> clears

    # 1) brief spike under 10s does NOT count
    for _ in range(5):
        feed(95)
    feed(80)
    assert t.count == 0, f"brief spike counted: {t.count}"

    # 2) three full violations -> count 3, no alerts
    for _ in range(3):
        violation(12)
    assert t.count == 3, f"count after 3: {t.count}"
    assert alerts == [], f"unexpected alerts in first 3: {alerts}"

    # 3) fourth violation -> strike alert
    violation(12)
    assert t.count == 4
    strikes = [a for a in alerts if a["kind"] == "strike"]
    assert len(strikes) == 1 and strikes[0]["violationNumber"] == 4, strikes

    # 4) fifth violation lasting 75s -> strike (#5) + long alert
    alerts.clear()
    violation(75)
    assert t.count == 5
    assert sorted(a["kind"] for a in alerts) == ["long", "strike"], alerts
    longa = [a for a in alerts if a["kind"] == "long"][0]
    assert longa["elapsedSec"] >= 60

    # 5) session auto-reset after a long data gap
    feed(80, dt=400)
    assert t.count == 0, f"session not reset after gap: {t.count}"

    print("ALL VIOLATION TESTS PASSED")
    print("  sample strike alert:", strikes[0])
    print("  sample long alert:  ", longa)


def run_sustain0():
    """10s-average mode: the metric is already a 10-second average, so a single
    frame at/over the threshold is a violation immediately (sustainSeconds=0)."""
    cfg = {"violations": {"metric": "M", "thresholdDb": 90, "sustainSeconds": 0,
                          "alertFromViolation": 3, "longViolationSeconds": 60,
                          "sessionGapSeconds": 300}}
    t = ViolationTracker(cfg)
    now = [0.0]

    def feed(level, dt=3.0):
        now[0] += dt
        t.process({"M": level}, now=now[0])
        return t.take_alerts()

    feed(91)                       # 10s avg over 90 -> instant violation
    assert t.count == 1, f"immediate trigger failed: {t.count}"
    feed(85)                       # back under 90 -> clears
    assert t.count == 1 and t.active is None
    print("SUSTAIN-0 (10s-average mode) OK")


def run_set_rule():
    """Limit-mode switch: an open episode closes on the swap (never judged
    against two rules), strikes are kept, and the new rule's sustain applies."""
    cfg = {"violations": {"metric": "LAeq 10s", "thresholdDb": 90, "sustainSeconds": 0,
                          "alertFromViolation": 3, "longViolationSeconds": 60,
                          "sessionGapSeconds": 300}}
    t = ViolationTracker(cfg)
    now = [0.0]

    def feed(metrics, dt=1.0):
        now[0] += dt
        t.process(metrics, now=now[0])

    feed({"LAeq 10s": 92})
    assert t.count == 1 and t.active is not None
    t.set_rule("SPL A Slow", 95, 3, now=now[0] + 1)
    assert t.active is None and len(t.take_completed()) == 1, "switch must close the episode"
    assert t.count == 1, "strikes kept across a switch"
    feed({"LAeq 10s": 99, "SPL A Slow": 94})      # old metric ignored, under 95
    assert t.active is None
    feed({"SPL A Slow": 96}); feed({"SPL A Slow": 97})
    assert t.count == 1, "2 s over must not count with 3 s sustain"
    feed({"SPL A Slow": 96}); feed({"SPL A Slow": 96})
    assert t.count == 2, f"3 s over should count: {t.count}"
    print("SET_RULE (limit-mode switch) OK")


def run_monitor_modes():
    """Monitor-level: modes drive light/headroom/red and fall back cleanly."""
    import json, pathlib
    from backend.processing import Monitor
    cfg = json.loads((pathlib.Path(__file__).resolve().parent.parent / "config.json").read_text())
    m = Monitor(cfg)
    assert m.limit_mode == "laeq10" and m.limits() == (80, 90)
    assert m.vtracker.metric == "LAeq 10s" and m.vtracker.threshold == 90
    assert m.set_limit_mode("aslow95") and m.limits() == (90, 95)
    assert m.vtracker.metric == "SPL A Slow" and m.vtracker.sustain == 3
    st = m.process({"metrics": {"SPL A Slow": 93.0, "SPL A Fast": 93.0, "LAeq 10s": 91.0}})
    assert st["lightMetric"] == "SPL A Slow" and st["headroom"] == 2.0 and st["light"] == "yellow", st["light"]
    assert not m.set_limit_mode("bogus")
    del cfg["limitModes"]
    legacy = Monitor(cfg)
    assert legacy.limit_mode is None and legacy.light_metric() == "LAeq 10s"
    print("MONITOR limit modes OK")


if __name__ == "__main__":
    run()
    run_sustain0()
    run_set_rule()
    run_monitor_modes()
