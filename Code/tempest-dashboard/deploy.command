#!/bin/bash
# Deploy tempest-dashboard to the n8n VM (192.168.200.84 via tds jump).
# Syncs code, preserves the VM's .env + history.json, restarts, verifies.
set +e
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="$SRC/deploy.out"
KEY=/Users/brianlloyd/.ssh/proxmox_tds
SSH="ssh -J tds -i $KEY -o ConnectTimeout=15 brian@192.168.200.84"

{
echo "===== tempest-dashboard deploy — $(date) ====="

echo; echo "----- [1] resolve service + working dir -----"
SVC=$($SSH "systemctl list-units --all --no-legend --no-pager | grep -i tempest | awk '{print \$1}' | head -1")
SVC=${SVC:-tempest-dashboard.service}
echo "service: $SVC"
WD=$($SSH "systemctl show $SVC -p WorkingDirectory --value")
[ -z "$WD" ] && WD=/opt/tempest-dashboard
echo "working dir: $WD"

echo; echo "----- [2] backup current server.js on VM -----"
$SSH "cp '$WD/server.js' '$WD/server.js.bak-$(date +%Y%m%d-%H%M%S)' && echo 'backup made' || echo 'backup FAILED'"

echo; echo "----- [3] rsync code (excluding .env, history.json, node_modules) -----"
rsync -az \
  --exclude .env --exclude history.json --exclude node_modules \
  --exclude .git --exclude '.claude' --exclude '*.command' --exclude '*.out' --exclude '*.bak-*' \
  -e "ssh -J tds -i $KEY" \
  "$SRC/" "brian@192.168.200.84:$WD/" && echo "rsync OK" || echo "rsync FAILED"

echo; echo "----- [4] restart service -----"
$SSH "sudo systemctl restart $SVC && sleep 3 && systemctl is-active $SVC"

echo; echo "----- [5] status tail -----"
$SSH "systemctl status $SVC --no-pager -l | head -12"

echo; echo "----- [6] verify: live WS payload — lightning should be IDENTICAL across all 3 cards -----"
$SSH "cd '$WD' && node -e '
const WS=require(\"ws\");
const ws=new WS(\"ws://localhost:3001\");
const t=setTimeout(()=>{console.log(\"timeout, no WS message\");process.exit(0)},9000);
ws.on(\"message\",m=>{
  clearTimeout(t);
  let a; try{a=JSON.parse(m)}catch(e){console.log(\"parse err\");process.exit(0)}
  for (const s of a) {
    console.log(s.name.padEnd(16), \"closestMi=\"+s.lightningClosestMi, \"count=\"+s.lightningCount,
                \"w1=\"+((s.lightningWithin||{})[1]||0), \"w5=\"+((s.lightningWithin||{})[5]||0));
  }
  const set=new Set(a.map(s=>s.lightningClosestMi+\"|\"+s.lightningCount));
  console.log(set.size===1 ? \"OK: all cards share one cluster lightning reading\" : \"WARN: cards differ\");
  process.exit(0);
});
ws.on(\"error\",e=>{console.log(\"WS error:\",e.message);process.exit(0)});
'"

echo; echo "===== done ====="
} 2>&1 | tee "$OUT"

echo; echo "Output saved to: $OUT"
