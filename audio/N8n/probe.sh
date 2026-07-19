#!/usr/bin/env bash
set -uo pipefail
SSH_OPTS=(-J tds -i ~/.ssh/proxmox_tds -o StrictHostKeyChecking=no)
VM="brian@192.168.200.84"
SLUG="2026-06-20-blue-eighty-eight"
KB="https://kb.tinydoorstudios.com"
BASE="/Users/brianlloyd/Documents/Claude/audio/N8n"
exec > >(tee "$BASE/probe.log") 2>&1
echo "=== probe $(date) ==="
for f in foh-channel-processing.pdf blue-eighty-eight.ses; do
  echo "--- $f"
  echo -n "  origin-direct (127.0.0.1:8088): "
  ssh "${SSH_OPTS[@]}" "$VM" "curl -s -o /dev/null -w '%{http_code}' -H 'Host: kb.tinydoorstudios.com' 'http://127.0.0.1:8088/assets/shows/$SLUG/$f'"; echo
  echo "  in-container file:"
  ssh "${SSH_OPTS[@]}" "$VM" "sudo docker exec landing ls -la '/kb-assets/shows/$SLUG/$f' 2>&1 | sed 's/^/    /'"
  echo "  through-Cloudflare headers:"
  curl -sI --max-time 30 "$KB/assets/shows/$SLUG/$f" | grep -iE '^(HTTP/|cf-cache-status|cf-ray|server|content-type|content-disposition)' | sed 's/^/    /'
  echo
done
echo "  landing /assets/ nginx block:"
ssh "${SSH_OPTS[@]}" "$VM" "sudo sed -n '/server_name kb/,/^}/p' /opt/landing/nginx.conf | sed 's/^/    /'"
