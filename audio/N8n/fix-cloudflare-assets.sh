#!/usr/bin/env bash
# fix-cloudflare-assets.sh  (clean parser version)
# Stops Cloudflare caching/stalling /assets/ downloads.
# Token read from HIDDEN prompt — never echoed, never written to disk, never logged.
#
# Token scope (zone tinydoorstudios.com): Zone:Read, Cache Rules:Edit, Cache Purge:Purge
#
# Run:  bash "/Users/brianlloyd/Documents/Claude/audio/N8n/fix-cloudflare-assets.sh"

set -uo pipefail
BASE="/Users/brianlloyd/Documents/Claude/audio/N8n"
LOG="$BASE/fix-cloudflare.log"
ZONE="tinydoorstudios.com"
SLUG="2026-06-20-blue-eighty-eight"
KB="https://kb.tinydoorstudios.com"
API="https://api.cloudflare.com/client/v4"
T=/tmp/cf_resp.json

CF="${CF:-}"
if [ -z "$CF" ]; then read -s -p "Paste Cloudflare API token (hidden), then press Enter: " CF; echo; fi
[ -n "$CF" ] || { echo "No token provided."; exit 1; }

exec > >(tee "$LOG") 2>&1
echo "=== fix-cloudflare-assets $(date) ==="
api() { curl -s -H "Authorization: Bearer $CF" -H "Content-Type: application/json" "$@"; }

echo "[1] Verify token…"
api "$API/user/tokens/verify" > "$T"
python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("    success:", d.get("success"), "status:", (d.get("result") or {}).get("status"), "errors:", d.get("errors"))
PY

echo "[2] Find zone id…"
api "$API/zones?name=$ZONE" > "$T"
ZID="$(python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
r=d.get("result") or []
print(r[0]["id"] if r else "")
PY
)"
echo "    zone_id: ${ZID:-<none>}"
[ -n "$ZID" ] || { echo "    Token cannot see zone (needs Zone:Read on $ZONE). Stop."; exit 1; }

echo "[3] Current PAGE RULES:"
api "$API/zones/$ZID/pagerules" > "$T"
python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
for pr in (d.get("result") or []):
    tgt=(pr.get("targets") or [{}])[0].get("constraint",{}).get("value")
    acts=[a.get("id") for a in pr.get("actions",[])]
    print("    -", pr.get("status"), "prio", pr.get("priority"), tgt, acts)
if not (d.get("result")): print("    (none)")
PY

echo "[4] Current CACHE RULES:"
api "$API/zones/$ZID/rulesets/phases/http_request_cache_settings/entrypoint" > "$T"
python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
rs=d.get("result") or {}
rules=rs.get("rules") or []
for r in rules:
    print("    -", r.get("expression"), "=>", json.dumps(r.get("action_parameters",{})))
if not rules: print("    (none)")
PY

echo "[5] Purge everything…"
api -X POST "$API/zones/$ZID/purge_cache" --data '{"purge_everything":true}' > "$T"
python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("    purge success:", d.get("success"), "errors:", d.get("errors"))
PY

echo "[6] Add Bypass-cache page rule for /assets/* …"
api -X POST "$API/zones/$ZID/pagerules" --data "{
  \"targets\":[{\"target\":\"url\",\"constraint\":{\"operator\":\"matches\",\"value\":\"*kb.$ZONE/assets/*\"}}],
  \"actions\":[{\"id\":\"cache_level\",\"value\":\"bypass\"}],
  \"status\":\"active\",\"priority\":1
}" > "$T"
python3 - "$T" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("    pagerule success:", d.get("success"), "errors:", d.get("errors"))
PY

echo "[7] Wait for propagation…"; sleep 8

echo "[8] Verify public downloads:"
ALLOK=1
for f in \
  "Blue%20Eighty-Eight%20-%20FOH%20Channel%20Processing.pdf" \
  "Blue%20Eighty-Eight%20-%20Input%20List.xlsx" \
  "Blue%20Eighty-Eight.ses" \
  "Blue88%20-%20Handoff.pdf"; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$KB/assets/shows/$SLUG/$f")"
  echo "    $code  $f"
  [ "$code" = "200" ] || ALLOK=0
done

rm -f "$T"
echo ""
if [ "$ALLOK" = "1" ]; then
  echo "============================================================"
  echo " DONE — all downloads return 200 through Cloudflare."
  echo "============================================================"
else
  echo "Not all 200 yet — rule dumps above are in $LOG; I'll read them and follow up."
fi
unset CF
