#!/bin/bash
# Deploy the Band Advance Form workflow to the n8n VM.
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees everything to deploy_log.txt.
set -o pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_log.txt"
JSON="$HERE/band_advance_form.json"

VM="brian@192.168.200.84"
JUMP="tds"
KEY="$HOME/.ssh/proxmox_tds"
WFID="band-advance-form"

{
  echo "=== Band Advance Form deploy — $(date) ==="

  echo "--- copying workflow JSON to VM /tmp ---"
  scp -J "$JUMP" -i "$KEY" "$JSON" "$VM:/tmp/band_advance_form.json" || { echo "SCP FAILED"; exit 1; }

  echo "--- copying JSON into the n8n container, importing, activating ---"
  ssh -J "$JUMP" -i "$KEY" "$VM" 'bash -s' <<'REMOTE'
set -e
cd /opt/n8n
sudo docker compose cp /tmp/band_advance_form.json n8n:/tmp/wf.json
echo "* import:"
sudo docker compose exec -T n8n n8n import:workflow --input=/tmp/wf.json
echo "* activate:"
sudo docker compose exec -T n8n n8n update:workflow --id=band-advance-form --active=true
echo "* restart (required for the form webhook to re-register):"
sudo docker compose restart n8n
echo "* done on VM"
REMOTE

  echo ""
  echo "=== If activation succeeded, the live form is at: ==="
  echo "    https://n8n.tinydoorstudios.com/form/band-advance"
  echo "=== (test URL, workflow inactive: .../form-test/band-advance) ==="
  echo "=== deploy finished $(date) ==="
} 2>&1 | tee "$LOG"
