"""SPL PDF report — Smaart-style (header, Max/L10/L50/L90 stats, violations) plus
violation shading marked directly on the history graphs.

build_report_pdf(meta, times, series, violations, thresholds) -> PDF bytes.
  meta       : {venue, date, device, channel, start, end, company, calibration, samples}
  times      : [datetime]  (x axis, one per sample)
  series     : {"SPL A Slow":[...], "LAeq 10s":[...], "LAeq 6":[...], "Peak C":[...]}
  violations : [{"start":dt, "end":dt, "durationSec":float, "peak":float}]
  thresholds : {"LAeq 10s":90, "LAeq 6":90}   (drawn as dashed lines)
"""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

import csv as _csv
import datetime as _dt

NAVY = colors.HexColor("#1A3A5C")
RED = colors.HexColor("#9B2222")
GREY = colors.HexColor("#666666")
LINE = {"SPL A Slow": "#5b6675", "LAeq 10s": "#2E6DA4", "LAeq 6": "#2e8b57", "Peak C": "#ff8c1a"}


def _parse_dt(ts):
    try:
        return _dt.datetime.fromisoformat(ts).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def load_series_from_csv(csv_text):
    """Parse a merged night CSV -> (times, {column: [float|None]}). Numeric columns only."""
    r = _csv.reader(io.StringIO(csv_text))
    header = next(r, None)
    if not header or "timestamp" not in header:
        return [], {}
    idx = {h: i for i, h in enumerate(header)}
    skip = {"timestamp", "venue", "light", "violation", "overload", "yellow_limit", "red_limit"}
    cols = {h: [] for h in header if h not in skip}
    times = []
    for row in r:
        if not row:
            continue
        t = _parse_dt(row[idx["timestamp"]])
        if t is None:
            continue
        times.append(t)
        for h in cols:
            try:
                cols[h].append(float(row[idx[h]]))
            except (ValueError, IndexError):
                cols[h].append(None)
    return times, cols


def _stats(vals):
    a = np.array([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return None
    # Ln = level exceeded n% of the time = (100-n)th percentile
    return {"max": a.max(), "L10": np.percentile(a, 90),
            "L50": np.percentile(a, 50), "L90": np.percentile(a, 10)}


def _graph(times, smap, thresh, violations, title, height=2.3):
    fig, ax = plt.subplots(figsize=(7.4, height), dpi=150)
    for name, vals in smap.items():
        arr = [np.nan if v is None else v for v in vals]
        ax.plot(times, arr, label=name, linewidth=0.9, color=LINE.get(name, "#333"))
    for v in violations:
        ax.axvspan(v["start"], v["end"], color="#e74c3c", alpha=0.20, lw=0)
    for name, lim in (thresh or {}).items():
        ax.axhline(lim, color="#e74c3c", linestyle="--", linewidth=1.0)
        ax.text(times[0], lim, f"  {name} limit {lim}", color="#c0392b", fontsize=6.5, va="bottom")
    ax.set_title(title, fontsize=9.5, loc="left", color="#1A3A5C", fontweight="bold")
    if len(smap) > 1 or True:
        ax.legend(fontsize=7, loc="upper right", ncol=max(1, len(smap)), framealpha=0.85)
    ax.grid(True, alpha=0.25)
    ax.set_ylabel("dB", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def _meta_table(meta):
    md = [
        ["Venue", meta.get("venue", ""), "Input Device", meta.get("device", "")],
        ["Company", meta.get("company", ""), "Input Channel", meta.get("channel", "")],
        ["Summary Start", meta.get("start", ""), "Calibration Date", meta.get("calibration", "")],
        ["Summary End", meta.get("end", ""), "Samples", str(meta.get("samples", ""))],
    ]
    t = Table(md, colWidths=[1.1 * inch, 2.2 * inch, 1.2 * inch, 2.2 * inch])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), GREY), ("TEXTCOLOR", (2, 0), (2, -1), GREY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"), ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def build_minimal_report_pdf(meta, violations, message):
    """One-page PDF for report days with no per-second data — keeps the nightly
    email's attachment present so the Gmail node never fails on an empty night."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=18, textColor=NAVY, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=ss["Normal"], fontSize=9, textColor=GREY)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, textColor=NAVY, spaceBefore=12, spaceAfter=4)
    story = [Paragraph("SPL Report", h1),
             Paragraph(f"{meta.get('venue','')} &nbsp;&middot;&nbsp; {meta.get('date','')}", sub),
             Spacer(1, 8), _meta_table(meta), Spacer(1, 10),
             Paragraph(message, ss["Normal"])]
    if violations:
        story.append(Paragraph(f"Violations ({len(violations)})", h2))
        vr = [["#", "Start", "Duration", "Peak"]]
        for i, v in enumerate(violations, 1):
            dur = v.get("durationSec") or 0
            m, sec = divmod(int(dur), 60)
            st = v["start"].strftime("%H:%M:%S") if v.get("start") else ""
            vr.append([str(i), st, (f"{m}:{sec:02d}" if m else f"{sec}s"), f"{v.get('peak','')} dBA"])
        vt = Table(vr, colWidths=[0.5 * inch, 1.6 * inch, 1.2 * inch, 1.4 * inch])
        vt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), RED), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbeded")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e0c0c0")),
        ]))
        story.append(vt)
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def build_report_pdf(meta, times, series, violations, thresholds):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=18, textColor=NAVY, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=ss["Normal"], fontSize=9, textColor=GREY)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, textColor=NAVY, spaceBefore=12, spaceAfter=4)
    story = []

    story.append(Paragraph("SPL Report", h1))
    story.append(Paragraph(f"{meta.get('venue','')} &nbsp;&middot;&nbsp; {meta.get('date','')}", sub))
    story.append(Spacer(1, 8))

    # metadata grid
    md = [
        ["Venue", meta.get("venue", ""), "Input Device", meta.get("device", "")],
        ["Company", meta.get("company", ""), "Input Channel", meta.get("channel", "")],
        ["Summary Start", meta.get("start", ""), "Calibration Date", meta.get("calibration", "")],
        ["Summary End", meta.get("end", ""), "Samples", str(meta.get("samples", ""))],
    ]
    t = Table(md, colWidths=[1.1 * inch, 2.2 * inch, 1.2 * inch, 2.2 * inch])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), GREY), ("TEXTCOLOR", (2, 0), (2, -1), GREY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"), ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    # statistics table
    story.append(Paragraph("Statistics", h2))
    rows = [["Metric", "Max", "L10", "L50", "L90"]]
    for name, vals in series.items():
        s = _stats(vals)
        if not s:
            continue
        rows.append([name] + [f"{s[k]:.1f}" for k in ("max", "L10", "L50", "L90")])
    st = Table(rows, colWidths=[1.9 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f7")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cdd6e2")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(st)
    story.append(Paragraph("L10 / L50 / L90 = level exceeded 10% / 50% / 90% of the time.", sub))

    # violations
    story.append(Paragraph(f"Violations ({len(violations)})", h2))
    if not violations:
        story.append(Paragraph("None recorded.", ss["Normal"]))
    else:
        vr = [["#", "Start", "Duration", "Peak"]]
        for i, v in enumerate(violations, 1):
            dur = v.get("durationSec") or 0
            m, s = divmod(int(dur), 60)
            vr.append([str(i), v["start"].strftime("%H:%M:%S"),
                       (f"{m}:{s:02d}" if m else f"{s}s"), f"{v.get('peak','')} dBA"])
        vt = Table(vr, colWidths=[0.5 * inch, 1.6 * inch, 1.2 * inch, 1.4 * inch])
        vt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), RED), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbeded")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e0c0c0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(vt)

    # graphs (violations shaded in red)
    story.append(Paragraph("History &mdash; violations shaded", h2))
    overview = {k: series[k] for k in ("SPL A Slow", "LAeq 10s", "LAeq 6") if k in series}
    story.append(Image(_graph(times, overview, thresholds, violations, "Overview"), width=7.0 * inch, height=2.2 * inch))
    story.append(Spacer(1, 4))
    if "LAeq 10s" in series:
        story.append(Image(_graph(times, {"LAeq 10s": series["LAeq 10s"]}, {"LAeq 10s": thresholds.get("LAeq 10s")},
                                  violations, "LAeq 10s (violation trigger)"), width=7.0 * inch, height=2.0 * inch))
        story.append(Spacer(1, 4))
    if "LAeq 6" in series:
        story.append(Image(_graph(times, {"LAeq 6": series["LAeq 6"]}, {"LAeq 6": thresholds.get("LAeq 6")},
                                  violations, "LAeq 6 (6-min compliance)"), width=7.0 * inch, height=2.0 * inch))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
