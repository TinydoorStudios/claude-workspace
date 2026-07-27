"""Sheet shape, seeding, analysis (conflict + count reconciliation), brief import."""
from __future__ import annotations

from datetime import date

from .schema import SCHEMA, blank_channel, blank_console, blank_device, blank_location, flatten
from .store import new_id

SECTION_BY_KEYWORD = [
    ("DRUMS", ("kick", "snare", "hat", "tom", "oh", "overhead", "ride", "perc", "conga", "bongo", "timbale", "cajon", "bodhran", "drum")),
    ("RHYTHM", ("bass", "gtr", "guitar", "keys", "key", "synth", "banjo", "mando", "bouzouki", "uke", "accordion", "click", "track", "playback")),
    ("PIANO", ("piano", "rhodes", "wurli")),
    ("STRINGS", ("violin", "viola", "cello", "fiddle", "harp", "string", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10")),
    ("HORNS", ("trumpet", "trombone", "sax", "tuba", "horn", "flute", "clarinet", "oboe", "pipes", "whistle")),
    ("VOCALS", ("vox", "vocal", "lead", "bgv", "talk", "mc", "announce")),
    ("AMBIENT", ("crowd", "ambient", "room", "audience", "house")),
]


def guess_section(name: str, instrument: str = "") -> str:
    hay = f"{name} {instrument}".lower()
    for section, words in SECTION_BY_KEYWORD:
        if any(w in hay for w in words):
            return section
    return "SPARE"


def blank_input(ch: int) -> dict:
    """v1 name for a console channel — kept so seeding and imports still read well."""
    return blank_channel(ch)


def blank_output(bus: str = "", name: str = "") -> dict:
    return {
        "id": new_id(),
        "bus": bus,
        "name": name,
        "port": "",
        "device": "",
        "location": "",
        "notes": "",
    }


def new_sheet(name: str, console: str, venue: str, venue_label: str, kind: str, bus_seed: list[dict], channels: int = 32) -> dict:
    """A fresh v2 sheet with one console."""
    con = blank_console(console, "FOH Console")
    con["channels"] = [blank_channel(i) for i in range(1, channels + 1)]
    con["outputs"] = [blank_output(b["bus"], b["name"]) for b in bus_seed]
    con["counts"]["inputs"] = channels
    con["counts"]["outputs"] = len(con["outputs"])
    return {
        "schema": SCHEMA,
        "name": name,
        "kind": kind,
        "console": console,
        "venue": venue,
        "venue_label": venue_label,
        "date": date.today().isoformat(),
        "meta": {"foh": "", "mon": "", "showtime": "", "artist": "", "notes": ""},
        "location": blank_location(),
        "consoles": [con],
        "devices": [],
        "positions": [],
        "data_runs": [],
        "contacts": [],
        "power": [],
        "from_template": None,
    }


def apply_wizard(sheet: dict, wizard: dict) -> dict:
    """Fold the New Patch Sheet wizard's answers into a sheet.

    Location and console info are stored as-is; the wizard's I/O devices become
    stage boxes, which is what the rest of the app patches against.
    """
    loc = {**blank_location(), **(wizard.get("location") or {})}
    sheet["location"] = loc

    info = wizard.get("console_info") or {}
    con = sheet["consoles"][0]
    con.update(
        {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "fw": info.get("fw", ""),
            "network": {k: info.get(k, "") for k in ("ip", "subnet", "gateway", "dns")},
        }
    )
    for key, src in [("inputs", "channels"), ("busses", "busses"), ("auxes", "auxes"), ("dcas", "dcas"),
                     ("mutes", "mutes"), ("matrix", "matrix"), ("outputs", "local_out")]:
        try:
            con["counts"][key] = int(info.get(src) or con["counts"].get(key) or 0)
        except (TypeError, ValueError):
            pass

    site = " · ".join(x for x in (loc.get("site"), loc.get("room")) if x)
    if site and not sheet.get("venue_label"):
        sheet["venue_label"] = site
    if loc.get("client"):
        sheet["meta"]["notes"] = (sheet["meta"].get("notes") or "") or f"Client: {loc['client']}"

    for dev in wizard.get("devices") or []:
        if not (dev.get("name") or dev.get("inputs") or dev.get("outputs")):
            continue
        device = blank_device("io")
        device.update(
            {
                "name": dev.get("name") or "I/O device",
                "inputs": int(dev.get("inputs") or 0),
                "outputs": int(dev.get("outputs") or 0),
                "ip": dev.get("ip", ""),
                "consoles": [con["id"]],
            }
        )
        sheet["devices"].append(device)
    return sheet


def analyze(sheet: dict, console: dict) -> dict:
    """Conflicts, channel-count reconciliation, and patch coverage."""
    problems = []
    used_ch: dict[int, list[str]] = {}
    used_port: dict[str, list[str]] = {}
    valid_in = {p for grp in console["input_ports"] for p in grp["ports"]}
    valid_out = {p for grp in console["output_ports"] for p in grp["ports"]}

    patched = 0
    active = 0
    for row in sheet.get("inputs", []):
        label = row.get("name") or row.get("instrument") or ""
        if label or row.get("mic"):
            active += 1
        ch = row.get("ch")
        if isinstance(ch, int):
            used_ch.setdefault(ch, []).append(label or f"CH {ch}")
        port = (row.get("port") or "").strip()
        if port:
            patched += 1
            used_port.setdefault(port, []).append(label or f"CH {ch}")
            if port not in valid_in:
                problems.append({"level": "warn", "where": f"CH {ch}", "msg": f"port '{port}' is not on this console's input surface"})
        elif label:
            problems.append({"level": "warn", "where": f"CH {ch}", "msg": f"'{label}' has no input port assigned"})
        if row.get("ribbon") and row.get("phantom"):
            problems.append({"level": "error", "where": f"CH {ch}", "msg": f"{row.get('mic') or 'ribbon mic'} — 48V is ON. Ribbon: turn it OFF."})

    for ch, who in used_ch.items():
        if len(who) > 1:
            problems.append({"level": "error", "where": f"CH {ch}", "msg": "duplicate channel number: " + ", ".join(who)})
    for port, who in used_port.items():
        if len(who) > 1:
            problems.append({"level": "error", "where": port, "msg": "port patched twice: " + ", ".join(who)})

    out_ports: dict[str, list[str]] = {}
    for row in sheet.get("outputs", []):
        port = (row.get("port") or "").strip()
        if not port:
            continue
        out_ports.setdefault(port, []).append(row.get("name") or row.get("bus") or port)
        if port not in valid_out:
            problems.append({"level": "warn", "where": row.get("bus") or port, "msg": f"output port '{port}' is not on this console's output surface"})
    for port, who in out_ports.items():
        if len(who) > 1:
            problems.append({"level": "error", "where": port, "msg": "output port used twice: " + ", ".join(who)})

    over = active - console["channels"]
    if over > 0:
        problems.append({"level": "error", "where": "Channel count", "msg": f"{active} active inputs vs {console['channels']} on the {console['label']} — {over} over"})

    return {
        "problems": problems,
        "counts": {
            "rows": len(sheet.get("inputs", [])),
            "active": active,
            "patched": patched,
            "unpatched": active - patched,
            "capacity": console["channels"],
            "outputs": len([o for o in sheet.get("outputs", []) if o.get("name") or o.get("port")]),
            "stageboxes": len(sheet.get("stageboxes", [])),
            "circuits": sum(len(d.get("circuits", [])) for d in sheet.get("power", [])),
        },
    }


def from_brief(brief: dict, console: str, venue_label: str, bus_seed: list[dict]) -> dict:
    """Build a sheet out of a ShowBuilder <Show>.brief.json."""
    sheet = new_sheet(
        name=brief.get("show_name") or brief.get("artist") or "Imported show",
        console=console,
        venue=brief.get("venue", ""),
        venue_label=brief.get("venue_label") or venue_label,
        kind="event",
        bus_seed=bus_seed,
        channels=0,
    )
    sheet["date"] = brief.get("show_date") or sheet["date"]
    sheet["meta"] = {
        "foh": brief.get("foh_engineer", ""),
        "mon": brief.get("mon_engineer", ""),
        "showtime": brief.get("show_time", ""),
        "artist": brief.get("artist", ""),
        "notes": brief.get("show_notes", ""),
    }
    rows = []
    for c in brief.get("channels", []):
        row = blank_input(int(c.get("ch") or 0))
        row.update(
            {
                "name": c.get("name", ""),
                "instrument": c.get("instrument", ""),
                "mic": c.get("mic", ""),
                "stand": c.get("stand", ""),
                "phantom": bool(c.get("phantom")),
                "ribbon": bool(c.get("ribbon")),
                "section": c.get("section") or guess_section(c.get("name", ""), c.get("instrument", "")),
                "port": c.get("patch", ""),
                "notes": c.get("notes", ""),
            }
        )
        rows.append(row)
    rows.sort(key=lambda r: r["ch"])
    sheet["consoles"][0]["channels"] = rows
    sheet["consoles"][0]["counts"]["inputs"] = len(rows)
    return sheet
