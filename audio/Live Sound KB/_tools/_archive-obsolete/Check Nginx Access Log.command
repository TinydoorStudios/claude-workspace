#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. make a public request then check nginx access log ============"
echo "Making public request..."
curl -s -o /dev/null -w "public curl: HTTP %{http_code}\n" \
    "https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo "Checking nginx access log for that request..."
$J "docker logs landing --tail 20 2>&1"

echo; echo "============ 2. nginx container port bindings ============"
$J "docker inspect landing --format '{{json .HostConfig.PortBindings}}' 2>&1"
$J "docker port landing 2>&1"

echo; echo "============ 3. what is listening on port 8088 on the host? ============"
$J "ss -tlnp | grep 8088 2>&1 || netstat -tlnp | grep 8088 2>&1 || echo '(ss/netstat failed)'"

echo; echo "============ 4. curl to 127.0.0.1:8088 WITHOUT host header — what server block answers? ============"
$J "curl -s -o /dev/null -w 'no-host-header: HTTP %{http_code} | type: %{content_type}\n' \
    http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ 5. verbose public curl showing response headers ============"
curl -sI "https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf" 2>&1 | head -15

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
