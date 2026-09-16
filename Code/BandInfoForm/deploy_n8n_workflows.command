#!/bin/bash
# Import + publish one or more n8n workflow JSON files from n8n/ onto the VM,
# resolving the two placeholders every workflow in this repo uses
# (REPLACE_WITH_ADVANCE_INTERNAL_TOKEN, REPLACE_WITH_GRAPH_CREDENTIAL_ID) so the
# committed copies never carry real secrets. Restarts n8n once at the end
# (routes don't mount on a freshly imported/activated workflow until then).
#
# Usage:
#   ./deploy_n8n_workflows.command daily_digest.json advance_notify.json ...
#   ./deploy_n8n_workflows.command --all      # every *.json in n8n/
#
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to
# deploy_n8n_log.txt. Safe to re-run — import/publish are both idempotent.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_n8n_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY $VM"
# Review 2026-09-14 (H6): refuse unless the deployed branch is checked out here.
WANT="${ADVANCE_DEPLOY_BRANCH:-main}"
CUR="$(git -C "$HERE" branch --show-current 2>/dev/null)"
if [ "$CUR" != "$WANT" ]; then
  echo "REFUSING to deploy: $HERE is on branch '$CUR', expected '$WANT' (set ADVANCE_DEPLOY_BRANCH to override)."
  exit 1
fi

if [ "$1" = "--all" ]; then
  FILES=("$HERE"/n8n/*.json)
else
  FILES=()
  for f in "$@"; do FILES+=("$HERE/n8n/$f"); done
fi
if [ ${#FILES[@]} -eq 0 ]; then
  echo "Usage: $0 <workflow.json> [more.json ...] | --all"
  exit 1
fi

{
  echo "=== n8n workflow deploy — $(date) ==="
  echo "files: ${FILES[*]}"

  echo
  echo "--- resolve placeholders ---"
  TOKEN=$($SSH "grep -m1 ADVANCE_INTERNAL_TOKEN /opt/band-advance/advance.env | cut -d= -f2-")
  if [ -z "$TOKEN" ]; then
    echo "Couldn't read ADVANCE_INTERNAL_TOKEN from advance.env — aborting."
    exit 1
  fi
  echo "token: resolved"

  GRAPH_CRED_ID=$($SSH '
    cd /opt/n8n
    sudo docker compose exec -T n8n n8n export:credentials --all --output=/tmp/creds_all.json >/dev/null 2>&1
    sudo docker compose exec -T n8n cat /tmp/creds_all.json
    sudo docker compose exec -T n8n rm -f /tmp/creds_all.json
  ' | python3 -c "
import json, sys
try:
    creds = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for c in creds:
    if c.get('name','').startswith('Microsoft Graph - Production@3cdc.org'):
        print(c['id']); break
")
  if [ -z "$GRAPH_CRED_ID" ]; then
    echo "Couldn't resolve the Graph credential id — any workflow needing it will import with a placeholder."
  else
    echo "graph credential id: $GRAPH_CRED_ID"
  fi

  echo
  echo "--- import + publish each workflow ---"
  IDS=()
  SKIPPED=0
  for f in "${FILES[@]}"; do
    name="$(basename "$f")"
    wfid="$(python3 -c "import json; print(json.load(open('$f'))['id'])")"
    # a workflow committed with "active": false is unpublished, not published
    PUBCMD="$(python3 -c "import json; print('unpublish:workflow' if json.load(open('$f')).get('active', True) is False else 'publish:workflow')")"
    IDS+=("$wfid")
    echo "  $name -> id=$wfid"
    tmp="/tmp/n8n_deploy_$name"
    # audit 2026-09-16 ops #4: python, not sed — and check the result
    # before shipping anything. GRAPH_CRED_ID resolving empty used to just
    # warn, then still import a workflow that read a live
    # REPLACE_WITH_GRAPH_CREDENTIAL_ID literal, breaking at runtime.
    if ! ADVANCE_TOKEN="$TOKEN" ADVANCE_GRAPH_CRED="$GRAPH_CRED_ID" python3 -c "
import os
text = open('$f').read()
text = text.replace('REPLACE_WITH_ADVANCE_INTERNAL_TOKEN', os.environ['ADVANCE_TOKEN'])
graph = os.environ.get('ADVANCE_GRAPH_CRED') or ''
if graph:
    text = text.replace('REPLACE_WITH_GRAPH_CREDENTIAL_ID', graph)
if 'REPLACE_WITH_' in text:
    import re
    left = sorted(set(re.findall(r'REPLACE_WITH_\w+', text)))
    print(f'unresolved placeholder(s) in $name: {left}')
    raise SystemExit(1)
open('$tmp', 'w').write(text)
"; then
      echo "  SKIPPING $name — see the placeholder error above"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    scp -J tds -i "$KEY" "$tmp" "$VM:$tmp" || { echo "  SCP FAILED for $name"; rm -f "$tmp"; continue; }
    rm -f "$tmp"
    $SSH "
      cd /opt/n8n
      sudo docker compose cp $tmp n8n:$tmp
      sudo docker compose exec -T n8n n8n import:workflow --input=$tmp
      sudo docker compose exec -T n8n n8n $PUBCMD --id=$wfid
      sudo docker compose exec -T n8n rm -f $tmp
      rm -f $tmp
    " || echo "  import/publish FAILED for $name"
  done

  echo
  echo "--- restart n8n (routes mount on restart) ---"
  $SSH "cd /opt/n8n && sudo docker compose restart n8n"
  echo "waiting for /healthz + routes to come up..."
  for i in $(seq 1 15); do
    sleep 2
    CODE=$($SSH "curl -s -o /dev/null -w '%{http_code}' http://localhost:5678/healthz" 2>/dev/null)
    [ "$CODE" = "200" ] && { echo "healthz OK after $((i*2))s"; break; }
  done
  sleep 10   # webhook routes lag healthz — give them real time, not a token sleep

  echo
  echo "--- final state ---"
  for wfid in "${IDS[@]}"; do
    # "activeVersionId" is what n8n actually schedules off of — the plain
    # active column can read false while the workflow still fires (the
    # Advance Follow-up Check zombie, root-caused 2026-09-16): a raw-column
    # edit clears active without touching activeVersionId.
    $SSH "cd /opt/n8n && sudo docker compose exec -T postgres psql -U n8n -d n8n -tAc \"select id, name, active, \\\"activeVersionId\\\" is not null as published from workflow_entity where id='$wfid';\""
  done

  echo
  if [ "$SKIPPED" -gt 0 ]; then
    echo "=== done with $SKIPPED workflow(s) SKIPPED $(date) ==="
  else
    echo "=== done $(date) ==="
  fi
} 2>&1 | tee "$LOG"
# audit 2026-09-16 ops #4: propagate a skipped workflow as a real failure
# exit code — piping through tee above means $? would otherwise always be
# tee's, never the actual run's.
! grep -q 'done with .* SKIPPED' "$LOG"
