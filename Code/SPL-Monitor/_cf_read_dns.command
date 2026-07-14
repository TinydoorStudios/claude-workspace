#!/usr/bin/env bash
# Read-only: list current DNS records so the memo-spl CNAME can be modeled on an existing one.
set -uo pipefail
cd "$(dirname "$0")"
TOKEN="t65O0ZcJlUjbYfJwvwhvLOVUiUtmINp-xFc8Dvm2"
ZONE="f5bf91260bd4b50fee1c185f40a46524"
curl -sS --max-time 15 -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records?per_page=100" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
if not d.get('success'):
    print('ERROR', d.get('errors')); sys.exit(1)
for r in d['result']:
    print(f\"{r['type']:6} {r['name']:35} -> {r['content']:50} proxied={r['proxied']}\")
"
