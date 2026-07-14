"""Continuous CSV logging plus an end-of-session XML summary.

The CSV is the minute-by-minute (or per-second) record for documentation. The
XML summary is the seed for the PNG/PDF report we add later.
"""

import csv
import datetime
import os
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET


# Full metric set logged per row (Smaart report order). Blank if a metric isn't
# in the stream. Enables the PDF report's complete Max/L10/L50/L90 stats table.
METRIC_COLS = [
    "FS Peak", "Peak C", "SPL Fast", "SPL A Fast", "SPL C Fast",
    "SPL Slow", "SPL A Slow", "SPL C Slow",
    "Leq 1", "LAeq 1", "LCeq 1", "LAeq 1s", "LAeq 3", "LAeq 6", "LAeq 10s",
    "LCeq 3", "LCeq 10s", "Leq 10s C-A",
    "Exposure O", "Exposure N",
]


class SessionLogger:
    def __init__(self, cfg, base_dir):
        lg = cfg.get("logging", {})
        self.enabled = lg.get("enabled", True)
        self.interval = lg.get("intervalSeconds", 1)
        directory = lg.get("directory", "logs")
        if not os.path.isabs(directory):
            directory = os.path.join(base_dir, directory)
        self.dir = directory

        self._last = 0.0
        self.rows = 0
        self.path_csv = None
        self.session_start = datetime.datetime.now()
        self.session_iso = self.session_start.isoformat(timespec="seconds")
        self.peak_long = None
        self.peak_inst = None
        self.peak_c = None
        self.peak_sub = None  # max 63 Hz octave 1-min Leq (for the watch period)
        self.violation_samples = 0
        self.overload_samples = 0
        self.venue = cfg.get("activeVenue")
        self.red = None
        self.yellow = None
        self._fh = None
        self._writer = None

        if self.enabled:
            self._open()

    def _open(self):
        os.makedirs(self.dir, exist_ok=True)
        ts = self.session_start.strftime("%Y%m%d_%H%M%S")
        self.path_csv = os.path.join(self.dir, f"spl_{ts}.csv")
        self._fh = open(self.path_csv, "w", newline="")
        self._writer = csv.writer(self._fh)
        self._writer.writerow(
            ["timestamp", "venue"] + METRIC_COLS
            + ["LAeq_10s_computed", "sub63_10s", "sub63_1min",
               "light", "violation", "overload", "yellow_limit", "red_limit"])
        self._fh.flush()

    def update(self, state, metrics=None):
        metrics = metrics or {}
        if not self.enabled:
            return
        # peaks / counters tracked every frame regardless of write interval
        ll = state.get("laeqLong")
        if ll is not None and (self.peak_long is None or ll > self.peak_long):
            self.peak_long = ll
        ins = state.get("instant")
        if ins is not None and (self.peak_inst is None or ins > self.peak_inst):
            self.peak_inst = ins
        pc = state.get("peakC")
        if pc is not None and (self.peak_c is None or pc > self.peak_c):
            self.peak_c = pc
        sl = state.get("subLong")
        if sl is not None and (self.peak_sub is None or sl > self.peak_sub):
            self.peak_sub = sl
        if state.get("violation"):
            self.violation_samples += 1
        if state.get("overload"):
            self.overload_samples += 1
        self.venue = state.get("venue", self.venue)
        self.red = state.get("red")
        self.yellow = state.get("yellow")

        now = state["t"]
        if now - self._last < self.interval:
            return
        self._last = now

        row = [
            state.get("timestamp") or datetime.datetime.now().isoformat(timespec="milliseconds"),
            state.get("venue"),
        ]
        row += [metrics.get(m) for m in METRIC_COLS]
        row += [
            state.get("laeqShort"),
            state.get("subShort"),
            state.get("subLong"),
            state.get("light"),
            int(bool(state.get("violation"))),
            int(bool(state.get("overload"))),
            state.get("yellow"),
            state.get("red"),
        ]
        self._writer.writerow(row)
        self._fh.flush()
        self.rows += 1

    def write_summary_xml(self):
        if not self.enabled:
            return None
        end = datetime.datetime.now()
        dur = end - self.session_start
        root = ET.Element("splSession")
        ET.SubElement(root, "venue").text = str(self.venue)
        ET.SubElement(root, "start").text = self.session_iso
        ET.SubElement(root, "end").text = end.isoformat(timespec="seconds")
        ET.SubElement(root, "durationSeconds").text = str(int(dur.total_seconds()))
        lim = ET.SubElement(root, "limits")
        ET.SubElement(lim, "yellow").text = _s(self.yellow)
        ET.SubElement(lim, "red").text = _s(self.red)
        pk = ET.SubElement(root, "peaks")
        ET.SubElement(pk, "laeq6minMax").text = _s(self.peak_long)
        ET.SubElement(pk, "instantMax").text = _s(self.peak_inst)
        ET.SubElement(pk, "peakCMax").text = _s(self.peak_c)
        ET.SubElement(pk, "sub63_1minMax").text = _s(self.peak_sub)
        ET.SubElement(root, "violationSamples").text = str(self.violation_samples)
        ET.SubElement(root, "overloadSamples").text = str(self.overload_samples)
        breached = (self.red is not None and self.peak_long is not None and self.peak_long >= self.red)
        ET.SubElement(root, "result").text = "LIMIT EXCEEDED" if breached else "WITHIN LIMIT"
        ET.SubElement(root, "csvFile").text = os.path.basename(self.path_csv) if self.path_csv else ""

        path_xml = os.path.splitext(self.path_csv)[0] + "_summary.xml" if self.path_csv else \
            os.path.join(self.dir, "session_summary.xml")
        pretty = minidom.parseString(ET.tostring(root, "utf-8")).toprettyxml(indent="  ")
        with open(path_xml, "w") as fh:
            fh.write(pretty)
        return path_xml

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None


def _s(x):
    return "" if x is None else str(x)
