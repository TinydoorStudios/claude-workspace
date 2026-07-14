#!/usr/bin/env bash
# Determine where the Cloudflare tunnel routes kb.tinydoorstudios.com (asset vs page).
J="ssh -J tds -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"
A="https://kb.tinydoorstudios.com/assets/shows/2026-06-20-blue-eighty-eight/download-test.pdf"
P="https://kb.tinydoorstudios.com/shows"

echo "============ cloudflared ingress rule — ASSET url ============"
$J "sudo cloudflared tunnel ingress rule '$A' 2>&1 || cloudflared tunnel ingress rule '$A' 2>&1"

echo; echo "============ cloudflared ingress rule — PAGE url ============"
$J "sudo cloudflared tunnel ingress rule '$P' 2>&1 || cloudflared tunnel ingress rule '$P' 2>&1"

echo; echo "============ cloudflared config / service ============"
$J "sudo cat /etc/cloudflared/config.yml 2>/dev/null || cat /etc/cloudflared/config.yml 2>/dev/null || echo '(no local config.yml — tunnel is dashboard/remote-managed)'"
echo "---- running cloudflared process ----"
$J "ps -eo args | grep -i '[c]loudflared' | head -3"

echo; echo "============ what the landing nginx server_name is ============"
$J "sudo docker exec landing sh -c 'grep -rn \"server_name\|listen\|proxy_pass\" /etc/nginx/conf.d/default.conf' 2>&1"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
