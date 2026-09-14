#!/bin/bash
# Ship the "3 days after a show" advance recap extraction feature end-to-end:
#   1. redeploy app + tools code (reuses deploy_app.command)
#   2. apply the schema addition (advance_recaps table) — idempotent
#   3. make sure LibreOffice (soffice) is on the VM, for docx->pdf conversion
#   4. import + activate the new n8n workflow (Advance Recap Extraction, daily 2am)
#   5. smoke-test the new internal endpoint
#
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to
# deploy_recap_log.txt. Safe to re-run — every step here is idempotent.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_recap_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH="ssh -J tds -i $KEY $VM"

{
  echo "=== Advance recap extraction deploy — $(date) ==="

  echo
  echo "--- 1. redeploy app + tools code ---"
  "$HERE/deploy_app.command" || { echo "deploy_app.command FAILED"; exit 1; }

  echo
  echo "--- 2. apply schema addition (advance_recaps table) ---"
  $SSH "sudo docker exec -i advance-db psql -U advance -d advance" < "$HERE/db/schema.sql" \
    || { echo "schema apply FAILED"; exit 1; }

  echo
  echo "--- 3. check / install LibreOffice on the VM ---"
  $SSH '
    if command -v soffice >/dev/null 2>&1; then
      echo "soffice already present: $(command -v soffice)"
    else
      echo "soffice not found — installing libreoffice-writer (headless-sufficient, lighter than full libreoffice)"
      sudo apt-get update -y && sudo apt-get install -y libreoffice-writer
      command -v soffice && echo "soffice installed OK" || { echo "soffice STILL missing after install"; exit 1; }
    fi
  ' || { echo "LibreOffice check/install FAILED"; exit 1; }

  echo
  echo "--- 4. import + activate the n8n workflow ---"
  TOKEN=$($SSH "grep -m1 ADVANCE_INTERNAL_TOKEN /opt/band-advance/advance.env | cut -d= -f2-")
  if [ -z "$TOKEN" ]; then
    echo "Couldn't read ADVANCE_INTERNAL_TOKEN from /opt/band-advance/advance.env on the VM — aborting import."
    exit 1
  fi
  sed "s/REPLACE_WITH_ADVANCE_INTERNAL_TOKEN/$TOKEN/" "$HERE/n8n/advance_recap_extraction.json" \
    > /tmp/advance_recap_extraction.json
  scp -J tds -i "$KEY" /tmp/advance_recap_extraction.json "$VM:/tmp/advance_recap_extraction.json" \
    || { echo "SCP workflow JSON FAILED"; exit 1; }
  rm -f /tmp/advance_recap_extraction.json
  $SSH '
    cd /opt/n8n
    sudo docker compose cp /tmp/advance_recap_extraction.json n8n:/tmp/advance_recap_extraction.json
    sudo docker compose exec -T n8n n8n import:workflow --input=/tmp/advance_recap_extraction.json
    sudo docker compose exec -T n8n n8n publish:workflow --id=advance-recap-extraction
    sudo docker compose restart n8n
    sleep 3
  ' || { echo "n8n import/activate FAILED"; exit 1; }

  echo
  echo "--- 5. smoke-test the new endpoint ---"
  $SSH "curl -s -X POST -H \"X-Advance-Token: $TOKEN\" http://localhost:8097/internal/run-recap-extraction; echo"

  echo
  echo "=== done $(date) ==="
} 2>&1 | tee "$LOG"
