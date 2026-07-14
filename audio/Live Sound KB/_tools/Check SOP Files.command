#!/usr/bin/env bash
J="ssh -J tds -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ SOP files on VM (/opt/kb-assets/sops/) ============"
$J "find /opt/kb-assets/sops/ -type f 2>/dev/null | sort || echo '(directory empty or missing)'"

echo; echo "============ top-level /opt/kb-assets/ ============"
$J "ls -la /opt/kb-assets/ 2>/dev/null"

echo; echo "============ test curl for one SOP PDF ============"
$J "curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: kb.tinydoorstudios.com' http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
