#!/usr/bin/env python3
"""
server.py — always-on HTTP front end for the roof-display failsafe.

Runs on the n8n VM (192.168.200.84), same LAN subnet as the DMP-8000
(192.168.200.121). Because it does NOT depend on the Show Control PC, it can
switch the roof to the Carbonite/DeckLink feed even when that PC is off or
won't boot.

Both trigger paths hit this one endpoint:
  - TDS landing dashboard button  -> POST/GET  /fire/switcher?pass=lockdown
  - Bitfocus Companion (Generic HTTP) -> same URL

Endpoints:
  GET  /                       -> health + config summary (no secrets)
  GET  /fire/{cue}?pass=...     -> fire a named cue (Companion-friendly)
  POST /fire/{cue}             -> fire a named cue (pass in body/header/query)

Config: config.json next to this file (see config.example.json).
Passcode convention matches Brian's other services ("lockdown").
"""

from __future__ import annotations
import json
import os
import time
from aiohttp import web

import vdcp

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get("ROOF_CONFIG", os.path.join(HERE, "config.json"))


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _check_pass(request: web.Request, cfg: dict) -> bool:
    want = str(cfg.get("passcode", ""))
    if not want:
        return True
    given = (
        request.query.get("pass")
        or request.headers.get("X-Passcode")
        or request.rel_url.query.get("passcode")
    )
    if given is None and request.can_read_body:
        # best-effort: allow pass in a form/query body without blocking
        given = request.query.get("pass")
    return given == want


async def handle_root(request: web.Request) -> web.Response:
    cfg = request.app["cfg"]
    safe = {
        "service": "roof-failsafe",
        "dmp_host": cfg.get("dmp_host"),
        "vdcp_port": cfg.get("vdcp_port"),
        "transport": cfg.get("transport"),
        "signal_port": cfg.get("signal_port"),
        "cues": list((cfg.get("cues") or {}).keys()),
        "configured": bool(cfg.get("vdcp_port")) and bool(cfg.get("cues")),
    }
    return web.json_response({"ok": True, "info": safe})


async def handle_fire(request: web.Request) -> web.Response:
    cfg = request.app["cfg"]
    cue = request.match_info["cue"]

    if not _check_pass(request, cfg):
        return web.json_response({"ok": False, "error": "bad passcode"}, status=403)

    cues = cfg.get("cues") or {}
    if cue not in cues:
        return web.json_response(
            {"ok": False, "error": f"unknown cue {cue!r}", "known": list(cues)},
            status=404,
        )

    port = cfg.get("vdcp_port")
    if not port:
        return web.json_response(
            {"ok": False, "error": "vdcp_port not set in config.json (get it from the DMP)"},
            status=503,
        )

    log_lines: list[str] = []
    ok = vdcp.fire_clip(
        host=cfg["dmp_host"],
        port=int(port),
        clip_id=str(cues[cue]),
        signal_port=int(cfg.get("signal_port", 1)),
        udp=(cfg.get("transport", "tcp").lower() == "udp"),
        open_first=bool(cfg.get("open_port_first", False)),
        id_mode=cfg.get("id_mode", "fixed8"),
        read_ack=not (cfg.get("transport", "tcp").lower() == "udp"),
        log=log_lines.append,
    )
    result = {
        "ok": ok,
        "cue": cue,
        "clip_id": cues[cue],
        "dmp": f"{cfg['dmp_host']}:{port}",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trace": log_lines,
    }
    print(json.dumps(result))  # journald / logs
    return web.json_response(result, status=200 if ok else 502)


def build_app() -> web.Application:
    app = web.Application()
    app["cfg"] = load_config()
    app.router.add_get("/", handle_root)
    app.router.add_get("/fire/{cue}", handle_fire)
    app.router.add_post("/fire/{cue}", handle_fire)
    return app


if __name__ == "__main__":
    cfg = load_config()
    listen = int(cfg.get("listen_port", 8099))
    print(f"[roof-failsafe] listening on :{listen}, target DMP "
          f"{cfg.get('dmp_host')}:{cfg.get('vdcp_port')} ({cfg.get('transport')})")
    web.run_app(build_app(), host="0.0.0.0", port=listen)
