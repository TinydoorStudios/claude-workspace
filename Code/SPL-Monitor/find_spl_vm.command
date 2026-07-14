#!/bin/bash
# Discover where spl-monitor actually runs (which Proxmox guest + its IP).
set -uo pipefail
LOG="$(cd "$(dirname "$0")" && pwd)/find_spl_vm.log"
exec > >(tee "$LOG") 2>&1
HOST=tds

echo "=== $(date) — locating spl-monitor guest ==="
ssh -o ConnectTimeout=15 "$HOST" '
echo "### VMs (qm):"; qm list 2>/dev/null
echo "### Containers (pct):"; pct list 2>/dev/null
echo
echo "### Guest IPs:"
for id in $(qm list 2>/dev/null | awk "NR>1{print \$1}"); do
  name=$(qm config "$id" 2>/dev/null | awk -F": " "/^name:/{print \$2}")
  ips=$(qm guest cmd "$id" network-get-interfaces 2>/dev/null | grep -oE "\"ip-address\" : \"[0-9.]+\"" | grep -oE "[0-9.]+" | grep -v "^127" | tr "\n" " ")
  echo "VM $id ($name): ${ips:-<no guest agent / no ip>}"
done
for id in $(pct list 2>/dev/null | awk "NR>1{print \$1}"); do
  name=$(pct config "$id" 2>/dev/null | awk -F": " "/^hostname:/{print \$2}")
  ip=$(pct exec "$id" -- hostname -I 2>/dev/null)
  echo "CT $id ($name): ${ip:-<n/a>}"
done
'
echo "=== done ==="
