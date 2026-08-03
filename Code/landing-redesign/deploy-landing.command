#!/bin/bash
# Push deploy/index.html (+ rack/index.html) to the landing nginx on the n8n VM.
# Run from the Mac with Tailscale up (or on the house/venue LAN).
set -euo pipefail
cd "$(dirname "$0")"

KEY=~/.ssh/proxmox_tds
VM=brian@192.168.200.84
STAMP=$(date +%Y%m%d-%H%M%S)

# Pick a working route: direct if on-LAN, else ProxyJump through tds.
if ssh -i "$KEY" -o ConnectTimeout=6 -o BatchMode=yes "$VM" true 2>/dev/null; then
  SSH=(ssh -i "$KEY")
  SCP=(scp -i "$KEY")
  echo "route: direct"
else
  SSH=(ssh -J tds -i "$KEY")
  SCP=(scp -o ProxyJump=tds -i "$KEY")
  echo "route: via tds"
fi

# scp flattens paths — stage under distinct names.
"${SCP[@]}" deploy/index.html      "$VM":/tmp/main-index.html
"${SCP[@]}" deploy/rack/index.html "$VM":/tmp/rack-index.html

"${SSH[@]}" "$VM" "
  sudo cp /opt/landing/html/index.html      /opt/landing/html/index.html.bak.$STAMP
  sudo cp /opt/landing/html/rack/index.html /opt/landing/html/rack/index.html.bak.$STAMP
  sudo cp /tmp/main-index.html /opt/landing/html/index.html
  sudo cp /tmp/rack-index.html /opt/landing/html/rack/index.html
  ls -l /opt/landing/html/index.html /opt/landing/html/rack/index.html
"

echo "done — no container restart needed (dir mount). https://tinydoorstudios.com"
