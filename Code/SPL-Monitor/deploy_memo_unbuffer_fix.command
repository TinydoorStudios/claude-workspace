#!/bin/bash
# Push the updated systemd unit (PYTHONUNBUFFERED=1) and restart so [smaart]
# connection logs actually show up, then tail fresh logs.
cd "$(dirname "$0")"
OUT="deploy_memo_unbuffer_fix.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"

{
echo "===== unbuffer fix  $(date) ====="

echo "----- push unit -----"
rsync -az -e "$SSH" ./deploy/spl-monitor-memo.service "$VM":/tmp/spl-monitor-memo.service
$SSH "$VM" 'sudo mv /tmp/spl-monitor-memo.service /etc/systemd/system/spl-monitor-memo.service && \
  sudo systemctl daemon-reload && \
  sudo systemctl restart spl-monitor-memo && \
  sleep 5 && systemctl is-active spl-monitor-memo'

echo "----- fresh logs (10s after restart) -----"
$SSH "$VM" 'journalctl -u spl-monitor-memo --since "-15 sec" --no-pager'

echo "----- local curl -----"
$SSH "$VM" 'curl -s -o /dev/null -w "local 8091 = HTTP %{http_code}\n" --max-time 10 http://127.0.0.1:8091/'

echo "===== end ====="
} 2>&1 | tee "$OUT"
