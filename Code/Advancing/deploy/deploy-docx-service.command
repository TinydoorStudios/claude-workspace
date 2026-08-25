#!/bin/bash
# Deploys the advance docx service + database to the n8n VM.
# Runs on the Mac (the Cowork sandbox can't reach the LAN). Double-click or:
#   bash deploy-docx-service.command
# Output is tee'd to deploy/deploy.log in this folder for Nyquist to read back.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$HERE/deploy/deploy.log"
exec > >(tee "$LOG") 2>&1

# ---- settings you confirm before running ----
VM="brian@192.168.200.84"                    # n8n VM
SSH="ssh -J tds -i $HOME/.ssh/proxmox_tds $VM"
PGUSER="${PGUSER:-n8n}"                       # <-- confirm the Postgres user in /opt/n8n/.env
PGSERVICE="postgres"                          # docker compose service name for Postgres
COMPOSE="sudo docker compose -f /opt/n8n/docker-compose.yml"
# ----------------------------------------------

echo "== $(date) =="
echo ">> 1. Create the 'advancing' database (ok if it already exists)"
$SSH "$COMPOSE exec -T $PGSERVICE psql -U $PGUSER -tc \"SELECT 1 FROM pg_database WHERE datname='advancing'\" | grep -q 1 || $COMPOSE exec -T $PGSERVICE psql -U $PGUSER -c 'CREATE DATABASE advancing;'"

echo ">> 2. Load schema"
$SSH "$COMPOSE exec -T $PGSERVICE psql -U $PGUSER -d advancing" < "$HERE/db/schema.sql"

echo ">> 3. Copy the docx service to the VM"
$SSH "sudo mkdir -p /opt/advance-docx && sudo chown brian:brian /opt/advance-docx"
rsync -av -e "ssh -J tds -i $HOME/.ssh/proxmox_tds" \
  "$HERE/docx-service/" "$VM:/opt/advance-docx/"

echo ">> 4. Python venv + deps"
$SSH "cd /opt/advance-docx && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt && echo venv-ok"

echo ">> 5. Env file check"
$SSH "test -f /etc/advance-docx.env && echo 'env present' || echo 'MISSING /etc/advance-docx.env — create it from docx-service/advance.env.example (see README) BEFORE starting the service'"

echo ">> 6. systemd unit"
$SSH "sudo tee /etc/systemd/system/advance-docx.service >/dev/null <<'UNIT'
[Unit]
Description=Advance docx render service
After=network.target
[Service]
EnvironmentFile=/etc/advance-docx.env
WorkingDirectory=/opt/advance-docx
ExecStart=/opt/advance-docx/.venv/bin/gunicorn -w 2 -b 0.0.0.0:8097 app:app
Restart=on-failure
User=brian
[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload"

echo ">> 7. Start (only if env exists)"
$SSH "test -f /etc/advance-docx.env && (sudo systemctl enable --now advance-docx && sleep 2 && curl -s localhost:8097/health && echo) || echo 'skipped start — create /etc/advance-docx.env first, then: sudo systemctl enable --now advance-docx'"

echo "== done =="
