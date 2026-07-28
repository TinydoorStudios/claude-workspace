"""Append one row of tent state to a CSV. Run on a timer.

AC Infinity's own history endpoint (/api/log/logdataByAll) returns zero rows for
the Controller AI (devType 20) — logging appears to be off or served by an
endpoint we haven't mapped — so we build our own trend log by polling.

Env: ACI_EMAIL, ACI_PASSWORD (same /etc/acinfinity.env the server uses).
Usage: sample.py <devId> [csv_path]
"""

import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from aci_client import ACInfinity

FIELDS = ["time", "air_tempF", "air_rh", "air_vpd",
          "media_tempF", "media_moist", "media_ec",
          "p1_out", "p2_out", "p3_out", "p4_out",
          "p1_load", "p2_load", "p3_load", "p4_load"]


async def collect(dev_id):
    aci = ACInfinity(os.environ["ACI_EMAIL"], os.environ["ACI_PASSWORD"])
    try:
        for dev in await aci.devices():
            if str(dev.get("devId")) != str(dev_id):
                continue
            info = dev.get("deviceInfo") or {}
            s = {x.get("sensorKey"): (x.get("sensorData") or 0) / 100
                 for x in (info.get("sensors") or [])}
            ports = {p.get("port"): p for p in (info.get("ports") or [])}
            row = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "air_tempF": (info.get("temperatureF") or 0) / 100,
                "air_rh": (info.get("humidity") or 0) / 100,
                "air_vpd": (info.get("vpdnums") or 0) / 100,
                # media probe reports on its own sensor port 1: temp / moisture / EC
                "media_tempF": s.get("0-1"),
                "media_moist": s.get("2-1"),
                "media_ec": s.get("3-1"),
            }
            for n in (1, 2, 3, 4):
                p = ports.get(n) or {}
                row[f"p{n}_out"] = p.get("speak")
                row[f"p{n}_load"] = p.get("loadState")
            return row
    finally:
        await aci.close()
    raise SystemExit(f"device {dev_id} not found")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: sample.py <devId> [csv_path]")
    dev_id = sys.argv[1]
    path = Path(sys.argv[2] if len(sys.argv) > 2
                else "/opt/acinfinity/logs/tent_log.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    row = asyncio.run(collect(dev_id))
    new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


if __name__ == "__main__":
    main()
