#!/usr/bin/env python3
"""'Run again' button worker: a full run_now.py pass (every current show,
blank cells only), writing its result JSON to the status file the booking
page polls (audit #23 — the button used to block a web request for minutes).

  run_again.py <status.json>
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
status = Path(sys.argv[1])
p = subprocess.run([sys.executable, "run_now.py"], cwd=HERE, capture_output=True, text=True)
sys.stdout.write(p.stdout or "")
sys.stdout.write(p.stderr or "")
line = (p.stdout or "").strip().splitlines()[-1] if (p.stdout or "").strip() else ""
try:
    result = json.loads(line)
except ValueError:
    result = {"error": "bad output"}
result["state"] = "error" if (p.returncode or "error" in result) else "done"
result["finished"] = dt.datetime.now().isoformat(timespec="seconds")
status.write_text(json.dumps(result))
