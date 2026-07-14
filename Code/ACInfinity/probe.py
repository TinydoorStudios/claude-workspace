#!/usr/bin/env python3
"""
AC Infinity cloud-API probe.

Throwaway diagnostic: logs into the AC Infinity cloud with your app credentials,
then dumps exactly what your controllers expose — device info, live sensors, and
every per-port mode setting. Tells us for certain what's readable/controllable
before building anything. Read-only: it never writes a setting.

Usage:
    python3 probe.py
    python3 probe.py --email you@example.com      # password prompted securely

Stdlib only — no pip install needed. Raw JSON is saved next to this script.
"""

import argparse
import getpass
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://www.acinfinityserver.com"
# The app's own UA — the cloud rejects unknown clients.
UA = ("ACController/1.8.2 (com.acinfinity.humiture; build:489; iOS 16.5.1) "
      "Alamofire/5.4.4")
OUT = Path(__file__).with_name(
    f"probe_dump_{datetime.now():%Y%m%d_%H%M%S}.json")


def _post(path, data, token=None):
    body = urllib.parse.urlencode(data).encode()
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }
    if token:
        headers["token"] = token
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def login(email, password):
    # Known quirk: the cloud truncates the password to 25 chars, and the field
    # is literally spelled "appPasswordl".
    resp = _post("/api/user/appUserLogin",
                 {"appEmail": email, "appPasswordl": password[:25]})
    if resp.get("code") != 200:
        sys.exit(f"Login failed: {resp.get('msg')!r} (code {resp.get('code')})")
    return resp["data"]["appId"]


def device_list(token):
    return _post("/api/user/devInfoListAll", {"userId": token}, token=token)


def port_settings(token, dev_id, port):
    return _post("/api/dev/getdevModeSettingList",
                 {"devId": str(dev_id), "port": str(port)}, token=token)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email")
    args = ap.parse_args()

    email = args.email or input("AC Infinity email: ").strip()
    password = getpass.getpass("AC Infinity password: ")

    print("\nLogging in...")
    token = login(email, password)
    print("OK — token acquired.\n")

    devs = device_list(token)
    raw = {"devInfoListAll": devs, "settings": {}}

    items = devs.get("data") or []
    if not items:
        print("No devices returned. Full response saved to disk.")
    for d in items:
        name = d.get("devName", "?")
        dev_id = d.get("devId")
        dtype = d.get("devType")
        info = d.get("deviceInfo", {}) or {}
        print("=" * 60)
        print(f"{name}   (devId={dev_id}, devType={dtype})")
        print(f"  online={d.get('online')}  fw={info.get('firmwareVersion')}  "
              f"hw={info.get('hardwareVersion')}")
        print(f"  temp={info.get('temperature')}  humidity={info.get('humidity')}  "
              f"vpd={info.get('vpdnums')}")
        ports = info.get("ports") or []
        for p in ports:
            pid = p.get("port")
            print(f"   - port {pid}: {p.get('portName','?')!r}  "
                  f"state={p.get('loadState')}  speed={p.get('speak')}")
            try:
                s = port_settings(token, dev_id, pid)
                raw["settings"].setdefault(str(dev_id), {})[str(pid)] = s
            except Exception as e:  # keep probing other ports
                print(f"       (settings fetch failed: {e})")
        print()

    OUT.write_text(json.dumps(raw, indent=2))
    print("=" * 60)
    print(f"Full raw JSON written to:\n  {OUT}")
    print("\nSend me that file (or paste it) and I'll tell you exactly what's "
          "buildable for each controller.")


if __name__ == "__main__":
    main()
