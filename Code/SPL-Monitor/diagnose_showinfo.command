#!/bin/bash
# Diagnose why the SPL dashboard show/engineer banner is blank.
# Runs from Brian's Mac; tees everything to diagnose_showinfo.out for Nyquist to read back.
cd "$(dirname "$0")"
OUT="diagnose_showinfo.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
JUMP="-J tds -i $KEY"

{
echo "===== SPL show-info diagnostic  $(date) ====="

echo
echo "----- 1) Public API: what the live server currently reports -----"
curl -s --max-time 15 https://spl.tinydoorstudios.com/api/show-info; echo

echo
echo "----- 2) VM config.json: showInfo block (enabled?) -----"
ssh $JUMP $VM 'python3 -c "import json;d=json.load(open(\"/opt/spl-monitor/config.json\"));import pprint;pprint.pprint(d.get(\"showInfo\",\"NO showInfo KEY\"))"' 2>&1

echo
echo "----- 3) VM service: recent [showinfo] log lines -----"
ssh $JUMP $VM 'journalctl -u spl-monitor --since "-2 days" --no-pager | grep -i showinfo | tail -20' 2>&1
echo "(if blank above: no showinfo log activity at all)"

echo
echo "----- 4) VM outbound reachability to docs.google.com -----"
ssh $JUMP $VM 'curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" --max-time 15 "https://docs.google.com/spreadsheets/d/10idHRrZrEjj1bwuexXIMQ6GY3tr0pXOd2YQcO60NnJw/export?format=csv&gid=1413426845"' 2>&1

echo
echo "----- 5) VM service status -----"
ssh $JUMP $VM 'systemctl is-active spl-monitor; systemctl show spl-monitor -p ActiveEnterTimestamp --value' 2>&1

echo
echo "===== end ====="
} 2>&1 | tee "$OUT"
