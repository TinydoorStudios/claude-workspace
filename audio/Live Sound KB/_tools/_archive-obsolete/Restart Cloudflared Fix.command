#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. config file mtime vs cloudflared start time ============"
$J "stat /etc/cloudflared/config.yml 2>&1 | grep -E 'Modify|Change'"
$J "sudo systemctl show cloudflared --property=ActiveEnterTimestamp 2>&1"

echo; echo "============ 2. current ingress config ============"
$J "cat /etc/cloudflared/config.yml"

echo; echo "============ 3. restart cloudflared ============"
$J "sudo systemctl restart cloudflared && echo 'cloudflared restarted OK' || echo 'ERROR: restart failed'"
sleep 4

echo; echo "============ 4. confirm running ============"
$J "sudo systemctl status cloudflared 2>&1 | head -8"

echo; echo "============ 5. verify public URL now returns PDF ============"
sleep 3
curl -sI "https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf" 2>&1 | grep -E "HTTP|content-type|content-length|server|cf-cache"

echo; echo "============ 6. check nginx log — public request should appear now ============"
$J "docker logs landing --tail 5 2>&1"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
