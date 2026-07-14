#!/usr/bin/env bash
set -uo pipefail
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"

echo "============ /opt/wikijs top-level ============"
$P "pct exec 101 -- ls -la /opt/wikijs/ 2>/dev/null"

echo; echo "============ /opt/wikijs/data (asset storage) ============"
$P "pct exec 101 -- find /opt/wikijs/data -maxdepth 3 -type d 2>/dev/null | sort"

echo; echo "============ how is wikijs started? (pm2/docker/supervisor) ============"
$P "pct exec 101 -- pm2 list 2>/dev/null || echo '(no pm2)'"
$P "pct exec 101 -- ls /etc/supervisor/ 2>/dev/null || echo '(no supervisor)'"
$P "pct exec 101 -- ls /etc/systemd/system/ 2>/dev/null | grep -i wiki"

echo; echo "============ cloudflared config ============"
$P "pct exec 101 -- cat /etc/cloudflared/config.yml 2>/dev/null"

echo; echo "============ wiki config.yml (app config) ============"
$P "pct exec 101 -- cat /opt/wikijs/config.yml 2>/dev/null || echo '(no config.yml at /opt/wikijs/)'"
$P "pct exec 101 -- find /opt/wikijs -maxdepth 2 -name 'config.yml' 2>/dev/null | head -5"

echo; echo "============ find assets/sops dir in wikijs ============"
$P "pct exec 101 -- find /opt/wikijs -maxdepth 5 -type d -name 'sops' 2>/dev/null | head -5"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
