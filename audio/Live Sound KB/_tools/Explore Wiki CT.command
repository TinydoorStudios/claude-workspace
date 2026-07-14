#!/usr/bin/env bash
set -uo pipefail
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"

echo "============ CT 101 process (find wiki node proc) ============"
$P "pct exec 101 -- ps aux 2>/dev/null" | grep -i node | head -10

echo; echo "============ root dirs in CT 101 ============"
$P "pct exec 101 -- ls / 2>/dev/null"

echo; echo "============ find wiki.js app.js (where installed) ============"
$P "pct exec 101 -- find / -maxdepth 6 -name 'app.js' 2>/dev/null" | grep -i wiki | head -10

echo; echo "============ find any 'wiki' dirs ============"
$P "pct exec 101 -- find / -maxdepth 4 -type d -iname '*wiki*' 2>/dev/null | head -20"

echo; echo "============ /etc/systemd/system — wiki service ============"
$P "pct exec 101 -- find /etc/systemd/system -name '*wiki*' 2>/dev/null | head -5"
$P "pct exec 101 -- cat /etc/systemd/system/wiki.service 2>/dev/null || echo '(no wiki.service)'"

echo; echo "============ /home and /root dirs ============"
$P "pct exec 101 -- ls /home 2>/dev/null; ls /root 2>/dev/null"

echo; echo "============ look for config.yml (wikijs config) ============"
$P "pct exec 101 -- find / -maxdepth 5 -name 'config.yml' -not -path '*/proc/*' 2>/dev/null | head -5"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
