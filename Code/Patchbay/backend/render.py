"""Printable patch sheet: one standalone HTML doc, printed by weasyprint if it's
installed and by the browser (Cmd-P → Save as PDF) otherwise. Palette and column
order follow the show-doc standard in CLAUDE.md."""
from __future__ import annotations

import html
from datetime import datetime

SECTION_COLORS = {
    "DRUMS": ("#FDE68A", "#FEF3C7", "DRUMS / PERC"),
    "RHYTHM": ("#BBF7D0", "#DCFCE7", "RHYTHM"),
    "PIANO": ("#FBCFE8", "#FCE7F3", "PIANO"),
    "STRINGS": ("#BFDBFE", "#DBEAFE", "STRINGS"),
    "HORNS": ("#FCD9B4", "#FFEDD5", "HORNS / WINDS"),
    "VOCALS": ("#DDD6FE", "#EDE9FE", "VOCALS"),
    "AMBIENT": ("#C7D2FE", "#E0E7FF", "AMBIENT / FOH"),
    "SPARE": ("#E5E7EB", "#F3F4F6", "SPARE"),
}
SECTION_ORDER = ["DRUMS", "RHYTHM", "PIANO", "STRINGS", "HORNS", "VOCALS", "AMBIENT", "SPARE"]

CSS = """
@page { size: Letter landscape; margin: 0.4in; }
* { box-sizing: border-box; }
html { color-scheme: light; background: #fff; }
body { font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 10pt; color: #111827;
       margin: 0; background: #fff; }
h2 { font-size: 12pt; margin: 18px 0 6px; text-transform: uppercase; letter-spacing: .04em; }
.titlebar { background: #1F2937; color: #fff; padding: 10px 14px; }
.titlebar .t { font-size: 20pt; font-weight: bold; line-height: 1.1; }
.subbar { background: #374151; color: #fff; padding: 5px 14px; font-size: 9.5pt;
          display: flex; flex-wrap: wrap; gap: 18px; }
.subbar b { font-weight: 600; opacity: .75; margin-right: 4px; }
table { width: 100%; border-collapse: collapse; margin-bottom: 6px; }
th { background: #111827; color: #fff; font-size: 8.5pt; text-align: left;
     padding: 4px 5px; text-transform: uppercase; letter-spacing: .03em; }
td { padding: 3px 5px; border-bottom: 1px solid #D1D5DB; font-size: 9.5pt; vertical-align: top; }
tr.sec td { font-weight: bold; font-size: 9pt; letter-spacing: .05em; padding: 4px 5px; }
.mono { font-family: Consolas, "Courier New", monospace; }
.ctr { text-align: center; }
.v48 { color: #065F46; font-weight: bold; }
.tour { background: #FFF3CD; }
.warn { background: #FFE4B5; }
.ribbon { color: #B91C1C; font-weight: bold; }
.notes { background: #F4F0E8; padding: 8px 10px; font-size: 9pt; white-space: pre-wrap; }
.small { font-size: 8.5pt; color: #4B5563; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.foot { margin-top: 10px; font-size: 8pt; color: #6B7280; }
.chip { display: inline-block; padding: 1px 6px; border-radius: 3px; background: #E5E7EB;
        font-size: 8.5pt; margin-right: 4px; }
"""


def e(v) -> str:
    return html.escape(str(v if v is not None else ""))


def _header(sheet: dict, console: dict, subtitle: str) -> str:
    m = sheet.get("meta", {})
    bits = [
        ("Venue", sheet.get("venue_label")),
        ("Console", console["label"]),
        ("Date", sheet.get("date")),
        ("Rev", sheet.get("rev")),
        ("FOH", m.get("foh")),
        ("MON", m.get("mon")),
        ("Show", m.get("showtime")),
    ]
    sub = "".join(f"<span><b>{e(k)}</b>{e(v)}</span>" for k, v in bits if v)
    artist = m.get("artist")
    return (
        f'<div class="titlebar" style="background:{console["title_color"]}">'
        f'<div class="t">{e(sheet.get("name"))}</div>'
        f'<div class="small" style="color:#D1D5DB">{e(artist or subtitle)}</div></div>'
        f'<div class="subbar" style="background:{console["accent"]}">{sub}</div>'
    )


CONSOLE_INFO_FIELDS = [
    ("manufacturer", "Manufacturer"),
    ("model", "Model"),
    ("fw", "Firmware"),
    ("channels", "Input channels"),
    ("busses", "Busses"),
    ("auxes", "Auxes"),
    ("dcas", "DCAs / VCAs"),
    ("mutes", "Mute groups"),
    ("matrix", "Matrix"),
    ("local_in", "Console inputs"),
    ("local_out", "Console outputs"),
    ("ip", "IP address"),
    ("subnet", "Subnet"),
    ("gateway", "Gateway"),
    ("dns", "DNS"),
]


def _kv_table(title: str, pairs: list[tuple[str, str]]) -> str:
    body = "".join(
        f'<tr><td class="small" style="width:38%;color:#4B5563">{e(k)}</td><td>{e(v)}</td></tr>'
        for k, v in pairs
    )
    return (
        f"<table><thead><tr><th colspan='2'>{e(title)}</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _info_block(sheet: dict) -> str:
    """Location + console info, side by side. Prints only what's filled in."""
    loc = sheet.get("location") or {}
    ci = sheet.get("console_info") or {}

    site = " · ".join(x for x in (loc.get("site"), loc.get("room")) if x)
    addr = ", ".join(x for x in (loc.get("address"), loc.get("city")) if x)
    region = " ".join(x for x in (loc.get("state"), loc.get("zip")) if x)
    loc_pairs = [
        (k, v)
        for k, v in [
            ("Project", loc.get("project")),
            ("Client / org", loc.get("client")),
            ("Site", site),
            ("Address", ", ".join(x for x in (addr, region) if x)),
        ]
        if v
    ]
    con_pairs = [(label, ci.get(key)) for key, label in CONSOLE_INFO_FIELDS if ci.get(key) not in (None, "")]
    if not loc_pairs and not con_pairs:
        return ""

    blocks = []
    if loc_pairs:
        blocks.append(("Location", loc_pairs))
    if con_pairs:
        # Split the console fields over two columns so the block stays short.
        half = (len(con_pairs) + 1) // 2 if len(con_pairs) > 6 else len(con_pairs)
        blocks.append(("Console", con_pairs[:half]))
        if con_pairs[half:]:
            blocks.append(("Console (cont.)", con_pairs[half:]))

    width = f"{100 // len(blocks)}%"
    cells = "".join(
        f'<td style="width:{width};border:0;padding:0 10px 0 0;vertical-align:top">{_kv_table(title, pairs)}</td>'
        for title, pairs in blocks
    )
    return f'<h2>Rig information</h2><table style="margin-bottom:2px"><tr>{cells}</tr></table>'


def _input_rows(sheet: dict) -> str:
    rows = sorted(sheet.get("inputs", []), key=lambda r: r.get("ch") or 0)
    by_section: dict[str, list[dict]] = {}
    for r in rows:
        if not (r.get("name") or r.get("mic") or r.get("instrument")):
            continue
        by_section.setdefault(r.get("section") or "SPARE", []).append(r)
    out = []
    for sec in SECTION_ORDER:
        group = by_section.get(sec)
        if not group:
            continue
        head, alt, label = SECTION_COLORS[sec]
        out.append(f'<tr class="sec"><td colspan="8" style="background:{head}">{label}</td></tr>')
        for i, r in enumerate(group):
            bg = alt if i % 2 else "#FFFFFF"
            cls = " tour" if r.get("tour") else ""
            mic = e(r.get("mic"))
            if r.get("tour"):
                mic += ' <span class="chip">⚑ TOUR</span>'
            v48 = '<span class="v48">✓</span>' if r.get("phantom") else ""
            if r.get("ribbon"):
                v48 = '<span class="ribbon">NO 48V</span>'
            out.append(
                f'<tr class="{cls}" style="background:{bg}">'
                f'<td class="mono ctr">{e(r.get("ch"))}</td>'
                f'<td>{e(r.get("name") or r.get("instrument"))}</td>'
                f"<td>{mic}</td>"
                f'<td class="mono">{e(r.get("port"))}</td>'
                f'<td class="mono">{e(r.get("split"))}</td>'
                f'<td class="ctr">{v48}</td>'
                f'<td>{e(r.get("stand"))}</td>'
                f'<td class="small">{e(r.get("notes"))}</td></tr>'
            )
    return "".join(out) or '<tr><td colspan="8" class="small">No inputs yet.</td></tr>'


def _patch_page(sheet: dict) -> str:
    rows = [r for r in sheet.get("inputs", []) if (r.get("port") or "").strip()]

    def key(r):
        port = r["port"]
        head = "".join(ch for ch in port if not ch.isdigit()).strip()
        num = "".join(ch for ch in port if ch.isdigit())
        return (0 if head.lower().startswith("aes") else 1, head.lower(), int(num or 0))

    rows.sort(key=key)
    body = "".join(
        f'<tr><td class="mono">{e(r["port"])}</td><td class="mono ctr">{e(r.get("ch"))}</td>'
        f'<td>{e(r.get("name") or r.get("instrument"))}</td><td>{e(r.get("mic"))}</td>'
        f'<td>{e(r.get("box"))}</td><td class="small">{e(r.get("notes"))}</td></tr>'
        for r in rows
    ) or '<tr><td colspan="6" class="small">Nothing patched yet.</td></tr>'
    return (
        "<h2>Patching — by port</h2><table><thead><tr>"
        "<th style='width:14%'>Port</th><th style='width:6%'>CH</th><th style='width:24%'>Input</th>"
        "<th style='width:20%'>Mic / DI</th><th style='width:16%'>Stage box</th><th>Notes</th>"
        f"</tr></thead><tbody>{body}</tbody></table>"
    )


def _crosspatch_page(sheet: dict) -> str:
    boxes = sheet.get("stageboxes", [])
    if not boxes:
        return ""
    out = ["<h2>Cross-patch — by stage box</h2>"]
    for box in boxes:
        rows = [r for r in sheet.get("inputs", []) if (r.get("box") or "") == box.get("name")]
        rows.sort(key=lambda r: r.get("ch") or 0)
        body = "".join(
            f'<tr><td class="mono ctr">{e(r.get("ch"))}</td><td class="mono">{e(r.get("port"))}</td>'
            f'<td>{e(r.get("name") or r.get("instrument"))}</td><td>{e(r.get("mic"))}</td>'
            f'<td class="mono">{e(r.get("split"))}</td></tr>'
            for r in rows
        ) or '<tr><td colspan="5" class="small">No inputs assigned to this box.</td></tr>'
        meta = " · ".join(
            x for x in [box.get("location"), box.get("format"),
                        f"{box.get('inputs') or '?'} in / {box.get('outputs') or '?'} out"] if x
        )
        out.append(
            f'<h3 style="font-size:10.5pt;margin:12px 0 4px">{e(box.get("name"))} '
            f'<span class="small">{e(meta)}</span></h3>'
            "<table><thead><tr><th style='width:8%'>CH</th><th style='width:16%'>Port</th>"
            "<th style='width:32%'>Input</th><th style='width:26%'>Mic / DI</th><th>Split</th>"
            f"</tr></thead><tbody>{body}</tbody></table>"
        )
    return "".join(out)


def _outputs_page(sheet: dict) -> str:
    rows = [r for r in sheet.get("outputs", []) if r.get("name") or r.get("port") or r.get("device")]
    body = "".join(
        f'<tr><td class="mono">{e(r.get("bus"))}</td><td>{e(r.get("name"))}</td>'
        f'<td class="mono">{e(r.get("port"))}</td><td>{e(r.get("device"))}</td>'
        f'<td>{e(r.get("location"))}</td><td class="small">{e(r.get("notes"))}</td></tr>'
        for r in rows
    ) or '<tr><td colspan="6" class="small">No outputs documented.</td></tr>'
    return (
        "<h2>Outputs &amp; buses</h2><table><thead><tr>"
        "<th style='width:12%'>Bus</th><th style='width:22%'>Feeds</th><th style='width:16%'>Port</th>"
        "<th style='width:20%'>Device</th><th style='width:14%'>Location</th><th>Notes</th>"
        f"</tr></thead><tbody>{body}</tbody></table>"
    )


def _power_page(sheet: dict) -> str:
    distros = sheet.get("power", [])
    if not distros:
        return ""
    out = ["<h2>Power</h2>"]
    for d in distros:
        circuits = d.get("circuits", [])
        body = "".join(
            f'<tr><td class="mono">{e(c.get("ckt"))}</td><td>{e(c.get("load"))}</td>'
            f'<td class="ctr">{e(c.get("amps"))}</td><td class="small">{e(c.get("notes"))}</td></tr>'
            for c in circuits
        ) or '<tr><td colspan="4" class="small">No circuits listed.</td></tr>'
        total = sum(float(c.get("amps") or 0) for c in circuits)
        meta = " · ".join(x for x in [d.get("location"), d.get("feed")] if x)
        out.append(
            f'<h3 style="font-size:10.5pt;margin:12px 0 4px">{e(d.get("name"))} '
            f'<span class="small">{e(meta)}</span></h3>'
            "<table><thead><tr><th style='width:14%'>Circuit</th><th style='width:44%'>Load</th>"
            "<th style='width:10%'>Amps</th><th>Notes</th></tr></thead>"
            f"<tbody>{body}</tbody></table>"
            f'<div class="small">Listed load: {total:g} A</div>'
        )
    return "".join(out)


def _contacts_page(sheet: dict) -> str:
    people = [c for c in sheet.get("contacts", []) if c.get("name") or c.get("role")]
    if not people:
        return ""
    body = "".join(
        f'<tr><td>{e(c.get("name"))}</td><td>{e(c.get("role"))}</td>'
        f'<td class="mono">{e(c.get("phone"))}</td><td>{e(c.get("email"))}</td>'
        f'<td class="small">{e(c.get("notes"))}</td></tr>'
        for c in people
    )
    return (
        "<h2>Contacts</h2><table><thead><tr><th style='width:22%'>Name</th>"
        "<th style='width:18%'>Role</th><th style='width:16%'>Phone</th>"
        f"<th style='width:22%'>Email</th><th>Notes</th></tr></thead><tbody>{body}</tbody></table>"
    )


def _stageio_page(sheet: dict) -> str:
    positions = [p for p in sheet.get("positions", []) if p.get("name") or p.get("runs")]
    runs = [d for d in sheet.get("data_runs", []) if d.get("label")]
    if not positions and not runs:
        return ""
    out = ["<h2>Stage I/O</h2>"]
    for pos in positions:
        body = "".join(
            f'<tr><td>{e(r.get("label"))}</td><td>{e(r.get("device"))}</td>'
            f'<td class="mono">{e(r.get("port"))}</td><td class="small">{e(r.get("notes"))}</td></tr>'
            for r in pos.get("runs", [])
        ) or '<tr><td colspan="4" class="small">No runs mapped.</td></tr>'
        out.append(
            f'<h3 style="font-size:10.5pt;margin:12px 0 4px">{e(pos.get("name"))} '
            f'<span class="small">{e(pos.get("note"))}</span></h3>'
            "<table><thead><tr><th style='width:30%'>Run</th><th style='width:26%'>Device</th>"
            f"<th style='width:16%'>Port</th><th>Notes</th></tr></thead><tbody>{body}</tbody></table>"
        )
    if runs:
        body = "".join(
            f'<tr><td>{e(d.get("label"))}</td><td>{e(d.get("type"))}</td></tr>' for d in runs
        )
        out.append(
            '<h3 style="font-size:10.5pt;margin:12px 0 4px">Data connections</h3>'
            "<table><thead><tr><th style='width:60%'>Label</th><th>Type</th></tr></thead>"
            f"<tbody>{body}</tbody></table>"
        )
    return "".join(out)


def _devices_page(sheet: dict) -> str:
    net = [d for d in sheet.get("devices", []) if d.get("kind") == "network" and d.get("name")]
    if not net:
        return ""
    body = "".join(
        f'<tr><td>{e(d.get("name"))}</td><td>{e(d.get("protocol"))}</td>'
        f'<td class="mono">{e(d.get("ip"))}</td><td class="small">{e(d.get("notes"))}</td></tr>'
        for d in net
    )
    return (
        "<h2>Network devices</h2><table><thead><tr><th style='width:30%'>Device</th>"
        "<th style='width:20%'>Protocol</th><th style='width:18%'>IP</th><th>Notes</th>"
        f"</tr></thead><tbody>{body}</tbody></table>"
    )


def render(sheet: dict, console: dict, analysis: dict) -> str:
    counts = analysis["counts"]
    errors = [p for p in analysis["problems"] if p["level"] == "error"]
    warn_block = ""
    if errors:
        items = "".join(f'<div>• {e(p["where"])} — {e(p["msg"])}</div>' for p in errors)
        warn_block = f'<div class="notes warn" style="margin:8px 0">Open conflicts at print time:{items}</div>'
    notes = sheet.get("meta", {}).get("notes")
    notes_block = f'<h2>Notes</h2><div class="notes">{e(notes)}</div>' if notes else ""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{e(sheet.get('name'))} — Patch Sheet</title><style>{CSS}</style></head><body>
<div class="page">
{_header(sheet, console, 'Patch sheet')}
{warn_block}
{_info_block(sheet)}
<h2>Input list</h2>
<table><thead><tr>
<th style="width:5%">CH</th><th style="width:19%">Instrument</th><th style="width:20%">Mic / DI</th>
<th style="width:11%">Port</th><th style="width:10%">Split</th><th style="width:5%">48V</th>
<th style="width:8%">Stand</th><th>Notes</th>
</tr></thead><tbody>{_input_rows(sheet)}</tbody></table>
<div class="foot">{counts['active']} active inputs · {counts['patched']} patched · capacity {counts['capacity']} on the {e(console['label'])}</div>
</div>
<div class="page">{_header(sheet, console, 'Patching')}{_patch_page(sheet)}{_crosspatch_page(sheet)}</div>
<div class="page">{_header(sheet, console, 'Outputs, power, notes')}{_outputs_page(sheet)}{_stageio_page(sheet)}{_devices_page(sheet)}{_power_page(sheet)}{_contacts_page(sheet)}{notes_block}
<div class="foot">Patchbay · {e(sheet.get('name'))} Rev {e(sheet.get('rev'))} · printed {stamp}</div>
</div>
</body></html>"""


def to_pdf(html_doc: str) -> bytes | None:
    """Return PDF bytes if weasyprint is installed, else None (browser prints it)."""
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        return None
    return HTML(string=html_doc).write_pdf()
