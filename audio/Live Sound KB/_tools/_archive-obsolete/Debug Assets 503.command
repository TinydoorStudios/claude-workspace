#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. files inside the 'landing' container at /kb-assets ============"
$J "docker exec landing ls -la /kb-assets/ 2>&1 || echo '(ls failed)'"
$J "docker exec landing ls -la /kb-assets/sops/ 2>&1 || echo '(sops dir not found)'"
$J "docker exec landing ls -la /kb-assets/sops/fsq/ 2>&1 || echo '(fsq dir not found)'"

echo; echo "============ 2. nginx user and file permissions ============"
$J "docker exec landing id nginx 2>/dev/null || docker exec landing id www-data 2>/dev/null || echo '(nginx user not found)'"
$J "stat /opt/kb-assets/ 2>/dev/null"
$J "stat /opt/kb-assets/sops/fsq/ 2>/dev/null"
$J "stat /opt/kb-assets/sops/fsq/fsq-m32-failover-sop.pdf 2>/dev/null"

echo; echo "============ 3. curl with Host header ============"
$J "curl -v -H 'Host: kb.tinydoorstudios.com' \
    http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf 2>&1 | head -40"

echo; echo "============ 4. full kb server block from config ============"
$J "python3 -c \"
import re
with open('/opt/landing/nginx.conf') as f:
    c = f.read()
# find the kb block
m = re.search(r'server\s*\{[^}]*kb\.tinydoorstudios[^}]*(?:\{[^}]*\}[^}]*)*\}', c, re.DOTALL)
print(m.group(0) if m else 'not found')
\""

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
