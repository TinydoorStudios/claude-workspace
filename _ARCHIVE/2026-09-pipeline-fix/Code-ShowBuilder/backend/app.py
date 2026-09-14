"""
app.py — ShowBuilder aiohttp server (facts-only brief capture).

ShowBuilder is a DATA-CAPTURE tool. It captures the input list + show metadata
and free-text notes, and exports a facts-only <Show>.brief.json. It NEVER
computes EQ, writes a .ses, or writes the FOH Channel Processing .md — all of
that is produced downstream by the `show-deep-build` skill, which researches the
artist and every source. See docs/HANDOFF.md.

  GET  /                 wizard UI
  GET  /api/bootstrap    venues, instruments, mics, genres, venue defaults
  POST /api/brief        build a Brief from the wizard payload, write
                         <Show>.brief.json into the show folder (Mac), or return
                         it as a download (package role with no audio_root)
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime
from pathlib import Path

from aiohttp import web

from .knowledge import Knowledge
from .brief import Brief, BriefChannel, APP_VERSION

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
INBOX = ROOT / "inbox"          # package role: server-side copy of every export


def load_config():
    """config.json overlaid with SHOWBUILDER_* env vars (env wins). On the
    package instance, ROLE=package and AUDIO_ROOT is unset: it returns the brief
    as a download instead of writing it to a show folder."""
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    env = os.environ
    if env.get("SHOWBUILDER_ROLE"):
        cfg["role"] = env["SHOWBUILDER_ROLE"]
    if env.get("SHOWBUILDER_PORT"):
        cfg["port"] = int(env["SHOWBUILDER_PORT"])
    if env.get("SHOWBUILDER_HOST"):
        cfg["host"] = env["SHOWBUILDER_HOST"]
    if "SHOWBUILDER_AUDIO_ROOT" in env:
        cfg["audio_root"] = env["SHOWBUILDER_AUDIO_ROOT"] or None
    cfg["passcode"] = env.get("SHOWBUILDER_PASSCODE") or cfg.get("passcode") or ""
    # the brief is written to a show folder only when we have an audio_root
    cfg["write_enabled"] = bool(cfg.get("audio_root")) and cfg.get("role") != "package"
    return cfg


CONFIG = load_config()
KN = Knowledge(CONFIG)


# ── passcode gate ─────────────────────────────────────────────────────────────
# The auth cookie is an HMAC of passcode + a per-boot secret, so a leaked cookie
# dies on the next service restart instead of living forever.
BOOT_SECRET = secrets.token_hex(16)
_LOGIN_FAILS: dict[str, int] = {}   # client ip -> consecutive failures


def _auth_token():
    return hmac.new((CONFIG["passcode"] + BOOT_SECRET).encode(),
                    b"showbuilder", hashlib.sha256).hexdigest()


def _client_ip(request):
    return request.headers.get("CF-Connecting-IP") or request.remote or "?"


@web.middleware
async def auth_middleware(request, handler):
    if not CONFIG.get("passcode"):
        return await handler(request)            # no gate when no passcode set
    if request.path in ("/login", "/style.css", "/health") or request.path.startswith("/favicon"):
        return await handler(request)
    if request.cookies.get("sb_auth") == _auth_token():
        return await handler(request)
    if request.path.startswith("/api/"):
        return web.json_response({"error": "unauthorized"}, status=401)
    raise web.HTTPFound("/login")


LOGIN_HTML = """<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1"><title>ShowBuilder</title>
<link rel=stylesheet href=/style.css>
<div style="max-width:360px;margin:16vh auto;padding:1.6rem 1.5rem;background:#141e30;
 border:1px solid #26344a;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.35)">
<h2 style="margin:.1rem 0 .2rem;color:#fff">Show<span style="color:#4da3ff">Builder</span></h2>
<p style="color:#8fa1b8;margin:.2rem 0 1rem">Enter the passcode to continue.</p>
<form method=post action=/login>
<input name=passcode type=password autofocus placeholder="Passcode" style="width:100%;font-size:1rem">
<button class=primary style="margin-top:.9rem;width:100%;font-size:1rem">Enter</button>
%MSG%</form></div>"""


# ── brief assembly ────────────────────────────────────────────────────────────
def _section_for(spec_inst, payload_section):
    """Honor a section typed in the wizard; else derive it from the instrument.
    Never guesses EQ — section is just a grouping fact for the packet."""
    if payload_section:
        return payload_section.strip().upper()
    ikey = KN.match_instrument(spec_inst)
    inst = KN.instrument(ikey) if ikey else None
    return (inst or {}).get("section", "SPARE")


def _brief_from_payload(payload) -> Brief:
    venue_key = payload.get("venue", "memo")
    venue = KN.venue(venue_key) or {}
    brief = Brief(
        show_name=(payload.get("show_name") or "Untitled Show").strip(),
        artist=payload.get("artist", "").strip(),
        genre=(payload.get("genre") or "").strip(),
        venue=venue_key,
        venue_label=payload.get("venue_label") or venue.get("name", venue_key),
        console_label=payload.get("console_label") or venue.get("console_label", ""),
        show_date=payload.get("show_date") or Brief().show_date,
        foh_engineer=payload.get("foh_engineer") or CONFIG.get("default_foh_engineer", "Brian Lloyd"),
        mon_engineer=payload.get("mon_engineer") or "TBD",
        show_time=payload.get("show_time") or "TBD",
        rev=payload.get("rev") or CONFIG.get("default_rev", "Rev 1.0"),
        show_notes=(payload.get("show_notes") or ""),   # verbatim — no strip
    )
    for row in payload.get("channels", []):
        name = (row.get("name") or "").strip()
        instrument = (row.get("instrument") or "").strip()
        if not (name or instrument):
            continue
        # a true spare is omitted, not emitted blank
        if (name.upper() == "SPARE" or instrument.lower() == "spare") and not row.get("mic"):
            continue
        mic = (row.get("mic") or "").strip()
        mrec = KN.match_mic(mic) or {}
        ribbon = bool(row.get("ribbon", mrec.get("ribbon", False)))
        # phantom: honor an explicit wizard value, else the mic's default (never on a ribbon)
        phantom = bool(row.get("phantom", mrec.get("phantom", False))) and not ribbon
        ch = row.get("ch")
        brief.channels.append(BriefChannel(
            ch=int(ch) if str(ch).strip().isdigit() else None,
            name=name,
            instrument=instrument,
            mic=mic,
            section=_section_for(instrument or name, row.get("section")),
            phantom=phantom,
            ribbon=ribbon,
            stand=(row.get("stand") or "—").strip() or "—",
            patch=(row.get("patch") or "").strip(),
            notes=(row.get("notes") or ""),             # verbatim — no strip
        ))
    _inject_crowd_rig(brief)
    return brief


def _inject_crowd_rig(brief: Brief):
    """Append the venue crowd-mic rig as facts-only channels (ch=None, no EQ).
    Memo always; others only if defined. These mics are physically patched every
    show — the deep build decides their treatment."""
    venue = KN.venue(brief.venue) or {}
    rig = venue.get("crowd_rig") or []
    if not rig or any(c.is_crowd for c in brief.channels):
        return
    for entry in rig:
        brief.channels.append(BriefChannel(
            ch=None, name=entry["name"], instrument="crowd", mic=entry["mic"],
            section="AMBIENT", phantom=True, stand="—",
            notes="Crowd rig — always patched at this venue; blank CH, treatment set downstream.",
            is_crowd=True))


# ── routes ──────────────────────────────────────────────────────────────────
async def index(request):
    return web.FileResponse(WEB / "index.html")


async def static_file(request):
    name = request.match_info["name"]
    p = WEB / name
    if not p.exists() or p.is_dir():
        raise web.HTTPNotFound()
    return web.FileResponse(p)


async def bootstrap(request):
    defaults = {v["key"]: KN.venue_defaults(v["key"]) for v in KN.venue_list()
                if KN.venue_defaults(v["key"])["channels"]}
    return web.json_response({
        "venues": KN.venue_list(),
        "instruments": KN.instrument_options(),
        "mics": KN.mic_options(),
        "genres": [{"key": k, "note": v.get("note", ""), "aliases": v.get("aliases", [])}
                   for k, v in KN.genres().items()],
        "defaults": defaults,
        "config": {"role": CONFIG.get("role", "mac"),
                   "write_enabled": CONFIG.get("write_enabled", True)},
    })


async def brief_route(request):
    payload = await request.json()
    brief = _brief_from_payload(payload)
    data = brief.to_dict()
    fn = f"{brief.slug()}.brief.json"

    # package role / no audio_root: keep a server-side copy in the inbox, then
    # hand the brief back as a download (the inbox is what the Mac pulls from)
    if not CONFIG.get("write_enabled"):
        INBOX.mkdir(exist_ok=True)
        (INBOX / f"{brief.show_date}_{fn}").write_text(brief.json(), encoding="utf-8")
        return web.Response(
            text=brief.json(), content_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{fn}"'})

    # Mac: write the brief into the show folder, next to where the skill will build
    folder = KN.show_folder(brief.venue, brief.folder_name())
    if folder is None:
        return web.json_response({"error": "No show folder (venue/audio_root not resolvable)."},
                                 status=400)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / fn
    if path.exists() and not payload.get("overwrite"):
        return web.json_response({
            "error": "exists", "exists": True, "path": str(path),
            "message": f"{fn} already exists in the show folder."}, status=409)
    brief.save(path)
    return web.json_response({
        "ok": True,
        "folder": str(folder),
        "path": str(path),
        "filename": fn,
        "brief": data,
        "channel_count": len([c for c in brief.channels if not c.is_crowd]),
        "crowd_count": len([c for c in brief.channels if c.is_crowd]),
        "next": f'In Cowork: "deep build {brief.show_name}" — the show-deep-build '
                f"skill reads this brief and produces the EQ, paperwork, and .ses.",
    })


async def login_get(request):
    return web.Response(text=LOGIN_HTML.replace("%MSG%", ""), content_type="text/html")


async def login_post(request):
    data = await request.post()
    ip = _client_ip(request)
    if CONFIG.get("passcode") and data.get("passcode", "") == CONFIG["passcode"]:
        _LOGIN_FAILS.pop(ip, None)
        r = web.HTTPFound("/")
        r.set_cookie("sb_auth", _auth_token(), httponly=True, samesite="Lax",
                     max_age=86400 * 7,
                     secure=CONFIG.get("role") == "package")
        return r
    fails = _LOGIN_FAILS[ip] = _LOGIN_FAILS.get(ip, 0) + 1
    await asyncio.sleep(min(5, fails))           # slow brute-force attempts
    msg = '<p style="color:#9B2222;margin-top:.6rem">Wrong passcode.</p>'
    return web.Response(text=LOGIN_HTML.replace("%MSG%", msg),
                        content_type="text/html", status=401)


# ── inbox + health ───────────────────────────────────────────────────────────
_SAFE_BRIEF_FN = re.compile(r"^[A-Za-z0-9 ._\-]+\.brief\.json$")


async def briefs_list(request):
    files = sorted(INBOX.glob("*.brief.json"), key=lambda p: p.stat().st_mtime,
                   reverse=True) if INBOX.exists() else []
    return web.json_response({"briefs": [
        {"name": p.name, "size": p.stat().st_size,
         "mtime": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}
        for p in files]})


async def briefs_get(request):
    name = request.match_info["name"]
    if not _SAFE_BRIEF_FN.match(name) or "/" in name or ".." in name:
        raise web.HTTPNotFound()
    p = INBOX / name
    if not p.is_file():
        raise web.HTTPNotFound()
    return web.FileResponse(p, headers={
        "Content-Disposition": f'attachment; filename="{name}"',
        "Content-Type": "application/json"})


async def health(request):
    return web.json_response({"ok": True, "app": "showbuilder",
                              "role": CONFIG.get("role", "mac"),
                              "version": APP_VERSION})


def make_app():
    app = web.Application(client_max_size=8 * 1024 * 1024,
                          middlewares=[auth_middleware])
    app.add_routes([
        web.get("/login", login_get),
        web.post("/login", login_post),
        web.get("/health", health),
        web.get("/", index),
        web.get("/api/bootstrap", bootstrap),
        web.post("/api/brief", brief_route),
        web.get("/api/briefs", briefs_list),
        web.get("/api/briefs/{name}", briefs_get),
        web.get("/{name}", static_file),
    ])
    return app


if __name__ == "__main__":
    app = make_app()
    print(f"ShowBuilder on http://{CONFIG.get('host','0.0.0.0')}:{CONFIG.get('port',8095)}  "
          f"(role={CONFIG.get('role','mac')}, write={CONFIG.get('write_enabled')})")
    web.run_app(app, host=CONFIG.get("host", "0.0.0.0"), port=CONFIG.get("port", 8095))
