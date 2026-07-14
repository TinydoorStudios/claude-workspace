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


if __name__ == "__main__":
    run()
    run_sustain0()
