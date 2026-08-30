#!/bin/bash
# Redeploy the Band Advance Form (Flask app) to the n8n VM and restart it.
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to deploy_log.txt.
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"

{
  echo "=== Band Advance Form (Flask) deploy — $(date) ==="
  echo "--- copy app.py + templates ---"
  scp -J tds -i "$KEY" "$HERE/app/app.py" "$VM:/opt/band-advance/app.py" || { echo "SCP app.py FAILED"; exit 1; }
  scp -J tds -i "$KEY" "$HERE/app/templates/form.html"   "$VM:/opt/band-advance/templates/form.html"   || { echo "SCP form.html FAILED"; exit 1; }
  scp -J tds -i "$KEY" "$HERE/app/templates/thanks.html" "$VM:/opt/band-advance/templates/thanks.html" || { echo "SCP thanks.html FAILED"; exit 1; }
  echo "--- restart service ---"
  ssh -J tds -i "$KEY" "$VM" 'sudo systemctl restart band-advance && sleep 2 && systemctl is-active band-advance && curl -s -o /dev/null -w "GET / -> %{http_code}\n" http://localhost:8097/'
  echo "=== done $(date) ==="
} 2>&1 | tee "$LOG"
