#!/bin/bash
# Push config.memo.json -> remote config.json on the Memo instance and restart.
cd "$(dirname "$0")"
OUT="deploy_memo_config.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"
REMOTE_DIR="/opt/spl-monitor-memo"

{
echo "===== push config.memo.json  $(date) ====="
rsync -az -e "$SSH" ./config.memo.json "$VM":"$REMOTE_DIR"/config.json && echo "config OK"
$SSH "$VM" 'sudo systemctl restart spl-monitor-memo && sleep 3 && systemctl is-active spl-monitor-memo'
echo "----- fresh logs -----"
$SSH "$VM" 'journalctl -u spl-monitor-memo --since "-10 sec" --no-pager'
echo "===== end ====="
} 2>&1 | tee "$OUT"
