#!/bin/bash
# Read-only status check for the Memo instance — no restart, no config change.
cd "$(dirname "$0")"
OUT="check_memo_status.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"

{
echo "----- service status -----"
$SSH "$VM" 'systemctl status spl-monitor-memo --no-pager -l | head -15'
echo
echo "----- last 40 log lines -----"
$SSH "$VM" 'journalctl -u spl-monitor-memo -n 40 --no-pager'
echo
echo "----- effective env -----"
$SSH "$VM" 'sudo cat /etc/spl-monitor-memo.env'
} 2>&1 | tee "$OUT"
