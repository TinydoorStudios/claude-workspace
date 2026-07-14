#!/usr/bin/env python3
"""
JVC KY-PZ100 control-plane reset tool.

Background
----------
The KY-PZ100 web/control interface is single-client by design. JVC's own Web API
spec states "another client cannot connect while the first client is using the
API interface," and the session it issues expires every 30 seconds. Leaving a
control browser open holds that single slot and, over hours, wedges the control
plane so nothing else can take over until the camera's video pipeline is bounced.
That is the manual "turn video off, then back on at the controller" fix.

This tool reproduces that fix over the network using JVC's documented Web API
(digest auth -> SessionID cookie -> JSON command POST). It runs on the n8n VM,
which sits on the same LAN as the cameras. The Mac triggers it over Tailscale.

Reset methods
-------------
  stream  (default)  SetStreamingCtrl Off -> wait -> On. Documented + supported
                     on the PZ100. Bounces the IP stream / encode pipeline.
  reboot             SystemRequest "Reboot". A full reboot is the surest way to
                     clear a wedged control plane IF the firmware accepts it
                     (JVC documents SystemRequest for PZ200/400/510; the PZ100
                     may return CommandError -- test it, see DEPLOY.md).
  status             Probe only. Authenticate + read camera status. No change.

Exit code 0 if every targeted camera succeeded, 1 otherwise.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

try:
    import requests
    from requests.auth import HTTPDigestAuth
except ImportError:
    sys.stderr.write("ERROR: the 'requests' package is required. "
                     "pip install requests\n")
    sys.exit(2)

CONFIG_PATH = os.environ.get(
    "JVC_RESET_CONFIG",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
)


def log(msg):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {msg}", flush=True)


_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def _balance_brackets(text):
    """Append any closing brackets the JVC firmware left off (it drops the final
    one). String-aware, so braces inside quoted values are ignored."""
    stack = []
    in_str = esc = False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]" and stack:
            stack.pop()
    return text + "".join("}" if c == "{" else "]" for c in reversed(stack))


def loads_lenient(text):
    """Parse a JSON object from a sloppy KY-PZ100 response body.

    PZ100 firmware returns non-standard JSON: trailing bytes after the object, a
    trailing comma before a closing brace, AND it omits the final closing brace
    (e.g. '...,"100":0},}}}' -- one comma too many and one brace too few). Strict
    json.loads / requests.json() reject all of these. We try a clean decode
    first; if that fails we strip trailing commas, re-balance the brackets, and
    decode again. raw_decode also ignores any trailing junk after the object.
    """
    if text and text[0] == "﻿":
        text = text[1:]
    text = text.lstrip()
    dec = json.JSONDecoder()
    try:
        return dec.raw_decode(text)[0]
    except ValueError:
        repaired = _balance_brackets(_TRAILING_COMMA.sub(r"\1", text))
        return dec.raw_decode(repaired)[0]


class JvcCamera:
    """A single KY-PZ100 reachable over the JVC Web API."""

    def __init__(self, name, ip, username="", password="", web_port=80,
                 probe_timeout=4, command_timeout=10):
        self.name = name
        self.ip = ip
        self.username = username or ""
        self.password = password or ""
        self.base = f"http://{ip}:{web_port}" if web_port != 80 else f"http://{ip}"
        self.probe_timeout = probe_timeout
        self.command_timeout = command_timeout
        self._session = None
        self._session_id = None
        # The web UI command channel (cmd.cgi) uses a SEPARATE session created
        # via login.php -- the api.php SessionID is rejected by cmd.cgi.
        self._web_session = None
        self._web_session_id = None
        self._web_auth = None

    # -- transport ---------------------------------------------------------

    def authenticate(self, timeout=None):
        """GET /api.php with digest auth; capture the SessionID cookie.

        Digest auth is used ONLY for this handshake. Command POSTs then
        authenticate with the SessionID alone. Leaving digest on the POST makes
        some PZ100 firmwares (CAM 2/3 on the high ports) stall on the 401
        re-send and read-timeout, even though the auth itself succeeds.
        """
        timeout = timeout or self.command_timeout
        s = requests.Session()
        auth = HTTPDigestAuth(self.username, self.password) if self.username else None
        try:
            r = s.get(f"{self.base}/api.php", auth=auth, timeout=timeout)
        except requests.RequestException as e:
            raise RuntimeError(f"auth request failed: {e}")
        if r.status_code not in (200, 302):
            raise RuntimeError(f"auth returned HTTP {r.status_code}")
        session_id = s.cookies.get("SessionID")
        if not session_id:
            # Some firmwares put it only in the header on a 302.
            raw = r.headers.get("Set-Cookie", "")
            if "SessionID=" in raw:
                session_id = raw.split("SessionID=", 1)[1].split(";", 1)[0]
        if not session_id:
            raise RuntimeError("no SessionID returned by camera")
        self._session = s
        self._session_id = session_id
        return session_id

    def command(self, command, params=None, timeout=None):
        """POST one JSON command to /cgi-bin/api.cgi and return the parsed dict."""
        if self._session is None:
            self.authenticate()
        timeout = timeout or self.command_timeout
        payload = {"Request": {"Command": command, "SessionID": self._session_id}}
        if params:
            payload["Request"]["Params"] = params
        # The camera rejects any whitespace/newlines inside the command string.
        body = json.dumps(payload, separators=(",", ":"))
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base}/api.php",
        }
        try:
            r = self._session.post(f"{self.base}/cgi-bin/api.cgi", data=body,
                                   headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise RuntimeError(f"command {command} failed: {e}")
        if r.status_code != 200:
            raise RuntimeError(f"command {command} returned HTTP {r.status_code}")
        try:
            data = loads_lenient(r.text)
        except ValueError:
            raise RuntimeError(f"command {command} returned non-JSON: {r.text[:200]}")
        result = data.get("Response", {}).get("Result", "?")
        if result != "Success":
            raise RuntimeError(f"command {command} -> {result}")
        return data.get("Response", {}).get("Data", {})

    # -- web UI command channel (cmd.cgi) ----------------------------------

    def web_authenticate(self, timeout=None):
        """Log in via login.php to get a session that cmd.cgi accepts.

        cmd.cgi (the channel the web control page uses) only honours a session
        created through login.php -- the api.php SessionID returns SessionError.
        """
        timeout = timeout or self.command_timeout
        s = requests.Session()
        self._web_auth = HTTPDigestAuth(self.username, self.password) if self.username else None
        try:
            r = s.get(f"{self.base}/login.php", auth=self._web_auth, timeout=timeout)
        except requests.RequestException as e:
            raise RuntimeError(f"web login failed: {e}")
        sid = s.cookies.get("SessionID")
        if not sid:
            raise RuntimeError("login.php returned no SessionID")
        self._web_session = s
        self._web_session_id = sid
        return sid

    def web_command(self, command, params=None, timeout=None, tries=6):
        """POST a command to cgi-bin/cmd.cgi, retrying the transient
        SessionError / DualExeError the single-client control plane throws
        (the web UI itself retries these)."""
        if self._web_session is None:
            self.web_authenticate()
        timeout = timeout or self.command_timeout
        payload = {"Request": {"Command": command, "SessionID": self._web_session_id}}
        if params:
            payload["Request"]["Params"] = params
        body = json.dumps(payload, separators=(",", ":"))
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base}/",
        }
        last = "?"
        for _ in range(tries):
            r = self._web_session.post(f"{self.base}/cgi-bin/cmd.cgi", data=body,
                                       headers=headers, auth=self._web_auth,
                                       timeout=timeout)
            if r.status_code != 200:
                raise RuntimeError(f"web command {command} HTTP {r.status_code}")
            last = loads_lenient(r.text).get("Response", {}).get("Result", "?")
            if last == "Success":
                return last
            if last in ("SessionError", "DualExeError"):
                time.sleep(0.4)
                continue
            raise RuntimeError(f"web command {command} -> {last}")
        raise RuntimeError(f"web command {command} -> {last} (after {tries} tries)")

    def _webkey(self, key):
        """Send a System key press (e.g. VideoOutputOff) plus its commit.

        The web UI sends the key, then a Disptv/Set 'enter' to apply it."""
        self.web_command("SetWebKeyEvent", {"Kind": "System", "Key": key})
        self.web_command("SetWebKeyEvent", {"Kind": "Disptv", "Key": "Set"})

    # -- high level --------------------------------------------------------

    def status(self):
        """Return a short status dict, or raise if the camera can't be reached."""
        self.authenticate(timeout=self.probe_timeout)
        data = self.command("GetCamStatusMinimum", timeout=self.probe_timeout)
        cam = data.get("Camera", {})
        return {
            "power": cam.get("PowerStatus") or cam.get("VideoOutputStatus", "?"),
            "menu": cam.get("MenuStatus", "?"),
            "streaming": data.get("Streaming", {}).get("Status", "?"),
        }

    def is_reachable(self, attempts=2, gap=2):
        """True if the control plane answers a status probe (i.e. not wedged).

        Retries before giving up: these cameras occasionally throw a transient
        HTTP 500 / slow response, and we must NOT let a one-off blip make the
        --if-wedged auto-healer bounce a healthy (possibly live) camera.
        """
        for i in range(attempts):
            try:
                self.status()
                return True
            except Exception:
                # Re-auth from scratch on the next attempt.
                self._session = None
                self._session_id = None
                if i < attempts - 1:
                    time.sleep(gap)
        return False

    def reset_video(self, off_seconds):
        """Reproduce the controller's 'video off, then on' -- the real fix.

        Turning the video output back on makes the camera reinitialise its
        pipeline (it goes briefly unreachable, which is expected and is what
        clears a wedged control plane). Uses the web UI command channel.
        """
        self.web_authenticate()
        self._webkey("VideoOutputOff")
        log(f"[{self.name}] video output OFF; waiting {off_seconds}s")
        time.sleep(off_seconds)
        # Turn back on. The commit may not return if the camera starts
        # reinitialising immediately -- that's fine, the toggle already fired.
        self.web_command("SetWebKeyEvent", {"Kind": "System", "Key": "VideoOutputOn"})
        try:
            self.web_command("SetWebKeyEvent", {"Kind": "Disptv", "Key": "Set"},
                             timeout=8, tries=2)
        except RuntimeError:
            pass
        log(f"[{self.name}] video output ON (camera reinitialising)")

    def reset_stream(self, off_seconds):
        """Bounce the video/stream pipeline: streaming Off -> wait -> On."""
        self.command("SetStreamingCtrl", {"Streaming": "Off"})
        log(f"[{self.name}] streaming OFF; waiting {off_seconds}s")
        time.sleep(off_seconds)
        self.command("SetStreamingCtrl", {"Streaming": "On"})
        log(f"[{self.name}] streaming ON")

    def reset_reboot(self):
        """Ask the camera to reboot (may be rejected on PZ100 firmware)."""
        self.command("SystemRequest", {"Request": "Reboot"})
        log(f"[{self.name}] reboot requested")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.stderr.write(f"ERROR: config not found at {CONFIG_PATH}\n")
        sys.exit(2)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def build_cameras(cfg, only=None):
    cams = []
    for c in cfg.get("cameras", []):
        if not c.get("enabled", True):
            continue
        if only and c["name"].lower() != only.lower() and c["ip"] != only:
            continue
        cams.append(JvcCamera(
            name=c["name"],
            ip=c["ip"],
            username=c.get("username", cfg.get("username", "")),
            password=c.get("password", cfg.get("password", "")),
            web_port=c.get("web_port", cfg.get("web_port", 80)),
            probe_timeout=cfg.get("probe_timeout", 4),
            command_timeout=cfg.get("command_timeout", 10),
        ))
    return cams


def main():
    ap = argparse.ArgumentParser(description="Reset wedged JVC KY-PZ100 control plane.")
    ap.add_argument("--method", choices=["video", "stream", "reboot", "status"],
                    default="video",
                    help="reset method (default: video -- the real video off/on fix)")
    ap.add_argument("--camera", help="act on one camera only (name or IP)")
    ap.add_argument("--off-seconds", type=int,
                    help="seconds to hold the stream off (default from config)")
    ap.add_argument("--if-wedged", action="store_true",
                    help="only reset cameras that fail a control probe first "
                         "(safe for scheduled runs -- won't bounce healthy cameras)")
    args = ap.parse_args()

    cfg = load_config()
    off_seconds = args.off_seconds if args.off_seconds is not None \
        else cfg.get("off_seconds", 5)
    cameras = build_cameras(cfg, only=args.camera)
    if not cameras:
        log("no cameras selected (check config / --camera)")
        return 1

    log(f"method={args.method}  cameras={[c.name for c in cameras]}"
        f"{'  (only if wedged)' if args.if_wedged else ''}")

    failures = 0
    for cam in cameras:
        try:
            if args.method == "status":
                st = cam.status()
                log(f"[{cam.name}] {cam.ip}  power={st['power']} "
                    f"menu={st['menu']} streaming={st['streaming']}")
                continue

            if args.if_wedged:
                if cam.is_reachable():
                    log(f"[{cam.name}] {cam.ip}  control OK -- skipping")
                    continue
                log(f"[{cam.name}] {cam.ip}  control NOT responding -- resetting")

            if args.method == "video":
                cam.reset_video(off_seconds)
            elif args.method == "stream":
                cam.reset_stream(off_seconds)
            elif args.method == "reboot":
                cam.reset_reboot()

            log(f"[{cam.name}] {cam.ip}  DONE")
        except Exception as e:
            failures += 1
            log(f"[{cam.name}] {cam.ip}  FAILED: {e}")

    log(f"finished: {len(cameras) - failures}/{len(cameras)} ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
