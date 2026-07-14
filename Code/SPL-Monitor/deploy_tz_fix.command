#!/bin/bash
# SPL Monitor — set New York timezone + deploy frontend clock fix
# Real host: n8n VM 192.168.200.84, reached by hopping through the
# Proxmox host "tds" (ProxyJump). VM user brian, key proxmox_tds.
# Run on the Mac: bash ~/Documents/Claude/Code/SPL-Monitor/deploy_tz_fix.command
set -uo pipefail

LOG="$(cd "$(dirname "$0")" && pwd)/deploy_tz_fix.log"
exec > >(tee "$LOG") 2>&1

KEY=~/.ssh/proxmox_tds
VM=brian@192.168.200.84
SSHOPT=(-J tds -i "$KEY" -o ConnectTimeout=20)
SRC=/Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/

echo "=== $(date) — SPL Monitor TZ fix (n8n VM via tds) ==="

echo "--- 0. confirm VM + current timezone ---"
ssh "${SSHOPT[@]}" "$VM" 'echo "host: $(hostname)  user: $(whoami)"; echo "VM date now: $(date)"; echo "system TZ:"; timedatectl 2>/dev/null | grep -i "time zone"; echo -n "spl-monitor: "; systemctl is-active spl-monitor; echo -n "/opt/spl-monitor: "; [ -d /opt/spl-monitor ] && echo present || echo MISSING' || { echo "!! cannot reach VM — stop."; exit 1; }

echo "--- 1. rsync source (frontend clock fix) ---"
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  -e "ssh -J tds -i $KEY" "$SRC" "$VM:/opt/spl-monitor/"

echo "--- 2a. set VM system timezone to America/New_York ---"
ssh "${SSHOPT[@]}" "$VM" 'sudo timedatectl set-timezone America/New_York && echo "set -> $(timedatectl | grep -i "time zone")"'

echo "--- 2b. rewrite /etc/spl-monitor.env with TZ=America/New_York (full var set) ---"
ssh "${SSHOPT[@]}" "$VM" 'sudo tee /etc/spl-monitor.env >/dev/null <<EOF
SPL_SOURCE=smaart
SMAART_HOST=192.24.143.121
SMAART_PORT=26000
SPL_PORT=8090
SPL_ALERT_WEBHOOK=http://localhost:5678/webhook/spl-violation
TZ=America/New_York
EOF
echo "env written:"; sudo cat /etc/spl-monitor.env'

echo "--- 3. restart service ---"
ssh "${SSHOPT[@]}" "$VM" 'sudo systemctl restart spl-monitor && sleep 2 && systemctl is-active spl-monitor'

echo "--- 4. verify process is on Eastern time ---"
ssh "${SSHOPT[@]}" "$VM" 'echo "VM date: $(date)"; \
  PID=$(systemctl show -p MainPID --value spl-monitor); \
  echo "spl-monitor PID: $PID"; \
  echo -n "process TZ env: "; sudo tr "\0" "\n" < /proc/$PID/environ 2>/dev/null | grep "^TZ=" || echo "(not set)"; \
  echo -n "daily generatedAt: "; curl -s localhost:8090/api/daily 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get(\"generatedAt\",\"(none)\"))" 2>/dev/null || echo "(endpoint unavailable)"'

echo "=== done $(date) ==="
