#!/usr/bin/env bash
set -uo pipefail
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"

echo "============ 1. write new cloudflared config ============"
$P "pct exec 101 -- tee /etc/cloudflared/config.yml" << 'EOF'
tunnel: b1e6581d-4384-4fbe-b960-a156760a2860
credentials-file: /etc/cloudflared/b1e6581d-4384-4fbe-b960-a156760a2860.json
ingress:
  - hostname: kb.tinydoorstudios.com
    path: /assets/
    service: http://192.168.200.84:8088
  - hostname: kb.tinydoorstudios.com
    service: http://localhost:3000
  - service: http_status:404
EOF
echo "✓ config written"

echo; echo "============ 2. verify config on disk ============"
$P "pct exec 101 -- cat /etc/cloudflared/config.yml"

echo; echo "============ 3. find cloudflared service / process ============"
$P "pct exec 101 -- systemctl list-units --type=service --all 2>/dev/null | grep -i cloud || echo '(no systemd service)'"
$P "pct exec 101 -- ls /etc/init.d/ 2>/dev/null | grep -i cloud || echo '(no init.d entry)'"
CF_PID=$($P "pct exec 101 -- pgrep -f cloudflared 2>/dev/null || echo ''")
echo "cloudflared PID: ${CF_PID:-not found}"

echo; echo "============ 4. restart cloudflared ============"
# Try systemd first, fall back to kill+restart
$P "pct exec 101 -- systemctl restart cloudflared 2>/dev/null && echo 'restarted via systemd'" || \
$P "pct exec 101 -- service cloudflared restart 2>/dev/null && echo 'restarted via init.d'" || {
  echo "no service manager found — sending HUP to process"
  $P "pct exec 101 -- pkill -HUP cloudflared 2>/dev/null && echo 'HUP sent'" || echo "HUP failed"
}

echo; echo "============ 5. wait 5s, then verify from CT 101 ============"
sleep 5
$P "pct exec 101 -- curl -s -o /dev/null -w 'SOP via n8n nginx: HTTP %{http_code}\n' \
    http://192.168.200.84:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ done — now test https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf ============"
echo "Press any key to close…"; read -n 1 -s
