"""Nightly roll-up: accumulate the night's max levels (per venue, with the time
each peak occurred) and every violation (with time, duration, peak), persisted to
disk so a restart never loses the night. Exposed via /api/daily for the n8n
nightly email.

A "report day" starts at `rolloverHour` local (default 5am), so an evening event
that runs past midnight still belongs to the same night's report.
"""

import base64
import csv
import datetime
import glob
import io
import json
import os


def _now():
    return datetime.datetime.now().astimezone()


def _parse_iso(ts):
    try:
        return datetime.datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _fmt_dur(secs):
    if secs is None:
        return "—"
    secs = int(round(secs))
    m, s = divmod(secs, 60)
    return f"{m}:{s:02d}" if m else f"{s}s"


def _fmt_time(iso):
    dt = _parse_iso(iso) if iso else None
    return dt.strftime("%-I:%M:%S %p") if dt else "—"


def _fmt_full(iso):
    dt = _parse_iso(iso) if iso else None
    return dt.strftime("%Y/%m/%d %H:%M:%S") if dt else ""


def _iso(dt):
    return dt.isoformat(timespec="seconds")


class DailySummary:
    def __init__(self, cfg, base_dir):
        d = cfg.get("dailySummary", {})
        self.rollover_hour = d.get("rolloverHour", 5)
        directory = cfg.get("logging", {}).get("directory", "logs")
        if not os.path.isabs(directory):
            directory = os.path.join(base_dir, directory)
        self.dir = directory
        os.makedirs(self.dir, exist_ok=True)
        self.current = None
        self._last_save = 0.0

    # -- report-day helpers ----------------------------------------------
    def report_day(self, dt=None):
        dt = dt or _now()
        if dt.hour < self.rollover_hour:
            dt = dt - datetime.timedelta(days=1)
        return dt.strftime("%Y-%m-%d")

    def _path(self, day):
        return os.path.join(self.dir, f"daily_{day}.json")

    def _new(self, day):
        return {"day": day, "rolloverHour": self.rollover_hour,
                "venues": {}, "violations": []}

    def _ensure(self, day):
        if self.current is None or self.current.get("day") != day:
            p = self._path(day)
            if os.path.exists(p):
                try:
                    self.current = json.loads(open(p).read())
                except (ValueError, OSError):
                    self.current = self._new(day)
            else:
                self.current = self._new(day)
        return self.current

    # -- accumulate ------------------------------------------------------
    def update(self, state):
        now = _now()
        rec = self._ensure(self.report_day(now))
        venue = state.get("venue") or "Unknown"
        v = rec["venues"].get(venue)
        if v is None:
            v = {"maxInstant": None, "maxInstantAt": None,
                 "maxLAeq10s": None, "maxLAeq10sAt": None,
                 "maxLAeq6": None, "maxLAeq6At": None,
                 "maxLCeq6": None, "maxLCeq6At": None,
                 "maxPeakC": None, "maxPeakCAt": None,
                 "redLimit": state.get("red"), "yellowLimit": state.get("yellow"),
                 "firstSeen": _iso(now), "lastSeen": None, "samples": 0}
            rec["venues"][venue] = v
        ts = _iso(now)
        v["lastSeen"] = ts
        v["samples"] += 1
        if state.get("red") is not None:
            v["redLimit"] = state.get("red")
        if state.get("yellow") is not None:
            v["yellowLimit"] = state.get("yellow")
        self._bump(v, "maxInstant", state.get("instant"), ts)
        self._bump(v, "maxLAeq10s", state.get("laeqShort"), ts)
        self._bump(v, "maxLAeq6", state.get("laeqLong"), ts)
        self._bump(v, "maxLCeq6", state.get("laeqLongC"), ts)
        self._bump(v, "maxPeakC", state.get("peakC"), ts)
        self._save_throttled(now.timestamp())

    @staticmethod
    def _bump(v, key, val, ts):
        if val is None:
            return
        if v[key] is None or val > v[key]:
            v[key] = round(val, 1)
            v[key + "At"] = ts

    def record_violation(self, venue, cv):
        rec = self._ensure(self.report_day())

        def iso_ts(t):
            return _iso(datetime.datetime.fromtimestamp(t).astimezone()) if t else None

        rec["violations"].append({
            "venue": venue,
            "start": iso_ts(cv.get("start")),
            "end": iso_ts(cv.get("end")),
            "durationSec": cv.get("durationSec"),
            "peak": cv.get("peak"),
        })
        self._save(rec)

    # -- output ----------------------------------------------------------
    def summary(self, day=None):
        day = day or self.report_day()
        if self.current is not None and self.current.get("day") == day:
            rec = self.current
        else:
            p = self._path(day)
            rec = json.loads(open(p).read()) if os.path.exists(p) else self._new(day)
        out = json.loads(json.dumps(rec))  # deep copy
        out["violationCount"] = len(rec["violations"])
        out["result"] = "VIOLATIONS RECORDED" if rec["violations"] else "NO VIOLATIONS"
        out["generatedAt"] = _iso(_now())
        return out

    # -- report window + merged CSV --------------------------------------
    def report_window(self, day):
        d = datetime.datetime.strptime(day, "%Y-%m-%d")
        start = d.replace(hour=self.rollover_hour, minute=0, second=0, microsecond=0)
        return start, start + datetime.timedelta(days=1)

    def daily_csv(self, day=None):
        """Merge the night's per-session CSV logs into one, filtered to the report window."""
        day = day or self.report_day()
        start, end = self.report_window(day)
        header = None
        rows = []
        for f in sorted(glob.glob(os.path.join(self.dir, "spl_2*.csv"))):
            try:
                with open(f, newline="") as fh:
                    r = csv.reader(fh)
                    h = next(r, None)
                    if not h:
                        continue
                    header = header or h
                    for row in r:
                        if not row:
                            continue
                        dt = _parse_iso(row[0])
                        if dt is None:
                            continue
                        if start <= dt.replace(tzinfo=None) < end:
                            rows.append(row)
            except OSError:
                continue
        rows.sort(key=lambda x: x[0])
        out = io.StringIO()
        w = csv.writer(out)
        if header:
            w.writerow(header)
        w.writerows(rows)
        return out.getvalue()

    def email_payload(self, day=None, show_info=None):
        day = day or self.report_day()
        s = self.summary(day)
        csv_text = self.daily_csv(day)
        show_info = show_info or {}
        show_label = f" — {show_info['show']}" if show_info.get("show") else ""
        if s["violationCount"]:
            subject = f"SPL Nightly Summary — {day}{show_label} — {s['violationCount']} violation(s)"
        else:
            subject = f"SPL Nightly Summary — {day}{show_label} — no violations"
        payload = {
            "date": day,
            "subject": subject,
            "html": self._html(s, show_info),
            "show": show_info.get("show"),
            "band": show_info.get("band"),
            "engineer": show_info.get("engineer"),
            "engineerCode": show_info.get("engineerCode"),
            "csvFilename": f"spl_night_{day}.csv",
            "csvBase64": base64.b64encode(csv_text.encode()).decode(),
        }
        pdf = self._build_pdf(s, csv_text, day)
        if pdf:
            payload["pdfFilename"] = f"SPL_Report_{day}.pdf"
            payload["pdfBase64"] = base64.b64encode(pdf).decode()
        return payload

    def _build_pdf(self, s, csv_text, day):
        try:
            from .report import (build_minimal_report_pdf, build_report_pdf,
                                  load_series_from_csv)
        except Exception as e:  # noqa: BLE001
            print(f"[report] plotting libs unavailable: {e!r}")
            return None
        try:
            times, cols = load_series_from_csv(csv_text)
            viols = []
            for v in s.get("violations", []):
                st, en = _parse_iso(v.get("start")), _parse_iso(v.get("end"))
                if st and en:
                    viols.append({"start": st.replace(tzinfo=None), "end": en.replace(tzinfo=None),
                                  "durationSec": v.get("durationSec"), "peak": v.get("peak")})
            venue = next(iter(s.get("venues", {})), "")
            vinfo = s.get("venues", {}).get(venue, {})
            meta = {"venue": venue, "date": day, "device": "DiGiCo UB MADI ASIO", "channel": "SPL",
                    "company": "3CDC", "start": _fmt_full(vinfo.get("firstSeen")),
                    "end": _fmt_full(vinfo.get("lastSeen")), "calibration": "",
                    "samples": vinfo.get("samples", "")}
            # No per-second data this report day (e.g. no show ran): still emit a
            # one-page PDF so the nightly email always has its attachment.
            if not times:
                return build_minimal_report_pdf(
                    meta, viols, "No SPL logging was recorded for this report day.")
            laeq10 = cols.get("LAeq 10s")
            if not laeq10 or all(v is None for v in laeq10):
                laeq10 = cols.get("LAeq_10s_computed")
            order = ["Peak C", "SPL Fast", "SPL A Fast", "SPL C Fast", "SPL Slow",
                     "SPL A Slow", "SPL C Slow", "Leq 1", "LAeq 1", "LCeq 1",
                     "LAeq 1s", "LAeq 3", "LAeq 6", "LAeq 10s",
                     "LCeq 3", "LCeq 10s", "Leq 10s C-A", "FS Peak"]
            resolved = {"LAeq 10s": laeq10}
            series = {}
            for m in order:
                src = resolved.get(m, cols.get(m))
                if src and any(v is not None for v in src):
                    series[m] = src
            red = vinfo.get("redLimit") or 90
            return build_report_pdf(meta, times, series, viols, {"LAeq 10s": red, "LAeq 6": red})
        except Exception as e:  # noqa: BLE001
            print(f"[report] pdf build failed: {e!r}")
            return None

    @staticmethod
    def _html(s, show_info=None):
        venues = s.get("venues", {})
        viols = s.get("violations", [])
        accent = "#9B2222" if viols else "#1f7a44"
        p = [("<div style='font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;max-width:680px'>"
              "<h2 style='margin:0 0 2px'>SPL Nightly Summary</h2>"
              f"<div style='color:#666;margin-bottom:14px'>{s.get('day')} &middot; "
              f"<span style='color:{accent};font-weight:700'>{s.get('result')}</span></div>")]

        show_info = show_info or {}
        if show_info.get("show") or show_info.get("engineer"):
            location = next(iter(venues), None) or "Fountain Square"
            p.append(
                "<div style='background:#eef2f7;border:1px solid #cdd6e2;border-radius:8px;"
                "padding:10px 14px;margin-bottom:14px;font-size:14px'>"
                f"<div><b>Show:</b> {show_info.get('show') or '—'}</div>"
                f"<div><b>Location:</b> {location}</div>"
                f"<div><b>Engineer:</b> {show_info.get('engineer') or '—'}</div>"
                "</div>")

        def lvl(label, val, at, lim=None, unit="dBA"):
            if val is None:
                return ""
            limtxt = f" <span style='color:#999'>(limit {lim})</span>" if lim is not None else ""
            return (f"<tr><td style='padding:4px 14px 4px 0'>{label}</td>"
                    f"<td style='padding:4px 14px 4px 0;font-weight:700'>{val} {unit}{limtxt}</td>"
                    f"<td style='padding:4px 0;color:#666'>{_fmt_time(at)}</td></tr>")

        if not venues:
            p.append("<p>No SPL logging was recorded for this night.</p>")
        for vn, v in venues.items():
            p.append(f"<h3 style='margin:16px 0 6px;border-bottom:2px solid #eee;padding-bottom:4px'>{vn}</h3>"
                     "<table style='border-collapse:collapse;font-size:14px'>")
            p.append(lvl("Max 6-min LAeq (compliance)", v.get("maxLAeq6"), v.get("maxLAeq6At"), v.get("redLimit")))
            p.append(lvl("Max LAeq 10s", v.get("maxLAeq10s"), v.get("maxLAeq10sAt")))
            p.append(lvl("Max instant (dBA Slow)", v.get("maxInstant"), v.get("maxInstantAt")))
            p.append(lvl("Max 6-min LCeq (bass)", v.get("maxLCeq6"), v.get("maxLCeq6At"), unit="dBC"))
            p.append(lvl("Max LCpeak", v.get("maxPeakC"), v.get("maxPeakCAt"), unit="dBC"))
            p.append("</table>"
                     f"<div style='color:#999;font-size:12px;margin-top:4px'>"
                     f"logged {_fmt_time(v.get('firstSeen'))} &ndash; {_fmt_time(v.get('lastSeen'))}</div>")

        p.append(f"<h3 style='margin:18px 0 6px'>Violations ({len(viols)})</h3>")
        if not viols:
            p.append("<p style='color:#1f7a44'>None — clean night.</p>")
        else:
            p.append("<table style='border-collapse:collapse;font-size:14px'>"
                     "<tr style='text-align:left;color:#666'>"
                     "<th style='padding:4px 14px 4px 0'>#</th><th style='padding:4px 14px 4px 0'>Where</th>"
                     "<th style='padding:4px 14px 4px 0'>Start</th><th style='padding:4px 14px 4px 0'>Duration</th>"
                     "<th style='padding:4px 0'>Peak</th></tr>")
            for i, vi in enumerate(viols, 1):
                p.append(f"<tr><td style='padding:4px 14px 4px 0'>{i}</td>"
                         f"<td style='padding:4px 14px 4px 0'>{vi.get('venue')}</td>"
                         f"<td style='padding:4px 14px 4px 0'>{_fmt_time(vi.get('start'))}</td>"
                         f"<td style='padding:4px 14px 4px 0'>{_fmt_dur(vi.get('durationSec'))}</td>"
                         f"<td style='padding:4px 0;font-weight:700'>{vi.get('peak')} dBA</td></tr>")
            p.append("</table>")

        p.append(f"<div style='color:#aaa;font-size:11px;margin-top:18px'>Generated "
                 f"{_fmt_time(s.get('generatedAt'))} &middot; raw per-second log attached (CSV)</div></div>")
        return "".join(p)

    def _save_throttled(self, t):
        if t - self._last_save >= 15:
            self._last_save = t
            self._save(self.current)

    def _save(self, rec):
        if not rec:
            return
        try:
            with open(self._path(rec["day"]), "w") as fh:
                json.dump(rec, fh, indent=2)
        except OSError:
            pass
