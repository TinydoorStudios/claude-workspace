#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ nginx/docker config on n8n VM ============"
$J "docker ps 2>/dev/null | grep -i nginx || echo '(no nginx docker containers running)'"
$J "find /etc/nginx /home/brian -name '*.conf' 2>/dev/null | head -10 || echo '(no nginx config found)'"
$J "docker inspect \$(docker ps -qf name=nginx 2>/dev/null) 2>/dev/null | grep -A5 'Mounts\|Binds' || echo '(no docker inspect)'"

echo; echo "============ any compose files referencing port 8088? ============"
$J "find /home/brian /opt -name 'docker-compose*' -o -name 'compose.yml' 2>/dev/null | xargs grep -l '8088' 2>/dev/null | head -5"

echo; echo "============ what IS on port 8088? ============"
$J "ss -tlnp 2>/dev/null | grep 8088 || netstat -tlnp 2>/dev/null | grep 8088 || echo '(nothing on 8088?)'"

echo; echo "============ test the SOP URL from n8n VM to itself ============"
$J "curl -s -o /dev/null -w 'HTTP %{http_code} | type: %{content_type} | size: %{size_download}\n' \
    http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ test a memo SOP from n8n VM ============"
$J "curl -s -o /dev/null -w 'HTTP %{http_code}\n' \
    http://127.0.0.1:8088/assets/sops/memo/memo-crowd-mics.pdf"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
