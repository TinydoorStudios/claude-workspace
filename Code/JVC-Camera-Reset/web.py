#!/usr/bin/env python3
"""One-button web front-end for the JVC camera reset.

Serves a small page (a big REBOOT button + live status) on 127.0.0.1:8092.
The landing nginx proxies it at https://tinydoorstudios.com/cameras/ behind
basic auth. Clicking REBOOT runs `reset_cameras.py --method video` on all three
cameras in the background (the controller's video off/on -> reinitialise).

Stdlib only -- no extra dependencies in the venv.
"""
import json
import os
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(HERE, ".venv", "bin", "python")
TOOL = os.path.join(HERE, "reset_cameras.py")
LOG_DIR = os.path.join(HERE, "logs")
LISTEN = ("127.0.0.1", 8092)

# Password-only gate. Replaces the nginx basic-auth (which always forced a
# username box). One password field; correct entry sets a cookie. Default
# matches the other Tiny Door Studios service gates.
PASSCODE = os.environ.get("JVC_PASSCODE", "lockdown")
COOKIE = "cams_gate"

sys.path.insert(0, HERE)
import reset_cameras as rc  # noqa: E402

PAGE = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Cameras — Tiny Door Studios</title><style>
:root{--bg:#0f1115;--card:#1a1d24;--ink:#e9edf3;--mut:#8b93a3;--accent:#2E6DA4;--ok:#3ecf8e;--bad:#e0556b;--warn:#f3c969}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
background:radial-gradient(1200px 600px at 50% -10%,#1b2230,#0f1115);color:var(--ink);min-height:100vh}
.wrap{max-width:560px;margin:0 auto;padding:44px 22px 70px}
h1{font-size:26px;margin:0 0 4px}.sub{color:var(--mut);margin:0 0 28px;font-size:14px}
.cams{display:grid;gap:10px;margin:0 0 28px}
.cam{display:flex;align-items:center;gap:12px;background:var(--card);border:1px solid #262b36;border-radius:12px;padding:14px 16px}
.dot{width:11px;height:11px;border-radius:50%;background:#555;flex:none}
.dot.ok{background:var(--ok)}.dot.bad{background:var(--bad)}.dot.warn{background:var(--warn)}
.cam .nm{font-weight:600}.cam .st{color:var(--mut);font-size:13px;margin-left:auto}
button{font:inherit;border:0;border-radius:14px;cursor:pointer}
.reboot{width:100%;padding:20px;font-size:18px;font-weight:700;color:#fff;background:var(--bad);letter-spacing:.3px}
.reboot:hover{filter:brightness(1.08)}.reboot:disabled{opacity:.5;cursor:default}
.ghost{margin-top:12px;width:100%;padding:12px;background:#222732;color:var(--ink);font-size:14px}
.msg{margin-top:18px;padding:14px 16px;border-radius:12px;font-size:14px;line-height:1.5;display:none}
.msg.show{display:block}.msg.go{background:#10263a;border:1px solid #1d4e7a}
.foot{color:#5b6373;font-size:12px;margin-top:40px;text-align:center}
.spin{display:inline-block;width:14px;height:14px;border:2px solid #6fb4ef;border-top-color:transparent;border-radius:50%;animation:s .8s linear infinite;vertical-align:-2px;margin-right:6px}
@keyframes s{to{transform:rotate(360deg)}}
</style></head><body><div class=wrap>
<h1>📷 Cameras</h1><p class=sub>JVC KY-PZ100 PTZ — Memorial Hall</p>
<div class=cams id=cams><div class=cam><span class="dot"></span><span class=nm>Loading…</span></div></div>
<button class=reboot id=go>⟳ Reboot all cameras</button>
<button class=ghost id=refresh>Refresh status</button>
<div class="msg" id=msg></div>
<div class=foot>tinydoorstudios.com · Nyquist</div>
</div><script>
const $=s=>document.querySelector(s);
async function loadStatus(){
  const box=$('#cams');
  try{
    const r=await fetch('status',{cache:'no-store'});const cams=await r.json();
    box.innerHTML=cams.map(c=>{
      let cls='warn',st=c.error||'';
      if(c.ok){cls=(c.power==='On')?'ok':'warn';st='video '+(c.power||'?')+' · '+(c.streaming||'');}
      else{cls='bad';st='not responding';}
      return `<div class=cam><span class="dot ${cls}"></span><span class=nm>${c.name}</span><span class=st>${st}</span></div>`;
    }).join('');
  }catch(e){box.innerHTML='<div class=cam><span class="dot bad"></span><span class=nm>status error</span></div>';}
}
$('#refresh').onclick=loadStatus;
$('#go').onclick=async()=>{
  if(!confirm('Reboot all 3 cameras now? Each will drop offline for ~45 seconds.'))return;
  $('#go').disabled=true;
  const m=$('#msg');m.className='msg show go';
  m.innerHTML='<span class=spin></span>Rebooting all cameras… they will go offline and come back in about a minute.';
  try{await fetch('reboot',{method:'POST'});}catch(e){}
  let n=0;const iv=setInterval(()=>{loadStatus();if(++n>8){clearInterval(iv);$('#go').disabled=false;
    m.innerHTML='Done. If a camera still shows offline, give it another minute or press Refresh.';}},10000);
};
loadStatus();
</script></body></html>"""

LOGIN = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Cameras — Tiny Door Studios</title><style>
:root{{--bg:#0f1115;--card:#1a1d24;--ink:#e9edf3;--mut:#8b93a3;--accent:#2E6DA4;--bad:#e0556b}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
background:radial-gradient(1200px 600px at 50% -10%,#1b2230,#0f1115);color:var(--ink);min-height:100vh;
display:flex;align-items:center;justify-content:center}}
.box{{width:100%;max-width:340px;background:var(--card);border:1px solid #262b36;border-radius:16px;padding:30px 26px;margin:22px}}
h1{{font-size:21px;margin:0 0 4px}}.sub{{color:var(--mut);margin:0 0 22px;font-size:13px}}
input{{width:100%;padding:14px 14px;font-size:16px;border-radius:11px;border:1px solid #2c323e;
background:#11141a;color:var(--ink);margin:0 0 12px}}
button{{width:100%;padding:14px;font:inherit;font-weight:700;border:0;border-radius:11px;cursor:pointer;
color:#fff;background:var(--accent)}}
button:hover{{filter:brightness(1.08)}}
.err{{color:var(--bad);font-size:13px;margin:0 0 12px;min-height:16px}}
.foot{{color:#5b6373;font-size:12px;margin-top:22px;text-align:center}}
</style></head><body>
<form class=box method=post action=login>
<h1>📷 Cameras</h1><p class=sub>Memorial Hall PTZ control</p>
<div class=err>{err}</div>
<input type=password name=pc placeholder=Passcode autofocus autocomplete=current-password>
<button type=submit>Enter</button>
<div class=foot>tinydoorstudios.com · Nyquist</div>
</form></body></html>"""


def get_status():
    cfg = rc.load_config()
    cams = rc.build_cameras(cfg)
    def one(cam):
        try:
            st = cam.status()
            return {"name": cam.name, "ok": True, "power": st["power"],
                    "menu": st["menu"], "streaming": st["streaming"]}
        except Exception:
            return {"name": cam.name, "ok": False, "error": "offline"}
    with ThreadPoolExecutor(max_workers=len(cams) or 1) as ex:
        return list(ex.map(one, cams))


def launch_reboot(camera=None):
    os.makedirs(LOG_DIR, exist_ok=True)
    args = [PYTHON, TOOL, "--method", "video"]
    if camera:
        args += ["--camera", camera]
    logf = open(os.path.join(LOG_DIR, "reboot.log"), "a")
    subprocess.Popen(args, stdout=logf, stderr=subprocess.STDOUT, cwd=HERE)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json", extra=None):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or []):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _authed(self):
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE and v == PASSCODE:
                return True
        return False

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if not self._authed():
            if path == "/":
                self._send(200, LOGIN.format(err=""), "text/html; charset=utf-8")
            else:
                self._send(401, '{"error":"locked"}')
            return
        if path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif path == "/status":
            self._send(200, json.dumps(get_status()))
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/login":
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length).decode("utf-8", "replace")
            given = urllib.parse.parse_qs(body).get("pc", [""])[0]
            if given == PASSCODE:
                cookie = "%s=%s; Path=/cameras; HttpOnly; SameSite=Lax; Max-Age=2592000" % (COOKIE, PASSCODE)
                self._send(303, "", "text/html", extra=[("Location", "./"), ("Set-Cookie", cookie)])
            else:
                self._send(401, LOGIN.format(err="Wrong passcode."), "text/html; charset=utf-8")
            return
        if not self._authed():
            self._send(401, '{"error":"locked"}')
            return
        if path == "/reboot":
            launch_reboot()
            self._send(200, '{"ok":true,"msg":"reboot started"}')
        else:
            self._send(404, '{"error":"not found"}')

    def log_message(self, *a):
        pass  # quiet


if __name__ == "__main__":
    srv = ThreadingHTTPServer(LISTEN, Handler)
    print(f"jvc-cameras-web on http://{LISTEN[0]}:{LISTEN[1]}", flush=True)
    srv.serve_forever()
