#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. cloudflared config file ============"
$J "cat /etc/cloudflared/config.yml 2>/dev/null || cat ~/.cloudflared/config.yml 2>/dev/null || echo '(no config file — may be remotely managed)'"

echo; echo "============ 2. cloudflared service status ============"
$J "sudo systemctl status cloudflared 2>&1 | head -20 || echo '(systemctl failed)'"

echo; echo "============ 3. cloudflared tunnel ingress (if locally managed) ============"
$J "sudo cloudflared tunnel ingress validate 2>&1 || echo '(ingress validate failed — likely remotely managed)'"

echo; echo "============ 4. curl directly to Wiki.js (port 3000) — does it 404 /assets/? ============"
$J "curl -s -o /dev/null -w 'Wiki.js direct: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    -H 'Host: kb.tinydoorstudios.com' \
    http://192.168.200.126:3000/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ 5. curl directly to nginx (port 8088) — what do we get? ============"
$J "curl -s -o /dev/null -w 'nginx direct: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    -H 'Host: kb.tinydoorstudios.com' \
    http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ 6. public URL headers (full curl from n8n VM) ============"
$J "curl -sI 'https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf' 2>&1 | head -20"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
