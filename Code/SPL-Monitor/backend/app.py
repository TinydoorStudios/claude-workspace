"""SPL-Monitor backend.

aiohttp app that runs a data source (simulator or real Smaart), maintains the
rolling LAeq / traffic-light / prediction state, logs to CSV, and serves the
dashboard while pushing live state to browsers over a WebSocket.

Run from the project root:

    ./.venv/bin/python -m backend.app
"""

import asyncio
import datetime
import json
import os
import pathlib
import time

import aiohttp
from aiohttp import WSMsgType, web

from .daily import DailySummary
from .logging_csv import SessionLogger
from .processing import Monitor
from .showinfo import ShowInfoTracker
from .sources import make_source

BASE = pathlib.Path(__file__).resolve().parent.parent
WEB = BASE / "web"

# If no measurement frame has arrived in this many seconds, treat the rig as
# "not logging" and the dashboard shows the standby screen. Rig pushes ~every 3s.
STALE_SECONDS = 9.0


class Hub:
    def __init__(self):
        self.clients = set()

    async def broadcast(self, obj):
        if not self.clients:
            return
        data = json.dumps(obj)
        dead = []
        for ws in self.clients:
            try:
                await ws.send_str(data)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for d in dead:
            self.clients.discard(d)


@web.middleware
async def no_cache(request, handler):
    """Always serve fresh — a live dashboard must never show a stale cached page."""
    resp = await handler(request)
    try:
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    except (AttributeError, TypeError):
        pass
    return resp


async def index(request):
    return web.FileResponse(WEB / "index.html")


async def reset_strikes_handler(request):
    """Reset the violation strike counter — requires the configured passcode."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "bad request"}, status=400)
    code = str(body.get("passcode", ""))
    expected = str(request.app["config"].get("resetPasscode", ""))
    if not expected or code != expected:
        return web.json_response({"ok": False, "error": "incorrect"}, status=403)
    monitor = request.app["monitor"]
    monitor.vtracker.reset()
    # broadcast the cleared state so every open browser updates instantly
    vstate = monitor.vtracker.state()
    if monitor.latest:
        await request.app["hub"].broadcast({"type": "state", **monitor.latest, "violations": vstate})
    print("[reset] strike counter cleared by authenticated request", flush=True)
    return web.json_response({"ok": True})


async def toggle_alerts_handler(request):
    """Runtime on/off switch for Slack violation alerts. Turning alerts OFF
    requires the reset passcode (so nobody silently kills alerting mid-show);
    turning them back ON is free. Console/webhook logging still records
    violations either way; this only gates the Slack POST."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "bad request"}, status=400)
    enabled = bool(body.get("enabled"))
    if not enabled:
        code = str(body.get("passcode", ""))
        expected = str(request.app["config"].get("resetPasscode", ""))
        if not expected or code != expected:
            return web.json_response({"ok": False, "error": "incorrect"}, status=403)
    request.app["alerts_enabled"] = enabled
    await request.app["hub"].broadcast({"type": "alertsToggle", "enabled": enabled})
    print(f"[alerts] Slack alerts {'enabled' if enabled else 'disabled'}", flush=True)
    return web.json_response({"ok": True, "enabled": enabled})


async def daily_handler(request):
    """Nightly roll-up for the n8n email. ?date=YYYY-MM-DD (default = current report day)."""
    return web.json_response(request.app["daily"].summary(request.query.get("date")))


async def show_info_handler(request):
    return web.json_response(request.app["showinfo"].current())


async def daily_email_handler(request):
    """Bundled nightly email: subject/html + CSV + PDF (base64) for the n8n Gmail node.
    PDF rendering is blocking (matplotlib) so it runs in a thread."""
    day = request.query.get("date")
    show_info = {}
    showinfo = request.app.get("showinfo")
    if showinfo and showinfo.enabled:
        try:
            show_info = await showinfo.for_date(day)
        except Exception as e:  # noqa: BLE001
            print(f"[showinfo] email lookup failed: {e!r}", flush=True)
    loop = asyncio.get_event_loop()
    payload = await loop.run_in_executor(
        None, request.app["daily"].email_payload, day, show_info)
    return web.json_response(payload)


async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    app = request.app
    hub = app["hub"]
    monitor = app["monitor"]
    hub.clients.add(ws)

    await ws.send_str(json.dumps({
        "type": "hello",
        "venues": app["config"].get("venues", {}),
        "venue": monitor.venue,
        "shortSecs": monitor.short_secs,
        "longSecs": monitor.long_secs,
        "horizonSeconds": monitor.horizon,
        "alertsEnabled": app.get("alerts_enabled", True),
    }))
    if monitor.latest:
        await ws.send_str(json.dumps({"type": "state", **monitor.latest}))
    # backfill the rolling chart so a refresh keeps the full 6-min graph
    await ws.send_str(json.dumps({"type": "history", "points": monitor.history_points()}))
    await ws.send_str(json.dumps({"type": "showinfo", **app["showinfo"].current()}))
    live = (time.time() - app.get("last_frame_ts", 0.0)) < STALE_SECONDS
    await ws.send_str(json.dumps({"type": "status", "live": live}))

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            try:
                cmd = json.loads(msg.data)
            except (ValueError, TypeError):
                continue
            if cmd.get("type") == "setVenue":
                if monitor.set_venue(cmd.get("venue")):
                    await hub.broadcast({"type": "venue", "venue": monitor.venue})
    finally:
        hub.clients.discard(ws)
    return ws


def _compose_alert_text(p):
    v = p.get("venue", "")
    if p.get("kind") == "strike":
        return (f":red_circle: SPL violation #{p['violationNumber']} — {v}. "
                f"FOH {p['metric']} hit {p['level']} dBA (limit {p['threshold']}). "
                f"Strike {p['count']} — alerting on every violation from here.")
    return (f":stopwatch: SPL violation #{p['violationNumber']} — {v} — over 1 minute. "
            f"FOH still above {p['threshold']} dBA at {p['level']} ({p['elapsedSec']}s and counting).")


async def send_alert(app, payload):
    payload = {
        **payload,
        "venue": app["monitor"].venue,
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    payload["text"] = _compose_alert_text(payload)
    print(f"[alert] {payload['text']}", flush=True)
    if not app.get("alerts_enabled", True):
        print("[alert] Slack alerts disabled — not posting", flush=True)
        return
    url = (app["config"].get("violations", {}) or {}).get("alertWebhookUrl")
    if not url:
        return  # no webhook configured yet — logged only
    try:
        async with aiohttp.ClientSession() as s:
            await s.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10))
    except Exception as e:  # noqa: BLE001
        print(f"[alert] webhook post failed: {e!r}", flush=True)


async def run_source(app):
    monitor = app["monitor"]
    hub = app["hub"]
    logger = app["logger"]
    source = app["source"]
    try:
        async for frame in source.frames():
            app["last_frame_ts"] = time.time()
            state = monitor.process(frame)
            for alert in monitor.vtracker.take_alerts():
                asyncio.create_task(send_alert(app, alert))
            daily = app["daily"]
            daily.update(state)
            for cv in monitor.vtracker.take_completed():
                daily.record_violation(monitor.venue, cv)
            logger.update(state, frame.get("metrics"))
            await hub.broadcast({"type": "state", **state})
    except asyncio.CancelledError:
        pass


async def status_ticker(app):
    """Tell clients whether SPL logging is actually happening (frames arriving)."""
    hub = app["hub"]
    try:
        while True:
            await asyncio.sleep(2)
            live = (time.time() - app.get("last_frame_ts", 0.0)) < STALE_SECONDS
            await hub.broadcast({"type": "status", "live": live})
    except asyncio.CancelledError:
        pass


async def show_info_ticker(app):
    """Poll the Google Sheets show/engineer schedule and push changes to clients."""
    tracker = app["showinfo"]
    if not tracker.enabled:
        return
    try:
        while True:
            try:
                changed = await tracker.refresh()
                if changed:
                    await app["hub"].broadcast({"type": "showinfo", **tracker.current()})
            except Exception as e:  # noqa: BLE001
                print(f"[showinfo] refresh error: {e!r}", flush=True)
            await asyncio.sleep(tracker.refresh_seconds)
    except asyncio.CancelledError:
        pass


async def on_startup(app):
    app["last_frame_ts"] = 0.0
    app["source_task"] = asyncio.create_task(run_source(app))
    app["status_task"] = asyncio.create_task(status_ticker(app))
    app["showinfo_task"] = asyncio.create_task(show_info_ticker(app))


async def on_cleanup(app):
    for key in ("source_task", "status_task", "showinfo_task"):
        task = app.get(key)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    try:
        path = app["logger"].write_summary_xml()
        if path:
            print(f"[session] summary written: {path}")
    except Exception as e:  # noqa: BLE001
        print(f"[session] summary error: {e!r}")
    app["logger"].close()


def load_config():
    cfg = json.loads((BASE / "config.json").read_text())
    _apply_env_overrides(cfg)
    return cfg


def _apply_env_overrides(cfg):
    """Let env vars override config so the work IP / API password live outside the
    repo (set them in /etc/spl-monitor.env on the Pi)."""
    src = cfg.setdefault("source", {})
    sm = src.setdefault("smaart", {})
    e = os.environ.get
    if e("SPL_SOURCE"):
        src["type"] = e("SPL_SOURCE")
    if e("SMAART_HOST"):
        sm["host"] = e("SMAART_HOST")
    if e("SMAART_PORT"):
        sm["port"] = int(e("SMAART_PORT"))
    if e("SMAART_PASSWORD"):
        sm["password"] = e("SMAART_PASSWORD")
    if e("SMAART_DEVICE"):
        sm["deviceName"] = e("SMAART_DEVICE")
    if e("SMAART_CHANNEL"):
        sm["channelName"] = e("SMAART_CHANNEL")
    srv = cfg.setdefault("server", {})
    if e("SPL_HOST"):
        srv["host"] = e("SPL_HOST")
    if e("SPL_PORT"):
        srv["port"] = int(e("SPL_PORT"))
    if e("SPL_ALERT_WEBHOOK"):
        cfg.setdefault("violations", {})["alertWebhookUrl"] = e("SPL_ALERT_WEBHOOK")
    if e("RESET_PASSCODE"):
        cfg["resetPasscode"] = e("RESET_PASSCODE")


def build_app():
    cfg = load_config()
    app = web.Application(middlewares=[no_cache])
    app["config"] = cfg
    app["hub"] = Hub()
    app["monitor"] = Monitor(cfg)
    app["logger"] = SessionLogger(cfg, str(BASE))
    app["daily"] = DailySummary(cfg, str(BASE))
    app["showinfo"] = ShowInfoTracker(cfg)
    app["source"] = make_source(cfg)
    app["alerts_enabled"] = True
    app.router.add_get("/", index)
    app.router.add_post("/api/reset-strikes", reset_strikes_handler)
    app.router.add_post("/api/toggle-alerts", toggle_alerts_handler)
    app.router.add_get("/api/daily", daily_handler)
    app.router.add_get("/api/show-info", show_info_handler)
    app.router.add_get("/api/daily/email", daily_email_handler)
    app.router.add_get("/ws", ws_handler)
    app.router.add_static("/static/", WEB)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app, cfg


def main():
    app, cfg = build_app()
    srv = cfg.get("server", {})
    host = srv.get("host", "0.0.0.0")
    port = srv.get("port", 8080)
    print(f"[spl-monitor] source={cfg['source']['type']}  "
          f"dashboard=http://{host}:{port}/")
    web.run_app(app, host=host, port=port, print=None)


if __name__ == "__main__":
    main()
