#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. docker inspect 'landing' — find mounts ============"
$J "docker inspect landing 2>/dev/null | python3 -c \"
import json,sys
d=json.load(sys.stdin)[0]
print('Mounts:')
for m in d.get('Mounts',[]):
    print(' ', m.get('Source','?'), '->', m.get('Destination','?'))
print('Ports:', list(d.get('HostConfig',{}).get('PortBindings',{}).keys()))
\""

echo; echo "============ 2. show current nginx config ============"
$J "docker exec landing cat /etc/nginx/nginx.conf 2>/dev/null || \
    docker exec landing cat /etc/nginx/conf.d/default.conf 2>/dev/null || \
    echo '(could not read config)'"

echo; echo "============ 3. list /opt/kb-assets/sops ============"
$J "ls /opt/kb-assets/sops/ 2>/dev/null || echo '(no /opt/kb-assets/sops)'"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
