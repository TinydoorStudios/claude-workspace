#!/bin/bash
# Deploy current SPL-Monitor source to the VM and restart. Brings the show/engineer
# banner (added 2026-07-01) live. Tees output to deploy_showinfo.out for Nyquist.
cd "$(dirname "$0")"
OUT="deploy_showinfo.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"

{
echo "===== SPL deploy  $(date) ====="
echo "----- rsync source -> VM -----"
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  -e "ssh -J tds -i $KEY" \
  /Users/brianlloyd/Documents/Claude/Code/SPL-Monitor/ "$VM":/opt/spl-monitor/ && echo "rsync OK"

echo "----- restart service -----"
ssh -J tds -i "$KEY" "$VM" 'sudo systemctl restart spl-monitor && sleep 3 && systemctl is-active spl-monitor'

echo "----- verify: /api/show-info now live -----"
sleep 2
curl -s --max-time 15 https://spl.tinydoorstudios.com/api/show-info; echo

echo "----- verify: VM config showInfo present -----"
ssh -J tds -i "$KEY" "$VM" 'python3 -c "import json;print(\"showInfo enabled:\", json.load(open(\"/opt/spl-monitor/config.json\")).get(\"showInfo\",{}).get(\"enabled\"))"' 2>&1

echo "----- verify: [showinfo] log activity -----"
ssh -J tds -i "$KEY" "$VM" 'journalctl -u spl-monitor --since "-1 min" --no-pager | grep -i showinfo | tail' 2>&1
echo "===== end ====="
} 2>&1 | tee "$OUT"
