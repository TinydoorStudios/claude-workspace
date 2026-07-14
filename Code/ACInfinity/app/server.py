"""
AC Infinity dashboard + control server.

Run:  ./run.sh      (reads creds from aci.env)
Then: http://localhost:8096

Credentials come from env (never hard-coded):
    ACI_EMAIL, ACI_PASSWORD   (required)
    ACI_PORT                  (default 8096)
    ACI_PASSCODE              (optional gate for the whole UI/API)
"""

import os
from pathlib import Path

from aiohttp import web

from aci_client import (ACInfinity, MODE_LABELS, GROUP_MODE_LABELS,
                        GROUP_DEV_TYPES, decode_reading)

WEB = Path(__file__).resolve().parent.parent / "web"
PORT = int(os.environ.get("ACI_PORT", "8096"))
PASSCODE = os.environ.get("ACI_PASSCODE")  # None = open


def _require(req):
    if not PASSCODE:
        return
    given = req.headers.get("X-Passcode") or req.query.get("pc")
    if given != PASSCODE:
        raise web.HTTPUnauthorized(text="bad passcode")


def _hhmm(minutes):
    if minutes is None:
        return None
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _shape_group(g):
    mode = g.get("currentMode")
    triggers = []
    if g.get("autoHighTempSwitch"):
        triggers.append(f"temp > {g.get('autoHighTempF')}°F")
    if g.get("autoLowTempSwitch"):
        triggers.append(f"temp < {g.get('autoLowTempF')}°F")
    if g.get("autoHighHumiSwitch"):
        triggers.append(f"RH > {g.get('autoHighHumi')}%")
    if g.get("autoLowHumiSwitch"):
        triggers.append(f"RH < {g.get('autoLowHumi')}%")
    return {
        "advId": g.get("advId"),
        "name": g.get("advName"),
        "isOn": g.get("isOn"),
        "mode": mode,
        "modeLabel": GROUP_MODE_LABELS.get(mode, f"Mode {mode}"),
        "devType": g.get("grouptDevType"),
        "devTypeLabel": GROUP_DEV_TYPES.get(g.get("grouptDevType"),
                                            f"Type {g.get('grouptDevType')}"),
        "onSpeed": g.get("onSpeed"),
        "offSpeed": g.get("offSpeed"),
        "triggers": triggers,
        "cycleOnMin": (g.get("cycleOn") or 0) // 60,
        "cycleOffMin": (g.get("cycleOff") or 0) // 60,
        "schedBegin": _hhmm(g.get("beginTime")),
        "schedEnd": _hhmm(g.get("endTime")),
        "raw": g,
    }


def _shape_device(d, groups):
    info = d.get("deviceInfo", {}) or {}
    sensors = []
    for s in info.get("sensors") or []:
        sensors.append({
            "type": s.get("sensorType"),
            "port": s.get("accessPort"),
            "value": round((s.get("sensorData") or 0) / 100, 2),
            "key": s.get("sensorKey"),
        })
    return {
        "devId": d.get("devId"),
        "name": d.get("devName"),
        "devType": d.get("devType"),
        "online": d.get("online"),
        "firmware": d.get("firmwareVersion"),
        "portCount": d.get("devPortCount"),
        "reading": decode_reading(info),
        "groups": [_shape_group(g) for g in groups],
        "sensors": sensors,
    }


async def handle_state(req):
    _require(req)
    aci = req.app["aci"]
    try:
        devices = await aci.devices()
        out = []
        for d in devices:
            groups = []
            if d.get("online"):
                try:
                    groups = await aci.get_groups(d.get("devId"))
                except Exception:
                    groups = []
            out.append(_shape_device(d, groups))
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)
    return web.json_response({"devices": out})


async def handle_port_settings(req):
    _require(req)
    aci = req.app["aci"]
    dev_id = req.match_info["dev_id"]
    port = int(req.match_info["port"])
    try:
        data = await aci.port_settings(dev_id, port)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)
    return web.json_response(data)


async def handle_control(req):
    _require(req)
    aci = req.app["aci"]
    body = await req.json()
    dev_id = body.get("devId")
    port = body.get("port")
    overrides = body.get("overrides") or {}
    if not dev_id or port is None or not overrides:
        return web.json_response(
            {"error": "need devId, port, overrides"}, status=400)
    # coerce everything to int — the API wants integers
    try:
        overrides = {k: int(v) for k, v in overrides.items()}
    except (TypeError, ValueError):
        return web.json_response(
            {"error": "override values must be integers"}, status=400)
    try:
        resp = await aci.set_port_mode(dev_id, int(port), overrides)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)
    return web.json_response({"ok": True, "msg": resp.get("msg")})


async def handle_group_control(req):
    _require(req)
    aci = req.app["aci"]
    body = await req.json()
    dev_id = body.get("devId")
    adv_id = body.get("advId")
    overrides = body.get("overrides") or {}
    if not dev_id or adv_id is None or not overrides:
        return web.json_response(
            {"error": "need devId, advId, overrides"}, status=400)
    try:
        overrides = {k: int(v) for k, v in overrides.items()}
    except (TypeError, ValueError):
        return web.json_response(
            {"error": "override values must be integers"}, status=400)
    try:
        groups = await aci.get_groups(dev_id)
        group = next((g for g in groups if g.get("advId") == int(adv_id)), None)
        if not group:
            return web.json_response({"error": "group not found"}, status=404)
        resp = await aci.update_group(group, overrides)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)
    return web.json_response({"ok": True, "msg": resp.get("msg")})


async def index(req):
    return web.FileResponse(WEB / "index.html",
                            headers={"Cache-Control": "no-store"})


async def on_cleanup(app):
    await app["aci"].close()


def make_app():
    email = os.environ.get("ACI_EMAIL")
    password = os.environ.get("ACI_PASSWORD")
    if not email or not password:
        raise SystemExit("Set ACI_EMAIL and ACI_PASSWORD (see aci.env.example)")
    app = web.Application()
    app["aci"] = ACInfinity(email, password)
    app.router.add_get("/api/state", handle_state)
    app.router.add_post("/api/groupcontrol", handle_group_control)
    app.router.add_get("/api/port/{dev_id}/{port}", handle_port_settings)
    app.router.add_post("/api/control", handle_control)
    app.router.add_get("/", index)
    app.router.add_static("/", WEB)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    web.run_app(make_app(), host="0.0.0.0", port=PORT)
