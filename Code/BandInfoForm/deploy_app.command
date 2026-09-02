#!/bin/bash
# Redeploy the Band Advance system (Flask app + offline tools) to the n8n VM.
# Runs on the Mac (reaches the VM via the tds SSH jump). Tees output to deploy_log.txt.
#
# This ships CODE only. It does NOT touch the database container, the env files,
# or the systemd unit — those are one-time setup (see db/DEPLOY notes in README).
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/deploy_log.txt"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"

{
  echo "=== Band Advance deploy — $(date) ==="
  STAMP=$(date +%Y%m%d-%H%M%S)

  echo "--- stage payloads ---"
  tar -C "$HERE/app"   -czf /tmp/adv_app.tgz   app.py advance_db.py forms_config.py templates || exit 1
  tar -C "$HERE/tools" -czf /tmp/adv_tools.tgz draft_emails.py backfill.py event.py daysheet.py sheet.py import_sheet.py fieldspec.py build_template.py dump_followups.py status_sheet.py package_run.py venue_email.py seed_bookings.py append_bookings.py merge_status.py run_now.py email_templates lists doc_templates || exit 1

  echo "--- copy to VM ---"
  scp -J tds -i "$KEY" /tmp/adv_app.tgz   "$VM:/tmp/adv_app.tgz"   || { echo "SCP app FAILED"; exit 1; }
  scp -J tds -i "$KEY" /tmp/adv_tools.tgz "$VM:/tmp/adv_tools.tgz" || { echo "SCP tools FAILED"; exit 1; }

  echo "--- extract + restart ---"
  ssh -J tds -i "$KEY" "$VM" "
    cp /opt/band-advance/app.py /opt/band-advance/app.py.bak.$STAMP
    tar -C /opt/band-advance       -xzf /tmp/adv_app.tgz
    tar -C /opt/band-advance/tools -xzf /tmp/adv_tools.tgz
    sudo systemctl restart band-advance && sleep 2
    echo \"service: \$(systemctl is-active band-advance)\"
    curl -s http://localhost:8097/healthz; echo
  "
  echo "=== done $(date) — https://advance.tinydoorstudios.com ==="
} 2>&1 | tee "$LOG"
