#!/bin/bash
# Export the shows board feed and push it to the gated /rack/ page on the n8n VM.
set -euo pipefail
cd "$(dirname "$0")"
LOG=/tmp/push-shows.log

# --delay: called by show_status.stamp() after every pipeline stamp. Wait so a
# burst of stamps (packet + ses land together) collapses into one push; a run
# that finds the lock held just exits, the running one picks up its change.
if [ "${1:-}" = "--delay" ]; then
  exec >>"$LOG" 2>&1
  LOCK=/tmp/push-shows.lock
  mkdir "$LOCK" 2>/dev/null || exit 0
  trap 'rmdir "$LOCK"' EXIT
  sleep 5
fi

KEY=~/.ssh/proxmox_tds
VM=brian@192.168.200.84

/usr/bin/python3 export_shows.py

if ssh -i "$KEY" -o ConnectTimeout=6 -o BatchMode=yes "$VM" true 2>/dev/null; then
  SSH=(ssh -i "$KEY" -o BatchMode=yes); SCP=(scp -i "$KEY" -o BatchMode=yes)
else
  SSH=(ssh -J tds -i "$KEY" -o BatchMode=yes); SCP=(scp -o ProxyJump=tds -i "$KEY" -o BatchMode=yes)
fi

"${SCP[@]}" deploy/rack/shows.json "$VM":/tmp/rack-shows.json
"${SSH[@]}" "$VM" 'sudo install -m 644 /tmp/rack-shows.json /opt/landing/html/rack/shows.json'
echo "shows.json pushed $(date '+%F %T')"
