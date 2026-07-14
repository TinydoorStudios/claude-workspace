#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ nginx -T (full parsed config) ============"
$J "docker exec landing nginx -T 2>&1"

echo; echo "============ nginx error log (last 30 lines) ============"
$J "docker exec landing tail -30 /var/log/nginx/error.log 2>/dev/null || echo '(no error log)'"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
