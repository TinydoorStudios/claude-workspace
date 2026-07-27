"""Sheet schema v2 — migration from the flat v1 shape, and a flat view for exports.

v1 was one console per sheet: {console: "q225", inputs: [...], outputs: [...],
stageboxes: [...]}. v2 mirrors how the desk world actually looks: a sheet holds
several consoles (FOH, MON…), each with its own channels and outputs; devices,
stage positions, data runs and contacts belong to the sheet.

Everything old on disk is migrated on read, so no data conversion pass is needed.
`flatten()` gives the exports and the analyzer the v1-style view of one console.
"""
from __future__ import annotations

from .store import new_id

SCHEMA = 2

COUNT_KEYS = ["inputs", "busses", "auxes", "dcas", "mutes", "matrix", "outputs"]


def blank_location() -> dict:
    return {"project": "", "client": "", "site": "", "room": "", "address": "", "city": "", "state": "", "zip": ""}


def blank_counts() -> dict:
    return {k: 0 for k in COUNT_KEYS}


def blank_console(console_id: str = "q225", name: str = "Console") -> dict:
    return {
        "id": new_id(),
        "name": name,
        "preset": console_id,
        "manufacturer": "",
        "model": "",
        "fw": "",
        "counts": blank_counts(),
        "network": {"ip": "", "subnet": "", "gateway": "", "dns": ""},
        "connections": [],
        "tielines": False,
        "channels": [],
        "outputs": [],
        "notes": "",
    }


def blank_channel(ch: int) -> dict:
    return {
        "id": new_id(),
        "ch": ch,
        "name": "",
        "instrument": "",
        "mic": "",
        "stand": "",
        "phantom": False,
        "ribbon": False,
        "tour": False,
        "ms": "",
        "link": "",
        "section": "SPARE",
        "port": "",
        "alt": "",
        "insert_a": "",
        "insert_b": "",
        "direct": "",
        "box": "",
        "split": "",
        "notes": "",
    }


def blank_device(kind: str = "io") -> dict:
    return {
        "id": new_id(),
        "kind": kind,  # "io" | "network"
        "name": "",
        "inputs": 0,
        "outputs": 0,
        "ip": "",
        "protocol": "",
        "location": "",
        "format": "",
        "notes": "",
        "consoles": [],
    }


def blank_position() -> dict:
    return {"id": new_id(), "name": "", "note": "", "runs": []}


def blank_contact() -> dict:
    return {"id": new_id(), "name": "", "role": "", "phone": "", "email": "", "notes": ""}


# ---------------------------------------------------------------- migrate
def migrate(sheet: dict) -> dict:
    """Bring any sheet up to v2. Idempotent."""
    if int(sheet.get("schema") or 0) >= SCHEMA:
        return _fill_defaults(sheet)

    con = blank_console(sheet.get("console") or "q225")
    info = sheet.get("console_info") or {}
    con.update(
        {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "fw": info.get("fw", ""),
            "network": {
                "ip": info.get("ip", ""),
                "subnet": info.get("subnet", ""),
                "gateway": info.get("gateway", ""),
                "dns": info.get("dns", ""),
            },
        }
    )
    counts = blank_counts()
    for key, src in [("inputs", "channels"), ("busses", "busses"), ("auxes", "auxes"),
                     ("dcas", "dcas"), ("mutes", "mutes"), ("matrix", "matrix"), ("outputs", "local_out")]:
        try:
            counts[key] = int(info.get(src) or 0)
        except (TypeError, ValueError):
            counts[key] = 0
    counts["inputs"] = counts["inputs"] or len(sheet.get("inputs", []))
    counts["outputs"] = counts["outputs"] or len(sheet.get("outputs", []))
    con["counts"] = counts

    for row in sheet.get("inputs", []):
        ch = blank_channel(row.get("ch") or 0)
        ch.update({k: row.get(k, ch[k]) for k in ch if k in row})
        ch["id"] = row.get("id") or ch["id"]
        con["channels"].append(ch)
    con["outputs"] = list(sheet.get("outputs", []))
    sheet["consoles"] = [con]

    devices = []
    for box in sheet.get("stageboxes", []):
        dev = blank_device("io")
        dev.update(
            {
                "id": box.get("id") or dev["id"],
                "name": box.get("name", ""),
                "inputs": int(box.get("inputs") or 0),
                "outputs": int(box.get("outputs") or 0),
                "location": box.get("location", ""),
                "format": box.get("format", ""),
                "notes": box.get("notes", ""),
                "consoles": [con["id"]],
            }
        )
        devices.append(dev)
    sheet["devices"] = devices

    for key in ("inputs", "outputs", "stageboxes", "console_info"):
        sheet.pop(key, None)
    sheet["schema"] = SCHEMA
    return _fill_defaults(sheet)


def _fill_defaults(sheet: dict) -> dict:
    sheet.setdefault("schema", SCHEMA)
    # Locked sheets are the house templates: read-only until explicitly unlocked,
    # so a show build can't drift the rig it was cloned from.
    sheet.setdefault("locked", False)
    sheet.setdefault("location", blank_location())
    sheet.setdefault("meta", {"foh": "", "mon": "", "showtime": "", "artist": "", "notes": ""})
    sheet.setdefault("consoles", [blank_console(sheet.get("console") or "q225")])
    sheet.setdefault("devices", [])
    sheet.setdefault("positions", [])
    sheet.setdefault("data_runs", [])
    sheet.setdefault("contacts", [])
    sheet.setdefault("power", [])
    for con in sheet["consoles"]:
        con.setdefault("counts", blank_counts())
        con.setdefault("network", {"ip": "", "subnet": "", "gateway": "", "dns": ""})
        con.setdefault("connections", [])
        con.setdefault("channels", [])
        con.setdefault("outputs", [])
    # `console` stays as the primary desk id: the exports and port maps use it.
    sheet["console"] = sheet["consoles"][0].get("preset") or sheet.get("console") or "q225"
    return sheet


# ---------------------------------------------------------------- flatten
def flatten(sheet: dict, console_index: int = 0) -> dict:
    """A v1-shaped view of one console — what render/xlsx/analyze expect."""
    consoles = sheet.get("consoles") or [blank_console()]
    con = consoles[min(console_index, len(consoles) - 1)]
    flat = dict(sheet)
    flat["console"] = con.get("preset") or "q225"
    flat["inputs"] = con.get("channels", [])
    flat["outputs"] = con.get("outputs", [])
    flat["stageboxes"] = [
        {
            "id": d["id"],
            "name": d.get("name", ""),
            "location": d.get("location", ""),
            "format": d.get("format") or d.get("protocol", ""),
            "inputs": d.get("inputs", 0),
            "outputs": d.get("outputs", 0),
            "notes": d.get("notes") or (f"IP {d['ip']}" if d.get("ip") else ""),
        }
        for d in sheet.get("devices", [])
        if d.get("kind", "io") == "io" and (not d.get("consoles") or con["id"] in d.get("consoles", []))
    ]
    flat["console_info"] = {
        "manufacturer": con.get("manufacturer", ""),
        "model": con.get("model", ""),
        "fw": con.get("fw", ""),
        "channels": con.get("counts", {}).get("inputs") or "",
        "busses": con.get("counts", {}).get("busses") or "",
        "auxes": con.get("counts", {}).get("auxes") or "",
        "dcas": con.get("counts", {}).get("dcas") or "",
        "mutes": con.get("counts", {}).get("mutes") or "",
        "matrix": con.get("counts", {}).get("matrix") or "",
        "local_out": con.get("counts", {}).get("outputs") or "",
        **{k: v for k, v in (con.get("network") or {}).items() if v},
    }
    return flat
