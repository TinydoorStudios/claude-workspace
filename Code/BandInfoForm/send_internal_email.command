#!/bin/bash
# Send an internal ops email as Production@3cdc.org via the app-only Microsoft
# Graph connector, using the n8n "Internal Send — Outlook" workflow
# (n8n/internal_send_outlook.json, id internal-send-outlook).
#
#   ./send_internal_email.command <file.html> ["Subject line"] [recipient]
#
# Defaults: subject "Internal Send Test", recipient blloyd@3cdc.org.
#
# Verified working 2026-09-09: Graph returned 202, execution 496075 success.
# Replaces six one-off debugging scripts from that session — everything they
# proved is folded in here:
#   • resolves the Graph credential's real n8n id/type at run time rather than
#     hardcoding it (and never touches the secret)
#   • the workflow uses responseMode:lastNode + fullResponse/neverError, so a
#     failure comes BACK to you instead of silently erroring inside n8n
#   • retries past the webhook-registration gap after an n8n restart —
#     /healthz answers 200 well before webhook routes are actually mounted
#   • prints the execution's status, and its real error text from Postgres if
#     it failed (that DB read is what cracked the original bug — read the
#     execution error before theorizing)
#
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees to send_internal_email_log.txt.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/send_internal_email_log.txt"
HTML="${1:-$HERE/mock_daily_digest_2026-09-10.html}"
SUBJECT="${2:-Internal Send Test}"
TO="${3:-blloyd@3cdc.org}"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY $VM"

{
  echo "=== Internal send — $(date) ==="
  [ -f "$HTML" ] || { echo "No such HTML file: $HTML"; exit 1; }
  echo "file: $HTML"
  echo "to:   $TO"
  echo "subj: $SUBJECT"

  TOKEN=$($SSH "grep -m1 ADVANCE_INTERNAL_TOKEN /opt/band-advance/advance.env | cut -d= -f2-")
  [ -n "$TOKEN" ] || { echo "Couldn't read ADVANCE_INTERNAL_TOKEN on the VM."; exit 1; }

  # Make sure the workflow is present + active with the right credential wired.
  # (Skip with --no-deploy once it's known good, to avoid the restart wait.)
  if [ "$4" != "--no-deploy" ]; then
    echo
    echo "--- ensuring workflow is deployed + active ---"
    $SSH '
      cd /opt/n8n
      sudo docker compose exec -T n8n n8n export:credentials --all --output=/tmp/c.json >/dev/null 2>&1
      sudo docker compose exec -T n8n cat /tmp/c.json
      sudo docker compose exec -T n8n rm -f /tmp/c.json
    ' > /tmp/creds.json 2>/dev/null
    read -r CRED_ID CRED_TYPE <<<"$(python3 - <<'PY'
import json,re
raw=open('/tmp/creds.json').read()
m=re.search(r'\[.*\]',raw,re.S)
creds=json.loads(m.group(0)) if m else []
c=next((c for c in creds if 'graph' in (c.get('name') or '').lower()), None)
print(f"{c['id']} {c['type']}" if c else " ")
PY
)"
    rm -f /tmp/creds.json
    [ -n "$CRED_ID" ] || { echo "Couldn't resolve the Graph credential."; exit 1; }
    echo "credential: $CRED_ID ($CRED_TYPE)"
    python3 - "$HERE/n8n/internal_send_outlook.json" "$CRED_ID" "$CRED_TYPE" "$TOKEN" <<'PY' > /tmp/wf.json
import json,sys
path,cid,ctype,token=sys.argv[1:5]
wf=json.load(open(path))
for n in wf["nodes"]:
    if n["type"]=="n8n-nodes-base.code":
        n["parameters"]["jsCode"]=n["parameters"]["jsCode"].replace("REPLACE_WITH_ADVANCE_INTERNAL_TOKEN",token)
    if n["type"]=="n8n-nodes-base.httpRequest":
        n["parameters"]["genericAuthType"]=ctype
        n["credentials"]={ctype:{"id":cid,"name":"Microsoft Graph - Production@3cdc.org (App-only)"}}
print(json.dumps(wf,ensure_ascii=False))
PY
    scp -q -J tds -i "$KEY" /tmp/wf.json "$VM:/tmp/wf.json" && rm -f /tmp/wf.json
    $SSH '
      cd /opt/n8n
      sudo docker compose cp /tmp/wf.json n8n:/tmp/wf.json >/dev/null
      sudo docker compose exec -T n8n n8n import:workflow --input=/tmp/wf.json 2>&1 | tail -1
      sudo docker compose exec -T n8n n8n publish:workflow --id=internal-send-outlook 2>&1 | tail -1
      sudo docker compose exec -T n8n rm -f /tmp/wf.json; rm -f /tmp/wf.json
      sudo docker compose restart n8n >/dev/null 2>&1
    '
  fi

  echo
  echo "--- sending ---"
  python3 - "$HTML" "$SUBJECT" "$TO" <<'PY' > /tmp/payload.json
import json,sys
print(json.dumps({"subject":sys.argv[2],"html":open(sys.argv[1]).read(),"to":sys.argv[3]}))
PY
  scp -q -J tds -i "$KEY" /tmp/payload.json "$VM:/tmp/payload.json" && rm -f /tmp/payload.json
  $SSH "
    for i in \$(seq 1 15); do
      CODE=\$(curl -sS -o /tmp/resp.txt -w '%{http_code}' -X POST \
        -H 'X-Advance-Token: $TOKEN' -H 'Content-Type: application/json' \
        --data @/tmp/payload.json http://localhost:5678/webhook/internal-send-outlook 2>/dev/null)
      if [ \"\$CODE\" != '404' ] && [ \"\$CODE\" != '000' ]; then break; fi
      echo \"  (waiting for webhook route… attempt \$i)\"; sleep 5
    done
    echo \"webhook HTTP \$CODE\"
    head -c 400 /tmp/resp.txt; echo
    rm -f /tmp/payload.json /tmp/resp.txt
  "

  echo
  echo "--- execution result ---"
  sleep 3
  $SSH 'cd /opt/n8n && ID=$(sudo docker compose exec -T postgres psql -U n8n -d n8n -t -A -c "SELECT id FROM execution_entity WHERE \"workflowId\"='"'"'internal-send-outlook'"'"' ORDER BY id DESC LIMIT 1;"); ST=$(sudo docker compose exec -T postgres psql -U n8n -d n8n -t -A -c "SELECT status FROM execution_entity WHERE id=$ID;"); echo "execution $ID: $ST"; if [ "$ST" != "success" ]; then echo "--- error text ---"; sudo docker compose exec -T postgres psql -U n8n -d n8n -t -A -c "SELECT data FROM execution_data WHERE \"executionId\"=$ID;" 2>/dev/null | grep -oE "\"message\":\"[^\"]{10,300}\"" | head -5; fi' 2>/dev/null

  echo
  echo "=== done $(date) ==="
} 2>&1 | tee "$LOG"
