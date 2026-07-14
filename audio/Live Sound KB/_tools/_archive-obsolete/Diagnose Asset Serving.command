#!/usr/bin/env bash
set -uo pipefail
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"

echo "============ 1. curl the SOP PDF directly from Wiki.js (inside CT 101) ============"
$P "pct exec 101 -- curl -s -o /dev/null -w 'HTTP %{http_code} | content-type: %{content_type}\n' \
    http://localhost:3000/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ 2. curl a shows asset (does this path work?) ============"
SHOWS_FILE=$($P "pct exec 101 -- find /opt/wikijs/data/assets/shows -type f 2>/dev/null | head -1")
echo "Shows file on disk: $SHOWS_FILE"
if [ -n "$SHOWS_FILE" ]; then
  SHOWS_URL="${SHOWS_FILE#/opt/wikijs/data}"
  echo "Trying URL: http://localhost:3000$SHOWS_URL"
  $P "pct exec 101 -- curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:3000$SHOWS_URL"
fi

echo; echo "============ 3. Wiki.js routes — how does /assets/ work? ============"
$P "pct exec 101 -- grep -rn 'assets' /opt/wikijs/server/app.js 2>/dev/null | head -20 || \
    grep -rn \"app.use.*assets\|router.*assets\|express.static\" /opt/wikijs/server/ 2>/dev/null | head -20"

echo; echo "============ 4. Is nginx available in CT 101? ============"
$P "pct exec 101 -- which nginx 2>/dev/null || echo '(no nginx)'"
$P "pct exec 101 -- nginx -v 2>&1 || echo '(nginx not installed)'"

echo; echo "============ 5. Can CT 101 reach n8n VM nginx? ============"
$P "pct exec 101 -- curl -s -o /dev/null -w 'HTTP %{http_code}\n' \
    http://192.168.200.84:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf 2>/dev/null || echo 'curl failed'"

echo; echo "============ 6. cloudflared systemd service name ============"
$P "pct exec 101 -- systemctl list-units --type=service 2>/dev/null | grep -i cloud"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
