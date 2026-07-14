#!/bin/bash
# Deploy the Slack alert toggle (backend + frontend) and enable the webhook
# for the Memo instance. Redeploys backend/web, pushes the updated env file,
# restarts, and confirms.
cd "$(dirname "$0")"
OUT="deploy_memo_slack_toggle.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"
REMOTE_DIR="/opt/spl-monitor-memo"

{
echo "===== Slack toggle deploy  $(date) ====="

echo "----- rsync source -----"
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  --exclude config.json --exclude config.memo.json \
  -e "$SSH" \
  ./ "$VM":"$REMOTE_DIR"/ && echo "rsync OK"

echo "----- push updated env (adds SPL_ALERT_WEBHOOK) -----"
rsync -az -e "$SSH" ./deploy/spl-monitor-memo.env "$VM":/tmp/spl-monitor-memo.env
$SSH "$VM" 'sudo mv /tmp/spl-monitor-memo.env /etc/spl-monitor-memo.env && sudo chmod 600 /etc/spl-monitor-memo.env'

echo "----- restart -----"
$SSH "$VM" 'sudo systemctl restart spl-monitor-memo && sleep 3 && systemctl is-active spl-monitor-memo'

echo "----- verify: local curl -----"
$SSH "$VM" 'curl -s -o /dev/null -w "local 8091 = HTTP %{http_code}\n" --max-time 10 http://127.0.0.1:8091/'

echo "----- fresh logs -----"
$SSH "$VM" 'journalctl -u spl-monitor-memo --since "-10 sec" --no-pager'

echo "===== end ====="
} 2>&1 | tee "$OUT"
