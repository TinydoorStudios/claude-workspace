#!/usr/bin/env bash
set -uo pipefail
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ A. ps aux in CT 101 — any cloudflared? ============"
$P "pct exec 101 -- ps aux 2>/dev/null" | grep -i cloud || echo "(no cloudflared in CT 101 ps)"

echo; echo "============ B. ps aux on Proxmox host (tds) — any cloudflared? ============"
$P "ps aux 2>/dev/null" | grep -i cloud || echo "(no cloudflared on tds)"

echo; echo "============ C. ps aux on n8n VM — any cloudflared? ============"
$J "ps aux 2>/dev/null" | grep -i cloud || echo "(no cloudflared on n8n VM)"

echo; echo "============ D. verify new config is on CT 101 disk ============"
$P "pct exec 101 -- cat /etc/cloudflared/config.yml 2>/dev/null"

echo; echo "============ E. cloudflared configs on Proxmox host ============"
$P "find /etc/cloudflared/ -type f 2>/dev/null | head -5"
$P "cat /etc/cloudflared/config.yml 2>/dev/null || echo '(no config on tds)'"

echo; echo "============ F. cloudflared configs on n8n VM ============"
$J "find /etc/cloudflared/ -type f 2>/dev/null | head -5 || echo '(no /etc/cloudflared on n8n VM)'"
$J "cat /etc/cloudflared/config.yml 2>/dev/null || echo '(no config on n8n VM)'"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
