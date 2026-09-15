#!/usr/bin/env bash
# Adds/verifies the digico.tinydoorstudios.com route on the REMOTE-managed n8n-tunnel
# (DNS CNAME + ingress rule). Credentials are read from the existing KB tunnel script so
# they never appear on a command line. Usage: cf-route.sh [show|apply]
set -uo pipefail
SRC="$HOME/Documents/Claude/audio/Live Sound KB/_tools/KB-Fix-Tunnel-API.command"
TOKEN=$(grep -m1 '^TOKEN=' "$SRC" | cut -d'"' -f2); ACCT=$(grep -m1 '^ACCT=' "$SRC" | cut -d'"' -f2); TUN=$(grep -m1 '^TUN=' "$SRC" | cut -d'"' -f2)
CF="https://api.cloudflare.com/client/v4"; H=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")
EP="$CF/accounts/$ACCT/cfd_tunnel/$TUN/configurations"
HOST="digico.tinydoorstudios.com"; TARGET="http://192.168.200.126:3002"
MODE="${1:-show}"
ZONE=$(curl -sS "${H[@]}" "$CF/zones?name=tinydoorstudios.com" | python3 -c "import json,sys;print(json.load(sys.stdin)['result'][0]['id'])")
echo "zone=$ZONE"
curl -sS "${H[@]}" "$EP" -o /tmp/cf_cur.json
python3 - "$MODE" "$HOST" "$TARGET" <<'PY'
import json,sys
mode,host,target=sys.argv[1:]
d=json.load(open('/tmp/cf_cur.json'))['result']; ing=d['config']['ingress']
print('current version',d['version']); [print('  ',i) for i in ing]
if mode=='apply':
    if not any(i.get('hostname')==host for i in ing):
        ing.insert(len(ing)-1,{'service':target,'hostname':host})
    new={'config':{'ingress':ing,'warp-routing':d['config'].get('warp-routing',{'enabled':False})}}
    json.dump(new,open('/tmp/cf_new.json','w'))
    print('prepared new ingress:'); [print('  ',i) for i in ing]
PY
echo "--- DNS ($HOST) ---"
curl -sS "${H[@]}" "$CF/zones/$ZONE/dns_records?name=$HOST" | python3 -c "import json,sys;d=json.load(sys.stdin);print([(r['type'],r['content'],r['proxied']) for r in d['result']])"
if [ "$MODE" = apply ]; then
  echo '--- PUT ingress ---'; curl -sS -X PUT "${H[@]}" "$EP" --data @/tmp/cf_new.json | python3 -c "import json,sys;d=json.load(sys.stdin);print('success',d['success'],'version',d.get('result',{}).get('version'),d.get('errors'))"
  echo '--- DNS create (if missing) ---'
  EXIST=$(curl -sS "${H[@]}" "$CF/zones/$ZONE/dns_records?name=$HOST" | python3 -c "import json,sys;print(len(json.load(sys.stdin)['result']))")
  if [ "$EXIST" = 0 ]; then
    curl -sS -X POST "${H[@]}" "$CF/zones/$ZONE/dns_records" --data "{\"type\":\"CNAME\",\"name\":\"digico\",\"content\":\"$TUN.cfargotunnel.com\",\"proxied\":true,\"ttl\":1}" | python3 -c "import json,sys;d=json.load(sys.stdin);print('dns success',d['success'],d.get('errors'))"
  else echo "dns record exists"; fi
fi
