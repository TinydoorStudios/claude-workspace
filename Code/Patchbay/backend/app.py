"""Patchbay — patch sheet manager for the Q225, M32 and Wing.

Run:  ./run.sh      → http://localhost:8096
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from aiohttp import web

from .export_xlsx import build as build_xlsx
from .knowledge import Knowledge
from .render import render, to_pdf
from .schema import flatten, migrate
from .sheet import analyze, apply_wizard, blank_input, blank_output, from_brief, guess_section, new_sheet
from .store import Store

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
PORT = int(os.environ.get("PATCHBAY_PORT", "8096"))
HOST = os.environ.get("PATCHBAY_HOST")  # the .app pins this to 127.0.0.1

KB = Knowledge()
STORE = Store()


def _safe_filename(name: str, ext: str) -> str:
    base = re.sub(r"[^A-Za-z0-9 _.-]+", "", name or "patch sheet").strip() or "patch sheet"
    return f"{base} - Patch Sheet.{ext}"


def _console_for(sheet: dict, index: int = 0) -> dict:
    consoles = sheet.get("consoles") or []
    preset = consoles[min(index, len(consoles) - 1)].get("preset") if consoles else sheet.get("console")
    c = KB.console(preset or "q225")
    return {
        **c,
        "input_ports": KB.ports(c["id"], "in"),
        "output_ports": KB.ports(c["id"], "out"),
    }


def _analysis(sheet: dict) -> list[dict]:
    """One analysis block per console, so the UI can show problems per desk."""
    out = []
    for i, con in enumerate(sheet.get("consoles") or [{}]):
        console = _console_for(sheet, i)
        block = analyze(flatten(sheet, i), console)
        block["console_id"] = con.get("id")
        block["console_label"] = console["label"]
        out.append(block)
    return out


# ---------------------------------------------------------------- API
async def api_bootstrap(request: web.Request) -> web.Response:
    return web.json_response(KB.bootstrap())


async def api_list(request: web.Request) -> web.Response:
    return web.json_response({"sheets": STORE.list()})


async def api_create(request: web.Request) -> web.Response:
    body = await request.json()
    console_id = body.get("console") or "q225"
    console = KB.console(console_id)
    wizard = body.get("wizard")
    if body.get("from_template"):
        sheet = STORE.duplicate(
            body["from_template"],
            body.get("name") or "Untitled",
            kind=body.get("kind") or "event",
        )
        if wizard:
            sheet.setdefault("location", {})
            sheet.setdefault("console_info", {})
            sheet.setdefault("stageboxes", [])
            sheet = STORE.save(sheet["id"], apply_wizard(sheet, wizard), bump=False)
        return web.json_response(sheet)
    venue = body.get("venue") or ""
    venue_label = next((v["label"] for v in KB.venues if v["id"] == venue), body.get("venue_label", ""))
    sheet = new_sheet(
        name=body.get("name") or "Untitled rig",
        console=console_id,
        venue=venue,
        venue_label=venue_label,
        kind=body.get("kind") or "install",
        bus_seed=console["bus_seed"],
        channels=int(body.get("channels") or 32),
    )
    if wizard:
        apply_wizard(sheet, wizard)
    return web.json_response(STORE.create(sheet))


async def api_get(request: web.Request) -> web.Response:
    sheet_id = request.match_info["id"]
    if not STORE.exists(sheet_id):
        raise web.HTTPNotFound()
    sheet = STORE.get(sheet_id)
    blocks = _analysis(sheet)
    return web.json_response({"sheet": sheet, "analysis": blocks[0], "analyses": blocks})


async def api_save(request: web.Request) -> web.Response:
    sheet_id = request.match_info["id"]
    body = await request.json()
    sheet = migrate(body["sheet"])
    if STORE.exists(sheet_id) and STORE.get(sheet_id).get("locked") and sheet.get("locked", True):
        # Locked house template: refuse the write rather than let a show drift the rig.
        return web.json_response({"error": "sheet is locked", "locked": True}, status=423)
    saved = STORE.save(sheet_id, sheet, bump=bool(body.get("bump", True)))
    blocks = _analysis(saved)
    return web.json_response({"sheet": saved, "analysis": blocks[0], "analyses": blocks})


async def api_delete(request: web.Request) -> web.Response:
    STORE.delete(request.match_info["id"])
    return web.json_response({"ok": True})


async def api_duplicate(request: web.Request) -> web.Response:
    body = await request.json()
    sheet = STORE.duplicate(request.match_info["id"], body.get("name") or "Copy", body.get("kind"))
    return web.json_response(sheet)


async def api_lock(request: web.Request) -> web.Response:
    """Flip a sheet's lock. The only write allowed on a locked sheet."""
    sheet_id = request.match_info["id"]
    body = await request.json()
    sheet = STORE.get(sheet_id)
    sheet["locked"] = bool(body.get("locked"))
    saved = STORE.save(sheet_id, sheet, bump=False)
    return web.json_response({"sheet": saved, "analyses": _analysis(saved)})


async def api_revisions(request: web.Request) -> web.Response:
    return web.json_response({"revisions": STORE.revisions(request.match_info["id"])})


async def api_restore(request: web.Request) -> web.Response:
    sheet_id = request.match_info["id"]
    body = await request.json()
    sheet = migrate(STORE.restore(sheet_id, body["file"]))
    blocks = _analysis(sheet)
    return web.json_response({"sheet": sheet, "analysis": blocks[0], "analyses": blocks})


async def api_import_brief(request: web.Request) -> web.Response:
    body = await request.json()
    brief = body["brief"]
    console_id = body.get("console") or "q225"
    console = KB.console(console_id)
    venue_label = next((v["label"] for v in KB.venues if v["id"] == brief.get("venue")), "")
    sheet = from_brief(brief, console_id, venue_label, console["bus_seed"])
    return web.json_response(STORE.create(sheet))


async def api_guess(request: web.Request) -> web.Response:
    """Mic lookup + section guess for a row the engineer is typing."""
    body = await request.json()
    mic = KB.mic(body.get("mic", ""))
    return web.json_response(
        {
            "mic": mic,
            "section": guess_section(body.get("name", ""), body.get("instrument", "")),
        }
    )


# ------------------------------------------------------------ exports
def _doc(sheet_id: str):
    sheet = STORE.get(sheet_id)
    console = _console_for(sheet)
    flat = flatten(sheet)
    return sheet, console, render(flat, console, analyze(flat, console))


async def export_html(request: web.Request) -> web.Response:
    _s, _c, doc = _doc(request.match_info["id"])
    return web.Response(text=doc, content_type="text/html")


async def export_pdf(request: web.Request) -> web.Response:
    sheet, _c, doc = _doc(request.match_info["id"])
    pdf = to_pdf(doc)
    if pdf is None:
        # weasyprint isn't installed here — hand back the print-ready HTML and
        # let the browser make the PDF.
        return web.Response(
            status=409,
            text=json.dumps({"error": "weasyprint not installed", "html_url": f"/api/sheets/{sheet['id']}/export.html"}),
            content_type="application/json",
        )
    return web.Response(
        body=pdf,
        content_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(sheet["name"], "pdf")}"'},
    )


async def export_xlsx(request: web.Request) -> web.Response:
    sheet_id = request.match_info["id"]
    sheet = STORE.get(sheet_id)
    data = build_xlsx(flatten(sheet), _console_for(sheet))
    return web.Response(
        body=data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(sheet["name"], "xlsx")}"'},
    )


async def export_json(request: web.Request) -> web.Response:
    sheet = STORE.get(request.match_info["id"])
    return web.Response(
        body=json.dumps(sheet, indent=1).encode(),
        content_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(sheet["name"], "json")}"'},
    )


async def health(request: web.Request) -> web.Response:
    return web.json_response({"ok": True, "sheets": len(STORE.list())})


async def index(request: web.Request) -> web.Response:
    return web.FileResponse(WEB / "index.html")


def make_app() -> web.Application:
    app = web.Application(client_max_size=32 * 1024 * 1024)
    app.add_routes(
        [
            web.get("/", index),
            web.get("/health", health),
            web.get("/api/bootstrap", api_bootstrap),
            web.get("/api/sheets", api_list),
            web.post("/api/sheets", api_create),
            web.post("/api/import/brief", api_import_brief),
            web.post("/api/guess", api_guess),
            web.get("/api/sheets/{id}", api_get),
            web.put("/api/sheets/{id}", api_save),
            web.delete("/api/sheets/{id}", api_delete),
            web.post("/api/sheets/{id}/duplicate", api_duplicate),
            web.post("/api/sheets/{id}/lock", api_lock),
            web.get("/api/sheets/{id}/revisions", api_revisions),
            web.post("/api/sheets/{id}/restore", api_restore),
            web.get("/api/sheets/{id}/export.html", export_html),
            web.get("/api/sheets/{id}/export.pdf", export_pdf),
            web.get("/api/sheets/{id}/export.xlsx", export_xlsx),
            web.get("/api/sheets/{id}/export.json", export_json),
            web.static("/static", WEB),
        ]
    )
    return app


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(f"Patchbay → http://localhost:{PORT}", flush=True)
    web.run_app(make_app(), host=HOST, port=PORT, print=None,
                access_log_format='%r %s %b')
