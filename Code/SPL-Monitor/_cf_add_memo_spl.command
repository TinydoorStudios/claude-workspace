#!/usr/bin/env bash
# Adds memo-spl.tinydoorstudios.com: DNS CNAME (modeled on the existing spl.* record)
# + a tunnel ingress rule -> localhost:8091. Backs up current tunnel config first,
# reads it fresh (not from notes) to avoid clobbering any rule added since the last
# doc update, inserts the new rule ahead of the catch-all, PUTs, then verifies.
set -uo pipefail
cd "$(dirname "$0")"
OUT="_cf_add_memo_spl.out"
TOKEN="t65O0ZcJlUjbYfJwvwhvLOVUiUtmINp-xFc8Dvm2"
ACCT="fbeee7047a26f8691be223ce5a7ba260"
ZONE="f5bf91260bd4b50fee1c185f40a46524"
TUN="b1e6581d-4384-4fbe-b960-a156760a2860"
CF="https://api.cloudflare.com/client/v4"
AUTH=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")
HOST="memo-spl.tinydoorstudios.com"
STAMP=$(date +%Y%m%d-%H%M%S)

{
echo "===== add $HOST  $(date) ====="

echo "----- 1. DNS: create CNAME -----"
curl -sS --max-time 20 -X POST "${AUTH[@]}" "$CF/zones/$ZONE/dns_records" \
  --data "{\"type\":\"CNAME\",\"name\":\"$HOST\",\"content\":\"$TUN.cfargotunnel.com\",\"proxied\":true}"
echo

echo "----- 2. tunnel: backup current ingress -> _cf_ingress_backup_$STAMP.json -----"
curl -sS --max-time 20 "${AUTH[@]}" "$CF/accounts/$ACCT/cfd_tunnel/$TUN/configurations" \
  -o "_cf_ingress_backup_$STAMP.json"
echo "saved: _cf_ingress_backup_$STAMP.json"
python3 -c "
import json
d = json.load(open('_cf_ingress_backup_$STAMP.json'))
print('current version:', d['result']['version'])
ing = d['result']['config']['ingress']
print(json.dumps(ing, indent=2))
"

echo "----- 3. build + PUT new ingress (insert memo-spl before catch-all) -----"
python3 -c "
import json
d = json.load(open('_cf_ingress_backup_$STAMP.json'))
ing = d['result']['config']['ingress']
new_rule = {'service': 'http://localhost:8091', 'hostname': '$HOST'}
if not any(r.get('hostname') == '$HOST' for r in ing):
    ing.insert(-1, new_rule)  # last entry is the http_status:404 catch-all
out = {'config': {'ingress': ing, 'warp-routing': {'enabled': False}}}
json.dump(out, open('/tmp/memo_spl_new_config.json', 'w'))
print(json.dumps(out, indent=2))
"
curl -sS --max-time 20 -X PUT "${AUTH[@]}" "$CF/accounts/$ACCT/cfd_tunnel/$TUN/configurations" \
  --data @/tmp/memo_spl_new_config.json
echo

echo "----- 4. re-read to confirm -----"
curl -sS --max-time 20 "${AUTH[@]}" "$CF/accounts/$ACCT/cfd_tunnel/$TUN/configurations" -o /tmp/memo_spl_after.json
python3 -c "
import json
d = json.load(open('/tmp/memo_spl_after.json'))
print('new version:', d['result']['version'])
print(json.dumps(d['result']['config']['ingress'], indent=2))
"

echo "Waiting 8s for edge propagation..."
sleep 8

echo "----- 5. live test (expect 502 until the VM-side service is deployed — that's OK, confirms routing) -----"
curl -s -D - -o /dev/null --max-time 20 "https://$HOST/" | grep -iE 'http/|server:|cf-'

echo "----- 6. sanity: existing spl.tinydoorstudios.com still up -----"
curl -s -o /dev/null -w 'spl.tinydoorstudios.com = HTTP %{http_code}\n' --max-time 20 "https://spl.tinydoorstudios.com/"

echo "===== end ====="
} 2>&1 | tee "$OUT"
