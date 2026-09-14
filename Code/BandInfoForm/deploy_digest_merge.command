#!/bin/bash
# Ship the Daily Digest / Crew Report merge (2026-09-09):
#   1. redeploy app + tools code (reuses deploy_app.command — daily_digest.py,
#      crew_report.py, app.py, email_templates/ are all in its tools tarball)
#   2. re-import crew_report.json over the existing "crew-report" workflow —
#      its daily 7:10am cron trigger node was removed, on-demand webhook kept.
#      Same id, so this is a safe re-import, not a new workflow.
#   3. smoke-test both /internal/daily-digest (now carries Today's Crew) and
#      the still-live /internal/crew-report on-demand endpoint.
#
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to
# deploy_digest_merge_log.txt. Safe to re-run.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_digest_merge_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY $VM"

{
  echo "=== Daily Digest / Crew Report merge deploy — $(date) ==="

  echo
  echo "--- 1. redeploy app + tools code ---"
  "$HERE/deploy_app.command" || { echo "deploy_app.command FAILED"; exit 1; }

  echo
  echo "--- 2. re-import crew_report.json (cron trigger removed) ---"
  TOKEN=$($SSH "grep -m1 ADVANCE_INTERNAL_TOKEN /opt/band-advance/advance.env | cut -d= -f2-")
  if [ -z "$TOKEN" ]; then
    echo "Couldn't read ADVANCE_INTERNAL_TOKEN from /opt/band-advance/advance.env on the VM — aborting import."
    exit 1
  fi
  sed "s/REPLACE_WITH_ADVANCE_INTERNAL_TOKEN/$TOKEN/" "$HERE/n8n/crew_report.json" \
    > /tmp/crew_report.json
  scp -J tds -i "$KEY" /tmp/crew_report.json "$VM:/tmp/crew_report.json" \
    || { echo "SCP workflow JSON FAILED"; exit 1; }
  rm -f /tmp/crew_report.json
  $SSH '
    cd /opt/n8n
    sudo docker compose cp /tmp/crew_report.json n8n:/tmp/crew_report.json
    sudo docker compose exec -T n8n n8n import:workflow --input=/tmp/crew_report.json
    sudo docker compose exec -T n8n n8n publish:workflow --id=crew-report
    sudo docker compose restart n8n
    sleep 3
  ' || { echo "n8n import/activate FAILED"; exit 1; }

  echo
  echo "--- 3. smoke-test both endpoints ---"
  echo "daily-digest (now carries Today's Crew):"
  $SSH "curl -s -X POST -H \"X-Advance-Token: $TOKEN\" http://localhost:8097/internal/daily-digest | head -c 400; echo"
  echo
  echo "crew-report (on-demand only now, no daily cron):"
  $SSH "curl -s -X POST -H \"X-Advance-Token: $TOKEN\" http://localhost:8097/internal/crew-report | head -c 400; echo"

  echo
  echo "=== done $(date) ==="
  echo "Reminder: the live Crew Report workflow's OLD 'Daily 7:10am' node is gone after"
  echo "this re-import. If n8n still shows a scheduled 7:10am trigger for it in the UI"
  echo "after this runs, the re-import didn't take — check there by hand."
} 2>&1 | tee "$LOG"
