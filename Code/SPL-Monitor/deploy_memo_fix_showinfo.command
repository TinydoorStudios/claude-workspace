#!/bin/bash
# Redeploy backend/ (showinfo.py fix) to the Memo instance and restart.
cd "$(dirname "$0")"
OUT="deploy_memo_fix_showinfo.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"
REMOTE_DIR="/opt/spl-monitor-memo"

{
echo "===== Memo SPL fix redeploy  $(date) ====="

echo "----- rsync source -----"
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  --exclude config.json --exclude config.memo.json \
  -e "$SSH" \
  ./ "$VM":"$REMOTE_DIR"/ && echo "rsync OK"

echo "----- restart -----"
$SSH "$VM" 'sudo systemctl restart spl-monitor-memo && sleep 3 && systemctl is-active spl-monitor-memo'

echo "----- verify: local curl -----"
$SSH "$VM" 'curl -s -o /dev/null -w "local 8091 = HTTP %{http_code}\n" --max-time 10 http://127.0.0.1:8091/'

echo "----- verify: journal -----"
sleep 2
$SSH "$VM" 'journalctl -u spl-monitor-memo --since "-1 min" --no-pager | tail -30'

echo "===== end ====="
} 2>&1 | tee "$OUT"
