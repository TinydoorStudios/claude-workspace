#!/bin/bash
# pve-status-push.sh — runs ON the pve host (tds). Collects host + guest stats
# with pvesh and pushes them to the n8n VM for the landing page's status.json.
#
# Install (as root on tds):
#   cp pve-status-push.sh /usr/local/bin/ && chmod +x /usr/local/bin/pve-status-push.sh
#   crontab -e  →  * * * * * /usr/local/bin/pve-status-push.sh >/dev/null 2>&1
#
# Requires root@pve's SSH key authorized for brian@192.168.200.84 (see DEPLOY.md).

set -euo pipefail
VM=brian@192.168.200.84
DEST=/opt/status-writer/pve.json

JSON=$(python3 - <<'EOF'
import json, subprocess
def pvesh(path):
    out = subprocess.run(["pvesh", "get", path, "--output-format", "json"],
                         capture_output=True, text=True, timeout=15).stdout
    return json.loads(out)
nodes = pvesh("/nodes")
n = nodes[0]
guests = [{"vmid": g["vmid"], "name": g["name"], "type": g["type"],
           "status": g["status"], "cpu": round(g.get("cpu", 0), 4),
           "mem": round(g.get("mem", 0) / max(g.get("maxmem", 1), 1), 4),
           "uptime": g.get("uptime", 0)}
          for g in pvesh("/cluster/resources?type=vm")]
print(json.dumps({
    "pve": {"cpu": round(n["cpu"], 4), "mem": round(n["mem"] / n["maxmem"], 4),
            "uptime": n["uptime"], "status": n["status"]},
    "guests": guests,
}, separators=(",", ":")))
EOF
)

echo "$JSON" | ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new "$VM" \
  "cat > $DEST.tmp && mv $DEST.tmp $DEST"
